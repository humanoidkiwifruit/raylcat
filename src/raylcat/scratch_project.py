import logging
import subprocess
from pathlib import Path
from typing import Any

from . import parsing, sb3_archive, workspaces
from .generation import Generation
from .scratch_types import (
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    TranspiledSprite,
    TranspiledStage,
)

logger = logging.getLogger(__name__)


class ScratchProject:
    def __init__(
        self,
        sb3_path: Path,
        work_dir: Path | None = None,
        overwrite_work_dir: bool = False,
    ):
        if work_dir is None:
            work_dir = Path("work/")
        self.stage: ScratchStage
        self.sprites: list[ScratchSprite]
        self.template_dir: Path = Path("go_templates/")
        self.scratchISA_prefix: str = "scratch"
        self.workspace: workspaces.Workspace = workspaces.Workspace(
            work_dir=work_dir,
            overwrite_work_dir=overwrite_work_dir,
        )
        self.sb3: sb3_archive.Sb3Archive = sb3_archive.Sb3Archive(sb3_path)
        self.parser: parsing.Parser = parsing.Parser()
        self.json_dict: dict[str, Any]
        self.generation: Generation = Generation(self.scratchISA_prefix)

    def extract(self):
        """Extract the sb3 to the extraction dir and the assets dir."""
        logger.debug("Extracting sb3 to assets and extraction directories")
        self.sb3.extract_to(self.workspace.sb3_extraction_dir)
        self.sb3.extract_to(self.workspace.assets_dir)

    def generate_main_go(
        self,
        transpiled_sprites: list[TranspiledSprite],
        transpiled_stage: TranspiledStage,
        transpiled_context_declaration: str,
        transpiled_custom_blocks: list[str],
        uncap_framerate: bool,
    ) -> str:
        go_sprite_object_declarations: list[str] = []
        go_texture_declarations: list[str] = []
        all_sprite_goroutines: list[str] = []
        main_func_goroutine_interrupts: list[str] = []
        go_ordered_render_sprites = (
            [""] * len(self.json_dict["targets"])
        )  # Subtract one to account for the stage <- Unsure of the meaning of this comment

        # All normal sprites
        for transpiled_sprite in transpiled_sprites:
            all_sprite_goroutines.extend(transpiled_sprite.goroutines)
            go_sprite_object_declarations.append(
                transpiled_sprite.go_sprite_object_declaration
            )
            go_texture_declarations.append(
                "\n".join(transpiled_sprite.texture_declarations)
            )
            go_ordered_render_sprites[transpiled_sprite.layer_order] = (
                f"&{transpiled_sprite.name},"
            )
            main_func_goroutine_interrupts.append(transpiled_sprite.goroutine_interrupt)

        # Special case for the stage
        all_sprite_goroutines.extend(transpiled_stage.goroutines)
        go_sprite_object_declarations.append(
            transpiled_stage.go_sprite_object_declaration
        )
        go_texture_declarations.extend(transpiled_stage.texture_declarations)
        main_func_goroutine_interrupts.append(transpiled_stage.goroutine_interrupt)

        initial_render_order = (
            f"{self.scratchISA_prefix}.OrderedRender ="
            + f"[]*{self.scratchISA_prefix}.ScratchSprite{{\n"
            + str(
                "\n".join(go_ordered_render_sprites)
            )  # needs to be casted to a string for some reason
            + "\n}"
        )
        main_go_file_str = self.workspace.populate_main_go_template(
            go_sprite_object_declarations=go_sprite_object_declarations,
            go_texture_declarations=go_texture_declarations,
            all_sprite_goroutines=all_sprite_goroutines,
            main_func_goroutine_interrupts=main_func_goroutine_interrupts,
            project_name="Scratch Go Raylib",
            initial_render_order=initial_render_order,
            context_declaration=transpiled_context_declaration,
            transpiled_custom_blocks=transpiled_custom_blocks,
            uncap_framerate=uncap_framerate,
        )

        return main_go_file_str

    def build(self, uncap_framerate: bool):
        """Fill the compilation directory, get it ready to compile"""
        print("uncap framerate: ", uncap_framerate)
        self.workspace.setup()
        self.extract()
        self.json_dict = self.sb3.read_json_to_dict()
        self.sprites = self.parser.get_sprites(self.json_dict)
        self.stage = self.parser.get_stage(self.json_dict)
        all_targets: list[ScratchTarget] = [*self.sprites, self.stage]
        self.custom_blocks = self.parser.parse_custom_block_declarations(all_targets)
        self.parsed_stage = self.parser.parse_stage(self.stage)
        self.parsed_sprites = self.parser.parse_sprites(self.sprites)
        transpiled_stage = self.generation.generate_stage(self.parsed_stage)
        transpiled_sprites: list[TranspiledSprite] = []
        for parsed_sprite in self.parsed_sprites:
            transpiled_sprites.append(self.generation.generate_sprite(parsed_sprite))
        transpiled_context = self.generation.generate_context(
            sprites=self.sprites, stage=self.stage
        )
        transpiled_custom_blocks = self.generation.generate_custom_blocks(
            self.custom_blocks
        )
        main_go_str = self.generate_main_go(
            transpiled_sprites,
            transpiled_stage,
            transpiled_context,
            transpiled_custom_blocks,
            uncap_framerate,
        )
        self.workspace.write_main_go(main_go_str)

    def run(self):
        _ = subprocess.run(
            ["go", "run", "."],
            cwd=self.workspace.compile_dir,
            capture_output=False,
            text=True,
            check=True,
        )
