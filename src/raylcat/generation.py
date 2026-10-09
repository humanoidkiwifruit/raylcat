from . import util
from .block_generation import BlockGeneration
from .scratch_types import (
    BlockSpec,
    ParsedSprite,
    ParsedStage,
    ParsedTarget,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    TargetScript,
    TranspiledSprite,
    TranspiledStage,
    WhenGreenFlagScript,
    WhenKeyPressedScript,
)
from .spec_loader import SpecLoader


class Generation:
    def __init__(self, scratchISA_prefix: str):
        self.scratchISA_prefix: str = scratchISA_prefix
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()
        self.block_generation: BlockGeneration = BlockGeneration(self.scratchISA_prefix)

    def generate_sprite_object_declaration(self, sprite: ParsedSprite) -> str:
        go_object_declaration = (
            f"{sprite.name} := {self.scratchISA_prefix}.ScratchSprite{{"
            + f"X: {sprite.x}, "
            + f"Y: {sprite.y}, "
            + f"Size: {sprite.size}, "
            + f"Direction: {sprite.direction}, "
            + f"CostumeNumber: {sprite.current_costume + 1}, "
            + f"Costumes: []{self.scratchISA_prefix}.Costume {{ {', '.join(self.transpile_costume_values(sprite))} }}, "
            + f"Show: {'true' if sprite.visible else 'false'}, "
            + f"Scripts: []{self.scratchISA_prefix}.SpriteScript{{"
        )
        for script in sprite.scripts:
            go_object_declaration += self.generate_script_declaration(script)
            go_object_declaration += ", "
        go_object_declaration += "}}"
        return go_object_declaration

    def generate_stage_object_declaration(self, stage: ParsedStage) -> str:
        go_object_declaration = (
            f"{stage.name} := {self.scratchISA_prefix}.ScratchStage{{"
            + f"CostumeNumber: {stage.current_costume + 1}, "
            + f"Costumes: []{self.scratchISA_prefix}.Costume {{ TEMPLATING:ADD_COSTUMES }}, "
            + f"Scripts: []{self.scratchISA_prefix}.StageScript{{"
        )
        for script in stage.scripts:
            go_object_declaration += self.generate_script_declaration(
                script, stage=True
            )
            go_object_declaration += ", "
        # go_object_declaration += "}}"
        go_object_declaration += "}}"
        costume_declarations = self.transpile_costume_values(stage)
        go_object_declaration = go_object_declaration.replace(
            "TEMPLATING:ADD_COSTUMES", ", ".join(costume_declarations)
        )
        return go_object_declaration

    def generate_texture_declarations(self, sprite: ParsedTarget) -> list[str]:
        texture_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            # force all textures to be .png as they will have been converted by now
            texture_filename = costume.asset_id + ".png"
            texture_go_name = util.generate_texture_name(sprite.name, index)
            texture_declarations.append(
                f'{texture_go_name} := rl.LoadTexture("assets/{texture_filename}")\ndefer rl.UnloadTexture({texture_go_name})'
            )  # Instantiate raylib textures
        return texture_declarations

    def transpile_costume_values(self, sprite: ParsedTarget) -> list[str]:
        costume_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            costume_declarations.append(
                f'{self.scratchISA_prefix}.Costume{{Name: "{costume.name}", Texture: {util.generate_texture_name(sprite.name, index)} }}'
            )
        return costume_declarations

    def generate_go_render(self, sprite: ScratchSprite) -> str:
        return f"{self.scratchISA_prefix}.DrawSprite(&{sprite.name})"

    def generate_script_declaration(
        self, script: TargetScript, stage: bool = False
    ) -> str:
        if isinstance(script, WhenGreenFlagScript):
            script_str = (
                '{Hat: scratch.HatBlock{Opcode: scratch.GreenFlag, Key: ""}, '
                + f"Function: func(sprite *scratch.Scratch{'Stage' if stage else 'Sprite'}, control scratch.ScratchScriptControl, context *scratch.Context) {{"
            )
        elif isinstance(script, WhenKeyPressedScript):  # pyright: ignore[reportUnnecessaryIsInstance]
            script_str = (
                f'{{Hat: scratch.HatBlock{{Opcode: scratch.KeyPressed, Key: "{script.key}"}}, '
                + f"Function: func(sprite *scratch.Scratch{'Stage' if stage else 'Sprite'}, control scratch.ScratchScriptControl, context *scratch.Context) {{"
            )

        script_str += self.block_generation.generate_stack(script.body)
        script_str += "\n for {scratch.Yield(control)}  }}"  # One to close the function declaration, one to close the slice entry

        return script_str

    def generate_context(
        self, sprites: list[ScratchSprite], stage: ScratchStage
    ) -> str:
        context_declaration = (
            "context := scratch.Context{Sprites: map[string]*scratch.ScratchSprite{"
        )

        # All normal sprites
        for sprite in sprites:
            context_declaration += (
                # Clean the name to be in line with the rest of main.go
                # the name isn't already cleaned because ScratchSprite tries to be as close to the projet.json as possible
                f'"{util.clean_name(sprite.name)}": &{util.clean_name(sprite.name)}, '
            )
        context_declaration += f"}}, Stage: &{stage.name}, Variables: map[string]{self.scratchISA_prefix}.ScratchValue{{"
        all_targets: list[ScratchTarget] = []
        all_targets.extend(sprites)
        all_targets.append(stage)
        for target in all_targets:
            for v in target.variables.values():
                context_declaration += f'"{v[0]}":'
                variable_value = v[1]
                if isinstance(variable_value, str):
                    context_declaration += f'{self.scratchISA_prefix}.ValueFromString("{variable_value}"), '
                elif isinstance(variable_value, (int, float)):
                    context_declaration += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({variable_value})), "
        context_declaration += "}"
        context_declaration += (
            f", Lists: map[string][]{self.scratchISA_prefix}.ScratchValue{{"
        )
        for target in all_targets:
            for v in target.lists.values():
                context_declaration += (
                    f'"{v[0]}": []{self.scratchISA_prefix}.ScratchValue{{'
                )
                list_value = v[1]
                for list_item_value in list_value:
                    if isinstance(list_item_value, str):
                        context_declaration += f'{self.scratchISA_prefix}.ValueFromString("{list_item_value}"), '
                    elif isinstance(list_item_value, (int, float)):
                        context_declaration += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({list_item_value})), "
                context_declaration += "}"
        context_declaration += "}}"
        return context_declaration

    def generate_stage(self, stage: ParsedStage) -> TranspiledStage:
        """Transpile the stage, ready for populating the template"""
        go_sprite_object_declaration = self.generate_stage_object_declaration(stage)
        texture_declarations = self.generate_texture_declarations(stage)
        return TranspiledStage(
            name=stage.name,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
        )

    def generate_sprite(self, sprite: ParsedSprite) -> TranspiledSprite:
        """Transpile a sprite, ready for populating the template"""
        go_sprite_object_declaration = self.generate_sprite_object_declaration(sprite)
        texture_declarations = self.generate_texture_declarations(sprite)
        return TranspiledSprite(
            name=sprite.name,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            layer_order=sprite.layer_order,
        )
