import pygame
import copy
import sys
from typing import List, Tuple, Optional

# Constants
BOARD_SIZE = 8
CELL_SIZE = 60
BOARD_OFFSET = (50, 100)
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET[0] * 2
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET[1] + 50

# Colors
COLOR_BG = (34, 139, 34)
COLOR_GRID = (0, 100, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_VALID = (50, 200, 50)
COLOR_TEXT = (255, 255, 255)

# Players
BLACK = "B"
WHITE = "W"
EMPTY = None

# All 8 directions: up, down, left, right, and 4 diagonals
DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),  # vertical and horizontal
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),  # diagonals
]


class OthelloLogic:
    """Core game logic for Othello/Reversi"""

    def __init__(self):
        self.board: List[List[Optional[str]]] = [
            [EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        self.current_player = BLACK
        self.consecutive_passes = 0  # Track consecutive passes
        self.initialize_board()

    def initialize_board(self):
        """Set up initial four pieces in center"""
        mid = BOARD_SIZE // 2
        self.board[mid - 1][mid - 1] = WHITE
        self.board[mid - 1][mid] = BLACK
        self.board[mid][mid - 1] = BLACK
        self.board[mid][mid] = WHITE

    def get_opponent(self, player: str) -> str:
        """Return the opponent of the given player"""
        return WHITE if player == BLACK else BLACK

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def find_flips_in_direction(
        self, row: int, col: int, dr: int, dc: int, player: str
    ) -> List[Tuple[int, int]]:
        """Find pieces to flip in a specific direction"""
        opponent = self.get_opponent(player)
        flips = []
        r, c = row + dr, col + dc

        # Collect opponent pieces in this direction
        while self.is_valid_position(r, c) and self.board[r][c] == opponent:
            flips.append((r, c))
            r += dr
            c += dc

        # Valid if we ended on our own piece (and found opponents in between)
        if flips and self.is_valid_position(r, c) and self.board[r][c] == player:
            return flips
        return []

    def get_valid_moves(self, player: str) -> List[Tuple[int, int]]:
        """Get all valid moves for the given player"""
        valid_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    valid_moves.append((row, col))
        return valid_moves

    def is_valid_move(self, row: int, col: int, player: str) -> bool:
        """Check if a move is valid for the given player"""
        if not self.is_valid_position(row, col) or self.board[row][col] is not EMPTY:
            return False

        # Check all directions for valid flips
        for dr, dc in DIRECTIONS:
            if self.find_flips_in_direction(row, col, dr, dc, player):
                return True
        return False

    def make_move(self, row: int, col: int, player: str) -> bool:
        """Make a move and flip pieces. Returns True if successful."""
        if not self.is_valid_move(row, col, player):
            return False

        # Place the piece
        self.board[row][col] = player

        # Flip pieces in all directions
        all_flips = []
        for dr, dc in DIRECTIONS:
            flips = self.find_flips_in_direction(row, col, dr, dc, player)
            all_flips.extend(flips)

        for r, c in all_flips:
            self.board[r][c] = player

        return True

    def switch_player(self):
        """Switch to the other player"""
        self.current_player = self.get_opponent(self.current_player)

    def get_score(self) -> Tuple[int, int]:
        """Return (black_count, white_count)"""
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)
        return black_count, white_count

    def is_game_over(self) -> bool:
        """Check if game is over (no valid moves for both players)"""
        # Game is over if both players have no valid moves
        black_has_moves = bool(self.get_valid_moves(BLACK))
        white_has_moves = bool(self.get_valid_moves(WHITE))
        return not black_has_moves and not white_has_moves

    def get_winner(self) -> Optional[str]:
        """Return winner or None for tie"""
        black_score, white_score = self.get_score()
        if black_score > white_score:
            return BLACK
        elif white_score > black_score:
            return WHITE
        return None


class OthelloAI:
    """AI player using Minimax with Alpha-Beta pruning"""

    # Positional weights (corners and edges are valuable)
    POSITION_WEIGHTS = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, 5, 1, 1, 5, -2, 10],
        [5, -2, 1, 0, 0, 1, -2, 5],
        [5, -2, 1, 0, 0, 1, -2, 5],
        [10, -2, 5, 1, 1, 5, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10, 5, 5, 10, -20, 100],
    ]

    def __init__(self, player: str, depth: int = 4):
        self.player = player
        self.opponent = WHITE if player == BLACK else BLACK
        self.depth = depth

    def evaluate_board(self, logic: OthelloLogic) -> float:
        """Evaluate board position from AI's perspective"""
        # Piece count differential
        black_score, white_score = logic.get_score()
        if self.player == BLACK:
            piece_diff = black_score - white_score
        else:
            piece_diff = white_score - black_score

        # Positional score
        position_score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if logic.board[r][c] == self.player:
                    position_score += self.POSITION_WEIGHTS[r][c]
                elif logic.board[r][c] == self.opponent:
                    position_score -= self.POSITION_WEIGHTS[r][c]

        # Mobility (number of valid moves)
        ai_moves = len(logic.get_valid_moves(self.player))
        opp_moves = len(logic.get_valid_moves(self.opponent))
        mobility = ai_moves - opp_moves

        # Combine heuristics
        return piece_diff * 10 + position_score + mobility * 5

    def minimax(
        self,
        logic: OthelloLogic,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        """Minimax with alpha-beta pruning"""
        # Base cases
        if depth == 0 or logic.is_game_over():
            return self.evaluate_board(logic)

        current = self.player if maximizing else self.opponent
        valid_moves = logic.get_valid_moves(current)

        # Pass if no valid moves
        if not valid_moves:
            logic_copy = copy.deepcopy(logic)
            return self.minimax(logic_copy, depth - 1, alpha, beta, not maximizing)

        if maximizing:
            max_eval = float("-inf")
            for row, col in valid_moves:
                logic_copy = copy.deepcopy(logic)
                logic_copy.make_move(row, col, current)
                eval_score = self.minimax(logic_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float("inf")
            for row, col in valid_moves:
                logic_copy = copy.deepcopy(logic)
                logic_copy.make_move(row, col, current)
                eval_score = self.minimax(logic_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def get_best_move(self, logic: OthelloLogic) -> Optional[Tuple[int, int]]:
        """Get the best move using minimax"""
        valid_moves = logic.get_valid_moves(self.player)
        if not valid_moves:
            return None

        best_move = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for row, col in valid_moves:
            logic_copy = copy.deepcopy(logic)
            logic_copy.make_move(row, col, self.player)
            score = self.minimax(logic_copy, self.depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_move = (row, col)
            alpha = max(alpha, score)

        return best_move


class OthelloGame:
    """Main game class with pygame rendering"""

    def __init__(self, ai_enabled: bool = True, ai_difficulty: int = 4):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Othello Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.logic = OthelloLogic()
        self.ai_enabled = ai_enabled
        self.ai = OthelloAI(WHITE, depth=ai_difficulty) if ai_enabled else None
        self.game_over = False
        self.message = "Black's turn"
        self.ai_thinking = False

    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to board coordinates"""
        mx, my = pos
        ox, oy = BOARD_OFFSET

        if mx < ox or my < oy:
            return None

        col = (mx - ox) // CELL_SIZE
        row = (my - oy) // CELL_SIZE

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None

    def draw_board(self):
        """Draw the game board"""
        ox, oy = BOARD_OFFSET

        # Draw cells
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = ox + col * CELL_SIZE
                y = oy + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE - 2, CELL_SIZE - 2)
                pygame.draw.rect(self.screen, COLOR_GRID, rect)

                # Draw valid move indicators
                if not self.game_over and self.logic.is_valid_move(
                    row, col, self.logic.current_player
                ):
                    pygame.draw.circle(self.screen, COLOR_VALID, rect.center, 5)

                # Draw pieces
                piece = self.logic.board[row][col]
                if piece == BLACK:
                    pygame.draw.circle(
                        self.screen, COLOR_BLACK, rect.center, CELL_SIZE // 2 - 6
                    )
                elif piece == WHITE:
                    pygame.draw.circle(
                        self.screen, COLOR_WHITE, rect.center, CELL_SIZE // 2 - 6
                    )

    def draw_ui(self):
        """Draw UI elements (scores, messages)"""
        black_score, white_score = self.logic.get_score()

        # Draw scores
        score_text = f"Black: {black_score}  White: {white_score}"
        text_surface = self.font.render(score_text, True, COLOR_TEXT)
        self.screen.blit(text_surface, (BOARD_OFFSET[0], 20))

        # Draw message
        msg_surface = self.small_font.render(self.message, True, COLOR_TEXT)
        msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
        self.screen.blit(msg_surface, msg_rect)

    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click"""
        if self.game_over or self.ai_thinking:
            return

        if self.ai_enabled and self.logic.current_player == WHITE:
            return  # AI's turn

        cell = self.get_cell_from_pos(pos)
        if cell:
            row, col = cell
            if self.logic.make_move(row, col, self.logic.current_player):
                self.check_game_state()

    def ai_move(self):
        """Execute AI move"""
        if (
            not self.ai_enabled
            or self.ai is None
            or self.logic.current_player != WHITE
            or self.game_over
        ):
            return

        self.ai_thinking = True
        self.message = "AI is thinking..."
        pygame.display.flip()

        move = self.ai.get_best_move(self.logic)
        if move:
            row, col = move
            self.logic.make_move(row, col, WHITE)

        self.ai_thinking = False
        self.check_game_state()

    def check_game_state(self):
        """Check game state and update accordingly"""
        # Check if current player has valid moves
        if not self.logic.get_valid_moves(self.logic.current_player):
            # Current player must pass
            player_name = "Black" if self.logic.current_player == BLACK else "White"
            self.message = f"{player_name} has no valid moves. Passing turn."
            self.logic.switch_player()
            self.logic.consecutive_passes += 1

            # If both players passed consecutively, game is over
            if self.logic.consecutive_passes >= 2 or self.logic.is_game_over():
                self.game_over = True
                winner = self.logic.get_winner()
                if winner == BLACK:
                    self.message = "Game Over! Black wins!"
                elif winner == WHITE:
                    self.message = "Game Over! White wins!"
                else:
                    self.message = "Game Over! It's a tie!"
                return
        else:
            self.logic.consecutive_passes = 0  # Reset on valid move

        # Update message
        if not self.game_over:
            player_name = "Black" if self.logic.current_player == BLACK else "White"
            self.message = f"{player_name}'s turn"

    def run(self):
        """Main game loop"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game
                        self.logic = OthelloLogic()
                        self.game_over = False
                        self.message = "Black's turn"

            # AI move
            if (
                self.ai_enabled
                and self.logic.current_player == WHITE
                and not self.game_over
            ):
                self.ai_move()

            # Draw
            self.screen.fill(COLOR_BG)
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Create game with AI (set ai_enabled=False for 2-player mode)
    # AI difficulty: 1-6 (4 is good balance of speed and strength)
    game = OthelloGame(ai_enabled=True, ai_difficulty=4)
    game.run()
