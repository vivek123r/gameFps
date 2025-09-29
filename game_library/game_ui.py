"""
Game Library UI module for displaying games in a grid-like interface.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import io
import webbrowser
import threading
from .game_api import GameAPI

class GameLibraryUI:
    """Class to handle the Game Library UI."""
    
    def __init__(self, master=None, api=None, vibrant_colors=None):
        """Initialize the Game Library UI.
        
        Args:
            master (tk.Tk or tk.Frame): Parent widget
            api (GameAPI): GameAPI instance for fetching game data
            vibrant_colors (dict): Dictionary of vibrant colors for UI styling
        """
        if master is None:
            self.root = tk.Tk()
            self.root.title("Game Library")
            self.root.geometry("1200x800")
            self.is_standalone = True
        else:
            self.root = master
            self.is_standalone = False
            
        # Set up colors - either use provided colors or defaults
        if vibrant_colors:
            self.bg_primary = vibrant_colors['bg_primary']
            self.bg_secondary = vibrant_colors['bg_secondary']
            self.bg_tertiary = vibrant_colors['bg_tertiary']
            self.text_primary = vibrant_colors['text_primary']
            self.text_secondary = vibrant_colors['text_secondary']
            self.accent_orange = vibrant_colors['accent_orange']
            self.accent_blue = vibrant_colors['accent_blue']
            self.accent_green = vibrant_colors['accent_green']
            self.accent_purple = vibrant_colors['accent_purple']
            self.accent_yellow = vibrant_colors['accent_yellow']
        else:
            # Default GitHub dark theme
            self.bg_primary = '#0d1117'
            self.bg_secondary = '#161b22'
            self.bg_tertiary = '#21262d'
            self.text_primary = '#c9d1d9'
            self.text_secondary = '#8b949e'
            self.accent_orange = '#f0883e'
            self.accent_blue = '#58a6ff'
            self.accent_green = '#3fb950'
            self.accent_purple = '#8957e5'
            self.accent_yellow = '#d29922'
        
        self.api = api if api else GameAPI()
        
        # Initialize image placeholders
        self.image_cache = {}
        self.default_image = None
        
        # Create widgets
        self.create_widgets()
        
        # Load data
        self.load_data()
        
    def create_widgets(self):
        """Create UI widgets."""
        # Configure the root background
        self.root.configure(bg=self.bg_primary)
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_primary)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title and search bar frame with vibrant styling
        self.header_frame = tk.Frame(self.main_frame, bg=self.bg_secondary, padx=15, pady=15)
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icon and Title with vibrant styling
        title_icon = tk.Label(self.header_frame, text="🎮", font=("Segoe UI", 24),
                             bg=self.bg_secondary, fg=self.accent_orange)
        title_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.title_label = tk.Label(self.header_frame, text="Game Library", 
                                  font=("Segoe UI", 20, "bold"),
                                  bg=self.bg_secondary, fg=self.text_primary)
        self.title_label.pack(side=tk.LEFT)
        
        # Search bar with vibrant styling
        self.search_var = tk.StringVar()
        self.search_frame = tk.Frame(self.header_frame, bg=self.bg_secondary)
        self.search_frame.pack(side=tk.RIGHT, padx=10)
        
        # Search icon
        search_icon = tk.Label(self.search_frame, text="🔍", 
                             font=("Segoe UI", 12), 
                             bg=self.bg_secondary, fg=self.accent_blue)
        search_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Styled search entry
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=25,
                                   font=("Segoe UI", 10),
                                   bg=self.bg_tertiary, fg=self.text_primary,
                                   insertbackground=self.text_primary,
                                   relief='flat', bd=0)
        self.search_entry.pack(side=tk.LEFT, padx=5, ipady=5)
        
        # Vibrant search button
        self.search_button = tk.Button(self.search_frame, text="Search",
                                     command=self.search_games,
                                     bg=self.accent_blue, fg=self.text_primary,
                                     font=("Segoe UI", 9, "bold"),
                                     relief="flat", padx=10, pady=5)
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Filter frame with vibrant styling
        self.filter_frame = tk.Frame(self.main_frame, bg=self.bg_secondary, padx=15, pady=10)
        self.filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Filter title with icon
        filter_icon = tk.Label(self.filter_frame, text="🔖", 
                             font=("Segoe UI", 12),
                             bg=self.bg_secondary, fg=self.accent_yellow)
        filter_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        filter_label = tk.Label(self.filter_frame, text="Filters:", 
                              font=("Segoe UI", 11, "bold"),
                              bg=self.bg_secondary, fg=self.accent_yellow)
        filter_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Genre filter with vibrant styling
        genre_label = tk.Label(self.filter_frame, text="Genre:", 
                             font=("Segoe UI", 10),
                             bg=self.bg_secondary, fg=self.text_primary)
        genre_label.pack(side=tk.LEFT, padx=5)
        
        self.genre_var = tk.StringVar()
        self.genre_combo = ttk.Combobox(self.filter_frame, textvariable=self.genre_var, width=15,
                                       font=("Segoe UI", 9))
        self.genre_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.genre_combo.bind("<<ComboboxSelected>>", self.filter_by_genre)
        
        # Platform filter with vibrant styling
        platform_label = tk.Label(self.filter_frame, text="Platform:", 
                                font=("Segoe UI", 10),
                                bg=self.bg_secondary, fg=self.text_primary)
        platform_label.pack(side=tk.LEFT, padx=5)
        
        self.platform_var = tk.StringVar()
        self.platform_combo = ttk.Combobox(self.filter_frame, textvariable=self.platform_var, width=15,
                                          font=("Segoe UI", 9))
        self.platform_combo.pack(side=tk.LEFT, padx=0)
        self.platform_combo.bind("<<ComboboxSelected>>", self.filter_by_platform)
        
        # Reset filters button
        self.reset_btn = tk.Button(self.filter_frame, text="Reset Filters",
                                 command=self.reset_filters,
                                 bg=self.bg_tertiary, fg=self.text_primary,
                                 font=("Segoe UI", 9),
                                 relief="flat", padx=10, pady=2)
        self.reset_btn.pack(side=tk.RIGHT, padx=5)
        
        # Sort options
        ttk.Label(self.filter_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="Rating")
        self.sort_options = {"Rating": "-rating", "Released": "-released", "Name": "name"}
        self.sort_combo = ttk.Combobox(self.filter_frame, textvariable=self.sort_var, 
                                       values=list(self.sort_options.keys()), width=10)
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_combo.bind("<<ComboboxSelected>>", self.sort_games)
        
        # Create a frame with canvas and scrollbar for the game grid
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbar for the game grid
        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame for game grid inside canvas
        self.game_grid_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.game_grid_frame, anchor="nw")
        
        # Bind mouse wheel to scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Loading games...")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Pagination frame
        self.pagination_frame = ttk.Frame(self.main_frame)
        self.pagination_frame.pack(fill=tk.X, pady=10)
        
        self.prev_button = ttk.Button(self.pagination_frame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.page_label = ttk.Label(self.pagination_frame, text="Page 1")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.next_button = ttk.Button(self.pagination_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        # Game detail popup
        self.game_detail_toplevel = None
        
        # Current state
        self.current_page = 1
        self.current_filter = None
        self.total_pages = 1
        
        # Style
        self.style = ttk.Style()
        self.configure_styles()
        
    def configure_styles(self):
        """Configure ttk styles."""
        # Create game card style with vibrant gaming aesthetics
        self.style.configure("GameCard.TFrame", 
                           background=self.bg_tertiary if hasattr(self, 'bg_tertiary') else "#1C0F28", 
                           borderwidth=2, 
                           relief="flat")
        
        # Hover effect style with gradient-like glow effect
        self.style.configure("GameCardHover.TFrame", 
                           background=self.bg_tertiary if hasattr(self, 'bg_tertiary') else "#3F2556", 
                           borderwidth=2, 
                           bordercolor=self.accent_purple if hasattr(self, 'accent_purple') else "#B366FF", 
                           relief="raised")
        
        # Game title with modern gaming font
        self.style.configure("GameTitle.TLabel", 
                           font=("Segoe UI", 12, "bold"),
                           foreground=self.text_primary if hasattr(self, 'text_primary') else "#FFFFFF")
        
        # Game info with improved readability
        self.style.configure("GameInfo.TLabel", 
                           font=("Segoe UI", 10),
                           foreground=self.text_secondary if hasattr(self, 'text_secondary') else "#DCC6E4")
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling.
        
        Args:
            event (tk.Event): Mousewheel event
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def load_data(self):
        """Load initial data from API."""
        # Start loading popular games in a separate thread
        threading.Thread(target=self._load_popular_games).start()
        
        # Load genres and platforms
        threading.Thread(target=self._load_filters).start()
        
    def _load_filters(self):
        """Load genres and platforms from API."""
        # Load genres
        genre_data = self.api.get_genres()
        if "results" in genre_data:
            genres = ["All Genres"] + [genre["name"] for genre in genre_data["results"]]
            self._update_combobox(self.genre_combo, genres)
            
            # Map genre names to IDs
            self.genre_map = {genre["name"]: genre["id"] for genre in genre_data["results"]}
            self.genre_map["All Genres"] = None
        
        # Load platforms
        platform_data = self.api.get_platforms()
        if "results" in platform_data:
            platforms = ["All Platforms"] + [platform["name"] for platform in platform_data["results"]]
            self._update_combobox(self.platform_combo, platforms)
            
            # Map platform names to IDs
            self.platform_map = {platform["name"]: platform["id"] for platform in platform_data["results"]}
            self.platform_map["All Platforms"] = None
    
    def _update_combobox(self, combo, values):
        """Update combobox values and set to first value.
        
        Args:
            combo (ttk.Combobox): Combobox to update
            values (list): List of values
        """
        combo["values"] = values
        combo.current(0)  # Set to first value
        
    def _load_popular_games(self):
        """Load popular games from API."""
        self.update_status("Loading popular games...")
        
        # Get sort ordering
        sort_key = self.sort_options[self.sort_var.get()]
        
        # Get popular games
        games_data = self.api.get_popular_games(
            page=self.current_page, 
            ordering=sort_key
        )
        
        if "results" in games_data:
            self.update_status(f"Displaying {len(games_data['results'])} games")
            
            # Calculate total pages
            if "count" in games_data:
                self.total_pages = (games_data["count"] // 20) + 1
                self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
            
            # Clear game grid
            for widget in self.game_grid_frame.winfo_children():
                widget.destroy()
            
            # Display games in grid
            self.display_game_grid(games_data["results"])
        else:
            self.update_status("Failed to load games")
            
    def update_status(self, message):
        """Update status label text.
        
        Args:
            message (str): Status message
        """
        # Use after to ensure this runs on the main thread
        self.status_label.after(0, lambda: self.status_label.config(text=message))
        
    def display_game_grid(self, games):
        """Display games in a grid layout with vibrant styling.
        
        Args:
            games (list): List of game data dictionaries
        """
        # Clear existing grid
        for widget in self.game_grid_frame.winfo_children():
            widget.destroy()
        
        # Calculate grid dimensions
        num_cols = 3  # Number of columns in the grid (reduced to make cards larger)
        
        # Create game cards in grid with vibrant styling
        for i, game in enumerate(games):
            row = i // num_cols
            col = i % num_cols
            
            # Create game card with vibrant styling
            game_card = self.create_game_card(game)
            game_card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Configure grid weights
            self.game_grid_frame.grid_columnconfigure(col, weight=1)
            
        # Update canvas scroll region
        self.game_grid_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def create_game_card(self, game):
        """Create a vibrant game card widget with modern styling and enhanced hover effects.
        
        Args:
            game (dict): Game data dictionary
            
        Returns:
            tk.Frame: Vibrant game card frame with gaming-inspired design
        """
        # Create card frame with glowing border effect
        card = ttk.Frame(self.game_grid_frame, style="GameCard.TFrame", width=300, height=400)
        card.grid_propagate(False)  # Don't shrink to content
        
        # Create a highlight border frame that will change on hover
        highlight_frame = tk.Frame(card, bg=self.accent_purple, padx=2, pady=2)
        highlight_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inner content with gradient-like background
        inner_card = tk.Frame(highlight_frame, bg=self.bg_secondary, padx=0, pady=0)
        inner_card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Game image with styled frame
        img_frame = tk.Frame(inner_card, bg=self.bg_secondary)
        img_frame.pack(fill=tk.X)
        
        # Placeholder for image with vibrant border
        img_container = tk.Frame(img_frame, bg=self.accent_blue, padx=2, pady=2)
        img_container.pack(fill=tk.X, padx=8, pady=8)
        
        img_label = tk.Label(img_container, bg=self.bg_primary)
        img_label.pack(fill=tk.BOTH, expand=True)
        
        # Load image in a separate thread
        if "background_image" in game and game["background_image"]:
            threading.Thread(target=self._load_game_image, 
                           args=(game["background_image"], img_label, 280, 158)).start()
        
        # Game title with vibrant styling
        title_frame = tk.Frame(inner_card, bg=self.bg_tertiary, padx=10, pady=10)
        title_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        title_label = tk.Label(title_frame, text=game["name"], 
                            bg=self.bg_tertiary, fg=self.text_primary,
                            font=("Segoe UI", 11, "bold"), 
                            wraplength=260, justify="center")
        title_label.pack(fill=tk.X)
        
        # Game info with vibrant styling
        info_frame = tk.Frame(inner_card, bg=self.bg_secondary, padx=10, pady=5)
        info_frame.pack(fill=tk.X, padx=8, pady=0)
        
        # Release date with icon
        if "released" in game and game["released"]:
            release_frame = tk.Frame(info_frame, bg=self.bg_secondary)
            release_frame.pack(fill=tk.X, pady=2)
            
            # Calendar icon
            calendar_icon = tk.Label(release_frame, text="📅", 
                                  bg=self.bg_secondary, fg=self.accent_yellow,
                                  font=("Segoe UI", 10))
            calendar_icon.pack(side=tk.LEFT, padx=(0, 5))
            
            # Release date with styled text
            release_label = tk.Label(release_frame, text=f"Released: {game['released']}", 
                                  bg=self.bg_secondary, fg=self.text_secondary,
                                  font=("Segoe UI", 9))
            release_label.pack(side=tk.LEFT)
        
        # Rating with star icon and vibrant styling
        if "rating" in game and game["rating"]:
            rating_frame = tk.Frame(info_frame, bg=self.bg_secondary)
            rating_frame.pack(fill=tk.X, pady=2)
            
            # Star icon
            star_icon = tk.Label(rating_frame, text="⭐", 
                              bg=self.bg_secondary, fg=self.accent_orange,
                              font=("Segoe UI", 10))
            star_icon.pack(side=tk.LEFT, padx=(0, 5))
            
            # Rating with styled text and color based on rating
            rating_value = float(game['rating'])
            if rating_value >= 4.0:
                rating_color = self.accent_green
            elif rating_value >= 3.0:
                rating_color = self.accent_yellow
            else:
                rating_color = self.accent_orange
                
            rating_label = tk.Label(rating_frame, text=f"Rating: {rating_value}/5", 
                                 bg=self.bg_secondary, fg=rating_color,
                                 font=("Segoe UI", 9, "bold"))
            rating_label.pack(side=tk.LEFT)
        
        # Platforms with gamepad icon and vibrant styling
        platform_frame = tk.Frame(info_frame, bg=self.bg_secondary)
        platform_frame.pack(fill=tk.X, pady=2)
        
        # Gamepad icon
        gamepad_icon = tk.Label(platform_frame, text="🎮", 
                             bg=self.bg_secondary, fg=self.accent_purple,
                             font=("Segoe UI", 10))
        gamepad_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Platform text
        platform_text = ""
        if "platforms" in game and game["platforms"]:
            platforms = [p["platform"]["name"] for p in game["platforms"]]
            platform_text += ", ".join(platforms[:3])
            if len(platforms) > 3:
                platform_text += f" +{len(platforms) - 3} more"
        else:
            platform_text += "Unknown"
            
        platform_label = tk.Label(platform_frame, text=platform_text, 
                              bg=self.bg_secondary, fg=self.text_secondary,
                              font=("Segoe UI", 9), wraplength=240)
        platform_label.pack(side=tk.LEFT)
        
        # Details button with vibrant styling
        button_frame = tk.Frame(inner_card, bg=self.bg_secondary, pady=10)
        button_frame.pack(fill=tk.X, padx=8, pady=(5, 8))
        
        details_button = tk.Button(button_frame, text="SHOW DETAILS", 
                               command=lambda g_id=game["id"]: self.show_game_details(g_id),
                               bg=self.accent_blue, fg=self.text_primary,
                               font=("Segoe UI", 9, "bold"),
                               relief="flat", padx=10, pady=5,
                               activebackground=self.accent_purple)
        details_button.pack(fill=tk.X)
        
        # Make the whole card clickable with hover effects
        for widget in [card, inner_card, img_label, title_label]:
            widget.bind("<Button-1>", lambda e, g_id=game["id"]: self.show_game_details(g_id))
            widget.bind("<Enter>", lambda e, w=card: self._on_card_enter(w))
            widget.bind("<Leave>", lambda e, w=card: self._on_card_leave(w))
        
        return card
    
    def _on_card_enter(self, widget):
        """Handle mouse enter event on game card with enhanced vibrant effects.
        
        Args:
            widget (ttk.Frame): Game card frame
        """
        # Apply hover style to the frame
        widget.configure(style="GameCardHover.TFrame")
        widget["relief"] = "raised"
        
        # Find the highlight frame (the second child) and change its color to create a glowing effect
        if len(widget.winfo_children()) > 0:
            highlight_frame = widget.winfo_children()[0]
            if isinstance(highlight_frame, tk.Frame):
                highlight_frame.configure(bg=self.accent_orange)
                
                # Add a subtle scale animation to the inner elements
                if len(highlight_frame.winfo_children()) > 0:
                    inner_frame = highlight_frame.winfo_children()[0]
                    inner_frame.configure(bg=self.bg_tertiary)
                    
                    # Find the button and update its style for a cohesive hover effect
                    for child in inner_frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            for btn_container in child.winfo_children():
                                if isinstance(btn_container, tk.Frame):
                                    for btn in btn_container.winfo_children():
                                        if isinstance(btn, tk.Button):
                                            btn.configure(bg=self.accent_orange)
        
    def _on_card_leave(self, widget):
        """Handle mouse leave event on game card, reverting vibrant effects.
        
        Args:
            widget (ttk.Frame): Game card frame
        """
        # Revert to normal style
        widget.configure(style="GameCard.TFrame")
        widget["relief"] = "flat"
        
        # Reset highlight frame color
        if len(widget.winfo_children()) > 0:
            highlight_frame = widget.winfo_children()[0]
            if isinstance(highlight_frame, tk.Frame):
                highlight_frame.configure(bg=self.accent_purple)
                
                # Reset inner elements
                if len(highlight_frame.winfo_children()) > 0:
                    inner_frame = highlight_frame.winfo_children()[0]
                    inner_frame.configure(bg=self.bg_secondary)
                    
                    # Reset button style
                    for child in inner_frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            for btn_container in child.winfo_children():
                                if isinstance(btn_container, tk.Frame):
                                    for btn in btn_container.winfo_children():
                                        if isinstance(btn, tk.Button):
                                            btn.configure(bg=self.accent_blue)
    
    def _load_game_image(self, url, label, width=240, height=135):
        """Load game image from URL and update label.
        
        Args:
            url (str): Image URL
            label (ttk.Label): Label to update
            width (int): Desired width
            height (int): Desired height
        """
        try:
            # Check cache first
            if url in self.image_cache:
                photo = self.image_cache[url]
            else:
                # Download image
                response = requests.get(url)
                img = Image.open(io.BytesIO(response.content))
                
                # Resize image
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Cache the image
                self.image_cache[url] = photo
                
            # Update label in main thread
            label.after(0, lambda: label.configure(image=photo))
            
            # Store a reference to prevent garbage collection
            label.image = photo
            
        except Exception as e:
            print(f"Error loading image: {e}")
            # Use default image if available
            if self.default_image:
                label.after(0, lambda: label.configure(image=self.default_image))
                label.image = self.default_image
    
    def show_game_details(self, game_id):
        """Show detailed information about a game.
        
        Args:
            game_id (int): Game ID
        """
        # Show loading status
        self.update_status(f"Loading details for game ID: {game_id}")
        
        # Load game details in a separate thread
        threading.Thread(target=self._load_and_display_game_details, args=(game_id,)).start()
    
    def _load_and_display_game_details(self, game_id):
        """Load and display game details.
        
        Args:
            game_id (int): Game ID
        """
        # Get game details
        game_data = self.api.get_game_details(game_id)
        
        # Get screenshots
        screenshots = self.api.get_game_screenshots(game_id)
        
        # Get trailers
        trailers = self.api.get_game_trailers(game_id)
        
        # Display details in main thread
        self.root.after(0, lambda: self._display_game_details(game_data, screenshots, trailers))
        
        # Update status
        self.update_status("Game details loaded")
    
    def _display_game_details(self, game_data, screenshots, trailers):
        """Display game details in a popup window.
        
        Args:
            game_data (dict): Game details data
            screenshots (dict): Game screenshots data
            trailers (dict): Game trailers data
        """
        # Close existing popup if open
        if self.game_detail_toplevel and self.game_detail_toplevel.winfo_exists():
            self.game_detail_toplevel.destroy()
        
        # Create new popup
        self.game_detail_toplevel = tk.Toplevel(self.root)
        self.game_detail_toplevel.title(game_data["name"])
        self.game_detail_toplevel.geometry("900x700")
        self.game_detail_toplevel.minsize(900, 700)
        
        # Main frame
        main_frame = ttk.Frame(self.game_detail_toplevel)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header with game image and basic info
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        # Game image
        img_frame = ttk.Frame(header_frame, width=320, height=180)
        img_frame.pack_propagate(False)
        img_frame.pack(side=tk.LEFT, padx=10)
        
        img_label = ttk.Label(img_frame)
        img_label.pack(fill=tk.BOTH, expand=True)
        
        if "background_image" in game_data and game_data["background_image"]:
            threading.Thread(target=self._load_game_image, 
                            args=(game_data["background_image"], img_label, 320, 180)).start()
        
        # Basic info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Game title
        title_label = ttk.Label(info_frame, text=game_data["name"], 
                               font=("Helvetica", 18, "bold"))
        title_label.pack(anchor="w", pady=5)
        
        # Release date
        if "released" in game_data and game_data["released"]:
            release_label = ttk.Label(info_frame, text=f"Released: {game_data['released']}", 
                                     font=("Helvetica", 11))
            release_label.pack(anchor="w", pady=2)
        
        # Rating
        if "rating" in game_data and game_data["rating"]:
            rating_label = ttk.Label(info_frame, text=f"Rating: {game_data['rating']}/5", 
                                    font=("Helvetica", 11))
            rating_label.pack(anchor="w", pady=2)
        
        # Platforms
        platform_text = "Platforms: "
        if "platforms" in game_data and game_data["platforms"]:
            platforms = [p["platform"]["name"] for p in game_data["platforms"]]
            platform_text += ", ".join(platforms)
        else:
            platform_text += "Unknown"
            
        platform_label = ttk.Label(info_frame, text=platform_text, 
                                  font=("Helvetica", 11), wraplength=400)
        platform_label.pack(anchor="w", pady=2)
        
        # Genres
        genre_text = "Genres: "
        if "genres" in game_data and game_data["genres"]:
            genres = [g["name"] for g in game_data["genres"]]
            genre_text += ", ".join(genres)
        else:
            genre_text += "Unknown"
            
        genre_label = ttk.Label(info_frame, text=genre_text, 
                               font=("Helvetica", 11), wraplength=400)
        genre_label.pack(anchor="w", pady=2)
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Description tab
        desc_frame = ttk.Frame(notebook)
        notebook.add(desc_frame, text="Description")
        
        # Description text
        desc_text = tk.Text(desc_frame, wrap=tk.WORD, font=("Helvetica", 11),
                           height=10, width=80)
        desc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert description
        if "description_raw" in game_data and game_data["description_raw"]:
            desc_text.insert(tk.END, game_data["description_raw"])
        else:
            desc_text.insert(tk.END, "No description available.")
        
        desc_text.config(state=tk.DISABLED)  # Make read-only
        
        # Screenshots tab
        screenshots_frame = ttk.Frame(notebook)
        notebook.add(screenshots_frame, text="Screenshots")
        
        # Create a canvas for screenshots
        ss_canvas = tk.Canvas(screenshots_frame)
        ss_scrollbar = ttk.Scrollbar(screenshots_frame, orient=tk.VERTICAL, command=ss_canvas.yview)
        
        ss_canvas.configure(yscrollcommand=ss_scrollbar.set)
        ss_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        ss_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame for screenshots inside canvas
        ss_inner_frame = ttk.Frame(ss_canvas)
        ss_canvas_window = ss_canvas.create_window((0, 0), window=ss_inner_frame, anchor="nw")
        
        # Configure canvas to resize with window
        def _configure_ss_canvas(event):
            ss_canvas.itemconfig(ss_canvas_window, width=event.width)
        
        ss_canvas.bind('<Configure>', _configure_ss_canvas)
        
        # Load screenshots
        if "results" in screenshots and screenshots["results"]:
            for i, screenshot in enumerate(screenshots["results"]):
                if "image" in screenshot:
                    # Create frame for this screenshot
                    ss_frame = ttk.Frame(ss_inner_frame)
                    ss_frame.pack(fill=tk.X, padx=10, pady=10)
                    
                    # Screenshot image
                    ss_label = ttk.Label(ss_frame)
                    ss_label.pack(fill=tk.X)
                    
                    # Load image in a separate thread
                    threading.Thread(target=self._load_game_image, 
                                    args=(screenshot["image"], ss_label, 800, 450)).start()
        else:
            ttk.Label(ss_inner_frame, text="No screenshots available.").pack(padx=10, pady=10)
        
        # Update screenshots canvas scroll region after images are loaded
        ss_inner_frame.update_idletasks()
        ss_canvas.configure(scrollregion=ss_canvas.bbox("all"))
        
        # Trailers tab
        trailers_frame = ttk.Frame(notebook)
        notebook.add(trailers_frame, text="Trailers")
        
        # Display trailers
        if "results" in trailers and trailers["results"]:
            trailer_list_frame = ttk.Frame(trailers_frame)
            trailer_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for i, trailer in enumerate(trailers["results"]):
                trailer_frame = ttk.Frame(trailer_list_frame, style="GameCard.TFrame")
                trailer_frame.pack(fill=tk.X, pady=10)
                
                # Trailer title
                trailer_title = ttk.Label(trailer_frame, text=trailer.get("name", f"Trailer {i+1}"), 
                                       font=("Helvetica", 12, "bold"))
                trailer_title.pack(anchor="w", padx=10, pady=5)
                
                # Trailer preview (if available)
                if "preview" in trailer:
                    preview_frame = ttk.Frame(trailer_frame)
                    preview_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    preview_label = ttk.Label(preview_frame)
                    preview_label.pack()
                    
                    # Load preview image
                    if trailer["preview"]:
                        threading.Thread(target=self._load_game_image, 
                                       args=(trailer["preview"], preview_label, 320, 180)).start()
                
                # Watch button
                if "data" in trailer and trailer["data"] and "max" in trailer["data"]:
                    watch_button = ttk.Button(trailer_frame, text="Watch Trailer", 
                                           command=lambda url=trailer["data"]["max"]: webbrowser.open(url))
                    watch_button.pack(pady=5)
        else:
            ttk.Label(trailers_frame, text="No trailers available.").pack(padx=10, pady=10)
        
        # Links tab
        links_frame = ttk.Frame(notebook)
        notebook.add(links_frame, text="Links")
        
        # Display links
        links_inner_frame = ttk.Frame(links_frame)
        links_inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Website
        if "website" in game_data and game_data["website"]:
            website_frame = ttk.Frame(links_inner_frame)
            website_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(website_frame, text="Official Website:", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT)
            
            website_link = ttk.Label(website_frame, text=game_data["website"], 
                                   font=("Helvetica", 11), foreground="blue", cursor="hand2")
            website_link.pack(side=tk.LEFT, padx=10)
            website_link.bind("<Button-1>", lambda e: webbrowser.open(game_data["website"]))
        
        # Reddit
        if "reddit_url" in game_data and game_data["reddit_url"]:
            reddit_frame = ttk.Frame(links_inner_frame)
            reddit_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(reddit_frame, text="Reddit:", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT)
            
            reddit_link = ttk.Label(reddit_frame, text=game_data["reddit_url"], 
                                  font=("Helvetica", 11), foreground="blue", cursor="hand2")
            reddit_link.pack(side=tk.LEFT, padx=10)
            reddit_link.bind("<Button-1>", lambda e: webbrowser.open(game_data["reddit_url"]))
        
        # Metacritic
        if "metacritic_url" in game_data and game_data["metacritic_url"]:
            metacritic_frame = ttk.Frame(links_inner_frame)
            metacritic_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(metacritic_frame, text="Metacritic:", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT)
            
            metacritic_link = ttk.Label(metacritic_frame, text=game_data["metacritic_url"], 
                                      font=("Helvetica", 11), foreground="blue", cursor="hand2")
            metacritic_link.pack(side=tk.LEFT, padx=10)
            metacritic_link.bind("<Button-1>", lambda e: webbrowser.open(game_data["metacritic_url"]))
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # RAWG link
        rawg_button = ttk.Button(button_frame, text="View on RAWG", 
                               command=lambda: webbrowser.open(f"https://rawg.io/games/{game_data['slug']}"))
        rawg_button.pack(side=tk.LEFT, padx=10)
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", 
                                 command=self.game_detail_toplevel.destroy)
        close_button.pack(side=tk.RIGHT, padx=10)
        
    def search_games(self):
        """Search for games based on search input."""
        query = self.search_var.get().strip()
        if query:
            self.update_status(f"Searching for: {query}")
            self.current_page = 1
            threading.Thread(target=self._load_search_results, args=(query,)).start()
        
    def _load_search_results(self, query):
        """Load search results from API.
        
        Args:
            query (str): Search query
        """
        results = self.api.search_games(query, page=self.current_page)
        
        if "results" in results:
            self.update_status(f"Found {len(results['results'])} games matching '{query}'")
            
            # Calculate total pages
            if "count" in results:
                self.total_pages = (results["count"] // 20) + 1
                self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
            
            # Display games
            self.display_game_grid(results["results"])
        else:
            self.update_status(f"No results found for '{query}'")
            
    def filter_by_genre(self, event=None):
        """Filter games by selected genre."""
        genre = self.genre_var.get()
        if genre == "All Genres":
            # Reset to popular games
            self.current_page = 1
            threading.Thread(target=self._load_popular_games).start()
        else:
            self.update_status(f"Filtering by genre: {genre}")
            genre_id = self.genre_map.get(genre)
            if genre_id:
                self.current_page = 1
                threading.Thread(target=self._load_genre_games, args=(genre_id,)).start()
    
    def _load_genre_games(self, genre_id):
        """Load games by genre from API.
        
        Args:
            genre_id (int): Genre ID
        """
        results = self.api.get_games_by_genre(genre_id, page=self.current_page)
        
        if "results" in results:
            genre_name = self.genre_var.get()
            self.update_status(f"Displaying {len(results['results'])} {genre_name} games")
            
            # Calculate total pages
            if "count" in results:
                self.total_pages = (results["count"] // 20) + 1
                self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
            
            # Display games
            self.display_game_grid(results["results"])
            
    def filter_by_platform(self, event=None):
        """Filter games by selected platform."""
        # TODO: Implement platform filtering
        platform = self.platform_var.get()
        self.update_status(f"Platform filtering not implemented yet: {platform}")
        
    def sort_games(self, event=None):
        """Sort games by selected option."""
        sort_option = self.sort_var.get()
        self.update_status(f"Sorting games by {sort_option}...")
        
        # Reload current view with new sort order
        self._load_popular_games()
        
    def next_page(self):
        """Go to next page of results."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
            self._load_popular_games()
            
    def prev_page(self):
        """Go to previous page of results."""
        if self.current_page > 1:
            self.current_page -= 1
            self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
            self._load_popular_games()
    
    def run(self):
        """Start the application main loop."""
        if self.is_standalone:
            self.root.mainloop()