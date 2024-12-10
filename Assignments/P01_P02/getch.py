#!/usr/bin/env python3
"""
This file is about using getch to capture input and handle certain keys 
when the are pushed. The 'command_helper.py' was about parsing and calling functions.
This file is about capturing the user input so that you can mimic shell behavior.

I'll discuss more in class.
"""
import os
import sys
from time import sleep

##################################################################################
##################################################################################
class Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): 
        return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        # prompt = "%: "
        # cmd = ""
        
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            # cmd += ch
            # sys.stdout.write("\r"+prompt+cmd)
            # sys.stdout.flush()
            # cmd = ""
            
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

##################################################################################
##################################################################################

# getch = Getch()                             # create instance of our getch class

# prompt = "%:"                               # set default prompt


# def print_cmd(cmd):
#     """ This function "cleans" off the command line, then prints
#         whatever cmd that is passed to it to the bottom of the terminal.
#     """
#     padding = " " * 80
#     sys.stdout.write("\r"+padding)
#     sys.stdout.write("\r"+prompt+cmd)
#     sys.stdout.flush()


