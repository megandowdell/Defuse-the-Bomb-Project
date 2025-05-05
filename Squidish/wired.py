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
        print(f"Initial wire state: {self._value}") # REMOVE
        self._prev_value = self._value
        self._state_changed = False
        
        # Print configuration info - REMOVE
        # print(f"Wires component initialized with {len(pins)} wires")
        # print("All wires should start CONNECTED")
        # print("Physical setup: GPIO pins with pull-up resistors -> wires -> GND")
    
    def run(self):
        """Main thread that continuously monitors wire state"""
        self._running = True
        # print(f"Wire monitoring thread running: {self._running}")
        # Initial reading
        self.update_state()
        
        while (True):
            # Check if wire state has changed
            if self.update_state():
                print(f"Wire state changed to: {self._value}")
            
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
    
    def __str__(self):
        """Display wire state as binary and decimal"""
        return f"{self._value}/{int(self._value, 2)}"

# Simulation mode for testing without hardware
class SimulatedPin:
    def __init__(self, initial_value=False):
        # False = connected (1), True = disconnected (0) with pull-ups
        self.value = initial_value
        
    def toggle(self):
        self.value = not self.value
        print(f"Pin toggled to: {self.value}")

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
BROWN_WIRE = (139, 69, 19)
RED_WIRE = (255, 0, 0)
ORANGE_WIRE = (255, 165, 0)
YELLOW_WIRE = (255, 255, 0)
GREEN_WIRE = (0, 190, 104)

# Font
font = pygame.font.Font('font1.otf', 30)
wire_font = pygame.font.Font('font1.otf', 24)

# Main game function
def main():
    background = pygame.image.load("how_to_play.jpg")
    background = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

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
    RPi = False
    try:
        import board
        from digitalio import DigitalInOut, Direction, Pull
        RPi = True
        print("Running on Raspberry Pi with hardware")
        
        # Set up physical pins
        wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
        for pin in wire_pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.DOWN
            
    except (ImportError, NotImplementedError):
        RPi = False
        print("Running in simulation mode (no hardware)")
        wire_pins = [SimulatedPin() for _ in range(5)]
    
    # Create and start wires component
    wires = Wires(wire_pins)
    wires.start()
    
    # Define colors and commands
    colors = ["brown", "red", "orange", "yellow", "blue"]
    print(f"Wire colors: {colors}")
    
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
    print(f"First command: {commands[0]}")
    
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
    
    # Print all commands
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
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    # Initialize the timer for 20 seconds
    command_start_time = time.time()
    timer_duration = 20  # 20 seconds timer

    while running:
        # Fill screen with black background
        screen.fill(BLACK)
        
        # Calculate remaining time for current command
        elapsed_time = time.time() - command_start_time
        remaining_time = max(0, timer_duration - elapsed_time)
        
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
                    # Check if command starts with "Simon says"
                    is_simon = current_command.startswith("Simon says")
                    is_disconnect = "disconnect" in current_command
                    color = next(c for c in colors if c in current_command)
                    color_index = colors.index(color)

                    # Check if wire state matches command
                    is_disconnected = wires._value[color_index] == "0"
                    
                    # If not a Simon says command, it should return false
                    if not is_simon:
                        result = False
                        status_message = "Command does not start with 'Simon says'!"
                    else:
                        # Simon commands must be followed
                        if is_disconnect:
                            result = is_disconnected
                        else:  # reconnect
                            result = not is_disconnected

                    if result:
                        # Move to next command
                        current_command_index += 1
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
                        game_over = True
                        won = False
                
                elif event.key == pygame.K_r and game_over:
                    # Restart game
                    print("Restarting game...")
                    
                    # Reset wire states
                    wire_states = {color: True for color in colors}
                    current_command_index = 0
                    current_command = commands[current_command_index]
                    game_over = False
                    won = False
                    status_message = ""
                    
                    # Reset timer
                    command_start_time = time.time()
                    
                    # Reset physical wires to connected if in simulation
                    if not RPi:
                        for pin in wire_pins:
                            if pin.value:  # If disconnected
                                pin.toggle()  # Connect it
                        wires.update_state()
                
                # Simulation mode: toggle wires with number keys
                elif not RPi and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    index = event.key - pygame.K_1
                    if index < len(wire_pins):
                        wire_pins[index].toggle()
                        wires.update_state()
                        print(f"Toggled wire {index+1} ({colors[index]})")
                        print(f"New wire state: {wires._value}")
        
        # Draw text elements
        # Title
        title = font.render("Simon Says Wire Game", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Wire states
        wire_state_text = font.render(f"Wire states: {wires._value}", True, WHITE)
        screen.blit(wire_state_text, (30, 80))
        
        # Individual wire labels and states
        for i, color in enumerate(colors):
            wire_text = font.render(f"{color}: {'Connected' if wires._value[i] == '1' else 'Disconnected'}", True, WHITE)
            screen.blit(wire_text, (30, 120 + i * 30))
        
        # Current command
        cmd_text = font.render(f"Command: {current_command}", True, WHITE)
        screen.blit(cmd_text, (30, 280))
        
        # Progress
        progress = font.render(f"Progress: {current_command_index + 1}/{len(commands)}", True, WHITE)
        screen.blit(progress, (30, 320))
        
        # Timer display
        timer_color = WHITE if remaining_time > 5 else RED  # Red when less than 5 seconds left
        timer_text = font.render(f"Time remaining: {int(remaining_time)} seconds", True, timer_color)
        screen.blit(timer_text, (30, 360))
        
        # Status message
        if status_message:
            status_text = font.render(f"Status: {status_message}", True, WHITE)
            screen.blit(status_text, (30, 400))
        
        # Game over message
        if game_over:
            result_text = font.render(f"Game Over - {'You Win!' if won else 'You Lose!'}", True, WHITE)
            screen.blit(result_text, (30, 440))
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (30, 480))
        
        # Instructions
        if RPi:
            instructions = font.render("Connect/disconnect physical wires. Press SPACE to check command.", True, WHITE)
        else:
            instructions = font.render("Press 1-5 to toggle wires. Press SPACE to check command.", True, WHITE)
        screen.blit(instructions, (30, SCREEN_HEIGHT - 60))
        
        # Debug info
        debug = font.render("See console for detailed debug info", True, WHITE)
        screen.blit(debug, (30, SCREEN_HEIGHT - 30))
        
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
