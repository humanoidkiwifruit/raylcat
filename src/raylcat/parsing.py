from typing import Any

from . import util
from .generation import Generation
from .scratch_types import (
    AccessVariable,
    BlockCall,
    BlockSpec,
    Expression,
    ForeverStatement,
    IfElseStatement,
    IfStatement,
    InputTypes,
    MenuValue,
    NumberLiteral,
    RepeatStatement,
    RepeatUntilStatement,
    ScratchBlock,
    ScratchCostume,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    SpriteScript,
    Statement,
    StringLiteral,
    TraditionalStatement,
    TranspiledSprite,
    TranspiledStage,
    WaitUntilStatement,
)
from .spec_loader import SpecLoader


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
    )


def parse_blocks(blocks_dict: dict[str, dict[str, Any]]) -> dict[str, ScratchBlock]:
    """Parse a sprite's blocks to dict of strings -> ScratchBlocks"""
    blocks: dict[str, ScratchBlock] = {}
    for key, value in blocks_dict.items():
        blocks[key] = parse_block(value)
    return blocks


def parse_sprites(json_dict: dict[str, Any]) -> list[ScratchSprite]:
    """Parse the sprites to a list of ScratchSprites"""
    sprites: list[ScratchSprite] = []
    for sprite_dict in json_dict["targets"]:
        if not sprite_dict["isStage"]:
            sprites.append(
                ScratchSprite(
                    is_stage=sprite_dict["isStage"],
                    name=util.clean_sprite_name(sprite_dict["name"]),
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
                )
            )
    return sprites


def parse_stage(json_dict: dict[str, Any]) -> ScratchStage:
    """Parse the stage to a ScratchStage"""
    for target in json_dict["targets"]:
        if target["isStage"]:
            stage_dict = target
            return ScratchStage(
                name="Stage",
                blocks=parse_blocks(stage_dict["blocks"]),
                current_costume=stage_dict["currentCostume"],
                costumes=parse_costumes(stage_dict["costumes"]),
                variables=stage_dict["variables"],
            )
    raise ValueError("No stage in sb3")


class Parser:
    def __init__(self):
        self.scratchISA_prefix: str = "scratch"
        self.context_variable_name: str = "context"
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()
        self.generation: Generation = Generation(self.scratchISA_prefix)

    def parse_input(
        self, sprite: ScratchTarget, block: ScratchBlock, input_name: str
    ) -> Expression:
        """Parse a block's input name to an Expression."""
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
                ]:  # Number, positive number or positive integer respectively
                    return NumberLiteral(value)
                else:
                    raise ValueError(
                        f"Unimplemented value type: {value_type} in {block.opcode} input {input_name}"
                    )

            elif isinstance(input_value, str):
                # Is a reference to another block
                spec = self.specs[sprite.blocks[input_value].opcode]
                referenced_block = sprite.blocks[input_value]
                if spec.is_menu:
                    # This solution is extremely inelegant and janky
                    if referenced_block.fields is None:
                        raise ValueError(
                            "Block menu " + input_value + " has no fields."
                        )
                    return MenuValue(next(iter(referenced_block.fields.values()))[0])
                else:
                    return self.parse_block(referenced_block, sprite)
            else:
                raise ValueError(
                    "input_value is of unexpected type: " + str(type(input_value))
                )
        elif (
            input_type == 2
        ):  # Block sits ontop of another default value? 2 is used in if statements.
            return self.parse_block(sprite.blocks[input_contents[1]], sprite)
        elif input_type == 3:  # Variable shadows default value?
            if isinstance(input_contents[1], list) and input_contents[1][0] == 12:
                return AccessVariable(variable_name=input_contents[1][1])
            elif isinstance(input_contents[1], str):
                return self.parse_block(sprite.blocks[input_contents[1]], sprite)
            raise ValueError(
                "input_contents[1] is of unexpected type: "
                + str(type(input_contents[1]))
            )
        else:
            raise ValueError(
                f"unimplemented input type: {input_type} in {block.opcode} input {input_name}"
            )

    def parse_inputs(
        self, sprite: ScratchTarget, block: ScratchBlock
    ) -> dict[str, Expression] | None:
        """Parse all of a block's inputs to a dict of names to Expressions."""
        if block.inputs is None:
            return None
        args: dict[str, Expression] = {}
        for k in block.inputs:
            args[k] = self.parse_input(sprite, block, k)
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

    def parse_block(self, block: ScratchBlock, sprite: ScratchTarget) -> BlockCall:
        """Parse a block to a BlockCall"""
        return BlockCall(
            opcode=block.opcode,
            fields=self.parse_fields(block),
            inputs=self.parse_inputs(sprite, block),
        )

    def parse_stack(
        self, sprite: ScratchTarget, starting_block_id: str
    ) -> list[Statement]:
        """Parse a stack to a list of Statements."""
        stack_list: list[Statement] = []
        current_block = sprite.blocks[starting_block_id]

        while not current_block is None:
            if current_block.opcode == "control_forever":
                if current_block.inputs is None:
                    raise ValueError(
                        "Forever block has no inputs and therefor no substack."
                    )
                stack_list.append(
                    ForeverStatement(
                        body=self.parse_stack(
                            sprite, util.get_substack_first_block_id(current_block)
                        )
                    )
                )
                break  # Blocks after forever cannot be breached
            elif current_block.opcode == "control_if":
                if current_block.inputs is None:
                    raise ValueError(
                        "If block has no inputs and therefore no substack or condition."
                    )
                stack_list.append(
                    IfStatement(
                        condition=self.parse_input(sprite, current_block, "CONDITION"),
                        body=self.parse_stack(
                            sprite, util.get_substack_first_block_id(current_block)
                        ),
                    )
                )
            elif current_block.opcode == "control_if_else":
                if current_block.inputs is None:
                    raise ValueError(
                        "If/else block has no inputs and therefore no substack or condition."
                    )
                stack_list.append(
                    IfElseStatement(
                        condition=self.parse_input(sprite, current_block, "CONDITION"),
                        then_body=self.parse_stack(
                            sprite, util.get_substack_first_block_id(current_block)
                        ),
                        else_body=self.parse_stack(
                            sprite, current_block.inputs["SUBSTACK2"][1]
                        ),
                    )
                )
            elif current_block.opcode == "control_repeat":
                if current_block.inputs is None:
                    raise ValueError(
                        "Repeat block has no inputs and therefore no number of repetitions or substack"
                    )
                stack_list.append(
                    RepeatStatement(
                        times=self.parse_input(sprite, current_block, "TIMES"),
                        body=self.parse_stack(
                            sprite, util.get_substack_first_block_id(current_block)
                        ),
                    )
                )
            elif current_block.opcode == "control_wait_until":
                if current_block.inputs is None:
                    raise ValueError(
                        "Wait until block has no inputs and therefore no substack or condition."
                    )
                stack_list.append(
                    WaitUntilStatement(
                        condition=self.parse_input(sprite, current_block, "CONDITION")
                    )
                )
            elif current_block.opcode == "control_repeat_until":
                if current_block.inputs is None:
                    raise ValueError(
                        "Repeat until block has no inputs and therefore no substack or condition."
                    )
                stack_list.append(
                    RepeatUntilStatement(
                        condition=self.parse_input(sprite, current_block, "CONDITION"),
                        substack=self.parse_stack(
                            sprite, util.get_substack_first_block_id(current_block)
                        ),
                    )
                )
            else:
                stack_list.append(
                    TraditionalStatement(self.parse_block(current_block, sprite))
                )
            if current_block.next is None:
                break
            current_block = sprite.blocks[current_block.next]
        return stack_list

    def transpile_stage(self, stage: ScratchStage) -> TranspiledStage:
        """Transpile the stage, ready for populating the template"""
        scripts = self.parse_sprite_scripts(stage)
        goroutines: list[str] = []
        for script in scripts:
            goroutines.append(self.generation.generate_goroutine(stage, script))
        go_sprite_object_declaration = (
            self.generation.generate_stage_object_declaration(stage)
        )
        texture_declarations = self.generation.generate_texture_declarations(stage)
        goroutine_interrupt = f"for _, control := range {stage.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
        costume_declarations = self.generation.transpile_costume_values(stage)
        go_sprite_object_declaration = go_sprite_object_declaration.replace(
            "TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations)
        )
        return TranspiledStage(
            name=stage.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
        )

    def transpile_sprite(self, sprite: ScratchSprite) -> TranspiledSprite:
        """Transpile a sprite, ready for populating the template"""
        scripts = self.parse_sprite_scripts(sprite)
        goroutines: list[str] = []
        for script in scripts:
            goroutines.append(self.generation.generate_goroutine(sprite, script))
        go_sprite_object_declaration = (
            self.generation.generate_sprite_object_declaration(sprite)
        )
        texture_declarations = self.generation.generate_texture_declarations(sprite)
        goroutine_interrupt = self.generation.generate_goroutine_interrupt(sprite)
        costume_declarations = self.generation.transpile_costume_values(sprite)
        go_sprite_object_declaration = go_sprite_object_declaration.replace(
            "TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations)
        )
        return TranspiledSprite(
            name=sprite.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
            layer_order=sprite.layer_order,
        )

    def parse_sprite_scripts(self, sprite: ScratchTarget) -> list[SpriteScript]:
        sprite_goroutines: list[SpriteScript] = []
        script_count = 0
        for possible_hat_block in sprite.blocks.values():
            if (
                possible_hat_block.opcode == "event_whenflagclicked"
            ):  # Only consider scripts that begin with a green flack clicked
                script_count += 1
                if possible_hat_block.next is None:
                    continue
                body = self.parse_stack(sprite, possible_hat_block.next)
                sprite_goroutines.append(
                    SpriteScript(body=body, control_index=script_count)
                )
        return sprite_goroutines

    def transpile_context(
        self, sprites: list[ScratchSprite], stage: ScratchStage
    ) -> str:
        context_declaration = f"{self.context_variable_name} := scratch.Context{{Sprites: map[string]*scratch.ScratchSprite{{"

        # All normal sprites
        for sprite in sprites:
            context_declaration += f'"{sprite.name}": &{sprite.name}, '

        context_declaration += f"}}, Stage: &Stage, Variables: map[string]{self.scratchISA_prefix}.ScratchValue{{"
        all_targets: list[ScratchTarget] = []
        all_targets.extend(sprites)
        all_targets.append(stage)
        for target in all_targets:
            for k, v in target.variables.items():
                context_declaration += f'"{k}":'
                variable_value = v[1]
                if isinstance(variable_value, str):
                    context_declaration += (
                        f'{self.scratchISA_prefix}.ValueFromString("{variable_value}")'
                    )
                elif isinstance(variable_value, (int, float)):
                    context_declaration += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({variable_value}))"
        context_declaration += "}}"
        return context_declaration
