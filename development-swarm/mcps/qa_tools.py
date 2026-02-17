from run_tools import *
from file_tools import *
import functools

def check_correct_ws(path: str) -> bool:
    abs_path = os.path.realpath(path)
    qa_space = os.path.realpath("qa-space")
    dev_space = os.path.realpath("dev-space")
    return abs_path.startswith(qa_space) or abs_path.startswith(dev_space)

def require_qa_space(func):
    @functools.wraps(func)  # preserves original function name/docstring for MCP
    def wrapper(path: str = ".", *args, **kwargs):
        if not check_correct_ws(path):
            return f"Access denied: '{path}' is outside qa/dev space"
        return func(path, *args, **kwargs)
    return wrapper

import file_tools

file_tools.list_cwd_contents = require_qa_space(file_tools.list_cwd_contents)
file_tools.read_file = require_qa_space(file_tools.read_file)
file_tools.write_file = require_qa_space(file_tools.write_file)
