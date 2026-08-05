package ScratchISA

motion_gotoxy :: proc(sprite: ^Scratch_Sprite, x, y : f32) {
	sprite.x = x
	sprite.y = y
}

motion_pointindirection :: proc(sprite: ^Scratch_Sprite, direction: f32) {
	sprite.direction = direction
}
