package ScratchISA

func Data_setvariableto(sprite *ScratchSprite, context *Context, value ScratchValue, variable ScratchValue) {
	setVariableValue(sprite, context, variable.StringValue, value)
}
func Data_changevariableby(sprite *ScratchSprite, context *Context, value ScratchValue, variable ScratchValue) {
	setVariableValue(sprite, context, variable.StringValue, ValueFromFloat64((GetVariableValue(sprite, context, variable.StringValue).NumberValue)+1))
}

/*
func Data_addtolist(sprite *ScratchSprite, context *Context, item ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue] = append(context.Lists[list.StringValue], item)
}
func Data_deletealloflist(sprite *ScratchSprite, context *Context, list ScratchValue) {
	context.Lists[list.StringValue] = []ScratchValue{}
}
func Data_deleteoflist(sprite *ScratchSprite, context *Context, index ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue] = slices.Delete(context.Lists[list.StringValue], int(index.NumberValue)-1, int(index.NumberValue))
}
func Data_insertatlist(sprite *ScratchSprite, context *Context, item ScratchValue, index ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue] = slices.Insert(context.Lists[list.StringValue], int(index.NumberValue)-1, item)
}
func Data_replaceitemoflist(sprite *ScratchSprite, context *Context, index ScratchValue, item ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue][int(index.NumberValue)-1] = item
}
func Data_itemoflist(sprite *ScratchSprite, context *Context, index ScratchValue, list ScratchValue) ScratchValue {
	return context.Lists[list.StringValue][int(index.NumberValue-1)]
}
func Data_itemnumoflist(sprite *ScratchSprite, context *Context, item ScratchValue, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(slices.Index(context.Lists[list.StringValue], item)) + 1)
}
func Data_lengthoflist(sprite *ScratchSprite, context *Context, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(len(context.Lists[list.StringValue])))
}
func Data_listcontainsitem(sprite *ScratchSprite, context *Context, item ScratchValue, list ScratchValue) bool {
	return slices.Contains(context.Lists[list.StringValue], item)
}
*/
