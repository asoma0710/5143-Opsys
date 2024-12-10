#!/usr/bin/env python3
import os, sys
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

touch_flags: set[str] = {
    "--help"
}

def touch(**kwargs) -> str:
    """
    NAME
        touch
        
    DESCRIPTION
        touch               : create a new empty file in the current directory with any specified extension or none 
            --help          : displays how to use the touch command
        
    EXAMPLE
        `touch <file.txt>`  : creates a new empty text file 
        `touch <file.py>`   : creates a new empty python file 
        `touch ~/<file.txt>`: creates a new empty text file in the home directory
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(touch_flags):
        result = invalidFlagsMsg(touch, touch_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = touch.__doc__
    else:
        for param in params:
            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)
            
            try:
                # Make the API request to create the file
                response = requests.post("http://127.0.0.1:8000/touch", json={"name": param})
                if response.status_code == 200:
                    result = response.json().get("message", "")
                else:
                    result = f"Error: {response.json().get('detail', 'Unknown error')}"
            except Exception as e:
                result = str(e)

    return result

if __name__ == "__main__":
    s = touch(params=sys.argv[1:], flags=[])
    print(s)
