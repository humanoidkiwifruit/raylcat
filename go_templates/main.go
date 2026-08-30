package main

import (
	"fmt"
	scratch "scratchgame/ScratchISA"

	rl "github.com/gen2brain/raylib-go/raylib"
)

func main() {
	dummy := scratch.ValueFromFloat64(0.0)
	fmt.Println(dummy)

	//rl.SetConfigFlags({ .VSYNC_HINT })
	rl.InitWindow(480, 360, "//TEMPLATING:NAME")
	defer rl.CloseWindow()
	rl.SetTargetFPS(30)

	//TEMPLATING:TEXTURES
	//TEMPLATING:SPRITE_OBJECTS

	//TEMPLATING:SPRITE_TICK_PROCEDURES

	for !rl.WindowShouldClose() {

		//TEMPLATING:CALL_SPRITE_TICK_PROCEDURES

		rl.BeginDrawing()
		rl.ClearBackground(rl.White)
		//TEMPLATING:RENDER_SPRITES
		rl.EndDrawing()
	}
}
