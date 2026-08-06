package ScratchISA

import "core:math"

motion_movesteps :: proc(sprite: ^Scratch_Sprite, steps: f32) {
	sprite_direction_rad := math.to_radians(sprite.direction - 90)
	//sprite.x += math.sin(math.to_radians(sprite_direction_rad))
	dx := steps * math.cos(sprite_direction_rad);
	dy := steps * math.sin(sprite_direction_rad);
	sprite.x += dx
	sprite.y -= dy
}

motion_turnright :: proc(sprite: ^Scratch_Sprite, degrees: f32) {
	sprite.direction += degrees
}

motion_turnleft :: proc(sprite: ^Scratch_Sprite, degrees: f32) {
	sprite.direction -= degrees
}

motion_gotoxy :: proc(sprite: ^Scratch_Sprite, x, y : f32) {
	sprite.x = x
	sprite.y = y
}

motion_pointindirection :: proc(sprite: ^Scratch_Sprite, direction: f32) {
	sprite.direction = direction
}

motion_changexby :: proc(sprite: ^Scratch_Sprite, x: f32) {
	sprite.x += x
}

motion_setx :: proc(sprite: ^Scratch_Sprite, x: f32) {
	sprite.x = x
}

motion_changeyby :: proc(sprite: ^Scratch_Sprite, y: f32) {
	sprite.y += y
}

motion_sety :: proc(sprite: ^Scratch_Sprite, y: f32) {
	sprite.y = y
}
