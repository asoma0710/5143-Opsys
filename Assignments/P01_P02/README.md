## 5143 Shell Project - P01

Due date: 09/25/2023

### Authors:
#### - [Angel Badillo](https://github.com/It-Is-Legend27)
#### - [Leslie Cook](https://github.com/Leslie-N-Cook)

### Overview:

This is a project written in Python3 that implements a basic shell that executes the UNIX commands below

### Instructions

- First, ensure all modules are installed for the shell commands by running

  `pip3 install -r requirements.txt` or `pip install -r requirements.txt`
- Next, execute the shell by running

  `python3 shell.py` or `python shell.py`
- To exit the shell, type

  `exit` or `ctrl-c`
- For more information about a specificcommand use the help flag

  `command --help`
- To run a command from the shell, type one of the commands from the list below including any flags and parameters needed

  `command -flags parameters`

## Table of Commands

| - |        Command        |                  Description                  |    Author    |             Flags             |            Parameters            |
| :-: | :--------------------: | :-------------------------------------------: | :-----------: | :---------------------------: | :-------------------------------: |
| 1 |    [ls](cmd_pkg/Ls.py)    |               directory listing               | Angel, Leslie | `-l` `-a` `-h` `-lah` |          `<dir name>`          |
| 2 |   [pwd](cmd_pkg/Pwd.py)   |            print working directory            |     Angel     |                              |                                  |
| 3 |    [cd](cmd_pkg/Cd.py)    |               change directory               |     Angel     |                              | `~` or `..` or `<dir name>` |
| 4 |   [cat](cmd_pkg/Cat.py)   |               concatenate files               |     Angel     |                              |          `<file name>`          |
| 5 |     [exit](shell.py)     |                  exit shell                  |     Angel     |                              |                                  |
| 6 | [mdkir](cmd_pkg/Mkdir.py) |             makes a new directory             |     Angel     |                              |          `<dir name>`          |
| 7 |   [who](cmd_pkg/Who.py)   |             show users logged in             |     Angel     |                              |                                  |
| 8 |  [sort](cmd_pkg/Sort.py)  |                   sort data                   |     Angel     |                              |          `<file name>`          |
| 9 |  [rmdir](cmd_pkg/Rmdir)  |            remove empty directory            |     Angel     |                              |          `<dir name>`          |
| 10 |    [rm](cmd_pkg/Rm.py)    |           remove file / directories           |     Angel     |            `-r`            | `<dir name>` or `<file name>` |
| 11 |    [history](shell.py)    |             show command history             | Leslie, Angel |                              |             `<num>`             |
| 12 |      [!x](shell.py)      |   retrieve command from history and run it   |     Angel     |                              |             `<num>`             |
| 13 |    [wc](cmd_pkg/Wc.py)    |   show line, word, and byte count of files   |     Angel     |     `-l` `-m` `-w`     |          `<file name>`          |
| 14 | [clear](cmd_pkg/Clear.py) |               clears the screen               |     Angel     |                              |                                  |
| 15 |    [cp](cmd_pkg/Cp.py)    |           copy file/dir to new path           |     Angel     |                              |     `<file/dir> <new path>`     |
| 16 |    [mv](cmd_pkg/Mv.py)    |           move file/dir to new path           |     Angel     |                              |     `<file/dir> <new path>`     |
| 17 | [touch](cmd_pkg/Touch.py) |             creates an empty file             |    Leslie    |                              |        `<new file name>`        |
| 18 | [chmod](cmd_pkg/Chmod.py) |  changes read, write, executable permissions  |    Leslie    |                              |  `<octal number> <file name>`  |
| 19 |  [grep](cmd_pkg/Grep.py)  | searches for a specific pattern of characters |    Leslie    | `-c` `-i` `-v ` `-l` |     `<pattern> <file path>`     |
| 20 |  [head](cmd_pkg/Head.py)  | writes to stdout the first 10 lines of a file |    Leslie    |       `-n, n is int`       |        `<path to file>`        |
| 21 |  [tail](cmd_pkg/Tail.py)  | writes to stdout the last 10 lines of a file |    Leslie    |       `-n, n is int`       |        `<path to file>`        |
| 22 |  [less](cmd_pkg/Less.py)  |      shows files contents on one screen      |    Leslie    |                              |        ` <path to file>`        |

## List of support functions

|                 Function                 |                                     Description                                     |
| :--------------------------------------: | :----------------------------------------------------------------------------------: |
|              [getch](getch.py)              |                        captures the users input for the shell                        |
|       [ParseCommand](ParseCommand.py)       | parses the command line input into a list of commands  to handle pipes and redirects |
|              [shell](shell.py)              |                         main program that launches the shell                         |
|         [init](cmd_pkg/__init__.py)         |            packages each command in [cmd_pkg](cmd_pkg) to use in the shell            |
| [InvalidFlagMsg](cmd_pkg/InvalidFlagMsg.py) |                   creates error message when a flag not recognized                   |
|  [TokenizeFlags](cmd_pkg/TokenizeFlags.py)  |                   checks for flags to direct the command behavior                   |

***References***

- [Python format size application (converting B to KB, MB, GB, TB) - Stack Overflow](https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb)
- [How to to split a list at a certain value](https://stackoverflow.com/a/30538599)
