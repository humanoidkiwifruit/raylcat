package ScratchISA

func Data_setvariableto(context *Context, variable ScratchValue, value ScratchValue) {
	context.Variables[variable.StringValue] = value
}
func Data_addtolist(context *Context, list ScratchValue, item ScratchValue) {
	context.Lists[list.StringValue] = append(context.Lists[list.StringValue], item)
}
func Data_deletealloflist(context *Context, list ScratchValue) {
	context.Lists[list.StringValue] = []ScratchValue{}
}
