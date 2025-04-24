#Hopscotch Game
#Megan Dowdell


import pygame
import random
import sys

# Initialize
pygame.init()
pygame.font.init()

# Screen
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hopscotch Phase")
clock = pygame.time.Clock()

# Fonts & Colors
FONT = pygame.font.SysFont("Arial", 30)
BIG_FONT = pygame.font.SysFont("Arial", 50)

BG = (10, 10, 10)
SAFE = (114, 197, 100)
FAIL = (180, 38, 38)
TEXT = (240, 240, 240)
ACTIVE = (202, 95, 241)  # Purple highlight for current row
DIM = (80, 80, 80)

TILE_WIDTH = 100
TILE_HEIGHT = 60
TILE_GAP = 40
ROWS = 5
COLS = 4

def generate_board(successes_per_row=1):
    board = []
    for _ in range(ROWS):
        safe = random.sample(range(COLS), successes_per_row)
        board.append(safe)
    return board

def get_tile_rect(row, col, current_row):
    # Shift everything upward based on current row
    y_offset = -(current_row * (TILE_HEIGHT + 60))
    x = (WIDTH - (COLS * TILE_WIDTH + (COLS - 1) * TILE_GAP)) // 2 + col * (TILE_WIDTH + TILE_GAP)
    y = 150 + row * (TILE_HEIGHT + 60) + y_offset
    return pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)

def draw_board(board, current_row, selected_tile=None):
    screen.fill(BG)

    for row in range(ROWS):
        for col in range(COLS):
            tile_rect = get_tile_rect(row, col, current_row)

            # Skip if row already passed
            if row < current_row:
                continue

            color = DIM
            if row == current_row:
                color = ACTIVE
            pygame.draw.rect(screen, color, tile_rect)
            label = FONT.render(chr(65 + col), True, TEXT)
            screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))

    level_text = FONT.render(f"Level: {current_row + 1}", True, TEXT)
    screen.blit(level_text, (20, 20))
    pygame.display.flip()

def play_game():
    board = generate_board(successes_per_row=1)
    current_row = 0
    game_over = False

    while not game_over:
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
                            current_row += 1
                            if current_row == ROWS:
                                return True  # Win
                        else:
                            # Flash red on wrong tile
                            pygame.draw.rect(screen, FAIL, tile_rect)
                            pygame.display.flip()
                            pygame.time.delay(800)
                            return False  # Loss

        clock.tick(60)

# Test the file on its own
if __name__ == "__main__":
    won = play_game()
    screen.fill(BG)
    msg = "SUCCESS!" if won else "BOOM!"
    text = BIG_FONT.render(msg, True, TEXT)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()