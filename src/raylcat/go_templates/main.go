package main

import (
	_ "embed"
	scratch "scratchgame/ScratchISA"

	rl "github.com/gen2brain/raylib-go/raylib"
)

//TEMPLATING:CUSTOM_BLOCK_DECLARATIONS

//TEMPLATING:IMAGES

func main() {
	//rl.SetConfigFlags(rl.FlagVsyncHint)
	//TEMPLATING:INIT_WINDOW
	defer rl.CloseWindow()
	//TEMPLATING:CAP_FRAMERATE

	//TEMPLATING:TEXTURES

	//TEMPLATING:SPRITE_OBJECTS
	//TEMPLATING:INSTANTIATE_CONTEXT

	scratch.InitCollisions()
	defer rl.UnloadRenderTexture(scratch.CollisionsRenderTarget)

	scratch.SetupGreenFlagScripts(&context)

	for !rl.WindowShouldClose() {
		scratch.UpdateTimer(&context)
		scratch.RunScripts(&context)
		scratch.DrawEverything(&context)
		//TEMPLATING:DRAW_FRAMERATE
	}
}
