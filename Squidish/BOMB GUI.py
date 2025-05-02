import pygame
import sys # to exitgame
from pygame.locals import * # handles events, mouse/keyboard controls etc.
import os  # for environment variables


# Game audio
pygame.mixer.init()
pygame.mixer.music.load("pink_soldiers.mp3")
pygame.mixer.music.play(-1)  # -1 makes it loop indefinitely

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

# Define Character class
class Character:
    # Constructor
    def __init__(self, name, role, power):
        self._name = name
        self._role = role
        self._power = power
    
    # Getters
    def get_name(self):
        return self._name
    
    def get_role(self):
        return self._role
    
    def get_power(self):
        return self._power
    
    # Setters
    def set_name(self, new_name):
        self._name = new_name
    
    def set_role(self, new_role):
        self._role = new_role
        
    def set_power(self, new_power):
        self._power = new_power
    
    # Deleters
    def del_name(self):
        del self._name
    
    def del_role(self):
        del self._role
    
    def del_power(self):
        del self._power
    
    # Property methods
    name = property(get_name, set_name, del_name)
    role = property(get_role, set_role, del_role)
    power = property(get_power, set_power, del_power)

# Subroutine to display menu
def show_menu(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("SQUID-ISH GAMES")
    
    # Fixed Colors
    BEIGE = (232, 218, 189)
    PURPLE= (67, 0, 117)
    YELLOW = (234, 202, 87)
    GREY = (149, 143, 137)
    GREEN = (0, 213, 136)
    BLACK = (0, 0, 0)
    PINK = (255, 64, 119)
    
    # Fonts
    title_font = pygame.font.Font("font2.otf", 80)
    subtitle_font = pygame.font.Font("font1.otf", 45)
    menu_font = pygame.font.Font("font2.otf", 40)

    bg_image = pygame.image.load("menu.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    # Changed menu items to have four buttons as requested
    menu_items = ["Start", "About Game", "Meet Team", "Quit"]
    selected_index = 0
    clock = pygame.time.Clock() # Manages frame rate of game
    
    while True:
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(70)
        overlay.fill((30, 20, 20))
        screen.blit(overlay, (0, 0))
        
        # Draw title and subtitle
        title_text = title_font.render("Squid-ish Games", True, BEIGE)
        subtitle_text = subtitle_font.render("Error 404: Mercy Not Found", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 60))
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 150))
        
        button_rects = []
        for i in range(len(menu_items)):
            item = menu_items[i]
            is_selected = i == selected_index
            color = YELLOW if is_selected else BEIGE
            bg_color = PURPLE if is_selected else GREY
            text_surface = menu_font.render(item, True, color)
            x = WIDTH // 2 - text_surface.get_width() // 2
            y = 250 + i * 70
            box_rect = pygame.Rect(x - 20, y - 10, text_surface.get_width() + 40, text_surface.get_height() + 20)
            pygame.draw.rect(screen, bg_color, box_rect, border_radius=10)
            screen.blit(text_surface, (x, y))
            button_rects.append((box_rect, item))
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if menu_items[selected_index] == "Start":
                        # Changed to go to "Meet Team" instead of starting game directly
                        return "Meet Team"
                    elif menu_items[selected_index] == "About Game":
                        # Renamed from "How to Play" to "About Game"
                        return "About Game"
                    elif menu_items[selected_index] == "Meet Team":
                        return "Meet Team"
                    elif menu_items[selected_index] == "Quit":
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, item in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if item == "Start":
                            # Changed to go to "Meet Team" instead of starting game directly
                            return "Meet Team"
                        elif item == "About Game":
                            # Renamed from "How to Play" to "About Game"
                            return "About Game"
                        elif item == "Meet Team":
                            return "Meet Team"
                        elif item == "Quit":
                            pygame.quit()
                            sys.exit()
                            
        pygame.display.flip() # Updates screen when changes are made
        clock.tick(120) # 120 frames per second (FPS)

# Subroutine to display game instructions
# Renamed function from show_how_to_play_screen to show_about_game_screen
def show_about_game_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("About Game")
    
    # Colors
    BEIGE = (232, 218, 189)
    PURPLE= (67, 0, 117)
    YELLOW = (234, 202, 87)
    GREY = (149, 143, 137)
    BLACK = (0, 0, 0)
    
    # Fonts
    title_font = pygame.font.Font("font2.otf", 40)
    button_font = pygame.font.Font("font2.otf", 20)
    text_font = pygame.font.Font("font5.otf", 20)
    
    # Background Image
    bg_image = pygame.image.load("how_to_play.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    
    # Game intro text - moved from the intro screen to here
    welcome_text = [
        "WELCOME TO SQUID-ISH GAMES",
        "AHFGIYGSLU;HSJF",
        "SBGJSNDGONSKSDHSO;",
    ]
    
    # Additional gameplay instructions
    gameplay_text = [
        "HOW TO PLAY:",
        "1. Choose your character wisely - each has different power levels.",
        "2. Navigate through the territories by selecting directional buttons.",
        "3. Collect weapons to increase your power level.",
        "4. When encountering a Titan:",
        "   - If your power exceeds the Titan's: Attack to win (but you'll lose power equal to the Titan's strength)",
        "   - If the Titan's power exceeds yours: Retreat to gain power (attacking will result in game over)",
        "5. Reach The Flying Ship to win the game.",
        "",
        "Remember: Choose your battles wisely. Sometimes retreat is the best strategy!"
    ]
    
    # Character options (buttons for 'Back' and 'Continue')
    htp_items = ["Back", "Continue"]
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
        
        # Draw title
        title_text = title_font.render("About Game", True, BEIGE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # Draw intro text using the improved text wrapping
        info_box = pygame.Surface((WIDTH-100, 300), pygame.SRCALPHA)
        info_box.fill((30, 30, 30, 180))  # Semi-transparent
        screen.blit(info_box, (50, 80))
        pygame.draw.rect(screen, (100, 100, 150), (50, 80, WIDTH-100, 300), 2)
        
        y_pos = 90
        max_text_width = WIDTH - 140
        for line in welcome_text:
            wrapped_lines = wrap_text(line, text_font, max_text_width)
            for wrapped_line in wrapped_lines:
                text_surf = text_font.render(wrapped_line, True, BEIGE)
                screen.blit(text_surf, (70, y_pos))
                y_pos += 20
                if y_pos > 360:  # Limit to fit in the box
                    break
            if y_pos > 360:
                break
        
        # Draw gameplay instructions
        instructions_box = pygame.Surface((WIDTH-100, 180), pygame.SRCALPHA) # .SRCALPHA allows for transparent text boxes
        instructions_box.fill((30, 30, 30, 180))  
        screen.blit(instructions_box, (50, 400))
        pygame.draw.rect(screen, (100, 100, 150), (50, 400, WIDTH-100, 180), 2)
        
        y_pos = 410
        for line in gameplay_text:
            wrapped_lines = wrap_text(line, text_font, max_text_width)
            for wrapped_line in wrapped_lines:
                text_surf = text_font.render(wrapped_line, True, YELLOW)
                screen.blit(text_surf, (70, y_pos))
                y_pos += 20
                if y_pos > 570:  
                    break
            if y_pos > 570:
                break
        
        # 'Back" and 'Continue' buttons
        padding = 15
        button_widths = [button_font.size(name)[0] + 40 for name in htp_items]
        total_width = sum(button_widths) + (len(htp_items) - 1) * padding
        start_x = WIDTH // 2 - total_width // 2
        y = HEIGHT - 50
        button_rects = []
        
        for i in range(len(htp_items)):
            name = htp_items[i]
            is_selected = i == selected_index
            color = YELLOW if is_selected else BEIGE
            bg_color = PURPLE if is_selected else GREY
            text_surface = button_font.render(name, True, color)
            width = button_widths[i]
            height = text_surface.get_height() + 20
            box_rect = pygame.Rect(start_x, y, width, height)
            pygame.draw.rect(screen, bg_color, box_rect, border_radius=10)
            screen.blit(text_surface, (box_rect.x + 20, box_rect.y + 10))
            button_rects.append((box_rect, name))
            start_x += width + padding
        
        # Event Handling (key or mouse input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(htp_items)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(htp_items)
                elif event.key == pygame.K_RETURN:
                    if htp_items[selected_index] == "Back": # Back button returns to menu
                        return "Menu"  
                    elif htp_items[selected_index] == "Continue": # Continue button proceeds to game just as Start button would on the menu page
                        return "Meet Team"  # Changed to go to "Meet Team" instead of "Start"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, item in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if item == "Back":
                            return "Menu"  
                        elif item == "Continue":
                            return "Meet Team"  # Changed to go to "Meet Team" instead of "Start"
        
        pygame.display.flip()
        clock.tick(60)

# Subroutine to select characters
def character_selection(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Meet The Team")
    
    # Colors
    BEIGE = (232, 218, 189)
    PURPLE = (67, 0, 117)
    YELLOW = (234, 202, 87)
    GREY = (149, 143, 137)
    BLACK = (0, 0, 0)
    
    # Fonts
    title_font = pygame.font.Font("font1.otf", 50)
    char_font = pygame.font.Font("font5.otf", 30)
    desc_font = pygame.font.Font("font5.otf", 18)
    
    # Character options
    characters = [
        {"name": "Christa", "role": "Masked Officer", "power": 15000, 
         "description": "Humanity's strongest soldier. Exceptional combat skills with ODM gear. Stoic and disciplined."},
        {"name": "Khalil", "role": "Masked Officer", "power": 25000, 
         "description": "Brilliant Titan researcher who combines scientific curiosity with unorthodoz tactics to the battlefield. Eccentric but effective leader."},
        {"name": "Matt", "role": "Masked Officer", "power": 10000, 
         "description": "Visionary commander driven by truth, known for his bold strategies and unwavering resolve."},
        {"name": "Megan", "role": "Masked Officer", "power": 10000, 
         "description": "Visionary commander driven by truth, known for his bold strategies and unwavering resolve."}
        
    ]
    
    # Character images
    character_images = {}
    for character in characters:
        img = pygame.image.load(f"{character['name'].split()[0].lower()}.jpg")
        character_images[character['name']] = pygame.transform.scale(img, (150, 150))
        
        bg_image = pygame.image.load("character_select.jpg")
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    selected_index = 0
    clock = pygame.time.Clock()
    
    while True:
        # Background 
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((30, 30, 40))
        screen.blit(overlay, (0, 0))
      
        title_text = title_font.render("Meet The Team", True, BEIGE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
        
        char_rects = []
        char_cards_width = min(WIDTH - 100, len(characters) * 180)
        start_x = (WIDTH - char_cards_width) // 2
        
        for i, char in enumerate(characters): # enumerate() function adds a counter to an iterable and returns it as an enumerate object
            is_selected = i == selected_index
            # Character card background
            card_width = 160
            card_height = 300
            card_x = start_x + i * (char_cards_width // len(characters))
            card_y = HEIGHT // 2 - 150
            
            card_color = PURPLE if is_selected else GREY
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
            
            if is_selected:
                # Highlight selected card with a border
                pygame.draw.rect(screen, YELLOW, card_rect, 3, border_radius=10)
            
            # Character image
            char_img = character_images[char['name']]
            char_img_rect = char_img.get_rect(center=(card_x + card_width//2, card_y + 80))
            screen.blit(char_img, char_img_rect)
            
            # Character name
            name_text = char_font.render(char['name'], True, YELLOW if is_selected else BEIGE)
            screen.blit(name_text, (card_x + card_width//2 - name_text.get_width()//2, card_y + 165))
            
            # Character role
            role_text = desc_font.render(char['role'], True, BEIGE)
            screen.blit(role_text, (card_x + card_width//2 - role_text.get_width()//2, card_y + 200))
            
            # Character power
            power_text = desc_font.render(f"Power: {char['power']}", True, BEIGE)
            screen.blit(power_text, (card_x + card_width//2 - power_text.get_width()//2, card_y + 225))
            
            # Store rectangle for mouse interaction
            char_rects.append((card_rect, i))
        
        # Character description
        char_desc = characters[selected_index]['description']
        desc_lines = wrap_text(char_desc, desc_font, WIDTH - 200)
        
        desc_box = pygame.Surface((WIDTH - 100, 80), pygame.SRCALPHA)
        desc_box.fill((30, 30, 30, 200))
        screen.blit(desc_box, (50, HEIGHT - 150))
        pygame.draw.rect(screen, (100, 100, 150), (50, HEIGHT - 150, WIDTH - 100, 80), 2)
        
        for i, line in enumerate(desc_lines):
            desc_text = desc_font.render(line, True, BEIGE)
            screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT - 140 + i * 25))
        
        # Select button
        select_button = pygame.Rect(WIDTH//2 - 75, HEIGHT - 60, 150, 40)
        pygame.draw.rect(screen, BLACK, select_button, border_radius=10)
        select_text = char_font.render("Select", True, YELLOW)
        screen.blit(select_text, (select_button.centerx - select_text.get_width()//2, select_button.centery - select_text.get_height()//2))
        
        # Back button
        back_button = pygame.Rect(50, HEIGHT - 60, 100, 40)
        pygame.draw.rect(screen, GREY, back_button, border_radius=10)
        back_text = char_font.render("Back", True, BEIGE)
        screen.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(characters)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(characters)
                elif event.key == pygame.K_RETURN:
                    # Return the selected character
                    selected_char = characters[selected_index]
                    return Character(selected_char["name"], selected_char["role"], selected_char["power"])
                elif event.key == pygame.K_ESCAPE:
                    return "Menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Check for character card clicks
                for rect, idx in char_rects:
                    if rect.collidepoint(mouse_pos):
                        selected_index = idx
                
                # Check for select button click
                if select_button.collidepoint(mouse_pos):
                    selected_char = characters[selected_index]
                    return Character(selected_char["name"], selected_char["role"], selected_char["power"])
                
                # Check for back button click
                if back_button.collidepoint(mouse_pos):
                    return "Menu"
        
        pygame.display.flip()
        clock.tick(60)
        
# MAIN PROGRAM #
def main():
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption("Attack on Titan: Beyond the Walls")
    
    # Screen setup with toggle for different displays
    # Check if RPI_MODE environment variable is set
    if os.environ.get('RPI_MODE', 'False').lower() == 'true':
        # Running on Raspberry Pi with 576x1024 display
        WIDTH, HEIGHT = 576, 1024
        print("Running in Raspberry Pi mode (576x1024)")
    else:
        # Running on desktop with 800x700 display for testing
        WIDTH, HEIGHT = 800, 700
        print("Running in desktop mode (800x700)")
        
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Fonts
    default_font = pygame.font.SysFont("hpsimplifiedbdit", 18)
    title_font = pygame.font.SysFont("hpsimplifiedbdit", 36)
    
    # Main variables
    game_running = True # Controls game loop
    game_state = "menu" # Controls current state/screen of game
    
    # Main game loop
    while game_running:
        if game_state == "menu":
            menu_choice = show_menu(screen)
            if menu_choice == "Start":
                # Changed to go to "Meet Team" instead of "character_select"
                game_state = "Meet Team"
            elif menu_choice == "About Game":  # Renamed from "How to Play"
                game_state = "About Game"  # Renamed from "how_to_play"
            elif menu_choice == "Meet Team":
                game_state = "Meet Team"
        
        elif game_state == "About Game":  # Renamed from "how_to_play"
            # Changed function name to match the renamed function
            htp_choice = show_about_game_screen(screen)
            if htp_choice == "Menu":
                game_state = "menu"
            elif htp_choice == "Meet Team":  # Changed from "Start"
                game_state = "Meet Team"  # Changed from "character_select"
        
        elif game_state == "Meet Team":  # This now corresponds to "character_select"
            character = character_selection(screen)
            if character == "Menu":
                game_state = "menu"
            else:
                # After character selection, go back to menu for now
                game_state = "menu"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Set to true when testing RPi
    os.environ['RPI_MODE'] = 'TRUE'
    
    main()