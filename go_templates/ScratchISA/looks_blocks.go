package ScratchISA

import (
	"fmt"
	"slices"
)

func Looks_changesizeby(sprite *ScratchSprite, change ScratchValue) {
	sprite.Size += change.NumberValue
}

func Looks_setsizeto(sprite *ScratchSprite, size ScratchValue) {
	sprite.Size = size.NumberValue
}

func Looks_show(sprite *ScratchSprite) {
	sprite.Show = true
}

func Looks_hide(sprite *ScratchSprite) {
	sprite.Show = false
}

func Looks_gotofrontback(sprite *ScratchSprite) {
	fmt.Println("before ", OrderedRender)
	index := slices.Index(OrderedRender, sprite)
	OrderedRender = append(OrderedRender, sprite)
	//item := OrderedRender[i]
	OrderedRender = append(OrderedRender[:index], OrderedRender[index+1:]...) // Remove item
	OrderedRender = append([]*ScratchSprite{sprite}, OrderedRender...)        // Prepend to front
	fmt.Println("after ", OrderedRender)
}

func Looks_say(sprite *ScratchSprite, message ScratchValue) {
	fmt.Println(message.StringValue)
}

func Looks_size(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(sprite.Size)
}
