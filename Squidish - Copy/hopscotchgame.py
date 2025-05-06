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
SAFE = (0, 144, 57)       # Green for correct tile
FAIL = (180, 38, 38)         # Red for incorrect choice
TEXT = (240, 240, 240)       # Light text
#ACTIVE = (202, 95, 241)      # Purple highlight for current row
DIM = (80, 80, 80)           # Gray for inactive rows

# Tile colors - one for each column (A, B, C, D)
TILE_A_COLOR = (255, 64, 119)  # Light red
TILE_B_COLOR = (0, 194, 176)  # Light blue
TILE_C_COLOR = (134, 233, 0)  # Light green
TILE_D_COLOR = (233, 219, 0)  # Light yellow

# Create a list for easy reference
TILE_COLORS = [TILE_A_COLOR, TILE_B_COLOR, TILE_C_COLOR, TILE_D_COLOR]

# Fonts
FONT = pygame.font.Font("font1.otf", 30)
BIG_FONT = pygame.font.Font("font1.otf", 50)

# Layout Configuration
TILE_WIDTH = 100
TILE_HEIGHT = 60
TILE_GAP = 40      # Space between tiles
ROWS = 5           # Total levels
COLS = 4           # Columns (A–D)

# Tile Generator
def generate_board(successes_per_row=1):
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
def draw_board(board, current_row, selected_tile=None, show_correct=False):
    screen.fill(BG)

    for row in range(ROWS):
        for col in range(COLS):
            tile_rect = get_tile_rect(row, col, current_row)

            # Skip rows already passed
            if row < current_row:
                continue

            # Determine tile color based on various conditions
            if row == current_row:
                # For current row - use the column's designated color
                if show_correct and col in board[row]:
                    color = SAFE  # Show safe tiles when appropriate
                else:
                    color = TILE_COLORS[col]  # Use the specific color for each column
            else:
                # For future rows - use dimmed version of the column's color
                base_color = TILE_COLORS[col]
                color = tuple(max(c // 2, 0) for c in base_color)  # Dimmed version
                
            # Draw the tile with appropriate color
            pygame.draw.rect(screen, color, tile_rect)

            # Add the letter label
            label = FONT.render(chr(65 + col), True, TEXT)
            screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))

    # Level display
    level_text = FONT.render(f"Level: {current_row + 1}", True, TEXT)
    screen.blit(level_text, (20, 20))

    pygame.display.flip()

# Play a Turn (for GPIO or internal use)
def play_turn(board, current_row, selected_col):
    """
    Processes a move based on selected column (0-3).
    Used by Raspberry Pi GPIO toggles.
    Returns: updated row index, and "win"/"lose"/None
    """
    if selected_col in board[current_row]:
        # Show correct tile briefly
        draw_board(board, current_row, show_correct=True)
        pygame.display.flip()
        pygame.time.delay(300)  # Brief flash of green
        
        current_row += 1
        result = None if current_row < len(board) else "win"
    else:
        # Show failed tile
        tile_rect = get_tile_rect(current_row, selected_col, current_row)
        pygame.draw.rect(screen, FAIL, tile_rect)
        
        # Redraw the letter label
        label = FONT.render(chr(65 + selected_col), True, TEXT)
        screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))
        
        pygame.display.flip()
        pygame.time.delay(800)
        result = "lose"

    draw_board(board, current_row)
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
    board = generate_board(successes_per_row=1)
    current_row = 0

    while True:
        draw_board(board, current_row)

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
                            # Correct choice - flash green briefly
                            pygame.draw.rect(screen, SAFE, tile_rect)
                            label = FONT.render(chr(65 + col), True, TEXT)
                            screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))
                            pygame.display.flip()
                            pygame.time.delay(300)
                            
                            current_row += 1
                            if current_row == ROWS:
                                return True
                        else:
                            # Wrong choice - show red
                            pygame.draw.rect(screen, FAIL, tile_rect)
                            label = FONT.render(chr(65 + col), True, TEXT)
                            screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))
                            pygame.display.flip()
                            pygame.time.delay(800)
                            return False

        clock.tick(60)

# Run Standalone
# if __name__ == "__main__":

won = play_game()
screen.fill(BG)
msg = "SUCCESS!" if won else "BOOM!"
text = BIG_FONT.render(msg, True, TEXT)
screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
pygame.display.flip()
pygame.time.delay(2000)
pygame.quit()
