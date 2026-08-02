package ScratchISA
import rl "vendor:raylib"
import "core:text/edit"

Scratch_Sprite :: struct {
	x: f32,
	y: f32,
	size: f32,
	direction: f32,
	costume_number: int,
	texture: rl.Texture2D,
	show: bool,
}

scratch_draw_sprite :: proc(sprite: ^Scratch_Sprite) {
	rl_x := rl.GetScreenWidth()/2 + i32(sprite.x)
	rl_y := rl.GetScreenHeight()/2 + i32(sprite.y)
	rl_rotation := sprite.direction - 90
	//rl.DrawTexture(sprite.texture, rl_x, rl_y, rl.WHITE)

	source := rl.Rectangle{0, 0, f32(sprite.texture.width), f32(sprite.texture.height)}
	dest := rl.Rectangle{f32(rl_x), f32(rl_y), f32(sprite.texture.width), f32(sprite.texture.height)}
	origin := rl.Vector2{
		f32(sprite.texture.width/2), f32(sprite.texture.height/2)}
	if sprite.show {
		rl.DrawTexturePro(sprite.texture, source, dest, origin, rl_rotation, rl.WHITE)
	}
}
