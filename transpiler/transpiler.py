import json

from .generation import Generation
from .scratch_types import ScratchBlock, ScratchSprite, TranspiledSprite
from .spec_loader import SpecLoader


class Transpiler:
    def __init__(self):
        self.scratchISA_prefix = "scratch"
        self.context_variable_name = "context"
        self.spec_loader = SpecLoader()
        self.specs = self.spec_loader.get_specs()
        self.generation = Generation(self.scratchISA_prefix)




    def opcode_to_go_func_call(self, opcode: str) -> str:
        return self.specs[opcode].go_func


    def transpile_input(self, sprite: ScratchSprite, block: ScratchBlock, input_name: str) -> str:
        i = block.inputs[input_name]
        input_type = i[0]
        line = ""
        if input_type == 1:
            input_value = i[1]
            if isinstance(input_value, list):
                #Input is a literal
                value_type = input_value[0]
                #value_data = input_value[1]
                if value_type == 10:
                    value = input_value[1]
                    line += f"{self.scratchISA_prefix}.ValueFromString(\"{value}\")"
                else:
                    try:
                        value = float(i[1][1])
                    except ValueError:
                        value = 0.0
                    line += f"{self.scratchISA_prefix}.ValueFromFloat64({value})"
            elif isinstance(input_value, str):
                #Is a reference to another block
                spec = self.specs[sprite.blocks[input_value].opcode]
                referenced_block = sprite.blocks[input_value]
                if spec.is_menu:
                    #This solution is extremely inelegant and janky
                    line += f"{self.scratchISA_prefix}.ValueFromString(\"" + next(iter( referenced_block.fields.values() ))[0] + "\")"
                else:
                    line += self.transpile_block(referenced_block, sprite)
        elif i[0] == 2 or i[0] == 3:
            line += self.transpile_block(sprite.blocks[i[1]], sprite)
        else:
            print("Something is wrong")
        return line


    def transpile_inputs(self, sprite: ScratchSprite, block: ScratchBlock) -> list[str]:
        args = []
        for key in block.inputs:
            args.append(self.transpile_input(sprite, block, key))
        return args

    def transpile_fields(self, block: ScratchBlock) -> list[str]:
        args = []
        for v in block.fields.values():
            args.append(f"{self.scratchISA_prefix}.ValueFromString(\"{v[0]}\")")
        return args

    def transpile_menu_block(self, block: ScratchBlock) -> str:
        if not block.fields is None:
            for value in block.fields.values():
                return f"{self.scratchISA_prefix}.ValueFromString(\"{value[0]}\")"
        return ""

    def transpile_wants(self, block: ScratchBlock) -> list[str]:
        wants = self.specs[block.opcode].wants
        if wants is None: return []
        return wants

    def transpile_block(self, block: ScratchBlock, sprite: ScratchSprite) -> str:
        new_opcode = self.opcode_to_go_func_call(block.opcode)
        args = []
        args.extend(self.transpile_wants(block))
        args.extend(self.transpile_inputs(sprite, block))
        args.extend(self.transpile_fields(block))
        return f"{self.scratchISA_prefix}.{new_opcode}({", ".join(args)})"


    def transpile_stack(self, sprite: ScratchSprite, starting_block_id: str) -> str:
        source_code_list = []
        current_block = sprite.blocks[starting_block_id]
        next_block_id = current_block.next

        while current_block is not None:
            if current_block.opcode == "control_forever":
                source_code_list.append("for {")
                source_code_list.append(self.transpile_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append(f"{self.scratchISA_prefix}.Yield(control)\n}}")
                break #Blocks after forever cannot be breached
            elif current_block.opcode == "control_if":
                source_code_list.append(f"if {self.transpile_block(sprite.blocks[current_block.inputs['CONDITION'][1]], sprite)} {{")
                source_code_list.append(self.transpile_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append("}")
            elif current_block.opcode == "control_if_else":
                source_code_list.append(f"if {self.transpile_block(sprite.blocks[current_block.inputs['CONDITION'][1]], sprite)} {{")
                source_code_list.append(self.transpile_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append("} else {")
                source_code_list.append(self.transpile_stack(sprite, current_block.inputs['SUBSTACK2'][1]))
                source_code_list.append("}")

            else:
                source_code_list.append(self.transpile_block(current_block, sprite))
            if current_block.next is None: break
            current_block = sprite.blocks[current_block.next]
        return "\n".join(source_code_list)



    def transpile_sprite(self, sprite: ScratchSprite) -> TranspiledSprite:
        goroutines = self.transpile_sprite_goroutines(sprite)
        go_sprite_object_declaration = self.generation.generate_sprite_object_declaration(sprite)
        texture_declarations = self.generation.generate_texture_declarations(sprite)
        goroutine_interrupt = f"for _, control := range {sprite.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
        go_render = self.generation.generate_go_render(sprite)
        costume_declarations = self.generation.transpile_costume_values(sprite)
        go_sprite_object_declaration = go_sprite_object_declaration.replace("TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations))
        return TranspiledSprite(
            name=sprite.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            goroutine_interrupt=goroutine_interrupt,
            go_render=go_render,
            layer_order=sprite.layer_order,
        )

    def transpile_sprite_goroutines(self, sprite: ScratchSprite) -> list[str]:
        sprite_goroutines = []
        script_count = 0
        for possible_hat_block in sprite.blocks.values():
            if possible_hat_block.opcode == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                script_count += 1
                current_goroutine = f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl, {self.context_variable_name} {self.scratchISA_prefix}.Context) {{\n<-control.AwakenChan\n"
                if possible_hat_block.next is None: break
                current_goroutine += self.transpile_stack(sprite, possible_hat_block.next)
                current_goroutine += f"\nfor {{ {self.scratchISA_prefix}.Yield(control) }}\n}}({self.context_variable_name}.Sprites[\"{sprite.name}\"], {self.context_variable_name}.Sprites[\"{sprite.name}\"].Controls[{script_count - 1}], {self.context_variable_name})" #negater off by one error
                sprite_goroutines.append(current_goroutine)
        return sprite_goroutines
