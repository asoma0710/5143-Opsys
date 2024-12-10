#!/usr/bin/env python3
import os
import requests
from glob import glob
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

RESET = "\033[0m"      # Reset text formatting and color
BOLD = "\033[1m"       # Bold text
DARK_GREEN = "\033[32m"     # Green text
BLUE = "\033[94m"      # Blue text
RED = "\033[91m"       # Red text

API_URL = "http://127.0.0.1:8000/rm"  # FastAPI endpoint for the rm command

rm_flags: set[str] = {
    "-r",    # Recursively remove directories and their contents
    "--help" # Show help
}

def rm(**kwargs) -> str:
    """
    NAME
        rm 
        
    DESCRIPTION
        rm                          : removes a file or directory
            -r                      : recursively removes all contents of a file/directory
            --help                  : displays how to use the rm command
            
    EXAMPLE
        `rm <filename>'             : removes a file
        `rm --help'                 : displays how to use the rm command
        `rm -r <directory name>'    : removes a directory and its contents
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check for invalid flags
    if not flags.issubset(rm_flags):
        return invalidFlagsMsg(rm, rm_flags, flags)
    
    # Handle --help flag
    if "--help" in flags:
        return rm.__doc__

    # Set recursive flag
    recursive = "-r" in flags

    for param in params:
        # Replace tilde with user directory
        if param.startswith("~"):
            param = param.replace("~", os.path.expanduser("~"), 1)

        try:
            # Make an API request to the FastAPI /rm endpoint
            response = requests.delete(API_URL, params={"path": param, "-r": recursive})

            # Handle the response from the API
            if response.status_code == 200:
                result += f"{BLUE}{response.json().get('message')}{RESET}\n"
            else:
                result += f"{RED}rm: {param}: {response.json().get('detail', 'Error occurred')}{RESET}\n"
        except Exception as e:
            result += f"{RED}Error: Failed to connect to the API. Details: {str(e)}{RESET}\n"

    return result.strip()

if __name__ == "__main__":
    # Example usage for testing
    print(rm(params=["testfile.txt", "mydir"], flags=["-r"]))
 