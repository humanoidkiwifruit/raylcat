#!/usr/bin/env python3
import json
import os
import pprint
import shutil
import sys
import zipfile


work_dir = "work/"
odin_compile_dir = work_dir + "odin_compile_dir/"
sb3_extraction_dir = work_dir + "sb3/"
odin_template_dir = "odin_templates"
assets_dir = odin_compile_dir + "assets/"

def setup_work(): # Set up the working directory
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    os.makedirs(sb3_extraction_dir)
    shutil.copytree(odin_template_dir, odin_compile_dir)
    os.makedirs(assets_dir)

def transpile_to_odin(sprite_dict):
    odin_list = []
    blocks_dict = sprite_dict['blocks']
    for block in blocks_dict.values():
        if block['opcode'] == "event_whenflagclicked":
            current_block = blocks_dict[block['next']]
            while True:
                temp_line = "scratch." + current_block['opcode'] + "("
                temp_line += "sprite, "
                for key, i in current_block['inputs'].items():
                    #pprint.pprint(key)
                    #pprint.pprint(i)
                    #print(type(i))
                    temp_line += key.lower() + "=" + i[1][1] + ", "
                temp_line += ")"
                odin_list.append(temp_line)
                if current_block['next'] == None: break
                current_block = blocks_dict[current_block['next']]
    return "\n".join(odin_list)

if len(sys.argv) > 1:
    sb3_path = sys.argv[1]
else:
    sb3_path = "Scratch Project.sb3"

setup_work()

with zipfile.ZipFile(sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
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
        tick_proc_odin = transpile_to_odin(i)
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
        tick_procs_odin.append(f"{new_name}_tick :: proc(sprite: ^scratch.Scratch_Sprite) {{\n" + tick_proc_odin + "\n}")
        objects_odin.append(f"{new_name} := scratch.Scratch_Sprite{{{i['x']}, {i['y']}, {i['size']}, {i['direction']}, 0, {new_name}_texture, {i_is_visible},}}") #Instantiate odin Scratch_Sprite objects
        textures_odin.append(f"{new_name}_texture: rl.Texture2D = rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({new_name}_texture)") #Instantiate raylib textures
        ordered_render_sprites[i['layerOrder']] = f"scratch.scratch_draw_sprite(&{new_name})"

#Read the template main.odin
with open(odin_compile_dir + "/main.odin", "r") as original_file:
    main_odin = original_file.read()

#Fill templates
main_odin = main_odin.replace("//TEMPLATING:SPRITE_OBJECTS", "\n".join(objects_odin))
main_odin = main_odin.replace("//TEMPLATING:TEXTURES", "\n".join(textures_odin))
main_odin = main_odin.replace("//TEMPLATING:RENDER_SPRITES", "\n".join(ordered_render_sprites)) #Insert the rendering code for each sprite into the raylib main loop in the correct order, so layers work. This will have to be changed in future, as sprites can change their layer at runtime.
main_odin = main_odin.replace("//TEMPLATING:SPRITE_TICK_PROCEDURES", "\n".join(tick_procs_odin))
main_odin = main_odin.replace("//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES", "\n".join(sprite_tick_proc_calls))

#Write to main.odin file
with open(odin_compile_dir + "main.odin", "w") as file:
    file.write(main_odin)
