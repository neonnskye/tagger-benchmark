import json
import logging
import re
from pathlib import Path

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MASTER_TAG_LIST_PATH = "tags/master.yaml"
RESPONSE_OUTPUT_DIR = Path("outputs")


def make_json_safe(obj):
    if isinstance(obj, set):
        return sorted(obj)  # or list(obj)
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    return obj


class Benchmark:
    def __init__(self):
        self.response_file_paths = {}
        self.find_response_file_paths()

        self.responses = {}
        self.parse_response_files()

    def find_response_file_paths(self):
        logging.info("Scanning responses...")
        found_file_paths = [p for p in RESPONSE_OUTPUT_DIR.iterdir() if p.is_file()]
        for file_path in found_file_paths:
            for model_name in config.MODEL_LIST:
                if file_path.name[:-3] in model_name:
                    self.response_file_paths[model_name] = file_path
        logging.info(f"Found {len(self.response_file_paths)} valid response files")

    def parse_response_files(self):
        logging.info("Parsing responses...")
        for response_file_path in self.response_file_paths.values():
            model_name = response_file_path.name[:-3]

            with open(response_file_path, "r", encoding="utf-8") as response_file:
                response_raw = response_file.read()

            match = re.search(r"({[\W\w]+})", response_raw)
            if not match:
                logging.warning(f"Skipped invalid JSON response: '{response_file_path}'...")
            response = json.loads(match.group(1))

            image_results = response["results"]
            for image_idx, image_result in enumerate(image_results):
                image_key = f"image_{image_idx + 1}"
                tags = set(image_result["tags"])

                if image_key not in self.responses:
                    self.responses[image_key] = {
                        "by_model": {},
                        "tag_index": {},
                    }

                self.responses[image_key]["by_model"][model_name] = tags

        # For debugging
        with open("out.json", "w", encoding="utf-8") as out_file:
            safe_json = make_json_safe(self.responses)
            json.dump(safe_json, out_file, indent=2)


if __name__ == "__main__":
    Benchmark()
