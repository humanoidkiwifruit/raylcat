#!/usr/bin/env python3
import json
import os
import pprint  # noqa: F401
import shutil
import subprocess
import sys
import zipfile

commands = ["build", "run"]
#work_dir = "work/"
#compile_dir = work_dir + "compile_dir/"
#sb3_extraction_dir = work_dir + "sb3_extraction_dir/"
#template_dir = "go_templates"
#assets_dir = compile_dir + "assets/"
#self.scratchISA_prefix = "scratch"

class ScratchProject:
    def __init__(self, sb3_path):
        self.sb3_path = sb3_path
        self.template_dir="go_templates"


    def setup_work(self, work_dir="work/"): # Set up the working directory
        self.compile_dir = work_dir + "compile_dir/"
        self.sb3_extraction_dir = work_dir + "sb3_extraction_dir/"
        self.assets_dir = self.compile_dir + "assets/"
        self.scratchISA_prefix = "scratch"

        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
        os.makedirs(work_dir)
        os.makedirs(self.sb3_extraction_dir)
        _ = shutil.copytree(self.template_dir, self.compile_dir)
        os.makedirs(self.assets_dir)

    def extract_sb3_to_work_dir(self):
        with zipfile.ZipFile(self.sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
            if not archive.filename is None:
                self.project_name = archive.filename
            archive.extractall(self.sb3_extraction_dir)
            self.json_text = archive.read("project.json")


    def transpile_block(self, block_dict, sprite_dict):
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


    def transpile_stack(self, sprite_dict, starting_block_id: str):
        source_code_list = []
        blocks_dict = sprite_dict['blocks']
        current_block = blocks_dict[starting_block_id]
        next_block_id = current_block.get('next')

        while not current_block is None:
            if current_block['opcode'] == "control_forever":
                source_code_list.append("for {")
                source_code_list.append(self.transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
                source_code_list.append(f"{self.scratchISA_prefix}.Yield(control)\n}}")
                next_block_id = current_block.get('next')
                if next_block_id is None: break
                current_block = blocks_dict[next_block_id]
                break
            elif current_block['opcode'] == "control_if":
                source_code_list.append(f"if {self.transpile_block(sprite_dict['blocks'][current_block['inputs']['CONDITION'][1]], sprite_dict)} {{")
                source_code_list.append(self.transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
                source_code_list.append("}")
            elif current_block['opcode'] == "control_if_else":
                source_code_list.append(f"if {self.transpile_block(sprite_dict['blocks'][current_block['inputs']['CONDITION'][1]], sprite_dict)} {{")
                source_code_list.append(self.transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
                source_code_list.append("} else {")
                source_code_list.append(self.transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK2'][1]))
                source_code_list.append("}")

            else:
                source_code_list.append(self.transpile_block(current_block, sprite_dict))
            next_block_id = current_block.get('next')
            if next_block_id is None: break
            current_block = blocks_dict[next_block_id]
        return "\n".join(source_code_list)

    def build(self, work_dir="work/"):
        self.setup_work(work_dir)
        self.extract_sb3_to_work_dir()
        project_name = "Scratch Go Raylib"
        self.json_dict = json.loads(self.json_text) #Convert project.json to a python dictionary

        #Template strings
        go_sprite_object_declarations = []
        texture_declarations_go = []
        all_sprite_goroutines = []
        main_func_goroutine_interrupts = []
        ordered_render_sprites = [""] * len(self.json_dict['targets']) #Subtract one to account for the stage
        try:
            self.targets = self.json_dict['targets']
        except KeyError:
            print("Failed to access target information from project. Perhaps your project.json is malformed?")
            return
        for sprite in self.json_dict["targets"]: #Iterate over sprites

            if sprite['isStage'] != True: #Ignore stage sprite for now
                sprite_goroutines = []

                new_name = sprite['name'].replace(" ", "") #Remove whitespaces
                script_count = 0
                for possible_hat_block in sprite['blocks'].values():
                    if possible_hat_block['opcode'] == "event_whenflagclicked": #Only consider scripts that begin with a green flack clicked
                        script_count += 1
                        current_goroutine = "" #Initialise and prevent unassigned errors
                        current_goroutine = f"go func(sprite *{self.scratchISA_prefix}.ScratchSprite, control {self.scratchISA_prefix}.ScratchScriptControl) {{\n<-control.AwakenChan\n"
                        current_goroutine += self.transpile_stack(sprite, possible_hat_block['next'])
                        current_goroutine += f"\n}}(&{new_name}, {new_name}.Controls[{script_count - 1}])" #off by one error
                        sprite_goroutines.append(current_goroutine)
                texture_filename = sprite['costumes'][0]['assetId'] + "." + sprite['costumes'][0]['dataFormat']
                if ".svg" in texture_filename:
                    print("SVG textures not supported.")
                    sys.exit()


                main_func_goroutine_interrupts.append(
                    f"for _, control := range {new_name}.Controls {{\ncontrol.AwakenChan <- true\n<-control.FinishedChan\n}}"
                )
                #main_func_goroutine_interrupts.append("control.AwakenChan <- true")
                #main_func_goroutine_interrupts.append("<-control.FinishedChan")
                #main_func_goroutine_interrupts.append("}")
                shutil.copy(self.sb3_extraction_dir + texture_filename, self.assets_dir + texture_filename) #Copy textures to the compilation directory
                if len(sprite_goroutines) != 0:
                    all_sprite_goroutines.extend(sprite_goroutines)
                sprite_go = f"{new_name} := {self.scratchISA_prefix}.ScratchSprite{{X: {sprite['x']}, Y: {sprite['y']}, Size: {sprite['size']}, Direction: {sprite['direction']}, CostumeNumber: 0, Texture: {new_name}_texture, Show: {  'true' if sprite['visible'] else 'false'  }, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{" #Instantiate go Scratch_Sprite objects
                print('counter is: ', script_count)
                for i in range(script_count):
                    sprite_go += "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
                sprite_go += "}}"
                go_sprite_object_declarations.append(sprite_go)
                texture_declarations_go.append(f"{new_name}_texture := rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({new_name}_texture)") #Instantiate raylib textures
                ordered_render_sprites[sprite['layerOrder']] = f"{self.scratchISA_prefix}.DrawSprite(&{new_name})"

        #Read the template main.go
        with open(self.compile_dir + "/main.go", "r") as original_file:
            main_go = original_file.read()

        #Fill templates
        main_go = main_go.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(go_sprite_object_declarations))
        main_go = main_go.replace("//TEMPLATING:TEXTURES", "\n".join(texture_declarations_go))
        main_go = main_go.replace("//TEMPLATING:RENDER_SPRITES", "\n".join(ordered_render_sprites)) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
        main_go = main_go.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(all_sprite_goroutines))
        main_go = main_go.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(main_func_goroutine_interrupts))
        main_go = main_go.replace("//TEMPLATING:NAME", project_name)

        #Write to main.go file
        with open(self.compile_dir + "main.go", "w") as file:
            file.write(main_go)

if len(sys.argv) > 1:
    command = sys.argv[1]
    if len(sys.argv) > 2:
        sb3_path = sys.argv[2]
        if command == "build":
            project = ScratchProject(sb3_path)
            project.setup_work()
            project.extract_sb3_to_work_dir()
            project.build()
        elif command == "run":
            project = ScratchProject(sb3_path)
            project.setup_work()
            project.extract_sb3_to_work_dir()
            project.build()
            _ = subprocess.run(["go", "run", "."], cwd=project.compile_dir, capture_output=False, text=True, check=True)

    elif command in commands:
        print("Please specify an sb3 path.")
    else:
        print("Invalid command.")
else:
    print(f"Please specify a command. Options are {commands}.")
