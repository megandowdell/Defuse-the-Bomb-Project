import time
import random
from bomb_configs import *
from bomb_phases import *

# Set up LED control
def set_led(color):
    #Set the RGB LED based on the current light color
    if not RPi:
        return

    if color == "green":
        component_button_RGB[0].value = True   # Red OFF
        component_button_RGB[1].value = False  # Green ON
        component_button_RGB[2].value = True   # Blue OFF
    elif color == "red":
        component_button_RGB[0].value = False  # Red ON
        component_button_RGB[1].value = True   # Green OFF
        component_button_RGB[2].value = True   # Blue OFF
    else:
        # turn everything off
        for pin in component_button_RGB:
            pin.value = True

def check_button_press():
    """Check if the button is pressed."""
    if not RPi:
        return False

    return component_button_state.value

def RedLightGreenLight():
    #Main Red Light Green Light game 
    print("Welcome to Red Light, Green Light!")
    print("Press the button ONLY when the light is GREEN.")

    # Initial light color
    light_color = "red"
    set_led(light_color)
    
    game_time = 20  # seconds to win
    start_time = time.time()

    while (time.time() - start_time) < game_time:
        # Randomly change the light every 2-5 seconds
        next_change = random.uniform(2, 5)
        change_time = time.time() + next_change

        while time.time() < change_time:
            if check_button_press():
                print("Button Pressed!")

                if light_color == "green":
                    print("Good move!")
                else:
                    print("You pressed during RED! You lose!")
                    set_led("off")
                    return  # End the game immediately

            
                time.sleep(0.3)

            time.sleep(0.05)  #

        # Switch the light
        light_color = "green" if light_color == "red" else "red"
        set_led(light_color)
        print(f"The light is now {light_color.upper()}!")

    # Survived the game
    print("Congratulations! You survived and won!")
    set_led("off")


if __name__ == "__main__":
    RedLightGreenLight()
