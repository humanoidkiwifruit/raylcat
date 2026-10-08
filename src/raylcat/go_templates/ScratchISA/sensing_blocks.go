package ScratchISA

import (
	"math"

	rl "github.com/gen2brain/raylib-go/raylib"
)

func Sensing_distanceto(context *Context, sprite *ScratchSprite, distancetomenu ScratchValue) ScratchValue {
	sx := sprite.X
	sy := sprite.Y
	if distancetomenu.StringValue == "_mouse_" {
		mx := Sensing_mousex().NumberValue
		my := Sensing_mousey().NumberValue
		return ValueFromFloat64(math.Sqrt(math.Pow(mx-sx, 2.0) + math.Pow(my-sy, 2.0)))
	} else {
		ox := context.Sprites[distancetomenu.StringValue].X
		oy := context.Sprites[distancetomenu.StringValue].Y
		return ValueFromFloat64(math.Sqrt(math.Pow(ox-sx, 2.0) + math.Pow(oy-sy, 2.0)))
	}
}

func Sensing_keypressed(key_option ScratchValue) bool {
	return rl.IsKeyDown(key_mappings[key_option.StringValue])
}

func Sensing_mousex() ScratchValue {
	return ValueFromFloat64(float64(rl.GetMouseX() - int32(rl.GetScreenWidth())/2))
}

func Sensing_mousey() ScratchValue {
	return ValueFromFloat64(float64(rl.GetScreenHeight()/2) - float64(rl.GetMouseY()))
}

func Sensing_mousedown() bool {
	return rl.IsMouseButtonDown(rl.MouseLeftButton)
}
func Sensing_resettimer(context *Context) {
	context.Timer = 0
}
func Sensing_timer(context *Context) ScratchValue {
	return ValueFromFloat64(context.Timer)
}
