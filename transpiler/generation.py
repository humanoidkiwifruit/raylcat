from . import util
from .scratch_types import ScratchSprite, ScratchStage, ScratchTarget


class Generation:
    def __init__(self, scratchISA_prefix):
        self.scratchISA_prefix = scratchISA_prefix

    def generate_sprite_object_declaration(self, sprite: ScratchSprite) -> str:
        go_object_declaration = f"{sprite.name} := {self.scratchISA_prefix}.ScratchSprite{{X: {sprite.x}, Y: {sprite.y}, Size: {sprite.size}, Direction: {sprite.direction}, CostumeNumber: {sprite.current_costume}, Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, Show: {'true' if sprite.visible else 'false'}, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        for _ in range(util.number_of_scripts(sprite)):
            go_object_declaration += (
                "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            )
        go_object_declaration += "}}"
        return go_object_declaration

    def generate_stage_object_declaration(self, stage: ScratchStage) -> str:
        go_object_declaration = f"{stage.name} := {self.scratchISA_prefix}.ScratchStage{{CostumeNumber: {stage.current_costume}, Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, Controls: []{self.scratchISA_prefix}.ScratchScriptControl{{"
        for _ in range(util.number_of_scripts(stage)):
            go_object_declaration += (
                "{AwakenChan: make(chan bool), FinishedChan: make(chan bool)},"
            )
        go_object_declaration += "}}"
        return go_object_declaration

    def generate_texture_declarations(self, sprite: ScratchTarget) -> list[str]:
        costume_declarations = []
        for index, costume in enumerate(sprite.costumes):
            texture_filename = costume["assetId"] + "." + costume["dataFormat"]
            texture_go_name = util.generate_texture_name(sprite, index)
            costume_declarations.append(
                f'{texture_go_name} := rl.LoadTexture("assets/{texture_filename}")\ndefer rl.UnloadTexture({texture_go_name})'
            )  # Instantiate raylib textures
        return costume_declarations

    def transpile_costume_values(self, sprite: ScratchTarget) -> list[str]:
        costume_declarations = []
        for index, costume in enumerate(sprite.costumes):
            costume_declarations.append(f"{self.scratchISA_prefix}.Costume{{Name: \"{costume["name"]}\", Texture: {util.generate_texture_name(sprite, index)} }}")
        return costume_declarations
    def generate_go_render(self, sprite: ScratchSprite) -> str:
        return f"{self.scratchISA_prefix}.DrawSprite(&{sprite.name})"
