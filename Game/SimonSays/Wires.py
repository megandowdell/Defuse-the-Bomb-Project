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
    
