import pygame
import sys # to exitgame
from pygame.locals import * # handles events, mouse/keyboard controls etc.
import os  # for environment variables
import random
import time
from threading import Thread
from time import sleep
import bomb
from bomb_configs import *
from bomb_phases import *

# Import Raspberry Pi specific modules if available
try:
    import RPi.GPIO as GPIO
    from adafruit_matrixkeypad import Matrix_Keypad
    import board
    from digitalio import DigitalInOut, Direction, Pull
    RPi = True
except ImportError:
    RPi = False
    print("Running in simulation mode - Raspberry Pi hardware not available")

# Initialize pygame mixer for sounds
pygame.mixer.init()

# Set up LED control function
def set_led(color):
    """Set the RGB LED based on the current light color"""
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
    """Check if the hardware button is pressed."""
    if not RPi:
        return False
    return component_button_state.value

def initialize_hardware():
    """Initialize Raspberry Pi hardware if available"""
    if not RPi:
        return
        
    # Set up RGB LED pins
    global component_button_RGB
    component_button_RGB = [
        DigitalInOut(board.D17),  # Red pin
        DigitalInOut(board.D27),  # Green pin
        DigitalInOut(board.D22)   # Blue pin
    ]

    # Set each pin as output
    for pin in component_button_RGB:
        pin.direction = Direction.OUTPUT
        pin.value = True  # Initialize all LEDs to OFF

    # Setup for button
    global component_button_state
    component_button_state = DigitalInOut(board.D4)
    component_button_state.direction = Direction.INPUT
    component_button_state.pull = Pull.DOWN

def RedLightGreenLight_Console():
    """Run Red Light Green Light game in console mode with hardware LED control"""
    print("Welcome to Red Light, Green Light!")
    print("Press the button ONLY when the light is GREEN.")
    
    # Initial light color
    light_color = "red"
    set_led(light_color)
    
    game_time = 20  # seconds to win
    start_time = time.time()
    
    while (time.time() - start_time) < game_time:
        # Randomly change the light every 2-5 seconds
        next_change = random.uniform(2, 5)
        change_time = time.time() + next_change
        
        while time.time() < change_time:
            if check_button_press():
                print("Button Pressed!")
                if light_color == "green":
                    print("Good move!")
                else:
                    print("You pressed during RED! You lose!")
                    set_led("off")
                    return False  # Indicate loss
                
                time.sleep(0.3)
            time.sleep(0.05)
            
        # Switch the light
        light_color = "green" if light_color == "red" else "red"
        set_led(light_color)
        print(f"The light is now {light_color.upper()}!")
    
    # Survived the game
    print("Congratulations! You survived and won!")
    set_led("off")
    return True  # Indicate win

def show_death_screen(screen):
    """Display a death screen after losing the game"""
    WIDTH, HEIGHT = screen.get_size()
    screen.fill((0, 0, 0))  # Black background
    
    # Display game over message
    font = pygame.font.Font("font1.otf" if os.path.exists("font1.otf") else None, 36)
    text = font.render("GAME OVER", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    
    pygame.display.flip()
    pygame.time.delay(2000)  # Show for 2 seconds

def show_redlightgreenlight_game_screen(screen):
    """Main function to display and run the Red Light Green Light game with pygame"""
    # Initialize hardware if available
    initialize_hardware()
    
    # Reference dimensions for scaling
    dev_width = 800
    dev_height = 600
    
    # Get current screen dimensions
    WIDTH, HEIGHT = screen.get_size()
    
    # Game setup
    pygame.display.set_caption("Red Light Green Light")
    clock = pygame.time.Clock()
    
    # Colors
    BG = (183, 246, 244)      # Background
    SAFE = (180, 38, 38)      # For green light (red in this version)
    FAIL = (0, 144, 57)       # For red light (green in this version)
    TEXT = (0, 0, 0)          # Black text
    RED = (255, 0, 0)         # Bright red
    GREEN = (0, 255, 0)       # Bright green
    
    # Scale font sizes based on screen dimensions
    base_font_size = 30
    base_big_font_size = 50
    font_size = int(base_font_size * WIDTH / dev_width)
    big_font_size = int(base_big_font_size * HEIGHT / dev_height)
    
    # Load fonts
    try:
        FONT = pygame.font.Font("font1.otf", 16)
        BIG_FONT = pygame.font.Font("font1.otf", 26)
    except:
        FONT = pygame.font.Font(None, 16)
        BIG_FONT = pygame.font.Font(None, 26)
    
    # Load background image
    try:
        bg_image = pygame.image.load("redlight_greenlight.png")
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except:
        bg_image = None
        
    # Scale elements based on screen size
    button_size = int(200 * WIDTH / dev_width)
    margin = int(50 * WIDTH / dev_width)
    
    # Load doll images 
    doll_width = int(WIDTH * 0.5)  # 50% of screen width
    doll_height = int(doll_width * 1.8)  # aspect ratio of 1.8
    
    try:
        doll_red_img = pygame.image.load("redlightdoll.png")
        doll_green_img = pygame.image.load("greenlightdoll.png")
        
        # Scale images to the desired size
        doll_red_img = pygame.transform.scale(doll_red_img, (doll_width, doll_height))
        doll_green_img = pygame.transform.scale(doll_green_img, (doll_width, doll_height))
    except:
        # Fallback if images can't be loaded
        doll_red_img = pygame.Surface((doll_width, doll_height))
        doll_red_img.fill(RED)
        doll_green_img = pygame.Surface((doll_width, doll_height))
        doll_green_img.fill(GREEN)

    # Game variables
    light_color = "red"
    game_time = 20  # seconds to win
    distance = 0
    target_distance = 75
    start_time = time.time()
    next_change_time = start_time  # Initialize for immediate first change
    message = "Press the button ONLY when the light is GREEN"
    
    # Game state variables
    running = True
    game_over = False
    won = False
    
    # Start with red LED on hardware
    set_led(light_color)
    
    while running:
        current_time = time.time()
        elapsed_time = current_time - start_time
        time_left = max(0, game_time - elapsed_time)
        
        # Draw background
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(BG)
        
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
        
        # Check hardware button
        hardware_button_pressed = check_button_press()
        if hardware_button_pressed:
            button_pressed = True
        
        # Check win condition (time elapsed)
        if time_left <= 0 and not game_over:
            message = "Congratulations! You survived and won!"
            game_over = True
            won = True
            set_led("off")  # Turn off LED
            pygame.display.flip()  # Update screen
            pygame.time.delay(1000)  # Show winning state briefly
            return "win"
        
        # Change light color based on timing
        if current_time >= next_change_time and not game_over:
            # Switch the light
            light_color = "green" if light_color == "red" else "red"
            set_led(light_color)  # Update hardware LED
            
            # Play sound effect
            try:
                pygame.mixer.music.stop()
                if light_color == "green":
                    pygame.mixer.music.load("redlight.mp3")
                else:
                    pygame.mixer.music.load("greenlight.mp3")
                pygame.mixer.music.play()
            except:
                pass
                
            # Set next change time (2-5 seconds)
            next_change = random.uniform(2, 5)
            next_change_time = current_time + next_change
            message = f"THE LIGHT IS NOW {light_color.upper()}!"
            print(f"THE LIGHT IS NOW {light_color.upper()}!")
        
        # Check button press
        if button_pressed and not game_over:
            print("Button Pressed!")
            if light_color == "green":
                distance += 1
                message = "Good move!"
                print(message)
                time.sleep(0.4)
            else:
                message = "You pressed during RED! You lose!"
                print(message)
                set_led("off")  # Turn off LED
                pygame.display.flip()
                show_death_screen(screen)
                return "lose"
        
        # Check distance win condition
        if distance >= target_distance and not game_over:
            set_led("off")  # Turn off LED
            return "win"
        
        # Draw doll image based on light color
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
        screen.blit(time_text, (margin, margin + font_size + 10))
        
        distance_text = FONT.render(f"Distance: {distance:.0f} / {target_distance:.0f}", True, TEXT)
        screen.blit(distance_text, (margin, margin + font_size + font_size + 20))
        
        # Draw message
        message_text = FONT.render(message, True, TEXT)
        message_x = WIDTH // 2 - message_text.get_width() // 2
        message_y = HEIGHT - int(120 * HEIGHT / dev_height)
        screen.blit(message_text, (message_x, message_y))
        
        # Draw instructions
        if not game_over:
            instructions = FONT.render("Press SPACE or CLICK to move forward", True, TEXT)
            instructions_x = WIDTH // 2 - instructions.get_width() // 2
            instructions_y = HEIGHT - int(60 * HEIGHT / dev_height)
            screen.blit(instructions, (instructions_x, instructions_y))
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
    
    # Turn off LED before leaving
    set_led("off")
    return "lose"  # Default to lose if the game is exited

def play_red_light_green_light(mode="console"):
    """Main function to start the Red Light Green Light game
    
    Args:
        mode (str): 'console' for text-based game or 'pygame' for graphical game
    
    Returns:
        str: "win" or "lose" indicating the game result
    """
    # Initialize hardware
    initialize_hardware()
    
    if mode == "console":
        # Run console version
        result = RedLightGreenLight_Console()
        return "win" if result else "lose"
    else:
        # Run pygame version if pygame is available
        if 'pygame' in sys.modules:
            pygame.init()
            screen = pygame.display.set_mode((800, 600))
            result = show_redlightgreenlight_game_screen(screen)
            return result
        else:
            print("Pygame not available, falling back to console mode")
            result = RedLightGreenLight_Console()
            return "win" if result else "lose"

# Main execution
if __name__ == "__main__":
    # Check if pygame is available and if we should use graphical mode
    use_graphical = 'pygame' in sys.modules
    
    # Determine which mode to use
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        mode = "console"
    else:
        mode = "pygame" if use_graphical else "console"
    
    # Run the game
    result = play_red_light_green_light(mode)
    print(f"Game result: {result}")
