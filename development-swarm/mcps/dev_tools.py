from pathlib import Path
import functools
import file_tools
import run_tools
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dev-tools server")
"""Server with tools that can be accessed by the developer agent"""

PROJECT_ROOT = Path(__file__).parent.parent
DEV_SPACE = PROJECT_ROOT / "dev-space"

def check_correct_ws(path: str) -> bool:
    return Path(path).resolve().is_relative_to(DEV_SPACE.resolve())

def require_dev_space(func):
    @functools.wraps(func)
    def wrapper(path: str = ".", *args, **kwargs):
        if not check_correct_ws(path):
            return f"Access denied: '{path}' is outside dev-space/"
        return func(path, *args, **kwargs)
    return wrapper

def require_dev_space_kwarg(argname: str):
    """For functions where the path argument isn't the first positional arg"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            path = kwargs.get(argname) or (args[0] if args else None)
            if not path or not check_correct_ws(path):
                return f"Access denied: '{path}' is outside dev-space/"
            return func(*args, **kwargs)
        return wrapper
    return decorator


#### GUARDED TOOLS #######
mcp.tool()(require_dev_space(file_tools.list_cwd_contents))
mcp.tool()(require_dev_space(file_tools.mkdir))
mcp.tool()(require_dev_space(file_tools.read_file))
mcp.tool()(require_dev_space(file_tools.write_file))
mcp.tool()(require_dev_space(run_tools.get_structure))

@mcp.tool()
def execute_and_log_command(rawcommand: str, logfile: str) -> str:
    """Runs a command and logs output, logfile must be inside dev-space/
       Args: rawcommand: str (command to run), logfile: str (path of log file)
    """
    if not check_correct_ws(logfile):
        return f"Access denied: '{logfile}' is outside dev-space/"
    return run_tools.execute_and_log_command(rawcommand, logfile)

#### GUARDED TOOLS END #######
mcp.tool()(file_tools.sys_info)
mcp.tool()(run_tools.custom_command)

if __name__ == "__main__":
    mcp.run(transport="stdio")