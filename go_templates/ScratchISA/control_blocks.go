package ScratchISA

import rl "github.com/gen2brain/raylib-go/raylib"

func Control_wait(sprite *ScratchSprite, control ScratchScriptControl, duration ScratchValue) {
	startingTime := rl.GetTime()
	for startingTime+duration.NumberValue > rl.GetTime() {
		Yield(control)
	}
}
