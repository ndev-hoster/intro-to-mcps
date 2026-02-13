from mcp.server.fastmcp import FastMCP
import os
import subprocess

# instantiate an MCP server client
mcp = FastMCP("OS Interactions Server")
"""An mcp server made with tools to support OS interactions"""


@mcp.tool()
def list_cwd_contents()->str:
    """Lists the contents of the current working directory"""
    return str(subprocess.check_output(["ls"]), "utf-8")

@mcp.tool()
def sys_info()->str:
    """Returns system information from fastfetch"""
    return str(subprocess.check_output(["fastfetch"]), "utf-8")

@mcp.tool()
def read_file(filepath:str):
    """Reads a file based on the provided filepath"""
    with open(filepath, "r") as f:
        return f.read()


# execute and return the stdio output
if __name__ == "__main__":
    mcp.run(transport="STDIO")