import logging
from pathlib import Path

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MASTER_TAG_LIST_PATH = "tags/master.yaml"
RESPONSE_OUTPUT_DIR = Path("outputs")


class Benchmark:
    def __init__(self):
        self.response_files = {}
        self.find_response_files()
        self.parse_response_files()

    def find_response_files(self):
        found_file_paths = [p for p in RESPONSE_OUTPUT_DIR.iterdir() if p.is_file()]
        for file_path in found_file_paths:
            for model_name in config.MODEL_LIST:
                if file_path.name[:-3] in model_name:
                    self.response_files[model_name] = file_path

    def parse_response_files(self):
        for response_file_path in self.response_files.values():
            with open(response_file_path, "r", encoding="utf-8") as response_file:
                print(response_file.read())


if __name__ == "__main__":
    Benchmark()
