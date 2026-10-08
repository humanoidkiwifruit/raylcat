from __future__ import annotations

from copyreg import constructor
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any


@dataclass
class ScratchBlock:
    opcode: str
    next: str | None
    parent: str | None
    inputs: dict[str, Any] | None
    fields: dict[str, Any] | None
    top_level: bool
    mutation: dict | None


@dataclass
class ScratchCostume:
    name: str
    bitmap_resolution: int | None
    data_format: str
    asset_id: str
    # md5ext: str
    rotation_centre_x: int
    rotation_centre_y: int


@dataclass
class ParsedTarget:
    name: str
    costumes: list[ScratchCostume]
    current_costume: int
    variables: dict[str, Expression]
    scripts: list[TargetScript]


@dataclass
class ParsedSprite(ParsedTarget):
    layer_order: int
    visible: bool
    x: float
    y: float
    size: float
    direction: float


@dataclass
class ParsedStage(ParsedTarget):
    pass


@dataclass
class ScratchTarget:
    name: str
    blocks: dict[str, ScratchBlock]
    costumes: list[ScratchCostume]
    current_costume: int
    variables: dict[str, list]
    lists: dict[str, list]


@dataclass
class TranspiledTarget:
    name: str
    go_sprite_object_declaration: str
    texture_declarations: list[str]


@dataclass
class ScratchSprite(ScratchTarget):
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
class TranspiledSprite(TranspiledTarget):
    layer_order: int


@dataclass
class TranspiledStage(TranspiledTarget):
    pass


@dataclass
class BlockSpec:
    go_func: str
    inputs: list[str]
    fields: list[str]
    wants: list[str] | None
    is_menu: bool = False


class InputTypes(IntEnum):
    NUMBER = 4
    POSITIVE_NUMBER = 5
    POSITIVE_INTEGER = 6
    INTEGER = 7
    ANGLE = 8
    COLOUR = 9
    STRING = 10
    BROADCAST = 11
    VARIABLE = 12
    LIST = 13


# ------------
# AST stuff
# ------------


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


@dataclass
class AccessVariable:
    variable_name: str


@dataclass
class AccessFunctionArgument:
    argument_name: str


type Expression = (
    StringLiteral
    | NumberLiteral
    | BlockCall
    | MenuValue
    | AccessVariable
    | AccessFunctionArgument
)


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


@dataclass
class RepeatStatement:
    times: Expression
    body: list[Statement]


@dataclass
class WaitUntilStatement:
    condition: Expression


@dataclass
class RepeatUntilStatement:
    condition: Expression
    substack: list[Statement]


@dataclass
class ProcedureCall:
    proc_code: str
    inputs: dict[str, Expression] | None


type Statement = (
    TraditionalStatement
    | IfStatement
    | IfElseStatement
    | ForeverStatement
    | RepeatStatement
    | WaitUntilStatement
    | RepeatUntilStatement
    | ProcedureCall
)


@dataclass
class Script:
    body: list[Statement]


@dataclass
class WhenGreenFlagScript(Script):
    control_index: int


@dataclass
class WhenKeyPressedScript(Script):
    key: str


type TargetScript = WhenGreenFlagScript | WhenKeyPressedScript


class ValueType(Enum):
    BOOLEAN = "bool"
    SCRATCH_VALUE = "ScratchValue"


@dataclass
class CustomBlockInput:
    name: str
    type: ValueType


@dataclass
class CustomBlockDeclaration:
    body: list[Statement]
    proc_code: str
    inputs: list[CustomBlockInput]
