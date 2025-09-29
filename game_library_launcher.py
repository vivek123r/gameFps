"""
Launcher script for the Game Library front page.
"""

import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import from game_library package
from game_library import GameLibraryUI

def main():
    """Launch the Game Library UI."""
    app = GameLibraryUI()
    app.run()

if __name__ == "__main__":
    main()