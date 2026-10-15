package ScratchISA

import (
	rl "github.com/gen2brain/raylib-go/raylib"
)

var key_mappings map[string]int32 = map[string]int32{
	"left arrow":  rl.KeyLeft,
	"right arrow": rl.KeyRight,
	"up arrow":    rl.KeyUp,
	"down arrow":  rl.KeyDown,
	"space":       rl.KeySpace,
	"a":           rl.KeyA,
	"b":           rl.KeyB,
	"c":           rl.KeyC,
	"d":           rl.KeyD,
	"e":           rl.KeyE,
	"f":           rl.KeyF,
	"g":           rl.KeyG,
	"h":           rl.KeyH,
	"i":           rl.KeyI,
	"j":           rl.KeyJ,
	"k":           rl.KeyK,
	"l":           rl.KeyL,
	"m":           rl.KeyM,
	"n":           rl.KeyN,
	"o":           rl.KeyO,
	"p":           rl.KeyP,
	"q":           rl.KeyQ,
	"r":           rl.KeyR,
	"s":           rl.KeyS,
	"t":           rl.KeyT,
	"u":           rl.KeyU,
	"v":           rl.KeyV,
	"w":           rl.KeyW,
	"x":           rl.KeyX,
	"y":           rl.KeyY,
	"z":           rl.KeyZ,
}

type HatBlockOpcode int

const (
	GreenFlag HatBlockOpcode = iota
	KeyPressed
)

type HatBlock struct {
	Opcode HatBlockOpcode
	Key    string
}

type Context struct {
	Sprites               map[string]*ScratchSprite
	Stage                 *ScratchStage
	Timer                 float64 //timer needs to be updated in the main loop
	RunningScriptControls []ScratchScriptControl
	CollisionRequests     chan CollisionRequest
	OrderedRender         []*ScratchSprite
}
type SpritesCollisionRequest struct {
	SpriteA  *ScratchSprite
	SpriteB  *ScratchSprite
	Response chan bool
}

type PointCollisionRequest struct {
	Point    rl.Vector2
	Sprite   *ScratchSprite
	Response chan bool
}

type CollisionRequest struct {
	Sprites *SpritesCollisionRequest
	Point   *PointCollisionRequest
}

func HandleKeyPressHatBlocks(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == KeyPressed {
				if rl.IsKeyDown(key_mappings[script.Hat.Key]) {
					scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
					context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
					go script.Function(sprite, scriptControl, context)
				}
			}
		}
	}
}

func GetVariableValue(
	sprite *ScratchSprite,
	context *Context,
	variable string,
) ScratchValue {
	if val, ok := sprite.Variables[variable]; ok {
		return val
	}

	return context.Stage.Variables[variable]
}

func setVariableValue(
	sprite *ScratchSprite,
	context *Context,
	variable string,
	value ScratchValue,
) {
	if _, ok := sprite.Variables[variable]; ok {
		sprite.Variables[variable] = value
		return
	}

	context.Stage.Variables[variable] = value
}

func GetListItem(
	sprite *ScratchSprite,
	context *Context,
	list string,
	index int,
) ScratchValue {
	if val, ok := sprite.Lists[list]; ok {
		return val[index-1]
	}

	return context.Stage.Lists[list][index-1]
}

func getList(
	sprite *ScratchSprite,
	context *Context,
	list string,
) []ScratchValue {
	if val, ok := sprite.Lists[list]; ok {
		return val
	}

	return context.Stage.Lists[list]
}

func setList(
	sprite *ScratchSprite,
	context *Context,
	list string,
	value []ScratchValue,
) {
	if _, ok := sprite.Lists[list]; ok {
		sprite.Lists[list] = value
		return
	}

	context.Stage.Lists[list] = value
}

func ScreenCoordsToScratchCoords(x, y float32) (float32, float32) {
	scratchX := x - float32(rl.GetScreenWidth())/2
	scratchY := float32(rl.GetScreenHeight())/2 - y
	return scratchX, scratchY
}

func ScratchCoordsToScreenCoords(x, y float32) (float32, float32) {
	screenX := float32(rl.GetScreenWidth())/2 + x
	screenY := float32(rl.GetScreenHeight())/2 - y
	return screenX, screenY
}

func ProcessCollisionRequest(context *Context, req CollisionRequest) {
	if req.Point != nil {
		result := scratchPointCollidesSprite(rl.Vector2{X: req.Point.Point.X, Y: req.Point.Point.Y}, req.Point.Sprite)
		req.Point.Response <- result
	}
	if req.Sprites != nil {
		result := spritesCollide(req.Sprites.SpriteA, req.Sprites.SpriteB)
		req.Sprites.Response <- result

	}
}

var CollisionsRenderTarget rl.RenderTexture2D //Keep target between runs (performance, no need to reallocate)

func InitCollisions() {
	CollisionsRenderTarget = rl.LoadRenderTexture(int32(rl.GetScreenWidth()), int32(rl.GetScreenHeight()))
}

func scratchPointCollidesSprite(point rl.Vector2, sprite *ScratchSprite) bool {
	x, y := ScratchCoordsToScreenCoords(point.X, point.Y)

	img := drawSpriteToColTarget(sprite)
	defer rl.UnloadImage(img)

	height := rl.GetScreenHeight()
	newY := int32(height - 1 - int(y))
	pointColour := rl.GetImageColor(*img, int32(x), newY) //Does the sprite occupy the given pixel?
	return pointColour != rl.Magenta
}

func spritesCollide(spriteA, spriteB *ScratchSprite) bool {

	spriteAimg := (drawSpriteToColTarget(spriteA))
	defer rl.UnloadImage(spriteAimg)
	//Get a screenshot of only spriteA stamped onto the magenta background

	spriteBimg := (drawSpriteToColTarget(spriteB))
	defer rl.UnloadImage(spriteBimg)
	//Get a screenshot of only spriteB stamped onto the magenta background

	pixelsA := rl.LoadImageColors(spriteAimg)
	defer rl.UnloadImageColors(pixelsA)
	pixelsB := rl.LoadImageColors(spriteBimg)
	defer rl.UnloadImageColors(pixelsB)

	for i := range pixelsA {
		if pixelsA[i] != rl.Magenta &&
			pixelsB[i] != rl.Magenta {
			return true
		}
	}
	return false //No collision
}

func drawSpriteToColTarget(sprite *ScratchSprite) *rl.Image { //Stamp a sprite onto a magenta background

	rl.BeginTextureMode(CollisionsRenderTarget)
	rl.ClearBackground(rl.Magenta)
	DrawSprite(sprite)
	rl.EndTextureMode()

	img := rl.LoadImageFromTexture(CollisionsRenderTarget.Texture)

	return img
}

func RunScripts(context *Context) {

	HandleKeyPressHatBlocks(context)

	for _, control := range context.RunningScriptControls {
		control.AwakenChan <- struct{}{}
	ThisRequests:
		for {
			select {
			case <-control.FinishedChan:
				break ThisRequests
			case req := <-context.CollisionRequests:
				ProcessCollisionRequest(context, req)
			}
		}
	}
}

func SetupGreenFlagScripts(context *Context) {
	for _, sprite := range context.Sprites {
		for _, script := range sprite.Scripts {
			if script.Hat.Opcode == GreenFlag {
				scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
				context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
				go script.Function(sprite, scriptControl, context)
			}
		}
	}
	for _, script := range context.Stage.Scripts {
		if script.Hat.Opcode == GreenFlag {
			scriptControl := ScratchScriptControl{AwakenChan: make(chan struct{}), FinishedChan: make(chan struct{})}
			context.RunningScriptControls = append(context.RunningScriptControls, scriptControl)
			go script.Function(context.Stage, scriptControl, context)
		}
	}
}
func DrawEverything(context *Context) {
	rl.BeginDrawing()
	rl.ClearBackground(rl.White)
	DrawStage(context.Stage)
	for _, sprite := range context.OrderedRender {
		DrawSprite(sprite)
	}
	//TEMPLATING:DRAW_FRAMERATE
	rl.EndDrawing()
}
func UpdateTimer(context *Context) {
	context.Timer += float64(rl.GetFrameTime())

}
