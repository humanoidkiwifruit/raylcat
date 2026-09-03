import os
import shutil
from pathlib import Path


class Workspace:
    def __init__(self, work_dir="work/", template_dir="go_templates/"):
        self.template_dir = Path(template_dir)
        self.work_dir = Path(work_dir)
        self.compile_dir = self.work_dir / "compile_dir"
        self.sb3_extraction_dir = self.work_dir / "sb3_extraction"
        self.assets_dir = self.compile_dir / "assets"

    def setup(self):
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir)
        os.makedirs(self.sb3_extraction_dir)
        _ = shutil.copytree(self.template_dir, self.compile_dir)
        os.makedirs(self.assets_dir)

    def write_main_go(self, main_go_str):
        #Write to main.go file
        with open(self.compile_dir / "main.go", "w") as file:
            file.write(main_go_str)
