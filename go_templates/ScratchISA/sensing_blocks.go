package ScratchISA

import (
	rl "github.com/gen2brain/raylib-go/raylib"
)

func Sensing_mousex(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(float64(rl.GetMouseX() - int32(rl.GetScreenWidth())/2))
}

func Sensing_mousey(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(float64(rl.GetScreenHeight()/2) - float64(rl.GetMouseY()))
}

func Sensing_mousedown(sprite *ScratchSprite) bool {
	return rl.IsMouseButtonDown(rl.MouseLeftButton)
}
