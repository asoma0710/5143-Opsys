#!/usr/bin/env python3
from types import FunctionType

def invalidFlagsMsg(func:FunctionType, validFlags:set[str], flags:set[str])-> str:
    """
    Creates an error message for a linux command
    when invalid flags are used.
    """
    invalidFlags:set[str] = flags.difference(validFlags)

    invalidFlagsStr:str = ', '.join(f'"{flag}"' for flag in invalidFlags)

    result = f"{func.__name__}: invalid option(s) -- {invalidFlagsStr}\nTry '{func.__name__} --help for more information."
    return result
