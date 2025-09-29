"""
Integration module for connecting the Game Library with the Modern Gaming Advisor.
"""

import tkinter as tk
from game_library.game_ui import GameLibraryUI

def integrate_game_library(modern_gaming_advisor, notebook):
    """Integrate the Game Library into the Modern Gaming Advisor application.
    
    Args:
        modern_gaming_advisor: The ModernGamingAdvisor instance
        notebook: The ttk.Notebook instance for tabs
    
    Returns:
        The GameLibraryUI instance
    """
    # Create a new tab for the game library
    game_library_frame = tk.Frame(notebook, bg=modern_gaming_advisor.bg_primary)
    notebook.add(game_library_frame, text="🎮 Game Library")
    
    # Create a color palette dictionary to pass to GameLibraryUI
    vibrant_colors = {
        'bg_primary': modern_gaming_advisor.bg_primary,
        'bg_secondary': modern_gaming_advisor.bg_secondary,
        'bg_tertiary': modern_gaming_advisor.bg_tertiary,
        'text_primary': modern_gaming_advisor.text_primary,
        'text_secondary': modern_gaming_advisor.text_secondary,
        'accent_orange': modern_gaming_advisor.accent_orange,
        'accent_blue': modern_gaming_advisor.accent_blue,
        'accent_green': modern_gaming_advisor.accent_green,
        'accent_purple': modern_gaming_advisor.accent_purple,
        'accent_yellow': modern_gaming_advisor.accent_yellow
    }
    
    # Initialize GameLibraryUI with the frame as the master and our vibrant colors
    game_library_ui = GameLibraryUI(game_library_frame, vibrant_colors=vibrant_colors)
    
    return game_library_ui