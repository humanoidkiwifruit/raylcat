import json
import logging
from typing import Any

from . import util
from .generation import Generation
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
    InputTypes,
    MenuValue,
    NumberLiteral,
    ParsedSprite,
    ParsedStage,
    ProcedureCall,
    RepeatStatement,
    RepeatUntilStatement,
    ScratchBlock,
    ScratchCostume,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    Statement,
    StringLiteral,
    TargetScript,
    TraditionalStatement,
    WaitUntilStatement,
)
from .spec_loader import SpecLoader

logger = logging.getLogger(__name__)


def parse_costumes(costumes: list[dict[str, Any]]) -> list[ScratchCostume]:
    """Parse the costumes to a list of ScratchCostumes"""
    new_costumes_list: list[ScratchCostume] = []
    for costume in costumes:
        new_costumes_list.append(
            ScratchCostume(
                name=costume["name"],
                bitmap_resolution=costume.get("bitmapResolution"),
                data_format=costume["dataFormat"],
                md5ext=costume["md5ext"],
                asset_id=costume["assetId"],
                rotation_centre_x=costume["rotationCenterX"],
                rotation_centre_y=costume["rotationCenterY"],
            )
        )
    return new_costumes_list


def parse_block(block_dict: dict[str, Any]) -> ScratchBlock:
    """Parse a block dict to ScratchBlock"""
    return ScratchBlock(
        opcode=block_dict["opcode"],
        next=block_dict.get("next"),
        parent=block_dict.get("parent"),
        inputs=block_dict.get("inputs", {}),
        fields=block_dict.get("fields", {}),
        top_level=block_dict.get("topLevel", False),
        mutation=block_dict.get("mutation"),
    )


def parse_blocks(blocks_dict: dict[str, dict[str, Any]]) -> dict[str, ScratchBlock]:
    """Parse a target's blocks to dict of strings -> ScratchBlocks"""
    blocks: dict[str, ScratchBlock] = {}
    for key, value in blocks_dict.items():
        blocks[key] = parse_block(value)
    return blocks


class Parser:
    def __init__(self):
        self.scratchISA_prefix: str = "scratch"
        self.context_variable_name: str = "context"
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()
        self.generation: Generation = Generation(self.scratchISA_prefix)

    def get_stage(self, json_dict: dict[str, Any]) -> ScratchStage:
        """Parse the stage to a ScratchStage"""
        for target in json_dict["targets"]:
            if target["isStage"]:
                logger.debug("Getting stage as ScratchStage")
                stage_dict = target
                return ScratchStage(
                    name="Stage",
                    blocks=parse_blocks(stage_dict["blocks"]),
                    current_costume=stage_dict["currentCostume"],
                    costumes=parse_costumes(stage_dict["costumes"]),
                    variables=stage_dict["variables"],
                    lists=stage_dict["lists"],
                )
        raise ValueError("No stage in sb3")

    def get_sprites(self, json_dict: dict[str, Any]):
        sprites: list[ScratchSprite] = []
        for sprite_dict in json_dict["targets"]:
            if not sprite_dict["isStage"]:
                logger.debug(f"Getting sprite {sprite_dict['name']} as ScratchSprite")
                sprites.append(
                    ScratchSprite(
                        # Do not clean the name yet
                        name=sprite_dict["name"],
                        blocks=parse_blocks(sprite_dict["blocks"]),
                        current_costume=sprite_dict["currentCostume"],
                        visible=sprite_dict["visible"],
                        x=sprite_dict["x"],
                        y=sprite_dict["y"],
                        size=sprite_dict["size"],
                        direction=sprite_dict["direction"],
                        layer_order=sprite_dict["layerOrder"],
                        costumes=parse_costumes(sprite_dict["costumes"]),
                        variables=sprite_dict["variables"],
                        lists=sprite_dict["lists"],
                    )
                )
        return sprites

    def parse_sprites(self, sprites: list[ScratchSprite]) -> list[ParsedSprite]:
        """Parse the sprites to a list of ScratchSprites"""
        parsed_sprites: list[ParsedSprite] = []
        for sprite in sprites:
            logger.debug(f"Parsing sprite {sprite.name}")
            parsed_sprites.append(
                ParsedSprite(
                    # Now we clean the name
                    name=util.clean_name(sprite.name),
                    current_costume=sprite.current_costume,
                    visible=sprite.visible,
                    x=sprite.x,
                    y=sprite.y,
                    size=sprite.size,
                    direction=sprite.direction,
                    layer_order=sprite.layer_order,
                    costumes=sprite.costumes,
                    variables=self.parse_initial_variables(sprite),
                    scripts=self.parse_target_scripts(sprite),
                )
            )
        return parsed_sprites

    def parse_stage(self, stage: ScratchStage) -> ParsedStage:
        logger.debug("Parsing stage")
        return ParsedStage(
            name=stage.name,
            current_costume=stage.current_costume,
            costumes=stage.costumes,
            variables=self.parse_initial_variables(stage),
            scripts=self.parse_target_scripts(stage),
        )

    def parse_initial_variables(self, target: ScratchTarget) -> dict[str, Expression]:
        initial_variables: dict[str, Expression] = {}
        for name, value in target.variables.items():
            initial_variables[name] = value[1]
        return initial_variables

    def parse_input(
        self, target: ScratchTarget, block: ScratchBlock, input_name: str
    ) -> Expression:
        """Parse a block's input name to an Expression."""
        logger.debug(f"Parsing {input_name} of {block.opcode}")
        if block.inputs is None:
            raise ValueError("Block with no inputs passed to parse_input")
        input_contents = block.inputs[input_name]
        input_type = input_contents[0]
        if input_type == 1:  # Literal value? Except sometimes it isn't
            input_value = input_contents[1]
            if isinstance(input_value, list):  # Input is an actual literal
                value_type = input_value[0]
                value = input_value[1]
                if value_type == InputTypes.STRING:  # String literal
                    return StringLiteral(value)
                elif value_type in [
                    InputTypes.NUMBER,
                    InputTypes.POSITIVE_NUMBER,
                    InputTypes.POSITIVE_INTEGER,
                    InputTypes.INTEGER,
                ]:  # Number, positive number or positive integer respectively
                    return NumberLiteral(value)
                else:
                    raise ValueError(
                        f"Unimplemented value type: {value_type} in {block.opcode} input {input_name}"
                    )

            elif isinstance(input_value, str):
                # Is a reference to another block
                spec = self.specs[target.blocks[input_value].opcode]
                referenced_block = target.blocks[input_value]
                if spec.is_menu:
                    # This solution is extremely inelegant and janky
                    if referenced_block.fields is None:
                        raise ValueError(
                            "Block menu " + input_value + " has no fields."
                        )
                    return MenuValue(next(iter(referenced_block.fields.values()))[0])
                else:
                    return self.parse_block(referenced_block, target)
            else:
                raise ValueError(
                    "input_value is of unexpected type: " + str(type(input_value))
                )
        elif (
            input_type == 2
        ):  # Block sits ontop of another default value? 2 is used in if statements.
            return self.parse_block(target.blocks[input_contents[1]], target)
        elif input_type == 3:  # Variable shadows default value?
            if isinstance(input_contents[1], list) and input_contents[1][0] == 12:
                return AccessVariable(variable_name=input_contents[1][1])
            elif isinstance(input_contents[1], str):
                return self.parse_block(target.blocks[input_contents[1]], target)
            raise ValueError(
                "input_contents[1] is of unexpected type: "
                + str(type(input_contents[1]))
            )
        else:
            raise ValueError(
                f"unimplemented input type: {input_type} in {block.opcode} input {input_name}"
            )

    def parse_inputs(
        self, target: ScratchTarget, block: ScratchBlock
    ) -> dict[str, Expression] | None:
        """Parse all of a block's inputs to a dict of names to Expressions."""
        if block.inputs is None:
            return None
        args: dict[str, Expression] = {}
        for k in block.inputs:
            args[k] = self.parse_input(target, block, k)
        return args

    def parse_fields(self, block: ScratchBlock) -> dict[str, Expression] | None:
        """Parse all of a block's fields to a dict of names to Expressions."""
        if block.fields is None:
            return None
        args: dict[str, Expression] = {}
        for k, v in block.fields.items():
            args[k] = StringLiteral(v[0])
        return args

    def parse_menu_block(self, block: ScratchBlock) -> MenuValue:
        if not block.fields is None:
            # TODO: rework this implementation
            for value in block.fields.values():
                return MenuValue(value[0])
            raise ValueError("Unable to parse menu block")
        else:
            raise ValueError("Unable to parse menu block")

    def parse_wants(self, block: ScratchBlock) -> list[str]:
        wants = self.specs[block.opcode].wants
        if wants is None:
            return []
        return wants

    def parse_block(self, block: ScratchBlock, target: ScratchTarget) -> Expression:
        """Parse a block to a BlockCall"""
        logger.debug(f"Parsing block of opcode {block.opcode}")
        if block.opcode in ["argument_reporter_string_number"]:
            return AccessFunctionArgument(block.fields["VALUE"][0])
        return BlockCall(
            opcode=block.opcode,
            fields=self.parse_fields(block),
            inputs=self.parse_inputs(target, block),
        )

    def parse_stack(
        self, target: ScratchTarget, starting_block_id: str
    ) -> list[Statement]:
        """Parse a stack to a list of Statements."""
        logger.debug(
            f"Parsing target {target.name} stack starting with block id {starting_block_id} opcode {target.blocks[starting_block_id].opcode}"
        )
        stack_list: list[Statement] = []
        current_block = target.blocks[starting_block_id]

        while not current_block is None:
            stack_list.append(self.parse_statement(current_block, target))
            if current_block.next is None:
                break
            current_block = target.blocks[current_block.next]
        return stack_list

    def parse_statement(self, block: ScratchBlock, target: ScratchTarget) -> Statement:
        if block.opcode == "control_forever":
            logger.debug("Forever block detected.")
            if block.inputs is None:
                raise ValueError(
                    "Forever block has no inputs and therefore no substack."
                )
            return ForeverStatement(
                body=self.parse_stack(target, util.get_substack_first_block_id(block))
            )
        elif block.opcode == "control_if":
            logger.debug("If statement detected.")
            if block.inputs is None:
                raise ValueError(
                    "If block has no inputs and therefore no substack or condition."
                )
            return IfStatement(
                condition=self.parse_input(target, block, "CONDITION"),
                body=self.parse_stack(target, util.get_substack_first_block_id(block)),
            )
        elif block.opcode == "control_if_else":
            logger.debug("If/else statement detected.")
            if block.inputs is None:
                raise ValueError(
                    "If/else block has no inputs and therefore no substack or condition."
                )
            return IfElseStatement(
                condition=self.parse_input(target, block, "CONDITION"),
                then_body=self.parse_stack(
                    target, util.get_substack_first_block_id(block)
                ),
                else_body=self.parse_stack(target, block.inputs["SUBSTACK2"][1]),
            )
        elif block.opcode == "control_repeat":
            logger.debug("repeat x times block detected.")
            if block.inputs is None:
                raise ValueError(
                    "Repeat block has no inputs and therefore no number of repetitions or substack"
                )
            return RepeatStatement(
                times=self.parse_input(target, block, "TIMES"),
                body=self.parse_stack(target, util.get_substack_first_block_id(block)),
            )
        elif block.opcode == "control_wait_until":
            logger.debug("Wait until block detected.")
            if block.inputs is None:
                raise ValueError(
                    "Wait until block has no inputs and therefore no substack or condition."
                )
            return WaitUntilStatement(
                condition=self.parse_input(target, block, "CONDITION")
            )
        elif block.opcode == "control_repeat_until":
            logger.debug("Repeat until block detected.")
            if block.inputs is None:
                raise ValueError(
                    "Repeat until block has no inputs and therefore no substack or condition."
                )
            return RepeatUntilStatement(
                condition=self.parse_input(target, block, "CONDITION"),
                substack=self.parse_stack(
                    target, util.get_substack_first_block_id(block)
                ),
            )
        elif block.opcode == "procedures_call":
            logger.debug("Custom block procedure call detected.")
            if block.mutation is None:
                raise ValueError(
                    "Custom block procedure call's mutation field is None and therefore the call is invalid"
                )
            # We need to clean here also because the cleaning that happens when parsing the declaration is separate.
            return ProcedureCall(util.clean_name(block.mutation["proccode"]))
        else:
            return TraditionalStatement(self.parse_block(block, target))

    def parse_target_scripts(self, target: ScratchTarget) -> list[TargetScript]:
        logger.debug(f"Parsing the scripts of target {target.name}")
        target_goroutines: list[TargetScript] = []
        script_count = 0
        for possible_hat_block in target.blocks.values():
            if (
                possible_hat_block.opcode == "event_whenflagclicked"
            ):  # Only consider scripts that begin with a green flack clicked
                script_count += 1
                if possible_hat_block.next is None:
                    continue
                body = self.parse_stack(target, possible_hat_block.next)
                target_goroutines.append(
                    TargetScript(body=body, control_index=script_count)
                )
        return target_goroutines

    def parse_custom_block_declarations(
        self, targets: list[ScratchTarget]
    ) -> list[CustomBlockDeclaration]:
        logger.debug("Parsing all targets for custom block declarations.")
        declarations: list[CustomBlockDeclaration] = []
        for target in targets:
            for k, possible_declaration_block in target.blocks.items():
                if possible_declaration_block.opcode == "procedures_definition":
                    if (
                        possible_declaration_block.next is None
                        or possible_declaration_block.inputs is None
                    ):
                        raise ValueError(
                            f"Custom block {k} procedure definition lacks field(s) therefore is invalid"
                        )
                    prototype_block_id: str = possible_declaration_block.inputs[
                        "custom_block"
                    ][1]
                    prototype_block = target.blocks[prototype_block_id]
                    if prototype_block.mutation is None:
                        raise ValueError(
                            f"Custom block {k} procedure definition lacks field(s) therefore is invalid"
                        )
                    declarations.append(
                        CustomBlockDeclaration(
                            proc_code=util.clean_name(
                                prototype_block.mutation["proccode"]
                            ),
                            body=self.parse_stack(
                                target, possible_declaration_block.next
                            ),
                            input_names=json.loads(
                                str(prototype_block.mutation["argumentnames"])
                            ),
                        )
                    )
                    print("declarations -1: ", declarations[-1])
        return declarations
