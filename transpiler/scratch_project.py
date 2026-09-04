import subprocess
from pathlib import Path

from . import parsing, sb3_archive, transpiler, workspaces
from .scratch_types import TranspiledSprite


class ScratchProject:
    def __init__(self, sb3_path):
        self.template_dir = Path("go_templates/")
        self.scratchISA_prefix = "scratch"
        self.workspace = workspaces.Workspace()
        self.sb3 = sb3_archive.Sb3Archive(sb3_path)
        self.transpiler = transpiler.Transpiler()
        self.json_dict = {}

    def extract(self):
        self.sb3.extract_to(self.workspace.sb3_extraction_dir)
        self.sb3.extract_to(self.workspace.assets_dir)


    def generate_main_go(self, transpiled_sprites: list[TranspiledSprite]) -> str:
        go_sprite_object_declarations = []
        go_texture_declarations = []
        all_sprite_goroutines = []
        main_func_goroutine_interrupts = []
        go_ordered_render_sprites = [""] * len(self.json_dict['targets']) #Subtract one to account for the stage
        for transpiled_sprite in transpiled_sprites:
            all_sprite_goroutines.extend(transpiled_sprite.goroutines)
            go_sprite_object_declarations.append(transpiled_sprite.go_sprite_object_declaration)
            go_texture_declarations.append("\n".join(transpiled_sprite.texture_declarations))
            go_ordered_render_sprites[transpiled_sprite.layer_order] = f"&{transpiled_sprite.name},"
            main_func_goroutine_interrupts.append(transpiled_sprite.goroutine_interrupt)

        #Fill templates
        initial_render_order = (
            f"{self.scratchISA_prefix}.OrderedRender ="
            + f"[]*{self.scratchISA_prefix}.ScratchSprite{{\n"
            + str( "\n".join(go_ordered_render_sprites) ) #needs to be casted to a string for some reason
            + "\n}"
        )
        main_go_file_str = self.workspace.populate_main_go_template(
            go_sprite_object_declarations=go_sprite_object_declarations,
            go_texture_declarations=go_texture_declarations,
            all_sprite_goroutines=all_sprite_goroutines,
            main_func_goroutine_interrupts=main_func_goroutine_interrupts,
            project_name="Scratch Go Raylib",
            initial_render_order=initial_render_order,
        )

        return main_go_file_str

    def build(self):
        self.workspace.setup()
        self.extract()
        self.json_dict = self.sb3.read_json_to_dict()
        sprites = parsing.get_sprites(self.json_dict)
        transpiled_sprites = []
        for sprite in sprites:
            transpiled_sprites.append(self.transpiler.transpile_sprite(sprite))
        main_go_str = self.generate_main_go(transpiled_sprites)
        self.workspace.write_main_go(main_go_str)

    def run(self):
        _ = subprocess.run(["go", "run", "."], cwd=self.workspace.compile_dir, capture_output=False, text=True, check=True)
