package ScratchISA

import (
	"math"
	"math/rand/v2"

	rl "github.com/gen2brain/raylib-go/raylib"
)

func clampDirection(direction float64) float64 {
	newDirection := direction
	for newDirection > 180 {
		newDirection -= 360
	}
	for newDirection < -180 {
		newDirection += 360
	}
	return newDirection
}

func Motion_movesteps(sprite *ScratchSprite, steps ScratchValue) {
	spriteDirectionRad := (90 - sprite.Direction) * math.Pi / 180

	dx := steps.NumberValue * math.Cos(spriteDirectionRad)
	dy := steps.NumberValue * math.Sin(spriteDirectionRad)
	sprite.X += dx
	sprite.Y += dy
}

func Motion_turnright(sprite *ScratchSprite, degrees ScratchValue) {
	sprite.Direction = clampDirection(sprite.Direction + degrees.NumberValue)
}

func Motion_turnleft(sprite *ScratchSprite, degrees ScratchValue) {
	sprite.Direction = clampDirection(sprite.Direction - degrees.NumberValue)
}

func Motion_goto(context Context, sprite *ScratchSprite, to ScratchValue) {
	if to.StringValue == "_mouse_" {
		sprite.X = Sensing_mousex().NumberValue
		sprite.Y = Sensing_mousey().NumberValue
	} else if to.StringValue == "_random_" {
		sprite.X = float64(-240 + rand.N(240-(-240)+1))
		sprite.Y = float64(-180 + rand.N(180-(-180)+1))
	} else {
		sprite.X = context.Sprites[to.StringValue].X
		sprite.Y = context.Sprites[to.StringValue].Y
	}
}
func Motion_gotoxy(sprite *ScratchSprite, x, y ScratchValue) {
	sprite.X = x.NumberValue
	sprite.Y = y.NumberValue
}

func Motion_glideto(context *Context, sprite *ScratchSprite, control ScratchScriptControl, secs, to ScratchValue) {
	if to.StringValue == "_mouse_" {
		Motion_glidesecstoxy(sprite, control, secs, Sensing_mousex(), Sensing_mousey())
	} else if to.StringValue == "_random_" {
		random_x := float64(-240 + rand.N(240-(-240)+1))
		random_y := float64(-180 + rand.N(180-(-180)+1))
		Motion_glidesecstoxy(sprite, control, secs, ValueFromFloat64(random_x), ValueFromFloat64(random_y))
	} else {
		subject_x := context.Sprites[to.StringValue].X
		subject_y := context.Sprites[to.StringValue].Y
		Motion_glidesecstoxy(sprite, control, secs, ValueFromFloat64(subject_x), ValueFromFloat64(subject_y))
	}
}

func Motion_glidesecstoxy(sprite *ScratchSprite, control ScratchScriptControl, secs, x, y ScratchValue) {
	starting_x := sprite.X
	starting_y := sprite.Y
	elapsed_secs := 0.0
	for elapsed_secs < secs.NumberValue {
		elapsed_secs = elapsed_secs + float64(rl.GetFrameTime())
		progress := elapsed_secs / secs.NumberValue
		sprite.X = starting_x + (x.NumberValue-starting_x)*progress
		sprite.Y = starting_y + (y.NumberValue-starting_y)*progress
		Yield(control)
	}
}

func Motion_pointindirection(sprite *ScratchSprite, direction ScratchValue) {
	sprite.Direction = clampDirection(direction.NumberValue)
}

func Motion_changexby(sprite *ScratchSprite, x ScratchValue) {
	sprite.X += x.NumberValue
}

func Motion_setx(sprite *ScratchSprite, x ScratchValue) {
	sprite.X = x.NumberValue
}

func Motion_changeyby(sprite *ScratchSprite, y ScratchValue) {
	sprite.Y += y.NumberValue
}

func Motion_sety(sprite *ScratchSprite, y ScratchValue) {
	sprite.Y = y.NumberValue
}

func Motion_xposition(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(sprite.X)
}

func Motion_yposition(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(sprite.Y)
}
