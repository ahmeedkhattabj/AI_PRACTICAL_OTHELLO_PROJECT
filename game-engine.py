import pygame
import copy
import sys
import random
from typing import List, Tuple, Optional

# --- CONSTANTS ---
BOARD_SIZE = 8
CELL_SIZE = 60
# Increased offset to make room for labels
BOARD_OFFSET_X = 60
BOARD_OFFSET_Y = 120
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET_X * 2
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET_Y + 100

# Colors
COLOR_BG = (34, 139, 34)  # Forest Green
COLOR_BOARD_BG = (0, 100, 0)  # Dark Green for grid background
COLOR_LINE = (0, 0, 0)
COLOR_BLACK = (20, 20, 20)
COLOR_WHITE = (240, 240, 240)
COLOR_VALID = (50, 255, 50)  # Bright green for hints
COLOR_TEXT = (255, 255, 255)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_HOVER = (100, 160, 210)
COLOR_WARNING = (255, 69, 0)  # Red-Orange for errors/passes

# Players
BLACK = "B"
WHITE = "W"
EMPTY = None

# Directions (Row, Col)
DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),  # Cardinals
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),  # Diagonals
]


class Button:
    """Helper class to create standard UI buttons"""

    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, screen):
        color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return (
            self.is_hovered
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        )


class OthelloLogic:
    """Core game logic for Othello/Reversi"""

    def __init__(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.initialize_board()

    def initialize_board(self):
        mid = BOARD_SIZE // 2
        self.board[mid - 1][mid - 1] = WHITE
        self.board[mid - 1][mid] = BLACK
        self.board[mid][mid - 1] = BLACK
        self.board[mid][mid] = WHITE

    def get_opponent(self, player):
        return WHITE if player == BLACK else BLACK

    def is_valid_bounds(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def get_flips(self, r, c, player):
        """Returns a list of pieces that would be flipped by placing a piece at r, c"""
        if not self.is_valid_bounds(r, c) or self.board[r][c] is not EMPTY:
            return []

        flips = []
        opponent = self.get_opponent(player)

        for dr, dc in DIRECTIONS:
            curr_r, curr_c = r + dr, c + dc
            potential_flips = []

            while (
                self.is_valid_bounds(curr_r, curr_c)
                and self.board[curr_r][curr_c] == opponent
            ):
                potential_flips.append((curr_r, curr_c))
                curr_r += dr
                curr_c += dc

            # If we found opponent pieces AND ended on our own piece, they are valid flips
            if (
                self.is_valid_bounds(curr_r, curr_c)
                and self.board[curr_r][curr_c] == player
            ):
                flips.extend(potential_flips)

        return flips

    def is_valid_move(self, r, c, player):
        return bool(self.get_flips(r, c, player))

    def get_valid_moves(self, player):
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c, player):
                    moves.append((r, c))
        return moves

    def make_move(self, r, c, player):
        flips = self.get_flips(r, c, player)
        if not flips:
            return False

        self.board[r][c] = player
        for fr, fc in flips:
            self.board[fr][fc] = player

        return True

    def get_score(self):
        b = sum(row.count(BLACK) for row in self.board)
        w = sum(row.count(WHITE) for row in self.board)
        return b, w

    def switch_turn(self):
        self.current_player = self.get_opponent(self.current_player)

    def is_game_over(self):
        # Game is over if neither player can move
        black_moves = self.get_valid_moves(BLACK)
        white_moves = self.get_valid_moves(WHITE)
        return not black_moves and not white_moves

    def get_winner(self):
        b, w = self.get_score()
        if b > w:
            return BLACK
        if w > b:
            return WHITE
        return "TIE"


class OthelloAI:
    """AI with Minimax and basic positional heuristics"""

    # Weight matrix: Corners are valuable, spaces next to corners are bad
    WEIGHTS = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, 5, 1, 1, 5, -2, 10],
        [5, -2, 1, 0, 0, 1, -2, 5],
        [5, -2, 1, 0, 0, 1, -2, 5],
        [10, -2, 5, 1, 1, 5, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10, 5, 5, 10, -20, 100],
    ]

    def __init__(self, player, difficulty):
        self.player = player
        self.difficulty = difficulty  # 1=Easy, 2=Medium, 3=Hard
        self.depth = 3 if difficulty == 3 else 1

    def get_best_move(self, logic):
        valid_moves = logic.get_valid_moves(self.player)
        if not valid_moves:
            return None

        if self.difficulty == 1:
            return random.choice(valid_moves)

        if self.difficulty == 2:
            # Greedy: Pick move that flips most pieces immediately
            best_move = valid_moves[0]
            max_flipped = -1
            for r, c in valid_moves:
                flips = len(logic.get_flips(r, c, self.player))
                if flips > max_flipped:
                    max_flipped = flips
                    best_move = (r, c)
            return best_move

        if self.difficulty == 3:
            # Minimax
            return self.minimax_root(logic, valid_moves)

    def evaluate(self, logic):
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if logic.board[r][c] == self.player:
                    score += self.WEIGHTS[r][c]
                elif logic.board[r][c] == logic.get_opponent(self.player):
                    score -= self.WEIGHTS[r][c]
        return score

    def minimax_root(self, logic, moves):
        best_score = float("-inf")
        best_move = moves[0]

        for r, c in moves:
            temp_logic = copy.deepcopy(logic)
            temp_logic.make_move(r, c, self.player)
            score = self.minimax(
                temp_logic, self.depth - 1, False, float("-inf"), float("inf")
            )
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_move

    def minimax(self, logic, depth, is_maximizing, alpha, beta):
        if depth == 0 or logic.is_game_over():
            return self.evaluate(logic)

        player = self.player if is_maximizing else logic.get_opponent(self.player)
        valid_moves = logic.get_valid_moves(player)

        if not valid_moves:
            # Pass turn logic in recursion
            return self.minimax(logic, depth - 1, not is_maximizing, alpha, beta)

        if is_maximizing:
            max_eval = float("-inf")
            for r, c in valid_moves:
                temp_logic = copy.deepcopy(logic)
                temp_logic.make_move(r, c, player)
                eval = self.minimax(temp_logic, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for r, c in valid_moves:
                temp_logic = copy.deepcopy(logic)
                temp_logic.make_move(r, c, player)
                eval = self.minimax(temp_logic, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.Font(None, 50)
        self.font = pygame.font.Font(None, 25)

        cx = WINDOW_WIDTH // 2
        # Main Menu Buttons
        self.btn_hvh = Button(cx - 100, 200, 200, 50, "Eng: Yousef VS us", self.font)
        self.btn_hvc = Button(cx - 100, 280, 200, 50, "Eng: Yousef VS AI", self.font)

        # AI Level Buttons
        self.btn_easy = Button(cx - 100, 200, 200, 50, "Easy", self.font)
        self.btn_med = Button(cx - 100, 280, 200, 50, "Medium", self.font)
        self.btn_hard = Button(cx - 100, 360, 200, 50, "Hard", self.font)
        self.btn_back = Button(cx - 100, 440, 200, 50, "Back", self.font)

    def show(self):
        """Returns (ai_enabled, difficulty). Difficulty 0 if HvH."""
        state = "MAIN"  # MAIN or DIFFICULTY
        clock = pygame.time.Clock()

        while True:
            self.screen.fill(COLOR_BG)
            mouse_pos = pygame.mouse.get_pos()

            # Draw Title
            title_text = "OTHELLO" if state == "MAIN" else "Select Difficulty"
            title_surf = self.title_font.render(title_text, True, COLOR_WHITE)
            title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
            self.screen.blit(title_surf, title_rect)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if state == "MAIN":
                for btn in [self.btn_hvh, self.btn_hvc]:
                    btn.check_hover(mouse_pos)
                    btn.draw(self.screen)
                    for event in events:
                        if btn.is_clicked(event):
                            if btn == self.btn_hvh:
                                return False, 0
                            if btn == self.btn_hvc:
                                state = "DIFFICULTY"

            elif state == "DIFFICULTY":
                buttons = [self.btn_easy, self.btn_med, self.btn_hard, self.btn_back]
                for btn in buttons:
                    btn.check_hover(mouse_pos)
                    btn.draw(self.screen)
                    for event in events:
                        if btn.is_clicked(event):
                            if btn == self.btn_easy:
                                return True, 1
                            if btn == self.btn_med:
                                return True, 2
                            if btn == self.btn_hard:
                                return True, 3
                            if btn == self.btn_back:
                                state = "MAIN"

            pygame.display.flip()
            clock.tick(60)


class OthelloGame:
    def __init__(self, screen, ai_enabled, difficulty):
        self.screen = screen
        self.ai_enabled = ai_enabled
        self.difficulty = difficulty
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.label_font = pygame.font.Font(None, 28)

        self.reset_game()

    def reset_game(self):
        self.logic = OthelloLogic()
        self.ai = OthelloAI(WHITE, self.difficulty) if self.ai_enabled else None
        self.game_over = False
        self.message = "Black's Turn"
        self.message_color = COLOR_TEXT

        # Buttons for Game Over screen
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        self.btn_play_again = Button(
            cx - 110, cy + 20, 220, 50, "Play Again", self.font
        )
        self.btn_menu = Button(cx - 110, cy + 90, 220, 50, "Main Menu", self.font)

    def draw_board(self):
        # Draw Background Panel for Grid
        grid_rect = pygame.Rect(
            BOARD_OFFSET_X,
            BOARD_OFFSET_Y,
            BOARD_SIZE * CELL_SIZE,
            BOARD_SIZE * CELL_SIZE,
        )
        pygame.draw.rect(self.screen, COLOR_BOARD_BG, grid_rect)
        pygame.draw.rect(self.screen, COLOR_LINE, grid_rect, 3)

        # Draw Labels (A-H, 1-8)
        letters = "ABCDEFGH"
        for i in range(8):
            # Top Letters
            lbl = self.label_font.render(letters[i], True, COLOR_WHITE)
            x = BOARD_OFFSET_X + i * CELL_SIZE + CELL_SIZE // 2 - lbl.get_width() // 2
            self.screen.blit(lbl, (x, BOARD_OFFSET_Y - 25))
            # Left Numbers
            lbl = self.label_font.render(str(i + 1), True, COLOR_WHITE)
            y = BOARD_OFFSET_Y + i * CELL_SIZE + CELL_SIZE // 2 - lbl.get_height() // 2
            self.screen.blit(lbl, (BOARD_OFFSET_X - 25, y))

        # Draw Cells and Pieces
        valid_moves = self.logic.get_valid_moves(self.logic.current_player)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = BOARD_OFFSET_X + c * CELL_SIZE
                y = BOARD_OFFSET_Y + r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                # Grid lines
                pygame.draw.rect(self.screen, COLOR_LINE, rect, 1)

                # Draw Piece
                piece = self.logic.board[r][c]
                if piece == BLACK:
                    pygame.draw.circle(
                        self.screen, COLOR_BLACK, rect.center, CELL_SIZE // 2 - 4
                    )
                elif piece == WHITE:
                    pygame.draw.circle(
                        self.screen, COLOR_WHITE, rect.center, CELL_SIZE // 2 - 4
                    )

                # Draw Hint (if human turn and not game over)
                if not self.game_over and (r, c) in valid_moves:
                    is_human_turn = not (
                        self.ai_enabled and self.logic.current_player == WHITE
                    )
                    if is_human_turn:
                        pygame.draw.circle(self.screen, COLOR_VALID, rect.center, 6)

    def draw_ui(self):
        # Header Info
        black_score, white_score = self.logic.get_score()

        # Difficulty Text
        mode_text = "Mode: PvP"
        if self.ai_enabled:
            diff_names = {1: "Easy", 2: "Medium", 3: "Hard"}
            mode_text = f"Mode: AI ({diff_names.get(self.difficulty)})"

        mode_surf = self.small_font.render(mode_text, True, (200, 200, 200))
        self.screen.blit(mode_surf, (20, 20))

        # Score Board
        score_text = f"Black: {black_score}   |   White: {white_score}"
        score_surf = self.font.render(score_text, True, COLOR_TEXT)
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(score_surf, score_rect)

        # Status Message
        msg_surf = self.font.render(self.message, True, self.message_color)
        msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        self.screen.blit(msg_surf, msg_rect)

    def draw_game_over(self):
        # Semi-transparent overlay
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))

        # Winner Text
        winner = self.logic.get_winner()
        if winner == BLACK:
            text = "BLACK WINS!"
        elif winner == WHITE:
            text = "WHITE WINS!"
        else:
            text = "IT'S A TIE!"

        # Color based on winner
        color = (
            COLOR_VALID
            if winner == BLACK or (winner == WHITE and not self.ai_enabled)
            else COLOR_WARNING
        )

        lbl = pygame.font.Font(None, 60).render(text, True, color)
        lbl_rect = lbl.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(lbl, lbl_rect)

        # Draw Buttons
        mouse_pos = pygame.mouse.get_pos()
        self.btn_play_again.check_hover(mouse_pos)
        self.btn_menu.check_hover(mouse_pos)
        self.btn_play_again.draw(self.screen)
        self.btn_menu.draw(self.screen)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            # Event Handling
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    return "EXIT"

                if self.game_over:
                    # Handle Game Over Inputs
                    if self.btn_play_again.is_clicked(event):
                        self.reset_game()
                    elif self.btn_menu.is_clicked(event):
                        return "MENU"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle Game Click
                    if self.ai_enabled and self.logic.current_player == WHITE:
                        continue  # Ignore clicks during AI turn

                    # Convert mouse to grid
                    mx, my = event.pos
                    cx = (mx - BOARD_OFFSET_X) // CELL_SIZE
                    cy = (my - BOARD_OFFSET_Y) // CELL_SIZE

                    if 0 <= cx < BOARD_SIZE and 0 <= cy < BOARD_SIZE:
                        if self.logic.make_move(cy, cx, self.logic.current_player):
                            self.logic.switch_turn()
                            self.message = (
                                "Black's Turn"
                                if self.logic.current_player == BLACK
                                else "White's Turn"
                            )
                            self.message_color = COLOR_TEXT
                        else:
                            self.message = "Invalid Move!"
                            self.message_color = COLOR_WARNING

            # Game Logic Loop (outside event loop)
            if not self.game_over:
                # 1. Check if game is over
                if self.logic.is_game_over():
                    self.game_over = True
                    continue

                # 2. Check for "Pass" (No valid moves)
                curr_moves = self.logic.get_valid_moves(self.logic.current_player)
                if not curr_moves:
                    p_name = "Black" if self.logic.current_player == BLACK else "White"
                    self.message = f"{p_name} has no moves! Passing..."
                    self.message_color = COLOR_WARNING

                    # Redraw immediately to show message before blocking/delay
                    self.screen.fill(COLOR_BG)
                    self.draw_board()
                    self.draw_ui()
                    pygame.display.flip()
                    pygame.time.delay(1500)  # Pause so user sees the message

                    self.logic.switch_turn()
                    continue

                # 3. AI Turn Handling
                if self.ai_enabled and self.logic.current_player == WHITE:
                    # Draw screen first so we see the board state before AI thinks
                    self.message = "Computer is thinking..."
                    self.screen.fill(COLOR_BG)
                    self.draw_board()
                    self.draw_ui()
                    pygame.display.flip()

                    # Add artificial delay for "thinking" feel
                    pygame.time.delay(500)

                    move = self.ai.get_best_move(self.logic)
                    if move:
                        self.logic.make_move(move[0], move[1], WHITE)

                    self.logic.switch_turn()
                    self.message = "Black's Turn"

            # Rendering
            self.screen.fill(COLOR_BG)
            self.draw_board()
            self.draw_ui()

            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            clock.tick(60)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Python Othello Improved")

    while True:
        menu = MenuScreen(screen)
        ai_enabled, difficulty = menu.show()

        game = OthelloGame(screen, ai_enabled, difficulty)
        result = game.run()  # result will be "MENU" or "EXIT"

        if result == "EXIT":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
