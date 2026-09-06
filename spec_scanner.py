import json
import pprint

from transpiler import parsing, scratch_project, util

project = scratch_project.ScratchProject("Scratch Project.sb3")
project.build()

specs_dict = {}

for sprite in project.sprites:
    for block in sprite.blocks.values():
        specs_dict[block.opcode] = {
            "go_func": project.transpiler.opcode_to_go_func_call(block.opcode),
            "inputs": list(block.inputs),
            "fields": list(block.fields),

        }
pprint.pprint(specs_dict)

with open("test_block_specs.json", "w") as f:
    json.dump(specs_dict, f)
