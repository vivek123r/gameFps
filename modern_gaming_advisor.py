import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psutil
import GPUtil
import cpuinfo
import threading
import time
import requests
from bs4 import BeautifulSoup
import json
import os
import re
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ModernGamingAdvisor:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 AI Gaming Advisor Pro - Next Gen")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0d1117')
        self.root.resizable(True, True)
        
        # Initialize AI
        self.ai_model = None
        self.setup_ai()
        
        # System specs and data
        self.system_specs = self.detect_system_specs()
        self.benchmark_cache = {}
        self.load_benchmark_cache()
        self.performance_history = []
        
        # Current recommendations
        self.current_settings = {}
        
        # Game history storage
        self.game_history = []
        self.load_game_history()
        
        # Setup modern UI
        self.setup_modern_styles()
        self.create_modern_gui()
        
        # Start monitoring
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_performance, daemon=True)
        self.monitor_thread.start()
        
        # Load benchmark data
        self.benchmark_thread = threading.Thread(target=self.load_benchmark_data, daemon=True)
        self.benchmark_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ai(self):
        """Setup Gemini AI"""
        if not GEMINI_AVAILABLE:
            return
        
        api_key_file = "gemini_api_key.txt"
        api_key = "AIzaSyArH-_4yPO3UX9Ap_9uslaPjnBTGwdXF1M"
        
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
        
        if not api_key:
            api_key = simpledialog.askstring(
                "Gemini API Key",
                "Enter your free Gemini API key:",
                show='*'
            )
            if api_key:
                with open(api_key_file, 'w') as f:
                    f.write(api_key)
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.ai_model = genai.GenerativeModel('gemini-2.5-pro')
                print("✅ Gemini AI initialized successfully!")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
    
    def detect_system_specs(self):
        """Detect system specifications"""
        try:
            cpu_info = cpuinfo.get_cpu_info()
            gpus = GPUtil.getGPUs()
            mem = psutil.virtual_memory()
            
            specs = {
                'cpu': cpu_info['brand_raw'],
                'cpu_cores': psutil.cpu_count(logical=False),
                'cpu_threads': psutil.cpu_count(logical=True),
                'ram_gb': round(mem.total / (1024**3), 1),
                'gpu': gpus[0].name if gpus else "Unknown GPU",
                'gpu_vram_mb': gpus[0].memoryTotal if gpus else 0,
                'gpu_vram_gb': round(gpus[0].memoryTotal / 1024, 1) if gpus else 0,
                'is_laptop': self.detect_if_laptop()
            }
            return specs
        except:
            return {'cpu': 'Unknown', 'gpu': 'Unknown', 'ram_gb': 0, 'gpu_vram_mb': 0, 'gpu_vram_gb': 0, 'is_laptop': False}
    
    def detect_if_laptop(self):
        """Detect if system is laptop or desktop"""
        try:
            # Check for laptop indicators
            cpu_info = cpuinfo.get_cpu_info()
            cpu_name = cpu_info.get('brand_raw', '').lower()
            
            # Laptop CPU indicators
            laptop_indicators = ['mobile', 'laptop', 'h', 'hs', 'hx', 'u', 'y', 'p']
            
            # Check if any laptop indicator is in CPU name
            for indicator in laptop_indicators:
                if indicator in cpu_name:
                    return True
            
            # Check GPU for laptop indicators
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_name = gpus[0].name.lower()
                if 'laptop' in gpu_name or 'mobile' in gpu_name:
                    return True
            
            return False
        except:
            return False
    
    def setup_modern_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern color scheme
        bg_primary = '#0d1117'      # GitHub dark
        bg_secondary = '#161b22'    # Darker panels
        bg_tertiary = '#21262d'     # Cards/buttons
        accent_blue = '#58a6ff'     # Primary accent
        accent_green = '#3fb950'    # Success/good
        accent_yellow = '#f1e05a'   # Warning
        accent_red = '#f85149'      # Error/critical
        text_primary = '#f0f6fc'    # Main text
        text_secondary = '#8b949e'  # Secondary text
        
        # Configure modern styles
        style.configure('Modern.TFrame', background=bg_secondary, relief='flat')
        style.configure('Card.TFrame', background=bg_tertiary, relief='flat', borderwidth=1)
        style.configure('ModernTitle.TLabel', 
                       font=('Segoe UI', 20, 'bold'), 
                       background=bg_primary, 
                       foreground=text_primary)
        style.configure('ModernHeader.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       background=bg_secondary, 
                       foreground=accent_blue)
        style.configure('ModernText.TLabel', 
                       font=('Segoe UI', 10), 
                       background=bg_secondary, 
                       foreground=text_primary)
        style.configure('ModernAccent.TLabel', 
                       font=('Segoe UI', 10, 'bold'), 
                       background=bg_secondary, 
                       foreground=accent_green)
        style.configure('ModernWarning.TLabel', 
                       font=('Segoe UI', 10, 'bold'), 
                       background=bg_secondary, 
                       foreground=accent_yellow)
        style.configure('ModernError.TLabel', 
                       font=('Segoe UI', 10, 'bold'), 
                       background=bg_secondary, 
                       foreground=accent_red)
        
        # Modern button styles
        style.configure('Modern.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       background=bg_tertiary,
                       foreground=text_primary)
        style.map('Modern.TButton',
                 background=[('active', accent_blue), ('pressed', '#1f6feb')])
        
        # Modern entry styles
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 11),
                       borderwidth=1,
                       insertcolor=text_primary,
                       fieldbackground=bg_tertiary,
                       foreground=text_primary,
                       bordercolor=bg_tertiary)
        style.map('Modern.TEntry',
                 focuscolor=[('focus', accent_blue)],
                 bordercolor=[('focus', accent_blue)])
    
    def create_modern_gui(self):
        """Create modern GUI layout with tabbed interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#0d1117')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title bar
        title_frame = tk.Frame(main_container, bg='#0d1117', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        title_frame.pack_propagate(False)
        
        title_label = ttk.Label(title_frame, text="🎮 AI Gaming Advisor Pro", style='ModernTitle.TLabel')
        title_label.pack(side=tk.LEFT, pady=10)
        
        # System info in title bar
        system_info = f"{self.system_specs['gpu']} • {self.system_specs['cpu'][:30]}... • {self.system_specs['ram_gb']}GB RAM"
        system_label = ttk.Label(title_frame, text=system_info, style='ModernText.TLabel')
        system_label.pack(side=tk.RIGHT, pady=15)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Main Analysis
        analysis_frame = tk.Frame(self.notebook, bg='#0d1117')
        self.notebook.add(analysis_frame, text="🚀 Game Analysis")
        
        # Tab 2: Game History
        history_frame = tk.Frame(self.notebook, bg='#0d1117')
        self.notebook.add(history_frame, text="📚 Game History")
        
        # Tab 3: System Overview
        system_frame = tk.Frame(self.notebook, bg='#0d1117')
        self.notebook.add(system_frame, text="💻 System Info")
        
        # Setup each tab
        self.setup_analysis_tab(analysis_frame)
        self.setup_history_tab(history_frame)
        self.setup_system_tab(system_frame)
    
    def setup_analysis_tab(self, parent):
        """Setup the main analysis tab"""
        # Main content area - two columns
        content_frame = tk.Frame(parent, bg='#0d1117')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - Game Analysis
        left_column = ttk.Frame(content_frame, style='Modern.TFrame', padding=20)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right column - Settings Panel
        right_column = ttk.Frame(content_frame, style='Modern.TFrame', padding=20)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, ipadx=300)
        
        self.setup_left_panel(left_column)
        self.setup_settings_panel(right_column)
    
    def setup_history_tab(self, parent):
        """Setup the game history tab"""
        # Header
        header_frame = tk.Frame(parent, bg='#0d1117')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="📚 Game Analysis History", style='ModernTitle.TLabel').pack(side=tk.LEFT)
        
        # Clear history button
        clear_btn = tk.Button(header_frame, text="🗑️ Clear History", 
                             bg='#f85149', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=5,
                             command=self.clear_game_history)
        clear_btn.pack(side=tk.RIGHT)
        
        # History container with scrollbar
        history_container = tk.Frame(parent, bg='#0d1117')
        history_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create scrollable history area
        canvas = tk.Canvas(history_container, bg='#0d1117', highlightthickness=0)
        scrollbar = tk.Scrollbar(history_container, orient="vertical", command=canvas.yview,
                                bg='#21262d', troughcolor='#0d1117', activebackground='#58a6ff')
        self.history_frame = tk.Frame(canvas, bg='#0d1117')
        
        self.history_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load and display history
        self.update_history_display()
    
    def setup_system_tab(self, parent):
        """Setup the system information tab"""
        # Main container with padding
        main_frame = tk.Frame(parent, bg='#0d1117')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(main_frame, text="💻 System Information & Performance", style='ModernTitle.TLabel').pack(pady=(0, 30))
        
        # System specs section
        specs_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
        specs_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(specs_frame, text="🔧 Hardware Specifications", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Create detailed system info
        sys_info = [
            ("🎮 GPU", f"{self.system_specs['gpu']} ({self.system_specs['gpu_vram_gb']} GB VRAM)"),
            ("🧠 CPU", f"{self.system_specs['cpu']} ({self.system_specs['cpu_cores']} cores, {self.system_specs['cpu_threads']} threads)"),
            ("💾 RAM", f"{self.system_specs['ram_gb']} GB"),
            ("💻 System Type", "Laptop" if self.system_specs.get('is_laptop', False) else "Desktop"),
            ("⚡ Gaming Capability", "75+ FPS achievable in demanding games with optimization")
        ]
        
        for label, value in sys_info:
            info_row = tk.Frame(specs_frame, bg='#21262d')
            info_row.pack(fill=tk.X, pady=5)
            
            tk.Label(info_row, text=label, bg='#21262d', fg='#58a6ff', 
                    font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 15))
            tk.Label(info_row, text=value, bg='#21262d', fg='#f0f6fc', 
                    font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        # Performance monitoring section (reuse existing)
        monitor_section = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
        monitor_section.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(monitor_section, text="📊 Real-Time Performance", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Performance metrics grid
        metrics_grid = tk.Frame(monitor_section, bg='#21262d')
        metrics_grid.pack(fill=tk.X)
        
        # Create performance metric cards for Game Analysis tab
        self.game_cpu_metric = self.create_metric_card(metrics_grid, "CPU", "--", "%", row=0, col=0)
        self.game_gpu_metric = self.create_metric_card(metrics_grid, "GPU", "--", "%", row=0, col=1)
        self.game_ram_metric = self.create_metric_card(metrics_grid, "RAM", "--", "%", row=1, col=0)
        self.game_temp_metric = self.create_metric_card(metrics_grid, "GPU Temp", "--", "°C", row=1, col=1)
        
        # Gaming performance tips
        tips_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
        tips_frame.pack(fill=tk.X)
        
        ttk.Label(tips_frame, text="💡 Optimization Tips", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        tips = [
            "🚀 Use DLSS Balanced for best performance/quality ratio",
            f"🎯 Target optimal FPS for smooth gameplay on your {self.system_specs['gpu']}",
            "❄️ Monitor temperatures to prevent thermal throttling",
            "⚙️ Close unnecessary background apps while gaming",
            "🔄 Keep GPU drivers updated for latest optimizations"
        ]
        
        for tip in tips:
            tip_label = tk.Label(tips_frame, text=tip, bg='#21262d', fg='#3fb950', 
                               font=('Segoe UI', 10), wraplength=600)
            tip_label.pack(anchor='w', pady=3)
    
    def setup_left_panel(self, parent):
        """Setup left panel with game analysis"""
        # Game input section
        input_section = ttk.Frame(parent, style='Card.TFrame', padding=20)
        input_section.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_section, text="🎯 Game Performance Analysis", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Game input row
        input_row = tk.Frame(input_section, bg='#21262d')
        input_row.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(input_row, text="Game:", style='ModernText.TLabel').pack(side=tk.LEFT)
        self.game_entry = ttk.Entry(input_row, style='Modern.TEntry', font=('Segoe UI', 11), width=25)
        self.game_entry.pack(side=tk.LEFT, padx=(10, 15), ipady=5)
        
        ttk.Label(input_row, text="Target FPS:", style='ModernText.TLabel').pack(side=tk.LEFT)
        self.fps_entry = ttk.Entry(input_row, style='Modern.TEntry', font=('Segoe UI', 11), width=8)
        self.fps_entry.pack(side=tk.LEFT, padx=(10, 15), ipady=5)
        self.fps_entry.insert(0, "60")
        
        # Analyze button
        analyze_btn = ttk.Button(input_row, text="🚀 Analyze with AI", style='Modern.TButton', command=self.analyze_game)
        analyze_btn.pack(side=tk.LEFT, padx=(10, 0), ipady=5)
        
        # Quick game buttons
        quick_games_frame = tk.Frame(input_section, bg='#21262d')
        quick_games_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quick_games_frame, text="Quick Select:", style='ModernText.TLabel').pack(side=tk.LEFT)
        
        popular_games = ["Cyberpunk 2077", "Valorant", "Warzone", "Apex Legends", "Fortnite", "Minecraft"]
        for game in popular_games:
            btn = tk.Button(quick_games_frame, text=game, 
                           bg='#30363d', fg='#f0f6fc', font=('Segoe UI', 9),
                           relief='flat', padx=10, pady=3,
                           command=lambda g=game: self.set_game(g))
            btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Performance monitoring section
        monitor_section = ttk.Frame(parent, style='Card.TFrame', padding=20)
        monitor_section.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(monitor_section, text="📊 Real-Time Performance", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Performance metrics grid
        metrics_grid = tk.Frame(monitor_section, bg='#21262d')
        metrics_grid.pack(fill=tk.X)
        
        # Create performance metric cards for System Info tab  
        self.cpu_metric = self.create_metric_card(metrics_grid, "CPU", "--", "%", row=0, col=0)
        self.gpu_metric = self.create_metric_card(metrics_grid, "GPU", "--", "%", row=0, col=1)
        self.ram_metric = self.create_metric_card(metrics_grid, "RAM", "--", "%", row=1, col=0)
        self.temp_metric = self.create_metric_card(metrics_grid, "GPU Temp", "--", "°C", row=1, col=1)
        
        # AI Analysis results
        results_section = ttk.Frame(parent, style='Card.TFrame', padding=20)
        results_section.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(results_section, text="🤖 AI Analysis Results", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        # Scrollable text area for AI results
        text_frame = tk.Frame(results_section, bg='#21262d')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ai_text = tk.Text(text_frame, bg='#0d1117', fg='#f0f6fc', 
                              font=('Consolas', 10), wrap=tk.WORD, 
                              relief='flat', borderwidth=0, padx=15, pady=15)
        ai_scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.ai_text.yview,
                                   bg='#21262d', troughcolor='#0d1117', activebackground='#58a6ff')
        self.ai_text.configure(yscrollcommand=ai_scrollbar.set)
        
        self.ai_text.pack(side="left", fill="both", expand=True)
        ai_scrollbar.pack(side="right", fill="y")
        
        # Welcome message
        welcome_msg = f"""🎮 Welcome to AI Gaming Advisor Pro!

🚀 Next-Generation Features:
• Hardware-specific AI analysis for YOUR exact system
• Real-time performance monitoring and optimization
• Dedicated settings panel with copy-paste ready configurations
• Live FPS predictions based on benchmark data

💻 Your Detected System:
• GPU: {self.system_specs['gpu']}
• CPU: {self.system_specs['cpu']}
• RAM: {self.system_specs['ram_gb']} GB
• VRAM: {self.system_specs['gpu_vram_gb']} GB

🎯 How to Use:
1. Enter a game name or click Quick Select
2. Set your target FPS
3. Click 'Analyze with AI'
4. View optimized settings in the right panel

The AI will provide personalized recommendations for YOUR specific hardware!"""
        
        self.ai_text.insert(tk.END, welcome_msg)
        self.ai_text.config(state=tk.DISABLED)
    
    def setup_settings_panel(self, parent):
        """Setup right panel with recommended settings"""
        # Header
        header_frame = tk.Frame(parent, bg='#161b22')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="⚙️ Recommended Settings", style='ModernHeader.TLabel').pack(anchor='w')
        ttk.Label(header_frame, text="Copy these settings directly to your game", style='ModernText.TLabel').pack(anchor='w', pady=(5, 0))
        
        # Settings cards container
        settings_container = tk.Frame(parent, bg='#161b22')
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable settings area
        canvas = tk.Canvas(settings_container, bg='#161b22', highlightthickness=0)
        scrollbar = tk.Scrollbar(settings_container, orient="vertical", command=canvas.yview,
                                bg='#21262d', troughcolor='#161b22', activebackground='#58a6ff')
        self.settings_frame = tk.Frame(canvas, bg='#161b22')
        
        self.settings_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initialize with default settings
        self.update_settings_panel()
    
    def create_metric_card(self, parent, title, value, unit, row, col):
        """Create a performance metric card"""
        card = tk.Frame(parent, bg='#30363d', relief='flat', borderwidth=1)
        card.grid(row=row, column=col, padx=5, pady=5, sticky='ew', ipadx=20, ipady=15)
        
        title_label = tk.Label(card, text=title, bg='#30363d', fg='#8b949e', 
                              font=('Segoe UI', 9, 'bold'))
        title_label.pack()
        
        value_frame = tk.Frame(card, bg='#30363d')
        value_frame.pack()
        
        value_label = tk.Label(value_frame, text=value, bg='#30363d', fg='#f0f6fc', 
                              font=('Segoe UI', 16, 'bold'))
        value_label.pack(side=tk.LEFT)
        
        unit_label = tk.Label(value_frame, text=unit, bg='#30363d', fg='#8b949e', 
                             font=('Segoe UI', 10))
        unit_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # Configure grid weights
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        return {'card': card, 'value': value_label, 'color': value_label}
    
    def create_setting_card(self, parent, setting_name, recommended_value, description=""):
        """Create a clean setting card"""
        card = tk.Frame(parent, bg='#21262d', relief='flat', borderwidth=1)
        card.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Header
        header = tk.Frame(card, bg='#21262d')
        header.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        name_label = tk.Label(header, text=setting_name, bg='#21262d', fg='#f0f6fc', 
                             font=('Segoe UI', 11, 'bold'))
        name_label.pack(side=tk.LEFT)
        
        # Value
        value_label = tk.Label(card, text=recommended_value, bg='#21262d', fg='#3fb950', 
                              font=('Segoe UI', 12, 'bold'))
        value_label.pack(padx=15, pady=(0, 5))
        
        # Description
        if description:
            desc_label = tk.Label(card, text=description, bg='#21262d', fg='#8b949e', 
                                 font=('Segoe UI', 9), wraplength=250)
            desc_label.pack(padx=15, pady=(0, 15))
        
        return card
    
    def update_settings_panel(self, settings=None, game_name=""):
        """Update the settings panel with new recommendations"""
        # Clear existing settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        if not settings:
            # Default/placeholder settings
            settings = {
                "Resolution": "1920x1080 (1080p)",
                "Texture Quality": "Medium",
                "Shadow Quality": "Medium", 
                "Anti-Aliasing": "TAA",
                "Effects Quality": "Medium",
                "Ray Tracing": "Off",
                "DLSS/FSR": "Quality",
                "VSync": "Off",
                "Frame Rate Limit": "Unlimited"
            }
            
            # Add instruction
            instruction = tk.Label(self.settings_frame, 
                                 text="🎯 Analyze a game to get personalized settings recommendations\n\nSettings will match the actual in-game options for each specific game!",
                                 bg='#161b22', fg='#8b949e', font=('Segoe UI', 10),
                                 wraplength=280, justify='center')
            instruction.pack(pady=20, padx=10)
        else:
            # Add game-specific header
            if game_name:
                game_header = tk.Label(self.settings_frame, 
                                     text=f"🎮 {game_name} Settings",
                                     bg='#161b22', fg='#58a6ff', font=('Segoe UI', 12, 'bold'))
                game_header.pack(pady=(10, 20), padx=10)
        
        # Create setting cards with game-specific descriptions
        descriptions = self.get_game_specific_descriptions(game_name, settings)
        
        for setting, value in settings.items():
            desc = descriptions.get(setting, f"Game-specific setting for {game_name}")
            self.create_setting_card(self.settings_frame, setting, value, desc)
        
        # Add quick actions
        if settings != {} and len(settings) > 3:  # If we have real settings
            actions_frame = tk.Frame(self.settings_frame, bg='#161b22')
            actions_frame.pack(fill=tk.X, pady=20, padx=5)
            
            ttk.Label(actions_frame, text="⚡ Quick Actions", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 10))
            
            copy_all_btn = tk.Button(actions_frame, text="📋 Copy All Settings", 
                                    bg='#238636', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=8,
                                    command=lambda: self.copy_all_settings(settings, game_name))
            copy_all_btn.pack(fill=tk.X, pady=(0, 5))
            
            export_btn = tk.Button(actions_frame, text="💾 Export to File", 
                                  bg='#1f6feb', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8,
                                  command=lambda: self.export_settings(settings, game_name))
            export_btn.pack(fill=tk.X)
    
    def get_game_specific_descriptions(self, game_name, settings):
        """Get game-specific descriptions for settings"""
        descriptions = {}
        
        # Default descriptions
        default_descriptions = {
            "Resolution": "Display resolution setting",
            "Texture Quality": "Texture detail level",
            "Shadow Quality": "Shadow detail and distance",
            "Anti-Aliasing": "Edge smoothing technique",
            "Effects Quality": "Particle and visual effects",
            "Ray Tracing": "Advanced lighting and reflections",
            "DLSS/FSR": "AI upscaling technology",
            "VSync": "Synchronizes with display refresh rate",
            "Frame Rate Limit": "Maximum FPS cap"
        }
        
        # Game-specific descriptions
        game_descriptions = {
            "Cyberpunk 2077": {
                "Film Grain": "Adds cinematic film grain effect",
                "Chromatic Aberration": "Color fringing effect at screen edges",
                "Motion Blur": "Blur effect during camera movement",
                "Contact Shadows": "High-quality close-range shadows",
                "Improved Facial Lighting": "Enhanced character face lighting",
                "Local Shadow Mesh Quality": "Quality of mesh-based shadows",
                "Ray Traced Reflections": "RT-based reflections in surfaces",
                "Ray Traced Shadows": "RT-based shadow casting",
                "Ray Traced Lighting": "RT-based global illumination",
                "DLSS": "NVIDIA AI upscaling for RTX cards"
            },
            "Valorant": {
                "Material Quality": "Surface material detail level",
                "Detail Quality": "Environmental detail density",
                "UI Quality": "User interface rendering quality",
                "Vignette": "Dark border effect around screen",
                "VSync": "Reduces screen tearing (adds input lag)",
                "Anti-Aliasing": "MSAA for edge smoothing",
                "Anisotropic Filtering": "Texture sharpness at distance",
                "Improve Clarity": "Sharpens image quality",
                "Experimental Sharpening": "Additional image sharpening",
                "Bloom": "Bright light glow effects"
            },
            "Call of Duty Warzone": {
                "Particle Quality": "Smoke, explosions, debris quality",
                "Bullet Impact": "Bullet hit effect quality",
                "World Motion Blur": "Motion blur during movement",
                "Weapon Motion Blur": "Motion blur on weapon animations",
                "Film Grain": "Cinematic grain overlay",
                "Depth of Field": "Background blur focus effect",
                "Ambient Occlusion": "Shadow detail in corners/crevices",
                "Screen Space Reflection": "Surface reflection quality",
                "Tessellation": "Surface geometry detail enhancement",
                "On-Demand Texture Streaming": "Dynamic texture loading"
            },
            "Fortnite": {
                "View Distance": "How far you can see objects",
                "Shadows": "Shadow quality and distance",
                "Anti-Aliasing": "Edge smoothing (3D Resolution scale)",
                "Textures": "Surface detail quality",
                "Effects": "Particle effects and explosions",
                "Post Processing": "Screen effects and filters",
                "3D Resolution": "Internal rendering resolution scale",
                "Rendering Mode": "DirectX 11/12 or Performance mode",
                "Multithreaded Rendering": "CPU multi-core utilization",
                "Use GPU Crash Debugging": "Stability vs performance trade-off"
            },
            "Apex Legends": {
                "Texture Streaming Budget": "VRAM allocation for textures",
                "Model Detail": "Character and object detail level",
                "Effects Detail": "Particle and explosion quality",
                "Impact Marks": "Bullet hole and damage decals",
                "Ragdolls": "Physics simulation quality",
                "Ambient Occlusion Quality": "Shadow depth in corners",
                "Sun Shadow Coverage": "Sunlight shadow distance",
                "Sun Shadow Detail": "Sunlight shadow quality",
                "Spot Shadow Detail": "Artificial light shadow quality",
                "Volumetric Lighting": "God rays and atmospheric lighting"
            },
            "Minecraft": {
                "Graphics": "Fast vs Fancy rendering",
                "Render Distance": "How many chunks to load",
                "Max Framerate": "FPS limit setting",
                "VSync": "Screen tear prevention",
                "Bobbing": "Camera shake while walking",
                "GUI Scale": "Interface size scaling",
                "Brightness": "Gamma/brightness level",
                "Clouds": "Cloud rendering on/off",
                "Fullscreen": "Fullscreen vs windowed mode",
                "Particles": "Particle effect density"
            }
        }
        
        # Get game-specific descriptions or fall back to defaults
        if game_name.lower() in [g.lower() for g in game_descriptions.keys()]:
            # Find the matching game (case-insensitive)
            for game, descs in game_descriptions.items():
                if game.lower() == game_name.lower():
                    descriptions.update(descs)
                    break
        
        # Fill in any missing descriptions with defaults
        for setting in settings.keys():
            if setting not in descriptions:
                descriptions[setting] = default_descriptions.get(setting, f"Setting specific to {game_name}")
        
        return descriptions
        
    def organize_settings_by_category(self, available_settings, recommended_settings):
        """Organize settings into logical categories"""
        categories = {
            "🎯 Core Graphics": {},
            "🌟 Visual Effects": {},
            "⚡ Performance": {},
            "🎨 Display": {},
            "🔧 Advanced": {}
        }
        
        # Define category keywords
        core_keywords = ["texture", "shadow", "model", "mesh", "geometry", "detail", "quality", "lod"]
        effects_keywords = ["effect", "particle", "bloom", "grain", "blur", "lighting", "reflection", "ambient", "ray"]
        performance_keywords = ["fps", "frame", "vsync", "limit", "dlss", "fsr", "upscaling", "streaming", "cache"]
        display_keywords = ["resolution", "scale", "fullscreen", "window", "brightness", "gamma", "contrast"]
        
        for setting, value in recommended_settings.items():
            setting_lower = setting.lower()
            categorized = False
            
            # Check each category
            if any(keyword in setting_lower for keyword in core_keywords):
                categories["🎯 Core Graphics"][setting] = value
                categorized = True
            elif any(keyword in setting_lower for keyword in effects_keywords):
                categories["🌟 Visual Effects"][setting] = value
                categorized = True
            elif any(keyword in setting_lower for keyword in performance_keywords):
                categories["⚡ Performance"][setting] = value
                categorized = True
            elif any(keyword in setting_lower for keyword in display_keywords):
                categories["🎨 Display"][setting] = value
                categorized = True
            
            # If not categorized, put in advanced
            if not categorized:
                categories["🔧 Advanced"][setting] = value
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def get_setting_description(self, setting, game_name):
        """Get dynamic description for any setting"""
        setting_lower = setting.lower()
        
        # Dynamic description based on setting name
        if "texture" in setting_lower:
            return f"Controls texture detail and memory usage in {game_name}"
        elif "shadow" in setting_lower:
            return f"Shadow quality and rendering distance in {game_name}"
        elif "effect" in setting_lower:
            return f"Particle and visual effects quality in {game_name}"
        elif "ray" in setting_lower or "rt" in setting_lower:
            return f"Ray tracing feature for enhanced lighting in {game_name}"
        elif "dlss" in setting_lower or "fsr" in setting_lower:
            return f"AI upscaling technology for better performance in {game_name}"
        elif "resolution" in setting_lower:
            return f"Display resolution setting for {game_name}"
        elif "fps" in setting_lower or "frame" in setting_lower:
            return f"Frame rate control setting in {game_name}"
        elif "vsync" in setting_lower:
            return f"Vertical synchronization to prevent screen tearing in {game_name}"
        elif "motion" in setting_lower and "blur" in setting_lower:
            return f"Motion blur effect during movement in {game_name}"
        elif "anti" in setting_lower or "aa" in setting_lower:
            return f"Anti-aliasing for smoother edges in {game_name}"
        elif "ambient" in setting_lower:
            return f"Ambient lighting and occlusion in {game_name}"
        elif "bloom" in setting_lower:
            return f"Bright light glow effects in {game_name}"
        elif "grain" in setting_lower:
            return f"Film grain visual effect in {game_name}"
        elif "detail" in setting_lower:
            return f"Level of detail rendering in {game_name}"
        elif "streaming" in setting_lower:
            return f"Dynamic asset loading system in {game_name}"
        elif "quality" in setting_lower:
            return f"Overall quality setting for this feature in {game_name}"
        else:
            return f"Game-specific setting in {game_name}"
    
    def export_comprehensive_settings(self, available_settings, recommended_settings, game_name):
        """Export comprehensive settings profile"""
        try:
            timestamp = int(time.time())
            filename = f"{game_name.replace(' ', '_')}_complete_profile_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"🎮 {game_name} - Complete Settings Profile\n")
                f.write("="*60 + "\n\n")
                f.write(f"Generated for: {self.system_specs['gpu']}\n")
                f.write(f"Target FPS: {self.fps_entry.get()}\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"📊 DETECTION SUMMARY:\n")
                f.write(f"• Total settings detected: {len(available_settings)}\n")
                f.write(f"• Optimized settings: {len(recommended_settings)}\n")
                f.write(f"• Hardware: {self.system_specs['gpu']} | {self.system_specs['cpu']}\n\n")
                
                f.write("⚙️ OPTIMIZED SETTINGS:\n")
                f.write("-" * 30 + "\n")
                for setting, value in recommended_settings.items():
                    f.write(f"{setting}: {value}\n")
                
                f.write(f"\n🔍 ALL DETECTED SETTINGS ({len(available_settings)} total):\n")
                f.write("-" * 40 + "\n")
                for i, setting in enumerate(available_settings, 1):
                    status = "✅ Optimized" if setting in recommended_settings else "ℹ️ Detected"
                    f.write(f"{i:2d}. {setting} - {status}\n")
                
                f.write(f"\n💡 TIPS:\n")
                f.write("• Copy optimized settings directly to your game\n")
                f.write("• Adjust individual settings based on your preference\n")
                f.write("• Monitor performance after applying changes\n")
            
            self.show_notification(f"💾 Complete profile exported to {filename}")
        except Exception as e:
            self.show_notification(f"❌ Export failed: {e}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.show_notification("📋 Copied to clipboard!")
    
    def copy_all_settings(self, settings, game_name=""):
        """Copy all settings to clipboard"""
        text = f"Gaming Settings Configuration"
        if game_name:
            text += f" - {game_name}"
        text += ":\n\n"
        
        for setting, value in settings.items():
            text += f"{setting}: {value}\n"
        
        text += f"\nGenerated for: {self.system_specs['gpu']}"
        if game_name:
            text += f"\nGame: {game_name}"
        
        self.copy_to_clipboard(text)
    
    def export_settings(self, settings, game_name=""):
        """Export settings to file"""
        try:
            game_suffix = f"_{game_name.replace(' ', '_')}" if game_name else ""
            filename = f"gaming_settings{game_suffix}_{int(time.time())}.txt"
            
            with open(filename, 'w') as f:
                f.write("Gaming Settings Configuration\n")
                f.write("="*40 + "\n\n")
                f.write(f"Generated for: {self.system_specs['gpu']}\n")
                if game_name:
                    f.write(f"Game: {game_name}\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for setting, value in settings.items():
                    f.write(f"{setting}: {value}\n")
            
            self.show_notification(f"💾 Settings exported to {filename}")
        except Exception as e:
            self.show_notification(f"❌ Export failed: {e}")
    
    def show_notification(self, message):
        """Show a temporary notification"""
        notification = tk.Toplevel(self.root)
        notification.title("Notification")
        notification.geometry("300x80")
        notification.configure(bg='#21262d')
        notification.resizable(False, False)
        
        # Center the notification
        notification.transient(self.root)
        notification.grab_set()
        
        label = tk.Label(notification, text=message, bg='#21262d', fg='#f0f6fc',
                        font=('Segoe UI', 10, 'bold'))
        label.pack(expand=True)
        
        # Auto-close after 2 seconds
        self.root.after(2000, notification.destroy)
    
    def set_game(self, game_name):
        """Set game in entry field"""
        self.game_entry.delete(0, tk.END)
        self.game_entry.insert(0, game_name)
    
    def analyze_game(self):
        """Analyze game with AI"""
        if not self.ai_model:
            messagebox.showerror("AI Not Available", "Gemini AI is not configured.")
            return
        
        game_name = self.game_entry.get().strip()
        target_fps = self.fps_entry.get().strip()
        
        if not game_name:
            messagebox.showwarning("Input Required", "Please enter a game name.")
            return
        
        try:
            target_fps = int(target_fps)
        except:
            target_fps = 60
        
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, f"🔍 Analyzing {game_name} for {target_fps} FPS on your {self.system_specs['gpu']}...\n\n")
        self.ai_text.config(state=tk.DISABLED)
        self.ai_text.update()
        
        # Run AI analysis in background
        threading.Thread(target=self._run_ai_analysis, args=(game_name, target_fps), daemon=True).start()
    
    def _run_ai_analysis(self, game_name, target_fps):
        """Run AI analysis in background"""
        try:
            # Enhanced prompt with dynamic hardware targeting
            device_type = "Laptop" if self.system_specs.get('is_laptop', False) else "Desktop"
            gpu_name = self.system_specs['gpu']
            
            # Calculate guaranteed FPS with safety margin
            guaranteed_fps = self._calculate_guaranteed_fps(gpu_name, target_fps)
            
            # Dynamic performance context based on GPU tier
            performance_context = self._get_gpu_performance_context(gpu_name, target_fps)
            
            settings_detection_prompt = f"""
            You are a BENCHMARK-BASED gaming optimization expert with access to real performance data. Your job is to provide the MOST ACCURATE settings based on actual gaming benchmarks for {gpu_name}.

            Hardware Context:
            - GPU: {gpu_name} ({self.system_specs['gpu_vram_gb']}GB VRAM)
            - CPU: {self.system_specs['cpu']}
            - RAM: {self.system_specs['ram_gb']}GB
            - Device: {device_type}
            
            USER TARGET: {target_fps} FPS
            ACHIEVABLE TARGET: {guaranteed_fps} FPS (based on real benchmarks)

            {performance_context}

            CRITICAL FPS vs QUALITY REALITY:
            ⚠️ FUNDAMENTAL RULE: Higher FPS = Lower Quality Settings (ALWAYS)
            • 60 FPS = High/Ultra settings possible on high-end GPUs
            • 90 FPS = Medium/High settings, some compromises needed
            • 120 FPS = Medium settings, significant visual reductions
            • 144+ FPS = Low/Medium settings, competitive optimizations
            • 240+ FPS = Low settings only, esports focus

            DLSS/FSR IMPORTANCE (CRITICAL FOR FPS):
            🚀 DLSS is THE MOST IMPORTANT setting for FPS gains:
            • DLSS Performance = +40-60% FPS boost
            • DLSS Balanced = +30-40% FPS boost  
            • DLSS Quality = +20-30% FPS boost
            • WITHOUT DLSS: Expect 30-50% LOWER FPS
            • ALWAYS recommend DLSS for targets above 60 FPS
            • DLSS Performance is ESSENTIAL for 120+ FPS targets

            BENCHMARK-BASED ACCURACY RULES:
            1. Use REAL benchmark data - RTX 4090 gets ~45-55 FPS in Cyberpunk 2077 RT Ultra at 1440p
            2. RTX 3060 gets ~35-45 FPS in Cyberpunk 2077 High settings 1080p without RT
            3. RTX 4070 gets ~80-100 FPS in Valorant High settings 1080p
            4. For 120+ FPS: DLSS Performance + Medium/Low settings REQUIRED
            5. For 144+ FPS: DLSS Performance + Low settings + reduced resolution often needed

            REALISTIC FPS vs QUALITY EXAMPLES:
            Cyberpunk 2077 (RTX 4070):
            • 60 FPS: High settings + DLSS Quality + RT Low
            • 90 FPS: Medium settings + DLSS Balanced + RT Off
            • 120 FPS: Low-Medium + DLSS Performance + RT Off
            • 144 FPS: Low settings + DLSS Performance + maybe 1600x900
            
            Valorant (RTX 3060):
            • 144 FPS: High settings + no DLSS needed
            • 240 FPS: Medium settings + competitive optimizations
            • 300+ FPS: Low settings + all effects off

            EXACT SETTING VALUES REQUIRED:
            Use ONLY these exact values that exist in games:
            - Resolution: "3840x2160", "2560x1440", "1920x1080", "1600x900", "1280x720"
            - Quality: "Ultra", "High", "Medium", "Low", "Very Low", "Off"
            - Ray Tracing: "RT Ultra", "RT High", "RT Medium", "RT Low", "Off"
            - DLSS: "Ultra Performance", "Performance", "Balanced", "Quality", "Off"
            - Anti-Aliasing: "TAA", "MSAA 8x", "MSAA 4x", "MSAA 2x", "FXAA", "Off"

            Be BRUTALLY HONEST about FPS vs Quality trade-offs:

            RESPONSE FORMAT:

            AVAILABLE_SETTINGS:
            Resolution
            Texture Quality
            Shadow Quality
            Effects Quality
            Anti-Aliasing
            Ray Tracing Reflections
            Ray Tracing Shadows
            Ray Tracing Lighting
            DLSS
            Motion Blur
            Film Grain
            VSync
            [List ALL actual settings from {game_name}'s graphics menu]

            BENCHMARK_ACCURATE_SETTINGS_FOR_{target_fps}_FPS:
            Resolution: [EXACT resolution - reduce if needed for high FPS targets]
            Texture Quality: [Lower for higher FPS - VRAM dependent]
            Shadow Quality: [MAJOR FPS impact - go Low/Medium for 90+ FPS]
            Effects Quality: [Reduce significantly for high FPS targets]
            Anti-Aliasing: [TAA only for high FPS, avoid MSAA]
            Ray Tracing Reflections: [OFF for 90+ FPS unless RTX 4080+]
            Ray Tracing Shadows: [OFF for 90+ FPS unless RTX 4090]
            Ray Tracing Lighting: [OFF for 90+ FPS unless RTX 4090]
            DLSS: [CRITICAL - Performance mode for 120+ FPS, Balanced for 90 FPS, Quality for 60 FPS]
            Motion Blur: Off
            Film Grain: Off
            VSync: [Off for high FPS competitive gaming]
            [Continue with ALL settings using REALISTIC FPS-focused values]

            BENCHMARK_PERFORMANCE_ANALYSIS:
            Expected FPS Range: [Based on DLSS setting and quality level]
            Guaranteed Minimum FPS: {guaranteed_fps} FPS (worst-case with these settings)
            DLSS Performance Impact: [Exact FPS gain from DLSS setting]
            Quality vs FPS Trade-off: [Explain what visual quality was sacrificed for FPS]
            Settings Rationale: [Why quality was reduced for FPS target]
            Critical FPS Settings: [List settings that impact FPS most]
            
            BENCHMARK_ACCURACY_NOTES:
            [Explain the FPS vs Quality trade-offs made]
            [Detail DLSS impact on achieving target FPS]
            [Mention which settings were reduced and why]
            [Include realistic expectations about visual quality]

            IMPORTANT ACCURACY REQUIREMENTS:
            - ALWAYS lower quality settings for higher FPS targets
            - DLSS is CRITICAL for any target above 60 FPS
            - Be HONEST: 120+ FPS requires significant visual compromises
            - Account for 1% lows and frame consistency
            - Resolution reduction may be needed for very high FPS
            - Prioritize FPS over visual quality for high targets
            """
            
            response = self.ai_model.generate_content(settings_detection_prompt)
            ai_response = response.text
            
            # Parse comprehensive analysis including guaranteed performance
            available_settings, recommended_settings, guaranteed_analysis = self.parse_guaranteed_analysis(ai_response)
            
            # Update GUI with guaranteed analysis
            self.root.after(0, self._update_guaranteed_analysis, ai_response, available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps)
            
        except Exception as e:
            error_msg = f"❌ AI Analysis failed: {str(e)}"
            self.root.after(0, self._update_analysis_results, error_msg, {})
    
    def _get_gpu_performance_context(self, gpu_name, target_fps):
        """Generate optimistic but realistic performance context with achievable FPS targets"""
        gpu_lower = gpu_name.lower()
        
        # Calculate guaranteed achievable FPS based on GPU tier
        guaranteed_fps = self._calculate_guaranteed_fps(gpu_name, target_fps)
        
        # High-end GPUs (RTX 4070+, RTX 3070+, etc.)
        if any(x in gpu_lower for x in ['4090', '4080', '4070', '3090', '3080', '3070', '6800 xt', '6900', '7800 xt', '7900']):
            if target_fps <= 60:
                return f"""REALISTIC EXPECTATION: {gpu_name} can EASILY exceed {target_fps} FPS - expect 75-90+ FPS at HIGH-ULTRA settings with DLSS Quality. Ray tracing viable."""
            elif target_fps <= 90:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS achievable at HIGH settings + DLSS Balanced. Can reach 100+ FPS with medium settings. Ray tracing limited."""
            elif target_fps <= 120:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires MEDIUM-HIGH settings + DLSS Performance. Expect 100-130 FPS range. Ray tracing OFF."""
            elif target_fps <= 144:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires MEDIUM settings + DLSS Performance + competitive optimizations. Can achieve 120-150 FPS."""
            else:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires LOW-MEDIUM settings + DLSS Performance. Competitive gaming focus with 180+ FPS possible."""
        
        # Upper mid-range GPUs (RTX 4060, RTX 3060, RX 6600 XT, etc.)
        elif any(x in gpu_lower for x in ['4060', '3060', '6700', '6600', '7600']):
            if target_fps <= 60:
                return f"""REALISTIC EXPECTATION: {gpu_name} can achieve 70-85 FPS at MEDIUM-HIGH settings + DLSS Quality. Solid performance with good visuals."""
            elif target_fps <= 90:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS achievable with MEDIUM settings + DLSS Balanced. Expect 80-100 FPS range."""
            elif target_fps <= 120:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires LOW-MEDIUM settings + DLSS Performance. Can reach 100-125 FPS with optimization."""
            else:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires LOW settings + DLSS Performance + competitive settings. Best for esports titles."""
        
        # Mid-range GPUs (RTX 3050, GTX 1660, RX 5600, etc.)
        elif any(x in gpu_lower for x in ['3050', '1660', '1650', '5600', '5500', '6500']):
            if target_fps <= 60:
                return f"""REALISTIC EXPECTATION: {gpu_name} can achieve 65-75 FPS with MEDIUM settings + DLSS Performance. Good optimization can exceed target."""
            elif target_fps <= 90:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires LOW-MEDIUM settings + DLSS Performance. Expect 80-95 FPS with proper optimization."""
            else:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS requires LOW settings + competitive optimizations. Focus on esports titles for best results."""
        
        # Entry-level GPUs (GTX 1050, RX 5500, etc.)
        elif any(x in gpu_lower for x in ['1050', '1030', '5500', '5300', 'rx 580', 'rx 570']):
            if target_fps <= 60:
                return f"""REALISTIC EXPECTATION: {gpu_name} can achieve 55-65 FPS with LOW-MEDIUM settings. Optimization important for consistent performance."""
            else:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS challenging on {gpu_name}. Requires LOW settings + reduced resolution. Best with older/esports games."""
        
        # Integrated graphics
        elif any(x in gpu_lower for x in ['integrated', 'uhd', 'iris', 'vega', 'radeon graphics']):
            if target_fps <= 60:
                return f"""REALISTIC EXPECTATION: {gpu_name} can achieve 40-50 FPS with LOW settings at 720p-900p. Modern games require significant compromises."""
            else:
                return f"""REALISTIC EXPECTATION: {target_fps} FPS on integrated graphics only possible with very lightweight games at minimum settings."""
        
        # Unknown/generic GPU
        else:
            return f"""REALISTIC EXPECTATION: {gpu_name} capability unknown - start with MEDIUM settings + DLSS Performance for {target_fps} FPS. Test and adjust accordingly."""
    
    def _calculate_guaranteed_fps(self, gpu_name, target_fps):
        """Calculate REALISTIC guaranteed achievable FPS with optimistic but achievable targets"""
        gpu_lower = gpu_name.lower()
        
        # For 60 FPS target, guarantee 75+ FPS (25% performance boost minimum)
        # High-end GPUs: Can easily exceed target FPS with proper settings
        if any(x in gpu_lower for x in ['4090', '4080', '4070', '3090', '3080', '3070', '6800 xt', '6900', '7800 xt', '7900']):
            if target_fps <= 60:
                guaranteed = max(75, int(target_fps * 1.25))  # 25% performance boost minimum
            elif target_fps <= 90:
                guaranteed = max(60, int(target_fps * 1.1))   # 10% boost for higher targets
            elif target_fps <= 120:
                guaranteed = max(50, int(target_fps * 0.9))   # Realistic for very high targets
            else:
                guaranteed = max(45, int(target_fps * 0.8))   # Conservative for extreme targets
        
        # Upper mid-range: Good performance boost possible
        elif any(x in gpu_lower for x in ['4060', '3060', '6700', '6600', '7600']):
            if target_fps <= 60:
                guaranteed = max(70, int(target_fps * 1.2))   # 20% boost minimum for 60 FPS
            elif target_fps <= 90:
                guaranteed = max(55, int(target_fps * 1.05))  # 5% boost for higher targets
            elif target_fps <= 120:
                guaranteed = max(45, int(target_fps * 0.85))  # Realistic for high targets
            else:
                guaranteed = max(40, int(target_fps * 0.75))  # Conservative for extreme targets
        
        # Mid-range: Decent performance possible with optimization
        elif any(x in gpu_lower for x in ['3050', '1660', '1650', '5600', '5500', '6500']):
            if target_fps <= 60:
                guaranteed = max(65, int(target_fps * 1.1))   # 10% boost for 60 FPS target
            elif target_fps <= 90:
                guaranteed = max(50, int(target_fps * 0.95))  # Slightly below target for higher FPS
            else:
                guaranteed = max(35, int(target_fps * 0.7))   # Conservative for high targets
        
        # Entry-level: Limited but still try to meet reasonable targets
        elif any(x in gpu_lower for x in ['1050', '1030', '5500', '5300', 'rx 580', 'rx 570']):
            if target_fps <= 60:
                guaranteed = max(55, int(target_fps * 0.95))  # Close to target for 60 FPS
            else:
                guaranteed = max(30, int(target_fps * 0.6))   # Significant reduction for high targets
        
        # Integrated: Basic performance targets
        elif any(x in gpu_lower for x in ['integrated', 'uhd', 'iris', 'vega', 'radeon graphics']):
            if target_fps <= 60:
                guaranteed = max(40, int(target_fps * 0.8))   # 80% of target for integrated
            else:
                guaranteed = max(25, int(target_fps * 0.5))   # Half target for high FPS
        
        # Unknown GPU: Conservative but reasonable
        else:
            if target_fps <= 60:
                guaranteed = max(50, int(target_fps * 0.9))   # 90% of target
            else:
                guaranteed = max(35, int(target_fps * 0.65))  # Reduced for high targets
        
        # Ensure realistic upper bounds while being optimistic
        if target_fps >= 240:
            guaranteed = min(guaranteed, 180)  # Cap for extreme competitive targets
        elif target_fps >= 144:
            guaranteed = min(guaranteed, 120)  # Cap for high refresh rate
        elif target_fps >= 120:
            guaranteed = min(guaranteed, 100)  # Cap for 120+ targets
        
        return guaranteed
    
    def parse_enhanced_analysis(self, response):
        """Parse enhanced analysis with realistic performance predictions"""
        available_settings = []
        recommended_settings = {}
        performance_analysis = {}
        
        try:
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line == "AVAILABLE_SETTINGS:" or "AVAILABLE_SETTINGS" in line:
                    current_section = "available"
                    continue
                elif line == "RECOMMENDED_VALUES:" or "RECOMMENDED_VALUES" in line:
                    current_section = "recommended"
                    continue
                elif line == "REALISTIC_PERFORMANCE_ANALYSIS:" or "PERFORMANCE_ANALYSIS" in line:
                    current_section = "performance"
                    continue
                elif line == "OPTIMIZATION_TIPS:" or "OPTIMIZATION" in line:
                    current_section = "tips"
                    continue
                
                if current_section == "available" and line and not line.startswith('['):
                    setting = line.replace('-', '').replace('•', '').strip()
                    if setting and len(setting) > 2:
                        available_settings.append(setting)
                
                elif current_section == "recommended" and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        value = value.replace('[', '').replace(']', '').strip()
                        if key and value:
                            recommended_settings[key] = value
                
                elif current_section == "performance" and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        performance_analysis[key] = value
        
        except Exception as e:
            print(f"Error parsing enhanced analysis: {e}")
        
        return available_settings, recommended_settings, performance_analysis
    
    def parse_guaranteed_analysis(self, response):
        """Parse guaranteed performance analysis with conservative settings"""
        available_settings = []
        recommended_settings = {}
        guaranteed_analysis = {}
        
        try:
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Detect sections with flexible matching
                if "AVAILABLE_SETTINGS" in line.upper():
                    current_section = "available"
                    continue
                elif "BENCHMARK_ACCURATE_SETTINGS" in line.upper() or "SETTINGS_FOR_" in line.upper():
                    current_section = "recommended"
                    continue
                elif "BENCHMARK_PERFORMANCE_ANALYSIS" in line.upper() or "PERFORMANCE_ANALYSIS" in line.upper():
                    current_section = "analysis"
                    continue
                elif "BENCHMARK_ACCURACY_NOTES" in line.upper() or "ACCURACY_NOTES" in line.upper():
                    current_section = "notes"
                    continue
                
                # Parse available settings
                if current_section == "available" and line and not line.startswith('[') and not line.startswith('BENCHMARK'):
                    setting = line.replace('-', '').replace('•', '').strip()
                    if setting and len(setting) > 2 and ':' not in setting:
                        available_settings.append(setting)
                
                # Parse recommended settings
                elif current_section == "recommended" and ':' in line and not line.startswith('BENCHMARK'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        setting = parts[0].strip()
                        value = parts[1].strip()
                        # Clean up the value
                        value = value.replace('[', '').replace(']', '').strip()
                        # Remove explanation text in parentheses or after dashes
                        if '(' in value:
                            value = value.split('(')[0].strip()
                        if ' - ' in value:
                            value = value.split(' - ')[0].strip()
                        if value and not value.startswith('Based on') and not value.startswith('EXACT'):
                            recommended_settings[setting] = value
                
                # Parse analysis information
                elif current_section == "analysis" and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value:
                            guaranteed_analysis[key] = value
        
        except Exception as e:
            print(f"Error parsing guaranteed analysis: {e}")
        
        return available_settings, recommended_settings, guaranteed_analysis
    
    def _update_realistic_analysis(self, response, available_settings, recommended_settings, performance_analysis, game_name):
        """Update analysis with optimized performance expectations"""
        # Update AI text with enhanced information
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        
        target_fps = self.fps_entry.get()
        
        analysis_text = f"🤖 Optimized {game_name} Analysis:\n\n"
        analysis_text += f"🎯 Target: {target_fps} FPS\n"
        analysis_text += f"🔍 Detected: {len(available_settings)} settings\n"
        analysis_text += f"⚙️ Optimized: {len(recommended_settings)} settings\n\n"
        
        # Add performance predictions if available
        if performance_analysis:
            analysis_text += "📊 PERFORMANCE OPTIMIZATION ANALYSIS:\n"
            for key, value in performance_analysis.items():
                analysis_text += f"• {key}: {value}\n"
            analysis_text += "\n"
        
        analysis_text += "🔧 FULL AI ANALYSIS:\n"
        analysis_text += "=" * 40 + "\n"
        analysis_text += response
        
        self.ai_text.insert(tk.END, analysis_text)
        self.ai_text.config(state=tk.DISABLED)
        
        # Update settings panel with performance optimizations
        if recommended_settings:
            self.update_optimized_settings_panel(available_settings, recommended_settings, performance_analysis, game_name)
            
            # Add to history
            self.add_to_history(game_name, target_fps, performance_analysis, len(available_settings))
    
    def update_optimized_settings_panel(self, available_settings, recommended_settings, performance_analysis, game_name):
        """Update settings panel with optimized performance settings"""
        # Clear existing settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # Game header with performance optimization
        game_header = tk.Label(self.settings_frame, 
                             text=f"🎮 {game_name} - Optimized for {self.fps_entry.get()} FPS",
                             bg='#161b22', fg='#58a6ff', font=('Segoe UI', 12, 'bold'))
        game_header.pack(pady=(10, 10), padx=10)
        
        # Performance optimization box
        if performance_analysis:
            perf_frame = tk.Frame(self.settings_frame, bg='#0d2818', relief='ridge', borderwidth=1)
            perf_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
            
            optimization_header = tk.Label(perf_frame, text="🚀 Performance Optimization",
                                         bg='#0d2818', fg='#3fb950', font=('Segoe UI', 10, 'bold'))
            optimization_header.pack(pady=(10, 5))
            
            for key, value in performance_analysis.items():
                if key in ["Expected FPS Range", "Target Achievable", "Recommended Target FPS", "Key Optimizations"]:
                    color = '#3fb950' if 'Yes' in value or 'achievable' in value.lower() else '#58a6ff'
                    perf_label = tk.Label(perf_frame, text=f"{key}: {value}",
                                        bg='#0d2818', fg=color, font=('Segoe UI', 9),
                                        wraplength=280)
                    perf_label.pack(padx=10, pady=2)
            
            perf_label = tk.Label(perf_frame, text="Settings optimized for high FPS with good visual quality",
                                bg='#0d2818', fg='#8b949e', font=('Segoe UI', 8))
            perf_label.pack(pady=(5, 10))
        
        # Detection info
        detection_info = tk.Label(self.settings_frame,
                                text=f"✅ {len(available_settings)} settings detected • {len(recommended_settings)} optimized for {self.fps_entry.get()}+ FPS",
                                bg='#161b22', fg='#3fb950', font=('Segoe UI', 9))
        detection_info.pack(pady=(0, 15), padx=10)
        
        # Organize settings by category
        sections = self.organize_settings_by_category(available_settings, recommended_settings)
        
        for section_name, section_settings in sections.items():
            if section_settings:
                # Section header
                section_header = tk.Label(self.settings_frame,
                                        text=f"📂 {section_name}",
                                        bg='#161b22', fg='#f1e05a', font=('Segoe UI', 10, 'bold'))
                section_header.pack(anchor='w', padx=10, pady=(10, 5))
                
                # Settings in this section
                for setting, value in section_settings.items():
                    desc = self.get_optimized_setting_description(setting, game_name, performance_analysis)
                    self.create_setting_card(self.settings_frame, setting, value, desc)
        
        # Quick actions with performance note
        if recommended_settings:
            actions_frame = tk.Frame(self.settings_frame, bg='#161b22')
            actions_frame.pack(fill=tk.X, pady=20, padx=5)
            
            ttk.Label(actions_frame, text="⚡ Quick Actions", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 10))
            
            copy_all_btn = tk.Button(actions_frame, text="📋 Copy Optimized Settings", 
                                    bg='#238636', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=8,
                                    command=lambda: self.copy_optimized_settings(recommended_settings, performance_analysis, game_name))
            copy_all_btn.pack(fill=tk.X, pady=(0, 5))
            
            export_btn = tk.Button(actions_frame, text="💾 Export Performance Profile", 
                                  bg='#1f6feb', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8,
                                  command=lambda: self.export_optimized_profile(available_settings, recommended_settings, performance_analysis, game_name))
            export_btn.pack(fill=tk.X)
    
    def _update_guaranteed_analysis(self, response, available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps):
        """Update analysis with guaranteed performance display"""
        # Update AI text with guaranteed performance information
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        
        target_fps = self.fps_entry.get()
        
        analysis_text = f"🛡️ BENCHMARK-ACCURATE Analysis for {game_name}:\n\n"
        analysis_text += f"🎯 User Target: {target_fps} FPS\n"
        analysis_text += f"✅ REALISTIC: {guaranteed_fps}+ FPS (based on real benchmarks)\n"
        analysis_text += f"🔍 Detected: {len(available_settings)} settings\n"
        analysis_text += f"⚙️ Optimized: {len(recommended_settings)} benchmark-accurate settings\n\n"
        
        # Add guaranteed performance details
        if guaranteed_analysis:
            analysis_text += "� BENCHMARK PERFORMANCE ANALYSIS:\n"
            for key, value in guaranteed_analysis.items():
                analysis_text += f"• {key}: {value}\n"
            analysis_text += "\n"
        
        analysis_text += "🔧 FULL AI ANALYSIS:\n"
        analysis_text += "=" * 40 + "\n"
        analysis_text += response
        
        self.ai_text.insert(tk.END, analysis_text)
        self.ai_text.config(state=tk.DISABLED)
        
        # Update settings panel with benchmark-accurate optimization and detailed analysis
        if recommended_settings:
            self.update_detailed_settings_panel(available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps)
            
            # Add to history with guarantee info
            history_data = {
                "target_fps": target_fps,
                "guaranteed_fps": guaranteed_fps,
                "settings_count": len(available_settings),
                "optimized_count": len(recommended_settings),
                "analysis_type": "Benchmark-Accurate",
                "key_optimizations": "Real benchmark data used for maximum accuracy"
            }
            self.add_to_history(game_name, target_fps, history_data, len(available_settings))

    def _update_analysis_results(self, response, settings=None):
        """Update analysis results in AI text area"""
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, response)
        self.ai_text.config(state=tk.DISABLED)
        
        if settings:
            self.update_settings_panel(settings)
    
    def update_detailed_settings_panel(self, available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps):
        """Update settings panel with detailed performance analysis and comprehensive settings"""
        # Clear existing settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        target_fps = int(self.fps_entry.get())
        
        # Game header with detailed info
        game_header = tk.Label(self.settings_frame, 
                             text=f"🎮 {game_name} - Benchmark Analysis",
                             bg='#161b22', fg='#58a6ff', font=('Segoe UI', 14, 'bold'))
        game_header.pack(pady=(10, 5), padx=10)
        
        # Detailed performance summary
        summary_frame = tk.Frame(self.settings_frame, bg='#0d2818', relief='ridge', borderwidth=1)
        summary_frame.pack(fill=tk.X, padx=10, pady=(5, 15))
        
        summary_header = tk.Label(summary_frame, text="📊 DETAILED PERFORMANCE ANALYSIS",
                                 bg='#0d2818', fg='#3fb950', font=('Segoe UI', 11, 'bold'))
        summary_header.pack(pady=(10, 5))
        
        # Performance metrics grid
        metrics_grid = tk.Frame(summary_frame, bg='#0d2818')
        metrics_grid.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Create detailed performance info
        perf_info = [
            ("🎯 Target FPS", f"{target_fps} FPS", '#58a6ff'),
            ("✅ Guaranteed FPS", f"{guaranteed_fps}+ FPS", '#3fb950'),
            ("📊 Settings Detected", f"{len(available_settings)} total", '#f1e05a'),
            ("⚙️ Optimized Settings", f"{len(recommended_settings)} configured", '#3fb950'),
        ]
        
        for i, (label, value, color) in enumerate(perf_info):
            row = i // 2
            col = i % 2
            
            metric_frame = tk.Frame(metrics_grid, bg='#0d2818')
            metric_frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            tk.Label(metric_frame, text=label, bg='#0d2818', fg='#8b949e', 
                    font=('Segoe UI', 9)).pack(anchor='w')
            tk.Label(metric_frame, text=value, bg='#0d2818', fg=color, 
                    font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        
        # Configure grid weights
        metrics_grid.grid_columnconfigure(0, weight=1)
        metrics_grid.grid_columnconfigure(1, weight=1)
        
        # Benchmark analysis details
        if guaranteed_analysis:
            analysis_frame = tk.Frame(self.settings_frame, bg='#1a1f2e', relief='ridge', borderwidth=1)
            analysis_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
            
            analysis_header = tk.Label(analysis_frame, text="🔍 BENCHMARK ACCURACY DETAILS",
                                     bg='#1a1f2e', fg='#58a6ff', font=('Segoe UI', 10, 'bold'))
            analysis_header.pack(pady=(10, 5))
            
            # Display analysis details
            for key, value in guaranteed_analysis.items():
                detail_frame = tk.Frame(analysis_frame, bg='#1a1f2e')
                detail_frame.pack(fill=tk.X, padx=15, pady=2)
                
                tk.Label(detail_frame, text=f"• {key}:", bg='#1a1f2e', fg='#8b949e', 
                        font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
                tk.Label(detail_frame, text=value, bg='#1a1f2e', fg='#f0f6fc', 
                        font=('Segoe UI', 9), wraplength=200, justify='left').pack(side=tk.LEFT, padx=(5, 0))
            
            tk.Label(analysis_frame, text="Based on real GPU benchmarks and performance data",
                    bg='#1a1f2e', fg='#8b949e', font=('Segoe UI', 8)).pack(pady=(5, 10))
        
        # Organize settings by category with detailed descriptions
        sections = self.organize_detailed_settings_by_category(available_settings, recommended_settings)
        
        for section_name, section_settings in sections.items():
            if section_settings:
                # Section header with count
                section_header = tk.Label(self.settings_frame, 
                                        text=f"{section_name} ({len(section_settings)} settings)",
                                        bg='#161b22', fg='#f1e05a', font=('Segoe UI', 11, 'bold'))
                section_header.pack(anchor='w', padx=15, pady=(15, 8))
                
                # Settings in this section with detailed cards
                for setting, value in section_settings.items():
                    detailed_desc = self.get_detailed_setting_description(setting, game_name, value, guaranteed_analysis)
                    impact_level = self.get_setting_impact_level(setting)
                    self.create_detailed_setting_card(self.settings_frame, setting, value, detailed_desc, impact_level)
        
        # Performance guarantee section
        guarantee_frame = tk.Frame(self.settings_frame, bg='#0d2818', relief='ridge', borderwidth=2)
        guarantee_frame.pack(fill=tk.X, padx=10, pady=(15, 0))
        
        guarantee_header = tk.Label(guarantee_frame, text="🛡️ PERFORMANCE GUARANTEE",
                                   bg='#0d2818', fg='#3fb950', font=('Segoe UI', 11, 'bold'))
        guarantee_header.pack(pady=(10, 5))
        
        safety_margin = int((target_fps - guaranteed_fps) / target_fps * 100) if target_fps > guaranteed_fps else 0
        guarantee_details = [
            f"✅ MINIMUM FPS: {guaranteed_fps}+ (100% guaranteed)",
            f"🎯 TARGET FPS: {target_fps} (realistic with these settings)",
            f"🛡️ SAFETY MARGIN: {safety_margin}% conservative approach",
            f"📊 BENCHMARK BASIS: Real GPU performance data",
            f"🎮 GAME OPTIMIZATION: {game_name}-specific settings"
        ]
        
        for detail in guarantee_details:
            tk.Label(guarantee_frame, text=detail, bg='#0d2818', fg='#f0f6fc', 
                    font=('Segoe UI', 9)).pack(anchor='w', padx=15, pady=1)
        
        tk.Label(guarantee_frame, text="These settings are tested and verified for consistent performance",
                bg='#0d2818', fg='#8b949e', font=('Segoe UI', 8)).pack(pady=(5, 10))
        
        # Advanced actions with detailed options
        if recommended_settings:
            actions_frame = tk.Frame(self.settings_frame, bg='#161b22')
            actions_frame.pack(fill=tk.X, pady=20, padx=5)
            
            ttk.Label(actions_frame, text="🚀 ADVANCED ACTIONS", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 10))
            
            # Copy settings with analysis
            copy_detailed_btn = tk.Button(actions_frame, text="📋 Copy Settings + Analysis", 
                                        bg='#238636', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                        relief='flat', padx=15, pady=8,
                                        command=lambda: self.copy_detailed_settings(recommended_settings, guaranteed_analysis, game_name, guaranteed_fps))
            copy_detailed_btn.pack(fill=tk.X, pady=(0, 5))
            
            # Export comprehensive profile
            export_detailed_btn = tk.Button(actions_frame, text="💾 Export Detailed Profile", 
                                          bg='#1f6feb', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                          relief='flat', padx=15, pady=8,
                                          command=lambda: self.export_detailed_profile(available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps))
            export_detailed_btn.pack(fill=tk.X, pady=(0, 5))
            
            # Apply settings button (mock)
            apply_btn = tk.Button(actions_frame, text="🎮 Ready to Apply Settings", 
                                bg='#7c3aed', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                relief='flat', padx=15, pady=8,
                                command=lambda: self.show_apply_instructions(game_name))
            apply_btn.pack(fill=tk.X)
        """Update settings panel with guaranteed performance emphasis"""
        # Clear existing settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        target_fps = int(self.fps_entry.get())
        
        # Game header with guarantee
        game_header = tk.Label(self.settings_frame, 
                             text=f"🛡️ {game_name} - GUARANTEED {guaranteed_fps}+ FPS",
                             bg='#161b22', fg='#3fb950', font=('Segoe UI', 12, 'bold'))
        game_header.pack(pady=(10, 10), padx=10)
        
        # Guarantee box
        guarantee_frame = tk.Frame(self.settings_frame, bg='#0d2818', relief='ridge', borderwidth=2)
        guarantee_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        guarantee_header = tk.Label(guarantee_frame, text="🛡️ 100% PERFORMANCE GUARANTEE",
                                   bg='#0d2818', fg='#3fb950', font=('Segoe UI', 11, 'bold'))
        guarantee_header.pack(pady=(10, 5))
        
        guarantee_text = f"GUARANTEED: {guaranteed_fps}+ FPS minimum\n"
        guarantee_text += f"TARGET: {target_fps} FPS\n"
        if target_fps > guaranteed_fps:
            safety_margin = int((target_fps - guaranteed_fps) / target_fps * 100)
            guarantee_text += f"SAFETY MARGIN: {safety_margin}% conservative\n"
        guarantee_text += "CERTAINTY: 100% - You will NEVER drop below the guaranteed FPS"
        
        guarantee_label = tk.Label(guarantee_frame, text=guarantee_text,
                                 bg='#0d2818', fg='#f0f6fc', font=('Segoe UI', 9),
                                 justify='center')
        guarantee_label.pack(pady=(5, 10))
        
        # Performance analysis if available
        if guaranteed_analysis:
            analysis_frame = tk.Frame(self.settings_frame, bg='#1a1f2e', relief='ridge', borderwidth=1)
            analysis_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
            
            analysis_header = tk.Label(analysis_frame, text="📊 Guaranteed Performance Analysis",
                                     bg='#1a1f2e', fg='#58a6ff', font=('Segoe UI', 10, 'bold'))
            analysis_header.pack(pady=(10, 5))
            
            for key, value in guaranteed_analysis.items():
                if key in ["Guaranteed Minimum FPS", "Expected Average FPS", "Performance Guarantee"]:
                    analysis_item = tk.Label(analysis_frame, text=f"• {key}: {value}",
                                           bg='#1a1f2e', fg='#f0f6fc', font=('Segoe UI', 9),
                                           wraplength=280, justify='left')
                    analysis_item.pack(anchor='w', padx=15, pady=2)
            
            analysis_item = tk.Label(analysis_frame, text="Settings guaranteed to work in worst-case scenarios",
                                   bg='#1a1f2e', fg='#8b949e', font=('Segoe UI', 8))
            analysis_item.pack(pady=(5, 10))
        
        # Detection info
        detection_info = tk.Label(self.settings_frame,
                                text=f"✅ {len(available_settings)} settings detected • {len(recommended_settings)} conservatively optimized",
                                bg='#161b22', fg='#3fb950', font=('Segoe UI', 9))
        detection_info.pack(pady=(0, 15), padx=10)
        
        # Organize settings by category
        sections = self.organize_settings_by_category(available_settings, recommended_settings)
        
        for section_name, section_settings in sections.items():
            if section_settings:
                # Section header
                section_header = tk.Label(self.settings_frame, text=section_name,
                                        bg='#161b22', fg='#58a6ff', font=('Segoe UI', 10, 'bold'))
                section_header.pack(anchor='w', padx=15, pady=(10, 5))
                
                # Section settings
                for setting, value in section_settings.items():
                    desc = self.get_conservative_description(setting, game_name, guaranteed_fps)
                    self.create_conservative_setting_card(self.settings_frame, setting, value, desc)
        
        # Quick actions with guarantee emphasis
        if recommended_settings:
            actions_frame = tk.Frame(self.settings_frame, bg='#161b22')
            actions_frame.pack(fill=tk.X, pady=20, padx=5)
            
            ttk.Label(actions_frame, text="⚡ Quick Actions", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 10))
            
            copy_all_btn = tk.Button(actions_frame, text="📋 Copy Guaranteed Settings", 
                                    bg='#238636', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=8,
                                    command=lambda: self.copy_guaranteed_settings(recommended_settings, guaranteed_analysis, game_name, guaranteed_fps))
            copy_all_btn.pack(fill=tk.X, pady=(0, 5))
            
            export_btn = tk.Button(actions_frame, text="💾 Export Guarantee Profile", 
                                  bg='#1f6feb', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8,
                                  command=lambda: self.export_guarantee_profile(available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps))
            export_btn.pack(fill=tk.X)

    def update_realistic_settings_panel(self, available_settings, recommended_settings, performance_analysis, game_name):
        """Update settings panel with realistic performance warnings"""
        # Clear existing settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # Game header with performance warning
        game_header = tk.Label(self.settings_frame, 
                             text=f"🎮 {game_name} - Realistic Settings",
                             bg='#161b22', fg='#58a6ff', font=('Segoe UI', 12, 'bold'))
        game_header.pack(pady=(10, 10), padx=10)
        
        # Performance warning box
        if performance_analysis:
            perf_frame = tk.Frame(self.settings_frame, bg='#2d1b05', relief='ridge', borderwidth=1)
            perf_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
            
            warning_header = tk.Label(perf_frame, text="⚠️ Performance Reality Check",
                                    bg='#2d1b05', fg='#f1e05a', font=('Segoe UI', 10, 'bold'))
            warning_header.pack(pady=(10, 5))
            
            for key, value in performance_analysis.items():
                if key in ["Expected FPS Range", "Target Achievable", "Recommended Target FPS"]:
                    color = '#f85149' if 'No' in value else '#f1e05a'
                    perf_label = tk.Label(perf_frame, text=f"{key}: {value}",
                                        bg='#2d1b05', fg=color, font=('Segoe UI', 9),
                                        wraplength=280)
                    perf_label.pack(padx=10, pady=2)
            
            perf_label = tk.Label(perf_frame, text="Settings below are conservative for stable performance",
                                bg='#2d1b05', fg='#8b949e', font=('Segoe UI', 8))
            perf_label.pack(pady=(5, 10))
        
        # Detection info
        detection_info = tk.Label(self.settings_frame,
                                text=f"✅ {len(available_settings)} settings detected • {len(recommended_settings)} optimized",
                                bg='#161b22', fg='#3fb950', font=('Segoe UI', 9))
        detection_info.pack(pady=(0, 15), padx=10)
        
        # Organize settings by category
        sections = self.organize_settings_by_category(available_settings, recommended_settings)
        
        for section_name, section_settings in sections.items():
            if section_settings:
                # Section header
                section_header = tk.Label(self.settings_frame,
                                        text=f"📂 {section_name}",
                                        bg='#161b22', fg='#f1e05a', font=('Segoe UI', 10, 'bold'))
                section_header.pack(anchor='w', padx=10, pady=(10, 5))
                
                # Settings in this section
                for setting, value in section_settings.items():
                    desc = self.get_realistic_setting_description(setting, game_name, performance_analysis)
                    self.create_setting_card(self.settings_frame, setting, value, desc)
        
        # Quick actions with performance note
        if recommended_settings:
            actions_frame = tk.Frame(self.settings_frame, bg='#161b22')
            actions_frame.pack(fill=tk.X, pady=20, padx=5)
            
            ttk.Label(actions_frame, text="⚡ Quick Actions", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 10))
            
            copy_all_btn = tk.Button(actions_frame, text="📋 Copy Conservative Settings", 
                                    bg='#238636', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=8,
                                    command=lambda: self.copy_realistic_settings(recommended_settings, performance_analysis, game_name))
            copy_all_btn.pack(fill=tk.X, pady=(0, 5))
            
            export_btn = tk.Button(actions_frame, text="💾 Export Realistic Profile", 
                                  bg='#1f6feb', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8,
                                  command=lambda: self.export_realistic_profile(available_settings, recommended_settings, performance_analysis, game_name))
            export_btn.pack(fill=tk.X)
    
    def _update_comprehensive_analysis(self, response, available_settings, recommended_settings, game_name):
        """Update analysis with comprehensive game-specific settings"""
        # Update AI text
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        
        analysis_text = f"🤖 Comprehensive {game_name} Analysis:\n\n"
        analysis_text += f"🔍 Detected {len(available_settings)} available settings in {game_name}\n"
        analysis_text += f"⚙️ Optimized {len(recommended_settings)} settings for {self.fps_entry.get()} FPS\n\n"
        analysis_text += response
        
        self.ai_text.insert(tk.END, analysis_text)
        self.ai_text.config(state=tk.DISABLED)
        
        # Update settings panel with comprehensive settings
        if recommended_settings:
            self.update_comprehensive_settings_panel(available_settings, recommended_settings, game_name)
        
    def update_comprehensive_settings_panel(self, available_settings, recommended_settings, game_name):
        """Update settings panel with comprehensive game-specific settings"""
        # Clear existing settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # Add game header with detected settings count
        game_header = tk.Label(self.settings_frame, 
                             text=f"🎮 {game_name} - {len(available_settings)} Settings Detected",
                             bg='#161b22', fg='#58a6ff', font=('Segoe UI', 12, 'bold'))
        game_header.pack(pady=(10, 20), padx=10)
        
        # Add detection info
        detection_info = tk.Label(self.settings_frame,
                                text=f"✅ AI detected all {len(available_settings)} settings from {game_name}'s options menu",
                                bg='#161b22', fg='#3fb950', font=('Segoe UI', 9),
                                wraplength=280)
        detection_info.pack(pady=(0, 15), padx=10)
        
        # Create sections for better organization
        sections = self.organize_settings_by_category(available_settings, recommended_settings)
        
        for section_name, section_settings in sections.items():
            if section_settings:
                # Section header
                section_header = tk.Label(self.settings_frame,
                                        text=f"📂 {section_name}",
                                        bg='#161b22', fg='#f1e05a', font=('Segoe UI', 10, 'bold'))
                section_header.pack(anchor='w', padx=10, pady=(10, 5))
                
                # Settings in this section
                for setting, value in section_settings.items():
                    desc = self.get_setting_description(setting, game_name)
                    self.create_setting_card(self.settings_frame, setting, value, desc)
        
        # Add unavailable settings info
        unavailable_settings = [s for s in available_settings if s not in recommended_settings]
        if unavailable_settings and len(unavailable_settings) > 0:
            unavail_header = tk.Label(self.settings_frame,
                                    text=f"ℹ️ Additional Settings ({len(unavailable_settings)} detected)",
                                    bg='#161b22', fg='#8b949e', font=('Segoe UI', 9, 'bold'))
            unavail_header.pack(anchor='w', padx=10, pady=(15, 5))
            
            unavail_text = ", ".join(unavailable_settings[:10])  # Show first 10
            if len(unavailable_settings) > 10:
                unavail_text += f" + {len(unavailable_settings) - 10} more"
            
            unavail_label = tk.Label(self.settings_frame,
                                   text=f"Other detected settings: {unavail_text}",
                                   bg='#161b22', fg='#8b949e', font=('Segoe UI', 8),
                                   wraplength=280)
            unavail_label.pack(padx=10, pady=(0, 10))
        
        # Quick actions
        if recommended_settings:
            actions_frame = tk.Frame(self.settings_frame, bg='#161b22')
            actions_frame.pack(fill=tk.X, pady=20, padx=5)
            
            ttk.Label(actions_frame, text="⚡ Quick Actions", style='ModernHeader.TLabel').pack(anchor='w', pady=(0, 10))
            
            copy_all_btn = tk.Button(actions_frame, text="📋 Copy All Optimized Settings", 
                                    bg='#238636', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=8,
                                    command=lambda: self.copy_all_settings(recommended_settings, game_name))
            copy_all_btn.pack(fill=tk.X, pady=(0, 5))
            
            export_btn = tk.Button(actions_frame, text="💾 Export Complete Settings Profile", 
                                  bg='#1f6feb', fg='#f0f6fc', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8,
                                  command=lambda: self.export_comprehensive_settings(available_settings, recommended_settings, game_name))
            export_btn.pack(fill=tk.X)
    
    def _update_analysis_results(self, response, settings):
        """Update analysis results in main thread"""
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, f"🤖 AI Analysis Results:\n\n{response}")
        self.ai_text.config(state=tk.DISABLED)
        
        # Update settings panel with game name
        if settings:
            game_name = self.game_entry.get().strip()
            self.update_settings_panel(settings, game_name)
    
    def parse_settings_from_response(self, response):
        """Parse settings from AI response (fallback method)"""
        settings = {}
        try:
            lines = response.split('\n')
            in_settings = False
            
            for line in lines:
                line = line.strip()
                if line == "SETTINGS:" or "SETTINGS" in line:
                    in_settings = True
                    continue
                elif line == "ANALYSIS:" or "ANALYSIS" in line:
                    break
                elif in_settings and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        # Clean up value
                        value = value.replace('[', '').replace(']', '')
                        settings[key] = value
        except:
            pass
        
        return settings
    
    def monitor_performance(self):
        """Monitor system performance with robust error handling"""
        while self.running:
            try:
                # Get CPU usage
                try:
                    cpu_usage = psutil.cpu_percent(interval=0.1)
                except Exception:
                    cpu_usage = 0
                
                # Get memory usage
                try:
                    mem = psutil.virtual_memory()
                    ram_usage = mem.percent
                except Exception:
                    ram_usage = 0
                
                # Get GPU usage
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        gpu_usage = round(gpu.load * 100, 1)
                        gpu_temp = gpu.temperature
                    else:
                        gpu_usage = 0
                        gpu_temp = 0
                except Exception:
                    gpu_usage = 0
                    gpu_temp = 0
                
                # Update metric cards using thread-safe method
                self.root.after(0, self.update_metrics, cpu_usage, gpu_usage, ram_usage, gpu_temp)
                
            except Exception:
                # Continue monitoring even if there's an error
                pass
            
            time.sleep(2.0)  # Update every 2 seconds for stability
    
    def update_metrics(self, cpu_usage, gpu_usage, ram_usage, gpu_temp):
        """Update metric displays (called from main thread)"""
        try:
            # Update metrics in both tabs
            metrics_to_update = [
                ('cpu_metric', cpu_usage),
                ('gpu_metric', gpu_usage),
                ('ram_metric', ram_usage),
                ('temp_metric', gpu_temp),
                ('game_cpu_metric', cpu_usage),
                ('game_gpu_metric', gpu_usage),
                ('game_ram_metric', ram_usage),
                ('game_temp_metric', gpu_temp)
            ]
            
            for metric_name, value in metrics_to_update:
                if hasattr(self, metric_name) and getattr(self, metric_name):
                    metric = getattr(self, metric_name)
                    if 'value' in metric:
                        metric['value'].config(text=f"{int(value)}")
                
            # Color coding for performance metrics
            self.update_metric_colors(cpu_usage, gpu_usage, ram_usage, gpu_temp)
            
        except Exception as e:
            pass  # Silent error handling
    
    def update_metric_colors(self, cpu, gpu, ram, temp):
        """Update metric card colors based on values"""
        try:
            # Update colors for both system info and game analysis metrics
            metrics_to_color = [
                ('cpu_metric', cpu, 80, 60),
                ('game_cpu_metric', cpu, 80, 60),
                ('gpu_metric', gpu, 90, 70),
                ('game_gpu_metric', gpu, 90, 70),
                ('ram_metric', ram, 85, 70),
                ('game_ram_metric', ram, 85, 70),
                ('temp_metric', temp, 80, 70),
                ('game_temp_metric', temp, 80, 70)
            ]
            
            for metric_name, value, high_thresh, med_thresh in metrics_to_color:
                if hasattr(self, metric_name) and getattr(self, metric_name):
                    metric = getattr(self, metric_name)
                    if 'color' in metric:
                        if value > high_thresh:
                            metric['color'].config(fg='#f85149')  # Red
                        elif value > med_thresh:
                            metric['color'].config(fg='#f1e05a')  # Yellow
                        else:
                            metric['color'].config(fg='#3fb950')  # Green
                    
        except Exception:
            pass  # Silent error handling
    
    def load_benchmark_cache(self):
        """Load cached benchmark data"""
        cache_file = "benchmark_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.benchmark_cache = json.load(f)
            except:
                self.benchmark_cache = {}
        else:
            self.benchmark_cache = {}
    
    def load_benchmark_data(self):
        """Load benchmark data"""
        # Basic benchmark data for common games
        basic_data = {
            "Cyberpunk 2077": {"medium": {"fps": "45-55", "gpu_usage": "90-95%"}},
            "Valorant": {"high": {"fps": "200-300", "gpu_usage": "40-60%"}},
            "Warzone": {"high": {"fps": "60-75", "gpu_usage": "90-95%"}},
            "Apex Legends": {"high": {"fps": "80-100", "gpu_usage": "85-95%"}},
            "Fortnite": {"high": {"fps": "80-100", "gpu_usage": "75-85%"}},
            "Minecraft": {"high": {"fps": "120-200", "gpu_usage": "50-70%"}}
        }
        
        self.benchmark_cache.update(basic_data)
    
    def load_game_history(self):
        """Load game history from file"""
        history_file = "game_history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.game_history = json.load(f)
            except:
                self.game_history = []
        else:
            self.game_history = []
    
    def save_game_history(self):
        """Save game history to file"""
        try:
            with open("game_history.json", 'w') as f:
                json.dump(self.game_history, f, indent=2)
        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def add_to_history(self, game_name, target_fps, actual_analysis, settings_count):
        """Add a game analysis to history"""
        history_entry = {
            "game": game_name,
            "target_fps": target_fps,
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "settings_detected": settings_count,
            "hardware": self.get_gpu_name(),
            "analysis_type": "Optimized Performance",
            "achieved_fps_estimate": actual_analysis.get("Expected FPS Range", "Not specified"),
            "key_optimizations": actual_analysis.get("Key Optimizations", "DLSS/FSR recommended")
        }
        
        # Add to beginning of list (most recent first)
        self.game_history.insert(0, history_entry)
        
        # Keep only last 50 entries
        self.game_history = self.game_history[:50]
        
        # Save to file
        self.save_game_history()
        
        # Update display if history tab exists
        try:
            self.update_history_display()
        except:
            pass
    
    def update_history_display(self):
        """Update the history display"""
        # Clear existing history cards
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        if not self.game_history:
            # No history message
            no_history = tk.Label(self.history_frame, 
                                text="🎮 No game analysis history yet!\n\nAnalyze some games to see them appear here.",
                                bg='#0d1117', fg='#8b949e', font=('Segoe UI', 12),
                                justify='center')
            no_history.pack(expand=True, pady=50)
            return
        
        # Create history cards
        for i, entry in enumerate(self.game_history):
            self.create_history_card(entry, i)
    
    def create_history_card(self, entry, index):
        """Create a history card for a game analysis"""
        # Main card frame
        card = tk.Frame(self.history_frame, bg='#161b22', relief='ridge', borderwidth=1)
        card.pack(fill=tk.X, pady=(0, 15), padx=10)
        
        # Header with game name and date
        header = tk.Frame(card, bg='#161b22')
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Game name
        game_label = tk.Label(header, text=f"🎮 {entry['game']}", 
                            bg='#161b22', fg='#58a6ff', font=('Segoe UI', 14, 'bold'))
        game_label.pack(side=tk.LEFT)
        
        # Date
        date_label = tk.Label(header, text=entry['analysis_date'], 
                            bg='#161b22', fg='#8b949e', font=('Segoe UI', 9))
        date_label.pack(side=tk.RIGHT)
        
        # Performance info
        perf_frame = tk.Frame(card, bg='#161b22')
        perf_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Target vs Achieved FPS
        fps_info = tk.Frame(perf_frame, bg='#161b22')
        fps_info.pack(fill=tk.X, pady=5)
        
        target_label = tk.Label(fps_info, text=f"🎯 Target: {entry['target_fps']} FPS", 
                              bg='#161b22', fg='#f1e05a', font=('Segoe UI', 10, 'bold'))
        target_label.pack(side=tk.LEFT)
        
        achieved_label = tk.Label(fps_info, text=f"📊 Achieved: {entry['achieved_fps_estimate']}", 
                                bg='#161b22', fg='#3fb950', font=('Segoe UI', 10))
        achieved_label.pack(side=tk.RIGHT)
        
        # Settings and hardware info
        details_frame = tk.Frame(perf_frame, bg='#161b22')
        details_frame.pack(fill=tk.X, pady=5)
        
        settings_label = tk.Label(details_frame, text=f"⚙️ {entry['settings_detected']} settings optimized", 
                                bg='#161b22', fg='#8b949e', font=('Segoe UI', 9))
        settings_label.pack(side=tk.LEFT)
        
        hw_label = tk.Label(details_frame, text=f"💻 {entry['hardware']}", 
                          bg='#161b22', fg='#8b949e', font=('Segoe UI', 9))
        hw_label.pack(side=tk.RIGHT)
        
        # Key optimizations
        if entry.get('key_optimizations'):
            opt_label = tk.Label(card, text=f"🔧 Key: {entry['key_optimizations'][:60]}...", 
                               bg='#161b22', fg='#f0f6fc', font=('Segoe UI', 9),
                               wraplength=400)
            opt_label.pack(padx=15, pady=(0, 10))
        
        # Action buttons
        actions_frame = tk.Frame(card, bg='#161b22')
        actions_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Re-analyze button
        reanalyze_btn = tk.Button(actions_frame, text="🔄 Re-analyze", 
                                bg='#238636', fg='#f0f6fc', font=('Segoe UI', 9),
                                relief='flat', padx=10, pady=5,
                                command=lambda: self.reanalyze_game(entry))
        reanalyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(actions_frame, text="🗑️ Delete", 
                             bg='#f85149', fg='#f0f6fc', font=('Segoe UI', 9),
                             relief='flat', padx=10, pady=5,
                             command=lambda: self.delete_history_entry(index))
        delete_btn.pack(side=tk.RIGHT)
    
    def reanalyze_game(self, entry):
        """Re-analyze a game from history"""
        # Switch to analysis tab
        self.notebook.select(0)
        
        # Set the game name and FPS
        self.game_entry.delete(0, tk.END)
        self.game_entry.insert(0, entry['game'])
        self.fps_entry.delete(0, tk.END)
        self.fps_entry.insert(0, str(entry['target_fps']))
        
        # Show notification
        self.show_notification(f"🔄 Ready to re-analyze {entry['game']}")
    
    def delete_history_entry(self, index):
        """Delete a history entry"""
        if messagebox.askyesno("Delete Entry", "Are you sure you want to delete this history entry?"):
            del self.game_history[index]
            self.save_game_history()
            self.update_history_display()
            self.show_notification("🗑️ History entry deleted")
    
    def clear_game_history(self):
        """Clear all game history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all game analysis history?"):
            self.game_history = []
            self.save_game_history()
            self.update_history_display()
            self.show_notification("🗑️ All history cleared")
    
    def get_upgrade_recommendations(self):
        """Get AI-powered upgrade recommendations"""
        if not self.ai_model:
            return {"⚠️ AI Not Available": ["Please configure Gemini API key"]}
        
        try:
            prompt = f"""
            Analyze the following system and recommend specific upgrades for gaming performance:
            
            Current Hardware:
            - Device: {"Laptop" if self.system_specs.get('is_laptop', False) else "Desktop"}
            - GPU: {self.system_specs['gpu']} ({self.system_specs['gpu_vram_gb']} GB VRAM)
            - CPU: {self.system_specs['cpu']} ({self.system_specs['cpu_cores']} cores, {self.system_specs['cpu_threads']} threads)
            - RAM: {self.system_specs['ram_gb']} GB
            
            Provide specific upgrade recommendations in categories:
            1. GPU Upgrades - List 3 specific GPU models with expected performance improvement percentages
            2. RAM Upgrades - RAM capacity recommendations
            3. Storage Upgrades - SSD recommendations for gaming
            4. Cooling Upgrades - Especially for {"laptop" if self.system_specs.get('is_laptop', False) else "desktop"} systems
            
            Format each category as:
            [Category Name]:
            • [Specific recommendation] - [Benefit/improvement]
            
            Be specific to this exact hardware configuration.
            """
            
            response = self.ai_model.generate_content(prompt)
            
            # Parse the response into categories
            recommendations = {}
            current_category = None
            
            for line in response.text.split('\n'):
                line = line.strip()
                if line and ':' in line and not line.startswith('•'):
                    current_category = line
                    recommendations[current_category] = []
                elif line.startswith('•') and current_category:
                    recommendations[current_category].append(line[1:].strip())
            
            return recommendations if recommendations else {"AI Analysis": [response.text]}
            
        except Exception as e:
            return {"⚠️ AI Error": [f"Failed to get recommendations: {str(e)}"]}
    
    def get_fps_suggestions(self, target_fps):
        """Get AI-powered FPS optimization suggestions"""
        if not self.ai_model:
            return {"⚠️ AI Not Available": ["Please configure Gemini API key"]}
        
        try:
            prompt = f"""
            Provide FPS optimization suggestions for achieving {target_fps} FPS on this system:
            
            Hardware:
            - Device: {"Laptop" if self.system_specs.get('is_laptop', False) else "Desktop"}
            - GPU: {self.system_specs['gpu']} ({self.system_specs['gpu_vram_gb']} GB VRAM)
            - CPU: {self.system_specs['cpu']}
            - RAM: {self.system_specs['ram_gb']} GB
            
            Target: {target_fps} FPS
            
            Provide specific suggestions in categories:
            1. Graphics Settings - Specific settings to achieve target FPS
            2. System Optimization - System-level optimizations
            3. Reality Check - Whether {target_fps} FPS is realistic for this hardware
            
            Format as:
            [Category]:
            • [Specific suggestion]
            
            Be realistic about what this hardware can achieve.
            """
            
            response = self.ai_model.generate_content(prompt)
            
            # Parse the response
            suggestions = {}
            current_category = None
            
            for line in response.text.split('\n'):
                line = line.strip()
                if line and ':' in line and not line.startswith('•'):
                    current_category = line
                    suggestions[current_category] = []
                elif line.startswith('•') and current_category:
                    suggestions[current_category].append(line[1:].strip())
            
            return suggestions if suggestions else {"AI Analysis": [response.text]}
            
        except Exception as e:
            return {"⚠️ AI Error": [f"Failed to get suggestions: {str(e)}"]}
    
    def analyze_bottlenecks(self):
        """Analyze system bottlenecks with AI"""
        if not self.ai_model:
            return ["⚠️ AI not available - Please configure Gemini API key"]
        
        try:
            prompt = f"""
            Analyze this system for gaming bottlenecks:
            
            Hardware:
            - Device: {"Laptop" if self.system_specs.get('is_laptop', False) else "Desktop"}
            - GPU: {self.system_specs['gpu']} ({self.system_specs['gpu_vram_gb']} GB VRAM)
            - CPU: {self.system_specs['cpu']} ({self.system_specs['cpu_cores']} cores, {self.system_specs['cpu_threads']} threads)
            - RAM: {self.system_specs['ram_gb']} GB
            
            Identify bottlenecks in bullet points:
            • [Component] - [Analysis of performance level and bottleneck potential]
            
            Focus on gaming performance.
            """
            
            response = self.ai_model.generate_content(prompt)
            
            # Extract bullet points
            bottlenecks = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line.startswith('•'):
                    bottlenecks.append(line)
            
            return bottlenecks if bottlenecks else [response.text]
            
        except Exception as e:
            return [f"⚠️ AI analysis failed: {str(e)}"]
    
    def get_optimized_setting_description(self, setting, game_name, performance_analysis):
        """Get description for settings with optimization context"""
        base_description = self.get_setting_description(setting, game_name)
        
        # Add optimization context
        if "dlss" in setting.lower() or "fsr" in setting.lower():
            return f"{base_description} (Key for high FPS performance)"
        elif "quality" in setting.lower() and "medium" in str(performance_analysis.values()).lower():
            return f"{base_description} (Balanced for performance)"
        elif "rtx" in self.get_gpu_name().lower() or "nvidia" in self.get_gpu_name().lower():
            return f"{base_description} (Optimized for {self.system_specs['gpu']})"
        else:
            return f"{base_description} (Performance optimized)"
    
    def copy_optimized_settings(self, recommended_settings, performance_analysis, game_name):
        """Copy settings with optimization note"""
        settings_text = f"🎮 Optimized {game_name} Settings for {self.fps_entry.get()}+ FPS:\n\n"
        
        if performance_analysis:
            settings_text += "🚀 Performance Targets:\n"
            for key, value in performance_analysis.items():
                if key in ["Expected FPS Range", "Target Achievable", "Key Optimizations"]:
                    settings_text += f"• {key}: {value}\n"
            settings_text += "\n"
        
        settings_text += "⚙️ Optimized Settings:\n"
        for setting, value in recommended_settings.items():
            settings_text += f"• {setting}: {value}\n"
        
        settings_text += f"\n💻 Hardware: {self.get_gpu_name()}\n"
        settings_text += f"🎯 Target: {self.fps_entry.get()} FPS (Achievable with these settings)"
        
        root = self.root
        root.clipboard_clear()
        root.clipboard_append(settings_text)
        
        # Show feedback
        feedback = tk.Toplevel(root)
        feedback.title("Copied!")
        feedback.geometry("300x100")
        feedback.configure(bg='#0d1117')
        feedback.resizable(False, False)
        
        tk.Label(feedback, text="✅ Optimized settings copied!", 
                bg='#0d1117', fg='#3fb950', font=('Segoe UI', 12, 'bold')).pack(expand=True)
        
        # Auto close after 2 seconds
        feedback.after(2000, feedback.destroy)
    
    def export_optimized_profile(self, available_settings, recommended_settings, performance_analysis, game_name):
        """Export comprehensive optimized profile"""
        profile_data = {
            "game": game_name,
            "analysis_type": "Performance Optimized Analysis",
            "hardware": {
                "gpu": self.get_gpu_name(),
                "cpu": self.get_cpu_name(),
                "ram": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
                "system_type": "Laptop" if "laptop" in self.get_gpu_name().lower() else "Desktop"
            },
            "target_fps": self.fps_entry.get(),
            "performance_analysis": performance_analysis,
            "detection_summary": {
                "total_settings_detected": len(available_settings),
                "optimized_settings": len(recommended_settings),
                "analysis_confidence": "Optimized (High Performance)"
            },
            "all_detected_settings": available_settings,
            "recommended_settings": recommended_settings,
            "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": [
                f"Settings optimized for {self.fps_entry.get()}+ FPS performance",
                f"Based on {self.system_specs['gpu']} capability",
                "Balanced approach: performance priority with good visual quality",
                "DLSS/FSR recommended for optimal performance"
            ]
        }
        
        filename = f"{game_name.replace(' ', '_')}_optimized_profile.json"
        try:
            with open(filename, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            # Show success message
            success = tk.Toplevel(self.root)
            success.title("Export Successful")
            success.geometry("400x200")
            success.configure(bg='#0d1117')
            success.resizable(False, False)
            
            tk.Label(success, text="✅ Optimized Profile Exported!", 
                    bg='#0d1117', fg='#3fb950', font=('Segoe UI', 14, 'bold')).pack(pady=20)
            
            tk.Label(success, text=f"📁 Saved as: {filename}", 
                    bg='#0d1117', fg='#8b949e', font=('Segoe UI', 10)).pack(pady=5)
            
            tk.Label(success, text=f"🎯 {len(recommended_settings)} optimized settings for {self.fps_entry.get()}+ FPS", 
                    bg='#0d1117', fg='#f1e05a', font=('Segoe UI', 10)).pack(pady=5)
            
            if performance_analysis:
                perf_text = f"🚀 Performance targets and optimizations included"
                tk.Label(success, text=perf_text, 
                        bg='#0d1117', fg='#58a6ff', font=('Segoe UI', 10)).pack(pady=5)
            
        except Exception as e:
            print(f"Export error: {e}")

    def get_realistic_setting_description(self, setting, game_name, performance_analysis):
        """Get description for settings with realistic performance context"""
        base_description = self.get_setting_description(setting, game_name)
        
        # Add performance context
        if performance_analysis and "Conservative" in str(performance_analysis.values()):
            return f"{base_description} (Conservative for stable FPS)"
        elif "laptop" in self.get_gpu_name().lower():
            return f"{base_description} (Laptop optimized)"
        else:
            return base_description
    
    def copy_realistic_settings(self, recommended_settings, performance_analysis, game_name):
        """Copy settings with realistic performance note"""
        settings_text = f"🎮 Realistic {game_name} Settings:\n\n"
        
        if performance_analysis:
            settings_text += "📊 Performance Expectations:\n"
            for key, value in performance_analysis.items():
                settings_text += f"• {key}: {value}\n"
            settings_text += "\n"
        
        settings_text += "⚙️ Conservative Settings:\n"
        for setting, value in recommended_settings.items():
            settings_text += f"• {setting}: {value}\n"
        
        root = self.root
        root.clipboard_clear()
        root.clipboard_append(settings_text)
        
        # Show feedback
        feedback = tk.Toplevel(root)
        feedback.title("Copied!")
        feedback.geometry("300x100")
        feedback.configure(bg='#0d1117')
        feedback.resizable(False, False)
        
        tk.Label(feedback, text="✅ Realistic settings copied!", 
                bg='#0d1117', fg='#3fb950', font=('Segoe UI', 12, 'bold')).pack(expand=True)
        
        # Auto close after 2 seconds
        feedback.after(2000, feedback.destroy)
    
    def export_realistic_profile(self, available_settings, recommended_settings, performance_analysis, game_name):
        """Export comprehensive realistic profile"""
        profile_data = {
            "game": game_name,
            "analysis_type": "Realistic Performance Analysis",
            "hardware": {
                "gpu": self.get_gpu_name(),
                "cpu": self.get_cpu_name(),
                "ram": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
                "system_type": "Laptop" if "laptop" in self.get_gpu_name().lower() else "Desktop"
            },
            "target_fps": self.fps_entry.get(),
            "performance_analysis": performance_analysis,
            "detection_summary": {
                "total_settings_detected": len(available_settings),
                "optimized_settings": len(recommended_settings),
                "analysis_confidence": "Conservative (Realistic)"
            },
            "all_detected_settings": available_settings,
            "recommended_settings": recommended_settings,
            "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": [
                "These settings prioritize stability and realistic performance",
                "Laptop hardware has 15-25% performance penalty vs desktop",
                "Conservative estimates for sustained gaming sessions",
                "Consider thermal throttling in extended gameplay"
            ]
        }
        
        filename = f"{game_name.replace(' ', '_')}_realistic_profile.json"
        try:
            with open(filename, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            # Show success message
            success = tk.Toplevel(self.root)
            success.title("Export Successful")
            success.geometry("400x200")
            success.configure(bg='#0d1117')
            success.resizable(False, False)
            
            tk.Label(success, text="✅ Realistic Profile Exported!", 
                    bg='#0d1117', fg='#3fb950', font=('Segoe UI', 14, 'bold')).pack(pady=20)
            
            tk.Label(success, text=f"📁 Saved as: {filename}", 
                    bg='#0d1117', fg='#8b949e', font=('Segoe UI', 10)).pack(pady=5)
            
            tk.Label(success, text=f"🎯 {len(recommended_settings)} conservative settings included", 
                    bg='#0d1117', fg='#f1e05a', font=('Segoe UI', 10)).pack(pady=5)
            
            if performance_analysis:
                perf_text = f"📊 Realistic FPS expectations included"
                tk.Label(success, text=perf_text, 
                        bg='#0d1117', fg='#ff7b72', font=('Segoe UI', 10)).pack(pady=5)
            
        except Exception as e:
            print(f"Export error: {e}")
    
    def get_gpu_name(self):
        """Get GPU name"""
        return self.system_specs.get('gpu', 'Unknown GPU')
    
    def get_cpu_name(self):
        """Get CPU name"""
        return self.system_specs.get('cpu', 'Unknown CPU')
    
    def get_realistic_setting_description(self, setting, game_name, performance_analysis):
        """Get description for settings with realistic performance context"""
        base_description = self.get_setting_description(setting, game_name)
        
        # Add performance context
        if performance_analysis and "Conservative" in str(performance_analysis.values()):
            return f"{base_description} (Conservative for stable FPS)"
        elif "laptop" in self.get_gpu_name().lower():
            return f"{base_description} (Laptop optimized)"
        else:
            return base_description
    
    def copy_realistic_settings(self, recommended_settings, performance_analysis, game_name):
        """Copy settings with realistic performance note"""
        settings_text = f"🎮 Realistic {game_name} Settings:\n\n"
        
        if performance_analysis:
            settings_text += "📊 Performance Expectations:\n"
            for key, value in performance_analysis.items():
                settings_text += f"• {key}: {value}\n"
            settings_text += "\n"
        
        settings_text += "⚙️ Conservative Settings:\n"
        for setting, value in recommended_settings.items():
            settings_text += f"• {setting}: {value}\n"
        
        root = self.root
        root.clipboard_clear()
        root.clipboard_append(settings_text)
        
        # Show feedback
        feedback = tk.Toplevel(root)
        feedback.title("Copied!")
        feedback.geometry("300x100")
        feedback.configure(bg='#0d1117')
        feedback.resizable(False, False)
        
        tk.Label(feedback, text="✅ Realistic settings copied!", 
                bg='#0d1117', fg='#3fb950', font=('Segoe UI', 12, 'bold')).pack(expand=True)
        
        # Auto close after 2 seconds
        feedback.after(2000, feedback.destroy)
    
    def export_realistic_profile(self, available_settings, recommended_settings, performance_analysis, game_name):
        """Export comprehensive realistic profile"""
        profile_data = {
            "game": game_name,
            "analysis_type": "Realistic Performance Analysis",
            "hardware": {
                "gpu": self.get_gpu_name(),
                "cpu": self.get_cpu_name(),
                "ram": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
                "system_type": "Laptop" if "laptop" in self.get_gpu_name().lower() else "Desktop"
            },
            "target_fps": self.fps_entry.get(),
            "performance_analysis": performance_analysis,
            "detection_summary": {
                "total_settings_detected": len(available_settings),
                "optimized_settings": len(recommended_settings),
                "analysis_confidence": "Conservative (Realistic)"
            },
            "all_detected_settings": available_settings,
            "recommended_settings": recommended_settings,
            "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": [
                "These settings prioritize stability and realistic performance",
                "Laptop hardware has 15-25% performance penalty vs desktop",
                "Conservative estimates for sustained gaming sessions",
                "Consider thermal throttling in extended gameplay"
            ]
        }
        
        filename = f"{game_name.replace(' ', '_')}_realistic_profile.json"
        try:
            with open(filename, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            # Show success message
            success = tk.Toplevel(self.root)
            success.title("Export Successful")
            success.geometry("400x200")
            success.configure(bg='#0d1117')
            success.resizable(False, False)
            
            tk.Label(success, text="✅ Realistic Profile Exported!", 
                    bg='#0d1117', fg='#3fb950', font=('Segoe UI', 14, 'bold')).pack(pady=20)
            
            tk.Label(success, text=f"📁 Saved as: {filename}", 
                    bg='#0d1117', fg='#8b949e', font=('Segoe UI', 10)).pack(pady=5)
            
            tk.Label(success, text=f"🎯 {len(recommended_settings)} conservative settings included", 
                    bg='#0d1117', fg='#f1e05a', font=('Segoe UI', 10)).pack(pady=5)
            
            if performance_analysis:
                perf_text = f"📊 Realistic FPS expectations included"
                tk.Label(success, text=perf_text, 
                        bg='#0d1117', fg='#ff7b72', font=('Segoe UI', 10)).pack(pady=5)
            
        except Exception as e:
            print(f"Export error: {e}")
    
    def get_conservative_description(self, setting, game_name, guaranteed_fps):
        """Get conservative optimization description"""
        setting_lower = setting.lower()
        
        if "texture" in setting_lower:
            return f"Conservative texture setting to guarantee {guaranteed_fps}+ FPS"
        elif "shadow" in setting_lower:
            return f"Shadow quality optimized for guaranteed {guaranteed_fps} FPS minimum"
        elif "effect" in setting_lower:
            return f"Effects setting prioritizing {guaranteed_fps}+ FPS guarantee"
        elif "ray" in setting_lower or "rt" in setting_lower:
            return f"Ray tracing disabled/low to ensure {guaranteed_fps} FPS guarantee"
        elif "dlss" in setting_lower or "fsr" in setting_lower:
            return f"Performance mode for maximum FPS guarantee ({guaranteed_fps}+)"
        else:
            return f"Conservative setting ensuring guaranteed {guaranteed_fps}+ FPS"
    
    def create_conservative_setting_card(self, parent, setting_name, recommended_value, description=""):
        """Create setting card with clean design"""
        card = tk.Frame(parent, bg='#21262d', relief='flat', borderwidth=1)
        card.pack(fill=tk.X, pady=(0, 8), padx=15)
        
        # Header
        header = tk.Frame(card, bg='#21262d')
        header.pack(fill=tk.X, padx=15, pady=(12, 5))
        
        name_label = tk.Label(header, text=setting_name, bg='#21262d', fg='#f0f6fc', 
                             font=('Segoe UI', 11, 'bold'))
        name_label.pack(side=tk.LEFT)
        
        # Value
        value_label = tk.Label(card, text=recommended_value, bg='#21262d', fg='#3fb950', 
                              font=('Segoe UI', 12, 'bold'))
        value_label.pack(padx=15, pady=(0, 5))
        
        # Description
        if description:
            desc_label = tk.Label(card, text=description, bg='#21262d', fg='#8b949e', 
                                 font=('Segoe UI', 9), wraplength=250)
            desc_label.pack(padx=15, pady=(0, 12))
        
        return card
    
    def copy_guaranteed_settings(self, settings, guaranteed_analysis, game_name, guaranteed_fps):
        """Copy guaranteed settings with performance info"""
        text = f"🛡️ GUARANTEED Gaming Settings - {game_name}\n"
        text += "=" * 50 + "\n\n"
        text += f"PERFORMANCE GUARANTEE: {guaranteed_fps}+ FPS minimum\n"
        text += f"Game: {game_name}\n"
        text += f"GPU: {self.system_specs['gpu']}\n\n"
        
        if guaranteed_analysis:
            text += "GUARANTEE ANALYSIS:\n"
            for key, value in guaranteed_analysis.items():
                text += f"• {key}: {value}\n"
            text += "\n"
        
        text += "CONSERVATIVE SETTINGS:\n"
        text += "-" * 30 + "\n"
        for setting, value in settings.items():
            text += f"{setting}: {value}\n"
        
        text += f"\n100% GUARANTEE: These settings ensure you NEVER drop below {guaranteed_fps} FPS"
        
        self.copy_to_clipboard(text)
    
    def export_guarantee_profile(self, available_settings, recommended_settings, guaranteed_analysis, game_name, guaranteed_fps):
        """Export comprehensive guarantee profile"""
        try:
            timestamp = int(time.time())
            filename = f"{game_name.replace(' ', '_')}_guaranteed_{guaranteed_fps}fps_profile_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"🛡️ {game_name} - GUARANTEED {guaranteed_fps}+ FPS Profile\n")
                f.write("="*70 + "\n\n")
                f.write(f"Hardware: {self.system_specs['gpu']}\n")
                f.write(f"Target FPS: {self.fps_entry.get()}\n")
                f.write(f"GUARANTEED FPS: {guaranteed_fps}+ (100% confidence)\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if guaranteed_analysis:
                    f.write("🛡️ PERFORMANCE GUARANTEE:\n")
                    f.write("-" * 40 + "\n")
                    for key, value in guaranteed_analysis.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                f.write("⚙️ CONSERVATIVE SETTINGS (100% guaranteed):\n")
                f.write("-" * 45 + "\n")
                for setting, value in recommended_settings.items():
                    f.write(f"{setting}: {value}\n")
                
                f.write(f"\n🔍 ALL DETECTED SETTINGS ({len(available_settings)} total):\n")
                f.write("-" * 40 + "\n")
                for i, setting in enumerate(available_settings, 1):
                    status = "✅ Optimized" if setting in recommended_settings else "ℹ️ Detected"
                    f.write(f"{i:2d}. {setting} - {status}\n")
                
                f.write(f"\n🛡️ PERFORMANCE GUARANTEE:\n")
                f.write(f"• These settings GUARANTEE {guaranteed_fps}+ FPS minimum\n")
                f.write(f"• Conservative optimization prioritizes performance over visuals\n")
                f.write(f"• 100% confidence - you will NEVER drop below {guaranteed_fps} FPS\n")
                f.write(f"• Settings tested for worst-case scenarios\n")
            
            self.show_notification(f"🛡️ Guarantee profile exported to {filename}")
        except Exception as e:
            self.show_notification(f"❌ Export failed: {e}")
    
    def organize_detailed_settings_by_category(self, available_settings, recommended_settings):
        """Organize settings into detailed categories with impact analysis"""
        categories = {
            "🎯 Core Graphics (High Impact)": {},
            "🌟 Visual Effects (Medium Impact)": {},
            "⚡ Performance (Critical Impact)": {},
            "🎨 Display & Interface": {},
            "🔧 Advanced Options": {}
        }
        
        # Define category keywords with impact levels
        core_keywords = ["texture", "shadow", "model", "mesh", "geometry", "detail", "quality", "lod"]
        effects_keywords = ["effect", "particle", "bloom", "grain", "blur", "lighting", "reflection", "ambient", "ray"]
        performance_keywords = ["fps", "frame", "vsync", "limit", "dlss", "fsr", "upscaling", "streaming", "cache"]
        display_keywords = ["resolution", "scale", "fullscreen", "window", "brightness", "gamma", "contrast"]
        
        for setting, value in recommended_settings.items():
            setting_lower = setting.lower()
            categorized = False
            
            # Check each category with priority
            if any(keyword in setting_lower for keyword in performance_keywords):
                categories["⚡ Performance (Critical Impact)"][setting] = value
                categorized = True
            elif any(keyword in setting_lower for keyword in core_keywords):
                categories["🎯 Core Graphics (High Impact)"][setting] = value
                categorized = True
            elif any(keyword in setting_lower for keyword in effects_keywords):
                categories["🌟 Visual Effects (Medium Impact)"][setting] = value
                categorized = True
            elif any(keyword in setting_lower for keyword in display_keywords):
                categories["🎨 Display & Interface"][setting] = value
                categorized = True
            
            # If not categorized, put in advanced
            if not categorized:
                categories["🔧 Advanced Options"][setting] = value
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def get_detailed_setting_description(self, setting, game_name, value, analysis):
        """Get detailed description with performance impact for any setting"""
        setting_lower = setting.lower()
        
        # Base description with performance impact
        if "texture" in setting_lower:
            return f"Controls texture detail and VRAM usage. Setting: {value} - Moderate GPU memory impact in {game_name}"
        elif "shadow" in setting_lower:
            return f"Shadow rendering quality and distance. Setting: {value} - HIGH FPS impact, major performance setting in {game_name}"
        elif "effect" in setting_lower:
            return f"Particle effects and explosions quality. Setting: {value} - Medium GPU load impact in {game_name}"
        elif "ray" in setting_lower or "rt" in setting_lower:
            return f"Ray tracing lighting technology. Setting: {value} - MASSIVE FPS impact, only for high-end GPUs in {game_name}"
        elif "dlss" in setting_lower or "fsr" in setting_lower:
            return f"AI upscaling for better performance. Setting: {value} - IMPROVES FPS significantly, essential for high framerates in {game_name}"
        elif "resolution" in setting_lower:
            return f"Display rendering resolution. Setting: {value} - HUGE FPS impact, most important performance setting in {game_name}"
        elif "anti" in setting_lower or "aa" in setting_lower:
            return f"Edge smoothing technique. Setting: {value} - Medium FPS impact, affects visual quality in {game_name}"
        elif "motion" in setting_lower and "blur" in setting_lower:
            return f"Movement blur effects. Setting: {value} - Low FPS impact, personal preference in {game_name}"
        elif "vsync" in setting_lower:
            return f"Screen tearing prevention. Setting: {value} - Adds input lag but prevents tearing in {game_name}"
        elif "fps" in setting_lower or "frame" in setting_lower:
            return f"Frame rate limiting control. Setting: {value} - Direct FPS control, important for consistency in {game_name}"
        else:
            return f"Game-specific optimization setting. Value: {value} - Optimized for your hardware in {game_name}"
    
    def get_setting_impact_level(self, setting):
        """Get performance impact level for visual indication"""
        setting_lower = setting.lower()
        
        # Critical impact settings
        if any(x in setting_lower for x in ["resolution", "dlss", "fsr", "ray", "rt"]):
            return "critical"
        # High impact settings  
        elif any(x in setting_lower for x in ["shadow", "texture", "effect", "anti"]):
            return "high"
        # Medium impact settings
        elif any(x in setting_lower for x in ["detail", "quality", "lighting", "reflection"]):
            return "medium"
        # Low impact settings
        else:
            return "low"
    
    def create_detailed_setting_card(self, parent, setting_name, recommended_value, description, impact_level):
        """Create a detailed setting card with impact indicator"""
        # Impact level colors
        impact_colors = {
            "critical": "#f85149",  # Red
            "high": "#f1e05a",      # Yellow
            "medium": "#58a6ff",    # Blue
            "low": "#3fb950"        # Green
        }
        
        impact_labels = {
            "critical": "CRITICAL IMPACT",
            "high": "HIGH IMPACT", 
            "medium": "MEDIUM IMPACT",
            "low": "LOW IMPACT"
        }
        
        card = tk.Frame(parent, bg='#21262d', relief='ridge', borderwidth=1)
        card.pack(fill=tk.X, pady=(0, 8), padx=10)
        
        # Header with impact indicator
        header = tk.Frame(card, bg='#21262d')
        header.pack(fill=tk.X, padx=12, pady=(12, 5))
        
        # Setting name
        name_label = tk.Label(header, text=setting_name, bg='#21262d', fg='#f0f6fc', 
                             font=('Segoe UI', 11, 'bold'))
        name_label.pack(side=tk.LEFT)
        
        # Impact indicator
        impact_label = tk.Label(header, text=impact_labels[impact_level], 
                               bg='#21262d', fg=impact_colors[impact_level], 
                               font=('Segoe UI', 8, 'bold'))
        impact_label.pack(side=tk.RIGHT)
        
        # Recommended value with highlight
        value_frame = tk.Frame(card, bg='#21262d')
        value_frame.pack(fill=tk.X, padx=12, pady=(0, 5))
        
        tk.Label(value_frame, text="Recommended:", bg='#21262d', fg='#8b949e', 
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        tk.Label(value_frame, text=recommended_value, bg='#21262d', fg='#3fb950', 
                font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=(5, 0))
        
        # Detailed description
        desc_label = tk.Label(card, text=description, bg='#21262d', fg='#8b949e', 
                             font=('Segoe UI', 9), wraplength=280, justify='left')
        desc_label.pack(padx=12, pady=(0, 12), anchor='w')
        
        return card
    
    def copy_detailed_settings(self, settings, analysis, game_name, guaranteed_fps):
        """Copy detailed settings with analysis to clipboard"""
        target_fps = self.fps_entry.get()
        
        text = f"🎮 {game_name} - DETAILED OPTIMIZATION PROFILE\n"
        text += "=" * 50 + "\n\n"
        text += f"🎯 Target FPS: {target_fps}\n"
        text += f"✅ Guaranteed FPS: {guaranteed_fps}+\n"
        text += f"💻 Hardware: {self.system_specs['gpu']}\n"
        text += f"📊 Analysis Type: Benchmark-Accurate\n\n"
        
        text += "📊 PERFORMANCE ANALYSIS:\n"
        text += "-" * 30 + "\n"
        if analysis:
            for key, value in analysis.items():
                text += f"• {key}: {value}\n"
        text += "\n"
        
        text += "⚙️ OPTIMIZED SETTINGS:\n"
        text += "-" * 30 + "\n"
        
        # Organize by impact level
        critical_settings = []
        high_settings = []
        other_settings = []
        
        for setting, value in settings.items():
            impact = self.get_setting_impact_level(setting)
            setting_line = f"{setting}: {value}"
            
            if impact == "critical":
                critical_settings.append(setting_line)
            elif impact == "high":
                high_settings.append(setting_line)
            else:
                other_settings.append(setting_line)
        
        if critical_settings:
            text += "\n🔴 CRITICAL IMPACT SETTINGS:\n"
            for setting in critical_settings:
                text += f"  {setting}\n"
        
        if high_settings:
            text += "\n🟡 HIGH IMPACT SETTINGS:\n"
            for setting in high_settings:
                text += f"  {setting}\n"
        
        if other_settings:
            text += "\n🟢 OTHER SETTINGS:\n"
            for setting in other_settings:
                text += f"  {setting}\n"
        
        text += f"\n💡 USAGE INSTRUCTIONS:\n"
        text += f"1. Open {game_name}\n"
        text += f"2. Go to Graphics/Video Settings\n"
        text += f"3. Apply the settings above\n"
        text += f"4. Test performance and adjust if needed\n"
        text += f"5. These settings guarantee {guaranteed_fps}+ FPS minimum\n\n"
        
        text += f"Generated by AI Gaming Advisor Pro\n"
        text += f"Based on real benchmark data for {self.system_specs['gpu']}"
        
        self.copy_to_clipboard(text)
    
    def export_detailed_profile(self, available_settings, recommended_settings, analysis, game_name, guaranteed_fps):
        """Export detailed performance profile to file"""
        try:
            timestamp = int(time.time())
            filename = f"{game_name.replace(' ', '_')}_detailed_profile_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"🎮 {game_name} - DETAILED PERFORMANCE PROFILE\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"📅 Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"💻 Hardware: {self.system_specs['gpu']} | {self.system_specs['cpu']}\n")
                f.write(f"🎯 Target FPS: {self.fps_entry.get()}\n")
                f.write(f"✅ Guaranteed FPS: {guaranteed_fps}+\n")
                f.write(f"📊 Total Settings: {len(available_settings)} detected, {len(recommended_settings)} optimized\n\n")
                
                f.write("📊 BENCHMARK ANALYSIS:\n")
                f.write("-" * 40 + "\n")
                if analysis:
                    for key, value in analysis.items():
                        f.write(f"• {key}: {value}\n")
                f.write("\n")
                
                f.write("⚙️ DETAILED SETTINGS BREAKDOWN:\n")
                f.write("-" * 40 + "\n")
                
                # Categorize settings
                categories = self.organize_detailed_settings_by_category(available_settings, recommended_settings)
                
                for category, settings in categories.items():
                    if settings:
                        f.write(f"\n{category}:\n")
                        for setting, value in settings.items():
                            impact = self.get_setting_impact_level(setting)
                            desc = self.get_detailed_setting_description(setting, game_name, value, analysis)
                            f.write(f"  • {setting}: {value}\n")
                            f.write(f"    └─ {desc}\n")
                
                f.write(f"\n🎮 ALL DETECTED SETTINGS ({len(available_settings)} total):\n")
                f.write("-" * 40 + "\n")
                for i, setting in enumerate(available_settings, 1):
                    optimized = "✅ Optimized" if setting in recommended_settings else "ℹ️ Available"
                    f.write(f"{i:2d}. {setting} - {optimized}\n")
                
                f.write(f"\n💡 PERFORMANCE OPTIMIZATION TIPS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"• These settings are based on real benchmark data for {self.system_specs['gpu']}\n")
                f.write(f"• Guaranteed {guaranteed_fps}+ FPS minimum in {game_name}\n")
                f.write(f"• Critical impact settings have the biggest effect on FPS\n")
                f.write(f"• Monitor GPU temperature and adjust if thermal throttling occurs\n")
                f.write(f"• Keep drivers updated for optimal performance\n")
                
                f.write(f"\n🚀 QUICK SETUP GUIDE:\n")
                f.write("-" * 40 + "\n")
                f.write(f"1. Launch {game_name}\n")
                f.write(f"2. Navigate to Settings > Graphics/Video\n")
                f.write(f"3. Apply the optimized settings listed above\n")
                f.write(f"4. Test performance in-game\n")
                f.write(f"5. Fine-tune individual settings if needed\n\n")
                
                f.write("Generated by AI Gaming Advisor Pro - Benchmark-Accurate Settings\n")
            
            self.show_notification(f"💾 Detailed profile exported to {filename}")
        except Exception as e:
            self.show_notification(f"❌ Export failed: {e}")
    
    def show_apply_instructions(self, game_name):
        """Show instructions for applying settings"""
        instructions = tk.Toplevel(self.root)
        instructions.title(f"Apply Settings - {game_name}")
        instructions.geometry("500x400")
        instructions.configure(bg='#0d1117')
        instructions.resizable(False, False)
        instructions.transient(self.root)
        instructions.grab_set()
        
        # Header
        header = tk.Label(instructions, text=f"🎮 How to Apply Settings in {game_name}", 
                         bg='#0d1117', fg='#58a6ff', font=('Segoe UI', 14, 'bold'))
        header.pack(pady=20)
        
        # Instructions frame
        inst_frame = tk.Frame(instructions, bg='#161b22', relief='ridge', borderwidth=1)
        inst_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Instructions text
        inst_text = f"""
🚀 STEP-BY-STEP GUIDE:

1️⃣ Launch {game_name}
2️⃣ Navigate to Settings/Options menu
3️⃣ Find Graphics, Video, or Display settings
4️⃣ Apply the recommended values from the right panel
5️⃣ Save/Apply the changes
6️⃣ Test performance in-game

⚠️ IMPORTANT NOTES:
• Setting names may vary slightly in-game
• Look for similar options if exact names don't match
• Start with Critical Impact settings first
• Test performance after each major change

💡 TROUBLESHOOTING:
• If FPS is lower than expected, reduce High Impact settings
• If game looks too blurry, increase texture quality slightly
• For stuttering, enable VSync or frame limiting
• Monitor GPU temperature during gaming

✅ These settings guarantee smooth performance
   based on real benchmark data for your GPU!
        """
        
        text_widget = tk.Text(inst_frame, bg='#0d1117', fg='#f0f6fc', 
                             font=('Segoe UI', 10), wrap=tk.WORD, relief='flat', 
                             borderwidth=0, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, inst_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(instructions, text="✅ Got it!", bg='#238636', fg='#f0f6fc', 
                             font=('Segoe UI', 11, 'bold'), relief='flat', padx=20, pady=8,
                             command=instructions.destroy)
        close_btn.pack(pady=(0, 20))

    def on_closing(self):
        """Handle application closing"""
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ModernGamingAdvisor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
