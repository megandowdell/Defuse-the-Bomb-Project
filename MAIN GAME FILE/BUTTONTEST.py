import pygame
import sys
import os
import random
import time
from threading import Thread
from time import sleep
import bomb
from bomb_configs import *
from bomb_phases import *

# Try different display drivers
# Comment out the one you don't want to use
# os.environ["SDL_VIDEODRIVER"] = "fbcon"  # Framebuffer console
os.environ["SDL_VIDEODRIVER"] = "x11"    # X11 window system
os.environ["SDL_VIDEO_CENTERED"] = "1"

# Print diagnostic info
print("Setting up environment...")
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir())

import RPi.GPIO as GPIO
from adafruit_matrixkeypad import Matrix_Keypad
import board
from digitalio import DigitalInOut, Direction, Pull

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Initialize pygame
print("Initializing pygame...")
pygame.init()
pygame.mixer.init()



def show_death_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    screen.fill((0, 0, 0))  # Black background
    
    font = pygame.font.Font("font1.otf", 36)
    text = font.render("YOU DIED!", True, (255, 0, 0))  # Red text
    
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    
    pygame.display.flip()
    pygame.time.delay(2000)  # 2 seconds

def show_redlightgreenlight_game_screen(screen):
    print("Starting Red Light Green Light game...")
    
    # Define constants needed in the inner function
    dev_width = 800
    dev_height = 600
    
    # Set up hardware
    component_button_RGB = [
        DigitalInOut(board.D17),  # Red pin
        DigitalInOut(board.D27),  # Green pin
        DigitalInOut(board.D22)   # Blue pin
    ]

    for pin in component_button_RGB:
        pin.direction = Direction.OUTPUT
        pin.value = True  # Initialize all LEDs to OFF

    # Setup for button
    component_button_state = DigitalInOut(board.D4)
    component_button_state.direction = Direction.INPUT
    component_button_state.pull = Pull.DOWN
    
    # Define hardware interaction functions
    def check_button_press():
        """Check if the button is pressed."""
        return component_button_state.value
    
    def set_led(color):
        """Set the RGB LED based on the current light color"""
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
    
    # Load music
    pygame.mixer.music.stop()
    pygame.mixer.music.load("fly_me.mp3")
    pygame.mixer.music.play(-1)
    
    def play_redlightgreenlight():
        WIDTH, HEIGHT = screen.get_size()
        pygame.display.set_caption("Red Light Green Light")
        clock = pygame.time.Clock()

        # Colors
        BG = (183, 246, 244)
        SAFE = (180, 38, 38)
        FAIL = (0, 144, 57)
        TEXT = (0, 0, 0)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)

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
        doll_width = int(WIDTH * 0.5)
        doll_height = int(doll_width * 1.8)

        doll_red_img = pygame.image.load("redlightdoll.jpg")
        doll_green_img = pygame.image.load("greenlightdoll.jpg")

        doll_red_img = pygame.transform.scale(doll_red_img, (doll_width, doll_height))
        doll_green_img = pygame.transform.scale(doll_green_img, (doll_width, doll_height))

        # Game variables
        light_color = "red"
        game_time = 20
        distance = 0
        target_distance = 75
        start_time = time.time()
        next_change_time = start_time
        message = "Wait for GREEN light to move!"

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
                        return show_redlightgreenlight_game_screen(screen)

                if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    button_pressed = True

            if time_left <= 0 and not game_over:
                message = "Congratulations! You survived and won!"
                game_over = True
                won = True
                pygame.display.flip()
                pygame.time.delay(1000)
                return "win"

            # Change light color
            if current_time >= next_change_time and not game_over:
                light_color = "green" if light_color == "red" else "red"
                set_led(light_color)  # Set the LED to match the game state
                if light_color == "green":
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("redlight.mp3")
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("greenlight.mp3")
                    pygame.mixer.music.play()

                next_change = random.uniform(2, 5)
                next_change_time = current_time + next_change
                message = f"THE LIGHT IS NOW {light_color.upper()}!"
                print(message)

            if (button_pressed or check_button_press()) and not game_over:
                print("Button Pressed!")
                if light_color == "green":
                    distance += 1
                    message = "Good move!"
                    time.sleep(0.4)
                else:
                    message = "You pressed during RED! You lose!"
                    pygame.display.flip()
                    show_death_screen(screen)
                    return "lose"

            if distance >= target_distance and not game_over:
                return "win"

            # Draw doll image
            doll_img = doll_red_img if light_color == "red" else doll_green_img
            doll_x = WIDTH // 2 - doll_width // 2
            doll_y = HEIGHT // 2 - doll_height // 2
            screen.blit(doll_img, (doll_x, doll_y))

            color = SAFE if light_color == "green" else FAIL
            pygame.draw.rect(screen, color, (
                WIDTH - button_size - margin,
                margin,
                button_size,
                button_size))

            # Draw text
            screen.blit(FONT.render(f"State: {light_color.upper()}", True, TEXT), (margin, margin))
            screen.blit(FONT.render(f"Time: {time_left:.1f}s", True, TEXT), (margin, margin + font_size + 10))
            screen.blit(FONT.render(f"Distance: {distance:.0f} / {target_distance:.0f}", True, TEXT),
                        (margin, margin + font_size * 2 + 20))

            message_text = FONT.render(message, True, TEXT)
            screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2,
                                    HEIGHT - int(120 * HEIGHT / dev_height)))

            if not game_over:
                instructions = FONT.render("Press SPACE or CLICK to move forward", True, TEXT)
                screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2,
                                        HEIGHT - int(60 * HEIGHT / dev_height)))
            else:
                result = FONT.render("You won! Press R to restart" if won else "You lost! Press R to restart", True, TEXT)
                screen.blit(result, (WIDTH // 2 - result.get_width() // 2,
                                    HEIGHT - int(60 * HEIGHT / dev_height)))

            pygame.display.flip()
            clock.tick(60)
            
        return "lose"  # Default return if loop exits without winning
    
    # Call the inner function and return its result
    result = play_redlightgreenlight()
    return result
