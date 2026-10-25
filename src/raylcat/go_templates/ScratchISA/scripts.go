package ScratchISA

import (
	"slices"

	rl "github.com/gen2brain/raylib-go/raylib"
)

type HatBlockOpcode int

const (
	GreenFlag HatBlockOpcode = iota
	KeyPressed
	Clicked
	BroadcastReceived
)

type HatBlock struct {
	Opcode        HatBlockOpcode
	Key           string
	BroadcastName string
}

func HandleKeyPressHatBlocks(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == KeyPressed {
				if rl.IsKeyDown(key_mappings[script.Hat.Key]) {
					scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), RelinquishChan: make(chan struct{}), DoneChan: make(chan struct{})}
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
				if pointHits(context, rl.Vector2{X: float32(Sensing_mousex().NumberValue), Y: float32(Sensing_mousey().NumberValue)}, shadedSprite, sprite) && rl.IsMouseButtonPressed(rl.MouseButtonLeft) {
					scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), RelinquishChan: make(chan struct{}), DoneChan: make(chan struct{})}
					context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
					go script.Function(sprite, scriptControl, context)
				}
			}
		}
	}
	for _, script := range context.Stage.Scripts {
		if script.Hat.Opcode == Clicked {
			if pointHits(context, rl.Vector2{X: float32(Sensing_mousex().NumberValue), Y: float32(Sensing_mousey().NumberValue)}, shadedStage, nil) && rl.IsMouseButtonPressed(rl.MouseButtonLeft) {
				scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), RelinquishChan: make(chan struct{}), DoneChan: make(chan struct{})}
				context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
				go script.Function(context.Stage, scriptControl, context)
			}
		}
	}

}

func RunScripts(context *Context) {

	HandleKeyPressHatBlocks(context)
	HandleClickedHatBlocks(context)

	indexesThatNeedToBeRemoved := []int{}

	for i, control := range context.RunningScriptControls {
		control.AwakenChan <- struct{}{}
	ThisRequests:
		for {
			select {
			case <-control.RelinquishChan:
				break ThisRequests
			case req := <-context.CollisionRequests:
				ProcessCollisionRequest(context, req)
			case <-control.DoneChan:
				indexesThatNeedToBeRemoved = append(indexesThatNeedToBeRemoved, i)
				break ThisRequests
			}
		}
	}
	for _, controlindex := range indexesThatNeedToBeRemoved {
		context.RunningScriptControls = slices.Delete(context.RunningScriptControls, controlindex, controlindex+1)
	}
}

func SetupGreenFlagScripts(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == GreenFlag { //Check all the sprites for green flag scripts
				scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), RelinquishChan: make(chan struct{}), DoneChan: make(chan struct{})}
				context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
				go script.Function(sprite, scriptControl, context) //kick off the goroutine
			}
		}
	}
	for _, script := range context.Stage.Scripts {
		if script.Hat.Opcode == GreenFlag { //Check the stage for green flag scripts
			scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), RelinquishChan: make(chan struct{}), DoneChan: make(chan struct{})}
			context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
			go script.Function(context.Stage, scriptControl, context) //kick off the goroutine
		}
	}
}
