package ScratchISA
import "core:fmt"
import "core:strconv"
import "core:strings"

/*Scratch_Type :: enum {
	STRING,
	NUMBER,
}*/

Scratch_Value :: struct {
	number_value: f64,
	string_value: string,
}

set_number :: proc(value: ^Scratch_Value, number: f64) {
	value.number_value = number
	value.string_value = strings.clone(fmt.tprintf("%g", number))
}

set_string :: proc(value: ^Scratch_Value, string: string) {
	if len(value.string_value) > 0 {
		delete(value.string_value)
	}
	value.string_value = strings.clone(string)
	number_value, ok := strconv.parse_f64(string)
	if ok {
		value.number_value = number_value
	} else {
		value.number_value = 0
	}
}

create_value_from_f64 :: proc(number: f64) -> Scratch_Value {
	temp_str := fmt.tprintf("%g", number)
	return Scratch_Value{
		number_value = number,
		string_value = strings.clone(temp_str)
	}
}

create_value_from_string :: proc(string: string) -> Scratch_Value {
	number_value, ok := strconv.parse_f64(string)
	if ok {
		return Scratch_Value{
			number_value = number_value,
			string_value = strings.clone(string)
		}
	} else {
		return Scratch_Value{
			number_value = 0,
			string_value = strings.clone(string)
		}
	}
}

update_value :: proc(value: ^Scratch_Value, new_value: Scratch_Value) {
	if len(value.string_value) > 0 {
		delete(value.string_value)
	}
	value.number_value = new_value.number_value
	value.string_value = new_value.string_value
}
