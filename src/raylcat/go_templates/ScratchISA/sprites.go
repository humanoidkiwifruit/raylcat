package ScratchISA

import (
	rl "github.com/gen2brain/raylib-go/raylib"
)

var OrderedRender []*ScratchSprite

type Costume struct {
	Name    string
	Texture rl.Texture2D
}

type ScratchSprite struct {
	X             float64
	Y             float64
	Size          float64
	Direction     float64
	CostumeNumber int
	Costumes      []Costume
	Show          bool
	Scripts       []SpriteScript
	Variables     map[string]ScratchValue
	Lists         map[string][]ScratchValue
}
type SpriteScript struct {
	Hat      HatBlock
	Function func(sprite *ScratchSprite, control ScratchScriptControl, context *Context)
}

type StageScript struct {
	Hat      HatBlock
	Function func(sprite *ScratchStage, control ScratchScriptControl, context *Context)
}

type ScratchStage struct {
	CostumeNumber int
	Costumes      []Costume
	Scripts       []StageScript
	Variables     map[string]ScratchValue
	Lists         map[string][]ScratchValue
}

type ScratchScriptControl struct {
	FinishedChan chan struct{}
	AwakenChan   chan struct{}
}

func DrawSprite(sprite *ScratchSprite) {
	screen_w := rl.GetScreenWidth()
	screen_h := rl.GetScreenHeight()
	texture := getActiveTexture(sprite)

	//Convert scratch coords & rotation into raylib terms
	rl_x := float64(screen_w)/2 + sprite.X
	rl_y := float64(screen_h)/2 - sprite.Y
	rl_rotation := sprite.Direction - 90
	rl_scale := sprite.Size / 100

	source := rl.Rectangle{
		X:      0,
		Y:      0,
		Width:  float32(texture.Width),
		Height: float32(texture.Height),
	}

	dest := rl.Rectangle{
		X:      float32(rl_x),
		Y:      float32(rl_y),
		Width:  float32(texture.Width) * float32(0.5) * float32(rl_scale),
		Height: float32(texture.Height) * float32(0.5) * float32(rl_scale),
	} // Can this maybe be repurposed for short-circuiting collision detections?

	origin := rl.Vector2{
		X: float32(texture.Width/4) * float32(rl_scale),
		Y: float32(texture.Height/4) * float32(rl_scale),
	}

	if sprite.Show {
		rl.DrawTexturePro(texture, source, dest, origin, float32(rl_rotation), rl.White)
	}
}

func DrawStage(stage *ScratchStage) {
	screen_w := rl.GetScreenWidth()
	screen_h := rl.GetScreenHeight()
	texture := stage.Costumes[stage.CostumeNumber-1].Texture
	//Convert scratch coords & rotation into raylib terms
	rl_x := float64(screen_w) / 2
	rl_y := float64(screen_h) / 2
	rl_rotation := 0
	rl_scale := 1

	source := rl.Rectangle{
		X:      0,
		Y:      0,
		Width:  float32(texture.Width),
		Height: float32(texture.Height),
	}

	dest := rl.Rectangle{
		X:      float32(rl_x),
		Y:      float32(rl_y),
		Width:  float32(texture.Width) * float32(0.5) * float32(rl_scale),
		Height: float32(texture.Height) * float32(0.5) * float32(rl_scale),
	}

	origin := rl.Vector2{
		X: float32(texture.Width/4) * float32(rl_scale),
		Y: float32(texture.Height/4) * float32(rl_scale),
	}

	rl.DrawTexturePro(texture, source, dest, origin, float32(rl_rotation), rl.White)
}
func getActiveTexture(sprite *ScratchSprite) rl.Texture2D {
	return sprite.Costumes[sprite.CostumeNumber-1].Texture
}
func Yield(control ScratchScriptControl) {
	control.FinishedChan <- struct{}{}
	<-control.AwakenChan
}
