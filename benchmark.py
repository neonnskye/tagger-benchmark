import json
import logging
from pathlib import Path
import re

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MASTER_TAG_LIST_PATH = "tags/master.yaml"
RESPONSE_OUTPUT_DIR = Path("outputs")


class Benchmark:
    def __init__(self):
        self.response_file_paths = {}
        self.find_response_file_paths()

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
            with open(response_file_path, "r", encoding="utf-8") as response_file:
                response_raw = response_file.read()

            match = re.search(r"({[\W\w]+})", response_raw)
            if not match:
                logging.warning(f"Skipped invalid JSON response: '{response_file_path}'...")

            response = json.loads(match.group(1))
            image_results = response["results"]
            for image_result in image_results:
                tags = [tag for tag in image_result["tags"]]
                logger.info(tags)


if __name__ == "__main__":
    Benchmark()
