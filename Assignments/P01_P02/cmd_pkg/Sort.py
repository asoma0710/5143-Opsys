#!/usr/bin/env python3
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

sort_flags:set[str] = {
    "--help"
}

API_URL = "http://127.0.0.1:8000"  # Replace with your actual FastAPI URL

def sort(**kwargs) -> str:
    """
    NAME
        sort
        
    DESCRIPTION
        sort             : used to sort a file, arranging the records in a particular order
            --help       : displays how to use the sort command
        
    EXAMPLE 
        `sort <file>'   : sorts the specified file
        `sort  --help`  : displays how to use the sort command
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    stdin: bool = kwargs.get("stdin", True)
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(sort_flags):
        result = invalidFlagsMsg(sort, sort_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = sort.__doc__
    # If valid flags, and expect data from stdin (from file or pipe)
    else:
        contents: list[str] = []

        for param in params:
            try:
                # Make API call to fetch the file content from the virtual filesystem
                response = requests.get(f"{API_URL}/cat", params={"names": [param]})
                
                if response.status_code != 200:
                    raise FileNotFoundError(f"Error: '{param}' not found in virtual filesystem.")

                # Get the file content from the virtual filesystem
                file_content = response.json().get("file_contents", "")
                text = file_content.splitlines()
                
                # Sort the lines of the file
                text.sort()

                contents.append('\n'.join(text))

            except FileNotFoundError as e:
                return f"{sort.__name__}: cannot access '{param}': No such file or directory"

        # Join the sorted content
        result = '\n'.join(contents)
        
    return result

if __name__ == "__main__":
    print(sort(params=["README.md"], flags=[], stdin=True))
