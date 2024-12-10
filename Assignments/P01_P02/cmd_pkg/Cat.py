#!/usr/bin/env python3
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg
import requests

cat_flags:set[str] = {
    "--help"
}

API_URL = "http://127.0.0.1:8000"  # Replace with your actual FastAPI base URL

def cat(**kwargs):
    """   
    NAME
        cat 

    DESCRIPTION
        cat                 : concatenate FILE(s) to standard output
            --help          : displays how to use the cat command
            
    EXAMPLES
        `cat <file name>`   : copy file contents to standard output
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""
    
    # Check if invalid flags are present
    if not flags.issubset(cat_flags):
        result = invalidFlagsMsg(cat, cat_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = cat.__doc__
    else:
        try:
            # Call the API to get the file contents
            result = _call_cat_api(params)
        except Exception as e:
            result = str(e)

    return result

def _call_cat_api(file_names: list[str]):
    """Helper function to call the FastAPI cat endpoint to get file contents."""
    response = requests.get(f"{API_URL}/cat", params={"names": file_names})
    
    if response.status_code == 200:
        data = response.json()
        return data.get("file_contents", "")
    else:
        raise Exception(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
