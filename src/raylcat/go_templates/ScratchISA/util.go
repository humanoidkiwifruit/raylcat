package ScratchISA

import (
	rl "github.com/gen2brain/raylib-go/raylib"
)

var key_mappings map[string]int32 = map[string]int32{
	"left arrow":  rl.KeyLeft,
	"right arrow": rl.KeyRight,
	"up arrow":    rl.KeyUp,
	"down arrow":  rl.KeyDown,
	"space":       rl.KeySpace,
	"a":           rl.KeyA,
	"b":           rl.KeyB,
	"c":           rl.KeyC,
	"d":           rl.KeyD,
	"e":           rl.KeyE,
	"f":           rl.KeyF,
	"g":           rl.KeyG,
	"h":           rl.KeyH,
	"i":           rl.KeyI,
	"j":           rl.KeyJ,
	"k":           rl.KeyK,
	"l":           rl.KeyL,
	"m":           rl.KeyM,
	"n":           rl.KeyN,
	"o":           rl.KeyO,
	"p":           rl.KeyP,
	"q":           rl.KeyQ,
	"r":           rl.KeyR,
	"s":           rl.KeyS,
	"t":           rl.KeyT,
	"u":           rl.KeyU,
	"v":           rl.KeyV,
	"w":           rl.KeyW,
	"x":           rl.KeyX,
	"y":           rl.KeyY,
	"z":           rl.KeyZ,
}

type HatBlockOpcode int

const (
	GreenFlag HatBlockOpcode = iota
	KeyPressed
)

type HatBlock struct {
	Opcode HatBlockOpcode
	Key    string
}

type Context struct {
	Sprites               map[string]*ScratchSprite
	Stage                 *ScratchStage
	Timer                 float64 //timer needs to be updated in the main loop
	RunningScriptControls []ScratchScriptControl
}

func HandleKeyPressHatBlocks(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == KeyPressed {
				if rl.IsKeyDown(key_mappings[script.Hat.Key]) {
					scriptControl := ScratchScriptControl{AwakenChan: make(chan bool), FinishedChan: make(chan bool)}
					context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
					go script.Function(sprite, scriptControl, context)
				}
			}
		}
	}
}

func GetVariableValue(
	sprite *ScratchSprite,
	context *Context,
	variable string,
) ScratchValue {
	if val, ok := sprite.Variables[variable]; ok {
		return val
	}

	return context.Stage.Variables[variable]
}

func setVariableValue(
	sprite *ScratchSprite,
	context *Context,
	variable string,
	value ScratchValue,
) {
	if _, ok := sprite.Variables[variable]; ok {
		sprite.Variables[variable] = value
		return
	}

	context.Stage.Variables[variable] = value
}
