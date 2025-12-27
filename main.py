from PIL import Image
from wdtagger import Tagger as WDTagger

TAG_LIST_PATH = "tags/master.yaml"
IMAGES_CAPTIONS = {
    "images/image1.jpg": "Mui..♡",
    "images/image2.jpg": "🩶⌨️🎧💿",
    "images/image3.jpg": "Alternative elf",
    "images/image4.jpg": "💫",
    "images/image5.jpg": "Fashion inspo - crochet maxi skirt",
    "images/image6.jpg": "death by thrifting",
}

TAG_LIST_TEMPLATE = """```yaml
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

PROMPT_TEMPLATE_PATH = "templates/prompt.md"
PROMPT_OUTPUT_PATH = "outputs/prompt.md"


class Tagger:
    def __init__(self):
        self.wdtagger = WDTagger()
        self.image_list = IMAGES_CAPTIONS.keys()

        self.wdtagger_results = None
        self.run_wdtagger()

        self.generate_prompt()

    def run_wdtagger(self):
        images = [Image.open(image_path) for image_path in self.image_list]
        self.wdtagger_results = self.wdtagger.tag(images)

    def generate_prompt(self):
        with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as prompt_template_file:
            prompt_template = prompt_template_file.read()

        with open(TAG_LIST_PATH, "r", encoding="utf-8") as tag_list_file:
            tag_list = tag_list_file.read()

        prompt_template_args = [TAG_LIST_TEMPLATE.format(tag_list)]

        for idx, (image_path, result) in enumerate(zip(self.image_list, self.wdtagger_results), 1):
            image_tags = ", ".join(f"{tag} ({score:.2f})" for tag, score in result.general_tag_data.items())
            image_caption = IMAGES_CAPTIONS[image_path]
            image_metadata = IMAGE_METADATA_TEMPLATE.format(idx, image_tags, image_caption)
            prompt_template_args.append(image_metadata)

        generated_prompt = prompt_template.format(*prompt_template_args)
        
        with open(PROMPT_OUTPUT_PATH, "w", encoding="utf-8") as prompt_output_file:
            prompt_output_file.write(generated_prompt)


if __name__ == "__main__":
    Tagger()
