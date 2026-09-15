from transpiler.spec_loader import SpecLoader

from . import util
from .scratch_types import (
    AccessVariable,
    BlockCall,
    BlockSpec,
    Expression,
    ForeverStatement,
    IfElseStatement,
    IfStatement,
    MenuValue,
    NumberLiteral,
    RepeatStatement,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    SpriteScript,
    Statement,
    StringLiteral,
    TraditionalStatement,
    WaitUntilStatement,
)


class Generation:
    def __init__(self, scratchISA_prefix: str):
        self.scratchISA_prefix: str = scratchISA_prefix
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()

    def generate_sprite_object_declaration(self, sprite: ScratchSprite) -> str:
        go_object_declaration = f"{sprite.name} := {self.scratchISA_prefix}.ScratchSprite{{X: {sprite.x}, Y: {sprite.y}, Size: {sprite.size}, Direction: {sprite.direction}, CostumeNumber: {sprite.current_costume + 1}, Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, Show: {'true' if sprite.visible else 'false'}, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        for _ in range(util.number_of_scripts(sprite)):
            go_object_declaration += (
                "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            )
        go_object_declaration += "}}"
        return go_object_declaration

    def generate_stage_object_declaration(self, stage: ScratchStage) -> str:
        go_object_declaration = f"{stage.name} := {self.scratchISA_prefix}.ScratchStage{{CostumeNumber: {stage.current_costume + 1}, Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        for _ in range(util.number_of_scripts(stage)):
            go_object_declaration += (
                "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            )
        go_object_declaration += "}}"
        return go_object_declaration

    def generate_texture_declarations(self, sprite: ScratchTarget) -> list[str]:
        texture_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            texture_filename = costume.asset_id + "." + costume.data_format
            texture_go_name = util.generate_texture_name(sprite, index)
            texture_declarations.append(
                f'{texture_go_name} := rl.LoadTexture("assets/{texture_filename}")\ndefer rl.UnloadTexture({texture_go_name})'
            )  # Instantiate raylib textures
        return texture_declarations

    def transpile_costume_values(self, sprite: ScratchTarget) -> list[str]:
        costume_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            costume_declarations.append(f"{self.scratchISA_prefix}.Costume{{Name: \"{costume.name}\", Texture: {util.generate_texture_name(sprite, index)} }}")
        return costume_declarations

    def generate_go_render(self, sprite: ScratchSprite) -> str:
        return f"{self.scratchISA_prefix}.DrawSprite(&{sprite.name})"

    def generate_goroutine_interrupt(self, sprite: ScratchSprite) -> str:
        return f"for _, control := range {sprite.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"

    def generate_goroutine(self, sprite: ScratchTarget, script: SpriteScript) -> str:
        goroutine_list = [f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, context *{self.scratchISA_prefix}.Context) {{\n<-control.AwakenChan\n"]
        goroutine_list.append(self.generate_stack(script.body))
        goroutine_list.append(f"\nfor {{ {self.scratchISA_prefix}.Yield(control) }}\n}}(context.Sprites[\"{sprite.name}\"], context.Sprites[\"{sprite.name}\"].Controls[{script.control_index - 1}], &context)") #negater off by one error
        return "".join(goroutine_list)

    def generate_expression(self, expression: Expression) -> str:
        if isinstance(expression, (StringLiteral, MenuValue)):
            return f"{self.scratchISA_prefix}.ValueFromString(\"{expression.value}\")"
        elif isinstance(expression, NumberLiteral):
            return f"{self.scratchISA_prefix}.ValueFromFloat64(float64({expression.value}))"
        elif isinstance(expression, BlockCall):
            return self.generate_block_call(expression)
        elif isinstance(expression, AccessVariable):
            return f"context.Variables[\"{expression.variable_name}\"]"

    def generate_block_call(self, block_call: BlockCall) -> str:
        block_call_str = f"{self.scratchISA_prefix}.{self.specs[block_call.opcode].go_func}("
        args: list[str] = []
        wants = self.specs[block_call.opcode].wants
        if not wants is None:
            args.extend(wants)
        if not block_call.fields is None:
            for field_expression in block_call.fields.values():
                args.append(self.generate_expression(field_expression))
        if not block_call.inputs is None:
            for input_expression in block_call.inputs.values():
                args.append(self.generate_expression(input_expression))
        block_call_str += ", ".join(args)
        block_call_str += ")"
        return block_call_str

    def generate_stack(self, stack: list[Statement]) -> str:
        stack_list: list[str] = []
        for statement in stack:
            stack_list.append(self.generate_statement(statement))
        return "\n".join(stack_list)

    def generate_statement(self, statement: Statement) -> str:
        statement_list: list[str] = []
        if isinstance(statement, TraditionalStatement):
            statement_list.append(self.generate_block_call(statement.block_call))
            return "\n".join(statement_list)
        elif isinstance(statement, IfStatement):
            statement_list.append(f"if {self.generate_expression(statement.condition)} {{")
            statement_list.append(self.generate_stack(statement.body))
            statement_list.append("}")
            return "\n".join(statement_list)
        elif isinstance(statement, IfElseStatement):
            statement_list.append(f"if {self.generate_expression(statement.condition)} {{")
            statement_list.append(self.generate_stack(statement.then_body))
            statement_list.append("} else {")
            statement_list.append(self.generate_stack(statement.else_body))
            statement_list.append("}")
            return "\n".join(statement_list)
        elif isinstance(statement, ForeverStatement):
            statement_list.append("for {")
            statement_list.append(self.generate_stack(statement.body))
            statement_list.append(f"{self.scratchISA_prefix}.Yield(control)\n}}")
            return "\n".join(statement_list)
        elif isinstance(statement, RepeatStatement):
            statement_list.append(f"for i := 0; i < int({self.generate_expression(statement.times)}.NumberValue); i++ {{")
            statement_list.append(self.generate_stack(statement.body))
            statement_list.append(f"{self.scratchISA_prefix}.Yield(control) }}")
            return "\n".join(statement_list)
        elif isinstance(statement, WaitUntilStatement):
            statement_list.append(f"for !{self.generate_expression(statement.condition)} {{ {self.scratchISA_prefix}.Yield(control) }}")
            return "\n".join(statement_list)
        else:
            raise TypeError("Unimplemented statement type: " + str(type(statement)) + " in generate_statement().")
