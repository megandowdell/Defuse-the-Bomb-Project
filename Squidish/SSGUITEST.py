import pygame
import time
import sys
import random 
from threading import Thread
from time import sleep
# import board
# from digitalio import DigitalInOut, Direction, Pull

# Base class for bomb components
class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
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
        
    def run(self):
        """Main thread that continuously monitors wire state"""
        self._running = True
        # Initial reading
        self.update_state()
        
        while (True):
            # Check if wire state has changed
            if self.update_state():
                pass  # Wire state changed
            
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

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simon Says Wire Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Define wire colors
BROWN = (139, 69, 19)
RED_WIRE = (255, 0, 0)  # Named RED_WIRE to avoid conflict with RED
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN_WIRE = (0, 190, 104)  # Renamed to avoid conflict

# Font
font = pygame.font.SysFont('Arial', 30)
small_font = pygame.font.SysFont('Arial', 24)
wire_font = pygame.font.SysFont('Arial', 22)

# Main game function
def main():
    # Initialize pygame mixer if not already done
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    # Load background image
    bg_image = pygame.image.load("how_to_play.jpg")  # Replace with your image path
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Create a semi-transparent overlay for better text readability
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) 

    command_sound_files = {
        "Simon says disconnect the brown wire": "ssdisbrw.mp3",
#         "Simon says reconnect the brown wire": "ssrebrw.mp3",
#         "Disconnect the brown wire": "disbrw.mp3",
        "Reconnect the brown wire": "rebrw.mp3",
#         "Simon says disconnect the red wire": "ssdisrw.mp3",
#         "Simon says reconnect the red wire": "ssrerw.mp3",
#         "Disconnect the red wire": "disrw.mp3",
#         "Reconnect the red wire": "rerw.mp3",
        "Simon says disconnect the orange wire": "ssdisow.mp3",
#         "Simon says reconnect the orange wire": "ssreow.mp3",
#         "Disconnect the orange wire": "disow.mp3",
        "Reconnect the orange wire": "reow.mp3",
#         "Simon says disconnect the yellow wire": "ssdisyw.mp3",
#         "Simon says reconnect the yellow wire": "ssreyw.mp3",
#         "Disconnect the yellow wire": "disyw.mp3",
#         "Reconnect the yellow wire": "reyw.mp3",
#         "Simon says disconnect the green wire": "ssdisgw.mp3",
#         "Simon says reconnect the green wire": "ssregw.mp3",
#         "Disconnect the green wire": "disgw.mp3",
#         "Reconnect the green wire": "regw.mp3"
    }
    
    # Load audio files - only load the ones that exist
    command_sounds = {}
    for command, filename in command_sound_files.items():
        try:
            command_sounds[command] = pygame.mixer.Sound(filename)
        except:
            pass  # Skip if file doesn't exist
        

    # Determine if running on Raspberry Pi with real hardware
    RPi = False
    try:
        import board
        from digitalio import DigitalInOut, Direction, Pull
        RPi = True
        
        # Set up physical pins
        wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
        for pin in wire_pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.DOWN
            
    except (ImportError, NotImplementedError):
        RPi = False
        wire_pins = [SimulatedPin() for _ in range(5)]
    
    # Create and start wires component
    wires = Wires(wire_pins)
    wires.start()
    
    # Define colors and commands
    colors = ["brown", "red", "orange", "yellow", "green"]
    color_values = [BROWN, RED_WIRE, ORANGE, YELLOW, GREEN_WIRE]  # Actual RGB values for display
    
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
    
    # Reset wire states for game start
    wire_states = {color: True for color in colors}
    current_command_index = 0
    current_command = commands[current_command_index]
    game_over = False
    won = False
    status_message = ""
    
    # Audio playback variables
    command_played = False
    
    # For automatic checking
    last_wire_state = wires._value
    action_result = None  # None = not checked, True = success, False = failure
    action_time = 0
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    # Initialize the timer for 20 seconds
    command_start_time = time.time()
    timer_duration = 20  # 20 seconds timer
    check_delay = 2.0  # Delay before checking the action
    show_result_time = 2.0  # How long to show success/failure message

    # Play the first command
    if current_command in command_sounds:
        pygame.mixer.stop()  # Stop any currently playing sounds
        command_sounds[current_command].play()
        command_played = True

    while running:
        current_time = time.time()
        
        # Calculate remaining time for current command
        elapsed_time = current_time - command_start_time
        remaining_time = max(0, timer_duration - elapsed_time)
        
        # Play command audio if not played yet
        if not command_played and not game_over:
            if current_command in command_sounds:
                pygame.mixer.stop()  # Stop any currently playing sounds
                command_sounds[current_command].play()
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
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    
                    # Reset wire states
                    wire_states = {color: True for color in colors}
                    current_command_index = 0
                    current_command = commands[current_command_index]
                    game_over = False
                    won = False
                    status_message = ""
                    action_result = None
                    command_played = False
                    
                    # Reset timer
                    command_start_time = time.time()
                    
                    # Reset physical wires to connected if in simulation
                    if not RPi:
                        for pin in wire_pins:
                            if pin.value:  # If disconnected
                                pin.toggle()  # Connect it
                        wires.update_state()
                    
                    # Play the first command again
                    if current_command in command_sounds:
                        pygame.mixer.stop()
                        command_sounds[current_command].play()
                        command_played = True
                
                # Simulation mode: toggle wires with number keys
                elif not RPi and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    index = event.key - pygame.K_1
                    if index < len(wire_pins):
                        wire_pins[index].toggle()
                        wires.update_state()
        
        # Automatic checking for wire changes
        if not game_over and wires._value != last_wire_state and action_result is None:
            last_wire_state = wires._value
            action_time = current_time
            
            # Check if command starts with "Simon says"
            is_simon = current_command.startswith("Simon says")
            is_disconnect = "disconnect" in current_command
            color = next(c for c in colors if c in current_command)
            color_index = colors.index(color)

            # Check if wire state matches command
            is_disconnected = wires._value[color_index] == "0"
            
            # If not a Simon says command, it should return false
            if not is_simon:
                action_result = False
                status_message = "FAILURE! Command did not start with 'Simon says'!"
            else:
                # Simon commands must be followed
                if is_disconnect:
                    action_result = is_disconnected
                else:  # reconnect
                    action_result = not is_disconnected
            
            # Success or failure action
            if action_result:
                status_message = "SUCCESS!"
            else:
                status_message = "FAILURE!"
                game_over = True
                won = False
        
        # Move to next command after a delay
        if action_result is True and current_time - action_time >= check_delay:
            current_command_index += 1
            if current_command_index < len(commands):
                current_command = commands[current_command_index]
                # Reset timer for the new command
                command_start_time = time.time()
                action_result = None
                command_played = False
                
                # Play the next command
                if current_command in command_sounds:
                    pygame.mixer.stop()
                    command_sounds[current_command].play()
                    command_played = True
            else:
                current_command = "All commands completed!"
                game_over = True
                won = True
                action_result = None
        
        # Draw elements
        screen.blit(bg_image, (0, 0))  # Draw background image
        screen.blit(overlay, (0, 0))  # Draw semi-transparent overlay
        
        # Display wire names and statuses
        wire_display_x = 50
        wire_display_y = 150
        wire_spacing = 40
        
        for i, color in enumerate(colors):
            y_pos = wire_display_y + i * wire_spacing
            is_connected = wires._value[i] == "1"
            status_text = "CONNECTED" if is_connected else "DISCONNECTED"
            
            # Display wire name and status
            wire_text = wire_font.render(f"{color.upper()} WIRE: {status_text}", True, color_values[i])
            screen.blit(wire_text, (wire_display_x, y_pos))
        
        # Current command - make it larger and centered
        cmd_text = font.render(f"{current_command}", True, WHITE)
        screen.blit(cmd_text, (SCREEN_WIDTH // 2 - cmd_text.get_width() // 2, 50))
        
        # Progress
        progress = small_font.render(f"Progress: {current_command_index + 1}/{len(commands)}", True, WHITE)
        screen.blit(progress, (30, 30))
        
        # Timer display
        timer_color = WHITE if remaining_time > 5 else RED  # Red when less than 5 seconds left
        timer_text = small_font.render(f"Time: {int(remaining_time)}s", True, timer_color)
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 30, 30))
        
        # Status message (success/failure) - always show if it exists
        if action_result is not None:
            status_color = GREEN if action_result else RED
            status_text = font.render(status_message, True, status_color)
            screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, 350))
        
        # Game over message
        if game_over:
            result_text = font.render(f"Game Over - {'You Win!' if won else 'You Lose!'}", True, WHITE)
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 400))
            restart_text = small_font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 450))
        
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