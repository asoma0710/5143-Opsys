#!/usr/bin/env python3
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

exit_flags:set[str] = {
    "--help"
}

def exit(**kwargs)-> str:
    """
    NAME
        exit
        
    DESCRIPTION
        exit        : exits the shell
            --help  : displays how to use the exit command 
        
    EXAMPLE
        'exit'      : exits the shell
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(exit_flags):
        result = invalidFlagsMsg(exit, exit_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = exit.__doc__
    # If other valid flags or none
    else:
        # If more than 0 arguments
        if len(params):
            result = f"{exit.__name__}: too many arguments"
        # Terminate shell
        else:
            raise(SystemExit)

    # Returns empty string if normal usage.
    return result

if __name__ == "__main__":
    print(exit(flags=[], params=["hi"]))