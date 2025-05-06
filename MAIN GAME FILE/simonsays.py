#Simon Says Game  ----  Defuse the Bomb
#Khalil Smith 

#Importing the all the functions of each library 
import pygame
import RPi.GPIO as GPIO
import time
import sys

#Setting up the GPIO
GPIO.setmode(GPIO.BCM)

#Defining the GPIO pins that are connected to the wires
#This was taken from the bomb test 
WIRE_PINS = {
    "brown": 14,  #GPIO 14
    "red": 15,    #GPIO 15
    "orange": 18, #GPIO 18
    "yellow": 23, #GPIO 23
    "blue": 24    #GPIO 24
}

#Setup each pin as input with pull-up resistor
for pin in WIRE_PINS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Setting up the pygame
#This will be changed
pygame.init()
WIDTH, HEIGHT = 700, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simon Says: Raspberry Pi Edition")

#Colors that are associated with squid games 
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
RED = (255, 0, 0)
WIRES = {
    "blue": (0, 102, 204),
    "red": (204, 0, 0),
    "orange": (255, 128, 0),
    "brown": (139, 69, 19),
    "yellow": (255, 204, 0)
}

#Specifying the front to display on the GUI during the simon says game
try:
    font_name = pygame.font.match_font('ds-digital')
    if font_name is None:
        raise ValueError("DS-Digital not found")
    font = pygame.font.Font(font_name, 40)
    large_font = pygame.font.Font(font_name, 60)
except:
    #Fallback to guaranteed monospace
    fallback_font = pygame.font.match_font('monospace')
    font = pygame.font.Font(fallback_font, 40)
    large_font = pygame.font.Font(fallback_font, 60)

#This is the list of commands that would be used in the game 
commands = [
    "Disconnect the blue wire",
    "Simon says disconnect the red wire",
    "Simon says disconnect the orange wire",
    "Reconnect the red wire",
    "Simon says disconnect the brown wire",
    "Simon says reconnect the orange wire",
    "Reconnect the brown wire",
    "Simon says reconnect the red wire",
    "Disconnect the blue wire",
    "Simon says reconnect the brown wire",
    "Disconnect the yellow wire",
    "Simon says disconnect the yellow wire",
    "Simon says reconnect the yellow wire"
]

#This is the expected actions for the player to complete 
expected_actions = {
    "Simon says disconnect the red wire": ("red", "disconnect"),
    "Simon says disconnect the orange wire": ("orange", "disconnect"),
    "Simon says disconnect the brown wire": ("brown", "disconnect"),
    "Simon says reconnect the orange wire": ("orange", "reconnect"),
    "Simon says reconnect the red wire": ("red", "reconnect"),
    "Simon says reconnect the brown wire": ("brown", "reconnect"),
    "Simon says disconnect the yellow wire": ("yellow", "disconnect"),
    "Simon says reconnect the yellow wire": ("yellow", "reconnect")
}

#Creating a subroutine that will detect if the wires are connected or disconnected 
def read_wire_state(color):
    """Return 'connected' or 'disconnected' based on GPIO pin state."""
    pin = WIRE_PINS[color]
    return "connected" if GPIO.input(pin) else "disconnected"

#This layout will be changed, used to test the code
#Setting up the screen that will be displayed dueing the game 
def draw_game(command, timer):
    win.fill(BLACK)
    cmd_text = font.render(f"Command: {command}", True, PINK)
    win.blit(cmd_text, (50, 50))
    
    #Having a countdown timer that counts down for the player to complete the task 
    timer_text = font.render(f"Time left: {max(0, round(5 - timer))}s", True, PINK)
    win.blit(timer_text, (50, 100))

    # Draw wire status
    for i, color in enumerate(WIRES):
        rect = pygame.Rect(100 + i * 110, 300, 100, 50)
        pygame.draw.rect(win, WIRES[color], rect)
        #Connecting the colors of the wires to their state of conneted or disconnected 
        state = read_wire_state(color)
        label = font.render(f"{color.title()} ({state})", True, PINK)
        win.blit(label, (rect.x + 5, rect.y + 15))

    pygame.display.update()

#Creating a subroutine that is setting up the configuartions of displaying the messages throught the game 
def show_message(text, color=PINK):
    win.fill(BLACK)
    msg = large_font.render(text, True, color)
    win.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
    pygame.display.update()
    time.sleep(3)

#Creating a main subroutine that will run the game 
def main():
    try:
        #Implementing the clock control 
        clock = pygame.time.Clock()
        #For loop to loop through each of the commands 
        for command in commands:
            start_time = time.time()
            #Tracking if the correct task is complete 
            action_done = False

            while not action_done:
                #Keeping tack of the time that has passed for the player to complete the task 
                timer = time.time() - start_time
                draw_game(command, timer)
                
                #For loop for checking the current event
                for event in pygame.event.get():
                    #If statment for when the player doesn't complete the task or disconnected the wrong wire 
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        GPIO.cleanup()
                        sys.exit()

                #If statment for when the command has Simon syas in front of it 
                if command.startswith("Simon says"):
                    #Returning the action of the wire after each action 
                    wire, expected_action = expected_actions[command]
                    state = read_wire_state(wire)
                    #Making sure the state of the wire would be disconnected for the expected actions for the wire to be disconnected 
                    if expected_action == "disconnect" and state == "disconnected":
                        #Making sure the action was completed to move onto the next command 
                        action_done = True
                    #Making sure the state of the wire would be connected for the expected actions for the wire to be reconnected    
                    elif expected_action == "reconnect" and state == "connected":
                        #Making sure the action was completed to move onto the next command 
                        action_done = True
                else:
                    #For loop for any action that is completed without Simon Says in front of the command to fail 
                    for color in WIRE_PINS:
                        state = read_wire_state(color)
                        if state == "disconnected":
                            show_message("Simon didn't say! Game Over", color=RED)
                            GPIO.cleanup()
                            return
                #If statemnet for if the player did not complete the task within 5 seconds
                if timer > 5:
                    show_message("Too slow! Game Over", color=RED)
                    GPIO.cleanup()
                    return

                clock.tick(30)
        #This message will display when the player completes the correct task within 5 seconds 
        show_message("Congratulations, you may advance!", color=PINK)
    
    #Clearing the GPIO after every task 
    finally:
        GPIO.cleanup()

#Running the Simon Says game and calling the main function 
if __name__ == "__main__":
    main()