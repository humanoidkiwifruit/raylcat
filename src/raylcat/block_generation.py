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
    ProcedureCall,
    RepeatStatement,
    RepeatUntilStatement,
    Statement,
    StringLiteral,
    TraditionalStatement,
    ValueType,
    WaitUntilStatement,
)
from .spec_loader import SpecLoader


class BlockGeneration:
    def __init__(self, scratchISA_prefix: str):
        self.scratchISA_prefix: str = scratchISA_prefix
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()

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
            raise TypeError(
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

    def generate_custom_blocks(
        self, custom_blocks: list[CustomBlockDeclaration]
    ) -> list[str]:
        functions_list: list[str] = []

        for custom_block in custom_blocks:
            current_function = f"func {custom_block.proc_code}(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, context *{self.scratchISA_prefix}.Context, "
            for input in custom_block.inputs:
                # argname scratch.ScratchValue,
                current_function += input.name + (
                    f" {self.scratchISA_prefix}.ScratchValue, "
                    if input.type is ValueType.SCRATCH_VALUE
                    else " bool, "
                )
            current_function += ") {"
            current_function += self.generate_stack(custom_block.body)
            current_function += "}"
            functions_list.append(current_function)

        return functions_list
