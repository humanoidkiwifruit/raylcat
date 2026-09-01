from dataclasses import dataclass


@dataclass
class ScratchBlock:
    opcode: str
    next: str | None
    parent: str | None
    inputs: dict
    fields: dict
    top_level: bool

@dataclass
class ScratchSprite:
    name: str
    is_stage: bool
    blocks: dict[str, ScratchBlock]
    current_costume: int
    layer_order: int
    visible: bool
    x: float
    y: float
    size: float
    direction: float
    costumes: list


@dataclass
class TranspiledSprite:
    name: str
    goroutines: list[str]
    go_sprite_object_declaration: str
    texture_declaration: str
    goroutine_interrupt: str
    go_render: str
