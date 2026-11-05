package ScratchISA

import (
	"fmt"

	rl "github.com/gen2brain/raylib-go/raylib"
)

var CollisionsRenderTarget rl.RenderTexture2D //Keep target between runs (performance, no need to reallocate)
var magentaShader rl.Shader                   //Shader to render sprites using when doing collisions
var redShader rl.Shader                       //Shader to draw the
var greenShader rl.Shader

type drawMode int

const (
	//Draw everything and shade a sprite
	shadedSprite = iota
	//Draw everything and shade the stage
	shadedStage
)

// Set up and allocate everything needed for collisions. Remember to call CloseCollisions()
func InitCollisions() {
	CollisionsRenderTarget = rl.LoadRenderTexture(int32(rl.GetScreenWidth()), int32(rl.GetScreenHeight()))
	magentaShader = rl.LoadShader("", "perfectmagenta.frag")
	redShader = rl.LoadShader("", "redshader.frag")
	greenShader = rl.LoadShader("", "greenshader.frag")
}

// Deconstruct everything needed for collisions
func CloseCollisions() {
	rl.UnloadShader(magentaShader)
	rl.UnloadShader(redShader)
	rl.UnloadShader(greenShader)
	rl.UnloadRenderTexture(CollisionsRenderTarget)
}

func ProcessCollisionRequest(context *Context, req CollisionRequest) {
	if req.Point != nil { //It's a point collision request
		result := pointHits(context, rl.Vector2{X: req.Point.Point.X, Y: req.Point.Point.Y}, shadedSprite, req.Point.Sprite)
		req.Point.Response <- result
	}
	if req.Sprites != nil { //It's a sprite-sprite collision request
		result := spritesCollide(req.Sprites.SpriteA, req.Sprites.SpriteB)
		req.Sprites.Response <- result

	}
}

// /Point collides with sprite, with drawing mode
func pointHits(
	context *Context,
	point rl.Vector2,
	mode drawMode,
	sprite *ScratchSprite,
) bool {
	x, y := ScratchCoordsToScreenCoords(point.X, point.Y)

	img := drawToCollisionTarget(context, sprite, mode)
	defer rl.UnloadImage(img)

	screenY := int32(rl.GetScreenHeight() - 1 - int(y))
	pointColour := rl.GetImageColor(*img, int32(x), screenY)

	return pointColour == rl.Magenta
}

func spritesCollide(spriteA, spriteB *ScratchSprite) bool {

	rl.BeginTextureMode(CollisionsRenderTarget) //Draw to the shared target

	{
		rl.ClearBackground(rl.Blank)

		rl.BeginShaderMode(redShader) //Draw the first sprite on the red channel
		{
			DrawSprite(spriteA)
		}
		rl.EndShaderMode()

		rl.BeginBlendMode(rl.BlendAdditive) //Draw the second sprite such that it adds to the channels rather than tinting
		{
			rl.BeginShaderMode(greenShader) //Draw in green channel
			{
				DrawSprite(spriteB)
			}
			rl.EndShaderMode()
		}
		rl.EndBlendMode()
	}
	rl.EndTextureMode()

	img := rl.LoadImageFromTexture(CollisionsRenderTarget.Texture)
	defer rl.UnloadImage(img)

	//Get a screenshot of only spriteB in queryColour stamped onto blank background

	pixels := rl.LoadImageColors(img)
	defer rl.UnloadImageColors(pixels)
	for _, v := range pixels {
		if v.R == 255 && v.G == 255 { //If a pixel has red and green...
			return true
		}
	}
	return false //No collision
}

// Stamp a sprite or the stage onto a magenta background. *Only for use by point collisions*
func drawToCollisionTarget(
	context *Context,
	sprite *ScratchSprite,
	mode drawMode,
) *rl.Image {
	rl.BeginTextureMode(CollisionsRenderTarget)

	switch mode {
	case shadedSprite: //Shade a sprites
		drawSpritesAndStageWithShadedSprite(context, sprite)

	case shadedStage: //Shade the stage
		drawShadedStageWithSprites(context)
	default:
		fmt.Println("bad input to drawToCollisionTarget")
	}

	rl.EndTextureMode()

	return rl.LoadImageFromTexture(CollisionsRenderTarget.Texture)
}

func drawSpritesAndStageWithShadedSprite(
	context *Context,
	shadedSprite *ScratchSprite,
) {
	rl.ClearBackground(rl.White)
	DrawStage(context.Stage)

	for _, sprite := range context.OrderedRender {
		if sprite == shadedSprite {
			rl.BeginShaderMode(magentaShader)
			DrawSprite(sprite)
			rl.EndShaderMode()
		} else {
			DrawSprite(sprite)
		}
	}
}

func drawShadedStageWithSprites(context *Context) {
	rl.ClearBackground(rl.White)

	rl.BeginShaderMode(magentaShader)
	DrawStage(context.Stage)
	rl.EndShaderMode()

	for _, sprite := range context.OrderedRender {
		DrawSprite(sprite)
	}
}
