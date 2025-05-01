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