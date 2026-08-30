package ScratchISA

func Motion_goto_menu(sprite *ScratchSprite, to ScratchValue) ScratchValue {
	return ValueFromString(to.StringValue)
}
