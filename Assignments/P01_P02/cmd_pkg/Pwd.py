#!/usr/bin/env python3
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

# Define valid flags for the pwd command
pwd_flags: set[str] = {
    "--help"
}

# Base URL for FastAPI API
API_URL = "http://127.0.0.1:8000/pwd"

def call_pwd_api() -> str:
    """
    Makes a GET request to the FastAPI /pwd endpoint to get the current working directory.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            # Get the current directory from the API response
            return response.json().get("current_directory", "")
        else:
            return f"Error: Unable to fetch the current directory (Status Code: {response.status_code})"
    except Exception as e:
        return f"Error: Failed to connect to the API. Details: {e}"

def pwd(**kwargs) -> str:
    """
    NAME
        pwd
    
    DESCRIPTION
        pwd             : prints the current working directory
            --help      : displays how to use the pwd command
   
    EXAMPLE
        `pwd'           : prints the current working directory
        `pwd --help'    : displays how to use the pwd command
    """
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))  # Tokenize flags
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(pwd_flags):
        result = invalidFlagsMsg(pwd, pwd_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = pwd.__doc__
    # Use the FastAPI to get the current directory
    else:
        result = call_pwd_api()  # Call the API to get the current working directory
    
    return result

if __name__ == "__main__":
    # Test case 1: Run pwd with invalid and valid flags
    f = ["--help", "--help", "-a", "-b"]
    print(f"Running 'pwd' with the flags: {f}")
    s = pwd(flags=f)
    print(s)

    # Test case 2: Run pwd with no flags
    print(f"\nRunning 'pwd' with no flags")
    s = pwd()
    print(s)

    # Test case 3: Run pwd with the help flag
    f = ["--help"]
    print(f"\nRunning pwd with the flags: {f}")
    s = pwd(flags=f)
    print(s)
