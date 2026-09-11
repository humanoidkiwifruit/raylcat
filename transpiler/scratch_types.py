from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScratchBlock:
    opcode: str
    next: str | None
    parent: str | None
    inputs: dict | None
    fields: dict | None
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
    variables: dict[str, list]

@dataclass
class TranspiledTarget:
    name: str
    goroutines: list[str]
    go_sprite_object_declaration: str
    texture_declarations: list[str]
    goroutine_interrupt: str

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
class TranspiledStage(TranspiledTarget):
    pass

@dataclass
class BlockSpec:
    go_func: str
    inputs: list
    fields: list
    wants: list[str] | None
    is_menu: bool = False

#------------
#IR stuff
#------------

@dataclass
class StringLiteral:
    value: str

@dataclass
class NumberLiteral:
    value: float

@dataclass
class BlockCall:
    opcode: str
    inputs: dict[str, Expression] | None
    fields: dict[str, Expression] | None

@dataclass
class MenuValue:
    value: str

type Expression = StringLiteral | NumberLiteral | BlockCall | MenuValue

@dataclass
class TraditionalStatement:
    block_call: BlockCall

@dataclass
class IfStatement:
    condition: Expression
    body: list[Statement]

@dataclass
class IfElseStatement:
    condition: Expression
    then_body: list[Statement]
    else_body: list[Statement]

@dataclass
class ForeverStatement:
    body: list[Statement]

type Statement = TraditionalStatement | IfStatement | IfElseStatement | ForeverStatement

@dataclass
class SpriteScript:
    body: list[Statement]
    control_index: int
