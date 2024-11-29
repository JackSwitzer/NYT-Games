from dataclasses import dataclass
from typing import Dict, Any, Callable, Type, List, get_type_hints, Optional, Union
from pathlib import Path
from datetime import date
import json
from utils.errors import GameConfigError

@dataclass
class GameConfig:
    min_length: int
    max_length: int
    data_dir: Path
    daily_dir: Path
    raw_dir: Path
    solutions_dir: Path
    actual_dir: Path
    validation_rules: Dict[str, Union[Type, Callable]]
    game_name: str

class ConfigManager:
    WORD_LIST_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
    GAMES = {
        'SB': ('Spelling Bee', 'SpellingBee'),
        'LB': ('Letter Boxed', 'LetterBoxed')
    }
    BASE_DATA_DIR = Path("Data")
    GAME_DATA_DIR = BASE_DATA_DIR / "GameData"
    DICTIONARY_DIR = BASE_DATA_DIR / "Dictionary"
    INVALID_WORDS_DIR = DICTIONARY_DIR / "invalid"

    def __init__(self):
        self._today = date.today()
        self._override_date = None
        self._configs = {}
        self.load_configs()
        self.INVALID_WORDS_DIR.mkdir(parents=True, exist_ok=True)

    def load_configs(self):
        """Load configurations from JSON files for each game type."""
        for game_code, (game_name, _) in self.GAMES.items():
            game_dir = self.GAME_DATA_DIR / game_code
            daily_dir = game_dir / "Daily"
            raw_dir = daily_dir / "raw"
            solutions_dir = daily_dir / "solutions"
            actual_dir = daily_dir / "actual"
            
            # Ensure directories exist
            for dir in [game_dir, daily_dir, raw_dir, solutions_dir, actual_dir, self.DICTIONARY_DIR]:
                dir.mkdir(parents=True, exist_ok=True)

            # Default configs
            self._configs[game_code] = GameConfig(
                min_length=3,
                max_length=15,
                data_dir=game_dir,
                daily_dir=daily_dir,
                raw_dir=raw_dir,
                solutions_dir=solutions_dir,
                actual_dir=actual_dir,
                validation_rules={'validator': validate_lb if game_code == 'LB' else None},
                game_name=game_name
            )

    @property
    def current_date_str(self) -> str:
        """Returns current date in YYYYMMDD format."""
        return (self._override_date or self._today).strftime("%Y%m%d")
    
    @property
    def current_date(self) -> str:
        """Returns current date in DDMMYYYY format."""
        return (self._override_date or self._today).strftime("%d%m%Y")
    
    @property
    def display_date(self) -> str:
        """Returns formatted date for display."""
        return (self._override_date or self._today).strftime("%B %d, %Y")
    
    @property
    def available_games(self) -> List[str]:
        """Returns list of available game types."""
        return list(self._configs.keys())

    def set_override_date(self, new_date: date | None) -> None:
        """Sets an override date for testing purposes."""
        self._override_date = new_date

    @property
    def CONFIGS(self) -> Dict[str, GameConfig]:
        """Access to game configurations."""
        return self._configs

def validate_lb(data: dict) -> bool:
    """Validates Letter Boxed data format."""
    required_sides = {'TOP', 'LEFT', 'BOTTOM', 'RIGHT'}
    if not all(side in data for side in required_sides):
        return False
    
    return all(
        isinstance(data[side], list) and
        len(data[side]) == 3 and
        all(isinstance(l, str) and l.isalpha() and l.isupper() 
            for l in data[side])
        for side in required_sides
    )

# Initialize the global instance
config = ConfigManager()


