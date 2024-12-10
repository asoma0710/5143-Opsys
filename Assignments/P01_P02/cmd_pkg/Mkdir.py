#!/usr/bin/env python3
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

mkdir_flags: set[str] = {
    "--help"
}

def mkdir(**kwargs) -> str:
    """
    NAME
        mkdir
        
    DESCRIPTION
        mkdir       : makes a new directory in the current directory using the API
            --help  : displays how to use the mkdir command
        
    EXAMPLE
        `mkdir <name of directory>` 
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = set(kwargs.get("flags", []))  # Convert flags to set
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(mkdir_flags):
        result = invalidFlagsMsg(mkdir, mkdir_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = mkdir.__doc__
    else:
        for param in params:
            try:
                # Send the path directly to the API
                response = requests.post("http://127.0.0.1:8000/mkdir", json={"path": param})
                
                if response.status_code == 200:
                    result += response.json().get("message", "") + "\n"
                else:
                    result += f"Error: {response.json().get('detail', 'Unknown error')}\n"
            except Exception as e:
                result += str(e) + "\n"

    return result

if __name__ == "__main__":
    s = mkdir(params=["Desktop/Hello"], flags=[])
    print(s)
