import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hop Map Demo")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREY = (180, 180, 180)
BLUE = (50, 150, 255)

# Load player sprite
player_img = pygame.image.load("menu3.jpg")  # Replace with your sprite
player_img = pygame.transform.scale(player_img, (50, 50))  # Resize to fit tile
player_rect = player_img.get_rect()

# Define hop map tile positions (x, y)
tile_positions = [
    (275, 600),       # 1
    (275, 540),       # 2
    (220, 480), (330, 480),  # 3 & 4
    (275, 420),       # 5
    (220, 360), (330, 360),  # 6 & 7
    (275, 300),       # 8
]

# Tile dimensions
tile_size = (50, 50)

# Start at first tile
current_tile_index = 0
player_rect.center = tile_positions[current_tile_index]

# Control jump cooldown
can_jump = True
jump_delay = 300  # milliseconds
last_jump_time = 0

# Main loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw tiles
    for pos in tile_positions:
        pygame.draw.rect(screen, GREY, (*pos, *tile_size), border_radius=8)

    # Handle jump logic
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    if keys[pygame.K_SPACE] and can_jump:
        current_tile_index += 1
        if current_tile_index < len(tile_positions):
            player_rect.center = tile_positions[current_tile_index]
            last_jump_time = current_time
            can_jump = False

    # Re-enable jump after delay
    if not can_jump and current_time - last_jump_time >= jump_delay:
        can_jump = True

    # Draw player
    screen.blit(player_img, player_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
