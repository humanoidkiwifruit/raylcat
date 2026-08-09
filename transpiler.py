#!/usr/bin/env python3
import json
import os
import pprint  # noqa: F401
import shutil
import subprocess
import sys
from tracemalloc import start
from turtle import st
import zipfile

work_dir = "work/"
odin_compile_dir = work_dir + "odin_compile_dir/"
sb3_extraction_dir = work_dir + "sb3_extraction_dir/"
odin_template_dir = "odin_templates"
assets_dir = odin_compile_dir + "assets/"
odin_scratchISA_prefix = "scratch"

commands = ["build", "run"]

def setup_work(): # Set up the working directory
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    os.makedirs(sb3_extraction_dir)
    shutil.copytree(odin_template_dir, odin_compile_dir)
    os.makedirs(assets_dir)

def transpile_block(block_dict):
    #print(f"transpile block called {block_dict}")
    line = f"{odin_scratchISA_prefix}.{block_dict['opcode']}(sprite, "
    inputs = block_dict.get('inputs', {})
    for key, i in inputs.items():
        if i[1][0] == 10:
            value = i[1][1]
            line += f"{odin_scratchISA_prefix}.create_value_from_string(\"{value}\"), "
        else:
            try:
                value = float(i[1][1])
            except:
                value = 0.0
            line += f"{odin_scratchISA_prefix}.create_value_from_f64({value}), "
    line += ")"
    return line


def transpile_to_odin(sprite_dict, starting_block_id):
    print(f"transpile to odin called: {sprite_dict['blocks'][starting_block_id]['opcode']}")
    odin_list = []
    blocks_dict = sprite_dict['blocks']
    current_state = 0
    current_block = blocks_dict[starting_block_id]
    next_block_id = current_block.get('next')

    '''
    if not next_block_id: #Check if the hat block actually has any code under it
        return
    '''

    odin_list.append("switch sprite.script_state {")
    odin_list.append(f"case {current_state}:")
    while not current_block is None:
        if current_block['opcode'] == "control_forever":
            odin_list.append("fallthrough")
            current_state += 1
            odin_list.append(f"case {current_state}:")
            print("calling transpile_to_odin from itself")
            odin_list.append(transpile_to_odin(sprite_dict, current_block['inputs']['SUBSTACK'][1]))
            next_block_id = current_block.get('next')
            if next_block_id is None: break
            current_block = blocks_dict[next_block_id]
            continue

        odin_list.append(transpile_block(current_block))
        next_block_id = current_block.get('next')
        if next_block_id is None: break
        current_block = blocks_dict[next_block_id]
    odin_list.append("}")
    print(f"transpile to odin : odin list {odin_list}")
    return "\n".join(odin_list)

def build(sb3_path):
    setup_work()
    project_name = "Scratch Odin Raylib"
    with zipfile.ZipFile(sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
        project_name = archive.filename
        archive.extractall(sb3_extraction_dir)
        json_text = archive.read("project.json")



    json_dict = json.loads(json_text) #Convert project.json to a python dictionary

    #Template strings
    objects_odin = []
    textures_odin = []
    tick_procs_odin = []
    sprite_tick_proc_calls = []
    ordered_render_sprites = [""] * len(json_dict['targets']) #Subtract one to account for the stage


    for i in json_dict["targets"]: #Iterate over sprites

        if i['isStage'] != True: #Ignore stage sprite

            new_name = i['name'].replace(" ", "") #Remove whitespaces
            for id, possible_hat_block in i['blocks'].items():
                if possible_hat_block['opcode'] == "event_whenflagclicked":
                    print("about to call transpile to odin")
                    tick_proc_odin = transpile_to_odin(i, possible_hat_block['next'])
            texture_filename = i['costumes'][0]['md5ext']
            if ".svg" in texture_filename:
                print("SVG textures not supported.")
                break
            if i['visible']:
                i_is_visible = "true"
            else:
                i_is_visible = "false"

            sprite_tick_proc_calls.append(new_name + f"_tick(&{new_name})")
            shutil.copy(sb3_extraction_dir + texture_filename, assets_dir + texture_filename) #Copy textures to the compilation directory
            tick_procs_odin.append(f"{new_name}_tick :: proc(sprite: ^{odin_scratchISA_prefix}.Scratch_Sprite) {{\n" + tick_proc_odin + "\n}")
            objects_odin.append(f"{new_name} := {odin_scratchISA_prefix}.Scratch_Sprite{{{i['x']}, {i['y']}, {i['size']}, {i['direction']}, 0, {new_name}_texture, {i_is_visible}, 0}}") #Instantiate odin Scratch_Sprite objects
            textures_odin.append(f"{new_name}_texture: rl.Texture2D = rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({new_name}_texture)") #Instantiate raylib textures
            ordered_render_sprites[i['layerOrder']] = f"{odin_scratchISA_prefix}.scratch_draw_sprite(&{new_name})"

    #Read the template main.odin
    with open(odin_compile_dir + "/main.odin", "r") as original_file:
        main_odin = original_file.read()

    #Fill templates
    main_odin = main_odin.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(objects_odin))
    main_odin = main_odin.replace("//TEMPLATING:TEXTURES", "\n".join(textures_odin))
    main_odin = main_odin.replace("//TEMPLATING:RENDER_SPRITES", "\n".join(ordered_render_sprites)) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
    main_odin = main_odin.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(tick_procs_odin))
    main_odin = main_odin.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(sprite_tick_proc_calls))
    main_odin = main_odin.replace("//TEMPLATING:NAME", project_name)

    #Write to main.odin file
    with open(odin_compile_dir + "main.odin", "w") as file:
        file.write(main_odin)

if len(sys.argv) > 1:
    command = sys.argv[1]
    if len(sys.argv) > 2:
        sb3_path = sys.argv[2]
        if command == "build":
            build(sb3_path)
        elif command == "run":
            build(sb3_path)
            subprocess.run(["odin", "run", "."], cwd=odin_compile_dir, capture_output=False, text=True)

    elif command in commands:
        print("Please specify an sb3 path.")
    else:
        print("Invalid command.")
else:
    print(f"Please specify a command. Options are {commands}.")
