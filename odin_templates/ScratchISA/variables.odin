package ScratchISA

Scratch_Type :: enum {
	STRING,
	NUMBER,
}

Scratch_Variable :: struct {
	type: Scratch_Type,
	number_value: f64,
	string_value: string,
}
