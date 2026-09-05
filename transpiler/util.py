from transpiler.scratch_types import ScratchSprite


def clean_sprite_name(name: str) -> str:
    return name.replace(" ", "")

def generate_texture_name(sprite: ScratchSprite, index: int):
 return f"{sprite.name}_texture_number_{index}"

def opcode_to_go_func_call(opcode: str) -> str:
     return opcode.capitalize()
