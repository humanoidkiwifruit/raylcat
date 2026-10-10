package ScratchISA

import "slices"

func Data_setvariableto(sprite *ScratchSprite, context *Context, value ScratchValue, variable ScratchValue) {
	setVariableValue(sprite, context, variable.StringValue, value)
}
func Data_changevariableby(sprite *ScratchSprite, context *Context, value ScratchValue, variable ScratchValue) {
	setVariableValue(sprite, context, variable.StringValue, ValueFromFloat64((GetVariableValue(sprite, context, variable.StringValue).NumberValue)+value.NumberValue))
}

func Data_addtolist(sprite *ScratchSprite, context *Context, item ScratchValue, list ScratchValue) {
	setList(sprite, context, list.StringValue, append(getList(sprite, context, list.StringValue), item))
}
func Data_deletealloflist(sprite *ScratchSprite, context *Context, list ScratchValue) {
	setList(sprite, context, list.StringValue, []ScratchValue{})
}
func Data_deleteoflist(sprite *ScratchSprite, context *Context, index ScratchValue, list ScratchValue) {
	setList(sprite, context, list.StringValue, slices.Delete(getList(sprite, context, list.StringValue), int(index.NumberValue)-1, int(index.NumberValue)))
}
func Data_insertatlist(sprite *ScratchSprite, context *Context, item ScratchValue, index ScratchValue, list ScratchValue) {
	setList(sprite, context, list.StringValue, slices.Insert(getList(sprite, context, list.StringValue), int(index.NumberValue)-1, item))
}
func Data_replaceitemoflist(sprite *ScratchSprite, context *Context, index ScratchValue, item ScratchValue, list ScratchValue) {
	newList := getList(sprite, context, list.StringValue)
	newList[int(index.NumberValue-1)] = item
	setList(sprite, context, list.StringValue, newList)
}
func Data_itemoflist(sprite *ScratchSprite, context *Context, index ScratchValue, list ScratchValue) ScratchValue {
	return GetListItem(sprite, context, list.StringValue, int(index.NumberValue))
}
func Data_itemnumoflist(sprite *ScratchSprite, context *Context, item ScratchValue, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(slices.Index(getList(sprite, context, list.StringValue), item)) + 1)
}
func Data_lengthoflist(sprite *ScratchSprite, context *Context, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(len(getList(sprite, context, list.StringValue))))
}
func Data_listcontainsitem(sprite *ScratchSprite, context *Context, item ScratchValue, list ScratchValue) bool {
	return slices.Contains(getList(sprite, context, list.StringValue), item)
}
