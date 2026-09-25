import logging
import shutil
from importlib.resources import as_file, files
from pathlib import Path

from . import util

logger = logging.getLogger(__name__)


class Workspace:
    def __init__(
        self,
        work_dir: Path | None,
        # template_dir: Path = Path("go_templates/"),
        overwrite_work_dir: bool = False,
    ):
        if work_dir is None:
            work_dir = Path("work/")
        # self.template_dir: Path = Path(template_dir)
        self.work_dir: Path = Path(work_dir)
        self.compile_dir: Path = self.work_dir / "compile_dir"
        self.sb3_extraction_dir: Path = self.work_dir / "sb3_extraction"
        self.assets_dir: Path = self.compile_dir / "assets"
        self.overwrite_work_dir: bool = overwrite_work_dir

    def setup(self):
        """Set up the workspace. Create the work dir and copy in the templates."""
        if self.work_dir.exists() and not self.overwrite_work_dir:
            logger.info("work dir exists but it will not be overwritten")
            if not self.work_dir.is_dir():
                raise FileExistsError("Work directory is found but isn't a directory.")
            elif not util.is_dir_empty(self.work_dir):
                raise FileExistsError(
                    "Work directory already exists, exiting to avoid overwriting possible files. Use the --overwrite-work-dir flag to silence."
                )
            else:
                shutil.rmtree(
                    self.work_dir, ignore_errors=True
                )  # Make it ignore errors in case the folder doesn't exist. Probably a bad idea but hey
                self.work_dir.mkdir()
        else:
            logger.info("work dir exists or it can be overwritten")
            shutil.rmtree(
                self.work_dir, ignore_errors=True
            )  # Make it ignore errors in case the folder doesn't exist. Probably a bad idea but hey
            self.work_dir.mkdir()
        self.sb3_extraction_dir.mkdir()
        with as_file(files("raylcat").joinpath("go_templates")) as template_dir:
            shutil.copytree(template_dir, self.compile_dir)
        self.assets_dir.mkdir()

    def write_main_go(self, main_go_str: str):
        """Write the provided string to the main.go file."""
        with open(self.compile_dir / "main.go", "w") as file:
            file.write(main_go_str)

    def populate_main_go_template(
        self,
        go_sprite_object_declarations: list[str],
        go_texture_declarations: list[str],
        all_sprite_goroutines: list[str],
        main_func_goroutine_interrupts: list[str],
        project_name: str,
        initial_render_order: str,
        context_declaration: str,
        transpiled_custom_blocks: list[str],
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
            "//TEMPLATING:FILL_RENDER_QUEUE", initial_render_order
        )  # Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(all_sprite_goroutines)
        )
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES",
            "\n".join(main_func_goroutine_interrupts),
        )
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:NAME", project_name)
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:INSTANTIATE_CONTEXT", context_declaration
        )
        main_go_file_str = main_go_file_str.replace(
            "//TEMPLATING:CUSTOM_BLOCK_DECLARATIONS",
            "\n".join(transpiled_custom_blocks),
        )
        return main_go_file_str
