from pathlib import Path

import base26

from .types import ScratchBlock


def clean_name(name: str) -> str:
    """Deterministically clean a string name to base26, eg ABCDEFGH"""
    return base26.encode(name.encode("utf-8"))


def generate_texture_name(sprite_name: str, index: int):
    return f"{sprite_name}_texture_number_{index}"


def is_dir_empty(dir_path: Path):
    """Check if a directory is empty."""
    return next(dir_path.iterdir(), None) is None


def get_substack_first_block_id(block: ScratchBlock) -> str:
    """Get the id of the first block in a block's SUBSTACK."""
    assert block.inputs is not None, (
        f"the block {block.opcode} passed to get_substack_first_block_id has no inputs"
    )
    return str(block.inputs["SUBSTACK"][1])
