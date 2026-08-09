package ScratchISA

looks_changesizeby :: proc(sprite: ^Scratch_Sprite, change: Scratch_Value) {
	sprite.size += f32(change.number_value)
}

looks_setsizeto :: proc(sprite: ^Scratch_Sprite, size: Scratch_Value) {
	sprite.size = f32(size.number_value)
}

looks_show :: proc(sprite: ^Scratch_Sprite) {
	sprite.show = true
}

looks_hide :: proc(sprite: ^Scratch_Sprite) {
	sprite.show = false
}
