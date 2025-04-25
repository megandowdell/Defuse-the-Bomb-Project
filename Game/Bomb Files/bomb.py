#################################
# CSC 102 Defuse the Bomb Project
# Main program 
# Team: HAS BEEN CHECKED AND CONVERTED TO PYGAME
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

import time
import sys

###########
# functions
###########
# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles
    
    # setup the timer thread
    timer = Timer(component_7seg, COUNTDOWN)
    # setup the keypad thread
    keypad = Keypad(component_keypad, keypad_target)
    # setup the jumper wires thread
    wires = Wires(component_wires, wires_target)
    # setup the pushbutton thread
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target)

    # start the phase threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

# checks the phase threads
def check_phases():
    global active_phases
    
    # check the timer
    if (timer._running):
        # print timer status for debugging
        print(f"Time left: {timer}")
    else:
        # the countdown has expired -> explode!
        # turn off the bomb and signal failure
        turn_off()
        # don't check any more phases
        return
    
    # check the keypad
    if (keypad._running):
        # print keypad status for debugging
        print(f"Combination: {keypad}")
        # the phase is defused -> stop the thread
        if (keypad._defused):
            keypad._running = False
            active_phases -= 1
            print("Keypad defused!")
        # the phase has failed -> strike
        elif (keypad._failed):
            strike()
            # reset the keypad
            keypad._failed = False
            keypad._value = ""
    
    # check the wires
    if (wires._running):
        # print wires status for debugging
        print(f"Wires: {wires}")
        # the phase is defused -> stop the thread
        if (wires._defused):
            wires._running = False
            active_phases -= 1
            print("Wires defused!")
        # the phase has failed -> strike
        elif (wires._failed):
            strike()
            # reset the wires
            wires._failed = False
    
    # check the button
    if (button._running):
        # print button status for debugging
        print(f"Button: {button}")
        # the phase is defused -> stop the thread
        if (button._defused):
            button._running = False
            active_phases -= 1
            print("Button defused!")
        # the phase has failed -> strike
        elif (button._failed):
            strike()
            # reset the button
            button._failed = False
    
    # check the toggles
    if (toggles._running):
        # print toggles status for debugging
        print(f"Toggles: {toggles}")
        # the phase is defused -> stop the thread
        if (toggles._defused):
            toggles._running = False
            active_phases -= 1
            print("Toggles defused!")
        # the phase has failed -> strike
        elif (toggles._failed):
            strike()
            # reset the toggles
            toggles._failed = False

    # Note the strikes on GUI for debugging
    print(f"Strikes left: {strikes_left}")
    
    # too many strikes -> explode!
    if (strikes_left == 0):
        # turn off the bomb and signal failure
        turn_off()
        # stop checking phases
        return

    # the bomb has been successfully defused!
    if (active_phases == 0):
        # turn off the bomb and signal success
        turn_off()
        # stop checking phases
        return

    #check the phases again after a slight delay
    time.sleep(0.1)
    check_phases()

# handles a strike
def strike():
    global strikes_left
    
    # note the strike
    strikes_left -= 1
    print(f"STRIKE! {strikes_left} strikes left.")

# turns off the bomb
def turn_off():
    # stop all threads
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    # turn off the 7-segment display
    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    # turn off the pushbutton's LED
    for pin in button._rgb:
        pin.value = True

######
# MAIN
######
# initialize the Pygame GUI - TBD

# initialize the bomb strikes and active phases (i.e., not yet defused)
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# "boot" the bomb
if (RPi):
    setup_phases()
    check_phases()
#display the Pygame GUI -TBD
