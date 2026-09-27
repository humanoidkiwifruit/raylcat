package ScratchISA

import (
	"slices"
)

func Data_setvariableto(context *Context, value ScratchValue, variable ScratchValue) {
	context.Variables[variable.StringValue] = value
}
func Data_changevariableby(context *Context, value ScratchValue, variable ScratchValue) {
	context.Variables[variable.StringValue] = ValueFromFloat64(context.Variables[variable.StringValue].NumberValue + 1)
}
func Data_addtolist(context *Context, item ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue] = append(context.Lists[list.StringValue], item)
}
func Data_deletealloflist(context *Context, list ScratchValue) {
	context.Lists[list.StringValue] = []ScratchValue{}
}
func Data_deleteoflist(context *Context, index ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue] = slices.Delete(context.Lists[list.StringValue], int(index.NumberValue)-1, int(index.NumberValue))
}
func Data_insertatlist(context *Context, item ScratchValue, index ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue] = slices.Insert(context.Lists[list.StringValue], int(index.NumberValue)-1, item)
}
func Data_replaceitemoflist(context *Context, index ScratchValue, item ScratchValue, list ScratchValue) {
	context.Lists[list.StringValue][int(index.NumberValue)-1] = item
}
func Data_itemoflist(context *Context, index ScratchValue, list ScratchValue) ScratchValue {
	return context.Lists[list.StringValue][int(index.NumberValue-1)]
}
func Data_itemnumoflist(context *Context, item ScratchValue, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(slices.Index(context.Lists[list.StringValue], item)) + 1)
}
func Data_lengthoflist(context *Context, list ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(len(context.Lists[list.StringValue])))
}
func Data_listcontainsitem(context *Context, item ScratchValue, list ScratchValue) bool {
	return slices.Contains(context.Lists[list.StringValue], item)
}
