package ScratchISA

func Operator_and(sprite *ScratchSprite, operand2 bool, operand1 bool) bool {
	return operand2 && operand1
}
func Operator_gt(sprite *ScratchSprite, operand1 ScratchValue, operand2 ScratchValue) bool {
	return operand1.NumberValue > operand2.NumberValue
}
