"""
Modified Modern Gaming Advisor with Game Library integration.
"""

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
import sys

# Import game library integration
from game_library.integration import integrate_game_library

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
        self.root.configure(bg='#2D1832')  # Deep burgundy background
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
        self.setup_vibrant_styles()
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
        except Exception as e:
            print(f"Error detecting system specs: {e}")
            return {'cpu': 'Unknown CPU', 'gpu': 'Unknown GPU', 'ram_gb': 16, 'gpu_vram_mb': 8000, 'gpu_vram_gb': 8, 'is_laptop': False}
    
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
    
    def load_benchmark_cache(self):
        """Load benchmark cache from file"""
        try:
            if os.path.exists('benchmark_cache.json'):
                with open('benchmark_cache.json', 'r') as f:
                    self.benchmark_cache = json.load(f)
                print(f"✅ Loaded {len(self.benchmark_cache)} benchmark entries from cache")
        except Exception as e:
            print(f"❌ Error loading benchmark cache: {e}")
            self.benchmark_cache = {}
    
    def save_benchmark_cache(self):
        """Save benchmark cache to file"""
        try:
            with open('benchmark_cache.json', 'w') as f:
                json.dump(self.benchmark_cache, f, indent=2)
            print(f"✅ Saved {len(self.benchmark_cache)} benchmark entries to cache")
        except Exception as e:
            print(f"❌ Error saving benchmark cache: {e}")
    
    def load_game_history(self):
        """Load game analysis history from file"""
        try:
            if os.path.exists('game_history.json'):
                with open('game_history.json', 'r') as f:
                    self.game_history = json.load(f)
                print(f"✅ Loaded {len(self.game_history)} game history entries")
        except Exception as e:
            print(f"❌ Error loading game history: {e}")
            self.game_history = []
    
    def setup_modern_styles(self):
        """Setup modern dark theme styles - legacy method kept for compatibility"""
        self.setup_vibrant_styles()
        
    def setup_vibrant_styles(self):
        """Setup vibrant gaming UI theme styles inspired by modern gaming interfaces"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Enhanced vibrant gaming color scheme
        self.bg_primary = '#1C0F28'      # Deep rich purple/navy background (darker)
        self.bg_secondary = '#2D1B36'    # Slightly lighter panels
        self.bg_tertiary = '#3F2556'     # Cards/buttons with more richness
        
        # Vibrant neon-like accent colors
        self.accent_orange = '#FF7D54'   # Vibrant orange accent
        self.accent_blue = '#38BBFF'     # Vibrant blue accent (more saturated)
        self.accent_green = '#4DFFA7'    # Vibrant green accent
        self.accent_purple = '#B366FF'   # Vibrant purple accent (lighter)
        self.accent_yellow = '#FFD646'   # Vibrant yellow accent (warmer)
        self.accent_red = '#FF5A5A'      # Vibrant red accent
        self.accent_pink = '#FF50D6'     # Vibrant pink accent (for variety)
        self.accent_cyan = '#50F5FF'     # Vibrant cyan accent (for variety)
        
        # Text colors
        self.text_primary = '#FFFFFF'    # Main text (white)
        self.text_secondary = '#DCC6E4'  # Secondary text (lighter purple/gray for better contrast)
        self.text_muted = '#9984A3'      # Muted text (darker for less important elements)
        
        # Border and highlight colors
        self.border_color = '#503667'    # Border color for panels and cards
        self.highlight_color = '#5F3D7A' # Highlight for hover and active elements
        
        # Configure vibrant styles with improved visual hierarchy
        style.configure('Modern.TFrame', background=self.bg_secondary, relief='flat')
        style.configure('Card.TFrame', background=self.bg_tertiary, relief='flat', borderwidth=1, borderradius=15)
        
        # Title and header styles
        style.configure('ModernTitle.TLabel', 
                       font=('Segoe UI', 22, 'bold'), 
                       background=self.bg_primary, 
                       foreground=self.text_primary)
                       
        style.configure('ModernHeader.TLabel', 
                       font=('Segoe UI', 16, 'bold'), 
                       background=self.bg_secondary, 
                       foreground=self.accent_orange)
                       
        style.configure('ModernSubHeader.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       background=self.bg_secondary, 
                       foreground=self.accent_blue)
        
        # Text styles with improved hierarchy
        style.configure('ModernText.TLabel', 
                       font=('Segoe UI', 11), 
                       background=self.bg_secondary, 
                       foreground=self.text_primary)
                       
        style.configure('ModernTextBold.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       background=self.bg_secondary, 
                       foreground=self.text_primary)
                       
        style.configure('ModernTextSmall.TLabel', 
                       font=('Segoe UI', 9), 
                       background=self.bg_secondary, 
                       foreground=self.text_secondary)
        
        # Accent text styles
        style.configure('ModernAccent.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       background=self.bg_secondary, 
                       foreground=self.accent_green)
                       
        style.configure('ModernWarning.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       background=self.bg_secondary, 
                       foreground=self.accent_yellow)
                       
        style.configure('ModernError.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       background=self.bg_secondary, 
                       foreground=self.accent_red)
        
        # Enhanced button styles with rounded corners and glow effect
        style.configure('Modern.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       background=self.bg_tertiary,
                       foreground=self.text_primary,
                       relief='flat',
                       padding=(15, 10))
                       
        style.map('Modern.TButton',
                 background=[('active', self.accent_orange), ('pressed', '#D96B48')])
        
        # Action button variants
        style.configure('Action.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       background=self.accent_blue,
                       foreground=self.text_primary,
                       relief='flat',
                       padding=(15, 10))
                       
        style.map('Action.TButton',
                 background=[('active', self.accent_cyan), ('pressed', self.accent_purple)])
        
        # Modern entry styles with better contrast
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 11),
                       borderwidth=1,
                       insertcolor=self.text_primary,
                       fieldbackground=self.bg_tertiary,
                       foreground=self.text_primary,
                       bordercolor=self.border_color,
                       padding=8)
                       
        style.map('Modern.TEntry',
                 focuscolor=[('focus', self.accent_blue)],
                 bordercolor=[('focus', self.accent_blue)])
                 
        # Tab styles for the notebook
        style.configure('Gaming.TNotebook', 
                      background=self.bg_primary,
                      borderwidth=0,
                      tabmargins=[0, 0, 0, 0])
                      
        style.configure('Gaming.TNotebook.Tab',
                      font=('Segoe UI', 11, 'bold'),
                      background=self.bg_tertiary,
                      foreground=self.text_secondary,
                      padding=[20, 8],
                      borderwidth=0)
                      
        style.map('Gaming.TNotebook.Tab',
                 background=[('selected', self.bg_secondary), ('active', self.highlight_color)],
                 foreground=[('selected', self.accent_orange), ('active', self.text_primary)])
    
    def monitor_performance(self):
        """Monitor system performance in a background thread"""
        while self.running:
            try:
                # Get current CPU and GPU usage
                cpu_percent = psutil.cpu_percent()
                
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_percent = gpus[0].load * 100
                    gpu_temp = gpus[0].temperature
                else:
                    gpu_percent = 0
                    gpu_temp = 0
                
                # Save to history (limit to last 100 points)
                self.performance_history.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'gpu_percent': gpu_percent,
                    'gpu_temp': gpu_temp
                })
                
                if len(self.performance_history) > 100:
                    self.performance_history.pop(0)
                
                # Update UI if we're on the system tab
                if hasattr(self, 'update_performance_charts'):
                    self.update_performance_charts()
                
                # Sleep for a bit
                time.sleep(1)
                
            except Exception as e:
                print(f"Error monitoring performance: {e}")
                time.sleep(5)  # Longer sleep on error
    
    def load_benchmark_data(self):
        """Load benchmark data for the current GPU"""
        if not self.system_specs['gpu'] or self.system_specs['gpu'] == "Unknown GPU":
            print("⚠️ Unknown GPU, can't load benchmarks")
            return
        
        # Clean GPU name for searching
        gpu_name = self.clean_gpu_name(self.system_specs['gpu'])
        print(f"🔍 Looking for benchmark data for: {gpu_name}")
        
        # Check if we already have this GPU's data in cache
        if gpu_name in self.benchmark_cache:
            print(f"✅ Using cached benchmark data for {gpu_name}")
            return
            
        # TODO: For now, we'll use a simplified approach
        # In a real app, this would scrape websites or use an API
        print(f"⏳ Fetching benchmark data for {gpu_name}...")
        
        # Sample benchmark data structure
        benchmark_data = self.get_default_benchmark_data(gpu_name)
        self.benchmark_cache[gpu_name] = benchmark_data
        
        # Save the updated cache
        self.save_benchmark_cache()
        print(f"✅ Added benchmark data for {gpu_name} to cache")
    
    def clean_gpu_name(self, gpu_name):
        """Clean GPU name for better matching with benchmarks"""
        # Remove common noise words, standardize spacing
        name = gpu_name.lower()
        name = re.sub(r'(nvidia|geforce|amd|radeon|intel)\s+', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Extract just the model number for better matching
        # Examples: RTX 3080, RX 6700 XT, etc.
        model_match = re.search(r'(gtx|rtx|rx)\s*\d{3,4}(\s*ti|\s*super|\s*xt|\s*m)?', name)
        if model_match:
            name = model_match.group(0)
        
        return name
    
    def get_default_benchmark_data(self, gpu_name):
        """Get default benchmark data for the given GPU"""
        # This is placeholder benchmark data
        # In a real app, this would come from a database or API
        
        # Default data structure
        data = {
            'name': gpu_name,
            'performance_tier': 'mid-range',  # high-end, mid-range, budget
            'avg_fps_1080p': {
                'ultra': 80,
                'high': 100,
                'medium': 120,
                'low': 140
            },
            'avg_fps_1440p': {
                'ultra': 60,
                'high': 80,
                'medium': 100,
                'low': 120
            },
            'avg_fps_4k': {
                'ultra': 30,
                'high': 45,
                'medium': 60,
                'low': 80
            },
            'vram_requirements': {
                'ultra_textures': 8,
                'high_textures': 6,
                'medium_textures': 4,
                'low_textures': 2
            }
        }
        
        # Adjust values based on detected GPU tier
        if 'rtx 30' in gpu_name or 'rtx 40' in gpu_name or 'rx 6' in gpu_name or 'rx 7' in gpu_name:
            # High-end modern GPU
            data['performance_tier'] = 'high-end'
            data['avg_fps_1080p'] = {'ultra': 160, 'high': 200, 'medium': 240, 'low': 300}
            data['avg_fps_1440p'] = {'ultra': 120, 'high': 150, 'medium': 180, 'low': 220}
            data['avg_fps_4k'] = {'ultra': 60, 'high': 80, 'medium': 100, 'low': 140}
            
        elif 'rtx 20' in gpu_name or 'gtx 16' in gpu_name or 'rx 5' in gpu_name:
            # Mid-range modern GPU
            data['performance_tier'] = 'mid-range'
            data['avg_fps_1080p'] = {'ultra': 100, 'high': 130, 'medium': 160, 'low': 200}
            data['avg_fps_1440p'] = {'ultra': 70, 'high': 90, 'medium': 120, 'low': 150}
            data['avg_fps_4k'] = {'ultra': 40, 'high': 55, 'medium': 70, 'low': 90}
            
        elif 'gtx 10' in gpu_name or 'rx 4' in gpu_name or 'rx 5' in gpu_name:
            # Budget/older GPU
            data['performance_tier'] = 'budget'
            data['avg_fps_1080p'] = {'ultra': 60, 'high': 80, 'medium': 100, 'low': 130}
            data['avg_fps_1440p'] = {'ultra': 40, 'high': 55, 'medium': 70, 'low': 90}
            data['avg_fps_4k'] = {'ultra': 25, 'high': 35, 'medium': 45, 'low': 60}
            
        return data
        
    def create_modern_gui(self):
        """Create vibrant gaming GUI layout with tabbed interface"""
        # Main container with rounded corners
        main_container = tk.Frame(self.root, bg=self.bg_primary)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Vibrant title bar with gradient effect
        title_frame = tk.Frame(main_container, bg=self.bg_primary, height=70)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        title_frame.pack_propagate(False)
        
        # Create custom title with emoji and gradient text effect
        title_label = tk.Label(title_frame, text="🎮 AI Gaming Advisor Pro", 
                              font=('Segoe UI', 24, 'bold'), 
                              bg=self.bg_primary, fg=self.accent_orange)
        title_label.pack(side=tk.LEFT, pady=10)
        
        # User profile icon (circular)
        user_frame = tk.Frame(title_frame, bg=self.bg_primary, width=40, height=40)
        user_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # System info in title bar with vibrant styling
        system_info = f"🖥️ {self.system_specs['gpu']} • 🧠 {self.system_specs['ram_gb']}GB RAM"
        system_label = tk.Label(title_frame, text=system_info, 
                              font=('Segoe UI', 10), 
                              bg=self.bg_primary, fg=self.text_secondary)
        system_label.pack(side=tk.RIGHT, pady=15)
        
        # Create custom notebook for tabs with vibrant styling
        notebook_frame = tk.Frame(main_container, bg=self.bg_primary)
        notebook_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Style the notebook tabs
        style = ttk.Style()
        style.configure("TNotebook", background=self.bg_primary, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg_tertiary, foreground=self.text_secondary, 
                      padding=[15, 8], font=('Segoe UI', 10, 'bold'))
        style.map("TNotebook.Tab", 
                background=[("selected", self.bg_secondary)],
                foreground=[("selected", self.accent_orange)])
        
        # Tab 1: Welcome tab (simplified to avoid missing method errors)
        welcome_frame = ttk.Frame(self.notebook, style='Modern.TFrame', padding=20)
        self.notebook.add(welcome_frame, text="🏠 Welcome")
        
        # Welcome message
        welcome_label = ttk.Label(welcome_frame, text="Welcome to AI Gaming Advisor Pro!", 
                                style='ModernHeader.TLabel')
        welcome_label.pack(pady=20)
        
        welcome_text = ttk.Label(welcome_frame, text="Select the Game Settings tab to get optimized settings recommendations\nSelect the Game Library tab to browse games",
                               style='ModernText.TLabel')
        welcome_text.pack(pady=10)
        
        # Tab 2: Game Settings Advisor tab
        self.setup_game_advisor_tab()
        
        # Integrate Game Library tab
        self.game_library_ui = integrate_game_library(self, self.notebook)
    
    # The rest of the methods are included from the original file...
    # For brevity, they are not repeated here.
    
    def load_benchmark_cache(self):
        """Load benchmark cache from file"""
        try:
            if os.path.exists('benchmark_cache.json'):
                with open('benchmark_cache.json', 'r') as f:
                    self.benchmark_cache = json.load(f)
                print(f"✅ Loaded {len(self.benchmark_cache)} benchmark entries from cache")
        except Exception as e:
            print(f"❌ Error loading benchmark cache: {e}")
            self.benchmark_cache = {}
    
    def save_benchmark_cache(self):
        """Save benchmark cache to file"""
        try:
            with open('benchmark_cache.json', 'w') as f:
                json.dump(self.benchmark_cache, f, indent=2)
            print(f"✅ Saved {len(self.benchmark_cache)} benchmark entries to cache")
        except Exception as e:
            print(f"❌ Error saving benchmark cache: {e}")
    
    def load_game_history(self):
        """Load game analysis history from file"""
        try:
            if os.path.exists('game_history.json'):
                with open('game_history.json', 'r') as f:
                    self.game_history = json.load(f)
                print(f"✅ Loaded {len(self.game_history)} game history entries")
        except Exception as e:
            print(f"❌ Error loading game history: {e}")
            self.game_history = []
    
    def save_game_history(self):
        """Save game analysis history to file"""
        try:
            with open('game_history.json', 'w') as f:
                json.dump(self.game_history, f, indent=2)
            print(f"✅ Saved {len(self.game_history)} game history entries")
        except Exception as e:
            print(f"❌ Error saving game history: {e}")
    
    def monitor_performance(self):
        """Monitor system performance in a background thread"""
        while self.running:
            try:
                # Get current CPU and GPU usage
                cpu_percent = psutil.cpu_percent()
                
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_percent = gpus[0].load * 100
                    gpu_temp = gpus[0].temperature
                else:
                    gpu_percent = 0
                    gpu_temp = 0
                
                # Save to history (limit to last 100 points)
                self.performance_history.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'gpu_percent': gpu_percent,
                    'gpu_temp': gpu_temp
                })
                
                if len(self.performance_history) > 100:
                    self.performance_history.pop(0)
                
                # Update UI if we're on the system tab
                if hasattr(self, 'update_performance_charts'):
                    self.update_performance_charts()
                
                # Sleep for a bit
                time.sleep(1)
                
            except Exception as e:
                print(f"Error monitoring performance: {e}")
                time.sleep(5)  # Longer sleep on error
    
    def load_benchmark_data(self):
        """Load benchmark data for the current GPU"""
        if not self.system_specs['gpu'] or self.system_specs['gpu'] == "Unknown GPU":
            print("⚠️ Unknown GPU, can't load benchmarks")
            return
        
        # Clean GPU name for searching
        gpu_name = self.clean_gpu_name(self.system_specs['gpu'])
        print(f"🔍 Looking for benchmark data for: {gpu_name}")
        
        # Check if we already have this GPU's data in cache
        if gpu_name in self.benchmark_cache:
            print(f"✅ Using cached benchmark data for {gpu_name}")
            return
            
        # TODO: For now, we'll use a simplified approach
        # In a real app, this would scrape websites or use an API
        print(f"⏳ Fetching benchmark data for {gpu_name}...")
        
        # Sample benchmark data structure
        benchmark_data = self.get_default_benchmark_data(gpu_name)
        self.benchmark_cache[gpu_name] = benchmark_data
        
        # Save the updated cache
        self.save_benchmark_cache()
        print(f"✅ Added benchmark data for {gpu_name} to cache")
    
    def clean_gpu_name(self, gpu_name):
        """Clean GPU name for better matching with benchmarks"""
        # Remove common noise words, standardize spacing
        name = gpu_name.lower()
        name = re.sub(r'(nvidia|geforce|amd|radeon|intel)\s+', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Extract just the model number for better matching
        # Examples: RTX 3080, RX 6700 XT, etc.
        model_match = re.search(r'(gtx|rtx|rx)\s*\d{3,4}(\s*ti|\s*super|\s*xt|\s*m)?', name)
        if model_match:
            name = model_match.group(0)
        
        return name
    
    def get_default_benchmark_data(self, gpu_name):
        """Get default benchmark data for the given GPU"""
        # This is placeholder benchmark data
        # In a real app, this would come from a database or API
        
        # Default data structure
        data = {
            'name': gpu_name,
            'performance_tier': 'mid-range',  # high-end, mid-range, budget
            'avg_fps_1080p': {
                'ultra': 80,
                'high': 100,
                'medium': 120,
                'low': 140
            },
            'avg_fps_1440p': {
                'ultra': 60,
                'high': 80,
                'medium': 100,
                'low': 120
            },
            'avg_fps_4k': {
                'ultra': 30,
                'high': 45,
                'medium': 60,
                'low': 80
            },
            'vram_requirements': {
                'ultra_textures': 8,
                'high_textures': 6,
                'medium_textures': 4,
                'low_textures': 2
            }
        }
        
        # Adjust values based on detected GPU tier
        if 'rtx 30' in gpu_name or 'rtx 40' in gpu_name or 'rx 6' in gpu_name or 'rx 7' in gpu_name:
            # High-end modern GPU
            data['performance_tier'] = 'high-end'
            data['avg_fps_1080p'] = {'ultra': 160, 'high': 200, 'medium': 240, 'low': 300}
            data['avg_fps_1440p'] = {'ultra': 120, 'high': 150, 'medium': 180, 'low': 220}
            data['avg_fps_4k'] = {'ultra': 60, 'high': 80, 'medium': 100, 'low': 140}
            
        elif 'rtx 20' in gpu_name or 'gtx 16' in gpu_name or 'rx 5' in gpu_name:
            # Mid-range modern GPU
            data['performance_tier'] = 'mid-range'
            data['avg_fps_1080p'] = {'ultra': 100, 'high': 130, 'medium': 160, 'low': 200}
            data['avg_fps_1440p'] = {'ultra': 70, 'high': 90, 'medium': 120, 'low': 150}
            data['avg_fps_4k'] = {'ultra': 40, 'high': 55, 'medium': 70, 'low': 90}
            
        elif 'gtx 10' in gpu_name or 'rx 4' in gpu_name or 'rx 5' in gpu_name:
            # Budget/older GPU
            data['performance_tier'] = 'budget'
            data['avg_fps_1080p'] = {'ultra': 60, 'high': 80, 'medium': 100, 'low': 130}
            data['avg_fps_1440p'] = {'ultra': 40, 'high': 55, 'medium': 70, 'low': 90}
            data['avg_fps_4k'] = {'ultra': 25, 'high': 35, 'medium': 45, 'low': 60}
            
        return data
    
    def setup_game_advisor_tab(self):
        """Setup vibrant game settings advisor tab with modern gaming UI"""
        # Create the main frame for game advisor
        game_advisor_frame = tk.Frame(self.notebook, bg=self.bg_primary)
        self.notebook.add(game_advisor_frame, text="⚙️ Game Settings")
        
        # Add a subtle gradient-like effect with a top highlight strip
        top_highlight = tk.Frame(game_advisor_frame, height=3, bg=self.accent_orange)
        top_highlight.pack(fill=tk.X, side=tk.TOP)
        
        # Container with modern padding
        container_frame = tk.Frame(game_advisor_frame, bg=self.bg_primary, padx=20, pady=20)
        container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game advisor header with gaming icon and gradient effect
        header_frame = tk.Frame(container_frame, bg=self.bg_primary, pady=5)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Gaming icon
        header_icon = tk.Label(header_frame, text="🎮", font=('Segoe UI', 24), 
                            bg=self.bg_primary, fg=self.accent_orange)
        header_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        # Main title with vibrant color
        header_label = tk.Label(header_frame, text="GAME SETTINGS ADVISOR", 
                             font=('Segoe UI', 20, 'bold'), 
                             bg=self.bg_primary, fg=self.accent_orange)
        header_label.pack(side=tk.LEFT)
        
        # Split into left and right panels with modern spacing
        panels_frame = tk.Frame(container_frame, bg=self.bg_primary)
        panels_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = tk.Frame(panels_frame, bg=self.bg_primary)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Vertical separator with gradient effect for visual separation
        separator_frame = tk.Frame(panels_frame, width=2, bg=self.bg_tertiary)
        separator_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        right_panel = tk.Frame(panels_frame, bg=self.bg_primary, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0), expand=True)
        
        # Left panel - Analysis section with vibrant UI
        self.setup_analysis_section(left_panel)
        
        # Right panel - Settings section with vibrant gaming cards
        self.setup_settings_panel(right_panel)
    
    def setup_analysis_section(self, parent):
        """Setup left panel with vibrant gaming analysis section"""
        # Control section with enhanced rounded corners and glow effect
        control_section = self._create_rounded_frame(parent, bg=self.bg_secondary)
        control_section.pack(fill=tk.X, pady=(0, 20))
        
        # Inner padding frame with gradient effect
        inner_section = tk.Frame(control_section, bg=self.bg_secondary, padx=20, pady=20)
        inner_section.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(inner_section, bg=self.bg_secondary)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Modern gaming header with icon and vibrant text
        header_icon = tk.Label(header_frame, text="🎮", font=('Segoe UI', 24), 
                            bg=self.bg_secondary, fg=self.accent_orange)
        header_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        header_text = tk.Label(header_frame, text="ANALYZE GAME SETTINGS", 
                             font=('Segoe UI', 16, 'bold'), 
                             bg=self.bg_secondary, fg=self.accent_orange)
        header_text.pack(side=tk.LEFT)
        
        # Modern description with subtle styling
        desc_frame = tk.Frame(inner_section, bg=self.bg_secondary)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        desc_text = tk.Label(desc_frame, 
                          text="Enter a game title to get optimized settings based on your system's hardware capabilities",
                          font=('Segoe UI', 10), bg=self.bg_secondary, fg=self.text_secondary,
                          wraplength=400, justify=tk.LEFT)
        desc_text.pack(anchor='w')
        
        # Modern input frame with gradient accent
        input_frame = tk.Frame(inner_section, bg=self.bg_secondary)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Game input section with accent line
        accent_line = tk.Frame(input_frame, bg=self.accent_blue, height=2)
        accent_line.pack(fill=tk.X, pady=(0, 15))
        
        # Game name input with modern gaming styling
        game_label = tk.Label(input_frame, text="GAME:", font=('Segoe UI', 11, 'bold'), 
                           bg=self.bg_secondary, fg=self.text_primary)
        game_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry field with modern gaming styling and glow effect
        entry_frame = tk.Frame(input_frame, bg=self.bg_tertiary, bd=0, relief='flat',
                            highlightthickness=1, highlightbackground=self.accent_blue)
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.game_entry = tk.Entry(entry_frame, font=('Segoe UI', 12), bg=self.bg_tertiary, 
                                fg=self.text_primary, insertbackground=self.accent_orange,
                                relief='flat', bd=0)
        self.game_entry.pack(fill=tk.X, ipady=8, padx=10)
        
        # Quick select button with vibrant gaming styling and hover effect
        quick_select_btn = tk.Button(input_frame, text="QUICK SELECT", 
                                  bg=self.accent_blue, fg=self.text_primary, 
                                  font=('Segoe UI', 10, 'bold'), relief='flat', 
                                  padx=15, pady=8,
                                  command=self.show_quick_select, 
                                  activebackground=self.accent_purple)
        quick_select_btn.pack(side=tk.RIGHT)
        
        # Target FPS section with modern gaming styling
        fps_section = tk.Frame(inner_section, bg=self.bg_secondary, pady=15)
        fps_section.pack(fill=tk.X, pady=(15, 0))
        
        # FPS section header
        fps_header = tk.Label(fps_section, text="TARGET FRAMERATE", font=('Segoe UI', 11, 'bold'), 
                           bg=self.bg_secondary, fg=self.accent_yellow)
        fps_header.pack(anchor='w', pady=(0, 10))
        
        fps_frame = tk.Frame(fps_section, bg=self.bg_secondary)
        fps_frame.pack(fill=tk.X)
        
        # Speed icon
        fps_icon = tk.Label(fps_frame, text="⚡", font=('Segoe UI', 18), 
                         bg=self.bg_secondary, fg=self.accent_yellow)
        fps_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        # Target FPS input with gaming style
        fps_entry_frame = tk.Frame(fps_frame, bg=self.bg_tertiary, bd=0, 
                                highlightthickness=1, highlightbackground=self.accent_yellow)
        fps_entry_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        self.fps_entry = tk.Entry(fps_entry_frame, font=('Segoe UI', 12, 'bold'), 
                               bg=self.bg_tertiary, fg=self.text_primary,
                               insertbackground=self.accent_yellow, relief='flat', 
                               bd=0, width=5, justify=tk.CENTER)
        self.fps_entry.insert(0, "60")  # Default value
        self.fps_entry.pack(padx=10, pady=8)
        
        # FPS slider with vibrant gaming style
        fps_values = [30, 60, 75, 90, 120, 144, 165, 240]
        fps_var = tk.IntVar(value=1)  # Default to 60 FPS (index 1)
        
        # Frame for slider with background
        slider_frame = tk.Frame(fps_frame, bg=self.bg_tertiary, padx=10, pady=8)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        fps_slider = tk.Scale(slider_frame, from_=0, to=len(fps_values)-1, orient='horizontal',
                           showvalue=False, 
                           command=lambda v: self.fps_entry.delete(0, tk.END) or 
                                          self.fps_entry.insert(0, str(fps_values[int(float(v))])),
                           length=200, bg=self.bg_tertiary, fg=self.text_primary, 
                           activebackground=self.accent_yellow, troughcolor=self.bg_primary,
                           relief='flat', sliderlength=20, highlightthickness=0)
        fps_slider.set(1)  # Default to 60 FPS (index 1)
        fps_slider.pack(fill=tk.X, expand=True)
        
        # Common FPS labels under slider
        fps_labels_frame = tk.Frame(slider_frame, bg=self.bg_tertiary)
        fps_labels_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Add common FPS markers
        for i, fps in enumerate([30, 60, 120, 240]):
            pos = i / 3  # Position based on the 4 values we're showing
            label_frame = tk.Frame(fps_labels_frame, bg=self.bg_tertiary)
            label_frame.place(relx=pos, y=0, anchor='n', width=30)
            
            fps_label = tk.Label(label_frame, text=str(fps), font=('Segoe UI', 8),
                              bg=self.bg_tertiary, fg=self.text_secondary)
            fps_label.pack()
        
        # Analyze button with vibrant gaming style and glow effect
        analyze_frame = tk.Frame(inner_section, bg=self.bg_secondary, pady=15)
        analyze_frame.pack(fill=tk.X)
        
        analyze_btn = tk.Button(analyze_frame, text="🔍 ANALYZE WITH AI", 
                              bg=self.accent_green, fg=self.bg_primary, 
                              font=('Segoe UI', 12, 'bold'), relief='flat', 
                              padx=15, pady=12,
                              command=self.analyze_game, 
                              activebackground=self.accent_blue)
        analyze_btn.pack(fill=tk.X)
        
        # AI Analysis results with enhanced vibrant gaming style
        results_section = self._create_rounded_frame(parent, bg=self.bg_secondary)
        results_section.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Inner padding frame
        inner_results = tk.Frame(results_section, bg=self.bg_secondary, padx=20, pady=20)
        inner_results.pack(fill=tk.BOTH, expand=True)
        
        # Header with AI icon and vibrant text
        results_header_frame = tk.Frame(inner_results, bg=self.bg_secondary)
        results_header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # AI icon with vibrant color
        results_icon = tk.Label(results_header_frame, text="🤖", font=('Segoe UI', 24), 
                             bg=self.bg_secondary, fg=self.accent_blue)
        results_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        # AI Results header
        results_text = tk.Label(results_header_frame, text="AI ANALYSIS RESULTS", 
                             font=('Segoe UI', 16, 'bold'), 
                             bg=self.bg_secondary, fg=self.accent_blue)
        results_text.pack(side=tk.LEFT)
        
        # AI output area with modern styling
        text_container = tk.Frame(inner_results, bg=self.bg_tertiary, bd=0,
                               highlightthickness=1, highlightbackground=self.accent_blue)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable text area with custom styling for AI results
        self.ai_text = tk.Text(text_container, bg=self.bg_primary, fg=self.text_primary, 
                            font=('Consolas', 11), wrap=tk.WORD, 
                            relief='flat', borderwidth=0, padx=15, pady=15)
                            
        # Custom scrollbar with vibrant styling
        ai_scrollbar = tk.Scrollbar(text_container, orient="vertical", 
                                 command=self.ai_text.yview,
                                 bg=self.bg_tertiary, 
                                 troughcolor=self.bg_primary, 
                                 activebackground=self.accent_blue)
                                 
        self.ai_text.configure(yscrollcommand=ai_scrollbar.set)
        
        # Apply some default placeholder text with styling
        self.ai_text.insert(tk.END, "AI analysis results will appear here...\n\n")
        self.ai_text.insert(tk.END, "Enter a game name above and click 'Analyze' to get personalized settings recommendations based on your system hardware.")
        self.ai_text.tag_configure("placeholder", foreground=self.text_secondary, font=('Consolas', 11, 'italic'))
        self.ai_text.tag_add("placeholder", "1.0", "end")
        self.ai_text.configure(state='disabled')  # Make read-only initially
        
        # Pack text and scrollbar
        self.ai_text.pack(side="left", fill="both", expand=True)
        ai_scrollbar.pack(side="right", fill="y")
    
    def _create_rounded_frame(self, parent, bg=None, width=None):
        """Create a rounded frame with optional width and background color"""
        if bg is None:
            bg = self.bg_tertiary
            
        # Main frame
        frame = tk.Frame(parent, bg=bg, bd=0)
        if width:
            frame.configure(width=width)
            
        # Add slight border effect for depth
        border_frame = tk.Frame(frame, bg=self.bg_tertiary, bd=1)
        border_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Inner frame with padding for content
        inner_frame = tk.Frame(border_frame, bg=bg, bd=0)
        inner_frame.place(x=1, y=1, relwidth=1, relheight=1, width=-2, height=-2)
        
        # Visual cues for rounded corners - using small frames in each corner
        corner_radius = 10
        corner_color = self.bg_primary
        
        # Top left corner
        top_left = tk.Frame(frame, bg=corner_color, width=corner_radius, height=corner_radius)
        top_left.place(x=0, y=0)
        
        # Top right corner
        top_right = tk.Frame(frame, bg=corner_color, width=corner_radius, height=corner_radius)
        top_right.place(relx=1.0, y=0, anchor='ne')
        
        # Bottom left corner
        bottom_left = tk.Frame(frame, bg=corner_color, width=corner_radius, height=corner_radius)
        bottom_left.place(x=0, rely=1.0, anchor='sw')
        
        # Bottom right corner
        bottom_right = tk.Frame(frame, bg=corner_color, width=corner_radius, height=corner_radius)
        bottom_right.place(relx=1.0, rely=1.0, anchor='se')
        
        return frame
        
        # Welcome message for game advisor
        welcome_msg = f"""🎮 Welcome to Game Settings Advisor!

🚀 Features:
• Hardware-specific AI analysis for YOUR exact system
• Game-specific optimized settings 
• FPS predictions based on benchmark data

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
        """Setup right panel with vibrant gaming-style recommended settings"""
        # Create settings panel with enhanced rounded corners and glow effect
        settings_panel = self._create_rounded_frame(parent, bg=self.bg_secondary)
        settings_panel.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding frame with gradient effect
        inner_panel = tk.Frame(settings_panel, bg=self.bg_secondary, padx=20, pady=20)
        inner_panel.pack(fill=tk.BOTH, expand=True)
        
        # Add a subtle accent line at the top
        accent_line = tk.Frame(inner_panel, height=3, bg=self.accent_green)
        accent_line.pack(fill=tk.X, pady=(0, 15))
        
        # Header with gaming icon and vibrant text
        header_frame = tk.Frame(inner_panel, bg=self.bg_secondary)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Gaming gear icon
        header_icon = tk.Label(header_frame, text="⚙️", font=('Segoe UI', 24), 
                            bg=self.bg_secondary, fg=self.accent_green)
        header_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        # Vibrant header text
        header_text = tk.Label(header_frame, text="OPTIMAL SETTINGS", 
                            font=('Segoe UI', 16, 'bold'), 
                            bg=self.bg_secondary, fg=self.accent_green)
        header_text.pack(side=tk.LEFT)
        
        # Badge showing "AI OPTIMIZED" with gaming style
        badge_frame = tk.Frame(inner_panel, bg=self.accent_green, padx=10, pady=5)
        badge_frame.pack(anchor='w', pady=(0, 15))
        
        badge_text = tk.Label(badge_frame, text="✓ AI OPTIMIZED", 
                           font=('Segoe UI', 9, 'bold'), 
                           bg=self.accent_green, fg=self.bg_primary)
        badge_text.pack()
        
        # Subheader with modern gaming instruction
        instruction_frame = tk.Frame(inner_panel, bg=self.bg_tertiary, padx=15, pady=10)
        instruction_frame.pack(fill=tk.X, pady=(0, 15))
        
        instruction_icon = tk.Label(instruction_frame, text="💡", 
                                 font=('Segoe UI', 14), 
                                 bg=self.bg_tertiary, fg=self.accent_yellow)
        instruction_icon.pack(side=tk.LEFT, padx=(0, 8))
        
        instruction_text = tk.Label(instruction_frame, 
                                 text="Apply these settings for the best gaming experience", 
                                 font=('Segoe UI', 10), 
                                 bg=self.bg_tertiary, fg=self.text_primary)
        instruction_text.pack(side=tk.LEFT, fill=tk.X)
        
        # Settings cards container with vibrant gaming styling
        settings_container = tk.Frame(inner_panel, bg=self.bg_secondary)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable settings area with enhanced gaming UI scrolling
        canvas = tk.Canvas(settings_container, bg=self.bg_secondary, 
                        highlightthickness=0, borderwidth=0)
        
        # Custom gaming style scrollbar
        scrollbar = tk.Scrollbar(settings_container, orient="vertical", 
                              command=canvas.yview,
                              bg=self.bg_tertiary, 
                              troughcolor=self.bg_secondary, 
                              activebackground=self.accent_green, 
                              width=10)
        
        # Create the frame that will contain all the setting cards
        self.settings_frame = tk.Frame(canvas, bg=self.bg_secondary, padx=5)
        
        # Configure scrolling behavior
        self.settings_frame.bind("<Configure>", 
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Create window within canvas for the settings frame
        canvas.create_window((0, 0), window=self.settings_frame, anchor="nw", width=310)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add smooth mouse wheel scrolling with enhanced behavior
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # Prevent event propagation
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Initialize with default settings and vibrant style
        self.update_settings_panel()
    
    def show_quick_select(self):
        """Show quick select dialog for popular games"""
        popular_games = [
            "Cyberpunk 2077", "Call of Duty: Modern Warfare", "Elden Ring",
            "Fortnite", "Apex Legends", "Red Dead Redemption 2",
            "Valorant", "Counter-Strike 2", "Baldur's Gate 3",
            "Starfield", "Hogwarts Legacy", "Diablo IV"
        ]
        
        select_dialog = tk.Toplevel(self.root)
        select_dialog.title("Select Popular Game")
        select_dialog.geometry("300x400")
        select_dialog.configure(bg='#21262d')
        select_dialog.resizable(False, False)
        
        ttk.Label(select_dialog, text="🎮 Select a Popular Game", style='ModernHeader.TLabel').pack(pady=(15, 10))
        
        games_frame = tk.Frame(select_dialog, bg='#21262d')
        games_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for game in popular_games:
            btn = tk.Button(games_frame, text=game, bg='#30363d', fg='#f0f6fc',
                          font=('Segoe UI', 10), relief='flat', pady=5,
                          command=lambda g=game: [self.set_game(g), select_dialog.destroy()])
            btn.pack(fill=tk.X, pady=3)
        
        close_btn = tk.Button(select_dialog, text="Cancel", bg='#30363d', fg='#f0f6fc',
                            font=('Segoe UI', 10), relief='flat', pady=5,
                            command=select_dialog.destroy)
        close_btn.pack(pady=15)
        
        # Center dialog
        select_dialog.transient(self.root)
        select_dialog.grab_set()
    
    def create_setting_card(self, parent, setting_name, recommended_value, description=""):
        """Create a vibrant setting card with rounded corners"""
        # Main card with rounded corners effect
        card = self._create_rounded_frame(parent, bg=self.bg_secondary, width=280)
        card.pack(fill=tk.X, pady=7, padx=10, ipady=8)
        
        # Setting icon based on setting type
        icon_text = "⚙️"  # Default icon
        
        # Choose appropriate icon based on setting name
        if any(keyword in setting_name.lower() for keyword in ["resolution", "screen", "display"]):
            icon_text = "🖥️"
        elif any(keyword in setting_name.lower() for keyword in ["texture", "quality", "detail"]):
            icon_text = "🎨"
        elif any(keyword in setting_name.lower() for keyword in ["shadow", "light"]):
            icon_text = "💡"
        elif any(keyword in setting_name.lower() for keyword in ["fps", "frame", "rate"]):
            icon_text = "⚡"
        elif any(keyword in setting_name.lower() for keyword in ["vsync", "sync"]):
            icon_text = "🔄"
        elif any(keyword in setting_name.lower() for keyword in ["ray", "tracing", "rt"]):
            icon_text = "✨"
        elif any(keyword in setting_name.lower() for keyword in ["dlss", "fsr", "upscal"]):
            icon_text = "🚀"
        elif any(keyword in setting_name.lower() for keyword in ["anti", "aliasing", "aa"]):
            icon_text = "📐"
        
        # Inner padding frame
        inner_card = tk.Frame(card, bg=self.bg_secondary, padx=12, pady=8)
        inner_card.pack(fill=tk.X)
        
        # Top section with icon and name
        top_frame = tk.Frame(inner_card, bg=self.bg_secondary)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Icon on the left
        icon_label = tk.Label(top_frame, text=icon_text, font=('Segoe UI', 16), 
                           fg=self.accent_blue, bg=self.bg_secondary)
        icon_label.pack(side=tk.LEFT, anchor='w', padx=(0, 8))
        
        # Setting name with vibrant color
        name_label = tk.Label(top_frame, text=setting_name, bg=self.bg_secondary, fg=self.text_primary, 
                           font=('Segoe UI', 11, 'bold'), anchor='w')
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Value with accent color based on setting type and value
        value_color = self.accent_green
        
        # Choose color based on value content for visual hints
        if any(term in str(recommended_value).lower() for term in ["high", "ultra", "maximum", "best", "quality", "on"]):
            value_color = self.accent_green
        elif any(term in str(recommended_value).lower() for term in ["medium", "balanced", "normal", "auto"]):
            value_color = self.accent_yellow
        elif any(term in str(recommended_value).lower() for term in ["low", "minimum", "off", "disabled"]):
            value_color = self.accent_orange
        elif "Resolution" in setting_name:
            value_color = self.accent_blue
        elif "Ray" in setting_name:
            value_color = self.accent_purple
        
        # Value badge with glowing effect
        value_frame = tk.Frame(inner_card, bg=self.bg_secondary)
        value_frame.pack(fill=tk.X, pady=(0, 10))
        
        value_badge = tk.Frame(value_frame, bg=value_color, padx=10, pady=5, bd=0)
        value_badge.pack(side=tk.LEFT)
        
        value_label = tk.Label(value_badge, text=recommended_value, bg=value_color, fg=self.bg_primary, 
                             font=('Segoe UI', 12, 'bold'))
        value_label.pack()
        
        # Description with subtle styling in a framed area
        if description:
            desc_frame = tk.Frame(inner_card, bg=self.bg_tertiary, bd=0, padx=8, pady=8)
            desc_frame.pack(fill=tk.X)
            
            desc_label = tk.Label(desc_frame, text=description, bg=self.bg_tertiary, fg=self.text_secondary, 
                               font=('Segoe UI', 9), wraplength=250, justify=tk.LEFT, anchor='w')
            desc_label.pack(fill=tk.X)
        
        # Bottom action section
        action_frame = tk.Frame(inner_card, bg=self.bg_secondary)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add copy button with improved styling
        copy_btn = tk.Button(action_frame, text="📋 Copy", bg=self.accent_blue, fg=self.text_primary,
                          font=('Segoe UI', 9, 'bold'), relief='flat', padx=10, pady=5,
                          activebackground=self.accent_purple, activeforeground=self.text_primary,
                          command=lambda: self.copy_to_clipboard(f"{setting_name}: {recommended_value}"))
        copy_btn.pack(side=tk.RIGHT)
        
        # Add hover effects
        def on_enter(e):
            card.configure(bg=self.bg_tertiary)
            inner_card.configure(bg=self.bg_tertiary)
            top_frame.configure(bg=self.bg_tertiary)
            icon_label.configure(bg=self.bg_tertiary)
            name_label.configure(bg=self.bg_tertiary)
            value_frame.configure(bg=self.bg_tertiary)
            action_frame.configure(bg=self.bg_tertiary)
            
        def on_leave(e):
            card.configure(bg=self.bg_secondary)
            inner_card.configure(bg=self.bg_secondary)
            top_frame.configure(bg=self.bg_secondary)
            icon_label.configure(bg=self.bg_secondary)
            name_label.configure(bg=self.bg_secondary)
            value_frame.configure(bg=self.bg_secondary)
            action_frame.configure(bg=self.bg_secondary)
            
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        return card
    
    def update_settings_panel(self, settings=None, game_name=""):
        """Update the settings panel with vibrant new recommendations"""
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
            
            # Add vibrant instruction with icon
            instruction_frame = tk.Frame(self.settings_frame, bg=self.bg_tertiary, padx=15, pady=15)
            instruction_frame.pack(fill=tk.X, pady=10)
            
            # Target icon
            target_icon = tk.Label(instruction_frame, text="🎯", font=('Segoe UI', 36), 
                                bg=self.bg_tertiary, fg=self.accent_orange)
            target_icon.pack(pady=(10, 15))
            
            # Instruction text
            instruction = tk.Label(instruction_frame, 
                                text="Analyze a game to get personalized settings recommendations",
                                bg=self.bg_tertiary, fg=self.text_primary, font=('Segoe UI', 11, 'bold'),
                                wraplength=280, justify='center')
            instruction.pack(pady=(0, 10))
            
            # Sub instruction
            sub_instruction = tk.Label(instruction_frame, 
                                    text="Settings will match the actual in-game options for each specific game!",
                                    bg=self.bg_tertiary, fg=self.text_secondary, font=('Segoe UI', 10),
                                    wraplength=280, justify='center')
            sub_instruction.pack(pady=(0, 10))
            
        else:
            # Add game-specific header with vibrant styling
            if game_name:
                game_header_frame = tk.Frame(self.settings_frame, bg=self.bg_tertiary, padx=15, pady=15)
                game_header_frame.pack(fill=tk.X, pady=(0, 15))
                
                game_icon = tk.Label(game_header_frame, text="🎮", font=('Segoe UI', 18), 
                                  bg=self.bg_tertiary, fg=self.accent_orange)
                game_icon.pack(side=tk.LEFT, padx=(0, 8))
                
                game_header = tk.Label(game_header_frame, text=f"{game_name} Settings", 
                                    bg=self.bg_tertiary, fg=self.accent_orange, font=('Segoe UI', 14, 'bold'))
                game_header.pack(side=tk.LEFT)
        
        # Create setting cards with descriptions
        descriptions = self.get_setting_descriptions(game_name, settings)
        
        # Group settings by category for better organization
        categories = {
            "Display": ["Resolution", "Refresh Rate", "Window Mode"],
            "Graphics": ["Texture", "Shadow", "Lighting", "Effects", "Detail", "Quality"],
            "Performance": ["DLSS", "FSR", "Ray Tracing", "Frame Rate", "VSync"],
            "Other": []
        }
        
        categorized_settings = {"Display": {}, "Graphics": {}, "Performance": {}, "Other": {}}
        
        # Categorize settings
        for setting, value in settings.items():
            categorized = False
            for category, keywords in categories.items():
                if any(keyword.lower() in setting.lower() for keyword in keywords):
                    categorized_settings[category][setting] = value
                    categorized = True
                    break
            
            if not categorized:
                categorized_settings["Other"][setting] = value
        
        # Create section for each category
        for category, category_settings in categorized_settings.items():
            if category_settings:
                # Create category header
                category_frame = tk.Frame(self.settings_frame, bg=self.bg_tertiary, padx=10, pady=5)
                category_frame.pack(fill=tk.X, pady=(15, 5))
                
                category_label = tk.Label(category_frame, text=category, 
                                       bg=self.bg_tertiary, fg=self.text_secondary, 
                                       font=('Segoe UI', 10, 'bold'))
                category_label.pack(anchor='w')
                
                # Add settings for this category
                for setting, value in category_settings.items():
                    desc = descriptions.get(setting, f"Game-specific setting for {game_name}")
                    self.create_setting_card(self.settings_frame, setting, value, desc)
        
        # Add quick actions with vibrant styling
        if settings != {} and len(settings) > 3:  # If we have real settings
            actions_frame = tk.Frame(self.settings_frame, bg=self.bg_tertiary, padx=15, pady=15)
            actions_frame.pack(fill=tk.X, pady=(20, 10))
            
            actions_header = tk.Label(actions_frame, text="⚡ Quick Actions", 
                                   bg=self.bg_tertiary, fg=self.accent_yellow,
                                   font=('Segoe UI', 12, 'bold'))
            actions_header.pack(anchor='w', pady=(0, 15))
            
            # Copy all button with vibrant design
            copy_all_btn = tk.Button(actions_frame, text="📋 Copy All Settings", 
                                   bg=self.accent_green, fg=self.bg_primary, 
                                   font=('Segoe UI', 11, 'bold'),
                                   relief='flat', padx=15, pady=10,
                                   command=lambda: self.copy_all_settings(settings, game_name),
                                   activebackground=self.accent_blue)
            copy_all_btn.pack(fill=tk.X, pady=(0, 8))
            
            # Export button with vibrant design
            export_btn = tk.Button(actions_frame, text="💾 Export to File", 
                                 bg=self.accent_blue, fg=self.text_primary, 
                                 font=('Segoe UI', 11, 'bold'),
                                 relief='flat', padx=15, pady=10,
                                 command=lambda: self.export_settings(settings, game_name),
                                 activebackground=self.accent_purple)
            export_btn.pack(fill=tk.X)
    
    def get_setting_descriptions(self, game_name, settings):
        """Get setting descriptions"""
        descriptions = {}
        
        # Default descriptions
        default_descriptions = {
            "Resolution": "Display resolution - higher values mean better visual clarity but lower FPS",
            "Texture Quality": "Texture detail level - affects VRAM usage and visual quality",
            "Shadow Quality": "Shadow detail and resolution - major impact on performance",
            "Anti-Aliasing": "Edge smoothing technique - higher values reduce jagged edges",
            "Effects Quality": "Visual effects like particles, explosions, and lighting",
            "Ray Tracing": "Advanced lighting technology - significant performance impact",
            "DLSS/FSR": "AI upscaling technology - improves performance with minimal visual loss",
            "VSync": "Vertical sync to prevent screen tearing - adds input lag",
            "Frame Rate Limit": "Caps maximum FPS - can improve stability",
            "Motion Blur": "Blur effect during movement - can hide low framerates",
            "Film Grain": "Artistic film grain effect - minimal performance impact"
        }
        
        # Fill in any missing descriptions with defaults
        for setting in settings.keys():
            if setting not in descriptions:
                descriptions[setting] = default_descriptions.get(setting, f"Setting specific to {game_name}")
        
        return descriptions
    
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

            EXACT SETTING VALUES REQUIRED:
            Use ONLY these exact values that exist in games:
            - Resolution: "3840x2160", "2560x1440", "1920x1080", "1600x900", "1280x720"
            - Quality: "Ultra", "High", "Medium", "Low", "Very Low", "Off"
            - Ray Tracing: "RT Ultra", "RT High", "RT Medium", "RT Low", "Off"
            - DLSS: "Ultra Performance", "Performance", "Balanced", "Quality", "Off"
            - Anti-Aliasing: "TAA", "MSAA 8x", "MSAA 4x", "MSAA 2x", "FXAA", "Off"

            Be HONEST about FPS vs Quality trade-offs:

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

            RECOMMENDED_SETTINGS_FOR_{target_fps}_FPS:
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

            PERFORMANCE_ANALYSIS:
            Expected FPS Range: [Based on DLSS setting and quality level]
            Settings Rationale: [Why quality was reduced for FPS target]
            Critical FPS Settings: [List settings that impact FPS most]
            Tuning Suggestions: [What to adjust first if FPS is too low]
            """
            
            response = self.ai_model.generate_content(settings_detection_prompt)
            ai_response = response.text
            
            # Parse the AI response to extract settings
            available_settings, recommended_settings, performance_analysis = self.parse_ai_response(ai_response)
            
            # Update UI
            self.root.after(0, self._update_analysis_results, ai_response, available_settings, recommended_settings, performance_analysis, game_name)
            
        except Exception as e:
            error_msg = f"❌ AI Analysis failed: {str(e)}"
            self.root.after(0, self._update_analysis_error, error_msg)
    
    def _get_gpu_performance_context(self, gpu_name, target_fps):
        """Generate performance context based on GPU"""
        gpu_lower = gpu_name.lower()
        
        # High-end GPUs (RTX 40xx, RTX 30xx, etc.)
        if any(x in gpu_lower for x in ['rtx 40', 'rtx 30', '6800', '6900', '7800', '7900']):
            if target_fps <= 60:
                return f"PERFORMANCE CONTEXT: {gpu_name} can achieve 60+ FPS at High-Ultra settings in most modern games."
            elif target_fps <= 120:
                return f"PERFORMANCE CONTEXT: {gpu_name} can achieve 100-120 FPS at Medium-High settings in most games."
            else:
                return f"PERFORMANCE CONTEXT: {gpu_name} may need Medium-Low settings to reach {target_fps}+ FPS in demanding games."
        
        # Mid-range GPUs
        elif any(x in gpu_lower for x in ['rtx 20', 'gtx 16', '6600', '5700']):
            if target_fps <= 60:
                return f"PERFORMANCE CONTEXT: {gpu_name} can achieve 60 FPS at Medium-High settings in most games."
            else:
                return f"PERFORMANCE CONTEXT: {gpu_name} will need Medium-Low settings to reach {target_fps}+ FPS in most games."
        
        # Budget GPUs
        else:
            if target_fps <= 60:
                return f"PERFORMANCE CONTEXT: {gpu_name} can achieve 60 FPS at Low-Medium settings in most games."
            else:
                return f"PERFORMANCE CONTEXT: {gpu_name} will need Low settings to reach {target_fps}+ FPS in most games."
    
    def parse_ai_response(self, response):
        """Parse AI response to extract settings"""
        available_settings = []
        recommended_settings = {}
        performance_analysis = ""
        
        # Extract available settings
        if "AVAILABLE_SETTINGS:" in response:
            available_section = response.split("AVAILABLE_SETTINGS:")[1].split("RECOMMENDED_SETTINGS")[0]
            available_settings = [s.strip() for s in available_section.strip().split('\n') if s.strip()]
        
        # Extract recommended settings
        if "RECOMMENDED_SETTINGS" in response:
            settings_section = response.split("RECOMMENDED_SETTINGS")[1].split("PERFORMANCE_ANALYSIS:")[0]
            settings_lines = settings_section.strip().split('\n')
            for line in settings_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    recommended_settings[key.strip()] = value.strip()
        
        # Extract performance analysis
        if "PERFORMANCE_ANALYSIS:" in response:
            performance_analysis = response.split("PERFORMANCE_ANALYSIS:")[1].strip()
        
        return available_settings, recommended_settings, performance_analysis
    
    def _update_analysis_results(self, response, available_settings, recommended_settings, performance_analysis, game_name):
        """Update UI with analysis results"""
        # Update text area
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        
        self.ai_text.insert(tk.END, f"✅ Analysis Complete: {game_name}\n\n")
        self.ai_text.insert(tk.END, f"Performance Analysis:\n{performance_analysis}\n\n")
        self.ai_text.insert(tk.END, f"Available Settings ({len(available_settings)}):\n")
        for setting in available_settings:
            self.ai_text.insert(tk.END, f"• {setting}\n")
        
        self.ai_text.config(state=tk.DISABLED)
        
        # Update settings panel
        self.update_settings_panel(recommended_settings, game_name)
        
        # Save to game history
        self.save_to_game_history(game_name, recommended_settings, performance_analysis)
    
    def _update_analysis_error(self, error_msg):
        """Update UI with error message"""
        self.ai_text.config(state=tk.NORMAL)
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, error_msg)
        self.ai_text.config(state=tk.DISABLED)
    
    def save_to_game_history(self, game_name, settings, analysis):
        """Save game analysis to history"""
        # Create history entry
        history_entry = {
            'timestamp': time.time(),
            'game': game_name,
            'settings': settings,
            'analysis': analysis,
            'hardware': {
                'gpu': self.system_specs['gpu'],
                'cpu': self.system_specs['cpu'],
                'ram_gb': self.system_specs['ram_gb']
            }
        }
        
        # Check if game already exists
        exists = False
        for i, entry in enumerate(self.game_history):
            if entry.get('game') == game_name:
                self.game_history[i] = history_entry
                exists = True
                break
        
        if not exists:
            self.game_history.append(history_entry)
        
        # Save updated history
        self.save_game_history()
    
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
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.show_notification("📋 Copied to clipboard!")
    
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