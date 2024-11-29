# NYT Games Solver

A Python tool that solves New York Times word games: Spelling Bee and Letter Boxed.

## Features

- Solves NYT Spelling Bee puzzles
- Solves NYT Letter Boxed puzzles
- Displays results grouped by word length
- Uses an extensive English word dictionary

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd nyt-games-solver
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Spelling Bee

1. Create a JSON configuration file in `Data/GameData/SB/Daily/` with format:
```json
{
    "mandatory_char": "o",
    "optional_chars": "tirmfy"
}
```

2. Run the solver:
```bash
python main.py SB
```

### Letter Boxed

1. Create a JSON configuration file in `Data/GameData/LB/Daily/` with format:
```json
{
    "sides": ["abc", "def", "ghi", "jkl"]
}
```

2. Run the solver:
```bash
python main.py LB
```

## Game Rules

### Spelling Bee
- Words must contain the central (mandatory) letter
- Words must be 4+ letters long
- Can only use provided letters
- Letters can be reused

### Letter Boxed
- Letters must be connected by lines
- Consecutive letters cannot come from the same side
- Letters can be reused
- Words must be 3+ letters long

## Next Steps
better data - more like the NYT corpus
better visualizatio
more games