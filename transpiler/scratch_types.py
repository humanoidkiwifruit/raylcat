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
class ScratchCostume:
    name: str
    go_texture_name: str


@dataclass
class ScratchTarget:
    name: str
    blocks: dict[str, ScratchBlock]
    costumes: list
    current_costume: int

@dataclass
class ScratchSprite(ScratchTarget):
    is_stage: bool
    layer_order: int
    visible: bool
    x: float
    y: float
    size: float
    direction: float

@dataclass
class ScratchStage(ScratchTarget):
    pass

@dataclass
class TranspiledSprite:
    name: str
    goroutines: list[str]
    go_sprite_object_declaration: str
    texture_declarations: list[str]
    goroutine_interrupt: str
    layer_order: int

@dataclass
class TranspiledStage:
    name: str
    goroutines: list[str]
    go_sprite_object_declaration: str
    texture_declarations: list[str]
    goroutine_interrupt: str

@dataclass
class BlockSpec:
    go_func: str
    inputs: list
    fields: list
    wants: list[str] | None
    is_menu: bool = False
