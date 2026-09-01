from .scratch_types import ScratchBlock


def parse_block(block_dict: dict) -> ScratchBlock:
    return ScratchBlock(
        opcode=block_dict['opcode'],
        next=block_dict.get('next'),
        parent=block_dict.get('parent'),
        inputs=block_dict.get('inputs'),
        fields=block_dict.get('fields'),
        top_level=block_dict.get('topLevel'),
    )

def parse_blocks(blocks_dict: dict) -> dict[str, ScratchBlock]:
    blocks = {}
    for key, value in blocks_dict.items():
        blocks[key] = parse_block(value)
    return blocks
