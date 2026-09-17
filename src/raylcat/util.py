from pathlib import Path

from .scratch_types import ScratchBlock


def clean_sprite_name(name: str) -> str:
    return name.replace(" ", "")


def generate_texture_name(sprite_name: str, index: int):
    return f"{sprite_name}_texture_number_{index}"


def is_dir_empty(dir_path: Path):
    """Check if a directory is empty."""
    return next(dir_path.iterdir(), None) is None


def get_substack_first_block_id(block: ScratchBlock) -> str:
    """Get the id of the first block in a block's SUBSTACK."""
    return block.inputs["SUBSTACK"][1]
