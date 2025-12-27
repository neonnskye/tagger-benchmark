import logging
import os
import time

from PIL import Image
from dotenv import load_dotenv
from openrouter import OpenRouter
from wdtagger import Tagger as WDTagger

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

MASTER_TAG_LIST_PATH = "tags/master.yaml"

SYSTEM_PROMPT_TEMPLATE_PATH = "templates/prompt/system.md"
USER_PROMPT_TEMPLATE_PATH = "templates/prompt/user.md"
JSON_OUTPUT_TEMPLATE_PATH = "templates/prompt/output.json"

SYSTEM_PROMPT_OUTPUT_PATH = "outputs/prompt/system.md"
USER_PROMPT_OUTPUT_PATH = "outputs/prompt/user.md"

MODEL_LIST = [
    "google/gemini-3-pro-preview",
    "google/gemini-3-flash-preview",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-opus-4.5",
    "x-ai/grok-4",
    "openai/gpt-5"
    "openai/gpt-5.2",
    "openai/o4-mini-high",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-chat-v3-0324",
]

MASTER_TAG_LIST_TEMPLATE = """```yaml
{}
```"""

IMAGE_METADATA_TEMPLATE = """## Image {}

### WD14 tags

```
{}
```

### Caption

```
"{}"
```"""


class Tagger:
    def __init__(self):
        logger.info("Initializing WDTagger...")
        self.wdtagger = WDTagger()
        self.image_list = config.IMAGES_CAPTIONS.keys()

        self.wdtagger_results = None
        self.run_wdtagger()

        self.system_prompt = None
        self.user_prompt = None

        logger.info("Generating prompts...")
        self.generate_system_prompt()
        self.generate_user_prompt()
        logger.info("Prompts generated and saved")

        self.run_prompt()

    def run_wdtagger(self):
        logger.info("Starting WD14 tagging...")
        images = [Image.open(image_path) for image_path in self.image_list]
        logger.info(f"Loaded {len(images)} images to be tagged")
        self.wdtagger_results = self.wdtagger.tag(images)
        logger.info("WD14 tagging completed")

    def generate_system_prompt(self):
        with open(SYSTEM_PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as system_prompt_template_file:
            system_prompt_template = system_prompt_template_file.read()

        with open(JSON_OUTPUT_TEMPLATE_PATH, "r", encoding="utf-8") as json_output_template_file:
            json_output_template = json_output_template_file.read()

        system_prompt_template_args = [json_output_template]
        self.system_prompt = system_prompt_template.format(*system_prompt_template_args)

        with open(SYSTEM_PROMPT_OUTPUT_PATH, "w", encoding="utf-8") as system_prompt_output_file:
            system_prompt_output_file.write(self.system_prompt)

    def generate_user_prompt(self):
        with open(USER_PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as user_prompt_template_file:
            user_prompt_template = user_prompt_template_file.read()

        with open(MASTER_TAG_LIST_PATH, "r", encoding="utf-8") as master_tag_list_file:
            master_tag_list = master_tag_list_file.read()

        user_prompt_template_args = [MASTER_TAG_LIST_TEMPLATE.format(master_tag_list)]

        for idx, (image_path, result) in enumerate(zip(self.image_list, self.wdtagger_results), 1):
            image_tags = ", ".join(f"{tag} ({score:.2f})" for tag, score in result.general_tag_data.items())
            image_caption = config.IMAGES_CAPTIONS[image_path]
            image_metadata = IMAGE_METADATA_TEMPLATE.format(idx, image_tags, image_caption)
            user_prompt_template_args.append(image_metadata)

        self.user_prompt = user_prompt_template.format(*user_prompt_template_args)

        with open(USER_PROMPT_OUTPUT_PATH, "w", encoding="utf-8") as user_prompt_template_file:
            user_prompt_template_file.write(self.user_prompt)

    def run_prompt(self):
        logger.info("Starting OpenRouter API...")
        with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:
            for model in MODEL_LIST[-2:]:  # FIXME prompt all
                logger.info(f"Sending request to model: '{model}'")
                response = client.chat.send(
                    model=model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": self.user_prompt}
                    ]
                )

                logger.info(f"Received response from '{model}'")
                print(response.choices[0].message.content)

                logger.info("Waiting 5 seconds before next request...")
                time.sleep(5)
            logger.info("All API calls completed.")


if __name__ == "__main__":
    Tagger()
