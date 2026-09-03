import subprocess
from pathlib import Path

from . import parsing, sb3_archive, workspaces
from .scratch_types import ScratchBlock, ScratchSprite, TranspiledSprite


class ScratchProject:
    def __init__(self, sb3_path):
        self.template_dir = Path("go_templates/")
        self.scratchISA_prefix = "scratch"
        self.workspace = workspaces.Workspace()
        self.sb3 = sb3_archive.Sb3_archive(sb3_path)

    def extract(self):
        self.sb3.extract_to(self.workspace.sb3_extraction_dir)
        self.sb3.extract_to(self.workspace.assets_dir)

    def opcode_to_go_func_call(self, opcode: str) -> str:
        return opcode.capitalize()


    def transpile_input(self, sprite: ScratchSprite, block: ScratchBlock, input_name: str) -> str:
        i = block.inputs[input_name]
        input_type = i[0]
        line = ""
        if input_type == 1:
            input_value = i[1]
            if isinstance(input_value, list):
                #Input is a literal
                value_type = input_value[0]
                value_data = input_value[1]
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
                line += self.transpile_block(sprite.blocks[input_value], sprite)
        elif i[0] == 2 or i[0] == 3:
            line += self.transpile_block(sprite.blocks[i[1]], sprite)
        else:
            print("Something is wrong")
        return line


    def transpile_inputs(self, sprite: ScratchSprite, block: ScratchBlock):
        args = []
        for key in block.inputs:
            args.append(self.transpile_input(sprite, block, key))
        return args

    def transpile_fields(self, sprite: ScratchSprite, block: ScratchBlock):
        args = []
        for v in block.fields.values():
            args.append(f"{self.scratchISA_prefix}.ValueFromString(\"{v[0]}\")")
        return args

    def transpile_menu_block(self, block: ScratchBlock):
        if not block.fields is None:
            for value in block.fields.values():
                return f"{self.scratchISA_prefix}.ValueFromString(\"{value[0]}\")"
        return

    def transpile_block(self, block: ScratchBlock, sprite: ScratchSprite) -> str:
        new_opcode = self.opcode_to_go_func_call(block.opcode)
        args = []
        args.extend(self.transpile_inputs(sprite, block))
        args.extend(self.transpile_fields(sprite, block))
        return f"{self.scratchISA_prefix}.{new_opcode}(sprite, {", ".join(args)})"


    def transpile_stack(self, sprite: ScratchSprite, starting_block_id: str) -> str:
        source_code_list = []
        current_block = sprite.blocks[starting_block_id]
        next_block_id = current_block.next

        while not current_block is None:
            if current_block.opcode == "control_forever":
                source_code_list.append("for {")
                source_code_list.append(self.transpile_stack(sprite, current_block.inputs['SUBSTACK'][1]))
                source_code_list.append(f"{self.scratchISA_prefix}.Yield(control)\n}}")
                next_block_id = current_block.next
                if next_block_id is None: break
                current_block = sprite.blocks[next_block_id]
                break
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
            next_block_id = current_block.next
            if next_block_id is None: break
            current_block = sprite.blocks[next_block_id]
        return "\n".join(source_code_list)


    def number_of_scripts(self, sprite: ScratchSprite) -> int:
        script_count = 0
        for possible_hat_block in sprite.blocks.values():
            if possible_hat_block.opcode == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                script_count += 1
        return script_count

    def generate_sprite_object_declaration(self, sprite: ScratchSprite) -> str:
        go_object_declaration = f"{sprite.name} := {self.scratchISA_prefix}.ScratchSprite{{X: {sprite.x}, Y: {sprite.y}, Size: {sprite.size}, Direction: {sprite.direction}, CostumeNumber: 0, Texture: {sprite.name}_texture, Show: {  'true' if sprite.visible else 'false'  }, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        for i in range(self.number_of_scripts(sprite)):
            go_object_declaration += "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
        go_object_declaration += "}}"
        return go_object_declaration


    def generate_texture_declaration(self, sprite: ScratchSprite) -> str:
        texture_filename = sprite.costumes[0]['assetId'] + "." + sprite.costumes[0]['dataFormat']
        return f"{sprite.name}_texture := rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({sprite.name}_texture)" #Instantiate raylib textures



    def transpile_sprite(self, sprite: ScratchSprite) -> TranspiledSprite:
        goroutines = self.transpile_sprite_goroutines(sprite)
        go_sprite_object_declaration = self.generate_sprite_object_declaration(sprite)
        texture_declaration = self.generate_texture_declaration(sprite)
        goroutine_interrupt = f"for _, control := range {sprite.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
        go_render = self.generate_go_render(sprite)
        return TranspiledSprite(
            name=sprite.name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declaration=texture_declaration,
            goroutine_interrupt=goroutine_interrupt,
            go_render=go_render,
            layer_order=sprite.layer_order,
        )

    def generate_go_render(self, sprite: ScratchSprite) -> str:
        return f"{self.scratchISA_prefix}.DrawSprite(&{sprite.name})"

    def transpile_sprite_goroutines(self, sprite: ScratchSprite) -> list[str]:
        sprite_goroutines = []
        script_count = 0
        for possible_hat_block in sprite.blocks.values():
            if possible_hat_block.opcode == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                script_count += 1
                current_goroutine = f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl) {{\n<-control.AwakenChan\n"
                if possible_hat_block.next is None: break
                current_goroutine += self.transpile_stack(sprite, possible_hat_block.next)
                current_goroutine += f"\nfor {{ {self.scratchISA_prefix}.Yield(control) }}\n}}(&{sprite.name}, {sprite.name}.Controls[{script_count - 1}])" #off by one error
                sprite_goroutines.append(current_goroutine)
        return sprite_goroutines

    def generate_main_go(self, transpiled_sprites: list[TranspiledSprite]) -> str:
        go_sprite_object_declarations = []
        go_texture_declarations = []
        all_sprite_goroutines = []
        main_func_goroutine_interrupts = []
        go_ordered_render_sprites = [""] * len(self.json_dict['targets']) #Subtract one to account for the stage
        for transpiled_sprite in transpiled_sprites:
            all_sprite_goroutines.extend(transpiled_sprite.goroutines)
            go_sprite_object_declarations.append(transpiled_sprite.go_sprite_object_declaration)
            go_texture_declarations.append(transpiled_sprite.texture_declaration)
            go_ordered_render_sprites[transpiled_sprite.layer_order] = f"&{transpiled_sprite.name},"
            #go_ordered_render_sprites[0] = transpiled_sprite.go_render
            main_func_goroutine_interrupts.append(transpiled_sprite.goroutine_interrupt)

        #Fill templates
        initial_render_order = (
            f"{self.scratchISA_prefix}.OrderedRender = []*{self.scratchISA_prefix}.ScratchSprite{{\n"
            + str( "\n".join(go_ordered_render_sprites) ) #needs to be casted to a string for some reason
            + "\n}"
        )
        main_go_file_str = self.workspace.populate_main_go_template(
            go_sprite_object_declarations=go_sprite_object_declarations,
            go_texture_declarations=go_texture_declarations,
            go_ordered_render_sprites=go_ordered_render_sprites,
            all_sprite_goroutines=all_sprite_goroutines,
            main_func_goroutine_interrupts=main_func_goroutine_interrupts,
            project_name="Scratch Go Raylib",
            initial_render_order=initial_render_order,
        )

        return main_go_file_str

    def build(self, work_dir="work/"):
        self.workspace.setup()
        self.extract()
        self.json_dict = self.sb3.read_json_to_dict()

        sprites = parsing.get_sprites(self.json_dict)
        transpiled_sprites = []
        for sprite in sprites:
            transpiled_sprites.append(self.transpile_sprite(sprite))
        main_go_str = self.generate_main_go(transpiled_sprites)
        self.workspace.write_main_go(main_go_str)

    def run(self):
        _ = subprocess.run(["go", "run", "."], cwd=self.workspace.compile_dir, capture_output=False, text=True, check=True)
