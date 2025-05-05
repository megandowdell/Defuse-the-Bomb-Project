# Tic Tac Toe Game - Megan Dowdell

import pygame  # GUI/game library
import sys     # For exiting the game
import random  # For CPU move selection
import time

# Initialize pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 600, 600  # Dimensions of game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create window
pygame.display.set_caption('Tic Tac Toe')  # Window title

# Game board setup
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS  # Size of each cell

# Line and shape settings
LINE_WIDTH = 15
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4  # Spacing inside squares for shapes

# Colors
BG_COLOR = (28, 170, 156)       # Background
LINE_COLOR = (23, 145, 135)     # Grid lines
CIRCLE_COLOR = (239, 231, 200)  # CPU's move
CROSS_COLOR = (66, 66, 66)      # Player's move
WIN_LINE_COLOR = (255, 50, 50)

# Fonts 
SCORE_FONT = pygame.font.SysFont("Arial", 26)
ROUND_FONT = pygame.font.SysFont("Arial", 42)
MESSAGE_FONT = pygame.font.SysFont("Arial", 36)

# Draws the grid lines for the board
def draw_lines():
    screen.fill(BG_COLOR)  # Fill screen with background color
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

# Draw X (player) and O (CPU) based on board values
def draw_figures(board):
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:  # Player move
                pygame.draw.line(screen, CROSS_COLOR, 
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE),
                                 CROSS_WIDTH)
            elif board[row][col] == 2:  # CPU move
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   CIRCLE_RADIUS, CIRCLE_WIDTH)

# Place a move on the board
def mark_square(board, row, col, player):
    board[row][col] = player

# Check if a square is empty
def available_square(board, row, col):
    return board[row][col] == 0

# Check if the board is completely filled
def is_board_full(board):
    return all(cell != 0 for row in board for cell in row)

# Check win condition for a player and return coordinates for winning line to be drawn
def check_win(board, player):
    # Check rows
    for row in board:
        if row.count(player) == BOARD_COLS:
            return True, [(0, row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                          (WIDTH, row * SQUARE_SIZE + SQUARE_SIZE // 2)]
    # Check columns
    for col in range(BOARD_COLS):
        if all(board[row][col] == player for row in range(BOARD_ROWS)):
            return True, [(col * SQUARE_SIZE + SQUARE_SIZE // 2, 0), 
                          (col * SQUARE_SIZE + SQUARE_SIZE // 2, HEIGHT)]

   # Check diagonals
    if all(board[i][i] == player for i in range(BOARD_ROWS)):
        return True, [(SPACE, SPACE), (WIDTH - SPACE, HEIGHT - SPACE)]
    if all(board[i][BOARD_COLS - 1 - i] == player for i in range(BOARD_ROWS)):
        return True, [(WIDTH - SPACE, SPACE), (SPACE, HEIGHT - SPACE)]
    return False, None

#Draw winning line
def draw_win_line(line_coords):
    pygame.draw.line(screen, WIN_LINE_COLOR, line_coords[0], line_coords[1], LINE_WIDTH)
    
# Random move by CPU (could be made smarter later)
def computer_move(board):
    available = [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] == 0]
    return random.choice(available) if available else (None, None)

# Display the round number and score on screen
def show_score(round_num, player_score, cpu_score):
    score_text = SCORE_FONT.render(f"Round {round_num} | You: {player_score}  CPU: {cpu_score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))  # Draw at top left

# Show "Round X starts!" between rounds
def show_next_round(round_num):
    screen.fill((0, 0, 0))
    text = ROUND_FONT.render(f"Round {round_num} starts!", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(1000)  # 1.5 seconds


# Show next round
def show_round_result(round_num):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    if result == "player":
        text = MESSAGE_FONT.render("You won this round!", True, (255, 255, 255))
    elif result == "cpu":
        text = MESSAGE_FONT.render("CPU won this round!", True, (255, 255, 255))
    else:
        text = MESSAGE_FONT.render("It's a tie!", True, (255, 255, 255))
    
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(800)  # Show message for 2 seconds

# Main game function
def play_tic_tac_toe():
    player_score = 0
    cpu_score = 0
    round_number = 1

    while True:
        # Empty board: 0 = empty, 1 = player, 2 = cpu
        board = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        draw_lines()
        show_score(round_number, player_score, cpu_score)
        pygame.display.update()

        player = 1  # Player goes first
        running = True
        winner = None
        win_line = None
        game_over = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Player's turn (left click)
                if player == 1 and event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]
                    clicked_row = mouseY // SQUARE_SIZE
                    clicked_col = mouseX // SQUARE_SIZE
                    
                    if 0 <= clicked_row < BOARD_ROWS and 0 <= clicked_col < BOARD_COLS: # Checks for valid click inside board
                        if available_square(board, clicked_row, clicked_col):
                            mark_square(board, clicked_row, clicked_col, 1)
                            win, win_line = check_win(board, 1)
                            if win:
                                player_score += 1
                                winner = "player"
                                game_over = True
                            elif is_board_full(board):
                                winner = "tie"
                                game_over = True
                            else:
                                player = 2  # Switch to CPU turn

            # CPU turn (random move)
            if player == 2 and not game_over:
                 # Add a small delay to make the CPU's move visible
                pygame.time.delay(75)
                
                row, col = computer_move(board)
                if row is not None and col is not None:
                    mark_square(board, row, col, 2)
                    win, win_line = check_win(board, 2)
                    if win:
                        cpu_score += 1
                        winner = "cpu"
                        game_over = True
                    elif is_board_full(board):
                        winner = "tie"
                        game_over = True
                    else:
                        player = 1   # Switch to player turn

            # Draw shapes and update score
            draw_lines()
            draw_figures(board)
            show_score(round_number, player_score, cpu_score)
            
            # Draw winning line if there is one
            if win_line:
                draw_win_line(win_line)
                
            pygame.display.update()
            
            # Handle game over state
            if game_over and not running:
                pygame.time.delay(1000)  # Wait before showing round result
                show_round_result(winner)
                running = False
            
            # If board is full without a winner
            if is_board_full(board) and not winner:
                winner = "tie"
                game_over = True
                pygame.time.delay(1000)
                show_round_result(winner)
                running = False

            # If game is over, wait a bit then end this round
            if game_over and running:
                pygame.display.update()
                pygame.time.delay(800)
                running = False
     

        # If someone wins 3 rounds: declare final outcome
        if player_score == 3:
            return "win"
        elif cpu_score == 3:
            return "lose"

        # Prepare for next round
        round_number += 1
        pygame.time.delay(800)
        show_next_round(round_number)

# Run this file standalone for testing
if __name__ == "__main__":
    result = play_tic_tac_toe()
    print("Result:", result)