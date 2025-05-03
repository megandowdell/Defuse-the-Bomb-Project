import pygame
import sys
import random
from threading import Thread
from time import sleep
import board
from digitalio import DigitalInOut, Direction, Pull

# CONSTANTS
# References for scaling
dev_width, dev_height = 800, 700  # Resolution of development screen
reference_scale = (dev_width, dev_height)  # Used to scale based on development screen

# Colors
BEIGE = (232, 218, 189)
PURPLE = (67, 0, 117)
YELLOW = (234, 202, 87)
GREY = (149, 143, 137)

# Subroutine to scale the position of elements  
def scale_position(x, y, current_size):
    # Calculates the ratio between dimensions on both screens and scales the elements based on this ratio
    scale_x = current_size[0] / reference_scale[0]
    scale_y = current_size[1] / reference_scale[1]
    return int(x * scale_x), int(y * scale_y)

# Subroutine to scale the size/position of elements
def scale_rect(rect, current_size):
   # Calculates the ratio between size/position of elements on both screens and scales the elements based on this ratio
    scale_x = current_size[0] / reference_scale[0]
    scale_y = current_size[1] / reference_scale[1]
    
    new_x = int(rect.x * scale_x) # position
    new_y = int(rect.y * scale_y)
    new_width = int(rect.width * scale_x) # size
    new_height = int(rect.height * scale_y)
    
    return pygame.Rect(new_x, new_y, new_width, new_height)

# Subroutine to scale font size in elements
def scale_font_size(size, current_size):
    # Calculates the ratio between the font size on both screens and scales the elements based on this ratio
    font_scale = current_size[1] / reference_scale[1]
    return int(size * font_scale)

# Subroutine to wrap text within text box
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    
    # Adds word to line by checking to see if it fits. If it doesn't a new line is started.
    for word in words:
        line = current_line + [word]
        width = font.size(' '.join(line))[0]
        if width <= max_width:
            current_line = line
        else:
            if current_line:  
                lines.append(' '.join(current_line))
            current_line = [word]
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    return lines


class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
        # initially, the phase thread isn't running
        self._running = False
        # phases can have values (e.g., a pushbutton can be True or False, a keypad passphrase can be some string, etc)
        self._value = None

    # resets the phase's value
    def reset(self):
        self._value = None


class Button(PhaseThread):
    colors = [ "R", "G", "B" ]  # the button's possible colors

    def __init__(self, state, rgb, name="Button"):
        super().__init__(name)
        self._value = False
        # the pushbutton's state pin
        self._state = state
        # the pushbutton's LED pins
        self._rgb = rgb

    # runs the thread
    def run(self):
        self._running = True
        # initialize and index and counter to help iterate through the RGB colors
        rgb_index = 0
        rgb_counter = 0
        while (True):
            # set the LED to the current color
            self._rgb[0].value = False if Button.colors[rgb_index] == "R" else True
            self._rgb[1].value = False if Button.colors[rgb_index] == "G" else True
            self._rgb[2].value = False if Button.colors[rgb_index] == "B" else True
            # get the pushbutton's state
            self._value = self._state.value
            # increment the RGB counter
            rgb_counter += 1
            # switch to the next RGB color every 1s (10 * 0.1s = 1s)
            if (rgb_counter == 10):
                rgb_index = (rgb_index + 1) % len(Button.colors)
                rgb_counter = 0
            sleep(0.1)
        self._running = False

    def __str__(self):
        return "Pressed" if self._value else "Released"

















# INSTRUCTIONS
def show_redlightgreenlight_instructions_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Red Light Green Light Instructions")
    
    # Base font sizes for reference design
    base_title_size = 40
    base_button_size = 20
    base_text_size = 20
    
    # Scale font sizes
    title_size = scale_font_size(base_title_size, (WIDTH, HEIGHT))
    button_size = scale_font_size(base_button_size, (WIDTH, HEIGHT))
    text_size = scale_font_size(base_text_size, (WIDTH, HEIGHT))
    
    # Fonts
    title_font = pygame.font.Font("font2.otf", title_size)
    button_font = pygame.font.Font("font2.otf", button_size)
    text_font = pygame.font.Font("font5.otf", text_size)
    
    # Background Image
    bg_image = pygame.image.load("how_to_play.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    # Hopscotch-specific instructions
    welcome_text = [
        " In this challenge, ",
    ]
    
    # Hint
    hint_text = [
        "HINT:",
         " Don’t trust the flash, it tells a lie",
         " Her turning head decides who’ll die.",
    ]
    
    # Character options (buttons for 'Play')
    ag_items = ["Play"]  
    selected_index = 0
    clock = pygame.time.Clock()
    
    while True:
        # Draw the background
        screen.blit(bg_image, (0, 0))
        
        # Overlay for the how-to-play screen
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)  # More opaque for readability
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Draw title - scale from reference position
        title_text = title_font.render("Instructions", True, BEIGE)
        base_title_pos = (dev_width // 2, 30)
        title_x, title_y = scale_position(base_title_pos[0], base_title_pos[1], (WIDTH, HEIGHT))
        screen.blit(title_text, (title_x - title_text.get_width() // 2, title_y))
        
        # Reference info box dimensions and position
        base_info_box = pygame.Rect(50, 80, dev_width-100, 300)
        info_box_rect = scale_rect(base_info_box, (WIDTH, HEIGHT))
        
        # Draw info box
        info_box = pygame.Surface((info_box_rect.width, info_box_rect.height), pygame.SRCALPHA)
        info_box.fill((30, 30, 30, 180))  # Semi-transparent
        screen.blit(info_box, (info_box_rect.x, info_box_rect.y))
        pygame.draw.rect(screen, (100, 100, 150), info_box_rect, 2)
        
        # Draw intro text
        y_pos = info_box_rect.y + 10
        max_text_width = info_box_rect.width - 40
        
        for line in welcome_text:
            wrapped_lines = wrap_text(line, text_font, max_text_width)
            for wrapped_line in wrapped_lines:
                text_surf = text_font.render(wrapped_line, True, BEIGE)
                screen.blit(text_surf, (info_box_rect.x + 20, y_pos))
                y_pos += text_surf.get_height() + 5
                
                # Stop if we reach the bottom of the box
                if y_pos > info_box_rect.y + info_box_rect.height - text_surf.get_height():
                    break
            if y_pos > info_box_rect.y + info_box_rect.height - text_surf.get_height():
                break
        
        # Reference instructions box dimensions and position
        base_instructions_box = pygame.Rect(50, 400, dev_width-100, 180)
        instructions_box_rect = scale_rect(base_instructions_box, (WIDTH, HEIGHT))
        
        # Draw instructions box
        instructions_box = pygame.Surface((instructions_box_rect.width, instructions_box_rect.height), pygame.SRCALPHA)
        instructions_box.fill((30, 30, 30, 180))  
        screen.blit(instructions_box, (instructions_box_rect.x, instructions_box_rect.y))
        pygame.draw.rect(screen, (100, 100, 150), instructions_box_rect, 2)
        
        # Draw gameplay instructions
        y_pos = instructions_box_rect.y + 10
        
        for line in hint_text:
            wrapped_lines = wrap_text(line, text_font, max_text_width)
            for wrapped_line in wrapped_lines:
                text_surf = text_font.render(wrapped_line, True, YELLOW)
                screen.blit(text_surf, (instructions_box_rect.x + 20, y_pos))
                y_pos += text_surf.get_height() + 5
                
                if y_pos > instructions_box_rect.y + instructions_box_rect.height - text_surf.get_height():
                    break
            if y_pos > instructions_box_rect.y + instructions_box_rect.height - text_surf.get_height():
                break
        
        # 'Play' button - centered at bottom
        base_button_height = 40
        base_button_width = 200
        base_button_y = dev_height - 90
        
        # Scale button dimensions
        button_height = int(base_button_height * HEIGHT / dev_height)
        button_width = int(base_button_width * WIDTH / dev_width)
        
        # Center button
        button_x = (WIDTH - button_width) // 2
        button_y = int(base_button_y * HEIGHT / dev_height)
        
        button_rects = []
        name = ag_items[0]  # "Play"
        color = YELLOW
        bg_color = PURPLE
        
        box_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, bg_color, box_rect, border_radius=10)
        
        # Center text in button
        text_surface = button_font.render(name, True, color)
        text_x = box_rect.centerx - text_surface.get_width() // 2
        text_y = box_rect.centery - text_surface.get_height() // 2
        
        screen.blit(text_surface, (text_x, text_y))
        button_rects.append((box_rect, name))
        
        # Event Handling (key or mouse input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "Play"  # Return "Play" to start the game
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, item in button_rects:
                    if rect.collidepoint(mouse_pos):
                        return "Play"  # Return "Play" to start the game
        
        pygame.display.flip()
        clock.tick(60)


# GAME LOGIC
def show_redlightgreenlight_game_screen(screen):
    dev_width = 800
    dev_height = 600

    # Default vertical reference dimensions for the portrait mode
    portrait_width = 576
    portrait_height = 1024

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

    # First show the instructions screen
    result = show_redlightgreenlight_instructions_screen(screen)
    
    # Only proceed to the game if the player clicked "Play"
    if result == "Play":
        pygame.mixer.music.stop()
        pygame.mixer.music.load("fly_me.mp3")
        pygame.mixer.music.play(-1)
        # Get current screen dimensions
        def play_redlightgreenlight():
            WIDTH, HEIGHT = screen.get_size()
            #bg_image = pygame.image.load("redlightbg.png")
            #bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            pygame.display.set_caption("Red Light Green Light")
            clock = pygame.time.Clock()
            
            # Colors
            BG = (183, 246, 244)            # Background
            #SAFE = (0, 144, 57)          # Green for correct
            SAFE = (180, 38, 38)
            FAIL = (0, 144, 57)
            #FAIL = (180, 38, 38)         # Red for incorrect
            TEXT = (0, 0, 0)       # Light text
            RED = (255, 0, 0)            # Bright red
            GREEN = (0, 255, 0)          # Bright green
            
            #screen.blit(bg_image, (0, 0))
            
            # Scale font sizes based on screen dimensions
            base_font_size = 30
            base_big_font_size = 50
            font_size = int(base_font_size * WIDTH / dev_width)
            big_font_size = int(base_big_font_size * HEIGHT / dev_height)
            
            # Fonts
            
            FONT = pygame.font.Font("font1.otf", 16)
            BIG_FONT = pygame.font.Font("font1.otf", 26)
            
            bg_image = pygame.image.load("redlight_greenlight.png") 
            bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            screen.blit(bg_image, (0, 0))
            
            # Scale elements based on screen size
            button_size = int(200 * WIDTH / dev_width)
            margin = int(50 * WIDTH / dev_width)
            
            # Load doll images 
            doll_width = int(WIDTH * 0.5)  # 50% of screen width
            doll_height = int(doll_width * 1.8)  # aspect ratio of 1.8
            
            
            doll_red_img = pygame.image.load("redlightdoll.jpg")  # Doll facing player (red light)
            doll_green_img = pygame.image.load("greenlightdoll.jpg")  # Doll facing away (green light)
                
                # Scale images to the desired size
            doll_red_img = pygame.transform.scale(doll_red_img, (doll_width, doll_height))
            doll_green_img = pygame.transform.scale(doll_green_img, (doll_width, doll_height))
            
            
            # Game variables
            light_color = "red"
            game_time = 20  # seconds to win
            start_time = time.time()
            next_change_time = start_time  # Initialize for immediate first change
            #message = "Press the button ONLY when the light is GREEN"
            
            # Game state variables
            running = True
            game_over = False
            won = False
            
            while running:
                current_time = time.time()
                elapsed_time = current_time - start_time
                time_left = max(0, game_time - elapsed_time)
                screen.blit(bg_image, (0, 0))
                
                # Process events
                button_pressed = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and not game_over:
                            button_pressed = True
                        if event.key == pygame.K_r and game_over:
                            # Restart the game
                            return show_redlightgreenlight_game_screen(screen)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                        button_pressed = True
                
                # Check win condition (time elapsed)
                if time_left <= 0 and not game_over:
                    message = "Congratulations! You survived and won!"
                    game_over = True
                    won = True
                    pygame.display.flip()  # Make sure screen is updated
                    pygame.time.delay(1000)  # Show the winning state briefly
                    return "win"  # Return win result directly
                    
                
                # Change light color based on timing
                if current_time >= next_change_time and not game_over:
                    # Switch the light
                    light_color = "green" if light_color == "red" else "red"
                    if light_color == "green":
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("redlight.mp3")
                        pygame.mixer.music.play()
                    else:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("greenlight.mp3")
                        pygame.mixer.music.play()
                        
                         
                    # Set next change time (2-5 seconds)
                    next_change = random.uniform(2, 5)
                    next_change_time = current_time + next_change
                    message = f"THE LIGHT IS NOW {light_color.upper()}!"
                    print(f"THE LIGHT IS NOW {light_color.upper()}!")
                
                # Check button press
                if button_pressed and not game_over:
                    print("Button Pressed!")
                    if light_color == "green":
                        message = "Good move!"
                        #print("Good move!")
                    else:
                        message = "You pressed during RED! You lose!"
                        pygame.display.flip()
                        #pygame.time.delay(1000)
                        show_death_screen(screen)
                        return "lose"
                        #print("You pressed during RED! You lose!")
#                         game_over = True
#                         won = False
                
                # Draw doll image based on light color
                # Select the appropriate image
                doll_img = doll_red_img if light_color == "red" else doll_green_img
                
                # Position doll (centered)
                doll_x = WIDTH // 2 - doll_width // 2  # Center horizontally
                doll_y = HEIGHT // 2 - doll_height // 2  # Center vertically 
                screen.blit(doll_img, (doll_x, doll_y))
                
                # Draw color indicator in top right
                color = SAFE if light_color == "green" else FAIL
                pygame.draw.rect(screen, color, (
                    WIDTH - button_size - margin, 
                    margin, 
                    button_size, 
                    button_size))
                
                # Draw state and time display
                state_text = FONT.render(f"State: {light_color.upper()}", True, TEXT)
                screen.blit(state_text, (margin, margin))
                
                time_text = FONT.render(f"Time: {time_left:.1f}s", True, TEXT)
                screen.blit(time_text, (margin, margin + font_size + 10))  # Position under state text
                
                # Draw message
                message_text = FONT.render(message, True, TEXT)
                message_x = WIDTH // 2 - message_text.get_width() // 2
                # Position message near the bottom of the screen
                message_y = HEIGHT - int(120 * HEIGHT / dev_height)
                screen.blit(message_text, (message_x, message_y))
                
                # Draw instructions
                if not game_over:
                    instructions = FONT.render("Press SPACE or CLICK to move forward", True, TEXT)
                    instructions_x = WIDTH // 2 - instructions.get_width() // 2
                    # Position instructions at the bottom of the screen
                    instructions_y = HEIGHT - int(60 * HEIGHT / dev_height)
                    screen.blit(instructions, (instructions_x, instructions_y))
                else:
                    if "win":
                        return "win"
                        result = FONT.render("You won! Press R to restart", True, TEXT)
                    else:
                        return "lose"
                        result = FONT.render("You lost! Press R to restart", True, TEXT)
                    result_x = WIDTH // 2 - result.get_width() // 2
                    # Position result text at the bottom of the screen
                    result_y = HEIGHT - int(60 * HEIGHT / dev_height)
                    screen.blit(result, (result_x, result_y))
                
                # Update display
                pygame.display.flip()
                
                # Control frame rate
                clock.tick(60)
            
        #return "win" if win else "lose"
            #return result
        
        result = play_redlightgreenlight()
        #return "win" if win else "lose"
        return result
        pygame.display.flip()

def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Set up the display
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Red Light Green Light")
    
    # Initialize the GPIO for the button
    button_input = DigitalInOut(board.D4)
    button_RGB = [DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
    button_input.direction = Direction.INPUT
    button_input.pull = Pull.DOWN
    for pin in button_RGB:
        pin.direction = Direction.OUTPUT
        pin.value = True
    
    # Create button object and start its thread
    button = Button(button_input, button_RGB)
    button.start()
    
    # Set up global variables for the game functions to access
    global component_button_state
    global component_button_RGB
    component_button_state = button_input
    component_button_RGB = button_RGB
    
    # Show game screen
    try:
        result = show_redlightgreenlight_game_screen(screen)
        print(f"Game ended with result: {result}")
    except Exception as e:
        print(f"Error during gameplay: {e}")
    
    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


