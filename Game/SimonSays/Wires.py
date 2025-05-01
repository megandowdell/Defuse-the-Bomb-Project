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

# Enhanced Wires class with configuration options
class Wires(PhaseThread):
    def __init__(self, pins, config=None, name="Wires"):
        super().__init__(name)
        # All wires start as connected - initialize with all 1's
        self._value = "1" * len(pins)
        # the jumper wire pins
        self._pins = pins
        # Default configuration - assuming all wires start connected
        self._config = {
            'pull': Pull.UP,     # Using Pull.UP since we expect wires to be connected to GND
            'connected_state': False,  # When using pull-up, a connected wire reads as False
            'poll_rate': 0.1,    # How frequently to check the wires (seconds)
            'debounce': True,    # Enable debounce for stability with physical wires
            'debounce_time': 0.05  # Debounce time in seconds
        }
        
        # Update with user configuration if provided
        if config:
            self._config.update(config)
        
        # Initialize the pins
        self._setup_pins()
        
        # For tracking state changes
        self._prev_value = self._value
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
                # 1 means connected, 0 means disconnected in the output
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

# Example of how to use this enhanced Wires class:
if __name__ == "__main__":
    # Example pin setup (adjust for your specific board)
    wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    
    # For a bomb game where all wires start connected:
    # - Use pull-up resistors (wires connect to GND when connected)
    # - A connected wire will read as False with pull-ups
    # - When a wire is cut/disconnected, it will read as True
    wires_config = {
        'pull': Pull.UP,          # Pull-up resistors
        'connected_state': False, # Connected wires read as False (connected to GND)
        'debounce': True          # Enable debouncing for stability
    }
    
    wires = Wires(wire_pins, wires_config)
    wires.start()
    
    print("Game starting - all wires should be connected!")
    print(f"Initial state: {wires}")
    
    try:
        while True:
            if wires.has_changed():
                print(f"ALERT: Wire state changed: {wires}")
                # Check if all wires are disconnected
                if wires._value == "0" * len(wire_pins):
                    print("All wires have been cut!")
                # Check for specific patterns that might be required for defusal
                if wires._value == "10101":  # Example pattern
                    print("Correct wire pattern detected!")
            sleep(0.2)
    except KeyboardInterrupt:
        print("Game terminated...")