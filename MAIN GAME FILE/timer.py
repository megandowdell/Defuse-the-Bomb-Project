import pygame
import sys # to exitgame
from pygame.locals import * # handles events, mouse/keyboard controls etc.
import os  # for environment variables
import random
import time
from threading import Thread
from time import sleep
import bomb
from bomb_configs import *
from bomb_phases import *
#import RPi.GPIO as GPIO  # Uncomment if using GPIO on Raspberry Pi

#from adafruit_matrixkeypad import Matrix_Keypad
#import RPi.GPIO as GPIO  # Uncomment if using GPIO on Raspberry Pi
#import board
#from digitalio import DigitalInOut, Direction, Pull

    
# if raspberry Pi is connected
if (RPi):
    # set up board
    i2c = board.I2C()
    component_7seg = Seg7x4(i2c)
    # set the 7-segment display brightness (0 -> dimmest; 1 -> brightest)
    component_7seg.brightness = 0.5
else:
    # For Pygame, component is None
    component_7seg = None
timer = Timer(component_7seg, 600)

timer.start()
