#!/usr/bin/env python3
import psutil
from datetime import datetime
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

who_flags:set[str] = {
    "--help"
}

def who(**kwargs)-> str:
    """
    NAME
        who 
        
    DESCRIPTION
        who             : prints out a list of users currently logged in
            --help      : displays how to use the who command
            -a          : displays all users currently logged in
        
    EXAMPLE
        `who'
        `who   --help`  : displays how to use the who command
        `who   -a`      : displays all users currently logged in
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(who_flags):
        result = invalidFlagsMsg(who, who_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = who.__doc__
    # If other valid flags or none
    else:
        contents:list[str] = []

        # Get list of users logged in
        users:list = psutil.users()

        for user in users:
            date:str = datetime.fromtimestamp(user.started).isoformat(sep=' ', timespec="minutes")
            contents.append(f"{user.name}\t{user.terminal}\t\t{date}")
        
        result = '\n'.join(contents)
        
    return result

if __name__ == "__main__":
    print(who())