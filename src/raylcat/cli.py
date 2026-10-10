#!/usr/bin/env python3
import logging
from pathlib import Path

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
    work_dir: str = "work/",
    overwrite_work_dir: bool = False,
    framerate: int = 30,
    stage_width: int = 480,
    stage_height: int = 360,
) -> scratch_project.ScratchProjectTranspiler:
    logger.info(f"Sb3 path: {sb3_path}")
    logger.info(f"work dir: {work_dir}")
    logger.info(f"overwriting work dir: {overwrite_work_dir}")
    logger.info(f"target fps: {framerate}")
    project = scratch_project.ScratchProjectTranspiler(
        sb3_path=Path(sb3_path),
        work_dir=Path(work_dir),
        overwrite_work_dir=overwrite_work_dir,
        stage_width=stage_width,
        stage_height=stage_height,
        framerate=framerate,
    )
    project.build()
    return project


@app.command()
def build(
    sb3_path: str,
    work_dir: str = "work/",
    overwrite_work_dir: bool = False,
    framerate: int = 30,
    stage_width: int = 480,
    stage_height: int = 360,
):
    _ = get_project_and_build(
        sb3_path,
        work_dir,
        overwrite_work_dir,
        framerate,
        stage_width,
        stage_height,
    )


@app.command()
def run(
    sb3_path: str,
    work_dir: str = "work/",
    overwrite_work_dir: bool = False,
    framerate: int = 30,
    stage_width: int = 480,
    stage_height: int = 360,
):
    project = get_project_and_build(
        sb3_path,
        work_dir,
        overwrite_work_dir,
        framerate,
        stage_width,
        stage_height,
    )
    project.run()


@app.command(name="build-binary")
def build_binary(
    sb3_path: str,
    work_dir: str = "work/",
    overwrite_work_dir: bool = False,
    framerate: int = 30,
    stage_width: int = 480,
    stage_height: int = 360,
):
    project = get_project_and_build(
        sb3_path, work_dir, overwrite_work_dir, framerate, stage_width, stage_height
    )
    project.run()


if __name__ == "__main__":
    app()
