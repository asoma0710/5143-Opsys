import requests
import sys
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

head_flags: set[str] = {
    "--help"
}

def head(**kwargs):
    """   
    NAME
        head 

    DESCRIPTION
        head               : display the first 10 lines of a file in the virtual filesystem.         
            --help         : displays how to use the head command
            -n <number>    : displays the first n lines of a file
            
    EXAMPLES
        `head <file name>` : copy the first 10 lines of the file contents to standard output
    """
    params: list[str] = kwargs.get("params", [])
    flags: list[str] = kwargs.get("flags", [])
    result: str = ""
    num_display_lines: int = 10  # Default to 10 lines if -n is not provided
    # Parse the flags to check for the -n option
    if len(params)>1:
        num_display_lines=params[1]

    # Handle --help flag
    if "--help" in flags:
        return head.__doc__




    # Make sure params (file names) are provided
    if not params:
        return "tail: missing file operand\nTry 'tail --help' for more information."


    response = requests.post("http://127.0.0.1:8000/head", json={"file_name": params[0], "num_lines": num_display_lines})
    if response.status_code == 200:
        result += response.json().get("content", "") + "\n"
    else:
        result += f"Error: {response.json().get('detail', 'Unknown error')}\n"


    return result

