package ScratchISA
import rl "vendor:raylib"
import "core:text/edit"

Scratch_Sprite :: struct { //Struct that represents a scratch sprite
	x: f32,
	y: f32,
	size: f32,
	direction: f32,
	costume_number: int,
	texture: rl.Texture2D,
	show: bool,
}

scratch_draw_sprite :: proc(sprite: ^Scratch_Sprite) {
	screen_w := f32(rl.GetScreenWidth())
	screen_h := f32(rl.GetScreenHeight())

	//Convert scratch coords & rotation into raylib terms
	rl_x := screen_w/2 + sprite.x
	rl_y := screen_h/2 - sprite.y
	rl_rotation := sprite.direction - 90

	source := rl.Rectangle{0, 0, f32(sprite.texture.width), f32(sprite.texture.height)}
	dest := rl.Rectangle{f32(rl_x), f32(rl_y), f32(sprite.texture.width)*0.5, f32(sprite.texture.height)*0.5}

	origin := rl.Vector2{f32(sprite.texture.width/4), f32(sprite.texture.height/4)}
	if sprite.show {
		rl.DrawTexturePro(sprite.texture, source, dest, origin, rl_rotation, rl.WHITE)
	}
}
