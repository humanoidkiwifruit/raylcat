from transpiler.scratch_types import ScratchSprite


def clean_sprite_name(name: str) -> str:
    return name.replace(" ", "")

def generate_texture_name(sprite: ScratchSprite, index: int):
 return f"{sprite.name}_texture_number_{index}"


def number_of_scripts(sprite: ScratchSprite) -> int:
    script_count = 0
    for possible_hat_block in sprite.blocks.values():
        if possible_hat_block.opcode == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
            script_count += 1
    return script_count
