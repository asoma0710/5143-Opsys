#!/usr/bin/env python3
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

CLEAR = "\033c"

clear_flags:set[str] = {
    "--help"
}

def clear(**kwargs)-> str:
    """
    NAME
       clear 
       
    DESCRIPTION
       clear        : clears the terminal screen
            --help  : displays how to use the clear command
            
    EXAMPLE
        `clear`     : clears the terminal screen
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(clear_flags):
        result = invalidFlagsMsg(clear, clear_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = clear.__doc__
    # If other valid flags or none
    else:
        result = CLEAR

    return result

if __name__ == "__main__":
    print(clear_flags(flags=[], params=["hi"]))