#!/usr/bin/env python3
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

chmod_flags: set[str] = {
    "--help",
}

def chmod(**kwargs) -> str:
    """
    NAME
        chmod
    
    DESCRIPTION
        all files/directories have specific permissions that determine who can read, write, and execute 

        owner | group | others
        ----------------------
        drwx  | rwx   | rwx
        ----------------------
        
        d = directory
        r = read
        w = write
        x = execute
    
        chmod              : changes permissions for a file/directory
             --help        : Displays the help page for chmod
             7             : rwx | 111 |
             6             : rw- | 110 |
             5             : r-x | 101 |
             4             : r-- | 100 |
             3             : -wx | 011 |
             2             : -w- | 010 |
             1             : --x | 001 |
             0             : --- | 000 | 

    EXAMPLE
        `chmod 777 <file>` : file is now readable, writable, and executable for everyone
        `chmod 644 <file>` : file is now readable and writable for the owner, and readable for everyone else
        `chmod 755 <file>` : file is now readable, writable, and executable for the owner, and readable and executable for everyone else
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(chmod_flags):
        result = invalidFlagsMsg(chmod, chmod_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = "".join(chmod.__doc__)
    else:
        if len(params) != 2:
            return "Usage: chmod <permissions> <path>"

        permissions = params[0]
        path = params[1]

        # Prepare the API request to change permissions
        response = requests.put(f"http://127.0.0.1:8000/chmod", json={"permissions": permissions, "path": path})

        if response.status_code == 200:
            result = response.json().get("detail", "")
        else:
            result = f"Error: {response.json().get('detail', 'Unknown error')}"

    return result

if __name__ == "__main__":
    # Example usage of the chmod command
    result = chmod(params=["755", "somefile.txt"])
    print(result)
