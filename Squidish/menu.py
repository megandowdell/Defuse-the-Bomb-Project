####################################################################################################################
# IMPORTS
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
import RPi.GPIO as GPIO  # Uncomment if using GPIO on Raspberry Pi
####################################################################################################################
# MENU AUDIO
pygame.mixer.init()
pygame.mixer.music.load("pink_soldiers.mp3")
pygame.mixer.music.play(-1)  # -1 makes it loop indefinitely
####################################################################################################################
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
####################################################################################################################
# Class for Meet Team
class Team:
    # Constructor
    def __init__(self, name, status, role):
        self._name = name
        self._status = status
        self._role = role
    
    # Getters
    def get_name(self):
        return self._name
    def get_status(self):
        return self._status
    def get_role(self):
        return self._role
        
    # Setters
    def set_name(self, new_name):
        self._name = new_name
    def set_status(self, new_status):
        self._status = new_status 
    def set_role(self, new_role):
        self._status = new_role
        
    # Deleters
    def del_name(self):
        del self._name
    def del_status(self):
        del self._role
    def del_role(self):
        del self._role
    
    # Property Methods
    name = property(get_name, set_name, del_name)
    status = property(get_status, set_status, del_status)
    role = property(get_role, set_role, del_role)
#####################################################################################################################
# MENU
# Subroutine to display menu       
def show_menu_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("SQUID-ISH GAMES")
    
    # Font sizes based on reference design
    base_title_size = 45
    base_subtitle_size = 30
    base_menu_size = 35
    
    # Scale font sizes based on current screen
    title_size = scale_font_size(base_title_size, (WIDTH, HEIGHT))
    subtitle_size = scale_font_size(base_subtitle_size, (WIDTH, HEIGHT))
    menu_size = scale_font_size(base_menu_size, (WIDTH, HEIGHT))
    
    # Fonts
    title_font = pygame.font.Font("font2.otf", title_size)
    subtitle_font = pygame.font.Font("font1.otf", subtitle_size)
    menu_font = pygame.font.Font("font2.otf", menu_size)

    # Background
    bg_image = pygame.image.load("menu.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    # Menu Buttons
    menu_items = ["Start", "About Game", "Meet Team", "Quit"]
    selected_index = 0
    clock = pygame.time.Clock() # Manages frame rate of game
    
    while True:
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(70)
        overlay.fill((30, 20, 20))
        screen.blit(overlay, (0, 0))
        
        # Draw title and subtitle - scale from reference positions
        title_text = title_font.render("Squid-ish Games", True, BEIGE)
        subtitle_text = subtitle_font.render("Error 404: Mercy Not Found", True, YELLOW)
        
        # Reference positions 
        base_title_pos = (dev_width // 2, 60)
        base_subtitle_pos = (dev_width // 2, 150)
        
        # Scale positions to current screen
        title_x, title_y = scale_position(base_title_pos[0], base_title_pos[1], (WIDTH, HEIGHT))
        subtitle_x, subtitle_y = scale_position(base_subtitle_pos[0], base_subtitle_pos[1], (WIDTH, HEIGHT))
        
        # Center text at scaled positions
        screen.blit(title_text, (title_x - title_text.get_width() // 2, title_y))
        screen.blit(subtitle_text, (subtitle_x - subtitle_text.get_width() // 2, subtitle_y))
        
        
        button_rects = [] # Button array 
        
        # Reference menu button positions
        base_button_y_start = 250
        base_button_spacing = 70
        
        # Navigation of menu
        for i in range(len(menu_items)):
            item = menu_items[i]
            is_selected = i == selected_index
            color = YELLOW if is_selected else BEIGE
            bg_color = PURPLE if is_selected else GREY
            text_surface = menu_font.render(item, True, color)
            
            # Calculate reference position
            base_x = dev_width // 2
            base_y = base_button_y_start + i * base_button_spacing
            
            # Scale position to current screen
            x, y = scale_position(base_x, base_y, (WIDTH, HEIGHT))
            x = x - text_surface.get_width() // 2  # Center text
            
            # Scale padding based on text size
            padding_x = int(text_surface.get_height() * 0.4)
            padding_y = int(text_surface.get_height() * 0.3)
            
            box_rect = pygame.Rect(x - padding_x, y - padding_y, 
                                  text_surface.get_width() + (padding_x * 2), 
                                  text_surface.get_height() + (padding_y * 2))
            
            pygame.draw.rect(screen, bg_color, box_rect, border_radius=10)
            screen.blit(text_surface, (x, y))
            button_rects.append((box_rect, item))
        
        # Key and mouse functions
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
                        return "Meet Team"
                    elif menu_items[selected_index] == "About Game":
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
                            return "Start"
                        elif item == "About Game":
                            return "About Game"
                        elif item == "Meet Team":
                            return "Meet Team"
                        elif item == "Quit":
                            pygame.quit()
                            sys.exit()
                            
        pygame.display.flip() # Updates screen when changes are made
        clock.tick(120) # 120 frames per second (FPS)
        
####################################################################################################################
# ABOUT GAME
# Subroutine to display game instructions
def show_about_game_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("About Game")
    
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
    
    # Game intro text -TO DO
    introduction_text = [
        "WELCOME TO SQUID-ISH GAMES",
        "AHFGIYGSLU;HSJF",
        "SBGJSNDGONSKSDHSO;",
    ]
    
    # Additional gameplay instructions - TO DO 
    gameplay_text = [
        "HOW TO PLAY:",
        "1. Choose your character wisely - each has different description levels.",
        "2. Navigate through the territories by selecting directional buttons.",
        "3. Collect weapons to increase your description level.",
        "4. When encountering a Titan:",
        "   - If your description exceeds the Titan's: Attack to win (but you'll lose description equal to the Titan's strength)",
        "   - If the Titan's description exceeds yours: Retreat to gain description (attacking will result in game over)",
        "5. Reach The Flying Ship to win the game.",
        "",
        "Remember: Choose your battles wisely. Sometimes retreat is the best strategy!"
    ]
    
    # Character options (buttons for 'Back' and 'Continue')
    ag_items = ["Back", "Continue"]
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
        title_text = title_font.render("About Game", True, BEIGE)
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
        
        for line in introduction_text:
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
        
        # 'Back" and 'Continue' buttons - scale from reference positions
        base_button_height = 40
        base_button_widths = [200, 250]  # Approximate widths for Back and Continue
        base_button_y = dev_height - 90
        
        # Scale button dimensions
        button_height = int(base_button_height * HEIGHT / dev_height)
        button_widths = [int(w * WIDTH / dev_width) for w in base_button_widths]
        
        # Center buttons with appropriate spacing
        total_width = sum(button_widths) + int(WIDTH * 0.05)  # 5% of width as spacing
        start_x = (WIDTH - total_width) // 5
        button_y = int(base_button_y * HEIGHT / dev_height)
        
        button_rects = []
        for i in range(len(ag_items)):
            name = ag_items[i]
            is_selected = i == selected_index
            color = YELLOW if is_selected else BEIGE
            bg_color = PURPLE if is_selected else GREY
            
            # Calculate button position
            button_x = start_x + (0 if i == 0 else (button_widths[0] + int(WIDTH * 0.05)))
            width = button_widths[i]
            
            box_rect = pygame.Rect(button_x, button_y, width, button_height)
            pygame.draw.rect(screen, bg_color, box_rect, border_radius=10)
            
            # Center text in button
            text_surface = button_font.render(name, True, color)
            text_x = box_rect.centerx - text_surface.get_width() // 2
            text_y = box_rect.centery - text_surface.get_height() // 2
            
            screen.blit(text_surface, (text_x, text_y))
            button_rects.append((box_rect, name))
            
            # Update start_x for the next button
            start_x = button_x + width
        
        # Event Handling (key or mouse input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(ag_items)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(ag_items)
                elif event.key == pygame.K_RETURN:
                    if ag_items[selected_index] == "Back": # Back button returns to menu
                        return "Menu"  
                    elif ag_items[selected_index] == "Continue": # Continue button proceeds to game just as Start button would on the menu page
                        #random.choice(["Hopscotch"])
                        return random.choice(["Hopscotch"]) 
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, item in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if item == "Back":
                            return "Menu"  
                        elif item == "Continue":
                            return random.choice(["Hopscotch"])  
        pygame.display.flip()
        clock.tick(60)
####################################################################################################################
# MEET TEAM
# Subroutine to "Meet Team"
def show_meet_team(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Meet The Team")
    
    # Base font sizes
    base_title_size = 50
    base_char_size = 30
    base_desc_size = 18
    base_button_size = 20
    
    # Scale font sizes
    title_size = scale_font_size(base_title_size, (WIDTH, HEIGHT))
    char_size = scale_font_size(base_char_size, (WIDTH, HEIGHT))
    desc_size = scale_font_size(base_desc_size, (WIDTH, HEIGHT))
    button_size = scale_font_size(base_button_size, (WIDTH, HEIGHT))
    
    # Fonts
    title_font = pygame.font.Font("font1.otf", title_size)
    char_font = pygame.font.Font("font5.otf", char_size)
    desc_font = pygame.font.Font("font5.otf", desc_size)
    button_font = pygame.font.Font("font2.otf", button_size)
    
    # teammate options with descriptions
    teammates = [
        {"name": "Christa", "status": "Sophomore", "role": "Interface Architect", 
         "description": "Majors in Computer Science and minors in Physics and Mathematics. Responsible for our the game's..."},
        {"name": "Khalil", "status": "Junior", "role": "Sequence Strategist", 
         "description": "Majors in Computer Science and Chemistry. Responsible for our the game's..."},
        {"name": "Matt", "status": "Junior",  "role": "Motion Engineer", 
         "description": "Majors in Mathematics. Responsible for our the game's..."},
        {"name": "Megan", "status": "Junior", "role": "Grid Tactician", 
         "description": "Majors in Mathematics with Computer Science. Responsible for our the game's..."}
    ]
    
    # Reference image size
    base_img_size = 150
    img_size = int(base_img_size * min(WIDTH/dev_width, HEIGHT/dev_height))
    
    # teammate images - scale responsively
    teammate_images = {}
    for teammate in teammates:
        img = pygame.image.load(f"{teammate['name'].split()[0].lower()}.jpg")
        teammate_images[teammate['name']] = pygame.transform.scale(img, (img_size, img_size))
    
    # Background image
    bg_image = pygame.image.load("meet_team.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    
    selected_index = 0
    clock = pygame.time.Clock()
    
    # Detect if we're in portrait mode (like RPi)
    is_portrait = HEIGHT > WIDTH
    
    while True:
        # Background 
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((30, 30, 40))
        screen.blit(overlay, (0, 0))
      
        # Title - scale from reference position
        title_text = title_font.render("Meet The Team", True, BEIGE)
        base_title_pos = (dev_width // 2, 30)
        title_x, title_y = scale_position(base_title_pos[0], base_title_pos[1], (WIDTH, HEIGHT))
        screen.blit(title_text, (title_x - title_text.get_width() // 2, title_y))
        
        teammate_rects = []
        
        # Adaptive layout based on orientation
        if is_portrait:
            # Use a 2x2 grid for teammate cards in portrait mode
            cards_per_row = 2
            rows = (len(teammates) + cards_per_row - 1) // cards_per_row
            
            # Scale card dimensions
            card_width = int(WIDTH * 0.4)
            card_height = int(HEIGHT * 0.25)
            card_spacing = int(WIDTH * 0.05)
            
            for i, teammate in enumerate(teammates):
                row = i // cards_per_row
                col = i % cards_per_row
                
                # Calculate card position in grid
                card_x = (WIDTH - (card_width * cards_per_row + card_spacing * (cards_per_row - 1))) // 2
                card_x += col * (card_width + card_spacing)
                card_y = int(HEIGHT * 0.15) + row * (card_height + int(HEIGHT * 0.05))
                
                is_selected = i == selected_index
                
                # Draw card background
                card_color = PURPLE if is_selected else GREY
                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
                
                if is_selected:
                    pygame.draw.rect(screen, YELLOW, card_rect, 3, border_radius=10)
                
                # Draw teammate image
                teammate_img = teammate_images[teammate['name']]
                teammate_img_rect = teammate_img.get_rect(center=(card_x + card_width//2, card_y + card_height * 0.3))
                screen.blit(teammate_img, teammate_img_rect)
                
                # Draw teammate info 
                name_text = char_font.render(teammate['name'], True, YELLOW if is_selected else BEIGE)
                name_y = card_y + int(card_height * 0.6)
                screen.blit(name_text, (card_x + card_width//2 - name_text.get_width()//2, name_y))
                
                status_text = desc_font.render(teammate['status'], True, BEIGE)
                status_y = name_y + name_text.get_height() + 5
                screen.blit(status_text, (card_x + card_width//2 - status_text.get_width()//2, status_y))
                
                role_text = desc_font.render(teammate['role'], True, YELLOW)
                role_y = status_y + status_text.get_height() + 5
                screen.blit(role_text, (card_x + card_width//2 - role_text.get_width()//2, role_y))
                
                teammate_rects.append((card_rect, i))
        else:
            # In landscape mode, display cards in a row
            # Reference card dimensions and positions
            base_card_width = 160
            base_card_height = 300
            
            # Scale card dimensions
            card_width = int(base_card_width * WIDTH / dev_width)
            card_height = int(base_card_height * HEIGHT / dev_height)
            
            # Calculate total width needed for all cards with spacing
            card_spacing = int(WIDTH * 0.02)
            total_width = (card_width * len(teammates)) + (card_spacing * (len(teammates) - 1))
            start_x = (WIDTH - total_width) // 2
            
            # Reference vertical position
            base_card_y = dev_height // 2 - 150
            card_y = int(base_card_y * HEIGHT / dev_height)
            
            for i, teammate in enumerate(teammates):
                is_selected = i == selected_index
                
                # Calculate card position
                card_x = start_x + i * (card_width + card_spacing)
                
                # Draw card background
                card_color = PURPLE if is_selected else GREY
                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
                
                if is_selected:
                    pygame.draw.rect(screen, YELLOW, card_rect, 3, border_radius=10)
                
                # Draw teammate image
                teammate_img = teammate_images[teammate['name']]
                teammate_img_rect = teammate_img.get_rect(center=(card_x + card_width//2, card_y + int(card_height * 0.25)))
                screen.blit(teammate_img, teammate_img_rect)
                
                # Draw teammate info 
                name_text = char_font.render(teammate['name'], True, YELLOW if is_selected else BEIGE)
                name_y = card_y + int(card_height * 0.55)
                screen.blit(name_text, (card_x + card_width//2 - name_text.get_width()//2, name_y))
                
                status_text = desc_font.render(teammate['status'], True, BEIGE)
                status_y = name_y + name_text.get_height() + 5
                screen.blit(status_text, (card_x + card_width//2 - status_text.get_width()//2, status_y))
                
                role_text = desc_font.render(teammate['role'], True, YELLOW)
                role_y = status_y + status_text.get_height() + 5
                screen.blit(role_text, (card_x + card_width//2 - role_text.get_width()//2, role_y))
                
                teammate_rects.append((card_rect, i))
        
        # teammate description - displayed in a dedicated box at the bottom
        teammate_desc = teammates[selected_index]['description']
        
        # Reference description box dimensions and position
        base_desc_box = pygame.Rect(50, dev_height - 175, dev_width - 100, 80)
        desc_box_rect = scale_rect(base_desc_box, (WIDTH, HEIGHT))
        
        desc_box = pygame.Surface((desc_box_rect.width, desc_box_rect.height), pygame.SRCALPHA)
        desc_box.fill((30, 30, 30, 200))
        screen.blit(desc_box, (desc_box_rect.x, desc_box_rect.y))
        pygame.draw.rect(screen, (100, 100, 150), desc_box_rect, 2)
        
        # Draw description text
        max_desc_width = desc_box_rect.width - 40
        desc_lines = wrap_text(teammate_desc, desc_font, max_desc_width)
        
        for i, line in enumerate(desc_lines):
            if i >= 2:  # Limit to 2 lines for consistent display
                break
            desc_text = desc_font.render(line, True, BEIGE)
            text_x = WIDTH//2 - desc_text.get_width()//2
            text_y = desc_box_rect.y + 10 + i * (desc_text.get_height() + 5)
            screen.blit(desc_text, (text_x, text_y))
        
        # Reference button positions and dimensions
        base_back_button = pygame.Rect(50, dev_height - 70, 200, 40)
        
        # Scale buttons to current screen size
        back_button = scale_rect(base_back_button, (WIDTH, HEIGHT))
        
        # Draw Back button
        pygame.draw.rect(screen, GREY, back_button, border_radius=10)
        back_text = button_font.render("Back", True, BEIGE)
        back_text_x = back_button.centerx - back_text.get_width()//2
        back_text_y = back_button.centery - back_text.get_height()//2
        screen.blit(back_text, (back_text_x, back_text_y))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(teammates)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(teammates)
                elif event.key == pygame.K_RETURN:
                    # Return the selected teammate as a teammate object
                    selected_teammate = teammates[selected_index]
                    return teammate(selected_teammate["name"], selected_teammate["status"], selected_teammate["role"])
                elif event.key == pygame.K_ESCAPE:
                    return "Menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Check for teammate card clicks
                for rect, idx in teammate_rects:
                    if rect.collidepoint(mouse_pos):
                        selected_index = idx
            
                if back_button.collidepoint(mouse_pos):
                    return "Menu"
        
        pygame.display.flip()
        clock.tick(60)        
####################################################################################################################       
# HOPSCOTCH GAME
# TOGGLES

# # Only import GPIO stuff if on a Pi
# try:
#     import board
#     from digitalio import DigitalInOut, Direction, Pull
#     RPi = True
# except ImportError:
#     RPi = False
#     print("GPIO not available. Running in simulation mode.")
# 
# 
# # Base thread class for phases like toggles/wires/buttons

class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
        self._running = False
        self._value = None



 #       if RPi:
#for pin in self._pins:
#                 pin.direction = Direction.INPUT
#                 pin.pull = Pull.DOWN
# 
#     def reset(self):
#         self._value = None
# 
# 


toggle_pins = [DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]

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
                print(f"Toggles changed: {self._value}/{self._prev_value} - {self._state_changed}, {next(i for i, (a, b) in enumerate(zip(self._value, self._prev_value)) if a != b)}")
                sleep(0.1)
                
    def update_state(self):
        """Update toggle state and return True if the state changed."""
        new_state = "".join([str(int(pin.value)) for pin in self._pins])
 
        changed = new_state != self._value
        if changed:
             self._prev_value = self._value
             self._value = new_state
             self._state_changed = True
        
            
        return changed
        
    def all_down(self):
        """Returns True if all toggles are down (i.e., '0000')"""
        return self._value == "0000"

    def get_toggle_index(self):
        """Returns index (0–3) of the single flipped toggle.
         Only works when exactly one toggle is up (i.e., value is '0100', etc).
         """
        pass
        # return None
 
    def has_changed(self):
        """Checks if toggles changed since last time."""
        if self._state_changed:
            self._state_changed = False
            return True
            
        return False
 
    def __str__(self):
        """Show state as binary and its decimal equivalent."""
        return f"{self._value}/{int(self._value, 2)}"

# Create and start the toggle monitor
toggles = Toggles(toggle_pins)

 
# Test code for local Pi testing (doesn't affect real game logic)
    # Set up pins (GPIO 12, 16, 20, 21 for 4 toggles)
print("Monitoring toggles... flip exactly ONE toggle to simulate input.")
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




# INSTRUCTIONS 
def show_hopscotch_instructions_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Hopscotch Instructions")
    
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
    
    # Hopscotch instructions
    introduction_text = [
        "In this challenge, you'll move forward by selecting the correct tile in each row using the toggles. Each row has more than one safe tile but choose carefully. If you step on the wrong tile, you will lose a life. You have ten lives to complete a total of 10 levels. After each mistake, the path stays the same so remember where you went wrong and try again.",
        "Good luck and most importantly, don't fall!"
    ]
    
    # Hint
    hint_text = [
        "HINT:",
        "The path repeats, though lives do not.",
        "Track each fall, or lose the plot."
    ]

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
        
        for line in introduction_text:
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
def show_hopscotch_game_screen(screen):
    # First show the instructions screen
    result = show_hopscotch_instructions_screen(screen)
    
    if result == "Play":
        toggles.start()
        pygame.mixer.music.stop()
        pygame.mixer.music.load("round_round.mp3")
        pygame.mixer.music.play(-1)
        
        # Get current screen dimensions
        WIDTH, HEIGHT = screen.get_size()
        pygame.display.set_caption("Hopscotch")
        clock = pygame.time.Clock()

        # Colors
        BG = (10, 10, 10)            # Background
        SAFE = (0, 144, 57)          # Green for correct tile
        FAIL = (180, 38, 38)         # Red for incorrect choice
        TEXT = (240, 240, 240)       # Light text
        DIM = (80, 80, 80)           # Gray for inactive rows

        # Tile colors - one for each column (A, B, C, D)
        TILE_A_PINK = (255, 64, 119)  
        TILE_B_BLUE = (0, 194, 176)  
        TILE_C_GREEN = (134, 233, 0)  
        TILE_D_YELLOW = (233, 219, 0) 

        # Create a list for easy reference
        TILE_COLORS = [TILE_A_PINK, TILE_B_BLUE, TILE_C_GREEN, TILE_D_YELLOW]
        
        # Scale font sizes based on screen dimensions
        base_font_size = 30
        base_big_font_size = 50
        font_size = scale_font_size(base_font_size, (WIDTH, HEIGHT))
        big_font_size = scale_font_size(base_big_font_size, (WIDTH, HEIGHT))
        
        # Fonts
        FONT = pygame.font.Font("font1.otf", 30)
        BIG_FONT = pygame.font.Font("font1.otf", 50)

        # Layout Configuration - scale based on screen size
        base_tile_width = 100
        base_tile_height = 60
        base_tile_gap = 40
        
        # Scale based on screen width
        TILE_WIDTH = int(base_tile_width * WIDTH / dev_width)
        TILE_HEIGHT = int(base_tile_height * HEIGHT / dev_height)
        TILE_GAP = int(base_tile_gap * WIDTH / dev_width)
        
        ROWS = 10           # Total levels
        COLS = 4           # Columns (A–D)
        VISIBLE_ROWS = 5

        # Tile Generator
        def generate_board(successes_per_row=4):
            board = []
            for _ in range(ROWS):
                safe = random.sample(range(COLS), successes_per_row)
                board.append(safe)  # Each row has 1 correct tile (change for more)
            return board
        
        # Generate a new row for the board
        def generate_new_row(successes_per_row=2):
            return random.sample(range(COLS), successes_per_row)

        # Positioning of tiles
        def get_tile_rect(row, col):
            row_height = TILE_HEIGHT + 60
            x = (WIDTH - (COLS * TILE_WIDTH + (COLS - 1) * TILE_GAP)) // 2 + col * (TILE_WIDTH + TILE_GAP)
            y = 150 + row * row_height  
            return pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)

       # Drawing tiles
        def draw_board(board, current_row, lives, rows_cleared=0, animation_offset=0, selected_tile=None, show_correct=False):
            screen.fill(BG)
            
            # Draw only visible rows
            for visible_row in range(min(VISIBLE_ROWS, len(board))):
                actual_row = visible_row + current_row
                if actual_row >= len(board):
                    continue
                    
                for col in range(COLS):
                    # Calculate position with animation offset
                    base_rect = get_tile_rect(visible_row, col)
                    # Adjust y position for animation
                    rect = pygame.Rect(base_rect.x, base_rect.y + animation_offset, base_rect.width, base_rect.height)
                    
                    # Determine tile color based on various conditions
                    if visible_row == 0:  # First visible row (current row)
                        # For current row - use the column's designated color
                        if show_correct and col in board[actual_row]:
                            color = SAFE  # Show safe tiles when appropriate
                        else:
                            color = TILE_COLORS[col]  # Use the specific color for each column
                    else:
                        # For future rows - use dimmed version of the column's color
                        base_color = TILE_COLORS[col]
                        color = tuple(max(c // 2, 0) for c in base_color)  #  list comprehension that processes each component of an RGB color tuple to create a darker version
                        
                    # Draw the tile with appropriate color
                    pygame.draw.rect(screen, color, rect)

                    # Add the letter label
                    label = FONT.render(chr(65 + col), True, TEXT)
                    screen.blit(label, (rect.x + TILE_WIDTH//2 - 10, rect.y + 15))

            # Level display
            level_text = FONT.render(f"Level: {rows_cleared + 1}/{ROWS}", True, TEXT)
            screen.blit(level_text, (20, 20))

            # Lives display 
            lives_text = FONT.render(f"Lives: {lives}", True, TEXT)
            screen.blit(lives_text, (20, 60))  # Position under level text
            pygame.display.flip()

        def animate_row(board, current_row, lives, rows_cleared, duration=500):
            start_time = pygame.time.get_ticks() # Counts
            row_height = TILE_HEIGHT + 60
            
            # Animate rows moving up
            while True:
                current_time = pygame.time.get_ticks() # Calculates how many milliseconds have passed since the animation began
                elapsed = current_time - start_time 
                
                if elapsed >= duration: # stops animation until completed (i.e all tiles cleared)
                    break
                    
                progress = elapsed / duration #Converts the elapsed time into a normalized value between 0.0 and 1.0
                offset = -int(row_height * progress)  # Negative offset to move up
                
                draw_board(board, current_row, lives, rows_cleared, offset)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                        
                clock.tick(60)
            
            # Move to next row in the board 
            current_row += 1
            draw_board(board, current_row, lives, rows_cleared)
            return current_row

        # Play a Turn (for GPIO or internal use)
        def play_turn(board, current_row, selected_col, lives, rows_cleared):
            """
            Processes a move based on selected column (0-3).
            Used by Raspberry Pi GPIO toggles.
            Returns: updated row index, and "win"/"lose"/None
            """
            if selected_col in board[current_row]:
                # Show correct tile briefly
                draw_board(board, current_row, lives, rows_cleared, 0, None, True)
                pygame.display.flip()
                pygame.time.delay(300)  
            
                rows_cleared += 1
                current_row = animate_row(board, current_row, lives, rows_cleared)
        
                result = None if rows_cleared < ROWS else "win"
            else:
                # Show failed tile
                tile_rect = get_tile_rect(0, selected_col)
                pygame.draw.rect(screen, FAIL, tile_rect)
        
                # Redraw the letter label
                label = FONT.render(chr(65 + selected_col), True, TEXT)
                screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))
        
                pygame.display.flip()
                pygame.time.delay(800)
        
                lives -= 1
                current_row = 0
                rows_cleared = 0
                result = "lose" if lives == 0 else None

            draw_board(board, current_row, lives, rows_cleared)
            return current_row, lives, rows_cleared, result

        # Optional GPIO Reset (not needed in GUI testing)
        def wait_for_toggle_reset(toggle_pins):
            """
            Pauses game until all toggles are back to "down".
            Use this in Raspberry Pi version only.
            """
            print("Flip all toggles down to continue...")

            while True:
                all_down = all(GPIO.input(pin) == 0 for pin in toggle_pins)
                if all_down:
                    break
                time.sleep(0.05)

        # Main Game (for local testing)
        def play_game():
            board = generate_board(successes_per_row=2)  # Create board once
            current_row = 0
            lives = 5  # Start with 5 lives
        
            while True:
                draw_board(board, current_row, lives)  # Now we also pass lives to draw
                # Check for a toggle change (user flips one switch)
                if toggles._state_changed:
                    # Get the index of the flipped toggle (0–3)
                    selected_col = next(i for i, (a, b) in enumerate(zip(toggles._value, toggles._prev_value)) if a != b)
                    print(f"Selected Col {selected_col}")
                    print(f"boardState  {board[current_row]}")
                    print(f"current Row  {current_row}")
        
                    if selected_col is not None:
                        # Check if selected toggle is correct for current row
                        if selected_col in board[current_row]:
                            current_row += 1
                            if current_row == ROWS:
                                print("WIN")
                                return True
                        else:
                            lives -= 1
                            current_row = 0
                            pygame.draw.rect(screen, FAIL, tile_rect)
                            print("WRONG TILE — Strike!")
                            if lives == 0:
                                print("BOOM!")
                                return False
        
                        # Wait for toggles to reset (all back to down/off)
                        #print("Waiting for reset...")
                        #while not toggles.all_down():
                         #   sleep(0.05)
                    toggles._state_changed = False
                clock.tick(60)

        won = play_game()
        return result
        screen.fill(BG)
        pygame.display.flip()
####################################################################################################################
# TIC TAC TOE
# KEYPAD



























# INSTRUCTIONS
def show_tictactoe_instructions_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Tic Tac Toe Instructions")
    
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
    
    # instructions
    introduction_text = [
        "Welcome to the Tic Tac Toe game! In this challenge, you'll face off against the computer in a game of classic Tic Tac Toe. You must win 3 rounds to pass. Use the keypad numbers to place your X, either vertically, horizontally or diagonally, to form a line of three before the computer can. Good luck and think ahead. ",
    ]
    
    # Hint
    hint_text = [
        "HINT:",
        "It guards the line, not claims it.",
        "Win by force, not patience."
    ]
    
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
        
        for line in introduction_text:
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
def show_tictactoe_game_screen(screen):
    # First show the instructions screen
    result = show_tictactoe_instructions_screen(screen)
    
    # Only proceed to the game if the player clicked "Play"
    if result == "Play":
        pygame.mixer.music.stop()
        pygame.mixer.music.load("way_forward.mp3")
        pygame.mixer.music.play(-1)
        
        # Window setup
        WIDTH, HEIGHT = 288, 512  # Dimensions of game window for tall screens
        screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create window
        pygame.display.set_caption('Tic Tac Toe')  # Window title

        # Game board setup
        BOARD_ROWS = 3
        BOARD_COLS = 3
        BOARD_SIZE = min(WIDTH, HEIGHT)  # Ensure square board
        SQUARE_SIZE = BOARD_SIZE // BOARD_COLS
        BOARD_TOP = (HEIGHT - BOARD_SIZE) // 2  # Center board vertically

        # Line and shape settings
        LINE_WIDTH = 15
        CIRCLE_RADIUS = SQUARE_SIZE // 3
        CIRCLE_WIDTH = 15
        CROSS_WIDTH = 25
        SPACE = SQUARE_SIZE // 4  # Spacing inside squares for shapes

        # Colors
        BG_COLOR = (170, 132, 210)
        LINE_COLOR = (206, 183, 231) 
        #BG_COLOR = (28, 170, 156)       # Background
        #LINE_COLOR = (23, 145, 135)     # Grid lines
        # CIRCLE_COLOR = (239, 231, 200)  # CPU's move
        CIRCLE_COLOR = (255, 255, 255)
        CROSS_COLOR = (66, 66, 66)      # Player's move
        WIN_LINE_COLOR = (255, 50, 50)  # Winning line

        # Fonts
        SCORE_FONT = pygame.font.Font("font1.otf", 26)
        ROUND_FONT = pygame.font.Font("font1.otf", 38)
        MESSAGE_FONT = pygame.font.Font("font1.otf", 30)

        # Draws the grid lines for the board
        def draw_lines():
            screen.fill(BG_COLOR)  # Fill screen with background color
            for row in range(1, BOARD_ROWS):
                pygame.draw.line(screen, LINE_COLOR, (0, row * SQUARE_SIZE + BOARD_TOP), (WIDTH, row * SQUARE_SIZE + BOARD_TOP), LINE_WIDTH)
            for col in range(1, BOARD_COLS):
                pygame.draw.line(screen, LINE_COLOR, (col * SQUARE_SIZE, BOARD_TOP), (col * SQUARE_SIZE, BOARD_TOP + BOARD_SIZE), LINE_WIDTH)

        # Draw X (player) and O (CPU) based on board values
        def draw_figures(board):
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if board[row][col] == 1:  # Player move
                        pygame.draw.line(screen, CROSS_COLOR, 
                                         (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE + BOARD_TOP),
                                         (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE + BOARD_TOP),
                                         CROSS_WIDTH)
                        pygame.draw.line(screen, CROSS_COLOR,
                                         (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE + BOARD_TOP),
                                         (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE + BOARD_TOP),
                                         CROSS_WIDTH)
                    elif board[row][col] == 2:  # CPU move
                        pygame.draw.circle(screen, CIRCLE_COLOR,
                                           (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_TOP),
                                           CIRCLE_RADIUS, CIRCLE_WIDTH)

        # Place a move on the board
        def mark_square(board, row, col, player):
            board[row][col] = player

        # Check if a square is empty
        def available_square(board, row, col):
            return board[row][col] == 0

        # Check if the board is completely filled
        def is_board_full(board):
            return all(cell != 0 for row in board for cell in row)

        # Check win condition for a player and return coordinates for winning line to be drawn
        def check_win(board, player):
            # Check rows
            for row in range(BOARD_ROWS):
                if all(board[row][col] == player for col in range(BOARD_COLS)):
                    y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_TOP
                    return True, [(0, y), (WIDTH, y)]
            # Check columns
            for col in range(BOARD_COLS):
                if all(board[row][col] == player for row in range(BOARD_ROWS)):
                    x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    return True, [(x, BOARD_TOP), (x, BOARD_TOP + BOARD_SIZE)]
            # Check diagonals
            if all(board[i][i] == player for i in range(BOARD_ROWS)):
                return True, [(SPACE, BOARD_TOP + SPACE), (WIDTH - SPACE, BOARD_TOP + BOARD_SIZE - SPACE)]
            if all(board[i][BOARD_COLS - 1 - i] == player for i in range(BOARD_ROWS)):
                return True, [(WIDTH - SPACE, BOARD_TOP + SPACE), (SPACE, BOARD_TOP + BOARD_SIZE - SPACE)]
            return False, None

        # Draw winning line
        def draw_win_line(line_coords):
            pygame.draw.line(screen, WIN_LINE_COLOR, line_coords[0], line_coords[1], LINE_WIDTH)

        # Check if player has an immediate win threat
        def check_player_win_threat(board):
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if board[row][col] == 0:
                        board[row][col] = 1
                        win, _ = check_win(board, 1)
                        board[row][col] = 0
                        if win:
                            return row, col
            return None, None

        # Random move by CPU, but block player if they can win
        def computer_move(board):
            block = check_player_win_threat(board)
            if block[0] is not None:
                return block
            available = [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] == 0]
            return random.choice(available) if available else (None, None)

        # Display the round number and score on screen
        def show_score(round_num, player_score, cpu_score):
            score_text = SCORE_FONT.render(f"Round {round_num}  You: {player_score}  CPU: {cpu_score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

        # Show message at end of each round
        def show_round_result(result):
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            if result == "player":
                text = MESSAGE_FONT.render("You won this round!", True, (255, 255, 255))
            elif result == "cpu":
                text = MESSAGE_FONT.render("CPU won this round!", True, (255, 255, 255))
            else:
                text = MESSAGE_FONT.render("It's a tie!", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(2000)

        # Show transition between rounds
        def show_next_round(round_num):
            screen.fill((0, 0, 0))
            text = ROUND_FONT.render(f"Round {round_num}!", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(1000)

        # Main game function
        def play_tic_tac_toe():
            player_score = 0
            cpu_score = 0
            round_number = 1

            while True:
                # Empty board: 0 = empty, 1 = player, 2 = cpu
                board = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
                draw_lines()
                show_score(round_number, player_score, cpu_score)
                pygame.display.update()

                player = 1  # Player goes first
                running = True
                winner = None
                win_line = None
                game_over = False

                # Main game loop
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        # Player's turn (left click)
                        if player == 1 and event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                            mouseX = event.pos[0]
                            mouseY = event.pos[1]
                            clicked_row = (mouseY - BOARD_TOP) // SQUARE_SIZE
                            clicked_col = mouseX // SQUARE_SIZE
                            if 0 <= clicked_row < BOARD_ROWS and 0 <= clicked_col < BOARD_COLS:  # Valid click
                                if available_square(board, clicked_row, clicked_col):
                                    mark_square(board, clicked_row, clicked_col, 1)
                                    win, win_line = check_win(board, 1)
                                    if win:
                                        player_score += 1
                                        winner = "player"
                                        game_over = True
                                    elif is_board_full(board):
                                        winner = "tie"
                                        game_over = True
                                    else:
                                        player = 2  # Switch to CPU turn

                    # CPU turn
                    if player == 2 and not game_over:
                        pygame.time.delay(75)
                        row, col = computer_move(board)
                        if row is not None and col is not None:
                            mark_square(board, row, col, 2)
                            win, win_line = check_win(board, 2)
                            if win:
                                cpu_score += 1
                                winner = "cpu"
                                game_over = True
                            elif is_board_full(board):
                                winner = "tie"
                                game_over = True
                            else:
                                player = 1  # Switch to player turn

                    # Draw shapes and update score
                    draw_lines()
                    draw_figures(board)
                    show_score(round_number, player_score, cpu_score)

                    # Draw winning line if needed
                    if win_line:
                        draw_win_line(win_line)

                    pygame.display.update()

                    # Handle end of round
                    if game_over:
                        pygame.time.delay(1000)
                        show_round_result(winner)
                        running = False

                # End game if someone wins 3 rounds
                if player_score == 3:
                    return "win"
                elif cpu_score == 3:
                    show_death_screen(screen)
                    return "lose"

                # Prepare for next round
                round_number += 1
                show_next_round(round_number)
           

    result = play_tic_tac_toe()
    return result
    pygame.display.flip()
####################################################################################################################
# RED LIGHT GREEN LIGHT
# BUTTON





















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
            
            
            doll_red_img = pygame.image.load("redlightdollZ.png")  # Doll facing player (red light)
            doll_green_img = pygame.image.load("greenlightdollZ.png")  # Doll facing away (green light)
                
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
                        print("Good move!")
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

















####################################################################################################################
# SIMON SAYS
# WIRES





# INSTRUCTIONS
# def show_redlightgreenlight_instructions_screen(screen):
#     WIDTH, HEIGHT = screen.get_size()
#     pygame.display.set_caption("Simon Says Instructions")
#     
#     # Base font sizes for reference design
#     base_title_size = 40
#     base_button_size = 20
#     base_text_size = 20
#     
#     # Scale font sizes
#     title_size = scale_font_size(base_title_size, (WIDTH, HEIGHT))
#     button_size = scale_font_size(base_button_size, (WIDTH, HEIGHT))
#     text_size = scale_font_size(base_text_size, (WIDTH, HEIGHT))
#     
#     # Fonts
#     title_font = pygame.font.Font("font2.otf", title_size)
#     button_font = pygame.font.Font("font2.otf", button_size)
#     text_font = pygame.font.Font("font5.otf", text_size)
#     
#     # Background Image
#     bg_image = pygame.image.load("how_to_play.jpg")
#     bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
#     
#     # Hopscotch-specific instructions
#     welcome_text = [
#         "In this challenge, "
#     ]
#     
#     # Additional gameplay instructions
#     hint_text = [
#         "HINT:",
#         "The colors come, but not in haste."
#         "Rush the wires, your turn’s a waste."
#     ]
#     
#     # Character options (buttons for 'Play')
#     ag_items = ["Play"] 
#     selected_index = 0
#     clock = pygame.time.Clock()
#     
#     while True:
#         # Draw the background
#         screen.blit(bg_image, (0, 0))
#         
#         # Overlay for the how-to-play screen
#         overlay = pygame.Surface((WIDTH, HEIGHT))
#         overlay.set_alpha(150)  # More opaque for readability
#         overlay.fill((20, 20, 30))
#         screen.blit(overlay, (0, 0))
#         
#         # Draw title - scale from reference position
#         title_text = title_font.render("Instructions", True, BEIGE)
#         base_title_pos = (dev_width // 2, 30)
#         title_x, title_y = scale_position(base_title_pos[0], base_title_pos[1], (WIDTH, HEIGHT))
#         screen.blit(title_text, (title_x - title_text.get_width() // 2, title_y))
#         
#         # Reference info box dimensions and position
#         base_info_box = pygame.Rect(50, 80, dev_width-100, 300)
#         info_box_rect = scale_rect(base_info_box, (WIDTH, HEIGHT))
#         
#         # Draw info box
#         info_box = pygame.Surface((info_box_rect.width, info_box_rect.height), pygame.SRCALPHA)
#         info_box.fill((30, 30, 30, 180))  # Semi-transparent
#         screen.blit(info_box, (info_box_rect.x, info_box_rect.y))
#         pygame.draw.rect(screen, (100, 100, 150), info_box_rect, 2)
#         
#         # Draw intro text
#         y_pos = info_box_rect.y + 10
#         max_text_width = info_box_rect.width - 40
#         
#         for line in welcome_text:
#             wrapped_lines = wrap_text(line, text_font, max_text_width)
#             for wrapped_line in wrapped_lines:
#                 text_surf = text_font.render(wrapped_line, True, BEIGE)
#                 screen.blit(text_surf, (info_box_rect.x + 20, y_pos))
#                 y_pos += text_surf.get_height() + 5
#                 
#                 # Stop if we reach the bottom of the box
#                 if y_pos > info_box_rect.y + info_box_rect.height - text_surf.get_height():
#                     break
#             if y_pos > info_box_rect.y + info_box_rect.height - text_surf.get_height():
#                 break
#         
#         # Reference instructions box dimensions and position
#         base_instructions_box = pygame.Rect(50, 400, dev_width-100, 180)
#         instructions_box_rect = scale_rect(base_instructions_box, (WIDTH, HEIGHT))
#         
#         # Draw instructions box
#         instructions_box = pygame.Surface((instructions_box_rect.width, instructions_box_rect.height), pygame.SRCALPHA)
#         instructions_box.fill((30, 30, 30, 180))  
#         screen.blit(instructions_box, (instructions_box_rect.x, instructions_box_rect.y))
#         pygame.draw.rect(screen, (100, 100, 150), instructions_box_rect, 2)
#         
#         # Draw gameplay instructions
#         y_pos = instructions_box_rect.y + 10
#         
#         for line in hint_text:
#             wrapped_lines = wrap_text(line, text_font, max_text_width)
#             for wrapped_line in wrapped_lines:
#                 text_surf = text_font.render(wrapped_line, True, YELLOW)
#                 screen.blit(text_surf, (instructions_box_rect.x + 20, y_pos))
#                 y_pos += text_surf.get_height() + 5
#                 
#                 if y_pos > instructions_box_rect.y + instructions_box_rect.height - text_surf.get_height():
#                     break
#             if y_pos > instructions_box_rect.y + instructions_box_rect.height - text_surf.get_height():
#                 break
#         
#         # 'Play' button - centered at bottom
#         base_button_height = 40
#         base_button_width = 200
#         base_button_y = dev_height - 90
#         
#         # Scale button dimensions
#         button_height = int(base_button_height * HEIGHT / dev_height)
#         button_width = int(base_button_width * WIDTH / dev_width)
#         
#         # Center button
#         button_x = (WIDTH - button_width) // 2
#         button_y = int(base_button_y * HEIGHT / dev_height)
#         
#         button_rects = []
#         name = ag_items[0]  # "Play"
#         color = YELLOW
#         bg_color = PURPLE
#         
#         box_rect = pygame.Rect(button_x, button_y, button_width, button_height)
#         pygame.draw.rect(screen, bg_color, box_rect, border_radius=10)
#         
#         # Center text in button
#         text_surface = button_font.render(name, True, color)
#         text_x = box_rect.centerx - text_surface.get_width() // 2
#         text_y = box_rect.centery - text_surface.get_height() // 2
#         
#         screen.blit(text_surface, (text_x, text_y))
#         button_rects.append((box_rect, name))
#         
#         # Event Handling (key or mouse input)
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_RETURN:
#                     return "Play"  # Return "Play" to start the game
#             elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                 mouse_pos = pygame.mouse.get_pos()
#                 for rect, item in button_rects:
#                     if rect.collidepoint(mouse_pos):
#                         return "Play"  # Return "Play" to start the game
#         
#         pygame.display.flip()
#         clock.tick(60)


# GAME LOGIC


























####################################################################################################################
# RESULT SCREENS
# DEATH SCREEN
def show_death_screen(screen):
    # Get screen dimensions
    pygame.mixer.music.load("gunshot.mp3")
    pygame.mixer.music.play(2)
    WIDTH, HEIGHT = screen.get_size()
    
    # Colors
    BLACK = (0, 0, 0)
    PINK = (255, 105, 180)
    
    # Load and scale coffin sprite
    coffin_width = 300
    coffin_height = 150
    coffin_sprite = pygame.image.load("coffin.jpg")
    coffin_sprite = pygame.transform.scale(coffin_sprite, (coffin_width, coffin_height))
    
    # Load font and prepare text
    font = pygame.font.Font("font1.otf", int(WIDTH * 0.15))
    game_over_text = font.render("GAME OVER", True, PINK)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Animation settings
    duration = 4.0  # seconds for full animation
    fps = 60
    total_frames = int(duration * fps)
    text_delay = 30  # frames to wait after coffin passes center
    
    # Animation loop variables
    clock = pygame.time.Clock()
    frame_count = 0
    passed_center = False
    text_counter = 0
    show_text = False
    
    # Main animation loop
    running = True
    while running and frame_count < total_frames + 60:  # Add extra time at end
        screen.fill(BLACK)
        
        # Calculate coffin position
        progress = min(1.0, frame_count / total_frames)
        start_y = -coffin_height
        end_y = HEIGHT + coffin_height
        current_y = start_y + progress * (end_y - start_y)
        
        # Check if coffin passed center
        if current_y > HEIGHT / 2 and not passed_center:
            passed_center = True
        
        # Handle text delay and appearance
        if passed_center:
            text_counter += 1
            if text_counter >= text_delay and not show_text:
                show_text = True
        
        # Draw coffin
        sprite_rect = coffin_sprite.get_rect(center=(WIDTH // 2, current_y))
        screen.blit(coffin_sprite, sprite_rect)
        
        # Draw text with fade-in effect if it's time
        if show_text:
            fade_progress = min(1.0, (text_counter - text_delay) / 15)
            text_alpha = int(255 * fade_progress)
            
            text_surface = pygame.Surface(text_rect.size, pygame.SRCALPHA)
            temp_text = font.render("GAME OVER", True, (PINK[0], PINK[1], PINK[2], text_alpha))
            text_surface.blit(temp_text, (0, 0))
            screen.blit(text_surface, text_rect)
        
        # Update display
        pygame.display.flip()
        
        # Check for exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and show_text:
                # Only allow exit after text has appeared
                running = False
        
        # Advance animation
        frame_count += 1
        clock.tick(fps)  
    return "Menu"

# WIN SCREEN
















####################################################################################################################    
# MAIN PROGRAM
def main():
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption("Squid-ish Games")

    # Screen setup
    if os.environ.get('RPI_MODE', 'False').lower() == 'true':
        WIDTH, HEIGHT = 288, 512
    else:
        WIDTH, HEIGHT = 800, 700

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    game_running = True
    game_state = "Menu"
    mini_games = ["Hopscotch", "Tic Tac Toe","Red Light Green Light"]
    completed_games = set()

    while game_running:
        if game_state == "Menu":
            completed_games.clear()  # Reset progress when returning to menu
            pygame.mixer.music.load("pink_soldiers.mp3")
            pygame.mixer.music.play(-1)
            menu_choice = show_menu_screen(screen)
            if menu_choice == "Start":
                game_state = random.choice(["Hopscotch"])
            elif menu_choice == "About Game":
                game_state = "About Game"
            elif menu_choice == "Meet Team":
                game_state = "Meet Team"
        
        elif game_state == "About Game":
            game_choice = show_about_game_screen(screen)
            game_state = game_choice  # Will return a game name
        
        elif game_state == "Meet Team":
            choice = show_meet_team(screen)
            game_state = "Menu"
        
        elif game_state in mini_games:
            if game_state in completed_games:
                # Skip already played game
                unplayed = [g for g in mini_games if g not in completed_games]
                game_state = random.choice(unplayed) if unplayed else "Win"
                continue
            if game_state == "Hopscotch":
                pygame.mixer.music.stop()
                pygame.mixer.music.load("hopscotch_instructions.mp3")
                pygame.mixer.music.play()
                result = show_hopscotch_game_screen(screen)

            elif game_state == "Tic Tac Toe":
                pygame.mixer.music.load("tictactoe_instructions.mp3")
                pygame.mixer.music.play(-1)
                result = show_tictactoe_game_screen(screen)
                
            elif game_state == "Red Light Green Light":
                pygame.mixer.music.load("redlightgreenlight_instructions.mp3")
                pygame.mixer.music.play(-1)
                result = show_redlightgreenlight_game_screen(screen)

#             elif game_state == "Simon Says":
#                 pygame.mixer.music.load("salesman_sound.mp3")
#                 pygame.mixer.music.play(-1)
#                 result = show_simon_says_game_screen(screen)  
#   
            # Handle result
            if result == "win":
                completed_games.add(game_state)
                if len(completed_games) == len(mini_games):
                    game_state = "Win"
                else:
                    unplayed = [g for g in mini_games if g not in completed_games]
                    game_state = random.choice(unplayed)
            else:
                game_state = "Menu"

        elif game_state == "Win":
            show_win_screen(screen)
            game_state = "Menu"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

    pygame.quit()
    sys.exit()
os.environ['RPI_MODE'] = 'TRUE'
main()
