from transpiler.generation import Generation
from transpiler.spec_loader import SpecLoader

from . import util
from .scratch_types import (
    BlockCall,
    Expression,
    MenuValue,
    NumberLiteral,
    ScratchBlock,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    StringLiteral,
    TranspiledSprite,
    TranspiledStage,
)


def parse_block(block_dict: dict) -> ScratchBlock:
    return ScratchBlock(
        opcode=block_dict['opcode'],
        next=block_dict.get('next'),
        parent=block_dict.get('parent'),
        inputs=block_dict.get('inputs', {}),
        fields=block_dict.get('fields', {}),
        top_level=block_dict.get('topLevel', False),
    )

def parse_blocks(blocks_dict: dict) -> dict[str, ScratchBlock]:
    blocks = {}
    for key, value in blocks_dict.items():
        blocks[key] = parse_block(value)
    return blocks

def get_sprites(json_dict: dict) -> list[ScratchSprite]:
    sprites = []
    for sprite_dict in json_dict['targets']:
        if not sprite_dict['isStage']:
            sprites.append(ScratchSprite(
                is_stage = sprite_dict['isStage'],
                name = util.clean_sprite_name(sprite_dict['name']),
                blocks = parse_blocks(sprite_dict['blocks']),
                current_costume = sprite_dict['currentCostume'],
                visible = sprite_dict["visible"],
                x = sprite_dict['x'],
                y = sprite_dict['y'],
                size = sprite_dict['size'],
                direction = sprite_dict['direction'],
                layer_order=sprite_dict['layerOrder'],
                costumes=sprite_dict['costumes'],
                variables=sprite_dict["variables"]
            ))
    return sprites

def get_stage(json_dict: dict) -> ScratchStage:
    for i in json_dict['targets']:
        if i['isStage']:
            stage_dict = i
            return ScratchStage(
                name="Stage",
                blocks=parse_blocks(stage_dict["blocks"]),
                current_costume=stage_dict["currentCostume"],
                costumes=stage_dict["costumes"],
                variables=stage_dict["variables"],
            )
    raise ValueError("No stage in sb3")









class Parser:
    def __init__(self):
        self.scratchISA_prefix = "scratch"
        self.context_variable_name = "context"
        self.spec_loader = SpecLoader()
        self.specs = self.spec_loader.get_specs()
        self.generation = Generation(self.scratchISA_prefix)


    def parse_input(self, sprite: ScratchTarget, block: ScratchBlock, input_name: str) -> Expression:
        if block.inputs is None:
            raise ValueError("Block with no inputs passed to parse_input")
        input_contents = block.inputs[input_name]
        input_type = input_contents[0]
        if input_type == 1: #Literal value?

            input_value = input_contents[1]
            if isinstance(input_value, list): #Input is an actual literal
                value_type = input_value[0]
                value = input_value[1]
                if value_type == 10: #String literal
                    return StringLiteral(value)
                elif value_type in [4, 5]: #Number literal
                    return NumberLiteral(value)
                else:
                    raise ValueError(f"unimplemented value type: {value_type} in {block.opcode} input {input_name}")

            elif isinstance(input_value, str):
                #Is a reference to another block
                spec = self.specs[sprite.blocks[input_value].opcode]
                referenced_block = sprite.blocks[input_value]
                if spec.is_menu:
                    #This solution is extremely inelegant and janky
                    if referenced_block.fields is None:
                        raise ValueError("Block menu " + input_value + " has no fields.")
                    return MenuValue(next(iter( referenced_block.fields.values() ))[0])
                else:
                    return self.parse_block(referenced_block, sprite)
            else:
                raise ValueError("input_value is of unexpected type: " + str(type(input_value)))
        elif input_type == 3: #Block sits ontop of another default value?
            return self.parse_block(sprite.blocks[input_contents[1]], sprite)
        else:
            raise ValueError(f"unimplemented input type: {input_type} in {block.opcode} input {input_name}")


    def parse_inputs(self, sprite: ScratchTarget, block: ScratchBlock) -> dict[str, Expression] | None:
        if block.inputs is None:
            return None
        args = {}
        for k in block.inputs:
            args[k] = self.parse_input(sprite, block, k)
        return args

    def parse_fields(self, block: ScratchBlock) -> dict[str, Expression] | None:
        if block.fields is None:
            return None
        args = {}
        for k, v in block.fields.items():
            args[k] = StringLiteral(v[0])
        return args

    def parse_menu_block(self, block: ScratchBlock) -> MenuValue:
        if not block.fields is None:
            #TODO: rework this implementation
            for value in block.fields.values():
                return MenuValue(value[0])
            raise ValueError("unable to parse menu block")
        else:
            raise ValueError("unable to parse menu block")

    def parse_wants(self, block: ScratchBlock) -> list[str]:
        wants = self.specs[block.opcode].wants
        if wants is None: return []
        return wants

    def parse_block(self, block: ScratchBlock, sprite: ScratchTarget) -> BlockCall:
        return BlockCall(
            opcode=self.specs[block.opcode].go_func,
            fields=self.parse_fields(block),
            inputs=self.parse_inputs(sprite, block)
        )


    def parse_stack(self, sprite: ScratchTarget, starting_block_id: str) -> str:
        source_code_list = []
        current_block = sprite.blocks[starting_block_id]

        while current_block is not None:
            if current_block.opcode == "control_forever":
                if current_block.inputs is None:
                    raise ValueError("Forever block has no inputs and therefor no substack.")
                source_code_list.append("for {")
                source_code_list.append(self.parse_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append(f"{self.scratchISA_prefix}.Yield(control)\n}}")
                break #Blocks after forever cannot be breached
            elif current_block.opcode == "control_if":
                if current_block.inputs is None:
                    raise ValueError("If block has no inputs and therefor no substack or condition.")
                source_code_list.append(f"if {self.parse_block(sprite.blocks[current_block.inputs['CONDITION'][1]], sprite)} {{")
                source_code_list.append(self.parse_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append("}")
            elif current_block.opcode == "control_if_else":
                if current_block.inputs is None:
                    raise ValueError("If/else block has no inputs and therefor no substack or condition.")
                source_code_list.append(f"if {self.parse_block(sprite.blocks[current_block.inputs['CONDITION'][1]], sprite)} {{")
                source_code_list.append(self.parse_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append("} else {")
                source_code_list.append(self.parse_stack(sprite, current_block.inputs['SUBSTACK2'][1]))
                source_code_list.append("}")

            else:
                source_code_list.append(self.parse_block(current_block, sprite))
            if current_block.next is None: break
            current_block = sprite.blocks[current_block.next]
        return "\n".join(source_code_list)

    def transpile_stage(self, stage: ScratchStage) -> TranspiledStage:
        goroutines = self.transpile_sprite_goroutines(stage)
        go_sprite_object_declaration = self.generation.generate_stage_object_declaration(stage)
        texture_declarations = self.generation.generate_texture_declarations(stage)
        goroutine_interrupt = f"for _, control := range {stage.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
        costume_declarations = self.generation.transpile_costume_values(stage)
        go_sprite_object_declaration = go_sprite_object_declaration.replace("TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations))
        return TranspiledStage(
            name=stage.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
        )


    def transpile_sprite(self, sprite: ScratchSprite) -> TranspiledSprite:
        goroutines = self.transpile_sprite_goroutines(sprite)
        go_sprite_object_declaration = self.generation.generate_sprite_object_declaration(sprite)
        texture_declarations = self.generation.generate_texture_declarations(sprite)
        goroutine_interrupt = f"for _, control := range {sprite.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
        costume_declarations = self.generation.transpile_costume_values(sprite)
        go_sprite_object_declaration = go_sprite_object_declaration.replace("TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations))
        return TranspiledSprite(
            name=sprite.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
            layer_order=sprite.layer_order,
        )

    def transpile_sprite_goroutines(self, sprite: ScratchTarget) -> list[str]:
        sprite_goroutines = []
        script_count = 0
        for possible_hat_block in sprite.blocks.values():
            if possible_hat_block.opcode == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                script_count += 1
                current_goroutine = f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, {self.context_variable_name} {self.scratchISA_prefix}.Context) {{\n<-control.AwakenChan\n"
                if possible_hat_block.next is None: break
                current_goroutine += self.parse_stack(sprite, possible_hat_block.next)
                current_goroutine += f"\nfor {{ {self.scratchISA_prefix}.Yield(control) }}\n}}({self.context_variable_name}.Sprites[\"{sprite.name}\"], {self.context_variable_name}.Sprites[\"{sprite.name}\"].Controls[{script_count - 1}], {self.context_variable_name})" #negater off by one error
                sprite_goroutines.append(current_goroutine)
        return sprite_goroutines

    def transpile_context(self, sprites: list[ScratchSprite], stage: ScratchStage) -> str:
        context_declaration = f"{self.context_variable_name} := scratch.Context{{Sprites: map[string]*scratch.ScratchSprite{{"

        #All normal sprites
        for sprite in sprites:
            context_declaration += f"\"{sprite.name}\": &{sprite.name}, "

        context_declaration += f"}}, Stage: &Stage, Variables: map[string]{self.scratchISA_prefix}.ScratchValue{{"
        all_targets = []
        all_targets.extend(sprites)
        all_targets.append(stage)
        for target in all_targets:
            for k, v in target.variables.items():
                context_declaration += f"\"{k}\":"
                variable_value = v[1]
                if isinstance(variable_value, str):
                    context_declaration += f"{self.scratchISA_prefix}.ValueFromString(\"{variable_value}\")"
                elif isinstance(variable_value, (int, float)):
                    context_declaration += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({variable_value}))"
        context_declaration += "}}"
        return context_declaration
