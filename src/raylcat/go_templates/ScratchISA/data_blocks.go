package ScratchISA

import "slices"

func Data_setvariableto(target ScratchTarget, context *Context, value ScratchValue, variable ScratchValue) {
	setVariableValue(target, context, variable.StringValue, value)
}

func Data_changevariableby(target ScratchTarget, context *Context, value ScratchValue, variable ScratchValue) {
	newValue := GetVariableValue(target, context, variable.StringValue).NumberValue + value.NumberValue
	setVariableValue(target,
		context,
		variable.StringValue,
		ValueFromFloat64(newValue),
	)
}

func Data_addtolist(target ScratchTarget, context *Context, item ScratchValue, list ScratchValue) {
	setList(target, context, list.StringValue, append(getList(target, context, list.StringValue), item))
}
func Data_deletealloflist(target ScratchTarget, context *Context, list ScratchValue) {
	setList(target, context, list.StringValue, []ScratchValue{})
}
func Data_deleteoflist(target ScratchTarget, context *Context, index ScratchValue, list ScratchValue) {
	setList(target, context, list.StringValue, slices.Delete(getList(target, context, list.StringValue), int(index.NumberValue)-1, int(index.NumberValue)))
}
func Data_insertatlist(target ScratchTarget, context *Context, item ScratchValue, index ScratchValue, list ScratchValue) {
	setList(target, context, list.StringValue, slices.Insert(getList(target, context, list.StringValue), int(index.NumberValue)-1, item))
}
func Data_replaceitemoflist(target ScratchTarget, context *Context, index ScratchValue, item ScratchValue, list ScratchValue) {
	newList := getList(target, context, list.StringValue)
	newList[int(index.NumberValue-1)] = item
	setList(target, context, list.StringValue, newList)
}
func Data_itemoflist(target ScratchTarget, context *Context, index ScratchValue, list ScratchValue) ScratchValue {
	return GetListItem(target, context, list.StringValue, int(index.NumberValue))
}
func Data_itemnumoflist(target ScratchTarget, context *Context, item ScratchValue, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(slices.Index(getList(target, context, list.StringValue), item)) + 1)
}
func Data_lengthoflist(target ScratchTarget, context *Context, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(len(getList(target, context, list.StringValue))))
}
func Data_listcontainsitem(target ScratchTarget, context *Context, item ScratchValue, list ScratchValue) bool {
	return slices.Contains(getList(target, context, list.StringValue), item)
}
