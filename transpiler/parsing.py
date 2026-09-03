from . import util
from .scratch_types import ScratchBlock, ScratchSprite


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

def get_sprites(json_dict: dict) -> list[ScratchSprite]:
    sprites = []
    for sprite_dict in json_dict['targets']:
        if not sprite_dict['isStage']:
            sprites.append(ScratchSprite(
                is_stage = sprite_dict['isStage'],
                name = util.clean_sprite_name(sprite_dict['name']),
                blocks = parse_blocks(sprite_dict['blocks']),
                current_costume = sprite_dict['currentCostume'],
                visible = sprite_dict["visible"],
                x = sprite_dict['x'],
                y = sprite_dict['y'],
                size = sprite_dict['size'],
                direction = sprite_dict['direction'],
                layer_order=sprite_dict['layerOrder'],
                costumes=sprite_dict['costumes']
            ))
    return sprites
