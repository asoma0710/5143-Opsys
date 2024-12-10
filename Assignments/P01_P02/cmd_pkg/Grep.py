
import requests
import re
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg
from rich import print

grep_flags: set[str] = {
    "--help", "-c", "-i", "-v", "-l",
}

API_URL = "http://127.0.0.1:8000"  # Base URL for FastAPI

def grep(**kwargs) -> str:
    """
    NAME
        grep
        
    DESCRIPTION
        grep                    : prints out the lines in a virtual file that match a given pattern
            --help              : displays how to use the grep command
            -c                  : prints the number of lines in a file that match a given pattern
            -i                  : ignores upper and lower case when searching for a pattern
            -v                  : prints lines that do not match the pattern
            -l                  : prints only the names of files that contain at least one matching line
    
    EXAMPLE
        `grep python README.md' : prints out the lines in README.md that contain the word "python"
    """
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    params: list[str] = kwargs.get("params", [])
    result: str = ""

    # Check if invalid flags are present
    if not flags.issubset(grep_flags):
        return invalidFlagsMsg(grep, grep_flags, flags)
    
    # Handle --help flag
    if "--help" in flags:
        return grep.__doc__
    
    # Extract pattern and file(s)
    if len(params) < 2:
        return "grep: missing pattern and file\nTry 'grep --help' for more information."
    
    pattern = params[0]
    file_names = params[1:]
    
    ignore_case: bool = "-i" in flags
    count_only: bool = "-c" in flags
    invert_match: bool = "-v" in flags
    list_file: bool = "-l" in flags

    contents: list[str] = []
    count: int = 0

    for file_name in file_names:
        try:
            # Make API call to fetch file content from the virtual filesystem
            response = requests.get(f"{API_URL}/cat", params={"names": [file_name]})
            if response.status_code != 200:
                raise FileNotFoundError(f"Error: '{file_name}' not found in virtual filesystem.")

            # Get the file contents
            file_content = response.json().get("file_contents", "")
            lines = file_content.splitlines()

            for line_number, line in enumerate(lines, start=1):
                line = line.strip()
                match = False

                # Perform pattern matching
                if ignore_case:
                    if re.search(re.escape(pattern), line, re.IGNORECASE):
                        match = True
                elif pattern in line:
                    match = True

                if match and not invert_match:
                    if not list_file:
                        contents.append(f"{file_name}:{line_number}: {line}")
                    else:
                        contents.append(f"{file_name}")
                    count += 1
                elif not match and invert_match:
                    contents.append(f"{file_name}:{line_number}: {line}")

        except FileNotFoundError as e:
            result += f"Error: '{e.filename}' not found.\n"

    if count_only:
        return str(count)
    
    if list_file:
        return "\n".join(set(contents))  # Return unique file names
    
    return "\n".join(contents)


if __name__ == "__main__":
    # Example usage in the shell
    print(grep(params=["python", "README.md"]))
