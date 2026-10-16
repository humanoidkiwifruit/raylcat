#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Annotated

import typer

from . import scratch_project

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
# Initialize your Typer app instance
app = typer.Typer(
    help="Tool to convert scratch3 .sb3 files into compilable go + raylib code"
)


def get_project_and_build(
    sb3_path: str,
    draw_framerate: bool,
    work_dir: str,
    framerate: int,
    stage_width: int,
    stage_height: int,
    embed_assets: bool = False,
) -> scratch_project.ScratchProjectTranspiler:
    logger.info(f"Sb3 path: {sb3_path}")
    logger.info(f"work dir: {work_dir}")
    logger.info(f"target fps: {framerate}")
    project = scratch_project.ScratchProjectTranspiler(
        sb3_path=Path(sb3_path),
        work_dir=Path(work_dir),
        stage_width=stage_width,
        stage_height=stage_height,
        framerate=framerate,
        draw_framerate=draw_framerate,
        embed_assets=embed_assets,
    )
    project.build()
    return project


Sb3Path = Annotated[
    Path,
    typer.Argument(
        help="Path to the .sb3 file to operate on",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
]

WorkDir = Annotated[
    Path,
    typer.Option(
        "--work-dir",
        help="Working directory for generated and temporary files",
        file_okay=False,
        dir_okay=True,
    ),
]

Framerate = Annotated[
    int,
    typer.Option(
        "--framerate",
        min=0,
        help="Maximum FPS; 0 uncapps the fps",
    ),
]

StageWidth = Annotated[
    int,
    typer.Option("--stage-width", min=1, help="Stage width in pixels"),
]

StageHeight = Annotated[
    int,
    typer.Option("--stage-height", min=1, help="Stage height in pixels"),
]

DrawFramerate = Annotated[
    bool,
    typer.Option(
        "--draw-framerate",
        help="Draw the current FPS in the top-left corner",
    ),
]


@app.command()
def build(
    sb3_path: Sb3Path,
    work_dir: WorkDir = Path("work/"),
    framerate: Framerate = 30,
    stage_width: StageWidth = 480,
    stage_height: StageHeight = 360,
    draw_framerate: DrawFramerate = False,
):
    _ = get_project_and_build(
        sb3_path=str(sb3_path),
        work_dir=str(work_dir),
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )


@app.command()
def run(
    sb3_path: Sb3Path,
    work_dir: WorkDir = Path("work/"),
    framerate: Framerate = 30,
    stage_width: StageWidth = 480,
    stage_height: StageHeight = 360,
    draw_framerate: DrawFramerate = False,
):
    """Build and run a Scratch project."""
    project = get_project_and_build(
        sb3_path=str(sb3_path),
        work_dir=str(work_dir),
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )
    project.run()


@app.command(name="build-zip")
def build_zip(
    sb3_path: Sb3Path,
    work_dir: WorkDir = Path("work/"),
    framerate: Framerate = 30,
    stage_width: StageWidth = 480,
    stage_height: StageHeight = 360,
    draw_framerate: DrawFramerate = False,
    out_path: Annotated[
        Path,
        typer.Option(
            "--out-path",
            help="Output path for the zip file, WITHOUT the .zip extension",
        ),
    ] = Path("Raylcat"),
):
    """Compile a Scratch project and package it into a zip file."""
    project = get_project_and_build(
        sb3_path=str(sb3_path),
        work_dir=str(work_dir),
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )
    project.build_zip(str(out_path))


@app.command(name="build-binary")
def build_binary(
    sb3_path: Sb3Path,
    work_dir: WorkDir = Path("work/"),
    framerate: Framerate = 30,
    stage_width: StageWidth = 480,
    stage_height: StageHeight = 360,
    draw_framerate: DrawFramerate = False,
    embed_assets: Annotated[
        bool,
        typer.Option(
            "--embed-assets",
            help="Embed assets into the generated binary",
        ),
    ] = False,
    out_path: Annotated[
        str,
        typer.Option("--out", help="Where build the binary to"),
    ] = "Raylcat",
):
    """Build a standalone executable from a Scratch project."""
    logger.info("Building binary")

    project = get_project_and_build(
        sb3_path=str(sb3_path),
        work_dir=str(work_dir),
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
        embed_assets=embed_assets,
    )
    project.build_binary(str(out_path))


if __name__ == "__main__":
    app()
