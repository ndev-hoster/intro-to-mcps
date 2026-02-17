from mcp.server.fastmcp import FastMCP
import os
import subprocess

mcp = FastMCP("OS Interactions Server")
"""An mcp server made with tools to support OS interactions"""


@mcp.tool()
def get_structure(directory)->str:
    """ Tree command to understand the directory structure 
        Args: 
        directory - str - the directory whose structure needs to be checked
    """
    return str(subprocess.check_output(["tree",directory,"-aL","3"], shell=True), "utf-8")

@mcp.tool()
def execute_and_log_command(rawcommand:str, logfile:str):
    """ Function to log the output of a command to a given file 
    Args: 
        rawcommand - str - command that needs to be ran
        logfile: - str - path of the log file
    """
    command_list=rawcommand.split(" ")
    with open(logfile, "w") as log_file:
        subprocess.run(command_list, stdout=log_file, stderr=log_file)

@mcp.tool()
def custom_command(command: str)->str:
    """Runs a custom command not available in the other tools"""
    allow_exec=input(f"Allow the execution of {command}? [y/n]:").lower()
    if allow_exec == "y":
        command_list=command.split(" ")
        return str(subprocess.check_output(command_list, shell=True), "utf-8")
    else:
        return "Command not executed"