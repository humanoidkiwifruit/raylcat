from pathlib import Path

from .scratch_types import ScratchBlock, ScratchTarget


def clean_sprite_name(name: str) -> str:
    return name.replace(" ", "")


def generate_texture_name(sprite: ScratchTarget, index: int):
    return f"{sprite.name}_texture_number_{index}"


def number_of_scripts(sprite: ScratchTarget) -> int:
    script_count = 0
    for possible_hat_block in sprite.blocks.values():
        if (
            possible_hat_block.opcode == "event_whenflagclicked"
        ):  # Only consider scripts that begin with a green flack clicked
            script_count += 1
    return script_count


def is_dir_empty(dir_path: Path):
    return next(dir_path.iterdir(), None) is None


def get_substack_first_block_id(block: ScratchBlock) -> str:
    return block.inputs["SUBSTACK"][1]
