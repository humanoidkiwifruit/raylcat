package ScratchISA

import "math"

/*
	clamp_direction :: proc(direction: f32) -> f32 {
		new_direction := direction
		for new_direction > 180 {
			new_direction -= 360
		}
		for new_direction < -180 {
			new_direction += 360
		}
		return new_direction
	}
*/
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
	spriteDirectionRad := sprite.Direction * math.Pi / 180

	dx := steps.NumberValue * math.Cos(spriteDirectionRad)
	dy := steps.NumberValue * math.Sin(spriteDirectionRad)
	sprite.X += dx
	sprite.Y += dy
}

/*motion_movesteps :: proc(sprite: ^ScratchSprite, steps: Scratch_Value) {
sprite_direction_rad := math.to_radians(sprite.direction - 90)
//sprite.x += math.sin(math.to_radians(sprite_direction_rad))
dx := f32(steps.number_value) * math.cos(sprite_direction_rad);
dy := f32(steps.number_value) * math.sin(sprite_direction_rad);
sprite.x += dx
sprite.y -= dy
}*/

func Motion_turnright(sprite *ScratchSprite, degrees ScratchValue) {
	sprite.Direction = clampDirection(sprite.Direction + degrees.NumberValue)
}

/*motion_turnright :: proc(sprite: ^ScratchSprite, degrees: Scratch_Value) {
	sprite.direction += f32(degrees.number_value)
	sprite.direction = clamp_direction(sprite.direction)
}*/

/*motion_turnleft :: proc(sprite: ^ScratchSprite, degrees: Scratch_Value) {
	sprite.direction -= f32(degrees.number_value)
	sprite.direction = clamp_direction(sprite.direction)
}*/

func Motion_turnleft(sprite *ScratchSprite, degrees ScratchValue) {
	sprite.Direction = clampDirection(sprite.Direction - degrees.NumberValue)
}

/*motion_gotoxy :: proc(sprite: ^ScratchSprite, x, y : Scratch_Value) {
	sprite.x = f32(x.number_value)
	sprite.y = f32(y.number_value)
}*/

func Motion_gotoxy(sprite *ScratchSprite, x, y ScratchValue) {
	sprite.X = x.NumberValue
	sprite.Y = y.NumberValue
}

/*motion_pointindirection :: proc(sprite: ^ScratchSprite, direction: Scratch_Value) {
	sprite.direction = f32(direction.number_value)
	sprite.direction = clamp_direction(sprite.direction)
}*/

func Motion_pointindirection(sprite *ScratchSprite, direction ScratchValue) {
	sprite.Direction = clampDirection(direction.NumberValue)
}

/*motion_changexby :: proc(sprite: ^ScratchSprite, x: Scratch_Value) {
	sprite.x += f32(x.number_value)
}*/

func Motion_changexby(sprite ScratchSprite, x ScratchValue) {
	sprite.X += x.NumberValue
}

/*motion_setx :: proc(sprite: ^ScratchSprite, x: Scratch_Value) {
	sprite.x = f32(x.number_value)
}*/

func Motion_setx(sprite ScratchSprite, x ScratchValue) {
	sprite.X = x.NumberValue
}

/*motion_changeyby :: proc(sprite: ^ScratchSprite, y: Scratch_Value) {
	sprite.y += f32(y.number_value)
}*/

func Motion_changeyby(sprite ScratchSprite, y ScratchValue) {
	sprite.Y += y.NumberValue
}

/*
		motion_sety :: proc(sprite: ^ScratchSprite, y: Scratch_Value) {
			sprite.y = f32(y.number_value)
	}
*/
func Motion_sety(sprite ScratchSprite, y ScratchValue) {
	sprite.Y = y.NumberValue
}
