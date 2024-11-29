from abc import ABC, abstractmethod
from utils.errors import *
from config import config

class Game(ABC):
    def __init__(self, word_manager, **game_params):
        self.word_manager = word_manager
        self.game_type = self._get_game_type()
        self.config = config.CONFIGS[self.game_type]
        
        # Load daily config if no params provided
        daily_config = None if game_params else self.LoadDailyConfig()
        self.InitializeGame(**(game_params or daily_config or {}))

    def _get_game_type(self) -> str:
        """Get game type code from class name."""
        for code, (_, class_name) in config.GAMES.items():
            if class_name == self.__class__.__name__:
                return code
        raise GameConfigError(f"Unknown game type: {self.__class__.__name__}")

    @abstractmethod
    def validate_game_specific(self, word: str) -> bool:
        """Game-specific validation rules."""
        pass

    def ValidateWord(self, word: str) -> bool:
        """Validate if a word is valid for the game."""
        # First check if word is in invalid words list
        if self.word_manager.is_invalid_word(self.game_type, word):
            return False
            
        # Then do the regular validation
        if len(word) < self.config.min_length:
            return False
            
        return self.validate_game_specific(word)

    @abstractmethod
    def InitializeGame(self, **params): pass

    def FindValidWords(self):
        """Cache and return valid words."""
        if not hasattr(self, '_word_cache'):
            word_list = self.word_manager.GetWordList(self.game_type)
            self._word_cache = {
                word for word in word_list
                if self.ValidateWord(word)
            }
        return self._word_cache

    @abstractmethod
    def GetGameRules(self): pass

    def SaveDailyConfig(self, config):
        if not isinstance(config, dict):
            raise GameConfigError("Configuration must be a dictionary")
        self.word_manager.SaveDailyData(self.game_type, config)

    def LoadDailyConfig(self):
        """Load and validate daily configuration."""
        config = self.word_manager.LoadDailyData(self.game_type)
        if not config:
            raise GameConfigError(f"No daily configuration found for {self.game_type}")
        return config