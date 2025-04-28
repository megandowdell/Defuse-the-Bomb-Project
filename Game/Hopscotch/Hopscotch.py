# Hopscotch Game Phase – Defuse the Bomb
# Megan Dowdell

# Imports
import pygame           # Main game engine
import random           # Used for randomly placing safe tiles
import sys              # System exit
# import RPi.GPIO as GPIO  # Uncomment if using GPIO on Raspberry Pi
# import time               # For delay/reset between turns

# Pygame Setup
pygame.init()
pygame.font.init()

# Window dimensions and caption
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hopscotch Phase")
clock = pygame.time.Clock()

# Colors
BG = (10, 10, 10)            # Background
SAFE = (114, 197, 100)       # Green for correct tile (currently unused)
FAIL = (180, 38, 38)         # Red for incorrect choice
TEXT = (240, 240, 240)       # Light text
ACTIVE = (202, 95, 241)      # Purple highlight for current row
DIM = (80, 80, 80)           # Gray for inactive rows

# Fonts
FONT = pygame.font.SysFont("Arial", 30)
BIG_FONT = pygame.font.SysFont("Arial", 50)

# Layout Configuration
TILE_WIDTH = 100
TILE_HEIGHT = 60
TILE_GAP = 40      # Space between tiles
ROWS = 5           # Total levels
COLS = 4           # Columns (A–D)


# number of strikes for hopscotch
lives = 5


# Tile Generator
def generate_board(successes_per_row=2):
    board = []
    for _ in range(ROWS):
        safe = random.sample(range(COLS), successes_per_row)
        board.append(safe)  # Each row has 1 correct tile (change for more)
    return board

# Positioning Function 
def get_tile_rect(row, col, current_row):
    # Push earlier rows off screen
    y_offset = -(current_row * (TILE_HEIGHT + 60))
    x = (WIDTH - (COLS * TILE_WIDTH + (COLS - 1) * TILE_GAP)) // 2 + col * (TILE_WIDTH + TILE_GAP)
    y = 150 + row * (TILE_HEIGHT + 60) + y_offset
    return pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)

# Board Drawing
def draw_board(board, current_row, lives, selected_tile=None):
    screen.fill(BG)

    for row in range(ROWS):
        for col in range(COLS):
            tile_rect = get_tile_rect(row, col, current_row)

            # Skip rows already passed
            if row < current_row:
                continue

            # Highlight current row, dim the rest
            color = ACTIVE if row == current_row else DIM
            pygame.draw.rect(screen, color, tile_rect)

            label = FONT.render(chr(65 + col), True, TEXT)
            screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))

    # Level display
    level_text = FONT.render(f"Level: {current_row + 1}", True, TEXT)
    screen.blit(level_text, (20, 20))
    
    # Lives display
    lives_text = FONT.render(f"Lives: {lives}", True, TEXT)
    screen.blit(lives_text, (WIDTH - 180, 20))  # top-right corner


    pygame.display.flip()

# Play a Turn (for GPIO or internal use)
def play_turn(board, current_row, selected_col):
    """
    Processes a move based on selected column (0-3).
    Used by Raspberry Pi GPIO toggles.
    Returns: updated row index, and "win"/"lose"/None
    """
    if selected_col in board[current_row]:
        current_row += 1
        result = None if current_row < len(board) else "win"
    else:
        result = "lose"

    draw_board(board, current_row, lives)
    return current_row, result

# Optional GPIO Reset (not needed in GUI testing)
def wait_for_toggle_reset(toggle_pins):
    """
    Pauses game until all toggles are back to "down".
    Use this in Raspberry Pi version only.
    """
    print("Flip all toggles down to continue...")

    while True:
        all_down = all(GPIO.input(pin) == 0 for pin in toggle_pins)
        if all_down:
            break
        time.sleep(0.05)
        
        
# Main Game (for local testing)
def play_game():
    board = generate_board(successes_per_row=2)  # Create board once
    current_row = 0
    lives = 5  # Start with 5 lives

    while True:
        draw_board(board, current_row, lives)  # Now we also pass lives to draw

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                for col in range(COLS):
                    tile_rect = get_tile_rect(current_row, col, current_row)
                    if tile_rect.collidepoint(mouse_pos):
                        if col in board[current_row]:
                            # Correct tile: advance to next row
                            current_row += 1
                            if current_row == ROWS:
                                return True  # WIN!
                        else:
                            # Wrong tile: lose a life
                            lives -= 1
                            current_row = 0
                            # Flash red tile
                            pygame.draw.rect(screen, FAIL, tile_rect)
                            pygame.display.flip()
                            pygame.time.delay(500)

                            if lives == 0:
                                return False  # LOSE after 5 wrong tries

        clock.tick(60)  # Maintain 60

# Run Standalone
if __name__ == "__main__":
    won = play_game()
    screen.fill(BG)
    msg = "SUCCESS!" if won else "BOOM!"
    text = BIG_FONT.render(msg, True, TEXT)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()