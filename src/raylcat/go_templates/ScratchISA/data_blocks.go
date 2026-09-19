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
