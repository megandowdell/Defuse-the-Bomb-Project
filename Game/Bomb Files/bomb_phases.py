#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: Christa, Khalil, Megan, Matt
#################################

# import the configs
from bomb_configs import *
# other imports
import pygame
from pygame.locals import * # handles events, mouse/keyboard controls etc.
from threading import Thread
from time import sleep
import os
import sys

#mini game imports
from TicTacToe import play_tic_tac_toe
from Hopscotch import play_turn, draw_board, generate_board



#########
# classes
#########
# the LCD display GUI
class Lcd:
    def __init__(self, window):
        # Initialize pygame
        pygame.init()
        # Set up the window
        self.window = window
        # Set the window to fullscreen
        self.fullscreen = True
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((800, 600))
        
        # Set caption and icon
        pygame.display.set_caption("Defuse the Bomb")
        
        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        
        # Setup fonts
        self.font = pygame.font.SysFont("Courier New", 14)
        self.font_large = pygame.font.SysFont("Courier New", 18)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        
        # Boot text
        self._boot_text = ""
        
        # Phase text elements
        self._timer_text = "Time left: "
        self._keypad_text = "Keypad phase: "
        self._wires_text = "Wires phase: "
        self._button_text = "Button phase: "
        self._toggles_text = "Toggles phase: "
        self._strikes_text = "Strikes left: "
        
        # Internal state
        self._game_active = True
        
        # setup the initial "boot" GUI
        self.setupBoot()

    # sets up the LCD "boot" GUI
    def setupBoot(self):
        # Clear the screen
        self.screen.fill(self.BLACK)
        # Update the display
        pygame.display.flip()

    # sets up the LCD GUI
    def setup(self):
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Draw the interface
        self._render_interface()
        
        # Update the display
        pygame.display.flip()

    # Render the main interface
    def _render_interface(self):
        # Only render if the game is active
        if not self._game_active:
            return
            
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Get screen dimensions
        width, height = self.screen.get_size()
        
        # Render the scroll text at the top
        text_surface = self.font.render(self._boot_text, True, self.WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        # Render timer
        text_surface = self.font_large.render(self._timer_text, True, self.GREEN)
        self.screen.blit(text_surface, (10, 100))
        
        # Render keypad status
        text_surface = self.font_large.render(self._keypad_text, True, self.GREEN)
        self.screen.blit(text_surface, (10, 130))
        
        # Render wires status
        text_surface = self.font_large.render(self._wires_text, True, self.GREEN)
        self.screen.blit(text_surface, (10, 160))
        
        # Render button status
        text_surface = self.font_large.render(self._button_text, True, self.GREEN)
        self.screen.blit(text_surface, (10, 190))
        
        # Render toggles status
        text_surface = self.font_large.render(self._toggles_text, True, self.GREEN)
        self.screen.blit(text_surface, (10, 220))
        
        # Render strikes
        text_surface = self.font_large.render(self._strikes_text, True, self.GREEN)
        self.screen.blit(text_surface, (width - 200, 220))
        
        # Show buttons if enabled
        if SHOW_BUTTONS:
            # Pause button
            pygame.draw.rect(self.screen, self.RED, (10, height - 80, 120, 40))
            text_surface = self.font_large.render("Pause", True, self.WHITE)
            text_rect = text_surface.get_rect(center=(10 + 60, height - 60))
            self.screen.blit(text_surface, text_rect)
            
            # Quit button
            pygame.draw.rect(self.screen, self.RED, (width - 130, height - 80, 120, 40))
            text_surface = self.font_large.render("Quit", True, self.WHITE)
            text_rect = text_surface.get_rect(center=(width - 70, height - 60))
            self.screen.blit(text_surface, text_rect)
        
        # Update the display
        pygame.display.flip()

    # Update the boot text
    def update_boot_text(self, text):
        self._boot_text = text
        self._render_interface()

    # Update the phase status texts
    def update_status(self, timer_text, keypad_text, wires_text, button_text, toggles_text, strikes_text):
        self._timer_text = f"Time left: {timer_text}"
        self._keypad_text = f"Keypad phase: {keypad_text}"
        self._wires_text = f"Wires phase: {wires_text}"
        self._button_text = f"Button phase: {button_text}"
        self._toggles_text = f"Toggles phase: {toggles_text}"
        self._strikes_text = f"Strikes left: {strikes_text}"
        self._render_interface()

    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button

    # pauses the timer
    def pause(self):
        if (RPi):
            self._timer.pause()

    # setup the conclusion GUI (explosion/defusion)
    def conclusion(self, success=False):
        self._game_active = False
        
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Get screen dimensions
        width, height = self.screen.get_size()
        
        # Display success or failure message
        message = "BOMB DEFUSED!" if success else "BOMB EXPLODED!"
        text_surface = self.font_large.render(message, True, self.GREEN if success else self.RED)
        text_rect = text_surface.get_rect(center=(width // 2, height // 3))
        self.screen.blit(text_surface, text_rect)
        
        # Retry button
        pygame.draw.rect(self.screen, self.RED, (width // 4 - 60, height // 2, 120, 40))
        text_surface = self.font_large.render("Retry", True, self.WHITE)
        text_rect = text_surface.get_rect(center=(width // 4, height // 2 + 20))
        self.screen.blit(text_surface, text_rect)
        
        # Quit button
        pygame.draw.rect(self.screen, self.RED, (3 * width // 4 - 60, height // 2, 120, 40))
        text_surface = self.font_large.render("Quit", True, self.WHITE)
        text_rect = text_surface.get_rect(center=(3 * width // 4, height // 2 + 20))
        self.screen.blit(text_surface, text_rect)
        
        # Update the display
        pygame.display.flip()

    # Process events (mouse clicks, etc.)
    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quit()
            elif event.type == MOUSEBUTTONDOWN:
                # Get screen dimensions
                width, height = self.screen.get_size()
                
                # Check if game is active
                if self._game_active:
                    # Check if pause button is clicked
                    if SHOW_BUTTONS and 10 <= event.pos[0] <= 130 and height - 80 <= event.pos[1] <= height - 40:
                        self.pause()
                    
                    # Check if quit button is clicked
                    if SHOW_BUTTONS and width - 130 <= event.pos[0] <= width - 10 and height - 80 <= event.pos[1] <= height - 40:
                        self.quit()
                else:
                    # Check if retry button is clicked
                    if width // 4 - 60 <= event.pos[0] <= width // 4 + 60 and height // 2 <= event.pos[1] <= height // 2 + 40:
                        self.retry()
                    
                    # Check if quit button is clicked
                    if 3 * width // 4 - 60 <= event.pos[0] <= 3 * width // 4 + 60 and height // 2 <= event.pos[1] <= height // 2 + 40:
                        self.quit()

    # re-attempts the bomb (after an explosion or a successful defusion)
    def retry(self):
        # re-launch the program (and exit this one)
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    # quits the GUI, resetting some components
    def quit(self):
        if (RPi):
            # turn off the 7-segment display
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            # turn off the pushbutton's LED
            for pin in self._button._rgb:
                pin.value = True
        # exit the application
        pygame.quit()
        exit(0)

# template (superclass) for various bomb components/phases
class PhaseThread(Thread): # Parent class connecting similarities across threads (thread -> phase thread -> individual threads)
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        # phases have an electronic component (which usually represents the GPIO pins)
        self._component = component
        # phases have a target value (e.g., a specific combination on the keypad, the proper jumper wires to "cut", etc)
        self._target = target
        # phases can be successfully defused
        self._defused = False
        # phases can be failed (which result in a strike)
        self._failed = False
        # phases have a value (e.g., a pushbutton can be True/Pressed or False/Released, several jumper wires can be "cut"/False, etc)
        self._value = None
        # phase threads are either running or not
        self._running = False

# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # the default value is the specified initial value
        self._value = initial_value
        # is the timer paused?
        self._paused = False
        # initialize the timer's minutes/seconds representation
        self._min = ""
        self._sec = ""
        # by default, each tick is 1 second
        self._interval = 1

    # runs the thread - adds logic to code
    def run(self):
        self._running = True
        while (self._running):
            if (not self._paused):
                # update the timer and display its value on the 7-segment display
                self._update()
                if RPi:
                    self._component.print(str(self))
                # wait 1s (default) and continue
                sleep(self._interval)
                # the timer has expired -> phase failed (explode)
                if (self._value == 0):
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)

    # updates the timer (only internally called)
    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    # pauses and unpauses the timer
    def pause(self):
        # toggle the paused state
        self._paused = not self._paused
        # blink the 7-segment display when paused
        if RPi:
            self._component.blink_rate = (2 if self._paused else 0)

    # returns the timer as a string (mm:ss)
    def __str__(self):
        return f"{self._min}:{self._sec}"

# the keypad phase
class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        # the default value is an empty string
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            if RPi:
                # process keys when keypad key(s) are pressed
                if (self._component.pressed_keys):
                    # debounce
                    while (self._component.pressed_keys):
                        try:
                            # just grab the first key pressed if more than one were pressed
                            key = self._component.pressed_keys[0]
                        except:
                            key = ""
                        sleep(0.1)
                    # log the key
                    self._value += str(key)
                    # the combination is correct -> phase defused
                    if (self._value == self._target):
                        self._defused = True
                    # the combination is incorrect -> phase failed (strike)
                    elif (self._value != self._target[0:len(self._value)]):
                        self._failed = True
            sleep(0.1)

    # returns the keypad combination as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value

# the jumper wires phase
class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)

    # runs the thread
    def run(self):
        # TODO
        pass

    # returns the jumper wires state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            # TODO
            pass

# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        # the default value is False/Released
        self._value = False
        # has the pushbutton been pressed?
        self._pressed = False
        # we need the pushbutton's RGB pins to set its color
        self._rgb = component_rgb
        # the pushbutton's randomly selected LED color
        self._color = color
        # we need to know about the timer (7-segment display) to be able to determine correct pushbutton releases in some cases
        self._timer = timer

    # runs the thread
    def run(self):
        self._running = True
        if RPi:
            # set the RGB LED color
            self._rgb[0].value = False if self._color == "R" else True
            self._rgb[1].value = False if self._color == "G" else True
            self._rgb[2].value = False if self._color == "B" else True
        while (self._running):
            if RPi:
                # get the pushbutton's state
                self._value = self._component.value
                # it is pressed
                if (self._value):
                    # note it
                    self._pressed = True
                # it is released
                else:
                    # was it previously pressed?
                    if (self._pressed):
                        # check the release parameters
                        # for R, nothing else is needed
                        # for G or B, a specific digit must be in the timer (sec) when released
                        if (not self._target or self._target in self._timer._sec):
                            self._defused = True
                        else:
                            self._failed = True
                        # note that the pushbutton was released
                        self._pressed = False
            sleep(0.1)

    # returns the pushbutton's state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return str("Pressed" if self._value else "Released")

# the toggle switches phase
class Toggles(PhaseThread):
    def __init__(self, pins, name="Toggles"):
        super().__init__(name)
        self._value = ""
        # the toggle switch pins
        self._pins = pins

    # runs the thread
    def run(self):
        self._running = True
        while (True):
            # get the toggle switch values (0->False, 1->True)
            self._value = "".join([str(int(pin.value)) for pin in self._pins])
            sleep(0.1)
        self._running = False

    def __str__(self):
        return f"{self._value}/{int(self._value, 2)}"

# Main game loop function to add to bomb.py
def pygame_main_loop(lcd):
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Process events
        lcd.process_events()
        
        # Maintain frame rate
        clock.tick(60)


# PHASE 1: TIC TAC TOE
def phase_1():
    result = play_tic_tac_toe()
    if result == "win":
        return True
    else:
        return False

# PHASE 2: RED LIGHT GREEN LIGHT
#def phase_2():
    
# PHASE 3: SIMON SAYS
#def phase_3():
    
    
    
# PHASE 4: HOPSCOTCH
# Initialize hopscotch board and progress tracker
hopscotch_board = generate_board(successes_per_row=1)
current_hopscotch_row = 0
hopscotch_result = None  # Can be None, "win", or "lose"

def phase_4(selected_col):
    global current_hopscotch_row, hopscotch_result

    if hopscotch_result is not None:
        return hopscotch_result  # Game is done for this round

    # selected_col is 0–3 based on the GPIO toggle input
    current_hopscotch_row, hopscotch_result = play_turn(
        hopscotch_board, current_hopscotch_row, selected_col
    )

    if hopscotch_result == "win":
        print("Hopscotch: SUCCESS")
    elif hopscotch_result == "lose":
        print("Hopscotch: BOOM")

    return hopscotch_result  # Used by bomb controller to move to next phase or end game