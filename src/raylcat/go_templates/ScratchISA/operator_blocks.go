package ScratchISA

import (
	"math"
	"math/rand/v2"
	"strings"
	"unicode/utf8"
)

func Operator_add(num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue + num2.NumberValue)
}

func Operator_subtract(num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue - num2.NumberValue)
}

func Operator_multiply(num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue * num2.NumberValue)
}

func Operator_divide(num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue / num2.NumberValue)
}
func Operator_random(from ScratchValue, to ScratchValue) ScratchValue {
	if math.Trunc(from.NumberValue) != from.NumberValue || math.Trunc(to.NumberValue) != to.NumberValue { //from or to has decimal places
		randFloatingPoint := from.NumberValue + rand.Float64()*(to.NumberValue-from.NumberValue)
		return ValueFromFloat64(math.Round(randFloatingPoint*100) / 100)
	} else { //both of the inputs are 'integers'
		return ValueFromFloat64(float64(int(from.NumberValue) + rand.N(int(to.NumberValue-from.NumberValue+1))))
	}
}
func Operator_gt(operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1.NumberValue > operand2.NumberValue
}

func Operator_lt(operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1.NumberValue < operand2.NumberValue
}

func Operator_equals(operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1 == operand2
}

func Operator_and(operand2 bool, operand1 bool) bool {
	return operand2 && operand1
}

func Operator_or(operand1 bool, operand2 bool) bool {
	return operand1 || operand2
}

func Operator_not(operand bool) bool {
	return !operand
}

func Operator_join(string1 ScratchValue, string2 ScratchValue) ScratchValue {
	return ValueFromString(string1.StringValue + string2.StringValue)
}

func Operator_letter_of(letter ScratchValue, inputstring ScratchValue) ScratchValue { //inputstring mustn't be named string as it would conflict
	runes := []rune(inputstring.StringValue)
	index := int(letter.NumberValue) - 1 //scratch starts at 1
	if index < 0 || index >= len(runes) {
		return ValueFromString("")
	}
	char := string(runes[index])
	return ValueFromString(char)
}

func Operator_length(string ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(utf8.RuneCountInString(string.StringValue)))
}

func Operator_contains(string1 ScratchValue, string2 ScratchValue) bool {
	return strings.Contains(string1.StringValue, string2.StringValue)
}
