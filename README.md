# Othello (Reversi) Game 🎮

A professional-grade implementation of the classic Othello/Reversi board game with an intelligent AI opponent built using Python and Pygame.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![Pygame](https://img.shields.io/badge/pygame-2.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

## 📋 Table of Contents

- [About the Game](#about-the-game)
- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Game Rules](#game-rules)
- [AI Implementation](#ai-implementation)
- [Configuration](#configuration)
- [Controls](#controls)
- [Screenshots](#screenshots)
- [Technical Details](#technical-details)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## 🎯 About the Game

Othello (also known as Reversi) is a strategic two-player board game played on an 8×8 grid. The game is famous for its simple rules but complex strategy, often described as _"A minute to learn, a lifetime to master."_

This implementation features:

- Complete rule enforcement
- Intelligent AI opponent using advanced algorithms
- Clean, intuitive user interface
- Real-time score tracking
- Visual feedback for valid moves

## ✨ Features

### Core Gameplay

- ✅ Full Othello rule implementation
- ✅ Valid move detection and highlighting
- ✅ Automatic piece flipping
- ✅ Turn management with pass handling
- ✅ Game over detection and winner announcement
- ✅ Real-time score display

### AI Features

- 🤖 **Minimax Algorithm** with Alpha-Beta pruning
- 🧠 **Multiple difficulty levels** (adjustable search depth)
- 📊 **Advanced evaluation heuristics**:
  - Positional weights (corners, edges, center)
  - Mobility analysis
  - Piece differential
- ⚡ Optimized performance with pruning

### User Interface

- 🎨 Clean, professional design
- 🟢 Green dots indicate valid moves
- 📢 Status messages for game events
- 🔄 Quick restart functionality
- 📱 Responsive click handling

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the repository**

```bash
git clone https://github.com/yourusername/othello-game.git
cd othello-game
```

2. **Install Pygame**

```bash
pip install pygame
```

Or if using pip3:

```bash
pip3 install pygame
```

3. **Run the game**

```bash
python othello_game.py
```

## 🎮 How to Play

### Starting the Game

1. Run the Python script
2. A game window will open with the board initialized
3. Black (human player) moves first

### Making Moves

1. **Look for green dots** - these indicate valid moves
2. **Click on a green dot** to place your piece
3. All opponent pieces between your new piece and existing pieces will flip to your color
4. The AI (White) will automatically make its move
5. Continue until no valid moves remain for both players

### Winning

- The player with the most pieces when the game ends wins
- The game ends when neither player has valid moves (usually a full board)

## 📖 Game Rules

1. **Initial Setup**: Four pieces in the center (2 black, 2 white diagonally)
2. **Valid Moves**: Must sandwich opponent pieces between your new piece and an existing piece
3. **Flipping**: All sandwiched pieces flip to your color
4. **Passing**: If no valid moves exist, your turn is skipped
5. **Game End**: When neither player can move
6. **Winner**: Most pieces on the board

### Strategy Tips

- 🏆 **Corners are crucial** - they can never be flipped
- 🛡️ **Control edges** - they lead to corners
- ⚠️ **Avoid early corners for opponent** - major strategic mistake
- 🎯 **Maximize mobility** - having more options is advantageous
- 🔄 **Game can reverse quickly** - don't get overconfident!

## 🤖 AI Implementation

### Algorithm: Minimax with Alpha-Beta Pruning

The AI uses a sophisticated game tree search algorithm:

```
Minimax + Alpha-Beta Pruning
├── Search Depth: 1-6 moves ahead (configurable)
├── Evaluation Function:
│   ├── Positional Weights (corners: +100, edges: varies)
│   ├── Mobility Score (number of valid moves)
│   └── Piece Differential (raw count)
└── Optimization: Alpha-Beta pruning (~50% node reduction)
```

### Difficulty Levels

| Depth | Strength  | Speed        | Recommended For     |
| ----- | --------- | ------------ | ------------------- |
| 2     | Easy      | Very Fast    | Beginners           |
| 3     | Medium    | Fast         | Learning            |
| 4     | **Hard**  | **Balanced** | **Most Players** ⭐ |
| 5     | Very Hard | Slower       | Advanced            |
| 6+    | Expert    | Slow         | Challenge Mode      |

## ⚙️ Configuration

### Game Modes

Edit the bottom of `othello_game.py`:

```python
# Player vs AI (default, difficulty 4)
game = OthelloGame(ai_enabled=True, ai_difficulty=4)

# Two-player mode (no AI)
game = OthelloGame(ai_enabled=False)

# Easy AI (depth 2)
game = OthelloGame(ai_enabled=True, ai_difficulty=2)

# Expert AI (depth 6)
game = OthelloGame(ai_enabled=True, ai_difficulty=6)
```

### Customizable Constants

At the top of the file, you can adjust:

```python
BOARD_SIZE = 8          # Board dimensions
CELL_SIZE = 60          # Cell size in pixels
# Colors, window size, etc.
```

## 🎹 Controls

| Key/Action       | Function                    |
| ---------------- | --------------------------- |
| **Left Click**   | Place piece on valid square |
| **R Key**        | Restart game                |
| **Close Window** | Exit game                   |

## 🖼️ Screenshots

```
     A   B   C   D   E   F   G   H
   +---+---+---+---+---+---+---+---+
 1 |   |   |   |   |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 2 |   |   |   |   |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 3 |   |   |   |   |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 4 |   |   | W | B |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 5 |   |   | B | W |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 6 |   |   |   |   |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 7 |   |   |   |   |   |   |   |   |
   +---+---+---+---+---+---+---+---+
 8 |   |   |   |   |   |   |   |   |
   +---+---+---+---+---+---+---+---+
```

## 🔧 Technical Details

### Project Structure

```
othello-game/
├── othello_game.py      # Main game file
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

### Architecture

```
OthelloGame (Main)
├── OthelloLogic (Game Rules)
│   ├── Board state management
│   ├── Valid move detection
│   ├── Piece flipping logic
│   └── Game over detection
│
└── OthelloAI (Artificial Intelligence)
    ├── Minimax algorithm
    ├── Alpha-beta pruning
    └── Board evaluation
```

### Code Quality

- ✅ Type hints for better IDE support
- ✅ Comprehensive docstrings
- ✅ Modular, reusable components
- ✅ Clear separation of concerns
- ✅ Efficient algorithms with optimization
- ✅ Clean, readable code style

### Dependencies

```
pygame>=2.0.0
```

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] **Opening Book**: Pre-computed optimal opening moves
- [ ] **Endgame Solver**: Perfect play in final 10-12 moves
- [ ] **Move History**: Undo/redo functionality
- [ ] **Save/Load Games**: Persistent game state
- [ ] **Statistics Tracking**: Win/loss records
- [ ] **Multiplayer**: Network play support
- [ ] **Tournament Mode**: Multiple AI difficulties
- [ ] **Hints System**: Suggest best moves
- [ ] **Animation**: Smooth piece flipping
- [ ] **Sound Effects**: Audio feedback
- [ ] **Themes**: Customizable color schemes
- [ ] **Move Timer**: Time controls per move

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Guidelines

- Follow PEP 8 style guide
- Add type hints where appropriate
- Include docstrings for new functions
- Test thoroughly before submitting

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Contact & Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Email**: your.email@example.com
- **Documentation**: Check code comments for detailed explanations

## 🙏 Acknowledgments

- Classic Othello game design by Goro Hasegawa (1971)
- Pygame community for excellent documentation
- Minimax algorithm and game theory research

---

**Made with ❤️ and Python**

_Happy Gaming! May your corners be secure and your moves be strategic!_ 🎯
