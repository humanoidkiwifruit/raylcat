import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from . import parsing, sb3_archive, workspaces
from .generation import Generation
from .types import (
    CustomBlockDeclaration,
    ParsedSprite,
    ParsedStage,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    TranspiledSprite,
    TranspiledStage,
)

logger = logging.getLogger(__name__)


class ScratchProjectTranspiler:
    def __init__(
        self,
        sb3_path: Path,
        draw_framerate: bool,
        work_dir: Path | None = None,
        stage_width: int = 480,
        stage_height: int = 360,
        framerate: int = 30,
        embed_assets: bool = False,
    ):
        if work_dir is None:
            work_dir = Path("work/")
        self.stage: ScratchStage
        self.sprites: list[ScratchSprite]
        self.template_dir: Path = Path("go_templates/")
        self.scratchISA_prefix: str = "scratch"
        self.workspace: workspaces.Workspace = workspaces.Workspace(
            work_dir=work_dir,
        )
        self.sb3: sb3_archive.Sb3Archive = sb3_archive.Sb3Archive(sb3_path)
        self.stage_width = stage_width
        self.stage_height = stage_height
        self.framerate: int = framerate
        self.draw_framerate: bool = draw_framerate
        self.parser: parsing.Parser = parsing.Parser()
        self.json_dict: dict[str, Any]
        self.generation: Generation = Generation(
            scratchISA_prefix=self.scratchISA_prefix, embed_assets=embed_assets
        )

        self.custom_blocks: list[CustomBlockDeclaration]
        self.parsed_stage: ParsedStage
        self.parsed_sprites: list[ParsedSprite]
        self.embed_assets = embed_assets

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
        framerate: int,
        stage_width: int,
        stage_height: int,
        draw_framerate: bool,
    ) -> str:
        go_sprite_object_declarations: list[str] = []
        go_texture_declarations: list[str] = []
        go_ordered_render_sprites = [""] * len(self.json_dict["targets"])
        image_vars: list[list[str]] = []

        # All normal sprite stuff ########
        for transpiled_sprite in transpiled_sprites:
            go_sprite_object_declarations.append(
                transpiled_sprite.go_sprite_object_declaration
            )
            go_texture_declarations.append(
                "\n".join(transpiled_sprite.texture_declarations)
            )
            go_ordered_render_sprites[transpiled_sprite.layer_order] = (
                f"&{transpiled_sprite.name},"
            )
            image_vars.append(transpiled_sprite.transpiled_sprite_image_vars)

        # Stage stuff #############################
        go_sprite_object_declarations.append(
            transpiled_stage.go_sprite_object_declaration
        )
        go_texture_declarations.extend(transpiled_stage.texture_declarations)
        image_vars.append(transpiled_stage.transpiled_sprite_image_vars)

        # Template population ####################

        main_go_file_str = self.workspace.populate_main_go_template(
            go_sprite_object_declarations=go_sprite_object_declarations,
            go_texture_declarations=go_texture_declarations,
            project_name="Scratch Go Raylib",
            context_declaration=transpiled_context_declaration,
            transpiled_custom_blocks=transpiled_custom_blocks,
            framerate=framerate,
            stage_width=stage_width,
            stage_height=stage_height,
            draw_framerate=draw_framerate,
            transpiled_sprite_image_vars=image_vars,
        )

        return main_go_file_str

    def build(self):
        """Fill the compilation directory, get it ready to compile. This is somewhat the *main* function for transpilation"""
        self.workspace.setup()
        self.extract()
        self.workspace.convert_svgs()
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
        transpiled_custom_blocks = (
            self.generation.block_generation.generate_custom_blocks(self.custom_blocks)
        )
        main_go_str = self.generate_main_go(
            transpiled_sprites=transpiled_sprites,
            transpiled_stage=transpiled_stage,
            transpiled_context_declaration=transpiled_context,
            transpiled_custom_blocks=transpiled_custom_blocks,
            framerate=self.framerate,
            stage_width=self.stage_width,
            stage_height=self.stage_height,
            draw_framerate=self.draw_framerate,
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

    def build_binary(self, out_path: str | None = None):
        logger.debug(
            "building compile dir to binary using `go build`. Specified out path: "
            + str(not (out_path is None))
        )
        if not (out_path is None):
            if self.embed_assets:
                out_path = str(Path(out_path).resolve())
            _ = subprocess.run(
                ["go", "build", "-o", out_path],
                cwd=self.workspace.compile_dir,
                capture_output=False,
                text=True,
                check=True,
            )
        else:
            _ = subprocess.run(
                ["go", "build"],
                cwd=self.workspace.compile_dir,
                capture_output=False,
                text=True,
                check=True,
            )

    def build_zip(self, out_path: str):
        logger.debug("Building compile-dir & binary to zip")
        self.build_binary()
        shutil.make_archive(
            base_name=out_path,
            format="zip",
            root_dir=str(self.workspace.compile_dir),
        )
