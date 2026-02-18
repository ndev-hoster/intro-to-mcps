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

# @mcp.tool()
# def run_python_script(path:str, inputs: Optional[str]=None)->str:
#     """ Function to execute the python script for the given path
#     Args: 
#         path - str - path of the python script
#         input - str - a string to be passed as an arg to the script if required
#     """
#     command_list=["python", path]
#     if inputs:
#         command_list.append(inputs)
#     try:
#         subprocess.run(command_list, shell=True, check=True, capture_output=True, text=True)
#         return f"Ran the python script {path} {inputs} successfully"
#     except subprocess.CalledProcessError as e:
#         error_message = f"Error running script {path}: {e.stderr}"
#         return error_message



@mcp.tool()
def custom_command(command: str)->str:
    """Runs a custom command not available in the other tools"""
    allow_exec=input(f"Allow the execution of {command}? [y/n]:").lower()
    if allow_exec == "y":
        command_list=command.split(" ")
        return str(subprocess.check_output(command_list, shell=True), "utf-8")
    else:
        return "Command not executed"