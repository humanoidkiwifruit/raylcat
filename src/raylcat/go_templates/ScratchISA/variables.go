package ScratchISA

import "strconv"

type ScratchValue struct {
	NumberValue float64
	StringValue string
}

func ValueFromFloat64(number float64) ScratchValue {
	return ScratchValue{
		number,
		strconv.FormatFloat(number, 'f', -1, 64),
	} //TODO: make this output the actual amount of decimal places scratch uses
}

func ValueFromString(string string) ScratchValue {
	value := ScratchValue{}
	parsedFloat, err := strconv.ParseFloat(string, 64)
	if err != nil {
		value.NumberValue = 0
	} else {
		value.NumberValue = parsedFloat
	}

	value.StringValue = string
	return value
}
