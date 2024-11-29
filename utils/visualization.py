from typing import Set, Dict, List, Optional
import logging
import json
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx

logger = logging.getLogger(__name__)

class GameVisualizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Suppress matplotlib debug messages
        logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

    def save_results(self, game_type: str, words: Set[str], solution_file: Path, 
                    solution_data: Dict, game_specific_data: Optional[Dict] = None) -> None:
        """Save results to JSON file with proper formatting."""
        if game_specific_data:
            solution_data.update(game_specific_data)
            
        with open(solution_file, 'w') as f:
            json.dump(solution_data, f, indent=2)

    def display_word_summary(self, words: Set[str]) -> None:
        """Display summary of found words."""
        if not words:
            logger.warning("No valid words found.")
            return

        logger.info(f"\nFound {len(words)} valid words")
        
        # Group words by length
        words_by_length = {}
        for word in sorted(words):
            words_by_length.setdefault(len(word), []).append(word)

        # Display summary
        for length, group in sorted(words_by_length.items(), reverse=True):
            logger.info(f"{length} letters: {len(group)} words")
            logger.debug(f"Words: {', '.join(sorted(group))}")

    def display_letter_boxed_path(self, solution_path: List[str], sides: List[str]) -> None:
        """Visualize Letter Boxed solution path using matplotlib."""
        if not solution_path:
            return

        # If solution_path is a list, convert it to the expected dictionary format
        if isinstance(solution_path, list):
            solution_paths = {len(solution_path): [solution_path]}
        else:
            solution_paths = solution_path

        # Display all solution paths grouped by word count
        logger.info("\nSolution paths:")
        for word_count, paths in sorted(solution_paths.items()):
            logger.info(f"\n{word_count}-word solutions:")
            for path in paths:
                logger.info(f"  {' -> '.join(path)}")
                logger.info(f"  Total letters used: {len(set(''.join(path)))}")

        # Visualize the shortest solution
        shortest_path = min(
            [path for paths in solution_paths.values() for path in paths], 
            key=len
        )
        self._create_path_visualization(shortest_path, sides)

    def _create_path_visualization(self, path: List[str], sides: List[str]) -> None:
        """Create the visual representation of a solution path."""
        # Create graph
        G = nx.DiGraph()
        
        # Calculate vertex positions (square corners)
        positions = {
            'top': (0.5, 1),
            'right': (1, 0.5),
            'bottom': (0.5, 0),
            'left': (0, 0.5)
        }

        # Add nodes for each letter
        side_positions = {}
        for side_name, (x, y) in positions.items():
            side_idx = list(positions.keys()).index(side_name)
            side_letters = sides[side_idx]
            for i, letter in enumerate(side_letters):
                # Adjust position slightly for each letter on the side
                offset = (i - 1) * 0.1
                if side_name in ['top', 'bottom']:
                    pos = (x + offset, y)
                else:
                    pos = (x, y + offset)
                side_positions[letter] = pos
                G.add_node(letter, pos=pos)

        # Add edges for solution path
        edges = []
        for word in path:
            for i in range(len(word) - 1):
                edges.append((word[i], word[i + 1]))
        G.add_edges_from(edges)

        # Draw the graph
        plt.figure(figsize=(10, 10))
        nx.draw(G, side_positions, 
                with_labels=True,
                node_color='lightblue',
                node_size=500,
                arrowsize=20,
                edge_color='gray',
                font_size=12,
                font_weight='bold')
        
        # Save the visualization
        plt.savefig('letter_boxed_solution.png')
        plt.close()
        logger.info("Solution visualization saved as 'letter_boxed_solution.png'")

    def format_solution_data(self, words: Set[str], date_str: str) -> Dict:
        """Format solution data for storage."""
        words_by_length = {}
        for word in sorted(words):
            words_by_length.setdefault(len(word), []).append(word)

        return {
            'date': date_str,
            'total_words': len(words),
            'words_by_length': {
                str(length): words 
                for length, words in sorted(words_by_length.items())
            }
        }

    def output_game_results(self, game_type: str, words: Set[str], config, game) -> None:
        """Handle all visualization and saving of game results."""
        if not words:
            logger.warning("No valid words found.")
            return

        # Save actual words for future reference
        game.word_manager.save_actual_words(game_type, words, config.current_date_str)

        # Format basic solution data
        solution_data = self.format_solution_data(words, config.current_date_str)
        
        # Add game-specific data and visualization
        game_specific_data = None
        if game_type == 'LB' and hasattr(game, 'solution_path') and game.solution_path:
            game_specific_data = {'solution_path': game.solution_path}
            self.display_letter_boxed_solution(game.solution_path, game.sides)

        # Save results
        solution_file = config.CONFIGS[game_type].solutions_dir / f"{config.current_date_str}.json"
        self.save_results(game_type, words, solution_file, solution_data, game_specific_data)

        # Display word summary
        self.display_word_summary(words)

    def display_letter_boxed_solution(self, solution_path: List[str], sides: List[str]) -> None:
        """Display Letter Boxed solution details and visualization."""
        logger.info("\nSolution path:")
        logger.info(" -> ".join(solution_path))
        logger.info(f"Total letters used: {len(set(''.join(solution_path)))}")
        logger.info(f"Number of words: {len(solution_path)}")
        
        # Generate visual representation of the solution
        self.display_letter_boxed_path(solution_path, sides)
