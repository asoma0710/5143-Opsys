#!/usr/bin/env python3
import os
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

rmdir_flags:set[str] = {
    "--help"
}

def rmdir(**kwargs)-> str:
    """
    NAME
        rm 
    
    DESCRIPTION
        rmdir                     : deletes a directory
             --help               : Displays the help page for rmdir
    EXAMPLE
        `rmdir <directory name>'  : removes the directory from the current working directory


    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # Check if invalid flags are present
    if not flags.issubset(rmdir_flags):
        result = invalidFlagsMsg(rmdir, rmdir_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = rmdir.__doc__
    # If other valid flags or none
    else:
        contents:list[str] = []

        for param in params:
            line:str = ""

            # Replace tilde with user directory
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)
            
            try:
                os.rmdir(param)
            except(FileNotFoundError):
                line:str = f"{rmdir.__name__}: failed to remove directory '{param}': No such file or directory"
            except(NotADirectoryError):
                line:str = f"{rmdir.__name__}: failed to remove '{param}': Not a directory"
            except(OSError):
                line = f"{rmdir.__name__}: failed to remove directory '{param}': Permission denied"
            contents.append(line)
        result = "\n".join(contents)

    return result

if __name__ == "__main__":
    # s= rmdir(params=["hi.txt", "woo", "."])
    # print(s)
    print("Be careful when testing this. Is mostly safe though.")