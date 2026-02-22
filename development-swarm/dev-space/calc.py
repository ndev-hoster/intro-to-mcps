#!/usr/bin/env python3
import sys

# --- Constants & Config ---
PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2
}
MAX_STACK_DEPTH = 100

# --- Exceptions ---
class CalcError(Exception):
    """Base class for calculator errors."""
    pass

class SyntaxError(CalcError):
    pass

class DivisionByZeroError(CalcError):
    pass

# --- Core Logic ---

def tokenize(expression):
    """
    Scans the input string and produces a list of tokens.
    Handles integers, floats, operators, and parentheses.
    """
    tokens = []
    i = 0
    n = len(expression)
    
    while i < n:
        char = expression[i]
        
        if char.isspace():
            i += 1
            continue
        
        if char in '()+-*/':
            tokens.append(char)
            i += 1
            continue
        
        if char.isdigit() or char == '.':
            # Extract number
            start = i
            dot_count = 0
            while i < n and (expression[i].isdigit() or expression[i] == '.'):
                if expression[i] == '.':
                    dot_count += 1
                i += 1
            
            if dot_count > 1:
                raise SyntaxError(f"Invalid number format: {expression[start:i]}")
            
            num_str = expression[start:i]
            # Validate it's not just a dot
            if num_str == '.':
                 raise SyntaxError("Invalid character: .")
            
            try:
                if '.' in num_str:
                    tokens.append(float(num_str))
                else:
                    tokens.append(int(num_str))
            except ValueError:
                raise SyntaxError(f"Invalid number: {num_str}")
            continue
            
        raise SyntaxError(f"Invalid character: {char}")
        
    return tokens

def validate_infix(tokens):
    """
    Validates the token stream for common infix errors before processing.
    """
    if not tokens:
        return

    # Check first token
    if tokens[0] in PRECEDENCE:
        raise SyntaxError(f"Unexpected operator at start: {tokens[0]}")
        
    # Check last token
    if tokens[-1] in PRECEDENCE:
        raise SyntaxError(f"Unexpected operator at end: {tokens[-1]}")
        
    if tokens[-1] == '(':
        raise SyntaxError("Unexpected ( at end")

    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next_t = tokens[i+1]
        
        # Number followed by Number
        if isinstance(curr, (int, float)) and isinstance(next_t, (int, float)):
             raise SyntaxError(f"Missing operator between {curr} and {next_t}")
             
        # Number followed by (
        if isinstance(curr, (int, float)) and next_t == '(':
             raise SyntaxError(f"Missing operator between {curr} and (")
             
        # ) followed by Number
        if curr == ')' and isinstance(next_t, (int, float)):
             raise SyntaxError(f"Missing operator between ) and {next_t}")
             
        # ) followed by (
        if curr == ')' and next_t == '(':
             raise SyntaxError("Missing operator between ) and (")
             
        # Operator followed by Operator
        if curr in PRECEDENCE and next_t in PRECEDENCE:
             raise SyntaxError(f"Unexpected operator {next_t} after {curr}")
             
        # ( followed by Operator
        if curr == '(' and next_t in PRECEDENCE:
             raise SyntaxError(f"Unexpected operator {next_t} after (")
             
        # Operator followed by )
        if curr in PRECEDENCE and next_t == ')':
             raise SyntaxError(f"Unexpected ) after operator {curr}")
             
        # Empty parens ()
        if curr == '(' and next_t == ')':
             raise SyntaxError("Empty parentheses")

def shunting_yard(tokens):
    """
    Converts infix tokens to Reverse Polish Notation (RPN) using the Shunting-Yard algorithm.
    """
    output_queue = []
    operator_stack = []
    
    for token in tokens:
        if isinstance(token, (int, float)):
            output_queue.append(token)
        
        elif token in PRECEDENCE:
            while (operator_stack and operator_stack[-1] != '(' and
                   PRECEDENCE.get(operator_stack[-1], 0) >= PRECEDENCE[token]):
                output_queue.append(operator_stack.pop())
            
            if len(operator_stack) >= MAX_STACK_DEPTH:
                raise SyntaxError("Stack depth limit exceeded")
            operator_stack.append(token)
            
        elif token == '(':
            if len(operator_stack) >= MAX_STACK_DEPTH:
                raise SyntaxError("Stack depth limit exceeded")
            operator_stack.append(token)
            
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output_queue.append(operator_stack.pop())
            
            if not operator_stack:
                raise SyntaxError("Mismatched parentheses")
            
            operator_stack.pop() # Pop '('
            
    while operator_stack:
        if operator_stack[-1] == '(':
            raise SyntaxError("Mismatched parentheses")
        output_queue.append(operator_stack.pop())
        
    return output_queue

def evaluate_rpn(rpn_queue):
    """
    Evaluates an RPN queue.
    """
    stack = []
    
    for token in rpn_queue:
        if isinstance(token, (int, float)):
            stack.append(token)
        elif token in PRECEDENCE:
            if len(stack) < 2:
                raise SyntaxError("Invalid expression")
            
            b = stack.pop()
            a = stack.pop()
            
            if token == '+':
                result = a + b
            elif token == '-':
                result = a - b
            elif token == '*':
                result = a * b
            elif token == '/':
                if b == 0:
                    raise DivisionByZeroError("Division by zero")
                result = a / b
            
            stack.append(result)
        else:
            raise SyntaxError(f"Unknown token in RPN: {token}")
            
    if len(stack) != 1:
        raise SyntaxError("Invalid expression")
        
    return stack[0]

def calculate(expression):
    """
    Orchestrates the calculation process.
    """
    try:
        if not expression.strip():
            return ""
        tokens = tokenize(expression)
        if not tokens:
            return ""
            
        validate_infix(tokens)
        
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn)
        
        # Format output
        if isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            else:
                # Round to 4 decimal places if needed, or just stringify
                # Spec says "at least 4 decimal places". 
                return f"{result:.4f}".rstrip('0').rstrip('.') if '.' in f"{result:.4f}" else f"{result:.4f}"
        return str(result)
        
    except CalcError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- CLI Interface ---

def print_help():
    print("CALC-CLI - BODMAS Calculator")
    print("Usage:")
    print("  python calc.py \"expression\"   Evaluate the expression")
    print("  python calc.py                Start interactive mode")
    print("  python calc.py --help         Show this help message")
    print("\nSupported Operators:")
    print("  +, -, *, /, (, )")

def interactive_mode():
    print("CALC-CLI Interactive Mode (Type 'exit' or 'quit' to stop)")
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ('exit', 'quit'):
                break
            if not user_input.strip():
                continue
            print(calculate(user_input))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--help":
            print_help()
        else:
            # Join all args just in case user didn't quote the expression
            # e.g. calc.py 2 + 2
            expression = " ".join(sys.argv[1:])
            print(calculate(expression))
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
