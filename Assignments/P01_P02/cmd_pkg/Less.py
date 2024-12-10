import requests
import sys
from .TockenizeFlags import tockenizeFlags
from .InvalidFlagsMsg import invalidFlagsMsg

CLEAR = "\033c"

less_flags: set[str] = {"--help"}

def less(**kwargs):
    """
    NAME
        less
    
    DESCRIPTION
        less               : display the contents of a file in the virtual filesystem one page at a time
            --help         : displays how to use the less command
            
    EXAMPLES
        `less <file name>` : copy the contents of the file to standard output
    """
    params: list[str] = kwargs.get("params", [])
    flags: set[str] = tockenizeFlags(kwargs.get("flags", []))
    result: str = CLEAR

    # Check if invalid flags are present
    if not flags.issubset(less_flags):
        return invalidFlagsMsg(less, less_flags, flags)

    # Provide help info if --help flag present
    if "--help" in flags:
        return less.__doc__

    # Ensure a file parameter is provided
    if len(params) == 0:
        return "less: missing file operand\nTry 'less --help' for more information."

    # Prepare file names for query parameter
    file_query = "&".join([f"names={param}" for param in params])

    # Make an API request to the /cat endpoint
    try:
        response = requests.get(f"http://127.0.0.1:8000/cat?{file_query}")
        
        if response.status_code == 200:
            file_content = response.json().get("file_contents", "")
            lines = file_content.splitlines()  # Split content into individual lines
            num_lines = len(lines)
            current_line = 0
            lines_per_page = 10  # Number of lines to display per page

            while True:
                print(CLEAR)
                for i in range(current_line, current_line + lines_per_page):
                    if i < num_lines:
                        print(lines[i].rstrip())

                # Display pagination instructions
                print("\n-- Press 'q' to quit, 'f' for next page, 'b' for previous page --")

                user_input = input()

                if user_input == 'q':
                    break
                elif user_input == 'f':
                    current_line += lines_per_page
                    if current_line >= num_lines:
                        current_line = num_lines - lines_per_page
                        if current_line < 0:
                            current_line = 0
                elif user_input == 'b':
                    current_line -= lines_per_page
                    if current_line < 0:
                        current_line = 0
        else:
            result = f"Error: {response.json().get('detail', 'Unknown error')}"

    except Exception as e:
        result = f"Error: {str(e)}"

    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python less.py <filename>")
        sys.exit(1)

    less_output = less(params=[sys.argv[1]])
    print(less_output)
