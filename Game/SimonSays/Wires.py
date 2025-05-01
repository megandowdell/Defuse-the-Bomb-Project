from threading import Thread
from time import sleep
import board
from digitalio import DigitalInOut, Direction, Pull

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
        
        # Setup pins with pull-up resistors (for connecting wires to GND)
        for pin in self._pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.UP
            
        # All wires start connected - initialize with all 1's
        self._value = "1" * len(pins)
        self._prev_value = self._value
        self._state_changed = False
        
        # Print configuration info
        print(f"Wires component initialized with {len(pins)} wires")
        print("All wires should start CONNECTED")
        print("Physical setup: GPIO pins with pull-up resistors -> wires -> GND")
    
    def run(self):
        """Main thread that continuously monitors wire state"""
        self._running = True
        
        # Initial reading
        self.update_state()
        
        while (True):
            # Check if wire state has changed
            if self.update_state():
                # State changed - we can take actions here if needed
                pass
            
            # Poll at a reasonable rate (100ms)
            sleep(0.1)
        
        self._running = False
    
    def update_state(self):
        """Updates wire state and returns True if state changed"""
        # Read raw pin values (TRUE = disconnected, FALSE = connected with pull-ups)
        raw_values = [pin.value for pin in self._pins]
        
        # Convert to wire state (1 = connected, 0 = disconnected)
        # With pull-up resistors: False = connected, True = disconnected
        new_state = "".join(["1" if not val else "0" for val in raw_values])
        
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
    
    def get_wire(self, index):
        """Get the state of a specific wire by index (1 = connected, 0 = disconnected)"""
        if 0 <= index < len(self._pins):
            return int(self._value[index])
        return None
    
    def __str__(self):
        """Display wire state as binary and decimal"""
        return f"{self._value}/{int(self._value, 2)}"

# Example usage
if __name__ == "__main__":
    # Create pins (match the pins used in your main program)
    wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    
    # Create and start wires component
    wires = Wires(wire_pins)
    wires.start()
    
    print("Wire monitoring started. Press Ctrl+C to exit.")
    print("Initial state:", wires)
    
    try:
        while True:
            if wires.has_changed():
                print(f"Wire state changed: {wires}")
                
                # Example game logic based on wire state
                if wires._value == "00000":
                    print("All wires have been cut!")
                elif wires._value == "10101":  # Example specific pattern
                    print("Correct wire pattern detected!")
                    
            sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting...")