from typing import Dict, Type, Set
import logging
from datetime import datetime
import json
import sys

from Data.Dictionary.WordManager import WordManager
from Games.SpellingBee import SpellingBee
from Games.LetterBoxed import LetterBoxed
from Games.Game import Game, GameConfigError, GameError, GameInitializationError, GameExecutionError, WordValidationError
from config import config
from utils.visualization import GameVisualizer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

visualizer = GameVisualizer()

class GameErrorContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
            
        if issubclass(exc_type, GameError):
            error_type = exc_type.__name__.replace('Error', '')
            logger.error(f"{error_type} error: {str(exc_val)}")
        else:
            logger.error(f"Unexpected error: {str(exc_val)}")
        return True

def RunGame(game_type: str, word_manager: WordManager, game_classes: Dict[str, Type[Game]]) -> None:
    """Run a specific game with error handling."""
    logger.debug(f"Loading daily data for {game_type}")
    daily_data = word_manager.LoadDailyData(game_type)
    
    if daily_data is None:
        logger.warning(f"No daily data found for {game_type}")
        return
            
    logger.info(f"\n=== {config.GAMES[game_type][0]} ===")
    
    with GameErrorContext():
        logger.debug(f"Initializing {game_type} game")
        game = game_classes[game_type](word_manager)
        game.InitializeGame(**daily_data)
        valid_words = game.FindValidWords()
        visualizer.output_game_results(game_type, valid_words, config, game)

def Main() -> None:
    """Main entry point for the NYT Word Games Solver."""
    logger.info(f"\n=== Running NYT Games for {config.display_date} ===")
    
    try:
        word_manager = WordManager(config)
        
        game_classes: Dict[str, Type[Game]] = {
            'SB': SpellingBee,
            'LB': LetterBoxed
        }
        
        # Add command-line argument handling for invalid words
        if len(sys.argv) > 1 and sys.argv[1] == '--add-invalid':
            game_type = input("Enter game type (SB/LB): ").upper()
            if game_type not in game_classes:
                logger.error(f"Invalid game type: {game_type}")
                return
                
            print("Enter invalid words (one per line, empty line to finish):")
            while True:
                word = input().strip()
                if not word:
                    break
                word_manager.add_invalid_word(game_type, word)
            return

        # Normal game execution
        for game_type in config.available_games:
            if game_type not in config.CONFIGS:
                logger.error(f"Unsupported game type: {game_type}")
                continue
            
            RunGame(game_type, word_manager, game_classes)
            
    except Exception as e:
        logger.error(f"Fatal error in Main: {str(e)}")
        raise

if __name__ == "__main__":
    Main()