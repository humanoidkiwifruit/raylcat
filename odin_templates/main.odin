package game

import rl "vendor:raylib"
import scratch "ScratchISA"

//TEMPLATING:SPRITE_TICK_PROCEDURES

main :: proc() {

	rl.SetConfigFlags({ .VSYNC_HINT })
	rl.InitWindow(480, 360, "Odin scratch")
	defer rl.CloseWindow()


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
		rl.ClearBackground({ 255, 255, 255, 255 })
		//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES
		//TEMPLATING:RENDER_SPRITES
		rl.EndDrawing()
	}
}
