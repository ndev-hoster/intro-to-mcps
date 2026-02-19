from mcp.server.fastmcp import FastMCP
import os
import subprocess
from typing import Optional

mcp = FastMCP("OS Interactions Server")
"""An mcp server made with tools to support OS interactions"""


@mcp.tool()
def get_structure(directory: Optional[str]=".")->str:
    """ Tree command to understand the directory structure 
        Args: 
        directory - str - the directory whose structure needs to be checked
    """
    return str(subprocess.check_output(["tree",directory,"-aL","3"], shell=True), "utf-8")

@mcp.tool()
def execute_and_log_command(rawcommand:str, logfile:str)->str:
    """ Function to log the output of a command to a given file 
    Args: 
        rawcommand - str - command that needs to be ran
        logfile: - str - path of the log file
    """
    command_list=rawcommand.split(" ")
    with open(logfile, "w") as log_file:
        subprocess.run(command_list, stdout=log_file, stderr=log_file)
    return f"Command {rawcommand} executed and logged to {logfile}"

@mcp.tool()
def run_test(command: str) -> str:
    """Execute a python command to test a python script
    and return output (auto-approved for testing)
    Args: command: str (command to run)
    """
    allowed_commands=["python"]
    if command.split(" ")[0] in allowed_commands:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.getcwd()
            )
            return f"Exit code: {result.returncode}\nOutput:\n{result.stdout}\nErrors:\n{result.stderr}"
        except Exception as e:
            return f"Execution failed: {str(e)}"



@mcp.tool()
def custom_command(command: str)->str:
    """Runs a custom command not available in the other tools"""
    return str(subprocess.check_output(command_list, shell=True), "utf-8")