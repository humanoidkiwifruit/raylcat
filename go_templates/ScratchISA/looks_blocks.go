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

func Looks_gotofrontback(sprite *ScratchSprite, front_back ScratchValue) {
	switch front_back.StringValue {
	case "back":
		index := slices.Index(OrderedRender, sprite)
		OrderedRender = append(OrderedRender[:index], OrderedRender[index+1:]...) // Remove item
		OrderedRender = append([]*ScratchSprite{sprite}, OrderedRender...)        // Prepend to front
	case "front":
		index := slices.Index(OrderedRender, sprite)
		OrderedRender = append(OrderedRender[:index], OrderedRender[index+1:]...) // Remove item
		OrderedRender = append(OrderedRender, sprite)
	}
}

func Looks_say(sprite *ScratchSprite, message ScratchValue) {
	fmt.Println(message.StringValue)
}
func Looks_nextcostume(sprite *ScratchSprite) {
	if sprite.CostumeNumber >= len(sprite.Costumes)-1 {
		sprite.CostumeNumber = 0
	} else {
		sprite.CostumeNumber += 1
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

func Looks_size(sprite *ScratchSprite) ScratchValue {
	return ValueFromFloat64(sprite.Size)
}
