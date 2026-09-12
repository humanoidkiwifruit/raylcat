package ScratchISA

func Data_setvariableto(context *Context, variable ScratchValue, value ScratchValue) {
	context.Variables[variable.StringValue] = value
}
