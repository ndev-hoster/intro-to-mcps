import re
import math
import argparse

# Custom Exceptions
class CalculatorError(Exception):
    pass

class InvalidSyntaxError(CalculatorError):
    pass

class DivideByZeroError(CalculatorError):
    pass

class UnsupportedCharacterError(CalculatorError):
    pass

# Token types
NUMBER = 'NUMBER'
OPERATOR = 'OPERATOR'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
UNARY_MINUS_OP = 'UNARY_MINUS_OP' # Special token for unary minus

# Operator precedence and associativity
OPERATORS = {
    '+': {'precedence': 1, 'associativity': 'left', 'arity': 2},
    '-': {'precedence': 1, 'associativity': 'left', 'arity': 2},
    '*': {'precedence': 2, 'associativity': 'left', 'arity': 2},
    '/': {'precedence': 2, 'associativity': 'left', 'arity': 2},
    '^': {'precedence': 3, 'associativity': 'right', 'arity': 2},
    UNARY_MINUS_OP: {'precedence': 4, 'associativity': 'right', 'arity': 1} # Unary minus has highest precedence
}

class Token:
    """Represents a token in the expression."""
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, {self.value})"
        return f"Token({self.type})"

def tokenize(expression):
    """
    Performs lexical analysis on the input expression string.
    Converts the string into a list of tokens.
    Handles unary minus by replacing it with a special UNARY_MINUS_OP token.
    """
    tokens = []
    i = 0
    # Regex to match numbers (integers and floats)
    number_pattern = re.compile(r'\d+(\.\d*)?|\.\d+')

    # Helper to check if the current minus is unary
    def is_unary_minus(current_index):
        if current_index == 0:
            return True
        prev_token = tokens[-1] if tokens else None
        return (prev_token is None or
                prev_token.type == LPAREN or
                (prev_token.type == OPERATOR and prev_token.value not in [RPAREN, NUMBER]))

    while i < len(expression):
        char = expression[i]

        if char.isspace():
            i += 1
            continue

        if char.isdigit() or (char == '.' and i + 1 < len(expression) and expression[i+1].isdigit()):
            match = number_pattern.match(expression, i)
            if match:
                num_str = match.group(0)
                tokens.append(Token(NUMBER, float(num_str)))
                i += len(num_str)
                continue

        if char == '+':
            tokens.append(Token(OPERATOR, '+'))
        elif char == '*':
            tokens.append(Token(OPERATOR, '*'))
        elif char == '/':
            tokens.append(Token(OPERATOR, '/'))
        elif char == '^':
            tokens.append(Token(OPERATOR, '^'))
        elif char == '(':
            tokens.append(Token(LPAREN, '('))
        elif char == ')':
            tokens.append(Token(RPAREN, ')'))
        elif char == '-':
            if is_unary_minus(i):
                tokens.append(Token(OPERATOR, UNARY_MINUS_OP))
            else:
                tokens.append(Token(OPERATOR, '-'))
        else:
            raise UnsupportedCharacterError(f"Unsupported character: '{char}' at position {i}")
        i += 1

    return tokens

def shunting_yard(tokens):
    """
    Converts an infix expression (list of tokens) to Reverse Polish Notation (RPN).
    Implements the Shunting-Yard algorithm.
    """
    output_queue = []
    operator_stack = []

    for token in tokens:
        if token.type == NUMBER:
            output_queue.append(token)
        elif token.type == OPERATOR:
            while (operator_stack and
                   operator_stack[-1].type == OPERATOR and
                   operator_stack[-1].value != LPAREN and
                   (OPERATORS[operator_stack[-1].value]['precedence'] > OPERATORS[token.value]['precedence'] or
                    (OPERATORS[operator_stack[-1].value]['precedence'] == OPERATORS[token.value]['precedence'] and
                     OPERATORS[token.value]['associativity'] == 'left'))):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token.type == LPAREN:
            operator_stack.append(token)
        elif token.type == RPAREN:
            while operator_stack and operator_stack[-1].type != LPAREN:
                output_queue.append(operator_stack.pop())
            if not operator_stack:
                raise InvalidSyntaxError("Mismatched parentheses: missing '('")
            operator_stack.pop() # Pop the '('

    while operator_stack:
        op = operator_stack.pop()
        if op.type == LPAREN:
            raise InvalidSyntaxError("Mismatched parentheses: missing ')'")
        output_queue.append(op)

    return output_queue

def evaluate_rpn(rpn_tokens):
    """
    Evaluates an expression in Reverse Polish Notation (RPN).
    """
    operand_stack = []

    for token in rpn_tokens:
        if token.type == NUMBER:
            operand_stack.append(token.value)
        elif token.type == OPERATOR:
            op_info = OPERATORS[token.value]
            arity = op_info['arity']

            if len(operand_stack) < arity:
                raise InvalidSyntaxError(f"Insufficient operands for operator '{token.value}'")

            if arity == 2:
                right_operand = operand_stack.pop()
                left_operand = operand_stack.pop()
                if token.value == '+':
                    operand_stack.append(left_operand + right_operand)
                elif token.value == '-':
                    operand_stack.append(left_operand - right_operand)
                elif token.value == '*':
                    operand_stack.append(left_operand * right_operand)
                elif token.value == '/':
                    if right_operand == 0:
                        raise DivideByZeroError("Cannot divide by zero")
                    operand_stack.append(left_operand / right_operand)
                elif token.value == '^':
                    operand_stack.append(left_operand ** right_operand)
            elif arity == 1: # Unary minus
                operand = operand_stack.pop()
                if token.value == UNARY_MINUS_OP:
                    operand_stack.append(-operand)

    if len(operand_stack) != 1:
        raise InvalidSyntaxError("Invalid expression: too many operands or operators")

    return operand_stack[0]

def calculate(expression):
    """
    Main function to tokenize, convert to RPN, and evaluate an expression.
    """
    if not expression.strip():
        raise InvalidSyntaxError("Empty expression")

    tokens = tokenize(expression)
    rpn_tokens = shunting_yard(tokens)
    result = evaluate_rpn(rpn_tokens)
    return result

def format_result(value):
    """
    Formats the numerical result to strip unnecessary trailing zeros.
    Limits to 10 decimal places for consistency.
    """
    if value == int(value):
        return str(int(value))
    return f"{value:.10f}".rstrip('0').rstrip('.')

def main():
    parser = argparse.ArgumentParser(description="CLI Expression Evaluator (BODMAS)")
    parser.add_argument("expression", nargs='*', help="Mathematical expression to evaluate") # Changed nargs to '*' for testing
    args = parser.parse_args()

    if args.expression:
        expression_str = " ".join(args.expression) # Join arguments for testing
        try:
            result = calculate(expression_str)
            print(format_result(result))
        except CalculatorError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("CLI Expression Evaluator (BODMAS) - Interactive Mode")
        print("Enter 'exit' or 'quit' to stop.")
        while True:
            try:
                expression = input(">>> ")
                if expression.lower() in ['exit', 'quit']:
                    break
                if not expression.strip():
                    continue
                result = calculate(expression)
                print(format_result(result))
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
            except CalculatorError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
