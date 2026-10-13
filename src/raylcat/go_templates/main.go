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

	//rl.SetConfigFlags(rl.FlagVsyncHint)
	//TEMPLATING:INIT_WINDOW
	defer rl.CloseWindow()
	//TEMPLATING:CAP_FRAMERATE

	//TEMPLATING:TEXTURES

	//TEMPLATING:SPRITE_OBJECTS
	//TEMPLATING:INSTANTIATE_CONTEXT

	//TEMPLATING:SPRITE_TICK_PROCEDURES

	//TEMPLATING:FILL_RENDER_QUEUE

	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == scratch.GreenFlag {
				scriptControl := scratch.ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
				context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
				go script.Function(sprite, scriptControl, &context)
			}
		}
	}
	for _, script := range context.Stage.Scripts {
		if script.Hat.Opcode == scratch.GreenFlag {
			scriptControl := scratch.ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
			context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
			go script.Function(context.Stage, scriptControl, &context)
		}
	}

	for !rl.WindowShouldClose() {
		context.Timer += float64(rl.GetFrameTime())
		scratch.HandleKeyPressHatBlocks(&context)
		for _, control := range context.RunningScriptControls {
			control.AwakenChan <- struct{}{}
			<-control.FinishedChan
		}

		rl.BeginDrawing()
		rl.ClearBackground(rl.White)
		scratch.DrawStage(context.Stage)
		for _, sprite := range scratch.OrderedRender {
			scratch.DrawSprite(sprite)
		}
		//TEMPLATING:DRAW_FRAMERATE
		rl.EndDrawing()
	}
}
