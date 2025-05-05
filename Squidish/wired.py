#Importing all the libraries 
import pygame
import time
import sys
import random 
from threading import Thread
from time import sleep
import board
from digitalio import DigitalInOut, Direction, Pull

#Base class for bomb components
class PhaseThread(Thread):
    def __init__(self, name):
        #Set thread as daemon to exit with main program 
        super().__init__(name = name, daemon = True)
        #Track if thread is active
        self._running = False
        #Store current state value
        self._value = None

    #Setting up getters and setters 
    def get_running(self):
        return self._running 
    def get_value(self):
        return self._value

    def set_running(self, value):
        self._name = value 
    def set_value(self, value):
        self._value = value 

    #Reset value 
    def reset(self):
        self._value = None

    #Setting up properties 
    running = property(get_running, set_running)
    value = property(get_value, set_value)

#Creation of the wire class that runs in background thread
class Wires(PhaseThread):
    def __init__(self, pins, name = "Wires"):
        super().__init__(name)
        #List of GPIO pins for the wires 
        self._pins = pins
        #Making sure all the wires are started connected = 1
        self._value = "1" * len(pins)
        #Checking the previous state 
        self._prev_value = self._value
        #Tracking if the wires have been changed 
        self._state_changed = False

    #Setting up getters and setters 
    def get_pins(self):
        return self._pins
    def get_value(self):
        return self._value
    def get_pre_value(self):
        return self._pre_value
    def get_state_changed(self):
        return self._state_changed

    def set_pins(self, value):
        self._pins = value 
    def set_value(self, value):
        self._value = value 
    def set_pre_value(self, value):
        self._pre_value = value 
    def set_state_changed(self, value):
        self._state_changed = value 

    #Setting up the properties 
    pins = property(get_pins, set_pins)
    value = property(get_value, set_value)
    pre_value = property(get_pre_value, set_pre_value)
    state_changed = property(get_state_changed, set_state_changed)

    #Starting the thread loop and checking the wire states 
    def run(self):
        self._running = True
        #Initial reading of the wires 
        self.update_state()
        while (True):
            #Check if wire state has changed
            if self.update_state():
                #Update if the wires change
                pass  
            
            #Check every 100ms
            sleep(0.1)
        #The thread is not exected to reach this point 
        self._running = False

    #Subroutine that updates teh wire states and returns true when the wire state changes 
    def update_state(self):
        #Reading all the pin states (TRUE = disconnected, FALSE = connected with pull-ups)
        raw_values = [pin.value for pin in self._pins]
        
        #Convert to wire state (1 = connected, 0 = disconnected)
        #With pull-up resistors: False = connected (1), True = disconnected (0)
        new_state = "".join(["0" if not val else "1" for val in raw_values])
        
        #Check if state changed 
        changed = new_state != self._value
        if changed:
            #Save old state 
            self._prev_value = self._value
            #Update the old state to the new state 
            self._value = new_state
            #Mark the changes 
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
        #Showing the binary values of the pins 
        return f"{self._value}/{int(self._value, 2)}"

#Simulation pin class for testing without hardware
class SimulatedPin:
    def __init__(self, initial_value=False):
        #False = connected (1), True = disconnected (0) with pin values 
        self.value = initial_value
        
    def toggle(self):
        self.value = not self.value

#Initialize pygame
pygame.init()

#Screen dimensions and create display surface
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1024
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simon Says Wire Game")

#Define RGB color values 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

#Defining the wire colors
# Wire Text Colours
BROWN_WIRE = (255, 255, 0) # TRUE COLOUR = YELLOW
RED_WIRE = (0, 190, 104) # TRUE COLOUR =  GREEN
ORANGE_WIRE = (255, 0, 0) # TRUE COLOUR =  RED
YELLOW_WIRE =  (255, 165, 0)# TRUE COLOUR =  ORANGE
GREEN_WIRE =  (174, 90, 0)# TRUE COLOUR =  BROWN

#Loading the fonts for different UI elements 
font = pygame.font.Font('font1.otf', 30)
small_font = pygame.font.Font('font1.otf', 24)
wire_font = pygame.font.Font('font1.otf', 22)

#Main game function
def main():
    #Initialize pygame mixer with explicit parameters for better compatibility
   
    
    
    #Load background image with error handling
    try:
        bg_image = pygame.image.load("simonsays.png")
        #Scaling the image to fit 
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Failed to load background image: {e}")
        # Create fallback background
        bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_image.fill((50, 50, 80))  # Dark blue fallback
    
    #Create a semi-transparent overlay for better text readability
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) 

    #Sound file mappings - unchanged
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
    
    #Load audio files with improved error handling
    command_sounds = {}
    for command, filename in command_sound_files.items():
        try:
            #Load sounds 
            command_sounds[command] = pygame.mixer.Sound(filename)
            print(f"Successfully loaded sound: {filename}")
        except Exception as e:
            print(f"Failed to load sound {filename}: {e}")
    
    #Test the first loaded sound if any were loaded
    if command_sounds:
        #Play test sounds 
        first_sound = list(command_sounds.values())[0]
        first_sound.play()
        print(f"Playing test sound from command file")
    else:
        print("No sound files loaded successfully! Check your sound files.")

    #Determine if running on Raspberry Pi with real hardware
    #Assuming this is running on Raspberry Pi with imports at the top
    RPi = True 
    try:
        # Set up physical pins
        wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
        for pin in wire_pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.DOWN
            
    except (ImportError, NotImplementedError, Exception) as e:
        print(f"Hardware setup error: {e}")
        RPi = False
        wire_pins = [SimulatedPin() for _ in range(5)]
    
    #Create wires object
    wires = Wires(wire_pins)
    #Start moitoring wires
    wires.start()
    
    #Define colors and commands
    colors = ["brown", "red", "orange", "yellow", "green"]
    color_values = [BROWN_WIRE, RED_WIRE, ORANGE_WIRE, YELLOW_WIRE, GREEN_WIRE]  # Actual RGB values for display

    #Creatinng a random set of commands with some commands having Simon says and some not having Simon says 
    non_simon_discommands = [f"Disconnect the {color} wire" for color in colors]
    non_simon_recommands = [f"Reconnect the {color} wire" for color in colors]
    simon_discommands = [f"Simon says disconnect the {color} wire" for color in colors]
    simon_recommands = [f"Simon says reconnect the {color} wire" for color in colors]
    
    #Generate game commands - unchanged
    wire_states = {color: True for color in colors}
    #Colors Simon has commanded to disconnect 
    simon_disconnected = set()
    #Colors Simon has commanded to reconnect 
    simon_reconnected = set()
    #Creation of the list to hold the commands 
    commands = []
    
    #First Simon command
    #Randomly pick a wire color to disconnect first 
    first_color = random.choice(colors)
    #Marking the wire as diconnected 
    wire_states[first_color] = False
    #Adding it to the list of disconnected colors 
    simon_disconnected.add(first_color)
    #Add the corresponding command 
    commands.append(simon_discommands[colors.index(first_color)])
    
    #Generate 9 more commands - unchanged
    while len(commands) < 10:
        #Possible valid actions for the next command 
        valid_actions = []

        #Add disconnect actions for wires not yet disconnected 
        for color in colors:
            if wire_states[color] and color not in simon_disconnected:
                valid_actions.append(("simon_disconnect", color))
        #Add reconnect actions for wires that have been disconnected but not reconnected 
        for color in simon_disconnected:
            if not wire_states[color] and color not in simon_reconnected:
                valid_actions.append(("simon_reconnect", color))
        #60 percent chance to pick a valid Simon says command
        if valid_actions and random.random() < 0.6:
            #Choose one 
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
            #Create a non Simon says command 
            if random.choice(["disconnect", "reconnect"]) == "disconnect":
                #Still connected 
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
    
    #Reset wire states for game start
    wire_states = {color: True for color in colors}
    #All wires start connected 
    current_command_index = 0
    #Start with the first command 
    current_command = commands[current_command_index]
    game_over = False
    won = False
    #Displa success/failure/status to player 
    status_message = ""
    
    #Audio playback variables
    #Track if audio has played for the command 
    command_played = False
    
    #For automatic checking
    #Initial state of wires 
    last_wire_state = wires._value
    #Result of the player's action
    action_result = None 
    #Time when action result was determined
    action_time = 0
    
    #Variables for tracking player actions
    waiting_for_confirmation = False
    #Track if player took an action
    #Whether a wire was chnaged
    wire_changed = False  
    
    #Store wire state at the start of each command 
    initial_wire_state = wires._value
    
    #Main game loop
    clock = pygame.time.Clock()
    running = True
    
    #Initialize the timer for 20 seconds
    command_start_time = time.time()
    #20 seconds timer
    timer_duration = 20
    #Delay before checking the action
    check_delay = 2.0  
    #How long to show success/failure message
    show_result_time = 2.0  

    #Play the first command
    if current_command in command_sounds:
        #Stop any currently playing sounds
        pygame.mixer.stop()  
        command_sounds[current_command].play()
        command_played = True

    while running:
        current_time = time.time()
        
        #Calculate remaining time for current command
        elapsed_time = current_time - command_start_time
        remaining_time = max(0, timer_duration - elapsed_time)
        
        #Play command audio if not played yet
        if not command_played and not game_over and not waiting_for_confirmation:
            if current_command in command_sounds:
                pygame.mixer.stop()  # Stop any currently playing sounds
                command_sounds[current_command].play()
            command_played = True
        
        #Timer check: if the player hasn't made a move in 20 seconds, game ends
        if remaining_time <= 0 and not game_over and not waiting_for_confirmation:
            game_over = True
            won = False
            status_message = "Time's up! You took too long."
        
        #Handle events 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                #Space to check command when waiting for confirmation
                if event.key == pygame.K_SPACE:
                    #Always allow checking with space, even if no wire changes detected
                    if not game_over:
                        #Store current wire state for evaluation
                        current_wire_state = wires._value
                        
                        #Check if command starts with "Simon says"
                        is_simon = current_command.startswith("Simon says")
                        is_disconnect = "disconnect" in current_command
                        color = next(c for c in colors if c in current_command)
                        color_index = colors.index(color)
                        
                        #Get wire state for the specific color
                        is_disconnected = current_wire_state[color_index] == "0"
                        initial_was_disconnected = initial_wire_state[color_index] == "0"
                        
                        #Check if the player actually changed the wire state
                        wire_was_changed = is_disconnected != initial_was_disconnected
                        
                        #First, determine the correct action based on command
                        if is_simon:
                            #Simon says: must follow command
                            correct_action = is_disconnect == is_disconnected
                        else:
                            #Not Simon says: must ignore command
                            #Success if the wire state hasn't changed
                            correct_action = not wire_was_changed
                        
                        #Set result
                        action_result = correct_action
                        
                        #Success or failure action
                        if action_result:
                            status_message = "SUCCESS!"
                            #Move to next command after success
                            current_command_index += 1
                            if current_command_index < len(commands):
                                current_command = commands[current_command_index]
                                #Reset timer for the new command
                                command_start_time = time.time()
                                action_result = None
                                command_played = False
                                waiting_for_confirmation = False
                                #Store new initial wire state for the new command
                                initial_wire_state = wires._value
                            else:
                                current_command = "All commands completed!"
                                game_over = True
                                won = True
                        else:
                            status_message = "FAILURE!"
                            game_over = True
                            won = False
                
                #Simulation mode: toggle wires with number keys
                elif not RPi and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    index = event.key - pygame.K_1
                    if index < len(wire_pins):
                        wire_pins[index].toggle()
                        wires.update_state()
        
        #Check for wire state changes (always update last_wire_state)
        if wires._value != last_wire_state:
            last_wire_state = wires._value
            #Set waiting for confirmation only if the game is still active
            if not game_over and not waiting_for_confirmation:
                waiting_for_confirmation = True
                status_message = "Press SPACE to check your action"
        
        #Draw elements
        #Draw background image
        screen.blit(bg_image, (0, 0))  
        #Draw semi-transparent overlay
        screen.blit(overlay, (0, 0))  
        
        #Display wire names and statuses
        wire_display_x = 50
        wire_display_y = 150
        wire_spacing = 40
        
        for i, color in enumerate(colors):
            y_pos = wire_display_y + i * wire_spacing
            is_connected = wires._value[i] == "1"
            status_text = "CONNECTED" if is_connected else "DISCONNECTED"
            
            #Display wire name and status
            wire_text = wire_font.render(f"{color.upper()} WIRE: {status_text}", True, color_values[i])
            screen.blit(wire_text, (wire_display_x, y_pos))
        
     
        
        #Show progress
        progress = small_font.render(f"Progress: {current_command_index}/{len(commands)}", True, WHITE)
        screen.blit(progress, (30, 30))
        
        #Timer display or instruction
        if not waiting_for_confirmation and not game_over:
            #Red when less than 5 seconds left
            timer_color = WHITE if remaining_time > 5 else RED  
            timer_text = small_font.render(f"Time: {int(remaining_time)}s", True, timer_color)
            screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 30, 30))
        else:
            #Show "Press SPACE" message
            space_text = small_font.render("PRESS SPACE TO CHECK", True, GREEN)
            screen.blit(space_text, (SCREEN_WIDTH - space_text.get_width() - 30, 30))
        
        #Status message (success/failure) - always show if it exists
        if status_message:
            if action_result is not None:
                status_color = GREEN if action_result else RED
            else:
                #For the "Press SPACE" message
                status_color = WHITE  
            status_text = font.render(status_message, True, status_color)
            screen.blit(status_text, (SCREEN_WIDTH // 2 - status_text.get_width() // 2, 350))
        
        #Game over message - no restart option
        if game_over:
            result_text = font.render(f"Game Over - {'You Win!' if won else 'You Lose!'}", True, WHITE)
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 400))
        
        #Update display
        pygame.display.flip()
        
        #Cap the frame rate
        clock.tick(60)
    
    #Clean up
    pygame.quit()
    sys.exit()

#Run the game
if __name__ == "__main__":
    main()
