import logging

from raylcat import util

from .spec_loader import SpecLoader
from .types import (
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

logger = logging.getLogger(__name__)


class BlockGeneration:
    """Mega class that contains all the logic for generating go code from blocks"""

    def __init__(self, scratchISA_prefix: str):
        self.scratchISA_prefix: str = scratchISA_prefix
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()

    def generate_expression(self, expression: Expression) -> str:
        """Generate go code for different expression types"""
        if isinstance(expression, (StringLiteral, MenuValue)):
            return f"{self.scratchISA_prefix}.ValueFromString(`{expression.value}`)"
        elif isinstance(expression, NumberLiteral):
            return f"{self.scratchISA_prefix}.ValueFromFloat64(float64({expression.value}))"
        elif isinstance(expression, BlockCall):
            return self.generate_block_call(expression)
        elif isinstance(expression, AccessVariable):
            return f"{self.scratchISA_prefix}.GetVariableValue(sprite, context, `{expression.variable_name}`)"
        elif isinstance(expression, AccessFunctionArgument):  # pyright: ignore[reportUnnecessaryIsInstance]
            return expression.argument_name
        else:
            raise TypeError(
                f"Unimplemented Expression type {type(expression)} in generate_expression()"
            )  # pyright: ignore[reportUnreachable]

    def generate_block_call(self, block_call: BlockCall) -> str:
        """generate go code for calling a scratch function with arguments: Wants, Inputs, Fields"""
        block_call_str = (
            f"{self.scratchISA_prefix}.{self.specs[block_call.opcode].go_func}("
        )
        args: list[str] = []
        wants = self.specs[block_call.opcode].wants
        block_call = self.sanitise_block_call(block_call)
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

    def sanitise_block_call(self, block_call: BlockCall) -> BlockCall:
        """Currently only serves the job of satitising variable/list names."""

        if self.specs[block_call.opcode].category == "data":
            logger.debug("Generating block call for data block")
            assert not block_call.fields is None, (
                "A data block's fields should never be none."
            )
            if "LIST" in block_call.fields:
                list_field = block_call.fields[
                    "LIST"
                ]  # Simple helper, modifying this will not modify the original
                if not isinstance(list_field, StringLiteral):
                    raise TypeError(
                        "Block call field LIST is of unexpected type",
                        type(list_field),
                    )
                    # Clean the name
                block_call.fields["LIST"].value = util.clean_name(list_field.value)  # pyright: ignore[reportAttributeAccessIssue] we have already determined that the LIST argument is of the correct type

            elif "VARIABLE" in block_call.fields:
                variable_field = block_call.fields[
                    "VARIABLE"
                ]  # Simple helper, modifying this will not modify the original
                if not isinstance(variable_field, StringLiteral):
                    raise TypeError(
                        "Block call field VARIABLE is of unexpected type",
                        type(variable_field),
                        " should be a string literal",
                    )
                    # Clean the name
                block_call.fields["VARIABLE"].value = util.clean_name(  # pyright: ignore[reportAttributeAccessIssue] we have already determined that the VARIABLE argument is of the correct type
                    variable_field.value
                )
        return block_call

    def generate_stack(self, stack: list[Statement]) -> str:
        """Generate multiline go code from a list of statements. Used to transpile the mouth of an if statement, for example."""
        stack_list: list[str] = []
        for statement in stack:
            stack_list.append(self.generate_statement(statement))
        return "\n".join(stack_list)

    def generate_statement(self, statement: Statement) -> str:
        """Generate go code for just 1 statement. Handles if/else/while blocks too."""
        statement_list: list[str] = []
        if isinstance(statement, TraditionalStatement):
            # Normal no-return-value statement, eg move 10 steps.
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

        elif isinstance(statement, ProcedureCall):  # pyright: ignore[reportUnnecessaryIsInstance]
            # Call a custom block
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
            )  # pyright: ignore[reportUnreachable]

    def generate_custom_blocks(
        self, custom_blocks: list[CustomBlockDeclaration]
    ) -> list[str]:
        """Generate declarations for custom blocks. Automatically take in all possible arguments in case they are needed"""
        functions_list: list[str] = []

        for custom_block in custom_blocks:
            current_function = f"func {custom_block.proc_code}(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, context *{self.scratchISA_prefix}.Context, "
            for block_input in custom_block.inputs:
                # argname scratch.ScratchValue,
                current_function += block_input.name + (
                    f" {self.scratchISA_prefix}.ScratchValue, "
                    if block_input.type is ValueType.SCRATCH_VALUE
                    else " bool, "
                )
            current_function += ") {"
            current_function += self.generate_stack(custom_block.body)
            current_function += "}"
            functions_list.append(current_function)

        return functions_list
