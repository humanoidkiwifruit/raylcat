package ScratchISA

import (
	"math"
	"math/rand/v2"
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
