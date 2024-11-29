from pathlib import Path
import requests
from typing import Set, Dict, Optional, Type, Callable
import json
from config import config
from Games.Game import GameConfigError, GameExecutionError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WordManager:
    """Manages word lists and daily game data persistence."""
    
    def __init__(self, config):
        """Initialize WordManager with empty word cache and ensure data directories exist."""
        self.config = config
        self._word_cache: Dict[str, Set[str]] = {}  # Separate cache for each game
        self._invalid_words: Dict[str, Set[str]] = {}  # Invalid words by game type
        self._actual_words: Dict[str, Set[str]] = {}  # Actual valid words by game type
        
        # Initialize directories
        for game_config in config.CONFIGS.values():
            game_config.data_dir.mkdir(parents=True, exist_ok=True)
            game_config.daily_dir.mkdir(parents=True, exist_ok=True)
            
        # Initialize invalid words files
        self._init_invalid_words()

    def _init_invalid_words(self):
        """Initialize invalid words lists for each game."""
        invalid_words_dir = self.config.DICTIONARY_DIR / "invalid"
        invalid_words_dir.mkdir(exist_ok=True)
        
        for game_type in self.config.CONFIGS:
            invalid_file = invalid_words_dir / f"{game_type}_invalid.txt"
            if invalid_file.exists():
                with open(invalid_file, 'r') as f:
                    self._invalid_words[game_type] = set(word.strip().lower() for word in f)
            else:
                self._invalid_words[game_type] = set()
                invalid_file.touch()

    def GetWordList(self, game_type: str) -> Set[str]:
        """Get game-specific filtered word list."""
        if game_type not in self._word_cache:
            base_words = self._get_base_words()
            actual_words = self._get_actual_words(game_type)
            invalid_words = self._invalid_words.get(game_type, set())
            
            # Combine sources with priority: actual > base - invalid
            self._word_cache[game_type] = actual_words | (base_words - invalid_words)
            
        return self._word_cache[game_type]

    def _get_base_words(self) -> Set[str]:
        """Get base dictionary words."""
        try:
            response = requests.get(config.WORD_LIST_URL)
            response.raise_for_status()
            return set(word.strip().lower() for word in response.text.split() if word.strip().isalpha())
        except requests.RequestException as e:
            raise GameExecutionError(f"Failed to download word list: {str(e)}")

    def _get_actual_words(self, game_type: str) -> Set[str]:
        """Load actual valid words from previous games."""
        if game_type not in self._actual_words:
            self._actual_words[game_type] = set()
            actual_dir = self.config.CONFIGS[game_type].actual_dir
            
            for file in actual_dir.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        if 'valid_words' in data:
                            self._actual_words[game_type].update(data['valid_words'])
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Error loading actual words from {file}: {e}")
                    
        return self._actual_words[game_type]

    def add_invalid_word(self, game_type: str, word: str) -> None:
        """Add a word to the invalid words list."""
        word = word.strip().lower()
        if not word:
            return
            
        self._invalid_words[game_type].add(word)
        invalid_file = self.config.DICTIONARY_DIR / "invalid" / f"{game_type}_invalid.txt"
        
        with open(invalid_file, 'a') as f:
            f.write(f"{word}\n")
        
        # Clear cache to force reload
        if game_type in self._word_cache:
            del self._word_cache[game_type]

    def save_actual_words(self, game_type: str, words: Set[str], date_str: str) -> None:
        """Save actual valid words from a game."""
        actual_file = self.config.CONFIGS[game_type].actual_dir / f"{game_type}_{date_str}.json"
        
        data = {
            'date': date_str,
            'valid_words': sorted(list(words))
        }
        
        with open(actual_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Update cache
        self._actual_words.setdefault(game_type, set()).update(words)
        if game_type in self._word_cache:
            del self._word_cache[game_type]

    def _get_game_path(self, game_type: str) -> Path:
        """Get the path for a game's daily data file."""
        if game_type not in config.CONFIGS:
            raise GameConfigError(f"Invalid game type: {game_type}")
        return config.CONFIGS[game_type].daily_dir / f"{game_type}_{config.current_date}.json"

    def _validate_data(self, data: dict, game_type: str) -> bool:
        """Validate game data against configuration rules."""
        validator = config.CONFIGS[game_type].validation_rules.get('validator')
        if validator:
            return validator(data)
        return True  # No validation rules means accept all data

    def SaveDailyData(self, game_type: str, data: Dict) -> None:
        """Save daily game data to raw directory."""
        data_file = config.CONFIGS[game_type].raw_dir / f"{game_type}_{config.current_date_str}.json"
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def LoadDailyData(self, game_type: str) -> Optional[Dict]:
        """Load daily game data from file."""
        config = self.config.CONFIGS[game_type]
        # Parse the YYYYMMDD string into a date object, then format as DDMMYYYY
        current_date = datetime.strptime(self.config.current_date_str, "%Y%m%d")
        date_str = current_date.strftime("%d%m%Y")
        daily_file = config.raw_dir / f"{game_type}_{date_str}.json"
        logging.debug(f"Looking for daily data at: {daily_file}")
        
        try:
            with open(daily_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"Daily data file not found: {daily_file}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding daily data file: {e}")
            return None

    def is_invalid_word(self, game_type: str, word: str) -> bool:
        """Check if a word is in the invalid words list."""
        return word.lower() in self._invalid_words.get(game_type, set())