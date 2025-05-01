#Simon Says Game  ----  Defuse the Bomb
#Khalil Smith 

#Importing the all the functions of each library 
import pygame
import time
import sys
import random
from threading import Thread
from time import sleep
# import board
# from digitalio import DigitalInOut, Direction, Pull


colors = ["brown", "red", "orange", "yellow", "blue"]
non_simon_discommands = []
non_simon_recommands = []
simon_discommands = []
simon_recommands = []

for color in colors:
    non_simon_discommands.append(f"Disconnect the {color} wire")
    non_simon_recommands.append(f"Reconnect the {color} wire")
    simon_discommands.append(f"Simon says disconnect the {color} wire")
    simon_recommands.append(f"Simon says reconnect the {color} wire")

wire_states = {color: True for color in colors}
simon_disconnected = set()
simon_reconnected = set()

def read_wire_state(color):
    return "connected" if wire_states[color] else "diconnected"
    
#Setting up the pygame
#This will be changed
pygame.init()
WIDTH, HEIGHT = 700, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simon Says: Raspberry Pi Edition")

#Colors that are associated with squid games 
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
RED = (255, 0, 0)
WIRES = {
    "blue": (0, 102, 204),
    "red": (204, 0, 0),
    "orange": (255, 128, 0),
    "brown": (139, 69, 19),
    "yellow": (255, 204, 0)
}



#Specifying the front to display on the GUI during the simon says game
try:
    font_name = pygame.font.match_font('ds-digital')
    if font_name is None:
        raise ValueError("DS-Digital not found")
    font = pygame.font.Font(font_name, 40)
    large_font = pygame.font.Font(font_name, 60)
except:
    #Fallback to guaranteed monospace
    fallback_font = pygame.font.match_font('monospace')
    font = pygame.font.Font(fallback_font, 40)
    large_font = pygame.font.Font(fallback_font, 60)
    
    
commands = simon_discommands + simon_recommands + non_simon_discommands + non_simon_recommands
random.shuffle(commands)

#This is the list of commands that would be used in the game 
# non_simon_commands = [
#     "Disconnect the brown wire",
#     
#     "Reconnect the red wire",
#     "Reconnect the brown wire",
#     "Disconnect the blue wire",
#     "Disconnect the yellow wire"]
# 
# simon_commands = ["Simon says disconnect the red wire",
#     "Simon says disconnect the orange wire",
#     "Simon says disconnect the brown wire",
#     "Simon says reconnect the orange wire",
#     "Simon says reconnect the red wire",
#     "Simon says reconnect the brown wire",
#     "Simon says disconnect the yellow wire",
#     "Simon says reconnect the yellow wire"
# ]
# commands = simon_commands + non_simon_commands
#This is the expected actions for the player to complete 
# expected_actions = {
#     "Simon says disconnect the red wire": 
#     "Simon says disconnect the orange wire":
#     "Simon says disconnect the brown wire": 
#     "Simon says reconnect the orange wire": 
#     "Simon says reconnect the red wire": 
#     "Simon says reconnect the brown wire": 
#     "Simon says disconnect the yellow wire": 
#     "Simon says reconnect the yellow wire": 
# }

class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
        # initially, the phase thread isn't running
        self._running = False
        # phases can have values (e.g., a pushbutton can be True or False, a keypad passphrase can be some string, etc)
        self._value = None

    # resets the phase's value
    def reset(self):
        self._value = None
        
class Wires(PhaseThread):
    def __init__(self, pins, config=None, name="Wires"):
        super().__init__(name)
        self._value = ""
        # the jumper wire pins
        self._pins = pins
        # Default configuration
        self._config = {
            'pull': Pull.DOWN,  # Can be Pull.UP or Pull.DOWN depending on your circuit
            'connected_state': True,  # What value indicates a connected wire
            'poll_rate': 0.1,  # How frequently to check the wires (seconds)
            'debounce': False,  # Enable debounce for noisy connections
            'debounce_time': 0.05  # Debounce time in seconds
        }
        
        # Update with user configuration if provided
        if config:
            self._config.update(config)
        
        # Initialize the pins
        self._setup_pins()
        
        # For tracking state changes
        self._prev_value = ""
        self._state_changed = False
    
    def _setup_pins(self):
        """Configure the GPIO pins based on settings"""
        for pin in self._pins:
            pin.direction = Direction.INPUT
            pin.pull = self._config['pull']
    
    def read_wires(self):
        """Read the current state of all wires with optional debouncing"""
        if self._config['debounce']:
            # Simple debouncing - take two readings and compare
            reading1 = [pin.value for pin in self._pins]
            sleep(self._config['debounce_time'])
            reading2 = [pin.value for pin in self._pins]
            
            # Only update if both readings match
            if reading1 == reading2:
                # Convert to 1/0 based on what we consider "connected"
                return "".join([str(int(val == self._config['connected_state'])) for val in reading1])
            return self._value  # Return previous value if readings don't match
        else:
            # No debouncing - straightforward reading
            return "".join([str(int(pin.value == self._config['connected_state'])) for pin in self._pins])
    
    # runs the thread
    def run(self):
        self._running = True
        while (True):
            # Get the new wire states
            new_value = self.read_wires()
            
            # Check for state changes
            if new_value != self._value:
                self._value = new_value
                self._state_changed = True
            else:
                self._state_changed = False
                
            sleep(self._config['poll_rate'])
        self._running = False
    
    def has_changed(self):
        """Returns True if wire state has changed since last check"""
        changed = self._state_changed
        self._state_changed = False  # Reset the flag
        return changed
    
    def get_wire(self, index):
        """Get the state of a specific wire by index"""
        if 0 <= index < len(self._pins):
            return bool(int(self._value[index]))
        return None
    
    def __str__(self):
        # Display the binary pattern and decimal value
        if self._value:
            return f"{self._value}/{int(self._value, 2)}"
        return "0/0"  # Default if no value yet

if __name__ == "__main__":
    # Example pin setup (adjust for your specific board)
    wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    
    # Example with custom configuration
    wires_config = {
        'pull': Pull.UP,  # Use pull-ups if your wires connect to ground when active
        'connected_state': False,  # If using pull-ups, a connected wire reads as False
        'debounce': True  # Enable debouncing for stability
    }
    
    wires = Wires(wire_pins, wires_config)
    wires.start()
    
    try:
        while True:
            if wires.has_changed():
                print(f"Wires state changed: {wires}")
            sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
#     def __init__(self, pins, name="Wires"):
#         super().__init__(name)
#         self._value = ""
#         # the jumper wire pins
#         self._pins = pins
# 
#     # runs the thread
#     def run(self):
#         self._running = True
#         while (True):
#             # get the jumper wire states (0->False, 1->True)
#             self._value = "".join([str(int(pin.value)) for pin in self._pins])
#             sleep(0.1)
#         self._running = False
# 
#     def __str__(self):
#         return f"{self._value}/{int(self._value, 2)}"
# 
# wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
# for pin in wire_pins:
#     pin.direction = Direction.INPUT
#     pin.pull = Pull.DOWN
# wires = Wires(wire_pins)

#Creating a subroutine that will detect if the wires are connected or disconnected 
# def read_wire_state(color):
#     pass

def get_scaled_font(size):
    """Returns a font scaled to fit within the window."""
    font_name = pygame.font.match_font('Courier')  # Change to Courier or any font you prefer
    if font_name is None:
        print("Warning: Courier font not found, using fallback font.")
        # Fall back to monospace if Courier is not found
        font_name = pygame.font.match_font('monospace')
    return pygame.font.Font(font_name, size)

def get_resized_font(text, max_width, max_height, initial_font_size=40):
    """
    Resizes the font so that the text fits within the given max_width and max_height.
    """
    font_size = initial_font_size
    font = pygame.font.Font(pygame.font.get_default_font(), font_size)
    text_width, text_height = font.size(text)
    
    # Gradually reduce font size until it fits the screen
    while text_width > max_width or text_height > max_height:
        font_size -= 2  # Decrease font size by 2 points
        font = pygame.font.Font(pygame.font.get_default_font(), font_size)
        text_width, text_height = font.size(text)
    
    return font
    
def wrap_text(text, font, max_width):
    """Wraps text to fit within a given width."""
    words = text.split(' ')
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        test_line = f"{current_line} {word}"
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    return lines

#This layout will be changed, used to test the code
#Setting up the screen that will be displayed dueing the game 
def draw_game(command, timer):
#     win.fill(BLACK)
#     cmd_text = font.render(f"Command: {command}", True, PINK)
#     win.blit(cmd_text, (50, 50))
#     
#     #Having a countdown timer that counts down for the player to complete the task 
#     timer_text = font.render(f"Time left: {max(0, round(5 - timer))}s", True, PINK)
#     win.blit(timer_text, (50, 100))
# 
#     # Draw wire status
#     for i, color in enumerate(WIRES):
#         rect = pygame.Rect(100 + i * 110, 300, 100, 50)
#         pygame.draw.rect(win, WIRES[color], rect)
#         #Connecting the colors of the wires to their state of conneted or disconnected 
#         state = read_wire_state(color)
#         label = font.render(f"{color.title()} ({state})", True, PINK)
#         win.blit(label, (rect.x + 5, rect.y + 15))
# 
#     pygame.display.update()

    win.fill(BLACK)

    # Set the font size dynamically
    font_size = min(WIDTH, HEIGHT) // 20
    font = get_scaled_font(font_size)

    # Wrap command text
    max_width = WIDTH - 50  # 50px padding
    command_lines = wrap_text(f"Command: {command}", font, max_width)
    
    # Display wrapped command text
    y_offset = 50
    for line in command_lines:
        cmd_text = font.render(line, True, PINK)
        win.blit(cmd_text, (50, y_offset))
        y_offset += cmd_text.get_height() + 5  # Adjust space between lines

    # Wrap timer text
    timer_lines = wrap_text(f"Time left: {max(0, round(5 - timer))}s", font, max_width)
    
    # Display wrapped timer text below command
    for line in timer_lines:
        timer_text = font.render(line, True, PINK)
        win.blit(timer_text, (50, y_offset))
        y_offset += timer_text.get_height() + 5

    pygame.display.update()

#Creating a subroutine that is setting up the configuartions of displaying the messages throught the game 
def show_message(text, color = PINK):
#     win.fill(BLACK)
#     msg = large_font.render(text, True, color)
#     win.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
#     pygame.display.update()
#     time.sleep(3)
    win.fill(BLACK)
    
    # Resize font based on text length and screen size
    font = get_resized_font(text, WIDTH - 50, HEIGHT - 50)  # 50px padding from edges
    
    # Render the message with the resized font
    msg = font.render(text, True, color)
    
    # Center the message on the screen
    win.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
    
    pygame.display.update()
    time.sleep(3)
#Creating a main subroutine that will run the game 
def main():
    clock = pygame.time.Clock()
    for command in commands:
        start_time = time.time()
        action_done = False
        while not action_done:
            timer = time.time() - start_time
            draw_game(command, timer)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if command.startswith("Simon says"):
                color = command.split()[3]
                action = "disconnect" if "disconnect" in command else "reconnnect"
                if action == "disconnect":
                    wire_states[color] = False
                    simon_disconnected.add(color)
                else:
                    wire_states[color] = True
                    simon_reconnected.add(color)
                    
                state = read_wire_state(color)
                if action == "diconnect" and state == "disconnected":
                    action_done = True
                elif action == "reconnect" and state == "connected":
                    action_done = True
                    
            else:
                show_message("Simon didn't say do that! Game Over", color = RED)
                pygame.quit()
                return
            
            if timer > 5:
                show_message("Too slow! Game Over!", color = RED)
                pygame.quit()
                return
            
            clock.tick(30)
            
    show_message("Congratulations, you may advance!", color = PINK)
    
if __name__ == "__main__":
    main()
    
                    
#                     if "yellow" in command and "disconnect" in command:
#                         index = wire_colors.index("yellow")
#                         actual_output = actual_output[:3] + "0" + actual_output[4:]
#                     elif "blue" in expection_action and "disconnect" in expected_action:
#                         index = wire_colors.index("blue")
#                         actual_output = actual_output[:4] 
#                     elif "brown" in expection_action and "disconnect" in expected_action:
#                         actual_output = actual_output[1:]
#                     elif "red" in expection_action and "disconnect" in expected_action:
#                         actual_output = actual_output[:1] + "0" + actual_output[3:]
#                     else:
#                         "orange" in expection_action and "disconnect" in expected_action
#                         actual_output = actual_output[:2] + "0" + actual_output[4:]
#                         
                        
                        
  