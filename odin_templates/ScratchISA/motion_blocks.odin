package ScratchISA

import "core:math"
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

motion_movesteps :: proc(sprite: ^Scratch_Sprite, steps: Scratch_Value) {
	sprite_direction_rad := math.to_radians(sprite.direction - 90)
	//sprite.x += math.sin(math.to_radians(sprite_direction_rad))
	dx := f32(steps.number_value) * math.cos(sprite_direction_rad);
	dy := f32(steps.number_value) * math.sin(sprite_direction_rad);
	sprite.x += dx
	sprite.y -= dy
}

motion_turnright :: proc(sprite: ^Scratch_Sprite, degrees: Scratch_Value) {
	sprite.direction += f32(degrees.number_value)
	sprite.direction = clamp_direction(sprite.direction)
}

motion_turnleft :: proc(sprite: ^Scratch_Sprite, degrees: Scratch_Value) {
	sprite.direction -= f32(degrees.number_value)
	sprite.direction = clamp_direction(sprite.direction)
}

motion_gotoxy :: proc(sprite: ^Scratch_Sprite, x, y : Scratch_Value) {
	sprite.x = f32(x.number_value)
	sprite.y = f32(y.number_value)
}

motion_pointindirection :: proc(sprite: ^Scratch_Sprite, direction: Scratch_Value) {
	sprite.direction = f32(direction.number_value)
	sprite.direction = clamp_direction(sprite.direction)
}

motion_changexby :: proc(sprite: ^Scratch_Sprite, x: Scratch_Value) {
	sprite.x += f32(x.number_value)
}

motion_setx :: proc(sprite: ^Scratch_Sprite, x: Scratch_Value) {
	sprite.x = f32(x.number_value)
}

motion_changeyby :: proc(sprite: ^Scratch_Sprite, y: Scratch_Value) {
	sprite.y += f32(y.number_value)
}

motion_sety :: proc(sprite: ^Scratch_Sprite, y: Scratch_Value) {
	sprite.y = f32(y.number_value)
}
