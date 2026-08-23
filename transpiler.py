#!/usr/bin/env python3
import json
import os
import pprint  # noqa: F401
import shutil
import subprocess
import sys
import zipfile

work_dir = "work/"
compile_dir = work_dir + "compile_dir/"
sb3_extraction_dir = work_dir + "sb3_extraction_dir/"
template_dir = "go_templates"
assets_dir = compile_dir + "assets/"
scratchISA_prefix = "scratch"

commands = ["build", "run"]

def setup_work(): # Set up the working directory
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    os.makedirs(sb3_extraction_dir)
    _ = shutil.copytree(template_dir, compile_dir)
    os.makedirs(assets_dir)

def transpile_block(block_dict, sprite_dict):
    new_opcode = block_dict['opcode'].capitalize()
    line = f"{scratchISA_prefix}.{new_opcode}(sprite, "
    inputs = block_dict.get('inputs', {})
    for argname, i in inputs.items():

        if i[0] == 1:
            if i[1][0] == 10:
                value = i[1][1]
                line += f"{scratchISA_prefix}.ValueFromString(\"{value}\")"
            else:
                try:
                    value = float(i[1][1])
                except ValueError:
                    value = 0.0
                line += f"{scratchISA_prefix}.ValueFromFloat64({value})"
        elif i[0] == 2 or i[0] == 3:
            line += transpile_block(sprite_dict['blocks'][i[1]], sprite_dict)
        else:
            print("Something is wrong")
        line += ", "

    line += ")"
    return line


def transpile_stack(sprite_dict, starting_block_id: str):
    source_code_list = []
    blocks_dict = sprite_dict['blocks']
    current_block = blocks_dict[starting_block_id]
    next_block_id = current_block.get('next')

    while not current_block is None:
        if current_block['opcode'] == "control_forever":
            source_code_list.append("for {")
            source_code_list.append(transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
            source_code_list.append(f"{scratchISA_prefix}.Yield(control)\n}}")
            next_block_id = current_block.get('next')
            if next_block_id is None: break
            current_block = blocks_dict[next_block_id]
            break
        elif current_block['opcode'] == "control_if":
            source_code_list.append(f"if {transpile_block(sprite_dict['blocks'][current_block['inputs']['CONDITION'][1]], sprite_dict)} {{")
            source_code_list.append(transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
            source_code_list.append("}")
        elif current_block['opcode'] == "control_if_else":
            source_code_list.append(f"if {transpile_block(sprite_dict['blocks'][current_block['inputs']['CONDITION'][1]], sprite_dict)} {{")
            source_code_list.append(transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
            source_code_list.append("} else {")
            source_code_list.append(transpile_stack(sprite_dict, current_block['inputs']['SUBSTACK2'][1]))
            source_code_list.append("}")

        else:
            source_code_list.append(transpile_block(current_block, sprite_dict))
        next_block_id = current_block.get('next')
        if next_block_id is None: break
        current_block = blocks_dict[next_block_id]
    return "\n".join(source_code_list)

def build(sb3_path: str):
    setup_work()
    project_name = "Scratch Go Raylib"
    with zipfile.ZipFile(sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
        if not archive.filename is None:
            project_name = archive.filename
        archive.extractall(sb3_extraction_dir)
        json_text = archive.read("project.json")



    json_dict = json.loads(json_text) #Convert project.json to a python dictionary

    #Template strings
    go_objects = []
    textures_go = []
    all_sprite_goroutines = []
    main_func_goroutine_interrupts = []
    ordered_render_sprites = [""] * len(json_dict['targets']) #Subtract one to account for the stage


    for sprite in json_dict["targets"]: #Iterate over sprites

        if sprite['isStage'] != True: #Ignore stage sprite
            script_goroutine = "" # prevent script_goroutine from being unbound
            sprite_scripts = []

            new_name = sprite['name'].replace(" ", "") #Remove whitespaces
            number_of_scripts_in_sprite = 0
            for possible_hat_block in sprite['blocks'].values():
                if possible_hat_block['opcode'] == "event_whenflagclicked":
                    number_of_scripts_in_sprite += 1
                    script_goroutine = f"go func(sprite *{scratchISA_prefix}.ScratchSprite, control {scratchISA_prefix}.ScratchScriptControl) {{\n<-control.AwakenChan\n"
                    script_goroutine += transpile_stack(sprite, possible_hat_block['next'])
                    script_goroutine += f"\n}}(&{new_name}, {new_name}.Controls[{number_of_scripts_in_sprite - 1}])" #off by one error
                    sprite_scripts.append(script_goroutine)
            texture_filename = sprite['costumes'][0]['assetId'] + "." + sprite['costumes'][0]['dataFormat']
            if ".svg" in texture_filename:
                print("SVG textures not supported.")
                sys.exit()
                break


            #main_func_goroutine_interrupts.append(f"{new_name}.AwakenChan <- true\n<-{new_name}.FinishedChan")
            main_func_goroutine_interrupts.append(f"for _, gate := range {new_name}.Controls {{")
            main_func_goroutine_interrupts.append("gate.AwakenChan <- true")
            main_func_goroutine_interrupts.append("<-gate.FinishedChan")
            main_func_goroutine_interrupts.append("}")
            shutil.copy(sb3_extraction_dir + texture_filename, assets_dir + texture_filename) #Copy textures to the compilation directory
            if script_goroutine != "":
                all_sprite_goroutines.extend(sprite_scripts)
            sprite_go = f"{new_name} := {scratchISA_prefix}.ScratchSprite{{X: {sprite['x']}, Y: {sprite['y']}, Size: {sprite['size']}, Direction: {sprite['direction']}, CostumeNumber: 0, Texture: {new_name}_texture, Show: {  'true' if sprite['visible'] else 'false'  }, Controls: []{scratchISA_prefix}.ScratchScriptControl{{" #Instantiate go Scratch_Sprite objects
            print('counter is: ', number_of_scripts_in_sprite)
            for i in range(number_of_scripts_in_sprite):
                sprite_go += "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            sprite_go += "}}"
            go_objects.append(sprite_go)
            textures_go.append(f"{new_name}_texture := rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({new_name}_texture)") #Instantiate raylib textures
            ordered_render_sprites[sprite['layerOrder']] = f"{scratchISA_prefix}.DrawSprite(&{new_name})"

    #Read the template main.go
    with open(compile_dir + "/main.go", "r") as original_file:
        main_go = original_file.read()

    #Fill templates
    main_go = main_go.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(go_objects))
    main_go = main_go.replace("//TEMPLATING:TEXTURES", "\n".join(textures_go))
    main_go = main_go.replace("//TEMPLATING:RENDER_SPRITES", "\n".join(ordered_render_sprites)) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
    main_go = main_go.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(all_sprite_goroutines))
    main_go = main_go.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(main_func_goroutine_interrupts))
    main_go = main_go.replace("//TEMPLATING:NAME", project_name)

    #Write to main.go file
    with open(compile_dir + "main.go", "w") as file:
        file.write(main_go)

if len(sys.argv) > 1:
    command = sys.argv[1]
    if len(sys.argv) > 2:
        sb3_path = sys.argv[2]
        if command == "build":
            build(sb3_path)
        elif command == "run":
            build(sb3_path)
            _ = subprocess.run(["go", "run", "."], cwd=compile_dir, capture_output=False, text=True, check=True)

    elif command in commands:
        print("Please specify an sb3 path.")
    else:
        print("Invalid command.")
else:
    print(f"Please specify a command. Options are {commands}.")
