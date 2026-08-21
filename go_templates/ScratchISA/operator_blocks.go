package ScratchISA

import (
	"math"
	"math/rand/v2"
	"unicode/utf8"
)

func Operator_add(sprite *ScratchSprite, num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue + num2.NumberValue)
}

func Operator_subtract(sprite *ScratchSprite, num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue - num2.NumberValue)
}

func Operator_multiply(sprite *ScratchSprite, num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue * num2.NumberValue)
}

func Operator_divide(sprite *ScratchSprite, num1 ScratchValue, num2 ScratchValue) ScratchValue {
	return ValueFromFloat64(num1.NumberValue / num2.NumberValue)
}
func Operator_random(sprite *ScratchSprite, from ScratchValue, to ScratchValue) ScratchValue {
	if math.Trunc(from.NumberValue) != from.NumberValue || math.Trunc(to.NumberValue) != to.NumberValue { //from or to has decimal places
		randFloatingPoint := from.NumberValue + rand.Float64()*(to.NumberValue-from.NumberValue)
		return ValueFromFloat64(math.Round(randFloatingPoint*100) / 100)
	} else { //both of the inputs are 'integers'
		return ValueFromFloat64(float64(int(from.NumberValue) + rand.N(int(to.NumberValue-from.NumberValue+1))))
	}
}
func Operator_gt(sprite *ScratchSprite, operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1.NumberValue > operand2.NumberValue
}

func Operator_lt(sprite *ScratchSprite, operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1.NumberValue < operand2.NumberValue
}

func Operator_equals(sprite *ScratchSprite, operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1 == operand2
}

func Operator_and(sprite *ScratchSprite, operand2 bool, operand1 bool) bool {
	return operand2 && operand1
}

func Operator_or(sprite *ScratchSprite, operand1 bool, operand2 bool) bool {
	return operand1 || operand2
}

func Operator_not(sprite *ScratchSprite, operand bool) bool {
	return !operand
}

func Operator_join(sprite *ScratchSprite, string1 ScratchValue, string2 ScratchValue) ScratchValue {
	return ValueFromString(string1.StringValue + string2.StringValue)
}

func Operator_length(sprite *ScratchSprite, string ScratchValue) ScratchValue {
	return ValueFromFloat64(float64(utf8.RuneCountInString(string.StringValue)))
}
