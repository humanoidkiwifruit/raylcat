import json
from importlib.resources import files

from .types import BlockSpec


class SpecLoader:
    """Loads the block_specs.json to a useful list[BlockSpec]"""

    def __init__(self, specs_path: str = "block_specs.json"):
        self.specs_path = files("raylcat").joinpath(specs_path)

    def get_specs(self) -> dict[str, BlockSpec]:
        """Get block_specs.json as a dict of opcode -> BlockSpec."""
        specs: dict[str, BlockSpec] = {}
        with self.specs_path.open("r") as file:
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
