from threading import Thread
from time import sleep

# Only import GPIO stuff if on a Pi
try:
    import board
    from digitalio import DigitalInOut, Direction, Pull
    RPi = True
except ImportError:
    RPi = False
    print("GPIO not available. Running in simulation mode.")


# Base thread class for phases like toggles/wires/buttons
class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
        self._running = False
        self._value = None
        if RPi:
            for pin in self._pins:
                pin.direction = Direction.INPUT
                pin.pull = Pull.DOWN

    def reset(self):
        self._value = None


# Toggle switch handler class
class Toggles(PhaseThread):
    def __init__(self, pins, name="Toggles"):
        super().__init__(name)
        self._pins = pins

        # Setup each pin as input with a pull-down resistor (starts as LOW / 0)
        for pin in self._pins:
            pin.direction = Direction.INPUT
            pin.pull = Pull.DOWN

        # Start with all toggles down
        self._value = "0000"
        self._prev_value = self._value
        self._state_changed = False

    def run(self):
        """Thread continuously checks for toggle changes."""
        self._running = True
        self.update_state()

        while self._running:
            if self.update_state():
                # You could trigger logic here or just print for testing
                print(f"Toggles changed: {self._value}/{int(self._value, 2)}")
            sleep(0.1)

    def update_state(self):
        """Update toggle state and return True if the state changed."""
        new_state = "".join([str(int(pin.value)) for pin in self._pins])

        changed = new_state != self._value
        if changed:
            self._prev_value = self._value
            self._value = new_state
            self._state_changed = True
        else:
            self._state_changed = False

        return changed

    def all_down(self):
        """Returns True if all toggles are down (i.e., '0000')"""
        return self._value == "0000"

    def get_toggle_index(self):
        """
        Returns index (0–3) of the single flipped toggle.
        Only works when exactly one toggle is up (i.e., value is '0100', etc).
        """
        if self._value.count("1") == 1:
            return self._value.find("1")
        return None

    def has_changed(self):
        """Checks if toggles changed since last time."""
        if self._state_changed:
            self._state_changed = False
            return True
        return False

    def __str__(self):
        """Show state as binary and its decimal equivalent."""
        return f"{self._value}/{int(self._value, 2)}"


# Test code for local Pi testing (doesn't affect real game logic)
if __name__ == "__main__":
    # Set up pins (GPIO 12, 16, 20, 21 for 4 toggles)
    toggle_pins = [DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]
    
    # Create and start the toggle monitor
    toggles = Toggles(toggle_pins)
    toggles.start()

    print("Monitoring toggles... flip exactly ONE toggle to simulate input.")

    try:
        while True:
            if toggles.has_changed():
                index = toggles.get_toggle_index()

                if index is not None:
                    print(f"User selected toggle index: {index}")
                    print("Waiting for toggles to reset (all down)...")

                    # Wait for reset before accepting another input
                    while not toggles.all_down():
                        sleep(0.1)
                    print("Toggles reset! Ready for next input.")

            sleep(0.1)

    except KeyboardInterrupt:
        print("\nToggles test interrupted. Exiting...")