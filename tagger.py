from PIL import Image
from wdtagger import Tagger as WDTagger

import config

MASTER_TAG_LIST_PATH = "tags/master.yaml"

SYSTEM_PROMPT_TEMPLATE_PATH = "templates/prompt/system.md"
USER_PROMPT_TEMPLATE_PATH = "templates/prompt/user.md"
JSON_OUTPUT_TEMPLATE_PATH = "templates/prompt/output.json"

SYSTEM_PROMPT_OUTPUT_PATH = "outputs/prompt/system.md"
USER_PROMPT_OUTPUT_PATH = "outputs/prompt/user.md"

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
        self.wdtagger = WDTagger()
        self.image_list = config.IMAGES_CAPTIONS.keys()

        self.wdtagger_results = None
        self.run_wdtagger()

        self.system_prompt = None
        self.user_prompt = None

        self.generate_system_prompt()
        self.generate_user_prompt()

    def run_wdtagger(self):
        images = [Image.open(image_path) for image_path in self.image_list]
        self.wdtagger_results = self.wdtagger.tag(images)

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


if __name__ == "__main__":
    Tagger()
