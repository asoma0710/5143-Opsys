#!/usr/bin/env python3
import requests
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

RESET = "\033[0m"      # Reset text formatting and color
BOLD = "\033[1m"       # Bold text
DARK_GREEN = "\033[32m"     # Green text
BLUE = "\033[94m"      # Blue text
RED = "\033[91m"       # Red text

API_URL = "http://127.0.0.1:8000/ls"  # Base URL for FastAPI `/ls` endpoint

ls_flags:set[str] = {
    "-l",    
    "-a",
    "-h",
    "--help",
}

def format_bytes(num_bytes: float) -> str:
    """Converts bytes into a human-readable format."""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while num_bytes > power:
        num_bytes /= power
        n += 1
    return f"{num_bytes:.1f}{power_labels[n]}" if n > 0 else f"{num_bytes:.0f}"

def ls(**kwargs) -> str:
    """
    NAME
        ls 
        
    DESCRIPTION
        ls          : lists the contents of a directory
            --help  : displays how to use the ls command
            -l      : lists the contents of a directory in long format
            -a      : lists the contents of a directory including hidden files
            -h      : lists the contents of a directory in human readable format
    
    EXAMPLE
        `ls'        : lists the contents of a directory in short format
        `ls -l'     : lists the contents of a directory in long format
        `ls -lah`   : lists the contents of a directory in long format including hidden files in human readable format
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # If no params, default to current working directory
    if not params:
        params.append(os.getcwd())

    # Check if invalid flags are present
    if not flags.issubset(ls_flags):
        result = invalidFlagsMsg(ls, ls_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = ls.__doc__
    else:
        try:
            # Prepare query parameters for the API request
            query_params = {
                "-a": "-a" in flags,
                "-l": "-l" in flags,
                "-h": "-h" in flags
            }

            # Make an API request to the FastAPI /ls endpoint
            response = requests.get(API_URL, params=query_params)
            
            if response.status_code != 200:
                return f"Error: Unable to fetch directory contents (Status Code: {response.status_code})"

            # Extract the result from the API response
            result = response.json().get("files_and_dirs", "")

        except Exception as e:
            return f"Error: Failed to connect to the API. Details: {e}"

    return result

if __name__ == "__main__":
    # Example usage
    print(ls(flags=["-lah"], params=["~/"]))
