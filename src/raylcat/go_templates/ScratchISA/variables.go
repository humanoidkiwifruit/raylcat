package ScratchISA

import "strconv"

type ScratchValue struct {
	NumberValue float64
	StringValue string
}

func SetNumber(value *ScratchValue, number float64) {
	value = &ScratchValue{}
	value.NumberValue = number
	value.StringValue = strconv.FormatFloat(number, 'f', -1, 64) //TODO: make this output the actual amount of decimal places scratch uses

}

func SetString(value *ScratchValue, string string) {
	value.StringValue = string
	parsedFloat, err := strconv.ParseFloat(string, 64)
	if err != nil {
		value.NumberValue = 0
	}
	value.NumberValue = parsedFloat
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
