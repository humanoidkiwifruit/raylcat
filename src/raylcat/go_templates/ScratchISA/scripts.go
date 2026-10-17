package ScratchISA

import (
	rl "github.com/gen2brain/raylib-go/raylib"
)

type HatBlockOpcode int

const (
	GreenFlag HatBlockOpcode = iota
	KeyPressed
	Clicked
)

type HatBlock struct {
	Opcode HatBlockOpcode
	Key    string
}

func HandleKeyPressHatBlocks(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == KeyPressed {
				if rl.IsKeyDown(key_mappings[script.Hat.Key]) {
					scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
					context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
					go script.Function(sprite, scriptControl, context)
				}
			}
		}
	}
}

func HandleClickedHatBlocks(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == Clicked {
				if pointHits(context, rl.Vector2{X: float32(Sensing_mousex().NumberValue), Y: float32(Sensing_mousey().NumberValue)}, allWithShadedSprite, sprite) && rl.IsMouseButtonPressed(rl.MouseButtonLeft) {
					scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
					context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
					go script.Function(sprite, scriptControl, context)
				}
			}
		}
	}
	for _, script := range context.Stage.Scripts {
		if script.Hat.Opcode == Clicked {
			if pointHits(context, rl.Vector2{X: float32(Sensing_mousex().NumberValue), Y: float32(Sensing_mousey().NumberValue)}, stage, nil) && rl.IsMouseButtonPressed(rl.MouseButtonLeft) {
				scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
				context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
				go script.Function(context.Stage, scriptControl, context)
			}
		}
	}

}

func RunScripts(context *Context) {

	HandleKeyPressHatBlocks(context)
	HandleClickedHatBlocks(context)

	for _, control := range context.RunningScriptControls {
		control.AwakenChan <- struct{}{}
	ThisRequests:
		for {
			select {
			case <-control.FinishedChan:
				break ThisRequests
			case req := <-context.CollisionRequests:
				ProcessCollisionRequest(context, req)
			}
		}
	}
}

func SetupGreenFlagScripts(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == GreenFlag {
				scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
				context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
				go script.Function(sprite, scriptControl, context)
			}
		}
	}
	for _, script := range context.Stage.Scripts {
		if script.Hat.Opcode == GreenFlag {
			scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
			context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
			go script.Function(context.Stage, scriptControl, context)
		}
	}
}
