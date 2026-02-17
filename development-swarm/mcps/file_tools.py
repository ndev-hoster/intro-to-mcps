from mcp.server.fastmcp import FastMCP
import os
import subprocess
from run_tools import custom_command

# instantiate an MCP server client
mcp = FastMCP("File Interactions Server")
"""An mcp server made with tools to support File interactions"""


@mcp.tool()
def list_cwd_contents(path: Otional[str] = ".")->str:
    """Lists the contents of the current working directory
        Args: path: str (path of the directory whose contents  need to be listed)
    """

    return str(subprocess.check_output(["ls",path,"-lar"]), "utf-8")

@mcp.tool()
def sys_info()->str:
    """Returns system information from fastfetch"""
    return str(subprocess.check_output(["fastfetch"]), "utf-8")

@mcp.tool()
def mkdir(directory:str):
    """Creates a directory based on the provided path
        Args: directory: str (path of the directory you want to create)
    """
    os.mkdir(directory)


@mcp.tool()
def read_file(filepath:str):
    """Reads a file based on the provided filepath
        Args: filepath: str (path of the file you want to read)
    """
    with open(filepath, "r") as f:
        return f.read()

@mcp.tool()
def write_file(filepath:str, content:str):
    """Writes a file based on the provided filepath and content
    Args: filepath: str (path you want to write into), content: str (what you want to write)
    """
    with open(filepath, "w") as f:
        f.write(content)



# execute and return the stdio output
if __name__ == "__main__":
    mcp.run(transport="STDIO")