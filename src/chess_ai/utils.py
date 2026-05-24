"""Utility functions for ChessAI application.

Contains helper functions for colors, paths, and other common operations.
"""

import os
from typing import Dict

# ANSI color codes for terminal output
ANSI_COLORS: Dict[str, str] = {
    "red": "\033[91m",
    "orange": "\033[38;5;208m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "anil": "\033[34m",
    "purple": "\033[95m",
    "white": "\033[97m"
}

RESET_COLORS = "\033[0m"

# ASCII art banner
ASCII_ART = """
 ██████╗██╗  ██╗███████╗███████╗███████╗     █████╗ ██╗
██╔════╝██║  ██║██╔════╝██╔════╝██╔════╝    ██╔══██╗██║
██║     ███████║█████╗  ███████╗███████╗    ███████║██║
██║     ██╔══██║██╔══╝  ╚════██║╚════██║    ██╔══██║██║
╚██████╗██║  ██║███████║███████║███████║    ██║  ██║██║
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝
"""


def get_path(file_name: str) -> str:
    """
    Build absolute path relative to the module directory.
    
    Args:
        file_name: Name or relative path of the file/directory
        
    Returns:
        Absolute path to the file/directory
    """
    return os.path.join(
        os.path.dirname(__file__),
        file_name
    )


def print_header() -> None:
    """Print the application header with ASCII art and description."""
    print(f"{ANSI_COLORS['green']}{ASCII_ART}{RESET_COLORS}")
    print("* AI assistant specialized in chess")
    print("* CTRL + C to quit\n")


def print_message(message: str, color: str = "white") -> None:
    """
    Print a colored message to stdout.
    
    Args:
        message: The message to print
        color: Color name from ANSI_COLORS dictionary
    """
    color_code = ANSI_COLORS.get(color, RESET_COLORS)
    print(f"{color_code}{message}{RESET_COLORS}")
