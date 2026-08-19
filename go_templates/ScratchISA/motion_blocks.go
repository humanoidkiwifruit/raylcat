package ScratchISA

import "math"

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
