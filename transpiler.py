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

def transpile_block(block_dict):
    line = f"{scratchISA_prefix}.{block_dict['opcode']}(sprite, "
    inputs = block_dict.get('inputs', {})
    for argname, i in inputs.items():
        if i[1][0] == 10:
            value = i[1][1]
            line += f"{argname.lower()}={scratchISA_prefix}.create_value_from_string(\"{value}\"), "
        else:
            try:
                value = float(i[1][1])
            except ValueError:
                value = 0.0
            line += f"{argname.lower()}={scratchISA_prefix}.create_value_from_f64({value}), "
    line += ")"
    return line


def transpile(sprite_dict, starting_block_id: str, current_state: int):
    source_code_list = []
    blocks_dict = sprite_dict['blocks']
    #current_state = 0
    current_block = blocks_dict[starting_block_id]
    next_block_id = current_block.get('next')

    source_code_list.append(f"case {current_state}:")
    while not current_block is None:
        if current_block['opcode'] == "control_forever":
            current_state += 1
            source_code_list.append(f"sprite.script_state = {current_state}")
            source_code_list.append("fallthrough")
            source_code_list.append(transpile(sprite_dict, current_block['inputs']['SUBSTACK'][1], current_state))
            next_block_id = current_block.get('next')
            if next_block_id is None: break
            current_block = blocks_dict[next_block_id]
            break

        source_code_list.append(transpile_block(current_block))
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
    tick_funcs_go = []
    sprite_tick_proc_calls = []
    ordered_render_sprites = [""] * len(json_dict['targets']) #Subtract one to account for the stage


    for i in json_dict["targets"]: #Iterate over sprites

        if i['isStage'] != True: #Ignore stage sprite
            tick_func_go = "" # prevent tick_func_go from being unbound

            new_name = i['name'].replace(" ", "") #Remove whitespaces
            for possible_hat_block in i['blocks'].values():
                if possible_hat_block['opcode'] == "event_whenflagclicked":
                    tick_func_go = "switch sprite.script_state {\n"
                    tick_func_go += transpile(i, possible_hat_block['next'], 0)
                    tick_func_go += "}"
            texture_filename = i['costumes'][0]['assetId'] + "." + i['costumes'][0]['dataFormat']
            if ".svg" in texture_filename:
                print("SVG textures not supported.")
                break
            if i['visible']:
                i_is_visible = "true"
            else:
                i_is_visible = "false"

            sprite_tick_proc_calls.append(new_name + f"_tick(&{new_name})")
            shutil.copy(sb3_extraction_dir + texture_filename, assets_dir + texture_filename) #Copy textures to the compilation directory
            if tick_func_go != "":
                tick_funcs_go.append(f"{new_name}_tick :: proc(sprite: ^{scratchISA_prefix}.Scratch_Sprite) {{\n" + tick_func_go + "\n}")
            go_objects.append(f"{new_name} := {scratchISA_prefix}.Scratch_Sprite{{{i['x']}, {i['y']}, {i['size']}, {i['direction']}, 0, {new_name}_texture, {i_is_visible}, 0}}") #Instantiate go Scratch_Sprite objects
            textures_go.append(f"{new_name}_texture: rl.Texture2D = rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({new_name}_texture)") #Instantiate raylib textures
            ordered_render_sprites[i['layerOrder']] = f"{scratchISA_prefix}.scratch_draw_sprite(&{new_name})"

    #Read the template main.go
    with open(compile_dir + "/main.go", "r") as original_file:
        main_go = original_file.read()

    #Fill templates
    main_go = main_go.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(go_objects))
    main_go = main_go.replace("//TEMPLATING:TEXTURES", "\n".join(textures_go))
    main_go = main_go.replace("//TEMPLATING:RENDER_SPRITES", "\n".join(ordered_render_sprites)) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
    main_go = main_go.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(tick_funcs_go))
    main_go = main_go.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(sprite_tick_proc_calls))
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
