import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

mv_flags: set[str] = {
    "--help", "-r"
}

def mv(**kwargs) -> str:
    """
    NAME
        mv
        
    DESCRIPTION
        mv            : moves a file or directory
            -r        : specifies that the source is a directory (recursive move)
            --help    : displays how to use the mv command
        
    EXAMPLE
       `mv <source> <destination>` 
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(mv_flags):
        result = invalidFlagsMsg(mv, mv_flags, flags)
    elif "--help" in flags:
        result = mv.__doc__
    else:
        if len(params) == 2:
            source = params[0]
            destination = params[1]
            is_directory = "-r" in flags  # Check if the -r flag is set
            
            try:
                # Make API request to FastAPI mv endpoint
                response = requests.post("http://127.0.0.1:8000/mv", json={
                    "source": source,
                    "destination": destination,
                    "isdirectory": is_directory
                })
                
                if response.status_code == 200:
                    result = response.json().get("message", "")
                else:
                    result = f"Error: {response.json().get('detail', 'Unknown error')}"
            except Exception as e:
                result = f"Error: {str(e)}"
        else:
            result = f"{mv.__name__}: missing file operand(s)"
    
    return result
