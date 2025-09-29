"""
Game API module for fetching game data from RAWG API.
"""
import requests
import os
import json
from datetime import datetime

class GameAPI:
    """Class to handle RAWG API requests and data processing."""
    
    def __init__(self, api_key='caeed1115dad4b85a0836f3667c467a5'):
        """Initialize the GameAPI with the provided API key.
        
        Args:
            api_key (str): RAWG API key
        """
        self.api_key = api_key
        self.base_url = "https://api.rawg.io/api"
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, endpoint, params):
        """Get the cache file path for the given request.
        
        Args:
            endpoint (str): API endpoint
            params (dict): Request parameters
            
        Returns:
            str: Cache file path
        """
        # Create a unique filename based on endpoint and params
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items()) if k != 'key'])
        filename = f"{endpoint.replace('/', '_')}_{params_str}.json"
        return os.path.join(self.cache_dir, filename)
    
    def _is_cache_valid(self, cache_path, max_age_hours=24):
        """Check if the cache file is valid.
        
        Args:
            cache_path (str): Path to cache file
            max_age_hours (int): Maximum age of cache in hours
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if not os.path.exists(cache_path):
            return False
        
        # Check if cache is older than max_age_hours
        file_time = os.path.getmtime(cache_path)
        file_dt = datetime.fromtimestamp(file_time)
        now_dt = datetime.now()
        
        # Calculate hours difference
        diff_hours = (now_dt - file_dt).total_seconds() / 3600
        
        return diff_hours < max_age_hours
    
    def _request_api(self, endpoint, params=None):
        """Make a request to the RAWG API.
        
        Args:
            endpoint (str): API endpoint
            params (dict): Request parameters
            
        Returns:
            dict: API response
        """
        if params is None:
            params = {}
        
        # Add API key to params
        params['key'] = self.api_key
        
        # Check for cache
        cache_path = self._get_cache_path(endpoint, params)
        
        # Use cache if valid
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If any error occurs, continue with API request
                pass
        
        # Make API request
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Cache the response
            try:
                with open(cache_path, 'w') as f:
                    json.dump(data, f)
            except IOError:
                pass  # Ignore cache write errors
            
            return data
        else:
            return {"error": f"API request failed with status code {response.status_code}"}
    
    def get_popular_games(self, page=1, page_size=20, ordering='-rating'):
        """Get popular games from the API.
        
        Args:
            page (int): Page number
            page_size (int): Number of games per page
            ordering (str): Ordering parameter
            
        Returns:
            dict: Popular games data
        """
        params = {
            'page': page,
            'page_size': page_size,
            'ordering': ordering
        }
        return self._request_api('games', params)
    
    def get_game_details(self, game_id):
        """Get detailed information about a specific game.
        
        Args:
            game_id (int): Game ID
            
        Returns:
            dict: Game details
        """
        return self._request_api(f'games/{game_id}')
    
    def get_game_screenshots(self, game_id):
        """Get screenshots for a specific game.
        
        Args:
            game_id (int): Game ID
            
        Returns:
            dict: Game screenshots
        """
        return self._request_api(f'games/{game_id}/screenshots')
    
    def get_game_trailers(self, game_id):
        """Get trailers for a specific game.
        
        Args:
            game_id (int): Game ID
            
        Returns:
            dict: Game trailers
        """
        return self._request_api(f'games/{game_id}/movies')
    
    def search_games(self, query, page=1, page_size=20):
        """Search for games by name.
        
        Args:
            query (str): Search query
            page (int): Page number
            page_size (int): Number of games per page
            
        Returns:
            dict: Search results
        """
        params = {
            'search': query,
            'page': page,
            'page_size': page_size
        }
        return self._request_api('games', params)
    
    def get_games_by_genre(self, genre_id, page=1, page_size=20):
        """Get games by genre.
        
        Args:
            genre_id (int): Genre ID
            page (int): Page number
            page_size (int): Number of games per page
            
        Returns:
            dict: Games in the specified genre
        """
        params = {
            'genres': genre_id,
            'page': page,
            'page_size': page_size
        }
        return self._request_api('games', params)
    
    def get_genres(self):
        """Get list of game genres.
        
        Returns:
            dict: Genres data
        """
        return self._request_api('genres')
    
    def get_platforms(self):
        """Get list of game platforms.
        
        Returns:
            dict: Platforms data
        """
        return self._request_api('platforms')