import shlex

class ShellCommand(object):
    """
    Class description
    """
    def __init__(self) -> None:
        """
        Init ShellCommand Object
        """
        
        # name of command
        self.name:str = ""
        # flags of command
        self.flags:list[str] = []
        # parameters of command
        self.params:list[str] = []

        # Input file if file input
        self.infile:str = ""
        # Output file if file output
        self.outfile:str = ""

        # fileIn is True if command has ">"
        self.fileIn:bool = False
        # fileOut is True if command has "<"
        self.fileOut:bool = False
        # fileAppend is True if command has ">"
        self.fileAppend:bool = False

        # stdin is False if command input does
        # not come from user input, (e.g, comes from file or pipe)
        self.stdin:bool = True

        # stdout is False if command output
        # goes to next command's params (input)
        self.stdout:bool = True

        
    def __iter__(self):
        """
        Enables ShellCommand object to be casted as dict,
        list, tuple, and other iterables.
        """
        yield "name", self.name
        yield "flags", self.flags
        yield "params", self.params
        yield "fileIn", self.fileIn
        yield "fileOut", self.fileOut
        yield "fileAppend", self.fileAppend
        yield "infile", self.infile
        yield "outfile", self.outfile
        yield "stdin", self.stdin
        yield "stdout", self.stdout
    
    def __str__(self) -> str:
        """
        Returns string representation of ShellCommand object.
        """
        return str(dict(self))


def list_split(input_list:list[str] ,sep:str)->list[list[str]]:
    """
    Splits a list[str] on a separator. Returns list[list[str]].
    """
    outer = []
    inner = []
    for elem in input_list:
        if elem == sep:
            outer.append(inner)
            inner = []
        else:
            inner.append(elem)
    if inner:
        outer.append(inner)
    return outer

def parseCommand(commandStr:str)->list[ShellCommand]:
    """
    Accepts a string consisting of a command, parses it turns it into a list
    of ShellCommands.
    """
    commandList:list[ShellCommand] = []

    commandPartsList:list[list[str]] = list_split(shlex.split(commandStr), "|")

    for index,commandParts in enumerate(commandPartsList, 0):
        shellCommand:ShellCommand = ShellCommand()
        
        # If not first command, input will come prev command
        if index:
            shellCommand.stdin = False
        # If not last command, output will not go to stdout
        if index < len(commandPartsList)-1:
            shellCommand.stdout = False
        # Store name of command
        if commandParts:
            shellCommand.name = commandParts[0]
        
        i:int = 1
        while(i < len(commandParts)):
            # Is flag
            if commandParts[i].startswith("-"):
                shellCommand.flags.append(commandParts[i])
            # Infile redirect
            elif commandParts[i] == "<":
                shellCommand.fileIn = True
                shellCommand.stdin = False
                if i+1 < len(commandParts):
                    # increment counter
                    i += 1
                    shellCommand.infile = commandParts[i]
            # Outfile redirect
            elif commandParts[i] == ">":
                shellCommand.fileOut = True
                shellCommand.stdout = False
                if i+1 < len(commandParts):
                    # increment counter
                    i += 1
                    shellCommand.outfile = commandParts[i]
            # Outfile append redirect
            elif commandParts[i] == ">>":
                shellCommand.fileAppend = True
                shellCommand.stdout = False
                if i+1 < len(commandParts):
                    # increment counter
                    i += 1
                    shellCommand.outfile = commandParts[i]
            else:
                shellCommand.params.append(commandParts[i])
            # increment counter
            i +=1
        
        commandList.append(shellCommand)
            
    return commandList

if __name__ == "__main__":
    t = "cp A.txt Documents/MyDocs"
    print(t)
    s = parseCommand(t)

    try:
        from rich import pretty

        for cmd in s:
            pretty.pprint(dict(cmd))
    except(ImportError):
        for cmd in s:
            print(dict(cmd))