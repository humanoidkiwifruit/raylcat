from . import util
from .scratch_types import (
    AccessFunctionArgument,
    AccessVariable,
    BlockCall,
    BlockSpec,
    CustomBlockDeclaration,
    Expression,
    ForeverStatement,
    IfElseStatement,
    IfStatement,
    MenuValue,
    NumberLiteral,
    ParsedSprite,
    ParsedStage,
    ParsedTarget,
    ProcedureCall,
    RepeatStatement,
    RepeatUntilStatement,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    Statement,
    StringLiteral,
    TargetScript,
    TraditionalStatement,
    TranspiledSprite,
    TranspiledStage,
    WaitUntilStatement,
)
from .spec_loader import SpecLoader


class Generation:
    def __init__(self, scratchISA_prefix: str):
        self.scratchISA_prefix: str = scratchISA_prefix
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()

    def generate_sprite_object_declaration(self, sprite: ParsedSprite) -> str:
        go_object_declaration = (
            f"{sprite.name} := {self.scratchISA_prefix}.ScratchSprite{{"
            + f"X: {sprite.x}, "
            + f"Y: {sprite.y}, "
            + f"Size: {sprite.size}, "
            + f"Direction: {sprite.direction}, "
            + f"CostumeNumber: {sprite.current_costume + 1}, "
            + f"Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, "
            + f"Show: {'true' if sprite.visible else 'false'}, "
            + f"Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        )
        for _ in range(len(sprite.scripts)):
            go_object_declaration += (
                "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            )
        go_object_declaration += "}}"
        costume_declarations = self.transpile_costume_values(sprite)
        go_object_declaration = go_object_declaration.replace(
            "TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations)
        )
        return go_object_declaration

    def generate_stage_object_declaration(self, stage: ParsedStage) -> str:
        go_object_declaration = (
            f"{stage.name} := {self.scratchISA_prefix}.ScratchStage{{"
            + f"CostumeNumber: {stage.current_costume + 1}, "
            + f"Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, "
            + f"Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        )
        for _ in range(len(stage.scripts)):
            go_object_declaration += (
                "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            )
        go_object_declaration += "}}"
        costume_declarations = self.transpile_costume_values(stage)
        go_object_declaration = go_object_declaration.replace(
            "TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations)
        )
        return go_object_declaration

    def generate_texture_declarations(self, sprite: ParsedTarget) -> list[str]:
        texture_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            texture_filename = costume.asset_id + "." + costume.data_format
            texture_go_name = util.generate_texture_name(sprite.name, index)
            texture_declarations.append(
                f'{texture_go_name} := rl.LoadTexture("assets/{texture_filename}")\ndefer rl.UnloadTexture({texture_go_name})'
            )  # Instantiate raylib textures
        return texture_declarations

    def transpile_costume_values(self, sprite: ParsedTarget) -> list[str]:
        costume_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            costume_declarations.append(
                f'{self.scratchISA_prefix}.Costume{{Name: "{costume.name}", Texture: {util.generate_texture_name(sprite.name, index)} }}'
            )
        return costume_declarations

    def generate_go_render(self, sprite: ScratchSprite) -> str:
        return f"{self.scratchISA_prefix}.DrawSprite(&{sprite.name})"

    def generate_goroutine_interrupt(self, target: ParsedTarget) -> str:
        return f"for _, control := range {target.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"

    def generate_goroutine(self, sprite: ParsedTarget, script: TargetScript) -> str:
        goroutine_list = [
            f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, context *{self.scratchISA_prefix}.Context) {{\n<-control.AwakenChan\n"
        ]
        goroutine_list.append(self.generate_stack(script.body))
        goroutine_list.append(
            f'\nfor {{ {self.scratchISA_prefix}.Yield(control) }}\n}}(context.Sprites["{sprite.name}"], context.Sprites["{sprite.name}"].Controls[{script.control_index - 1}], &context)'
        )  # negater off by one error
        return "".join(goroutine_list)

    def generate_expression(self, expression: Expression) -> str:
        if isinstance(expression, (StringLiteral, MenuValue)):
            return f'{self.scratchISA_prefix}.ValueFromString("{expression.value}")'
        elif isinstance(expression, NumberLiteral):
            return f"{self.scratchISA_prefix}.ValueFromFloat64(float64({expression.value}))"
        elif isinstance(expression, BlockCall):
            return self.generate_block_call(expression)
        elif isinstance(expression, AccessVariable):
            return f'context.Variables["{expression.variable_name}"]'
        elif isinstance(expression, AccessFunctionArgument):
            return expression.argument_name
        else:
            raise ValueError(
                f"Unimplemented Expression type {type(expression)} in generate_expression()"
            )

    def generate_block_call(self, block_call: BlockCall) -> str:
        """Wants, Inputs, Fields"""
        block_call_str = (
            f"{self.scratchISA_prefix}.{self.specs[block_call.opcode].go_func}("
        )
        args: list[str] = []
        wants = self.specs[block_call.opcode].wants
        if not wants is None:
            args.extend(wants)
        if not block_call.inputs is None:
            for input_expression in block_call.inputs.values():
                args.append(self.generate_expression(input_expression))
        if not block_call.fields is None:
            for field_expression in block_call.fields.values():
                args.append(self.generate_expression(field_expression))
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
            statement_list.append(
                f"if {self.generate_expression(statement.condition)} {{"
            )
            statement_list.append(self.generate_stack(statement.body))
            statement_list.append("}")
            return "\n".join(statement_list)
        elif isinstance(statement, IfElseStatement):
            statement_list.append(
                f"if {self.generate_expression(statement.condition)} {{"
            )
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
            statement_list.append(
                f"for i := 0; i < int({self.generate_expression(statement.times)}.NumberValue); i++ {{"
            )
            statement_list.append(self.generate_stack(statement.body))
            statement_list.append(f"{self.scratchISA_prefix}.Yield(control) }}")
            return "\n".join(statement_list)
        elif isinstance(statement, WaitUntilStatement):
            statement_list.append(
                f"for !{self.generate_expression(statement.condition)} {{ {self.scratchISA_prefix}.Yield(control) }}"
            )
            return "\n".join(statement_list)
        elif isinstance(statement, RepeatUntilStatement):
            statement_list.append(
                f"for !{self.generate_expression(statement.condition)} {{"
            )
            statement_list.append(self.generate_stack(statement.substack))
            statement_list.append(f"{self.scratchISA_prefix}.Yield(control) }}")
            return "\n".join(statement_list)
        elif isinstance(statement, ProcedureCall):
            proc_call = statement.proc_code + "(sprite, control, context, "
            if not statement.inputs is None:
                for input_expression in statement.inputs.values():
                    proc_call += self.generate_expression(input_expression) + ", "
            proc_call += ")"
            statement_list.append(proc_call)
            return "\n".join(statement_list)
        else:
            raise TypeError(
                "Unimplemented statement type: "
                + str(type(statement))
                + " in generate_statement()."
            )

    def generate_context(
        self, sprites: list[ScratchSprite], stage: ScratchStage
    ) -> str:
        context_declaration = (
            "context := scratch.Context{Sprites: map[string]*scratch.ScratchSprite{"
        )

        # All normal sprites
        for sprite in sprites:
            context_declaration += (
                # Clean the name to be in line with the rest of main.go
                # the name isn't already cleaned because ScratchSprite tries to be as close to the projet.json as possible
                f'"{util.clean_name(sprite.name)}": &{util.clean_name(sprite.name)}, '
            )
        context_declaration += f"}}, Stage: &{stage.name}, Variables: map[string]{self.scratchISA_prefix}.ScratchValue{{"
        all_targets: list[ScratchTarget] = []
        all_targets.extend(sprites)
        all_targets.append(stage)
        for target in all_targets:
            for v in target.variables.values():
                context_declaration += f'"{v[0]}":'
                variable_value = v[1]
                if isinstance(variable_value, str):
                    context_declaration += f'{self.scratchISA_prefix}.ValueFromString("{variable_value}"), '
                elif isinstance(variable_value, (int, float)):
                    context_declaration += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({variable_value})), "
        context_declaration += "}"
        context_declaration += (
            f", Lists: map[string][]{self.scratchISA_prefix}.ScratchValue{{"
        )
        for target in all_targets:
            for v in target.lists.values():
                context_declaration += (
                    f'"{v[0]}": []{self.scratchISA_prefix}.ScratchValue{{'
                )
                list_value = v[1]
                for list_item_value in list_value:
                    if isinstance(list_item_value, str):
                        context_declaration += f'{self.scratchISA_prefix}.ValueFromString("{list_item_value}"), '
                    elif isinstance(list_item_value, (int, float)):
                        context_declaration += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({list_item_value})), "
                context_declaration += "}"
        context_declaration += "}}"
        return context_declaration

    def generate_stage(self, stage: ParsedStage) -> TranspiledStage:
        """Transpile the stage, ready for populating the template"""
        goroutines: list[str] = []
        for script in stage.scripts:
            goroutines.append(self.generate_goroutine(stage, script))
        go_sprite_object_declaration = self.generate_stage_object_declaration(stage)
        texture_declarations = self.generate_texture_declarations(stage)
        goroutine_interrupt = self.generate_goroutine_interrupt(stage)
        return TranspiledStage(
            name=stage.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
        )

    def generate_sprite(self, sprite: ParsedSprite) -> TranspiledSprite:
        """Transpile a sprite, ready for populating the template"""
        goroutines: list[str] = []
        for script in sprite.scripts:
            goroutines.append(self.generate_goroutine(sprite, script))
        go_sprite_object_declaration = self.generate_sprite_object_declaration(sprite)
        texture_declarations = self.generate_texture_declarations(sprite)
        goroutine_interrupt = self.generate_goroutine_interrupt(sprite)
        return TranspiledSprite(
            name=sprite.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
            layer_order=sprite.layer_order,
        )

    def generate_custom_blocks(
        self, custom_blocks: list[CustomBlockDeclaration]
    ) -> list[str]:
        functions_list: list[str] = []

        for custom_block in custom_blocks:
            current_function = f"func {custom_block.proc_code}(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, context *{self.scratchISA_prefix}.Context, "
            for input_name in custom_block.input_names:
                # argname scratch.ScratchValue,
                current_function += (
                    input_name + f" {self.scratchISA_prefix}.ScratchValue, "
                )
            current_function += ") {"
            current_function += self.generate_stack(custom_block.body)
            current_function += "}"
            functions_list.append(current_function)

        return functions_list
