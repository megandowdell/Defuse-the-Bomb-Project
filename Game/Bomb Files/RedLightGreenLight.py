import pygame
import time
import random
import sys

# RPi setup
try:
    import board
    from digitalio import DigitalInOut, Direction, Pull
    RPi = True
except ImportError:
    RPi = False

pygame.mixer.init()
greenmus = pygame.mixer.Sound("greenlight.wav")
redmus = pygame.mixer.Sound("redlight.wav")
song = pygame.mixer.Sound("flyme.mp3")

player = "Name"
# Real button and RGB LED (lets us run the program on laptop)
if RPi:
    component_button_state = DigitalInOut(board.D4)
    component_button_state.direction = Direction.INPUT
    component_button_state.pull = Pull.DOWN

    component_button_RGB = [DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
    for pin in component_button_RGB:
        pin.direction = Direction.OUTPUT
        pin.value = True
else:
    component_button_state = None
    component_button_RGB = None

# LED control
def set_led(color):
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
        for pin in component_button_RGB:
            pin.value = True

# Button press check
def check_button_press():
    return component_button_state.value if RPi else False

# Main game with GUI and distance
def red_light_green_light_game_gui():
    pygame.init()
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Red Light, Green Light")

    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 20)

    clock = pygame.time.Clock()
    running = True
    light_color = "red"
    set_led(light_color)

    game_time = 120
    start_time = time.time()

    player_distance = 0
    target_distance = 100
    game_over = False
    result_message = ""
    
    song.play(-1)

    


    def draw_text(text, y, color=(255, 255, 255)):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(WIDTH // 2, y))
        screen.blit(rendered, rect)

    try:
        current_light = None  # Track current state to detect change
        while running:
            screen.fill((0, 0, 0))
            elapsed = time.time() - start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    set_led("off")

            if not game_over and elapsed < game_time:
                draw_text(f"Time left: {int(game_time - elapsed)}", 40)
                draw_text(f"Distance: {player_distance} / {target_distance}", 100)

                if not hasattr(red_light_green_light_game_gui, "next_switch"):
                    red_light_green_light_game_gui.next_switch = time.time() + random.uniform(2, 5)

                if time.time() > red_light_green_light_game_gui.next_switch:
                    light_color = "green" if light_color == "red" else "red"
                    set_led(light_color)
                    red_light_green_light_game_gui.next_switch = time.time() + random.uniform(2, 5)

                draw_text(f"LIGHT: {light_color.upper()}", 180,
                          (0, 255, 0) if light_color == "green" else (255, 0, 0))
                
                if light_color != current_light:
                    current_light = light_color
                    if light_color == "green":
                        greenmus.play()
                    
                    if light_color == "red":
                        redmus.play()

                if check_button_press():
                    if light_color == "green":
                        player_distance += 1
                        time.sleep(0.4)
                    else:
                        draw_text(f"Player {player} has been eliminated.", 260, (255, 0, 0))
                        result_message = "Game's Over!"
                        game_over = True
                        set_led("off")
                        time.sleep(2)

                if player_distance >= target_distance:
                    result_message = "You beat right light green light!"
                    game_over = True
                    set_led("off")

            elif not game_over:
                result_message = f"Time's up! Player {player} has been eliminated."
                game_over = True
                set_led("off")

            if game_over:
                draw_text(result_message, 260)

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    running = False

            pygame.display.flip()
            clock.tick(120)

    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        set_led("off")
        pygame.quit()

if __name__ == "__main__":
    red_light_green_light_game_gui()
