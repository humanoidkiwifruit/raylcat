#!/usr/bin/env python3
import argparse
from pathlib import Path

from . import scratch_project


def main():
    COMMANDS = ["build", "run"]

    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        help="What you wish to do with the sb3",
        choices=COMMANDS,
    )
    parser.add_argument("sb3_path", help="The path of the sb3 you wish to convert")
    parser.add_argument("--work-dir", help="The working directory", default="work/")
    parser.add_argument(
        "--overwrite-work-dir",
        help="Delete any files in the working directory before proceeding",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()
    logger.info(f"Command: {args.command}")
    logger.info(f"Sb3 path: {args.sb3_path}")
    logger.info(f"work dir: {args.work_dir}")
    logger.info(f"overwriting work dir: {args.overwrite_work_dir}")
    if args.command == "build":
        project = scratch_project.ScratchProject(
            sb3_path=(args.sb3_path),
            work_dir=Path(args.work_dir),
            overwrite_work_dir=args.overwrite_work_dir,
        )
        project.build()
    elif args.command == "run":
        project = scratch_project.ScratchProject(
            args.sb3_path,
            work_dir=Path(args.work_dir),
            overwrite_work_dir=args.overwrite_work_dir,
        )
        project.build()
        project.run()
    else:
        print("Invalid command.")


if __name__ == "__main__":
    main()
