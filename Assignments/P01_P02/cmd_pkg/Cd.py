import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

cd_flags: set[str] = {
    "--help"
}

def cd(**kwargs) -> str:
    """
    NAME
        cd 
        
    DESCRIPTION
        cd           : changes the current directory to the specified directory
            --help   : displays how to use the cd command
        
    EXAMPLE
        `cd <path>`  : moves into the specified directory path
        `cd ~`       : changes the current directory to the home directory
        `cd ..`      : moves the current directory back one directory
    """
    params: list[str] = kwargs.get("params", [])
    
    # If no param is passed, use the default "~"
    if not params:
        params.append("~")



    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    if not flags.issubset(cd_flags):
        result = invalidFlagsMsg(cd, cd_flags, flags)
    elif "--help" in flags:
        result = cd.__doc__
    else:
        if len(params) > 1:
            result = f"{cd.__name__}: too many arguments"
        else:
            path = params[0]
            
            try:
                # Make the API request to change the directory
                response = requests.post("http://127.0.0.1:8000/cd", json={"path": path})
                if response.status_code == 200:
                    result = response.json().get("message", "")
                else:
                    result = f"Error: {response.json().get('detail', 'Unknown error')}"
            except Exception as e:
                result = str(e)

    return result


if __name__ == "__main__":
    result = cd(params=["~/projects"], flags=[])
    print(result)
