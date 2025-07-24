import requests
import json
import os
import time

class FreeDictionaryClient:
    """
    A client to interact with the Free Dictionary API.
    It includes caching to avoid redundant API calls and ensure reproducibility.
    """
    API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
    CACHE_FILE = "cache.json"

    def __init__(self):
        self.cache = self._load_cache()

    def _load_cache(self):
        """Loads the API response cache from a file."""
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_cache(self):
        """Saves the current cache to a file."""
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def get_definition(self, word):
        """
        Retrieves the definition of a word, using cache if available.
        """
        if word in self.cache:
            return self.cache[word]

        try:
            response = requests.get(f"{self.API_URL}{word}")
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            self.cache[word] = data
            self._save_cache()
            # To avoid hitting rate limits
            time.sleep(0.5)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching definition for '{word}': {e}")
            self.cache[word] = None  # Cache failures to avoid retrying
            self._save_cache()
            return None