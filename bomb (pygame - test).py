#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: 
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

import pygame
import sys

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Defuse the Bomb")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont("courier", 16)

# Global display variables
boot_text_display = ""
timer_display = "Time left: "
keypad_display = "Combination: "
wires_display = "Wires: "
button_display = "Button: "
toggles_display = "Toggles: "
strikes_display = f"Strikes left: {NUM_STRIKES}"

# Game state
boot_complete = False
game_over = False
game_success = False

###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0): # CHECKED
    global boot_text_display, boot_complete
    
    # if we're not animating (or we're at the end of the bootup text)
    if (not ANIMATE or n == len(boot_text)):
        # if we're not animating, render the entire text at once (and don't process \x00)
        if (not ANIMATE):
            boot_text_display = boot_text.replace("\x00", "")
        # mark bootup as complete
        boot_complete = True
        # setup the phase threads, execute them, and check their statuses
        if (RPi):
            setup_phases()
            # Schedule phase checking
            pygame.time.set_timer(CHECK_PHASES_EVENT, 100)
    # if we're animating
    else:
        # add the next character (but don't render \x00 since it specifies a longer pause)
        if (boot_text[n] != "\x00"):
            boot_text_display += boot_text[n]

        # schedule the next character
        delay = 25 if boot_text[n] != "\x00" else 750
        pygame.time.set_timer(BOOTUP_EVENT, delay, 1)  # One-time event
        next_bootup_index = n + 1

# sets up the phase threads
def setup_phases(): # CHECKED
    global timer, keypad, wires, button, toggles
    
    # setup the timer thread
    timer = Timer(component_7seg, COUNTDOWN)
    # setup the keypad thread
    keypad = Keypad(component_keypad, keypad_target)
    # setup the jumper wires thread
    wires = Wires(component_wires, wires_target)
    # setup the pushbutton thread
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target)

    # start the phase threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

# checks the phase threads
def check_phases(): #CHECKED
    global active_phases, strikes_left, timer_display, keypad_display, wires_display, button_display, toggles_display, strikes_display, game_over, game_success
    
    # check the timer
    if (timer._running):
        # update the display
        timer_display = f"Time left: {timer}"
    else:
        # the countdown has expired -> explode!
        turn_off()
        game_over = True
        game_success = False
        # don't check any more phases
        return False
    
    # check the keypad
    if (keypad._running):
        # update the display
        keypad_display = f"Combination: {keypad}"
        # the phase is defused -> stop the thread
        if (keypad._defused):
            keypad._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (keypad._failed):
            strike()
            # reset the keypad
            keypad._failed = False
            keypad._value = ""
    
    # check the wires
    if (wires._running):
        # update the display
        wires_display = f"Wires: {wires}"
        # the phase is defused -> stop the thread
        if (wires._defused):
            wires._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (wires._failed):
            strike()
            # reset the wires
            wires._failed = False
    
    # check the button
    if (button._running):
        # update the display
        button_display = f"Button: {button}"
        # the phase is defused -> stop the thread
        if (button._defused):
            button._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (button._failed):
            strike()
            # reset the button
            button._failed = False
    
    # check the toggles
    if (toggles._running):
        # update the display
        toggles_display = f"Toggles: {toggles}"
        # the phase is defused -> stop the thread
        if (toggles._defused):
            toggles._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (toggles._failed):
            strike()
            # reset the toggles
            toggles._failed = False

    # note the strikes
    strikes_display = f"Strikes left: {strikes_left}"
    
    # too many strikes -> explode!
    if (strikes_left == 0):
        turn_off()
        game_over = True
        game_success = False
        return False

    # the bomb has been successfully defused!
    if (active_phases == 0):
        turn_off()
        game_over = True
        game_success = True
        return False

    # continue checking phases
    return True

# handles a strike
def strike(): #CHECKED
    global strikes_left
    
    # note the strike
    strikes_left -= 1

# turns off the bomb
def turn_off(): #CHECKED
    # stop all threads
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    # turn off the 7-segment display
    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    # turn off the pushbutton's LED
    for pin in button._rgb:
        pin.value = True

# Draw the game
def draw_game():
    # Clear screen
    screen.fill((0, 0, 0))  # Black background
    
    # If game is over, show conclusion
    if game_over:
        if game_success:
            text = font.render("BOMB DEFUSED!", True, (0, 255, 0))  # Green
        else:
            text = font.render("BOOM! GAME OVER", True, (255, 0, 0))  # Red
        
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()//2))
        return
    
    # If still in boot sequence
    if not boot_complete:
        # Draw bootup text
        y_pos = 20
        for line in boot_text_display.split('\n'):
            text = font.render(line, True, (0, 255, 0))  # Green
            screen.blit(text, (20, y_pos))
            y_pos += 20
        return
    
    # Draw main game interface
    y_pos = 20
    
    # Draw status displays
    text = font.render(timer_display, True, (255, 255, 255))
    screen.blit(text, (20, y_pos))
    y_pos += 30
    
    text = font.render(strikes_display, True, (255, 255, 255))
    screen.blit(text, (20, y_pos))
    y_pos += 30
    
    text = font.render(keypad_display, True, (255, 255, 255))
    screen.blit(text, (20, y_pos))
    y_pos += 30
    
    text = font.render(wires_display, True, (255, 255, 255))
    screen.blit(text, (20, y_pos))
    y_pos += 30
    
    text = font.render(button_display, True, (255, 255, 255))
    screen.blit(text, (20, y_pos))
    y_pos += 30
    
    text = font.render(toggles_display, True, (255, 255, 255))
    screen.blit(text, (20, y_pos))
    
    # Draw game components (simplified)
    draw_game_components()

# Draw game components
def draw_game_components():
    # Draw keypad
    pygame.draw.rect(screen, (100, 100, 100), (500, 100, 250, 150), 2)
    # Draw keypad buttons
    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    for i, key in enumerate(keys):
        x = 520 + (i % 3) * 60
        y = 110 + (i // 3) * 30
        pygame.draw.rect(screen, (150, 150, 150), (x, y, 40, 20), 1)
        text = font.render(key, True, (255, 255, 255))
        screen.blit(text, (x + 15, y + 5))
    
    # Draw wires
    pygame.draw.rect(screen, (100, 100, 100), (500, 270, 250, 80), 2)
    for i in range(min(len(component_wires), 4)):
        wire_color = (255, 0, 0) if i == 0 else (0, 255, 0) if i == 1 else (0, 0, 255) if i == 2 else (255, 255, 255)
        y = 290 + i * 15
        
        # If wire state can be determined, show connected/disconnected
        if 'wires' in globals() and hasattr(wires, '_status'):
            if wires._status[i] == "disconnected":
                # Draw disconnected wire
                pygame.draw.line(screen, wire_color, (520, y), (620, y), 2)
                pygame.draw.line(screen, wire_color, (670, y), (730, y), 2)
            else:
                # Draw connected wire
                pygame.draw.line(screen, wire_color, (520, y), (730, y), 2)
        else:
            # Default to connected
            pygame.draw.line(screen, wire_color, (520, y), (730, y), 2)
    
    # Draw button
    pygame.draw.rect(screen, (100, 100, 100), (500, 370, 250, 60), 2)
    
    # If button state can be determined, show pressed/released
    if 'button' in globals() and hasattr(button, '_pressed') and button._pressed:
        # Pressed state
        pygame.draw.rect(screen, (150, 0, 0), (575, 385, 100, 30))
    else:
        # Released state
        pygame.draw.rect(screen, (255, 0, 0), (575, 385, 100, 30))
    
    # Draw toggles
    pygame.draw.rect(screen, (100, 100, 100), (500, 450, 250, 60), 2)
    for i in range(min(len(component_toggles), 4)):
        x = 520 + i * 50
        y = 470
        # Draw toggle base
        pygame.draw.rect(screen, (50, 50, 50), (x, y, 40, 20), 0)
        
        # If toggle state can be determined, show on/off position
        if 'toggles' in globals() and hasattr(toggles, '_state'):
            toggle_pos = x + 20 if toggles._state[i] else x
            pygame.draw.rect(screen, (200, 200, 200), (toggle_pos, y, 20, 20), 0)
        else:
            # Default to off position
            pygame.draw.rect(screen, (200, 200, 200), (x, y, 20, 20), 0)

# Handle mouse input
def handle_mouse_click(pos):
    if not boot_complete or game_over:
        return
    
    # Check for keypad clicks
    if 500 <= pos[0] <= 750 and 100 <= pos[1] <= 250:
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
        for i, key in enumerate(keys):
            x = 520 + (i % 3) * 60
            y = 110 + (i // 3) * 30
            if x <= pos[0] <= x + 40 and y <= pos[1] <= y + 20:
                if keypad._running and not keypad._defused:
                    keypad._value += key
                    
                    # Check if combination matches target
                    if not keypad_target.startswith(keypad._value):
                        keypad._failed = True
                        keypad._value = ""
                    elif keypad._value == keypad_target:
                        keypad._defused = True
    
    # Check for wire clicks
    if 500 <= pos[0] <= 750 and 270 <= pos[1] <= 350:
        for i in range(min(len(component_wires), 4)):
            y = 290 + i * 15
            if 520 <= pos[0] <= 730 and y - 5 <= pos[1] <= y + 5:
                if wires._running and not wires._defused:
                    if wires._status[i] == "connected":
                        wires._status[i] = "disconnected"
                    else:
                        wires._status[i] = "connected"
                    
                    # Check if configuration matches target
                    match = True
                    for j, state in enumerate(wires._target):
                        if state != wires._status[j]:
                            match = False
                            break
                    if match:
                        wires._defused = True
    
    # Check for button click
    button_rect = pygame.Rect(575, 385, 100, 30)
    if button_rect.collidepoint(pos):
        if button._running and not button._defused:
            button._pressed = True

# Handle mouse button release
def handle_mouse_release(pos):
    if not boot_complete or game_over:
        return
    
    # Check if button was released
    button_rect = pygame.Rect(575, 385, 100, 30)
    if button_rect.collidepoint(pos):
        if button._running and not button._defused and button._pressed:
            button._pressed = False
            
            # Check button target condition
            if button._target == "hold":
                # Check timer condition for hold
                current_time = timer._time_left
                if int(current_time) % 60 == button._color:
                    button._defused = True
                else:
                    button._failed = True
            else:  # tap
                button._defused = True

# Handle toggle click
def handle_toggle_click(pos):
    if not boot_complete or game_over:
        return
    
    # Check for toggle clicks
    if 500 <= pos[0] <= 750 and 450 <= pos[1] <= 510:
        for i in range(min(len(component_toggles), 4)):
            x = 520 + i * 50
            y = 470
            if x <= pos[0] <= x + 40 and y <= pos[1] <= y + 20:
                if toggles._running and not toggles._defused:
                    toggles._state[i] = not toggles._state[i]
                    
                    # Check if configuration matches target
                    match = True
                    for j, state in enumerate(toggles._target):
                        if state != toggles._state[j]:
                            match = False
                            break
                    if match:
                        toggles._defused = True

######
# MAIN
######

# Custom events
BOOTUP_EVENT = pygame.USEREVENT + 1
CHECK_PHASES_EVENT = pygame.USEREVENT + 2
next_bootup_index = 0

# initialize the bomb strikes and active phases (i.e., not yet defused)
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# "boot" the bomb (schedule the first bootup call)
pygame.time.set_timer(BOOTUP_EVENT, 1000, 1)  # Start bootup after 1 second

# Main game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            # Turn off the bomb if it's running
            if 'timer' in globals():
                turn_off()
        
        elif event.type == BOOTUP_EVENT:
            # Continue bootup animation
            bootup(next_bootup_index)
        
        elif event.type == CHECK_PHASES_EVENT:
            # Check phase status
            if not check_phases():
                # If check_phases returns False, stop the timer
                pygame.time.set_timer(CHECK_PHASES_EVENT, 0)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                handle_mouse_click(event.pos)
                handle_toggle_click(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                handle_mouse_release(event.pos)
    
    # Draw the game
    draw_game()
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()