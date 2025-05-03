#Import the different libraries 
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
        new_state = "".join(["0" if val else "1" for val in raw_values])

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

# Example usage
if __name__ == "__main__":
    # Create pins (match the pins used in your main program)
    wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    for pin in wire_pins:
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN
    print("HHH")
    # Create and start wires component
    wires = Wires(wire_pins)
    wires.start()
    
    print("Wire monitoring started. Press Ctrl+C to exit.")
    print("Initial state:", wires)
    


##################################################################################################################



# Command generation
colors = ["brown", "red", "orange", "yellow", "blue"]
non_simon_discommands = [f"Disconnect the {color} wire" for color in colors]
non_simon_recommands = [f"Reconnect the {color} wire" for color in colors]
simon_discommands = [f"Simon says disconnect the {color} wire" for color in colors]
simon_recommands = [f"Simon says reconnect the {color} wire" for color in colors]

wire_states = {color: True for color in colors}
simon_disconnected = set()
simon_reconnected = set()
commands = []

def display_wire_states():
    return ''.join(['1' if wire_states[color] else '0' for color in colors])

def display_individual_wire_states():
    return ''.join(['1' if wire_states[color] else '0' for color in colors])

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

######################################################################################################################

# Evaluate commands
wire_states = {color: True for color in colors}
for i, command in enumerate(commands):
    is_simon = command.startswith("Simon says")
    is_disconnect = "disconnect" in command
    color = next(c for c in colors if c in command)

    prev_state = ''.join(['1' if wire_states[c] else '0' for c in colors])
    if is_simon:
        if is_disconnect:
            wire_states[color] = False
        else:
            wire_states[color] = True

    expected_state = ''.join(['1' if wire_states[c] else '0' for c in colors])
    actual_state = wires._value

    # Placeholder: result = {"command": command, "expected": expected_state, "actual": actual_state, "status": "correct/incorrect"}
    # You can use this dictionary to pass to the GUI layer later
    if is_simon:
        result_ok = actual_state == expected_state
    else:
        result_ok = actual_state == prev_state