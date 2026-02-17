from mcp.server.fastmcp import FastMCP
import json
import requests
from datetime import datetime as dt
from datetime import date
from typing import Optional
import logging

# instantiate an MCP server client
mcp = FastMCP("API Endpoint response retreiver")
"""An mcp server made with tools to support API interactions"""

base_url="https://jsonplaceholder.typicode.com"


def get_posts(postid: int=None)->str:
    """ helper function to get Posts from jsonplaceholder """
    if postid is None:
        url = f"{base_url}/posts"
    else:
        url = f"{base_url}/posts/{postid}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return json.dumps(data, indent=4)

    else:
        return f"Encountered error while accessing API: {response.status_code}"


def get_users(userId:Optional[int]=None)->str:
    """ helper function to get Posts from jsonplaceholder """
    
    if userId is None:
        url = f"{base_url}/users"
    else:
        url = f"{base_url}/users/{userId}"
    logging.info("GET "+url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return json.dumps(data, indent=4)

    else:
        return f"Encountered error while accessing API: {response.status_code}"


@mcp.tool()
def show_posts(postid: Optional[int]=None):
    """ Function to get posts from the API
    Args: postid - Optional post ID. If not provided, returns all posts
    """
    raw_response = get_posts(postid)
    try:
        data = json.loads(raw_response)
        if isinstance(data, list):
            result = f"Found {len(data)} posts:\n\n"
            for post in data[:10]:
                result += f"Post {post['id']} by User {post['userId']}: {post['title']}\n"
            if len(data) > 10:
                result += f"\n... and {len(data) - 10} more posts"
            return result
        else:
            return f"Posted by {data['userId']} on {date.today()}: {data['title']}\n{data['body']}"
            
    except Exception as e:
        return f"Error processing API response: {raw_response}.  Details: {e}"

@mcp.tool()
def show_users(userId: Optional[int]=None):
    """ Function to get raw response from API and parse it
    Args: None
    """
    raw_response=get_users(userId)
    try:
        data = json.loads(raw_response)
        return data
    except Exception as e:
        return f"Error processing API response: {raw_response}.  Details: {e}"




# execute and return the stdio output
if __name__ == "__main__":
    mcp.run(transport="stdio")