# Modern Gaming Advisor Pro

A comprehensive gaming application that helps gamers optimize their gaming experience with:
- Game performance analysis based on system specifications
- Personalized graphics settings recommendations
- Game library with details, screenshots, and trailers

## Features

### Game Analysis
- Detects your system specifications
- Provides optimized graphics settings for games
- Analyzes performance impact of different settings
- Saves history of analyzed games

### System Information
- Real-time monitoring of CPU and GPU usage
- Complete system specifications
- Performance metrics and benchmark comparisons

### Game Library
- Browse popular games with ratings and release dates
- View detailed game information, screenshots, and trailers
- Search and filter games by genre and platform
- Direct links to official websites and other resources

## Installation

1. Ensure you have Python 3.8+ installed
2. Clone this repository
3. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### Running the Enhanced Gaming Advisor with Game Library

```
python enhanced_gaming_advisor.py
```

### Running the Game Library Standalone

```
python game_library_launcher.py
```

## Dependencies

- tkinter: GUI framework
- Pillow: Image handling
- requests: API communication
- psutil, py-cpuinfo, GPUtil: System monitoring
- google-generativeai (optional): AI-powered recommendations

## Configuration

- The application uses the RAWG API for game data
- API key is pre-configured but can be changed in the code
- Benchmark data is cached locally in benchmark_cache.json
- Game analyses are stored in game_history.json

## Credits

- Game data provided by [RAWG API](https://rawg.io/apidocs)
- System monitoring tools by psutil, py-cpuinfo, and GPUtil
- AI recommendations powered by Gemini API (if enabled)

## License

This project is open source and available for personal and educational use.