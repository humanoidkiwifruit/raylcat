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

    def populate_main_go_template(self, go_sprite_object_declarations: list[str], go_texture_declarations: list[str], go_ordered_render_sprites: list[str], all_sprite_goroutines: list[str], main_func_goroutine_interrupts: list[str], project_name: str, initial_render_order: str) -> str:
        with open(self.template_dir / "main.go", "r") as original_file:
            main_go_file_str = original_file.read()

        main_go_file_str = main_go_file_str.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(go_sprite_object_declarations))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:TEXTURES", "\n".join(go_texture_declarations))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:FILL_RENDER_QUEUE", initial_render_order) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(all_sprite_goroutines))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(main_func_goroutine_interrupts))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:NAME", project_name)
        return main_go_file_str
