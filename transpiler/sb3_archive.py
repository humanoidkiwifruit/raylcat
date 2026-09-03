import json
import zipfile
from pathlib import Path


class Sb3_archive:
    def __init__(self, sb3_path: str):
        self.sb3_path = sb3_path


    def extract_to(self, extraction_path: str | Path):
        with zipfile.ZipFile(self.sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
            archive.extractall(extraction_path)

    def read_json_to_dict(self) -> dict:
        with zipfile.ZipFile(self.sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
            with archive.open("project.json") as file:
                json_text = file.read()
        return json.loads(json_text) #Convert project.json to a python dictionary
