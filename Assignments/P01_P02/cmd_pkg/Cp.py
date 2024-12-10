#!/usr/bin/env python3
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

cp_flags: set[str] = {
    "--help",
    "-r"
}

API_URL = "http://127.0.0.1:8000/cp"  # Base URL for FastAPI `/cp` endpoint

def cp(**kwargs) -> str:
    """
    NAME
        cp
        
    DESCRIPTION
        cp          : copies a file or directory to a new location
            --help  : displays how to use the cp command
            -r      : recursively copy a directory and its contents
        
    EXAMPLE
        `cp <file/directory to copy> <path to destination>'
        `cp -r <directory to copy> <path to destination>'
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(cp_flags):
        result = invalidFlagsMsg(cp, cp_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = cp.__doc__
    else:
        if len(params) == 2:
            try:
                # Check if the recursive flag is set for directories
                is_directory = "-r" in flags

                # Make an API request to copy the file or directory
                payload = {
                    "source": params[0],
                    "destination": params[1],
                    "is_directory": is_directory
                }

                # Perform the API request
                response = requests.post(API_URL, json=payload)
                
                if response.status_code != 200:
                    return f"Error during copy: {response.json().get('detail', 'Unknown error')}"
                
                result = response.json().get("message", "Copy operation completed.")

            except Exception as e:
                result = f"Error during copy: {str(e)}"
        else:
            result = f"{cp.__name__}: missing file operand(s)"
            
    return result

if __name__ == "__main__":
    print(cp(params=["source_directory", "destination_directory"], flags=["-r"]))  # Example usage with the -r flag
