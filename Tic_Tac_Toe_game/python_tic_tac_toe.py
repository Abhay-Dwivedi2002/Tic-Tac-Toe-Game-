import pygame
import sys
import random
import time
from enum import Enum

# Initialize Pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 650
BOARD_SIZE = 300
BOARD_OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = 180
CELL_SIZE = BOARD_SIZE // 3
TIMER_DURATION = 10  # 10 seconds per turn
AI_MOVE_DELAY = 3  # 3 seconds for AI to move

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Player(Enum):
    HUMAN = 1
    AI = 2

class TicTacToe:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tic Tac Toe - Timed Battle")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 40)
        self.button_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        self.timer_font = pygame.font.Font(None, 36)
        
        # Game state
        self.state = GameState.MENU
        self.difficulty = Difficulty.MEDIUM
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = Player.HUMAN
        self.winner = None
        
        # Timer variables
        self.turn_start_time = 0
        self.time_remaining = TIMER_DURATION
        self.auto_move_made = False
        self.ai_move_timer = 0  # Timer for AI moves
        
    def reset_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = Player.HUMAN
        self.winner = None
        self.state = GameState.PLAYING
        self.turn_start_time = time.time()
        self.time_remaining = TIMER_DURATION
        self.auto_move_made = False
        self.ai_move_timer = 0
        
    def check_winner(self):
        # Check rows
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != '':
                return self.board[i][0]
        
        # Check columns
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] != '':
                return self.board[0][j]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
            
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        
        # Check for tie
        if all(self.board[i][j] != '' for i in range(3) for j in range(3)):
            return 'tie'
            
        return None
        
    def get_empty_cells(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == '']
        
    def evaluate_position(self, board, player):
        """Evaluate the current board position"""
        winner = self.check_winner_board(board)
        if winner == player:
            return 100
        elif winner and winner != player:
            return -100
        else:
            return 0
            
    def minimax(self, board, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        winner = self.check_winner_board(board)
        if winner == 'O':  # AI wins
            return 10 - depth
        elif winner == 'X':  # Human wins
            return depth - 10
        elif self.is_board_full_board(board):  # Tie
            return 0
            
        if depth > 6:  # Limit depth for performance
            return 0
            
        if is_maximizing:
            max_eval = float('-inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = 'O'
                        eval_score = self.minimax(board, depth + 1, False, alpha, beta)
                        board[i][j] = ''
                        max_eval = max(max_eval, eval_score)
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '':
                        board[i][j] = 'X'
                        eval_score = self.minimax(board, depth + 1, True, alpha, beta)
                        board[i][j] = ''
                        min_eval = min(min_eval, eval_score)
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
            return min_eval
            
    def check_winner_board(self, board):
        # Check rows
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '':
                return board[i][0]
        
        # Check columns
        for j in range(3):
            if board[0][j] == board[1][j] == board[2][j] != '':
                return board[0][j]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            return board[0][0]
            
        if board[0][2] == board[1][1] == board[2][0] != '':
            return board[0][2]
            
        return None
        
    def is_board_full_board(self, board):
        return all(board[i][j] != '' for i in range(3) for j in range(3))
        
    def find_winning_move(self, board, player):
        """Find a move that wins the game immediately"""
        for i in range(3):
            for j in range(3):
                if board[i][j] == '':
                    board[i][j] = player
                    if self.check_winner_board(board) == player:
                        board[i][j] = ''
                        return (i, j)
                    board[i][j] = ''
        return None
        
    def find_blocking_move(self, board, opponent):
        """Find a move that blocks opponent from winning"""
        return self.find_winning_move(board, opponent)
        
    def find_fork_move(self, board, player):
        """Find a move that creates two winning opportunities"""
        for i in range(3):
            for j in range(3):
                if board[i][j] == '':
                    board[i][j] = player
                    winning_moves = 0
                    for x in range(3):
                        for y in range(3):
                            if board[x][y] == '':
                                board[x][y] = player
                                if self.check_winner_board(board) == player:
                                    winning_moves += 1
                                board[x][y] = ''
                    board[i][j] = ''
                    if winning_moves >= 2:
                        return (i, j)
        return None
        
    def ai_strategic_move(self):
        """Enhanced AI strategy based on difficulty"""
        empty_cells = self.get_empty_cells()
        board_copy = [row[:] for row in self.board]
        
        # Easy mode - mostly random with some basic strategy
        if self.difficulty == Difficulty.EASY:
            if random.random() < 0.7:  # 70% random
                return random.choice(empty_cells)
        
        # Medium mode - good strategy with some randomness
        elif self.difficulty == Difficulty.MEDIUM:
            if random.random() < 0.3:  # 30% random
                return random.choice(empty_cells)
        
        # Strategic play for medium and hard modes
        
        # 1. Try to win immediately
        winning_move = self.find_winning_move(board_copy, 'O')
        if winning_move:
            return winning_move
            
        # 2. Block opponent from winning
        blocking_move = self.find_blocking_move(board_copy, 'X')
        if blocking_move:
            return blocking_move
            
        # 3. Create a fork (hard mode only)
        if self.difficulty == Difficulty.HARD:
            fork_move = self.find_fork_move(board_copy, 'O')
            if fork_move:
                return fork_move
                
            # Block opponent's fork
            opponent_fork = self.find_fork_move(board_copy, 'X')
            if opponent_fork:
                return opponent_fork
        
        # 4. Take center if available
        if self.board[1][1] == '':
            return (1, 1)
            
        # 5. Take corners (strategic positions)
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [(i, j) for i, j in corners if self.board[i][j] == '']
        if available_corners:
            return random.choice(available_corners)
            
        # 6. Take sides
        sides = [(0, 1), (1, 0), (1, 2), (2, 1)]
        available_sides = [(i, j) for i, j in sides if self.board[i][j] == '']
        if available_sides:
            return random.choice(available_sides)
            
        # 7. Fallback to minimax for hard mode
        if self.difficulty == Difficulty.HARD:
            best_score = float('-inf')
            best_move = None
            
            for i, j in empty_cells:
                board_copy[i][j] = 'O'
                score = self.minimax(board_copy, 0, False)
                board_copy[i][j] = ''
                
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
                    
            return best_move if best_move else random.choice(empty_cells)
        
        # Fallback
        return random.choice(empty_cells) if empty_cells else None
        
    def update_timer(self):
        """Update the timer and handle automatic moves"""
        if self.state != GameState.PLAYING or self.winner:
            return
            
        current_time = time.time()
        
        if self.current_player == Player.HUMAN:
            # Timer only runs for human player
            elapsed = current_time - self.turn_start_time
            self.time_remaining = max(0, TIMER_DURATION - elapsed)
            
            # Time's up - make random move for human
            if self.time_remaining <= 0 and not self.auto_move_made:
                self.auto_move_made = True
                empty_cells = self.get_empty_cells()
                
                if empty_cells:
                    row, col = random.choice(empty_cells)
                    self.board[row][col] = 'X'
                    
                    # Check for winner
                    winner = self.check_winner()
                    if winner:
                        self.winner = winner
                        self.state = GameState.GAME_OVER
                    else:
                        # Switch to AI turn
                        self.current_player = Player.AI
                        self.ai_move_timer = current_time
                        
        else:  # AI turn
            # AI moves after 3 seconds
            if current_time - self.ai_move_timer >= AI_MOVE_DELAY:
                move = self.ai_strategic_move()
                if move:
                    row, col = move
                    self.board[row][col] = 'O'
                    
                    # Check for winner
                    winner = self.check_winner()
                    if winner:
                        self.winner = winner
                        self.state = GameState.GAME_OVER
                    else:
                        # Switch to human turn
                        self.current_player = Player.HUMAN
                        self.turn_start_time = time.time()
                        self.time_remaining = TIMER_DURATION
                        self.auto_move_made = False
        
    def draw_timer(self):
        """Draw the countdown timer (only for human player)"""
        if self.current_player == Player.HUMAN:
            timer_color = RED if self.time_remaining <= 3 else ORANGE if self.time_remaining <= 5 else GREEN
            
            timer_text = f"Time: {int(self.time_remaining)}s"
            timer_surface = self.timer_font.render(timer_text, True, timer_color)
            timer_x = (WINDOW_WIDTH - timer_surface.get_width()) // 2
            self.screen.blit(timer_surface, (timer_x, 130))
            
            # Timer bar
            bar_width = 200
            bar_height = 10
            bar_x = (WINDOW_WIDTH - bar_width) // 2
            bar_y = 155
            
            # Background bar
            pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress = self.time_remaining / TIMER_DURATION
            progress_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, timer_color, (bar_x, bar_y, progress_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        else:
            # Show "AI Thinking..." for computer turn
            thinking_text = "AI Thinking..."
            thinking_surface = self.timer_font.render(thinking_text, True, BLUE)
            thinking_x = (WINDOW_WIDTH - thinking_surface.get_width()) // 2
            self.screen.blit(thinking_surface, (thinking_x, 140))
        
    def draw_button(self, x, y, width, height, text, color):
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        
        text_surface = self.button_font.render(text, True, WHITE)
        text_x = x + (width - text_surface.get_width()) // 2
        text_y = y + (height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        return button_rect
        
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        # Title
        title_text = self.title_font.render("Tic Tac Toe - Timed Battle", True, BLACK)
        title_x = (WINDOW_WIDTH - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, 50))
        
        # Subtitle
        subtitle_text = self.small_font.render("10 seconds per turn!", True, RED)
        subtitle_x = (WINDOW_WIDTH - subtitle_text.get_width()) // 2
        self.screen.blit(subtitle_text, (subtitle_x, 90))
        
        # Description
        desc_text = self.small_font.render("Choose Difficulty:", True, GRAY)
        desc_x = (WINDOW_WIDTH - desc_text.get_width()) // 2
        self.screen.blit(desc_text, (desc_x, 130))
        
        # Buttons
        button_width = 200
        button_height = 50
        button_x = (WINDOW_WIDTH - button_width) // 2
        
        easy_button = self.draw_button(button_x, 170, button_width, button_height, "Easy", GREEN)
        medium_button = self.draw_button(button_x, 240, button_width, button_height, "Medium", BLUE)
        hard_button = self.draw_button(button_x, 310, button_width, button_height, "Hard", RED)
        quit_button = self.draw_button(button_x, 420, button_width, button_height, "Quit", GRAY)
        
        # Difficulty descriptions - positioned below each button
        descriptions = [
            "AI makes mistakes often",
            "AI plays smart strategy", 
            "Perfect AI - Advanced tactics"
        ]
        
        desc_font = pygame.font.Font(None, 18)
        for i, desc in enumerate(descriptions):
            desc_surface = desc_font.render(desc, True, GRAY)
            desc_x = (WINDOW_WIDTH - desc_surface.get_width()) // 2
            desc_y = 225 + (i * 70)  # Position below each button
            self.screen.blit(desc_surface, (desc_x, desc_y))
        
        return {
            'easy': easy_button,
            'medium': medium_button,
            'hard': hard_button,
            'quit': quit_button
        }
        
    def draw_x(self, x, y, size):
        margin = size // 4
        pygame.draw.line(self.screen, RED, 
                        (x + margin, y + margin),
                        (x + size - margin, y + size - margin), 6)
        pygame.draw.line(self.screen, RED,
                        (x + size - margin, y + margin),
                        (x + margin, y + size - margin), 6)
                        
    def draw_o(self, x, y, size):
        center_x = x + size // 2
        center_y = y + size // 2
        radius = size // 3
        pygame.draw.circle(self.screen, BLUE, (center_x, center_y), radius, 6)
            
    def draw_game(self):
        self.screen.fill(WHITE)
        
        # Title
        title_text = self.title_font.render("Tic Tac Toe", True, BLACK)
        title_x = (WINDOW_WIDTH - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, 20))
        
        # Difficulty display
        diff_text = self.small_font.render(f"Difficulty: {self.difficulty.name}", True, GRAY)
        diff_x = (WINDOW_WIDTH - diff_text.get_width()) // 2
        self.screen.blit(diff_text, (diff_x, 50))
        
        # Current player
        if self.current_player == Player.HUMAN:
            player_text = "Your Turn (X)"
            color = RED
        else:
            player_text = "Computer's Turn (O)"
            color = BLUE
            
        player_surface = self.small_font.render(player_text, True, color)
        player_x = (WINDOW_WIDTH - player_surface.get_width()) // 2
        self.screen.blit(player_surface, (player_x, 75))
        
        # Timer
        self.draw_timer()
        
        # Draw board
        for i in range(4):
            # Vertical lines
            start_x = BOARD_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK,
                           (start_x, BOARD_OFFSET_Y),
                           (start_x, BOARD_OFFSET_Y + BOARD_SIZE), 3)
            # Horizontal lines
            start_y = BOARD_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, BLACK,
                           (BOARD_OFFSET_X, start_y),
                           (BOARD_OFFSET_X + BOARD_SIZE, start_y), 3)
        
        # Draw X's and O's
        for i in range(3):
            for j in range(3):
                x = BOARD_OFFSET_X + j * CELL_SIZE
                y = BOARD_OFFSET_Y + i * CELL_SIZE
                
                if self.board[i][j] == 'X':
                    self.draw_x(x, y, CELL_SIZE)
                elif self.board[i][j] == 'O':
                    self.draw_o(x, y, CELL_SIZE)
        
        # Bottom buttons
        button_width = 100
        button_height = 40
        button_y = BOARD_OFFSET_Y + BOARD_SIZE + 30
        
        menu_x = (WINDOW_WIDTH // 2) - button_width - 10
        restart_x = (WINDOW_WIDTH // 2) + 10
        
        menu_button = self.draw_button(menu_x, button_y, button_width, button_height, "Menu", GRAY)
        restart_button = self.draw_button(restart_x, button_y, button_width, button_height, "Restart", GREEN)
        
        return {
            'menu': menu_button,
            'restart': restart_button
        }
            
    def draw_game_over(self):
        buttons = self.draw_game()
        
        # Game over message
        if self.winner == 'X':
            message = "You Win!"
            color = GREEN
        elif self.winner == 'O':
            message = "Computer Wins!"
            color = RED
        else:
            message = "It's a Tie!"
            color = BLUE
            
        message_surface = self.title_font.render(message, True, color)
        message_x = (WINDOW_WIDTH - message_surface.get_width()) // 2
        message_y = 100
        
        # Background for message
        pygame.draw.rect(self.screen, WHITE, (message_x - 10, message_y - 5, 
                                            message_surface.get_width() + 20, 
                                            message_surface.get_height() + 10))
        pygame.draw.rect(self.screen, BLACK, (message_x - 10, message_y - 5, 
                                            message_surface.get_width() + 20, 
                                            message_surface.get_height() + 10), 2)
        
        self.screen.blit(message_surface, (message_x, message_y))
        
        return buttons
        
    def handle_click(self, pos):
        if self.state == GameState.MENU:
            buttons = self.draw_menu()
            
            if buttons['easy'].collidepoint(pos):
                self.difficulty = Difficulty.EASY
                self.reset_game()
            elif buttons['medium'].collidepoint(pos):
                self.difficulty = Difficulty.MEDIUM
                self.reset_game()
            elif buttons['hard'].collidepoint(pos):
                self.difficulty = Difficulty.HARD
                self.reset_game()
            elif buttons['quit'].collidepoint(pos):
                return False
                
        elif self.state == GameState.PLAYING:
            buttons = self.draw_game()
            
            if buttons['menu'].collidepoint(pos):
                self.state = GameState.MENU
            elif buttons['restart'].collidepoint(pos):
                self.reset_game()
            elif self.current_player == Player.HUMAN:
                # Check board click only during human turn
                if (BOARD_OFFSET_X <= pos[0] <= BOARD_OFFSET_X + BOARD_SIZE and
                    BOARD_OFFSET_Y <= pos[1] <= BOARD_OFFSET_Y + BOARD_SIZE):
                    
                    col = (pos[0] - BOARD_OFFSET_X) // CELL_SIZE
                    row = (pos[1] - BOARD_OFFSET_Y) // CELL_SIZE
                    
                    if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == '':
                        self.board[row][col] = 'X'
                        
                        winner = self.check_winner()
                        if winner:
                            self.winner = winner
                            self.state = GameState.GAME_OVER
                        else:
                            self.current_player = Player.AI
                            self.ai_move_timer = time.time()
                            
        elif self.state == GameState.GAME_OVER:
            buttons = self.draw_game_over()
            
            if buttons['menu'].collidepoint(pos):
                self.state = GameState.MENU
            elif buttons['restart'].collidepoint(pos):
                self.reset_game()
                
        return True
        
    def update(self):
        if self.state == GameState.PLAYING:
            self.update_timer()
                    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        running = self.handle_click(event.pos)
                        
            self.update()
            
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("🎮 Timed Tic Tac Toe Battle")
    print("=" * 30)
    print("⏰ NEW FEATURES:")
    print("• 10-second timer per turn (human only)")
    print("• AI moves in 3 seconds")
    print("• Auto-move when time runs out")

    print("\n🧠 AI Improvements:")
    print("• Easy: 70% random moves")
    print("• Medium: Smart blocking & winning")
    print("• Hard: Advanced tactics + forks")
    print("\nStarting game...")
    
    game = TicTacToe()
    game.run()