from Games.Game import Game
from typing import Set

class LetterBoxed(Game):
    def InitializeGame(self, **data):
        # Convert the JSON data format into a list of sides
        sides = [data['TOP'], data['LEFT'], data['BOTTOM'], data['RIGHT']]
        # Flatten and convert to lowercase
        self.sides = [
            ''.join(side).lower() for side in sides
        ]
        self.allowed_chars = set(''.join(self.sides))
        self.char_to_side = {
            char: idx for idx, side in enumerate(self.sides)
            for char in side
        }

    def GetValidationParams(self):
        return {
            'allowed_chars': self.allowed_chars,
            'char_to_side': self.char_to_side
        }

    def GetGameRules(self):
        return (
            f"Letter Boxed Rules:\n"
            f"1. Words must contain at least {self.config.min_length} letters\n"
            f"2. Letters must be connected by lines\n"
            f"3. Consecutive letters cannot come from the same side\n"
            f"4. Letters can be reused\n"
            f"Sides: {' | '.join(''.join(side) for side in self.sides)}"
        )

    def validate_game_specific(self, word: str) -> bool:
        return (all(c in self.allowed_chars for c in word) and
                all(self.char_to_side[word[i]] != self.char_to_side[word[i + 1]] 
                    for i in range(len(word) - 1)))

    def FindValidWords(self) -> Set[str]:
        """Override to find valid words and calculate solution path."""
        valid_words = super().FindValidWords()
        self.solution_path = self.find_solution_path(valid_words)
        return valid_words

    def find_solution_path(self, words: Set[str]) -> list:
        """Find the shortest solution path that uses all letters."""
        if not words:
            return []

        # Create optimized word connections dictionary with letter coverage
        word_connections = {}
        word_letters = {}
        for word in words:
            word_letters[word] = set(word)
            word_connections[word] = {
                w for w in words 
                if w[0] == word[-1]
            }

        # Try increasing path lengths until solution found
        target_chars = set(self.allowed_chars)
        max_path_length = 6

        for path_length in range(1, max_path_length + 1):
            # Start with words that cover more unique letters
            start_words = sorted(
                words,
                key=lambda w: len(word_letters[w] & target_chars),
                reverse=True
            )

            for start_word in start_words:
                path = self._find_optimal_path(
                    start_word,
                    target_chars,
                    word_connections,
                    word_letters,
                    [],
                    path_length
                )
                if path:
                    return path

        return []

    def _find_optimal_path(
        self, 
        word: str,
        target_chars: set,
        connections: dict,
        word_letters: dict,
        current_path: list,
        target_length: int,
        memo: dict = None
    ) -> list:
        """Recursively find the optimal path with pruning and memoization."""
        if memo is None:
            memo = {}

        current_path = current_path + [word]
        remaining = target_chars - set.union(*[word_letters[w] for w in current_path])

        # Early termination if we can't cover remaining letters
        if len(current_path) == target_length:
            return current_path if not remaining else None

        # Check if we need more words than we have length for
        min_words_needed = len(remaining) // max(len(w) for w in connections[word])
        if len(current_path) + min_words_needed > target_length:
            return None

        # Create state key for memoization
        state = (word, frozenset(remaining), len(current_path))
        if state in memo:
            return memo[state]

        # Sort next words by coverage of remaining letters
        next_words = sorted(
            [w for w in connections[word] if w not in current_path],
            key=lambda w: len(word_letters[w] & remaining),
            reverse=True
        )

        for next_word in next_words:
            result = self._find_optimal_path(
                next_word,
                target_chars,
                connections,
                word_letters,
                current_path,
                target_length,
                memo
            )
            if result:
                return result

        return None