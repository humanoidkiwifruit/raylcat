package ScratchISA

import (
	"fmt"
	"slices"
)

func Looks_switchcostumeto(sprite *ScratchSprite, costume ScratchValue) {
	for index, currentCostume := range sprite.Costumes {
		if currentCostume.Name == costume.StringValue {
			sprite.CostumeNumber = index + 1
		}
	}
}
func Looks_switchbackdropto(context *Context, backdrop ScratchValue) {
	for i, v := range context.Stage.Costumes {
		if v.Name == backdrop.StringValue {
			context.Stage.CostumeNumber = i + 1
			return
		}
	}
	fmt.Println("something went wrong in switchbackdropto")
}

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

func Looks_gotofrontback(context *Context, sprite *ScratchSprite, front_back ScratchValue) {
	switch front_back.StringValue {
	case "back":
		index := slices.Index(context.OrderedRender, sprite)
		context.OrderedRender = append(context.OrderedRender[:index], context.OrderedRender[index+1:]...) // Remove item
		context.OrderedRender = append([]*ScratchSprite{sprite}, context.OrderedRender...)                // Prepend to front
	case "front":
		index := slices.Index(context.OrderedRender, sprite)
		context.OrderedRender = append(context.OrderedRender[:index], context.OrderedRender[index+1:]...) // Remove item
		context.OrderedRender = append(context.OrderedRender, sprite)
	}
}

func Looks_say(sprite *ScratchSprite, message ScratchValue) {
	fmt.Println(message.StringValue)
}
func Looks_nextcostume(sprite *ScratchSprite) {
	if sprite.CostumeNumber >= len(sprite.Costumes) {
		sprite.CostumeNumber = 1
	} else {
		sprite.CostumeNumber += 1
	}
}

func Looks_nextbackdrop(context *Context) {
	stage := context.Stage
	if stage.CostumeNumber >= len(stage.Costumes) {
		stage.CostumeNumber = 1
	} else {
		stage.CostumeNumber += 1
	}
}

func Looks_costumenumbername(sprite *ScratchSprite, number_name ScratchValue) ScratchValue {
	if number_name.StringValue == "name" {
		return ValueFromString(sprite.Costumes[sprite.CostumeNumber-1].Name)
	} else if number_name.StringValue == "number" {
		return ValueFromFloat64(float64(sprite.CostumeNumber))
	} else {
		fmt.Println("Malformed input to Looks_costumenumbername")
		return ValueFromString("") //TODO: Proper error handling
	}
}

func Looks_backdropnumbername(context *Context, number_name ScratchValue) ScratchValue {
	backdrop_number := context.Stage.CostumeNumber
	if number_name.StringValue == "name" {
		return ValueFromString(context.Stage.Costumes[backdrop_number-1].Name)
	} else if number_name.StringValue == "number" {
		return ValueFromFloat64(float64(backdrop_number))
	} else {
		fmt.Println("Malformed input to Looks_costumenumbername")
		return ValueFromString("") //TODO: Proper error handling
	}
}
func Looks_size(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(sprite.Size)
}
