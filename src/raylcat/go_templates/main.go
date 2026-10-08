package main

import (
	"fmt"
	scratch "scratchgame/ScratchISA"

	rl "github.com/gen2brain/raylib-go/raylib"
)

//TEMPLATING:CUSTOM_BLOCK_DECLARATIONS

func main() {
	dummy := scratch.ValueFromFloat64(0.0)
	fmt.Println(dummy)

	//rl.SetConfigFlags({ .VSYNC_HINT })
	rl.InitWindow(480, 360, "//TEMPLATING:NAME")
	defer rl.CloseWindow()
	//TEMPLATING:CAP_FRAMERATE

	//TEMPLATING:TEXTURES

	//TEMPLATING:SPRITE_OBJECTS
	//TEMPLATING:INSTANTIATE_CONTEXT

	//TEMPLATING:SPRITE_TICK_PROCEDURES

	//TEMPLATING:FILL_RENDER_QUEUE

	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			scriptControl := scratch.ScratchScriptControl{AwakenChan: make(chan bool), FinishedChan: make(chan bool)}
			context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
			go script.Function(sprite, scriptControl, &context)
		}
	}
	for _, script := range context.Stage.Scripts {
		scriptControl := scratch.ScratchScriptControl{AwakenChan: make(chan bool), FinishedChan: make(chan bool)}
		context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
		go script.Function(context.Stage, scriptControl, &context)
	}

	for !rl.WindowShouldClose() {
		context.Timer += float64(rl.GetFrameTime())

		//TEMPLATING:/CALL_SPRITE_TICK_PROCEDURES
		for _, control := range context.RunningScriptControls {
			control.AwakenChan <- true
			<-control.FinishedChan
		}

		rl.BeginDrawing()
		rl.ClearBackground(rl.White)
		scratch.DrawStage(context.Stage)
		for _, sprite := range scratch.OrderedRender {
			scratch.DrawSprite(sprite)
		}
		rl.EndDrawing()
	}
}
