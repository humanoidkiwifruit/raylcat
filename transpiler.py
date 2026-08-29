#!/usr/bin/env python3
import json
import os
import pprint  # noqa: F401
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path  # noqa: F401

commands = ["build", "run"]

@dataclass
class ScratchSprite:
    name: str
    is_stage: bool
    blocks: dict
    current_costume: int
    layer_order: int
    visible: bool
    x: float
    y: float
    size: float
    direction: float

@dataclass
class SpriteTranspilation:
    name: str
    goroutines: list[str]
    go_sprite_object_declaration: str
    texture_declaration: str
    goroutine_interrupt: str
    go_render: str


class ScratchProject:
    def __init__(self, sb3_path):
        self.sb3_path = sb3_path
        self.template_dir="go_templates/"
        self.scratchISA_prefix = "scratch"


    def setup_work(self, work_dir="work/"): # Set up the working directory
        self.template_dir = Path("go_templates")
        self.work_dir = Path(work_dir)
        self.compile_dir = self.work_dir / "compile_dir"
        self.sb3_extraction_dir = self.work_dir / "sb3_extraction"
        self.assets_dir = self.compile_dir / "assets"

        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        os.makedirs(work_dir)
        os.makedirs(self.sb3_extraction_dir)
        _ = shutil.copytree(self.template_dir, self.compile_dir)
        os.makedirs(self.assets_dir)

    def read_json(self):
        with open(self.sb3_extraction_dir / "project.json", "r", encoding="utf-8") as file:
            self.json_text = file.read()
        self.json_dict = json.loads(self.json_text) #Convert project.json to a python dictionary


    def extract_sb3_to_work_dir(self):
        with zipfile.ZipFile(self.sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
            if not archive.filename is None:
                self.project_name = archive.filename
            archive.extractall(self.sb3_extraction_dir)
            archive.extractall(self.assets_dir)


    def populate_main_go_template(self, go_sprite_object_declarations, go_texture_declarations, go_ordered_render_sprites, all_sprite_goroutines, main_func_goroutine_interrupts, project_name) -> str:
        with open(self.template_dir / "main.go", "r") as original_file:
            main_go_file_str = original_file.read()
        print("AAAAAA", go_sprite_object_declarations)
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(go_sprite_object_declarations))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:TEXTURES", "\n".join(go_texture_declarations))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:RENDER_SPRITES", "\n".join(go_ordered_render_sprites)) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(all_sprite_goroutines))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(main_func_goroutine_interrupts))
        main_go_file_str = main_go_file_str.replace("//TEMPLATING:NAME", project_name)
        return main_go_file_str

    def transpile_block(self, block_dict, sprite_dict) -> str:
        new_opcode = block_dict['opcode'].capitalize()
        line = f"{self.scratchISA_prefix}.{new_opcode}(sprite, "
        inputs = block_dict.get('inputs', {})
        for argname, i in inputs.items(): # noqa: PERF102 #ignoreing in case argname is needed in future

            if i[0] == 1:
                if i[1][0] == 10:
                    value = i[1][1]
                    line += f"{self.scratchISA_prefix}.ValueFromString(\"{value}\")"
                else:
                    try:
                        value = float(i[1][1])
                    except ValueError:
                        value = 0.0
                    line += f"{self.scratchISA_prefix}.ValueFromFloat64({value})"
            elif i[0] == 2 or i[0] == 3:
                line += self.transpile_block(sprite_dict['blocks'][i[1]], sprite_dict)
            else:
                print("Something is wrong")
            line += ", "

        line += ")"
        return line


    def transpile_stack(self, sprite_index, starting_block_id: str) -> str:
        sprite_dict = self.sprite_index_to_dict(sprite_index)
        source_code_list = []
        blocks_dict = sprite_dict['blocks']
        current_block = blocks_dict[starting_block_id]
        next_block_id = current_block.get('next')

        while not current_block is None:
            if current_block['opcode'] == "control_forever":
                source_code_list.append("for {")
                source_code_list.append(self.transpile_stack(sprite_index, current_block['inputs']['SUBSTACK'][1]))
                source_code_list.append(f"{self.scratchISA_prefix}.Yield(control)\n}}")
                next_block_id = current_block.get('next')
                if next_block_id is None: break
                current_block = blocks_dict[next_block_id]
                break
            elif current_block['opcode'] == "control_if":
                source_code_list.append(f"if {self.transpile_block(sprite_dict['blocks'][current_block['inputs']['CONDITION'][1]], sprite_dict)} {{")
                source_code_list.append(self.transpile_stack(sprite_index, current_block['inputs']['SUBSTACK'][1]))
                source_code_list.append("}")
            elif current_block['opcode'] == "control_if_else":
                source_code_list.append(f"if {self.transpile_block(sprite_dict['blocks'][current_block['inputs']['CONDITION'][1]], sprite_dict)} {{")
                source_code_list.append(self.transpile_stack(sprite_index, current_block['inputs']['SUBSTACK'][1]))
                source_code_list.append("} else {")
                source_code_list.append(self.transpile_stack(sprite_index, current_block['inputs']['SUBSTACK2'][1]))
                source_code_list.append("}")

            else:
                source_code_list.append(self.transpile_block(current_block, sprite_dict))
            next_block_id = current_block.get('next')
            if next_block_id is None: break
            current_block = blocks_dict[next_block_id]
        return "\n".join(source_code_list)

    def sprite_index_to_dict(self, sprite_index) -> dict:
        return self.json_dict['targets'][sprite_index]

    def cleaned_sprite_name(self, sprite_index) -> str:
        sprite_dict = self.sprite_index_to_dict(sprite_index)
        return sprite_dict['name'].replace(" ", "")

    def number_of_scripts(self, sprite_index) -> int:
        sprite_dict = self.sprite_index_to_dict(sprite_index)
        script_count = 0
        for possible_hat_block in sprite_dict['blocks'].values():
            if possible_hat_block['opcode'] == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                script_count += 1
        return script_count

    def generate_sprite_object_declaration(self, sprite_index) -> str:
        new_name = self.cleaned_sprite_name(sprite_index)
        sprite_dict = self.sprite_index_to_dict(sprite_index)
        go_object_declaration = f"{new_name} := {self.scratchISA_prefix}.ScratchSprite{{X: {sprite_dict['x']}, Y: {sprite_dict['y']}, Size: {sprite_dict['size']}, Direction: {sprite_dict['direction']}, CostumeNumber: 0, Texture: {new_name}_texture, Show: {  'true' if sprite_dict['visible'] else 'false'  }, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        for i in range(self.number_of_scripts(sprite_index)):
            go_object_declaration += "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
        go_object_declaration += "}}"
        return go_object_declaration


    def generate_texture_declaration(self, sprite_index) -> str:
        new_name = self.cleaned_sprite_name(sprite_index)
        sprite_dict = self.sprite_index_to_dict(sprite_index)
        texture_filename = sprite_dict['costumes'][0]['assetId'] + "." + sprite_dict['costumes'][0]['dataFormat']
        return f"{new_name}_texture := rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({new_name}_texture)" #Instantiate raylib textures



    def transpile_sprite(self, sprite_index) -> SpriteTranspilation:
        #sprite_dict = self.json_dict['targets'][sprite_index]

        name = self.cleaned_sprite_name(sprite_index)
        goroutines = self.transpile_sprite_goroutines(sprite_index)
        go_sprite_object_declaration = self.generate_sprite_object_declaration(sprite_index)
        texture_declaration = self.generate_texture_declaration(sprite_index)
        goroutine_interrupt = f"for _, control := range {name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
        go_render = self.generate_go_render(sprite_index)
        return SpriteTranspilation(
            name=name,
            goroutines=goroutines,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declaration=texture_declaration,
            goroutine_interrupt=goroutine_interrupt,
            go_render=go_render
        )

    def generate_go_render(self, sprite_index):
        name = self.cleaned_sprite_name(sprite_index)
        return f"{self.scratchISA_prefix}.DrawSprite(&{name})"

    def transpile_sprite_goroutines(self, sprite_index) -> list[str]:
        sprite_dict = self.sprite_index_to_dict(sprite_index)
        sprite_goroutines = []

        new_name = self.cleaned_sprite_name(sprite_index)
        script_count = 0
        for possible_hat_block in sprite_dict['blocks'].values():
            if possible_hat_block['opcode'] == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                script_count += 1
                current_goroutine = f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl) {{\n<-control.AwakenChan\n"
                current_goroutine += self.transpile_stack(sprite_index, possible_hat_block['next'])
                current_goroutine += f"\n}}(&{new_name}, {new_name}.Controls[{script_count - 1}])" #off by one error
                sprite_goroutines.append(current_goroutine)
        return sprite_goroutines


    def build(self, work_dir="work/"):
        self.setup_work(work_dir)
        self.extract_sb3_to_work_dir()
        self.read_json()
        project_name = "Scratch Go Raylib"

        #Template strings
        go_sprite_object_declarations = []
        go_texture_declarations = []
        all_sprite_goroutines = []
        main_func_goroutine_interrupts = []
        go_ordered_render_sprites = [""] * len(self.json_dict['targets']) #Subtract one to account for the stage
        print(self.transpile_sprite(1))
        for index, sprite in enumerate(self.json_dict["targets"]): #Iterate over sprites

            if sprite['isStage'] != True: #Ignore stage sprite for now
                transpiled_sprite = self.transpile_sprite(index)

                if len(transpiled_sprite.goroutines) != 0:
                    all_sprite_goroutines.extend(transpiled_sprite.goroutines)

                go_sprite_object_declarations.append(transpiled_sprite.go_sprite_object_declaration)
                go_texture_declarations.append(transpiled_sprite.texture_declaration) #Instantiate raylib textures
                go_ordered_render_sprites[sprite['layerOrder']] = self.generate_go_render(index)
                main_func_goroutine_interrupts.append(f"for _, control := range {transpiled_sprite.name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}")

        #Read the template main.go
        with open(self.compile_dir / "main.go", "r") as original_file:
            main_go_file_str = original_file.read()

        #Fill templates
        main_go_file_str = self.populate_main_go_template(
            go_sprite_object_declarations=go_sprite_object_declarations,
            go_texture_declarations=go_texture_declarations,
            go_ordered_render_sprites=go_ordered_render_sprites,
            all_sprite_goroutines=all_sprite_goroutines,
            main_func_goroutine_interrupts=main_func_goroutine_interrupts,
            project_name=project_name
        )

        #Write to main.go file
        with open(self.compile_dir / "main.go", "w") as file:
            file.write(main_go_file_str)

if len(sys.argv) > 1:
    command = sys.argv[1]
    if len(sys.argv) > 2:
        sb3_path = sys.argv[2]
        if command == "build":
            project = ScratchProject(sb3_path)
            project.build()
        elif command == "run":
            project = ScratchProject(sb3_path)
            project.build()
            _ = subprocess.run(["go", "run", "."], cwd=project.compile_dir, capture_output=False, text=True, check=True)

    elif command in commands:
        print("Please specify an sb3 path.")
    else:
        print("Invalid command.")
else:
    print(f"Please specify a command. Options are {commands}.")
