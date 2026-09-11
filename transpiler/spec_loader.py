import json

from .scratch_types import BlockSpec


class SpecLoader:
    def __init__(self, specs_path="block_specs.json"):
        self.specs_path = specs_path

    def get_specs(self) -> dict[str, BlockSpec]:
        specs = {}
        with open(self.specs_path, "r") as file:
            data_dict = json.load(file)
        for opcode, v in data_dict.items():
            specs[opcode] = BlockSpec(
                go_func=v["go_func"],
                inputs=v["inputs"],
                fields=v["fields"],
                wants=v.get("wants"),
                is_menu=v.get("is_menu", False),
            )
        return specs
