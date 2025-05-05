import pygame
#from menu import show_menu_screen

def show_death_screen(screen):
    # Get screen dimensions
    pygame.mixer.music.load("gunshot.mp3")
    pygame.mixer.music.play(2)
    WIDTH, HEIGHT = screen.get_size()
    
    # Colors
    BLACK = (0, 0, 0)
    PINK = (255, 105, 180)
    
    # Load and scale coffin sprite
    coffin_width = 300
    coffin_height = 150
    coffin_sprite = pygame.image.load("coffin.jpg")
    coffin_sprite = pygame.transform.scale(coffin_sprite, (coffin_width, coffin_height))
    
    # Load font and prepare text
    font = pygame.font.Font("font1.otf", int(WIDTH * 0.15))
    game_over_text = font.render("GAME OVER", True, PINK)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Animation settings
    duration = 4.0  # seconds for full animation
    fps = 60
    total_frames = int(duration * fps)
    text_delay = 30  # frames to wait after coffin passes center
    
    # Animation loop variables
    clock = pygame.time.Clock()
    frame_count = 0
    passed_center = False
    text_counter = 0
    show_text = False
    
    # Main animation loop
    running = True
    while running and frame_count < total_frames + 60:  # Add extra time at end
        screen.fill(BLACK)
        
        # Calculate coffin position
        progress = min(1.0, frame_count / total_frames)
        start_y = -coffin_height
        end_y = HEIGHT + coffin_height
        current_y = start_y + progress * (end_y - start_y)
        
        # Check if coffin passed center
        if current_y > HEIGHT / 2 and not passed_center:
            passed_center = True
        
        # Handle text delay and appearance
        if passed_center:
            text_counter += 1
            if text_counter >= text_delay and not show_text:
                show_text = True
        
        # Draw coffin
        sprite_rect = coffin_sprite.get_rect(center=(WIDTH // 2, current_y))
        screen.blit(coffin_sprite, sprite_rect)
        
        # Draw text with fade-in effect if it's time
        if show_text:
            fade_progress = min(1.0, (text_counter - text_delay) / 15)
            text_alpha = int(255 * fade_progress)
            
            text_surface = pygame.Surface(text_rect.size, pygame.SRCALPHA)
            temp_text = font.render("GAME OVER", True, (PINK[0], PINK[1], PINK[2], text_alpha))
            text_surface.blit(temp_text, (0, 0))
            screen.blit(text_surface, text_rect)
        
        # Update display
        pygame.display.flip()
        
        # Check for exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and show_text:
                # Only allow exit after text has appeared
                running = False
        
        # Advance animation
        frame_count += 1
        clock.tick(fps)
        
    return "Menu"

# # This is how you would run it standalone for testing
# if __name__ == "__main__":
#     pygame.init()
#     WIDTH, HEIGHT = 288, 512
#     screen = pygame.display.set_mode((WIDTH, HEIGHT))
#     pygame.display.set_caption("Death Screen")
#     show_death_screen(screen)
#     pygame.quit()