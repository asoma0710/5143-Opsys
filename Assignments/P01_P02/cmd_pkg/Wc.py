#!/usr/bin/env python3
import os
import requests
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

wc_flags: set[str] = {
    "--help",
    "-l",
    "-m",
    "-w"
}

def wc(**kwargs) -> str:
    """
    NAME
        wc 
        
    DESCRIPTION
        wc                  : prints out the number of lines, words, and bytes in a file
            -l              : prints the number of lines in a file
            -m              : prints the number of bytes in a file
            -w              : prints the number of words in a file
            --help          : displays how to use the wc command
        
    EXAMPLE
        `wc README.md'      : prints out the number of lines, words, and bytes in README.md
        `wc -l README.md'   : prints out the number of lines in README.md
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = ""

    # Handle the --help flag
    if "--help" in flags:
        return wc.__doc__

    # Default behavior (lines, words, bytes) when no specific flag is provided
    if not flags:
        flags = {"-l", "-m", "-w"}  # Show lines, words, and bytes if no flags

    # Check for invalid flags
    if not flags.issubset(wc_flags):
        result = invalidFlagsMsg(wc, wc_flags, flags)
    else:
        # Initialize counts
        showLines = "-l" in flags
        showChars = "-m" in flags
        showWords = "-w" in flags

        contents: list[str] = []

        for param in params:
            if param.startswith("~"):
                param = param.replace("~", os.path.expanduser("~"), 1)

            # API request to get the content of the file
            response = requests.get(f"http://127.0.0.1:8000/cat", params={"names": [param]})

            if response.status_code == 200:
                file_data = response.json().get("file_contents", "")
                byte_count = len(file_data.encode('utf-8'))
                lines = file_data.splitlines(True)
                line_count = len(lines)
                word_count = sum(len(line.split()) for line in lines)

                wc_counts = []
                if showLines:
                    wc_counts.append(str(line_count))
                if showWords:
                    wc_counts.append(str(word_count))
                if showChars:
                    wc_counts.append(str(byte_count))
                wc_counts.append(param)  # Append the file name

                contents.append('\t'.join(wc_counts))
            else:
                contents.append(f"{wc.__name__}: cannot access '{param}': No such file or directory")

        result = '\n'.join(contents)

    return result

if __name__ == "__main__":
    print(wc(params=["README.md"], flags=["-m"]))  # Example usage
