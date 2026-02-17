from mcp.server.fastmcp import FastMCP
import os
import subprocess

mcp = FastMCP("OS Interactions Server")
"""An mcp server made with tools to support OS interactions"""


@mcp.tool()
def custom_command(command: str)->str:
    """Runs a custom command not available in the tools above"""
    allow_exec=input(f"Allow the tool to execute {command} (y/n):").lower()
    if allow_exec == "y":
        command_list=command.split(" ")
        return str(subprocess.check_output(command_list, shell=True), "utf-8")
    else:
        return "Command not executed"