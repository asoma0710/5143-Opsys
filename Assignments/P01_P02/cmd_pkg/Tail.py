import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

tail_flags: set[str] = {"--help", "-n"}

def tail(**kwargs):
    """   
    NAME
        tail 

    DESCRIPTION
        tail                : display the last N lines of a file in the virtual filesystem.
            --help          : displays how to use the tail command
            -n <number>     : displays the last <number> lines of a file
            
    EXAMPLES
        `tail <file name>`   : display the last 10 lines of the file contents to standard output (default behavior)
        `tail -n 10 <file>`  : display the last 10 lines of the file contents
    """
    params: list[str] = kwargs.get("params", [])
    flags: list[str] = kwargs.get("flags", [])
    result: str = ""
    num_display_lines: int = 10  # Default to 10 lines if -n is not provided
    # Parse the flags to check for the -n option
    if len(params)>1:
        num_display_lines=params[1]

    # Check for --help flag
    if "--help" in flags:
        return tail.__doc__

    # Make sure params (file names) are provided
    if not params:
        return "tail: missing file operand\nTry 'tail --help' for more information."


    response = requests.post("http://127.0.0.1:8000/tail", json={"file_name": params[0], "num_lines": num_display_lines})
    if response.status_code == 200:
        result += response.json().get("content", "") + "\n"
    else:
        result += f"Error: {response.json().get('detail', 'Unknown error')}\n"


    return result
