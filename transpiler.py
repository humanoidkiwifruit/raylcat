import json
import os
from pydoc import text
import shutil
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

sb3_path = "Scratch Project.sb3"
setup_work()

with zipfile.ZipFile(sb3_path, mode="r") as archive: #Extract the sb3 file to a directory
    archive.extractall(sb3_extraction_dir)
    json_text = archive.read("project.json")



json_dict = json.loads(json_text) #convert project.json to a python dictionary

#Template strings
objects_odin = ""
textures_odin = ""
render_sprites_odin = ""

for i in json_dict["targets"]: #Iterate over sprites

    if i['isStage'] != True: #Ignore stage sprite

        texture_filename = i['costumes'][0]['md5ext']

        shutil.copy(sb3_extraction_dir + texture_filename, assets_dir + texture_filename) #Copy textures to the compilation directory
        objects_odin += f"{i['name']} := scratch.Scratch_Sprite{{{i['x']}, {i['y']}, {i['size']}, {i['direction']}, 0, {i['name']}_texture, true,}}\n" #Instantiate odin Scratch_Sprite objects
        textures_odin += f"{i['name']}_texture: rl.Texture2D = rl.LoadTexture(\"assets/{texture_filename}\")\ndefer rl.UnloadTexture({i['name']}_texture)\n" #Instantiate raylib textures
        render_sprites_odin += f"scratch.scratch_draw_sprite(&{i['name']})\n" #Draw sprites in odin

#Read the template main.odin
with open(odin_compile_dir + "/main.odin", "r") as original_file:
    main_odin = original_file.read()

#Fill templates
main_odin = main_odin.replace("//TEMPLATING:SPRITE_OBJECTS", objects_odin)
main_odin = main_odin.replace("//TEMPLATING:TEXTURES", textures_odin)
main_odin = main_odin.replace("//TEMPLATING:RENDER_SPRITES", render_sprites_odin)

#Write to main.odin file
with open(odin_compile_dir + "main.odin", "w") as file:
    file.write(main_odin)
