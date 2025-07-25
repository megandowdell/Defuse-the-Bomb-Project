import pygame
import time
import sys
import random 
from threading import Thread
from time import sleep
#import board
#from digitalio import DigitalInOut, Direction, Pull

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
        print (self._value)
        self._prev_value = self._value
        self._state_changed = False
        
        # Print configuration info
        print(f"Wires component initialized with {len(pins)} wires")
        print("All wires should start CONNECTED")
        print("Physical setup: GPIO pins with pull-up resistors -> wires -> GND")
    
    def run(self):
        """Main thread that continuously monitors wire state"""
        self._running = True
        print(self._running)
        # Initial reading
        self.update_state()
        print(self.update_state())
        
        while (True):
            # Check if wire state has changed
            if self.update_state():
                print(self.update_state())
                # State changed - we can take actions here if needed
                pass
            
            # Poll at a reasonable rate (100ms)
            sleep(0.1)
        
        self._running = False
    
    def update_state(self):
        """Updates wire state and returns True if state changed"""
        # Read raw pin values (TRUE = disconnected, FALSE = connected with pull-ups)
        raw_values = [pin.value for pin in self._pins]
        print (raw_values)
        # Convert to wire state (1 = connected, 0 = disconnected)
        # With pull-up resistors: False = connected (1), True = disconnected (0)
        new_state = "".join(["1" if val else "0" for val in raw_values])

        pin_values = "".join([str(int(pin.value)) for pin in self._pins])
        
        print("Pin values - ", pin_values)
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
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simon Says")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont('Arial', 24)

# Simon Says Game Logic
class SimonSaysGame:
    def __init__(self, wires):
        self.wires = wires
        self.colors = ["brown", "red", "orange", "yellow", "blue"]
        self.commands = []
        self.current_command_index = 0
        self.current_command = ""
        self.game_over = False
        self.won = False
        self.status_message = ""
        
        # Generate commands
        self.generate_commands()
        
    def generate_commands(self):
        """Generate Simon Says commands"""
        # Command types
        non_simon_discommands = [f"Disconnect the {color} wire" for color in self.colors]
        non_simon_recommands = [f"Reconnect the {color} wire" for color in self.colors]
        simon_discommands = [f"Simon says disconnect the {color} wire" for color in self.colors]
        simon_recommands = [f"Simon says reconnect the {color} wire" for color in self.colors]

        # Track wire states
        wire_states = {color: True for color in self.colors}
        simon_disconnected = set()
        simon_reconnected = set()
        self.commands = []

        # First Simon command
        first_color = random.choice(self.colors)
        wire_states[first_color] = False
        simon_disconnected.add(first_color)
        self.commands.append(simon_discommands[self.colors.index(first_color)])
        
        # Generate 9 more commands
        while len(self.commands) < 10:
            valid_actions = []

            # Find valid simon commands
            for color in self.colors:
                if wire_states[color] and color not in simon_disconnected:
                    valid_actions.append(("simon_disconnect", color))
            for color in simon_disconnected:
                if not wire_states[color] and color not in simon_reconnected:
                    valid_actions.append(("simon_reconnect", color))

            # 60% chance of simon command, 40% normal command
            if valid_actions and random.random() < 0.6:
                action, color = random.choice(valid_actions)
                if action == "simon_disconnect":
                    command = simon_discommands[self.colors.index(color)]
                    wire_states[color] = False
                    simon_disconnected.add(color)
                elif action == "simon_reconnect":
                    command = simon_recommands[self.colors.index(color)]
                    wire_states[color] = True
                    simon_reconnected.add(color)
                self.commands.append(command)
            else:
                cmd = None
                if random.choice(["disconnect", "reconnect"]) == "disconnect":
                    valid = [c for c in self.colors if wire_states[c]]
                    if valid:
                        color = random.choice(valid)
                        cmd = non_simon_discommands[self.colors.index(color)]
                else:
                    valid = [c for c in simon_disconnected if not wire_states[c] and c not in simon_reconnected]
                    if valid:
                        color = random.choice(valid)
                        cmd = non_simon_recommands[self.colors.index(color)]
                if cmd:
                    self.commands.append(cmd)
                    
        # Print all commands for debugging
        print("Generated commands:")
        for i, cmd in enumerate(self.commands):
            print(f"{i+1}. {cmd}")
            
        # Set initial command
        if self.commands:
            self.current_command = self.commands[0]
            print(f"First command: {self.current_command}")
    
    def check_command(self):
        """Check if current command was fulfilled correctly"""
        if self.game_over or not self.current_command:
            return False
            
        cmd = self.current_command
        is_simon = cmd.startswith("Simon says")
        is_disconnect = "disconnect" in cmd
        
        # Extract color from command
        color = next(c for c in self.colors if c in cmd)
        color_index = self.colors.index(color)
        
        # Check wire state
        is_disconnected = self.wires._value[color_index] == "0"
        
        print(f"Checking command: {cmd}")
        print(f"Wire state: {'disconnected' if is_disconnected else 'connected'}")
        
        if is_simon:
            # For Simon commands, the action must be performed
            if (is_disconnect and is_disconnected) or (not is_disconnect and not is_disconnected):
                print("CORRECT - Simon command was followed")
                self.status_message = "CORRECT!"
                if not self.next_command():
                    self.game_over = True
                    self.won = True
                return True
            else:
                print("INCORRECT - Simon command was not followed")
                self.status_message = "INCORRECT!"
                self.game_over = True
                return False
        else:
            # For non-Simon commands, the action must NOT be performed
            if (is_disconnect and not is_disconnected) or (not is_disconnect and is_disconnected):
                print("CORRECT - Non-Simon command was ignored")
                self.status_message = "CORRECT!"
                if not self.next_command():
                    self.game_over = True
                    self.won = True
                return True
            else:
                print("INCORRECT - Non-Simon command was followed")
                self.status_message = "INCORRECT!"
                self.game_over = True
                return False
                
    def next_command(self):
        """Move to next command"""
        self.current_command_index += 1
        if self.current_command_index < len(self.commands):
            self.current_command = self.commands[self.current_command_index]
            print(f"Next command: {self.current_command}")
            return True
        else:
            print("All commands completed!")
            self.current_command = "All commands completed!"
            return False
            
    def restart(self):
        """Restart the game"""
        print("Restarting game...")
        self.commands = []
        self.current_command_index = 0
        self.game_over = False
        self.won = False
        self.status_message = ""
        self.generate_commands()

# Main game function
def main():
    # Determine if running on Raspberry Pi with real hardware
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
    
    # Create game logic
    game = SimonSaysGame(wires)
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Fill screen with black background
        screen.fill(BLACK)
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.game_over:
                    game.check_command()
                elif event.key == pygame.K_r and game.game_over:
                    game.restart()
                # Simulation mode: toggle wires with number keys
                elif not RPi and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    index = event.key - pygame.K_1
                    if index < len(wires._pins):
                        wires._pins[index].toggle()
                        wires.update_state()
                        print(f"Toggled wire {index+1}")
                        print(f"New wire state: {wires._value}")
        
        # Draw text elements
        # Title
        title = font.render("Simon Says Wire Game", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Wire states
        wire_state_text = font.render(f"Wire states: {wires._value}", True, WHITE)
        screen.blit(wire_state_text, (30, 80))
        
        # Individual wire labels and states
        for i, color in enumerate(game.colors):
            wire_text = font.render(f"{color}: {'Connected' if wires._value[i] == '1' else 'Disconnected'}", True, WHITE)
            screen.blit(wire_text, (30, 120 + i * 30))
        
        # Current command
        cmd_text = font.render(f"Command: {game.current_command}", True, WHITE)
        screen.blit(cmd_text, (30, 280))
        
        # Progress
        progress = font.render(f"Progress: {game.current_command_index + 1}/{len(game.commands)}", True, WHITE)
        screen.blit(progress, (30, 320))
        
        # Status message
        if game.status_message:
            status_text = font.render(f"Status: {game.status_message}", True, WHITE)
            screen.blit(status_text, (30, 360))
        
        # Game over message
        if game.game_over:
            result_text = font.render(f"Game Over - {'You Win!' if game.won else 'You Lose!'}", True, WHITE)
            screen.blit(result_text, (30, 400))
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (30, 440))
        
        # Instructions
        if RPi:
            instructions = font.render("Connect/disconnect physical wires. Press SPACE to check command.", True, WHITE)
        else:
            instructions = font.render("Press 1-5 to toggle wires. Press SPACE to check command.", True, WHITE)
        screen.blit(instructions, (30, SCREEN_HEIGHT - 60))
        
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