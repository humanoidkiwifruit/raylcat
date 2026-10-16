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
    )
    project.build()
    return project


@app.command()
def build(
    sb3_path: Annotated[
        str,
        typer.Argument(help="Path to the .sb3 that you wish to operate on"),
    ],
    work_dir: Annotated[
        str,
        typer.Argument(
            help="directory that all sb3/.go file manipulation will happen in"
        ),
    ] = "work/",
    framerate: Annotated[
        int,
        typer.Argument(
            help="Framerate to cap the project at. 0 results in uncapped framerate"
        ),
    ] = 30,
    stage_width: int = 480,
    stage_height: int = 360,
    draw_framerate: Annotated[
        bool,
        typer.Argument(help="Draw the current framerate at the top left of the screen"),
    ] = False,
):
    _ = get_project_and_build(
        sb3_path=sb3_path,
        work_dir=work_dir,
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )


@app.command()
def run(
    sb3_path: Annotated[
        str,
        typer.Argument(help="Path to the .sb3 that you wish to operate on"),
    ],
    work_dir: Annotated[
        str,
        typer.Argument(
            help="directory that all sb3/.go file manipulation will happen in"
        ),
    ] = "work/",
    framerate: Annotated[
        int,
        typer.Argument(
            help="Framerate to cap the project at. 0 results in uncapped framerate"
        ),
    ] = 30,
    stage_width: int = 480,
    stage_height: int = 360,
    draw_framerate: bool = False,
):
    project = get_project_and_build(
        sb3_path=sb3_path,
        work_dir=work_dir,
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )
    project.run()


@app.command(name="build-zip")
def build_zip(
    sb3_path: Annotated[
        str,
        typer.Argument(help="Path to the .sb3 that you wish to operate on"),
    ],
    work_dir: Annotated[
        str,
        typer.Argument(
            help="directory that all sb3/.go file manipulation will happen in"
        ),
    ] = "work/",
    framerate: Annotated[
        int,
        typer.Argument(
            help="Framerate to cap the project at. 0 results in uncapped framerate"
        ),
    ] = 30,
    stage_width: int = 480,
    stage_height: int = 360,
    draw_framerate: bool = False,
    out_path: str = "raylcatoutput.zip",
):
    """Compile the specified sb3 and package it into a zip file"""
    project = get_project_and_build(
        sb3_path=sb3_path,
        work_dir=work_dir,
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )
    project.build_zip(out_path)


@app.command(name="build-binary")
def build_binary(
    sb3_path: Annotated[
        str,
        typer.Argument(help="Path to the .sb3 that you wish to operate on"),
    ],
    work_dir: Annotated[
        str,
        typer.Argument(
            help="directory that all sb3/.go file manipulation will happen in"
        ),
    ] = "work/",
    framerate: Annotated[
        int,
        typer.Argument(
            help="Framerate to cap the project at. 0 results in uncapped framerate"
        ),
    ] = 30,
    stage_width: int = 480,
    stage_height: int = 360,
    draw_framerate: bool = False,
):
    logger.fatal("Building binaries not yet supported")
    """
    project = get_project_and_build(
        sb3_path=sb3_path,
        work_dir=work_dir,
        framerate=framerate,
        stage_width=stage_width,
        stage_height=stage_height,
        draw_framerate=draw_framerate,
    )
    project.build_binary()"""


if __name__ == "__main__":
    app()
