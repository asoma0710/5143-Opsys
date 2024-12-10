#!/usr/bin/env python3

def tockenizeFlags(flagList:list[str])-> set[str]:
    """
    Splits compounded flags into single letter flags, and
    also removes repeated flags by returning as a list.
    """
    flags:set[str] = set()

    for flagStr in flagList:
        if flagStr.startswith("--"):
            flags.add(flagStr)
        else:
            for i in range(1, len(flagStr)):
                flags.add(f"-{flagStr[i]}")
    
    return flags

if __name__ == "__main__":
    f = ["-lah", "-l", "--help", "-a", "-h"]
    l = []
    print(tockenizeFlags(f))