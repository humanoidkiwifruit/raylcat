import logging
import shutil
from importlib.resources import as_file, files
from pathlib import Path

import cairosvg

logger = logging.getLogger(__name__)


class Workspace:
    """Manages the working area for files"""

    def __init__(
        self,
        work_dir: Path | None,
    ):
        if work_dir is None:
            work_dir = Path("work/")
        # self.template_dir: Path = Path(template_dir)
        self.work_dir: Path = Path(work_dir)
        self.compile_dir: Path = self.work_dir / "compile_dir"
        self.sb3_extraction_dir: Path = self.work_dir / "sb3_extraction"
        self.assets_dir: Path = self.compile_dir / "assets"

    def setup(self):
        """Set up the workspace. Create the work dir and copy in the templates."""
        if self.work_dir.exists():
            logger.info("work dir already exists")
            if not self.work_dir.is_dir():
                raise FileExistsError("Work directory is found but isn't a directory.")
            logger.info("overwriting work dir")
            shutil.rmtree(
                self.work_dir, ignore_errors=True
            )  # Make it ignore errors in case the folder doesn't exist. Probably a bad idea but hey
            self.work_dir.mkdir()
        else:
            logger.info("overwriting work dir")
            shutil.rmtree(
                self.work_dir, ignore_errors=True
            )  # Make it ignore errors in case the folder doesn't exist. Probably a bad idea but hey
            self.work_dir.mkdir()
        self.sb3_extraction_dir.mkdir()
        with as_file(files("raylcat").joinpath("go_templates")) as template_dir:
            _ = shutil.copytree(template_dir, self.compile_dir)
        self.assets_dir.mkdir()

    def convert_svgs(self):
        """convert all the svgs in the assets dir into pngs, scaled up by 2 for some reason"""
        for item in self.assets_dir.iterdir():
            if item.is_file():  # noqa SIM102
                if item.suffix == ".svg":
                    logger.debug(f"rasterising svg {item}")
                    output_path = self.assets_dir / item.with_suffix(".png").name
                    _ = cairosvg.svg2png(url=item, write_to=str(output_path), scale=2)

    def write_main_go(self, main_go_str: str):
        """Write the provided string to the main.go file."""
        with open(self.compile_dir / "main.go", "w") as file:
            _ = file.write(main_go_str)

    def populate_main_go_template(
        self,
        go_sprite_object_declarations: list[str],
        go_texture_declarations: list[str],
        project_name: str,
        context_declaration: str,
        transpiled_custom_blocks: list[str],
        framerate: int,
        stage_width: int,
        stage_height: int,
        draw_framerate: bool,
        transpiled_sprite_image_vars: list[list[str]],
    ) -> str:
        """Populate the main.go template with the provided arguments to a string."""
        with (
            files("raylcat")
            .joinpath("go_templates", "main.go")
            .open("r") as original_file
        ):
            main_go_file_str = original_file.read()

        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:SPRITE_OBJECTS", "\n".join(go_sprite_object_declarations)
        )
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:TEXTURES", "\n".join(go_texture_declarations)
        )
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:INIT_WINDOW",
            f'rl.InitWindow({stage_width}, {stage_height}, "{project_name}")',
        )
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:INSTANTIATE_CONTEXT", context_declaration
        )
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:CUSTOM_BLOCK_DECLARATIONS",
            "\n".join(transpiled_custom_blocks),
        )

        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:IMAGES",
            "\n".join(
                [item for sublist in transpiled_sprite_image_vars for item in sublist]
            ),
        )

        if framerate > 0:
            logger.debug(f"Capping framerate to {framerate}")
            main_go_file_str = main_go_file_str.replace(
                "//TEMPLATING:CAP_FRAMERATE",
                f"rl.SetTargetFPS({framerate})",
            )
        if draw_framerate:
            logger.debug("Drawing framerate to screen")
            main_go_file_str = main_go_file_str.replace(
                "//TEMPLATING:DRAW_FRAMERATE", "rl.DrawFPS(10, 10)"
            )
        return main_go_file_str
