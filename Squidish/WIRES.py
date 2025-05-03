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
        print(f"Initial wire state: {self._value}")
        self._prev_value = self._value
        self._state_changed = False
        
        # Print configuration info
        print(f"Wires component initialized with {len(pins)} wires")
        print("All wires should start CONNECTED")
        print("Physical setup: GPIO pins with pull-up resistors -> wires -> GND")
    
    def run(self):
        """Main thread that continuously monitors wire state"""
        self._running = True
        print(f"Wire monitoring thread running: {self._running}")
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
        new_state = "".join(["1" if not val else "0" for val in raw_values])
        
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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simon Says Wire Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont('Arial', 24)

# Main game function
def main():
    # Determine if running on Raspberry Pi with real hardware
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
   # Main game loop
clock = pygame.time.Clock()
running = True
start_time = time.time()  # Initialize the timer

while running:
    # Fill screen with black background
    screen.fill(BLACK)
    
    # Timer check: if the player hasn't made a move in 20 seconds, game ends
    if time.time() - start_time > 20:
        game_over = True
        won = False
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # Check current command
                is_simon = current_command.startswith("Simon says")
                is_disconnect = "disconnect" in current_command
                color = next(c for c in colors if c in current_command)
                color_index = colors.index(color)

                # Check if wire state matches command
                is_disconnected = wires._value[color_index] == "0"

                if is_simon:
                    # Simon commands must be followed
                    if is_disconnect:
                        result = is_disconnected
                    else:  # reconnect
                        result = not is_disconnected
                else:
                    # Non-Simon commands must be ignored
                    if is_disconnect:
                        result = not is_disconnected
                    else:  # reconnect
                        result = is_disconnected

                if result:
                    # Move to next command
                    current_command_index += 1
                    if current_command_index < len(commands):
                        current_command = commands[current_command_index]
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
                wire_states = {color: True for color in colors}
                current_command_index = 0
                current_command = commands[current_command_index]
                game_over = False
                won = False
                status_message = ""
    
    # Render game elements, update screen...
                pygame.display.flip()
            
                clock.tick(60)  # Frame rate


                
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
        
        # Status message
        if status_message:
            status_text = font.render(f"Status: {status_message}", True, WHITE)
            screen.blit(status_text, (30, 360))
        
        # Game over message
        if game_over:
            result_text = font.render(f"Game Over - {'You Win!' if won else 'You Lose!'}", True, WHITE)
            screen.blit(result_text, (30, 400))
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (30, 440))
        
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
