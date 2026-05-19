from analyzer.parser import is_valid_python


def check_syntax(code):

    valid, error = is_valid_python(code)

    return {
        "valid": valid,
        "errors": [] if valid else [str(error)]
    }