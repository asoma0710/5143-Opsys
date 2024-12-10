#!/usr/bin/env python3
import os, sys, socket, getpass, shutil
from time import sleep
import cmd_pkg
from getch import Getch
from ParseCommand import parseCommand
from ParseCommand import ShellCommand
from cmd_pkg.TockenizeFlags import tockenizeFlags
from cmd_pkg.InvalidFlagsMsg import invalidFlagsMsg

from filesystem import FileSystem

# Instantiate the Filesystem
fs = FileSystem()

RESET = "\033[0m"      # Reset text formatting and color
BOLD = "\033[1m"       # Bold text
GREEN = "\033[92m"     # Green text
YELLOW = "\033[93m"    # Yellow text
CYAN = "\033[36m"      # Blue text
PURPLE = "\033[35m"    # Purple text

history_flags:set[str] = {
    "--help",
    "-c"
}

def history(historyList:list[str], **kwargs)->str:
    """
    NAME
        history
        
    DESCRIPTION
        history             : prints out the history of commands that have been entered by the user
            --help          : displays how to use the history command
            -c              : clears the history of commands entered by the user
            
    EXAMPLE
        `history`           : prints the all commands entered by the user
        `history   10`      : prints the first 10 commands entered by the user
        `history   --help`  : displays how to use the history command
        `history   -c`      : clears the history of commands entered by the user
    """
    params:list[str] = kwargs.get("params", [])
    flags:set[str] = tockenizeFlags(kwargs.get("flags", []))
    result:str = ""

    # If no params, default to display full history
    if not params:
        params.append(len(historyList))

    # Check if invalid flags are present
    if not flags.issubset(history_flags):
        result = invalidFlagsMsg(history, history_flags, flags)
    # Provide help info if --help flag present
    elif "--help" in flags:
        result = history.__doc__
    elif "-c" in flags:
        historyList.clear()
    else:
         # If more than 1 argument
        if len(params) > 1:
            result = f"{history.__name__}: too many arguments"
        else:
            contents:list[str] = []
            
            try:
                numLines:int = int(params[0])
                for index in range(0, numLines):
                    contents.append(f"\t{index+1} {historyList[index]}")
                result = "\n".join(contents)
            # If param is not positive integer, result is error message
            except(ValueError):
                result = f"{history.__name__}: {params[0]}: invalid option"
                
    return result

def prompt()->str:
    """
    Returns a linux-like prompt.
    """
    username = PURPLE + BOLD + getpass.getuser() + RESET

    return f"{username}:%: {RESET}"

def print_cmd(commandStr:str)->str:
    """ This function "cleans" off the command line, then prints
        whatever cmd that is passed to it to the bottom of the terminal.
    """
    terminal_width = shutil.get_terminal_size().columns
    padding = " " * terminal_width
    sys.stdout.write("\r"+padding)
    sys.stdout.write("\r"+prompt()+commandStr)
    sys.stdout.flush()

historyFileName:str = ".myHistory"

# Store history here
historyList:list[str] = []
# Current index of history
movingIndex:int = 0

# Open and read history file, if it exists
if os.path.isfile(historyFileName):
    with open(historyFileName, "r") as historyFile:
        historyList = historyFile.read().splitlines()
    if historyList:
        movingIndex = len(historyList)

getch:Getch = Getch()  # create instance of our getch class

if __name__ == '__main__':
    commandStr = ""  # empty commandStr variable

    while True:  # loop forever
        print_cmd(commandStr)  # print the commandStr (with our prompt)
        char = getch()  # read a character (but don't print)

        if char == '\x03':  # ctrl-c
            with open(historyFileName, "w") as historyFile:
                historyFile.write('\n'.join(historyList))
            print_cmd(f"{commandStr}\n")
            cmd_pkg.exit()

        elif char == '\x7f':  # back space pressed
            commandStr = commandStr[:-1]
            print_cmd(commandStr)

        elif char in '\x1b':  # arrow key pressed
            null = getch()  # waste a character
            direction = getch()  # grab the direction

            if direction in 'A':  # up arrow pressed
                if movingIndex:
                    movingIndex -= 1 
                    commandStr = historyList[movingIndex]
                else:
                    if historyList:
                        commandStr = historyList[0]
                    else:
                        commandStr = ""

                print_cmd(commandStr)

            if direction in 'B':  # down arrow pressed
                if movingIndex < len(historyList):
                    movingIndex += 1
                    if movingIndex < len(historyList):
                        commandStr = historyList[movingIndex]
                    else:
                        commandStr = ""
                else:
                    commandStr = ""

            if direction in 'C':  # right arrow pressed  
                commandStr = commandStr + "\x1b[C"

            if direction in 'D':  # left arrow pressed
                commandStr = commandStr + "\x1b[D"

        elif char in '\r':  # return pressed 
            
            if not commandStr:
                print_cmd("\n")
                continue
            
            historyList.append(commandStr)
            movingIndex += 1

            commandList:list[ShellCommand] = parseCommand(commandStr)
            pipe_result = None  # Initialize for piped results

            for i in range(0, len(commandList)):
                result:str = ""
                try:
                    if commandList[i].name.startswith("!"):
                        search_term = commandList[i].name[1:]  # Get the part after '!'
                        
                        found_command = None
                        for hist_cmd in reversed(historyList):  # Search from most recent backwards
                            if hist_cmd.startswith(search_term):
                                found_command = hist_cmd
                                break
                        
                        if found_command:
                            print_cmd(f"Executing: {found_command}")
                            commandStr = found_command
                            commandList = parseCommand(found_command)  # Reparse the found command
                        else:
                            result = f"{commandStr}\n{commandList[i].name}: event not found\n"
                            print_cmd(result)
                            commandStr = ""


                    if commandList[i].name == "history":
                        result = history(historyList, flags=commandList[i].flags, params=commandList[i].params)
                        if not historyList:
                            movingIndex = 0

                    elif callable(getattr(cmd_pkg, commandList[i].name, None)):
                        commandFunc = getattr(cmd_pkg, commandList[i].name)

                        if commandList[i].fileIn:  # Handle file input redirection
                            try:
                                commandList[i].params.append(commandList[i].infile)
                            except:
                                result = f"File {commandList[i].infile} not found in virtual filesystem."
                                print_cmd(result)
                                commandStr = ""
                                break



                        # Execute the command
                        result = commandFunc(flags=commandList[i].flags, \
                                params=commandList[i].params, \
                                stdin= commandList[i].stdin, \
                                stdout=commandList[i].stdout)

                        # Handle output redirection (`>`)
                        if commandList[i].fileOut:
                            try:
                                fs._write_to_file(commandList[i].outfile, result)
                                result = ""  # Clear the result since it's redirected
                            except Exception as e:
                                result = f"Error writing to {commandList[i].outfile}: {str(e)}"
                                print_cmd(result)
                                commandStr = ""
                                break

                        # Handle append redirection (`>>`)
                        elif commandList[i].fileAppend:
                            try:
                                existing_content = fs.cat([commandList[i].outfile])
                                updated_content = existing_content + result
                                fs._write_to_file(commandList[i].outfile, updated_content)
                                result = ""  # Clear the result since it's redirected
                            except Exception as e:
                                result = f"Error appending to {commandList[i].outfile}: {str(e)}"
                                print_cmd(result)
                                commandStr = ""
                                break

                    else:
                        result = f"{commandStr}\n{commandList[i].name}: command not found\n"
                        print_cmd(result)
                        commandStr = ""
                        break

                    # Handle piping
                    if i + 1 < len(commandList) and not commandList[i].stdout:
                        # Write result to temporary file if it's being piped to the next command
                        temp_filename="pipe_result.txt"
                        fs._write_to_file(temp_filename, result)
                        commandList[i+1].params.append(temp_filename)
                        result = ""

                except (SystemExit) as e:
                    with open(historyFileName, "w") as historyFile:
                        historyFile.write('\n'.join(historyList))
                    print_cmd(f"{commandStr}\n")
                    cmd_pkg.exit()

                # If last command
                if i == len(commandList) - 1:
                    print_cmd(f"{commandStr}\n{result}\n")
                    commandStr = ""

        else:
            commandStr += char  # add typed character to our "cmd"
