import pygame
import time
import sys
import random 
from threading import Thread
from time import sleep
import board
from digitalio import DigitalInOut, Direction, Pull

# Base class for bomb components
class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name = name, daemon = True)
        self._running = False
        self._value = None

    def reset(self):
        self._value = None

# Improved Wires class that handles common wire detection issues
class Wires(PhaseThread):
    def __init__(self, pins, name="Wires"):
        super().__init__(name)
        # the jumper wire pins
        self._pins = pins
            
        # All wires start connected - initialize with all 1's
        self._value = "1" * len(pins)
        self._prev_value = self._value
        self._state_changed = False
        
        # Print configuration info - REMOVE
        # print(f"Wires component initialized with {len(pins)} wires")
        # print("All wires should start CONNECTED")
        # print("Physical setup: GPIO pins with pull-up resistors -> wires -> GND")
    
    def run(self):
        """Main thread that continuously monitors wire state"""
        self._running = True
        
        # Initial reading
        self.update_state()
        
        while (True):
            # Check if wire state has changed
            if self.update_state():
                pass
            # Poll at a reasonable rate (100ms)
            sleep(0.1)
        
        self._running = False
    
    def update_state(self):
        """Updates wire state and returns True if state changed"""
        # Read raw pin values (TRUE = disconnected, FALSE = connected with pull-ups)
        raw_values = [pin.value for pin in self._pins]
        
        # Convert to wire state (1 = connected, 0 = disconnected)
        # With pull-up resistors: False = connected (1), True = disconnected (0)
        new_state = "".join(["0" if not val else "1" for val in raw_values])
        
        # Check if state changed 
        changed = new_state != self._value
        if changed:
            # Update state and set change flag
            self._prev_value = self._value
            self._value = new_state
            self._state_changed = True
            print(f"Wire state changed from {self._prev_value} to {self._value}")
        else:
            self._state_changed = False
            
        return changed
    
    def has_changed(self):
        """Returns True if wire state has changed since last check"""
        if self._state_changed:
            self._state_changed = False
            return True
        return False
    
    

# Simulation mode for testing without hardware


# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1024
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simon Says")

# Text Colours
WHITE = (255, 255, 255)
RED = (255, 0, 0)  
GREEN = (0, 255, 0)

# Wire Text Colours
BROWN_WIRE = (255, 255, 0) # TRUE COLOUR = YELLOW
RED_WIRE = (0, 190, 104) # TRUE COLOUR =  GREEN
ORANGE_WIRE = (139, 69, 19) # TRUE COLOUR =  BROWN
YELLOW_WIRE = (255, 0, 0) # TRUE COLOUR =  RED
GREEN_WIRE = (255, 165, 0) # TRUE COLOUR =  ORANGE

# Font
font = pygame.font.Font('font1.otf', 30)
wire_font = pygame.font.Font('font1.otf', 24)

# Main game function
def main():
    bg_image = pygame.image.load("simonsays.png")
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) 

    # Dictionary mapping commands to appropriate sound files
    command_sound_files = {
        "Simon says disconnect the brown wire": "ssdisbw.mp3",
        "Simon says reconnect the brown wire": "ssrebw.mp3",
        "Disconnect the brown wire": "disbw.mp3",
        "Reconnect the brown wire": "rebw.mp3",
        "Simon says disconnect the red wire": "ssdisrw.mp3",
        "Simon says reconnect the red wire": "ssrerw.mp3",
        "Disconnect the red wire": "disrw.mp3",
        "Reconnect the red wire": "rerw.mp3",
        "Simon says disconnect the orange wire": "ssdisow.mp3",
        "Simon says reconnect the orange wire": "ssreow.mp3",
        "Disconnect the orange wire": "disow.mp3",
        "Reconnect the orange wire": "reow.mp3",
        "Simon says disconnect the yellow wire": "ssdisyw.mp3",
        "Simon says reconnect the yellow wire": "ssreyw.mp3",
        "Disconnect the yellow wire": "disyw.mp3",
        "Reconnect the yellow wire": "reyw.mp3",
        "Simon says disconnect the green wire": "ssdisgw.mp3",
        "Simon says reconnect the green wire": "ssregw.mp3",
        "Disconnect the green wire": "disgw.mp3",
        "Reconnect the green wire": "regw.mp3"
    }

    # For each command in dictionary, play the assigned sound to match
    command_sounds = {}
    for command, command_sound in command_sound_files:
        command_sounds[command] = pygame.mixer.music.Sound(command_sound)

    # Setup for RPI environment
    # RPI = True
    # try:
    #     import board
    #     from digitalio import DigitalInOut, Direction, Pull
    #     RPi = True
    #     print("Running on Raspberry Pi with hardware")
        
        # Set up physical pins
        wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
        for pin in wire_pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.DOWN
    
    # Create and start wires component
    wires = Wires(wire_pins)
    wires.start()
    
    # Define colors and commands
    colors = ["brown", "red", "orange", "yellow", "blue"]
    GUI_colors = [BROWN_WIRE, RED_WIRE, ORANGE_WIRE, YELLOW_WIRE, GREEN_WIRE] 
    
    non_simon_discommands = [f"Disconnect the {color} wire" for color in colors]
    non_simon_recommands = [f"Reconnect the {color} wire" for color in colors]
    simon_discommands = [f"Simon says disconnect the {color} wire" for color in colors]
    simon_recommands = [f"Simon says reconnect the {color} wire" for color in colors]
    
    wire_states = {color: True for color in colors}
    simon_disconnected = set()
    simon_reconnected = set()
    commands = []
    
    # First Simon command
    first_color = random.choice(colors)
    wire_states[first_color] = False
    simon_disconnected.add(first_color)
    commands.append(simon_discommands[colors.index(first_color)])
    
    # Generate 9 more commands
    while len(commands) < 10:
        valid_actions = []
        
        for color in colors:
            if wire_states[color] and color not in simon_disconnected:
                valid_actions.append(("simon_disconnect", color))
        for color in simon_disconnected:
            if not wire_states[color] and color not in simon_reconnected:
                valid_actions.append(("simon_reconnect", color))
        
        if valid_actions and random.random() < 0.6:
            action, color = random.choice(valid_actions)
            if action == "simon_disconnect":
                command = simon_discommands[colors.index(color)]
                wire_states[color] = False
                simon_disconnected.add(color)
            elif action == "simon_reconnect":
                command = simon_recommands[colors.index(color)]
                wire_states[color] = True
                simon_reconnected.add(color)
            commands.append(command)
        else:
            cmd = None
            if random.choice(["disconnect", "reconnect"]) == "disconnect":
                valid = [c for c in colors if wire_states[c]]
                if valid:
                    color = random.choice(valid)
                    cmd = non_simon_discommands[colors.index(color)]
            else:
                valid = [c for c in simon_disconnected if not wire_states[c] and c not in simon_reconnected]
                if valid:
                    color = random.choice(valid)
                    cmd = non_simon_recommands[colors.index(color)]
            if cmd:
                commands.append(cmd)
    
    # Print all commands - REMOVE
    print("Generated commands:")
    for i, cmd in enumerate(commands):
        print(f"{i+1}. {cmd}")
    
    # Reset wire states for game start
    wire_states = {color: True for color in colors}
    current_command_index = 0
    current_command = commands[current_command_index]
    game_over = False
    won = False
    status_message = ""
    command_played = False # Check if command audio played or not

   # Wire tracking variables
    initial_wire_state = wires._value # Stores current state of wires before player action
    updated_wire_state = wires._value # Stores state of wires after player action
    action_result = None # Tracks player's actions
    # action_time = 0 # Tracks timing of player's actions
    
    # Player tracking variables
    player_confirmation = False # Check if player has confirmed their choice via space bar
    wire_changed = False  # Check if initial state of wire has been changed
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    # Initialize the timer for 30 seconds
    command_start_time = time.time()
    timer_duration = 30  # 30 seconds timer
    delay_time = 2 # Delays before player's action is checked
    result_time = 2 # Time result is showed
    
    # If command has a sound, play it
    if current_command in command_sounds:
        pygame.mixer.music.stop()
        command_sounds[current_command].play()
        command_played = True

    while running:
        # Fill screen with black background
        screen.fill(BLACK)
        
        # Calculate remaining time for current command
        elapsed_time = time.time() - command_start_time
        remaining_time = max(0, timer_duration - elapsed_time)

        # If the command has not been given, the game is still going and player has not yet confirmed, play another sound from list
        if not command_played and not gamer_over and not player_confirmation:
            if current_command in command_sounds:
                pygame.mixer.stop()
                command_sounds[current_command]
            command_played = True
            
        # Timer check: if the player hasn't made a move in 20 seconds, game ends
        if remaining_time <= 0 and not game_over:
            game_over = True
            won = False
            status_message = "Time's up! You took too long."
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    current_wire_state = wires._value # Store wire state for it to be checked
                    # Check if command starts with "Simon says"
                    is_simon = current_command.startswith("Simon says")
                    is_disconnect = "disconnect" in current_command
                    color = next(c for c in colors if c in current_command)
                    color_index = colors.index(color)

                    # Check if wire was changed from its previous state - TO CHANGE (298 - 301)
                    is_disconnected = wires._value[color_index] == "0"  # Change : instead get current_wire state instead of directly from wire object
                    # Implement check if wire was even connected to begin with
                   # wire_change = implement to check if is disconnect and was ever connected are not equal
                    
                    # If not a Simon says command, it should return false - TO CHANGE (303 - 312)
                    if not is_simon:
                        result = False
                        status_message = "Command does not start with 'Simon says'!"
                    else:
                        # Simon commands must be followed
                        if is_disconnect:
                            result = is_disconnected # == is_disconnect
                        else:  # reconnect
                            result = not is_disconnected

                    if result:
                        status_message = "SUCCESS"
                        # Move to next command
                        current_command_index += 1 # TO CHANGE (317 - 321)
                        if current_command_index < len(commands):
                            current_command = commands[current_command_index]
                            # Reset timer for the new command
                            command_start_time = time.time()
                        else:
                            current_command = "All commands completed!"
                            game_over = True
                            won = True
                    else:
                        # Player fails the game
                        status_message = "FAILURE"
                        game_over = True
                        won = False

            #Check for wire state changes (always update last_wire_state)
        if wires._value != initial_wire_state:
            initial_wire_state = wires._value
            #Set waiting for confirmation only if the game is still active
            if not game_over and not player_confirmation:
                player_confirmation = True
                status_message = "Press SPACE to check your action"
                
                # elif event.key == pygame.K_r and game_over:
                    # Restart game
                    # #print("Restarting game...")
                    
                    # # Reset wire states
                    # wire_states = {color: True for color in colors}
                    # current_command_index = 0
                    # current_command = commands[current_command_index]
                    # game_over = False
                    # won = False
                    # status_message = ""
                    
                    # # Reset timer
                    # command_start_time = time.time()
                    
                    # # Reset physical wires to connected if in simulation
                    # if not RPi:
                    #     for pin in wire_pins:
                    #         if pin.value:  # If disconnected
                    #             pin.toggle()  # Connect it
                    #     wires.update_state()
                
                # # Simulation mode: toggle wires with number keys
                # elif not RPi and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                #     index = event.key - pygame.K_1
                #     if index < len(wire_pins):
                #         wire_pins[index].toggle()
                #         wires.update_state()
                #         print(f"Toggled wire {index+1} ({colors[index]})")
                #         print(f"New wire state: {wires._value}")
        
        # Draw text elements
        # Title
        title = font.render("Simon Says", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        #Draw background image
        screen.blit(bg_image, (0, 0))  
        #Draw semi-transparent overlay
        screen.blit(overlay, (0, 0))  
        
        #Display wire names and statuses
        wire_display_x = 50
        wire_display_y = 150
        wire_spacing = 40

        # Individual wire labels and states
        for i, color in enumerate(colors):
            y_pos = wire_display_y + i*wire_spacing
            wire_text = font.render(f"{color}: {'Connected' if wires._value[i] == '1' else 'Disconnected'}", True, WHITE)
            screen.blit(wire_text, (wire_display_x, y_pos))
        
        # Progress
        progress = font.render(f"Progress: {current_command_index + 1}/{len(commands)}", True, WHITE)
        screen.blit(progress, (30, 30))
        
        # Timer display
        timer_color = WHITE if remaining_time > 5 else RED  # Red when less than 5 seconds left
        timer_text = font.render(f"Time: {int(remaining_time)} s", True, timer_color)
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 30, 30))
        
        # Status message
        if status_message:
            status_text = font.render(f"{status_message}", True, WHITE)
            screen.blit(status_text, (30, 400))
        
        # Game over message
        if game_over:
            result_text = font.render(f"Game Over - {'You Win!' if won else 'You Lose!'}", True, WHITE)
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 400))
        
        # Instructions
        instructions = font.render("Press SPACE to check command.", True, WHITE)

        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()
