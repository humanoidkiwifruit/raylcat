package main

import (
	rl "github.com/gen2brain/raylib-go/raylib"
	//"scratchgame/ScratchISA"
)

//TEMPLATING:SPRITE_TICK_PROCEDURES

func main() {

	//rl.SetConfigFlags({ .VSYNC_HINT })
	rl.InitWindow(480, 360, "//TEMPLATING:NAME")
	defer rl.CloseWindow()
	rl.SetTargetFPS(30)

	//TEMPLATING:TEXTURES
	//cat_texture: rl.Texture2D = rl.LoadTexture("assets/cat.png")
	//defer rl.UnloadTexture(cat_texture)

	//TEMPLATING:SPRITE_OBJECTS
	/*cat := scratch.Scratch_Sprite{
		0,
		0,
		100,
		90,
		0,
		cat_texture,
		true,
	}
	*/

	for !rl.WindowShouldClose() {

		rl.BeginDrawing()
		rl.ClearBackground(rl.White)
		//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES
		//TEMPLATING:RENDER_SPRITES
		rl.EndDrawing()
	}
}
