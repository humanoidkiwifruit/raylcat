package ScratchISA

import (
	"fmt"
	"image/color"

	rl "github.com/gen2brain/raylib-go/raylib"
)

var collisionsRenderTarget rl.RenderTexture2D //Keep target between runs (performance, no need to reallocate)
var magentaShader rl.Shader                   //Shader to render sprites using when doing collisions
var pixelsA []color.RGBA
var pixelsB []color.RGBA

type drawMode int

const (
	spriteOnly = iota
	allWithShadedSprite
	stage
)

func InitCollisions() {
	collisionsRenderTarget = rl.LoadRenderTexture(int32(rl.GetScreenWidth()), int32(rl.GetScreenHeight()))
	magentaShader = rl.LoadShader("", "perfectmagenta.fs")
}

func CloseCollisions() {
	rl.UnloadShader(magentaShader)
	rl.UnloadRenderTexture(collisionsRenderTarget)
}

func ProcessCollisionRequest(context *Context, req CollisionRequest) {
	if req.Point != nil {
		result := pointHits(context, rl.Vector2{X: req.Point.Point.X, Y: req.Point.Point.Y}, allWithShadedSprite, req.Point.Sprite)
		req.Point.Response <- result
	}
	if req.Sprites != nil {
		result := spritesCollide(context, req.Sprites.SpriteA, req.Sprites.SpriteB)
		req.Sprites.Response <- result

	}
}

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

func spritesCollide(context *Context, spriteA, spriteB *ScratchSprite) bool {

	spriteAimg := (drawToCollisionTarget(context, spriteA, spriteOnly))
	defer rl.UnloadImage(spriteAimg)
	//Get a screenshot of only spriteA in queryColour stamped onto blank background

	spriteBimg := (drawToCollisionTarget(context, spriteB, spriteOnly))
	defer rl.UnloadImage(spriteBimg)
	//Get a screenshot of only spriteB in queryColour stamped onto blank background

	pixelsA = rl.LoadImageColors(spriteAimg)
	defer rl.UnloadImageColors(pixelsA)
	pixelsB = rl.LoadImageColors(spriteBimg)
	defer rl.UnloadImageColors(pixelsB)

	for i := range pixelsA {
		if pixelsA[i] == rl.Magenta &&
			pixelsB[i] == rl.Magenta {
			return true
		}
	}
	return false //No collision
}

// /Stamp a sprite onto a queryColour background. Allobject determines whether or not to draw all the sprites and stage or just the one in question
func drawToCollisionTarget(
	context *Context,
	sprite *ScratchSprite,
	mode drawMode,
) *rl.Image {
	rl.BeginTextureMode(collisionsRenderTarget)

	switch mode {
	case allWithShadedSprite:
		drawSpritesAndStageWithShadedSprite(context, sprite)

	case spriteOnly:
		rl.ClearBackground(rl.Blank)
		rl.BeginShaderMode(magentaShader)
		DrawSprite(sprite)
		rl.EndShaderMode()

	case stage:
		drawShadedStageWithSprites(context)
	default:
		fmt.Println("bad input to drawToCollisionTarget")
	}

	rl.EndTextureMode()

	return rl.LoadImageFromTexture(collisionsRenderTarget.Texture)
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

//STAGE STUFF ##################################################
//STAGE STUFF ##################################################
//STAGE STUFF ##################################################

func drawShadedStageWithSprites(context *Context) {
	rl.ClearBackground(rl.White)

	rl.BeginShaderMode(magentaShader)
	DrawStage(context.Stage)
	rl.EndShaderMode()

	for _, sprite := range context.OrderedRender {
		DrawSprite(sprite)
	}
}
