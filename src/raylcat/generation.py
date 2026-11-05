from . import util
from .block_generation import BlockGeneration
from .spec_loader import SpecLoader
from .types import (
    BlockSpec,
    ClickedScript,
    NumberLiteral,
    ParsedSprite,
    ParsedStage,
    ParsedTarget,
    ScratchSprite,
    ScratchStage,
    ScratchTarget,
    StringLiteral,
    TargetScript,
    TranspiledSprite,
    TranspiledStage,
    WhenGreenFlagScript,
    WhenIReceiveBroadcastScript,
    WhenKeyPressedScript,
)


class Generation:
    def __init__(self, scratchISA_prefix: str, embed_assets: bool):
        self.scratchISA_prefix: str = scratchISA_prefix
        self.spec_loader: SpecLoader = SpecLoader()
        self.specs: dict[str, BlockSpec] = self.spec_loader.get_specs()
        self.block_generation: BlockGeneration = BlockGeneration(self.scratchISA_prefix)
        self.embed_assets: bool = embed_assets

    def generate_sprite_object_declaration(self, sprite: ParsedSprite) -> str:
        go_object_declaration = (
            f"{sprite.name} := {self.scratchISA_prefix}.ScratchSprite{{\n"
            + f"X: {sprite.x}, \n"
            + f"Y: {sprite.y}, \n"
            + f"Size: {sprite.size}, \n"
            + f"Direction: {sprite.direction}, \n"
            + f"CostumeNumber: {sprite.current_costume + 1}, \n"
            + f"Costumes: []{self.scratchISA_prefix}.Costume {{ {', '.join(self.transpile_costume_values(sprite))} }}, \n"
            + f"Show: {'true' if sprite.visible else 'false'}, \n"
            + f"Variables: map[string]scratch.ScratchValue{{ {self.generate_variable_declarations(sprite)} }}, \n"
            + f"Lists: map[string][]{self.scratchISA_prefix}.ScratchValue {{ {self.generate_list_declarations(sprite)} }}, \n"
            + f"Scripts: []{self.scratchISA_prefix}.SpriteScript{{\n"
        )
        for script in sprite.scripts:
            go_object_declaration += self.generate_script_declaration(script)
            go_object_declaration += ", "
        go_object_declaration += "\n},\n}"
        return go_object_declaration

    def generate_stage_object_declaration(self, stage: ParsedStage) -> str:
        go_object_declaration = (
            f"{stage.name} := {self.scratchISA_prefix}.ScratchStage{{\n"
            + f"CostumeNumber: {stage.current_costume + 1}, \n"
            + f"Costumes: []{self.scratchISA_prefix}.Costume{{ {', '.join(self.transpile_costume_values(stage))} }}, \n"
            + f"Variables: map[string]scratch.ScratchValue{{ {self.generate_variable_declarations(stage)} }}, \n"
            + f"Lists: map[string][]{self.scratchISA_prefix}.ScratchValue{{ {self.generate_list_declarations(stage)} }}, \n"
            + f"Scripts: []{self.scratchISA_prefix}.StageScript{{\n"
        )
        for script in stage.scripts:
            go_object_declaration += self.generate_script_declaration(
                script, stage=True
            )
            go_object_declaration += ", "
        go_object_declaration += "\n},\n}"
        return go_object_declaration

    def generate_texture_declarations(self, sprite: ParsedTarget) -> list[str]:
        texture_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            # make all textures *.png as they will have been converted by now
            texture_filename = costume.asset_id + ".png"
            texture_go_name = util.generate_texture_name(sprite.name, index)

            if self.embed_assets:
                texture_declarations.extend(
                    [
                        f'{texture_go_name}_image := rl.LoadImageFromMemory(".png", {texture_go_name}_bytes, int32(len({texture_go_name}_bytes)))\n',
                        f"{texture_go_name} := rl.LoadTextureFromImage({texture_go_name}_image)\n",
                        f"defer rl.UnloadTexture({texture_go_name})",
                    ]
                )  # Grabs the image from the *_bytes file generated earlier

            else:
                texture_declarations.append(
                    f"{texture_go_name} := rl.LoadTexture(`assets/{texture_filename}`)\n"
                    + f"defer rl.UnloadTexture({texture_go_name})\n"
                )  # Grabs the image from a filename

        return texture_declarations

    def transpile_costume_values(self, sprite: ParsedTarget) -> list[str]:
        costume_declarations: list[str] = []
        for index, costume in enumerate(sprite.costumes):
            costume_declarations.append(
                "{"
                + f"Name: `{costume.name}`, "
                + f" Texture: {util.generate_texture_name(sprite.name, index)}"
                + "}"
            )
        return costume_declarations

    def generate_script_declaration(
        self, script: TargetScript, stage: bool = False
    ) -> str:
        if isinstance(script, WhenGreenFlagScript):
            script_str = (
                '{\nHat: scratch.HatBlock{Opcode: scratch.GreenFlag, Key: ""}, '
            )
        elif isinstance(script, WhenKeyPressedScript):
            script_str = f'{{\nHat: scratch.HatBlock{{Opcode: scratch.KeyPressed, Key: "{script.key}"}}, '
        elif isinstance(script, ClickedScript):
            script_str = '{\nHat: scratch.HatBlock{Opcode: scratch.Clicked, Key: ""}, '
        elif isinstance(script, WhenIReceiveBroadcastScript):  # pyright: ignore[reportUnnecessaryIsInstance]
            script_str = f'{{\nHat: scratch.HatBlock{{Opcode: scratch.BroadcastReceived, Key: "", BroadcastName: "{script.broadcast_name}"}}, '
        else:
            raise TypeError(f"Script is of unexpected type {type(script)}")  # pyright: ignore[reportUnreachable]
        script_str += "\n"
        script_str += f"Function: func(sprite *scratch.Scratch{'Stage' if stage else 'Sprite'}, control scratch.ScratchScriptControl, context *scratch.Context) {{"
        script_str += "\n<-control.AwakenChan \n"
        script_str += self.block_generation.generate_stack(script.body)
        script_str += "\n control.DoneChan <- struct{}{} },\n}"  # Send down the DoneChan, to signal that the script is well and truly finished and ready to be removed from the list of active scripts

        return script_str

    def generate_context(
        self, sprites: list[ScratchSprite], stage: ScratchStage
    ) -> str:
        context_declaration = (
            "context := scratch.Context{ "
            + "\nSprites: map[string]*scratch.ScratchSprite{\n"
        )

        # All normal sprites
        for sprite in sprites:
            context_declaration += (
                # Clean the name to be in line with the rest of main.go
                # the name isn't already cleaned because ScratchSprite tries to be as close to the project.json as possible
                f"`{sprite.name}`: &{util.clean_name(sprite.name)}, \n"
            )
        context_declaration += (
            "},\n"
            + f" Stage: &{stage.name}, \n"
            + "CollisionRequests: make(chan scratch.CollisionRequest),\n"
            + f" OrderedRender: []*{self.scratchISA_prefix}.ScratchSprite{{\n"
        )
        go_ordered_render_sprites: list[str] = [""] * len(sprites)
        # All normal sprites
        for sprite in sprites:
            go_ordered_render_sprites[sprite.layer_order - 1] = (
                f"&{util.clean_name(sprite.name)},"
            )
        context_declaration += "\n".join(go_ordered_render_sprites) + "\n},"
        all_targets: list[ScratchTarget] = []
        all_targets.extend(sprites)
        all_targets.append(stage)
        context_declaration += "\n}"
        return context_declaration

    def generate_stage(self, stage: ParsedStage) -> TranspiledStage:
        """Transpile the stage, ready for populating the template"""
        go_sprite_object_declaration = self.generate_stage_object_declaration(stage)
        texture_declarations = self.generate_texture_declarations(stage)
        transpiled_sprite_image_vars: list[str] = (
            self.generate_image_vars(stage) if self.embed_assets else []
        )
        return TranspiledStage(
            name=stage.name,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            transpiled_sprite_image_vars=transpiled_sprite_image_vars,
        )

    def generate_sprite(self, sprite: ParsedSprite) -> TranspiledSprite:
        """Transpile a sprite, ready for populating the template"""
        go_sprite_object_declaration = self.generate_sprite_object_declaration(sprite)
        texture_declarations = self.generate_texture_declarations(sprite)
        transpiled_sprite_image_vars: list[str] = (
            self.generate_image_vars(sprite) if self.embed_assets else []
        )
        return TranspiledSprite(
            name=sprite.name,
            go_sprite_object_declaration=go_sprite_object_declaration,
            texture_declarations=texture_declarations,
            layer_order=sprite.layer_order,
            transpiled_sprite_image_vars=transpiled_sprite_image_vars,
        )

    def generate_variable_declarations(self, target: ParsedTarget) -> str:
        var_declarations: str = ""
        for name, value in target.variables.items():
            var_declarations += f'"{name}":'
            if isinstance(value, StringLiteral):
                var_declarations += (
                    f'{self.scratchISA_prefix}.ValueFromString("{value.value}"), '
                )
            elif isinstance(value, NumberLiteral):  # pyright: ignore[reportUnnecessaryIsInstance]
                var_declarations += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({value.value})), "
            else:
                raise TypeError(
                    f"Variable {name} ScratchLiteral is of unexpected type {type(value)}"
                )
        return var_declarations

    def generate_list_declarations(self, target: ParsedTarget) -> str:
        list_delcarations: str = ""
        for name, value in target.lists.items():
            list_delcarations += f'"{name}": []{self.scratchISA_prefix}.ScratchValue{{'
            for list_item in value:
                if isinstance(list_item, StringLiteral):
                    list_delcarations += f'{self.scratchISA_prefix}.ValueFromString("{list_item.value}"), '
                elif isinstance(list_item, NumberLiteral):  # pyright: ignore[reportUnnecessaryIsInstance]
                    list_delcarations += f"{self.scratchISA_prefix}.ValueFromFloat64(float64({list_item.value})), "
                else:
                    raise TypeError(
                        f"list_item is of unexpected type {type(list_item)}"
                    )
            list_delcarations += "}"
        return list_delcarations

    def generate_image_vars(self, target: ParsedTarget) -> list[str]:
        result: list[str] = []
        for index, costume in enumerate(target.costumes):
            texture_filename = costume.asset_id + ".png"
            result.append(
                f"//go:embed assets/{texture_filename}\nvar  {util.generate_texture_name(target.name, index)}_bytes []byte"
            )
        return result
