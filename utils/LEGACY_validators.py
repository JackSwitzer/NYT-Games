class GameValidator:
    def __init__(self, config=None):
        self.config = config

    @staticmethod
    def ValidateWordLength(word: str, min_length: int, max_length: int) -> bool:
        return min_length <= len(word) <= max_length

    def ValidateWord(self, word: str, game_type: str, **params) -> bool:
        """Generic word validator that handles all game types."""
        if not word or not isinstance(word, str):
            return False
            
        word = word.lower()
        
        # First check length for all games
        if not self.ValidateWordLength(word, params.get('min_length'), params.get('max_length')):
            return False

        # Dispatch to specific game validator
        if game_type == 'SB':
            return self.ValidateSpellingBee(word, params['mandatory_char'], params['allowed_chars'])
        elif game_type == 'LB':
            return self.ValidateLetterBoxed(word, params['allowed_chars'], params['char_to_side'])
        return False

    @staticmethod
    def ValidateSpellingBee(word: str, mandatory_char: str, allowed_chars: set) -> bool:
        return (mandatory_char in word and 
                all(c in allowed_chars for c in word))

    @staticmethod
    def ValidateLetterBoxed(word: str, allowed_chars: set, char_to_side: dict) -> bool:
        return (all(c in allowed_chars for c in word) and
                all(char_to_side[word[i]] != char_to_side[word[i + 1]] 
                    for i in range(len(word) - 1)))