package ScratchISA

import (
	"slices"
)

func Data_setvariableto(context *Context, variable ScratchValue, value ScratchValue) {
	context.Variables[variable.StringValue] = value
}
func Data_addtolist(context *Context, list ScratchValue, item ScratchValue) {
	context.Lists[list.StringValue] = append(context.Lists[list.StringValue], item)
}
func Data_deletealloflist(context *Context, list ScratchValue) {
	context.Lists[list.StringValue] = []ScratchValue{}
}
func Data_deleteoflist(context *Context, list ScratchValue, index ScratchValue) {
	context.Lists[list.StringValue] = slices.Delete(context.Lists[list.StringValue], int(index.NumberValue)-1, int(index.NumberValue))
}
func Data_insertatlist(context *Context, list ScratchValue, item ScratchValue, index ScratchValue) {
	context.Lists[list.StringValue] = slices.Insert(context.Lists[list.StringValue], int(index.NumberValue)-1, item)
}
