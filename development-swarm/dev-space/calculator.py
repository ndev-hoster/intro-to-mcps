
import sys

def main():
    """
    Main function for the CLI expression evaluator.
    Handles argument parsing, input validation, and orchestrates
    the evaluation process.
    """
    if len(sys.argv) < 2:
        print("Usage: calc \"<expression>\"", file=sys.stderr)
        sys.exit(1)

    expression = sys.argv[1]
    
    # Task 1.3: Sanitization - Remove all whitespace
    sanitized_expression = expression.replace(" ", "")

    print(f"Sanitized Expression: {sanitized_expression}") # For debugging, will remove later

    # Placeholder for further phases
    # tokens = tokenize(sanitized_expression)
    # rpn_tokens = shunting_yard(tokens)
    # result = evaluate_rpn(rpn_tokens)
    # print(format_result(result))

if __name__ == "__main__":
    main()
