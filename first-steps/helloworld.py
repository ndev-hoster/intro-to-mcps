from mcp.server.fastmcp import FastMCP
import os
import subprocess

# instantiate an MCP server client
mcp = FastMCP("Echo world")

@mcp.tool()
def echo(text:str)->str:
    words=text.split(" ")
    return text

@mcp.tool()
def hello()->str:
    return "hello world!!"


# execute and return the stdio output
if __name__ == "__main__":
    mcp.run(transport="STDIO")