from typing import Set
from Games.Game import Game
from config import config

class SpellingBee(Game):
    """
    SpellingBee game implementation.
    
    A word puzzle where players must create words using a set of letters,
    always including one mandatory central letter.
    
    Attributes:
        mandatory_char (str): The central letter that must be used in every word
        allowed_chars (set[str]): Set of all allowed letters including mandatory_char
    """

    def InitializeGame(self, mandatory_char, optional_chars):
        self.mandatory_char = mandatory_char.lower()
        self.allowed_chars = set(optional_chars.lower() + self.mandatory_char)

    def GetValidationParams(self):
        return {
            'mandatory_char': self.mandatory_char,
            'allowed_chars': self.allowed_chars
        }

    def GetGameRules(self):
        return (f"Spelling Bee: {self.config.min_length}+ letters, must include {self.mandatory_char}, "
                f"using only: {', '.join(sorted(self.allowed_chars))}")

    def validate_game_specific(self, word: str) -> bool:
        return (self.mandatory_char in word and 
                all(c in self.allowed_chars for c in word))