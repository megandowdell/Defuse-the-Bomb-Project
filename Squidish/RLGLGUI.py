import pygame
import time
import random
import os
import sys

# Initialize pygame
pygame.init()

# Development reference dimensions
# Using landscape reference for calculations, but the game runs in portrait mode
dev_width = 800
dev_height = 600

# Default vertical reference dimensions for the portrait mode
portrait_width = 576
portrait_height = 1024

# Set up LED control
def set_led(color):
    #Set the RGB LED based on the current light color
    if not RPi:
        return
    if color == "green":
        component_button_RGB[0].value = True   # Red OFF
        component_button_RGB[1].value = False  # Green ON
        component_button_RGB[2].value = True   # Blue OFF
    elif color == "red":
        component_button_RGB[0].value = False  # Red ON
        component_button_RGB[1].value = True   # Green OFF
        component_button_RGB[2].value = True   # Blue OFF
    else:
        # turn everything off
        for pin in component_button_RGB:
            pin.value = True

def check_button_press():
    """Check if the button is pressed."""
    if not RPi:
        return False
    return component_button_state.value





def show_redlightgreenlight_game_screen(screen):
    # First show the instructions screen
    #result = show_redlightgreenlight_instructions_screen(screen)
    
    # Only proceed to the game if the player clicked "Play"
    #if result == "Play":
        # Get current screen dimensions
        def play_redlightgreenlight():
            WIDTH, HEIGHT = screen.get_size()
            #bg_image = pygame.image.load("redlightbg.png")
            #bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            pygame.display.set_caption("Red Light Green Light")
            clock = pygame.time.Clock()
            
            # Colors
            BG = (183, 246, 244)            # Background
            #SAFE = (0, 144, 57)          # Green for correct
            SAFE = (180, 38, 38)
            FAIL = (0, 144, 57)
            #FAIL = (180, 38, 38)         # Red for incorrect
            TEXT = (0, 0, 0)       # Light text
            RED = (255, 0, 0)            # Bright red
            GREEN = (0, 255, 0)          # Bright green
            
            #screen.blit(bg_image, (0, 0))
            
            # Scale font sizes based on screen dimensions
            base_font_size = 30
            base_big_font_size = 50
            font_size = int(base_font_size * WIDTH / dev_width)
            big_font_size = int(base_big_font_size * HEIGHT / dev_height)
            
            # Fonts
            
            FONT = pygame.font.Font("font1.otf", 16)
            BIG_FONT = pygame.font.Font("font1.otf", 26)
            
            bg_image = pygame.image.load("redlight_greenlight.png") 
            bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            screen.blit(bg_image, (0, 0))
            
            # Scale elements based on screen size
            button_size = int(200 * WIDTH / dev_width)
            margin = int(50 * WIDTH / dev_width)
            
            # Load doll images 
            doll_width = int(WIDTH * 0.5)  # 50% of screen width
            doll_height = int(doll_width * 1.8)  # aspect ratio of 1.8
            
            
            doll_red_img = pygame.image.load("redlightdollZ.png")  # Doll facing player (red light)
            doll_green_img = pygame.image.load("greenlightdollZ.png")  # Doll facing away (green light)
                
                # Scale images to the desired size
            doll_red_img = pygame.transform.scale(doll_red_img, (doll_width, doll_height))
            doll_green_img = pygame.transform.scale(doll_green_img, (doll_width, doll_height))
            
            
            # Game variables
            light_color = "red"
            game_time = 20  # seconds to win
            start_time = time.time()
            next_change_time = start_time  # Initialize for immediate first change
            #message = "Press the button ONLY when the light is GREEN"
            
            # Game state variables
            running = True
            game_over = False
            won = False
            
            while running:
                current_time = time.time()
                elapsed_time = current_time - start_time
                time_left = max(0, game_time - elapsed_time)
                screen.blit(bg_image, (0, 0))
                
                # Process events
                button_pressed = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not game_over:
                            button_pressed = True
                        if event.key == pygame.K_r and game_over:
                            # Restart the game
                            return show_redlightgreenlight_game_screen(screen)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                        button_pressed = True
                
                # Check win condition (time elapsed)
                if time_left <= 0 and not game_over:
                    message = "Congratulations! You survived and won!"
                    game_over = True
                    won = True
                
                # Change light color based on timing
                if current_time >= next_change_time and not game_over:
                    # Switch the light
                    light_color = "green" if light_color == "red" else "red"
                    
                    # Set next change time (2-5 seconds)
                    next_change = random.uniform(2, 5)
                    next_change_time = current_time + next_change
                    message = f"THE LIGHT IS NOW {light_color.upper()}!"
                    print(f"THE LIGHT IS NOW {light_color.upper()}!")
                
                # Check button press
                if button_pressed and not game_over:
                    print("Button Pressed!")
                    if light_color == "green":
                        message = "Good move!"
                        print("Good move!")
                    else:
                        message = "You pressed during RED! You lose!"
                        print("You pressed during RED! You lose!")
                        game_over = True
                        won = False
                
                # Draw doll image based on light color
                # Select the appropriate image
                doll_img = doll_red_img if light_color == "red" else doll_green_img
                
                # Position doll (centered)
                doll_x = WIDTH // 2 - doll_width // 2  # Center horizontally
                doll_y = HEIGHT // 2 - doll_height // 2  # Center vertically 
                screen.blit(doll_img, (doll_x, doll_y))
                
                # Draw color indicator in top right
                color = SAFE if light_color == "green" else FAIL
                pygame.draw.rect(screen, color, (
                    WIDTH - button_size - margin, 
                    margin, 
                    button_size, 
                    button_size))
                
                # Draw state and time display
                state_text = FONT.render(f"State: {light_color.upper()}", True, TEXT)
                screen.blit(state_text, (margin, margin))
                
                time_text = FONT.render(f"Time: {time_left:.1f}s", True, TEXT)
                screen.blit(time_text, (margin, margin + font_size + 10))  # Position under state text
                
                # Draw message
                message_text = FONT.render(message, True, TEXT)
                message_x = WIDTH // 2 - message_text.get_width() // 2
                # Position message near the bottom of the screen
                message_y = HEIGHT - int(120 * HEIGHT / dev_height)
                screen.blit(message_text, (message_x, message_y))
                
                # Draw instructions
                if not game_over:
                    instructions = FONT.render("Press SPACE or CLICK to move forward", True, TEXT)
                    instructions_x = WIDTH // 2 - instructions.get_width() // 2
                    # Position instructions at the bottom of the screen
                    instructions_y = HEIGHT - int(60 * HEIGHT / dev_height)
                    screen.blit(instructions, (instructions_x, instructions_y))
                else:
                    if won:
                        result = FONT.render("You won! Press R to restart", True, TEXT)
                    else:
                        result = FONT.render("You lost! Press R to restart", True, TEXT)
                    result_x = WIDTH // 2 - result.get_width() // 2
                    # Position result text at the bottom of the screen
                    result_y = HEIGHT - int(60 * HEIGHT / dev_height)
                    screen.blit(result, (result_x, result_y))
                
                # Update display
                pygame.display.flip()
                
                # Control frame rate
                clock.tick(60)
            
            return "win" if won else "lose"
        
        result = play_redlightgreenlight()
        return result
        pygame.display.flip()
# Main game function for standalone testing
def main():
    # Initialize pygame and screen
    pygame.init()
    # Use the 576x1024 screen dimensions (portrait orientation for the game)
    screen = pygame.display.set_mode((288, 512))
    
    # Run the game
    show_redlightgreenlight_game_screen(screen)
    
    # Quit pygame
    pygame.quit()

if __name__ == "__main__":
    main()