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

import RPi.GPIO as GPIO
from adafruit_matrixkeypad import Matrix_Keypad
import board
from digitalio import DigitalInOut, Direction, Pull
RPi = True

pygame.mixer.init() # for game sounds

# Set up LED control
def set_led(color):
    #Set the RGB LED based on the current light color
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
    return component_button_state.value

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

    # Setup for button - FROM BOMB CONFIGS
global component_button_state
component_button_state = DigitalInOut(board.D4)
component_button_state.direction = Direction.INPUT
component_button_state.pull = Pull.DOWN

def RedLightGreenLight():
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
                if light_color == "green":
                    pass
                else:
                    set_led("off")
                    return  False # End the game immediately
                time.sleep(0.3)
            time.sleep(0.05)  #

        # Switch the light
        light_color = "green" if light_color == "red" else "red"
        set_led(light_color)
        print(f"The light is now {light_color.upper()}!")

    # Survived the game
    set_led("off")
    return True


def play_redlightgreenlight():
    dev_width = 800
    dev_height = 600
    
    WIDTH, HEIGHT = screen.get_size()
    #bg_image = pygame.image.load("redlightbg.png")
    #bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
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
    
    
    doll_red_img = pygame.image.load("redlightdoll.png")  # Doll facing player (red light)
    doll_green_img = pygame.image.load("greenlightdoll.png")  # Doll facing away (green light)
        
        # Scale images to the desired size
    doll_red_img = pygame.transform.scale(doll_red_img, (doll_width, doll_height))
    doll_green_img = pygame.transform.scale(doll_green_img, (doll_width, doll_height))
    

    # Game variables
    light_color = "red"
    game_time = 120  # seconds to win
    distance = 0
    target_distance = 75
    start_time = time.time()
    next_change_time = start_time  # Initialize for immediate first change
    # message = "Press the button ONLY when the light is GREEN"

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

    set_led(light_color)
    
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
            pygame.display.flip()  # Make sure screen is updated
            pygame.time.delay(1000)  # Show the winning state briefly
            return "win"  # Return win result directly
            
        
        # Change light color based on timing
        if current_time >= next_change_time and not game_over:
            # Switch the light
            light_color = "green" if light_color == "red" else "red"
            set_led(light_color)
            if light_color == "green":
                pygame.mixer.music.load("redlight.mp3")
            else:
                pygame.mixer.music.load("greenlight.mp3")
                
                
                 
            # Set next change time (2-5 seconds)
            next_change = random.uniform(2, 5)
            next_change_time = current_time + next_change
            message = f"THE LIGHT IS NOW {light_color.upper()}!"
            print(f"THE LIGHT IS NOW {light_color.upper()}!")
        

        # Check button press
        if button_pressed and not game_over:
            if light_color == "green":
                distance += 1
                message = f"Good move!"
                print(message)
                time.sleep(0.4)
            else:
                message = "You pressed during RED! You lose!"
                print(message)
                pygame.display.flip()
                # show_death_screen(screen)
                return "lose"
        if distance >= target_distance and not game_over:
            set_led("off")
            return "win"

#         # Check button press
#         if button_pressed and not game_over:
#             print("Button Pressed!")
#             if light_color == "green":
#                 message = "Good move!"
#                 #print("Good move!")
#             else:
#                 message = "You pressed during RED! You lose!"
#                 pygame.display.flip()
#                 #pygame.time.delay(1000)
#                 show_death_screen(screen)
#                 return "lose"
#                 #print("You pressed during RED! You lose!")
# #                         game_over = True
# #                         won = False

        
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
        

        distance_text = FONT.render(f"Distance: {distance :.0f} / {target_distance :.0f}", True, TEXT)
        screen.blit(distance_text, (margin, margin + font_size + font_size + 20))  # Position under state text
        
        # Draw message
        message_text = FONT.render(message, True, TEXT)
        message_x = WIDTH // 2 - message_text.get_width() // 2
        # Position message near the bottom of the screen
        message_y = HEIGHT - int(120 * HEIGHT / dev_height)
        screen.blit(message_text, (message_x, message_y))

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
        # else:
        #     if "win":
        #         return "win"
        #         result = FONT.render("You won! Press R to restart", True, TEXT)
        #     else:
        #         return "lose"
        #         result = FONT.render("You lost! Press R to restart", True, TEXT)
        #     result_x = WIDTH // 2 - result.get_width() // 2
        #     # Position result text at the bottom of the screen
        #     result_y = HEIGHT - int(60 * HEIGHT / dev_height)
        #     screen.blit(result, (result_x, result_y))
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
    set_led("off")
    return "win" if result else "lose"
    

    
result = play_redlightgreenlight()
#return "win" if win else "lose"
return result
pygame.display.flip()
    




