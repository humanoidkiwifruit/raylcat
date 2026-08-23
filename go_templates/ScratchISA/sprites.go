package ScratchISA

import (
	rl "github.com/gen2brain/raylib-go/raylib"
)

type ScratchSprite struct {
	X             float64
	Y             float64
	Size          float64
	Direction     float64
	CostumeNumber int
	Texture       rl.Texture2D
	Show          bool
	Controls      []ScratchScriptControl
}

type ScratchScriptControl struct {
	FinishedChan chan bool
	AwakenChan   chan bool
}

func DrawSprite(sprite *ScratchSprite) {

	screen_w := rl.GetScreenWidth()
	screen_h := rl.GetScreenHeight()

	//Convert scratch coords & rotation into raylib terms
	rl_x := float64(screen_w)/2 + sprite.X
	rl_y := float64(screen_h)/2 - sprite.Y
	rl_rotation := sprite.Direction - 90
	rl_scale := sprite.Size / 100

	source := rl.Rectangle{
		X:      0,
		Y:      0,
		Width:  float32(sprite.Texture.Width),
		Height: float32(sprite.Texture.Height),
	}

	dest := rl.Rectangle{
		X:      float32(rl_x),
		Y:      float32(rl_y),
		Width:  float32(sprite.Texture.Width) * float32(0.5) * float32(rl_scale),
		Height: float32(sprite.Texture.Height) * float32(0.5) * float32(rl_scale),
	}

	origin := rl.Vector2{
		X: float32(sprite.Texture.Width/4) * float32(rl_scale),
		Y: float32(sprite.Texture.Height/4) * float32(rl_scale),
	}

	if sprite.Show {
		rl.DrawTexturePro(sprite.Texture, source, dest, origin, float32(rl_rotation), rl.White)
	}
}

func Yield(control ScratchScriptControl) {
	control.FinishedChan <- true
	<-control.AwakenChan
}
