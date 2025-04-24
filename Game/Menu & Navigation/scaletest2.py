import pygame
import sys # to exitgame
from pygame.locals import * # handles events, mouse/keyboard controls etc.
import os  # for environment variables


# Game audio
pygame.mixer.init()
pygame.mixer.music.load("pink_soldiers.mp3")
pygame.mixer.music.play(-1)  # -1 makes it loop indefinitely

# References for scaling
dev_width, dev_height = 800, 700  # Resolution of development screen
reference_scale = (dev_width, dev_height)  # Used to scale based on development screen

# Subroutine to scale the position of elements  
def scale_position(x, y, current_size):
    # Calculates the ratio between dimensions on both screens and scales the elements based on this ratio
    """Scale a position based on current screen size compared to reference design size"""
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
    font_scale = (current_size[0] + current_size[1]) / (reference_scale[0] + reference_scale[1])
    scaled = int(size * font_scale)
    return max(16, min(scaled, 100))  # Keeps font size in a readable range

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

# Define Team class
class Soldier:
    # Constructor
    def __init__(self, name, role):
        self._name = name
        self._role = role
    
    # Getters
    def get_name(self):
        return self._name
    
    def get_role(self):
        return self._role
        
    # Setters
    def set_name(self, new_name):
        self._name = new_name
    
    def set_role(self, new_role):
        self._role = new_role

    
    # Deleters
    def del_name(self):
        del self._name
    
    def del_role(self):
        del self._role
    
    # Property methods
    name = property(get_name, set_name, del_name)
    role = property(get_role, set_role, del_role)


# Subroutine to display menu
def show_menu(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("SQUID-ISH GAMES")
    
    # Fixed Colors
    BEIGE = (232, 218, 189)
    PURPLE= (67, 0, 117)
    YELLOW = (234, 202, 87)
    GREY = (149, 143, 137)
    #GREEN = (0, 213, 136)
    #BLACK = (0, 0, 0)
    #PINK = (255, 64, 119)
    
    # Font sizes based on reference design
    base_title_size = 80
    base_subtitle_size = 45
    base_menu_size = 50 
    
    # Scale font sizes based on current screen
    title_size = scale_font_size(base_title_size, (WIDTH, HEIGHT))
    subtitle_size = scale_font_size(base_subtitle_size, (WIDTH, HEIGHT))
    menu_size = scale_font_size(base_menu_size, (WIDTH, HEIGHT))
    
    # Fonts
    title_font = pygame.font.Font("font2.otf", title_size)
    subtitle_font = pygame.font.Font("font1.otf", subtitle_size)
    menu_font = pygame.font.Font("font2.otf", menu_size)

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
        
        # Draw title and subtitle - scale from reference positions
        title_text = title_font.render("Squid-ish Games", True, BEIGE)
        subtitle_text = subtitle_font.render("Error 404: Mercy Not Found", True, YELLOW)
        
        # Reference positions (from your original design)
        base_title_pos = (dev_width // 2, 60)
        base_subtitle_pos = (dev_width // 2, 150)
        
        # Scale positions to current screen
        title_x, title_y = scale_position(base_title_pos[0], base_title_pos[1], (WIDTH, HEIGHT))
        subtitle_x, subtitle_y = scale_position(base_subtitle_pos[0], base_subtitle_pos[1], (WIDTH, HEIGHT))
        
        # Center text at scaled positions
        screen.blit(title_text, (title_x - title_text.get_width() // 2, title_y))
        screen.blit(subtitle_text, (subtitle_x - subtitle_text.get_width() // 2, subtitle_y))
        
        button_rects = []
        # Reference menu button positions
        base_button_y_start = 250
        base_button_spacing = 70
        
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
def show_about_game_screen(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("About Game")
    
    # Colors
    BEIGE = (232, 218, 189)
    PURPLE= (67, 0, 117)
    YELLOW = (234, 202, 87)
    GREY = (149, 143, 137)
    BLACK = (0, 0, 0)
    
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
    
    # Game intro text - moved from the intro screen to here
    welcome_text = [
        "WELCOME TO SQUID-ISH GAMES",
        "AHFGIYGSLU;HSJF",
        "SBGJSNDGONSKSDHSO;",
    ]
    
    # Additional gameplay instructions
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
        
        for line in gameplay_text:
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
        base_button_widths = [160, 220]  # Approximate widths for Back and Continue
        base_button_y = dev_height - 100
        
        # Scale button dimensions
        button_height = int(base_button_height * HEIGHT / dev_height)
        button_widths = [int(w * WIDTH / dev_width) for w in base_button_widths]
        
        # Center buttons with appropriate spacing
        total_width = sum(button_widths) + int(WIDTH * 0.05)  # 5% of width as spacing
        start_x = (WIDTH - total_width) // 2
        button_y = int(base_button_y * HEIGHT / dev_height)
        
        button_rects = []
        for i in range(len(htp_items)):
            name = htp_items[i]
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
def soldier_select(screen):
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Meet The Team")
    
    # Colors
    BEIGE = (232, 218, 189)
    PURPLE = (67, 0, 117)
    YELLOW = (234, 202, 87)
    GREY = (149, 143, 137)
    BLACK = (0, 0, 0)
    
    # Base font sizes
    base_title_size = 50
    base_char_size = 30
    base_desc_size = 18
    
    # Scale font sizes
    title_size = scale_font_size(base_title_size, (WIDTH, HEIGHT))
    char_size = scale_font_size(base_char_size, (WIDTH, HEIGHT))
    desc_size = scale_font_size(base_desc_size, (WIDTH, HEIGHT))
    
    # Fonts
    title_font = pygame.font.Font("font1.otf", title_size)
    char_font = pygame.font.Font("font5.otf", char_size)
    desc_font = pygame.font.Font("font5.otf", desc_size)
    
    # Soldier options with descriptions
    soldiers = [
        {"name": "Christa", "role": "Masked Officer", 
         "description": "Humanity's strongest soldier. Exceptional combat skills with ODM gear. Stoic and disciplined."},
        {"name": "Khalil", "role": "Masked Officer", 
         "description": "Brilliant Titan researcher who combines scientific curiosity with unorthodoz tactics to the battlefield. Eccentric but effective leader."},
        {"name": "Matt", "role": "Masked Officer",  
         "description": "Visionary commander driven by truth, known for his bold strategies and unwavering resolve."},
        {"name": "Megan", "role": "Masked Officer", 
         "description": "Visionary commander driven by truth, known for his bold strategies and unwavering resolve."}
    ]
    
    # Reference image size
    base_img_size = 150
    img_size = int(base_img_size * min(WIDTH/dev_width, HEIGHT/dev_height))
    
    # Soldier images - scale responsively
    soldier_images = {}
    for soldier in soldiers:
        img = pygame.image.load(f"{soldier['name'].split()[0].lower()}.jpg")
        soldier_images[soldier['name']] = pygame.transform.scale(img, (img_size, img_size))
    
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
        
        soldier_rects = []
        
        # Adaptive layout based on orientation
        if is_portrait:
            # Use a 2x2 grid for soldier cards in portrait mode
            cards_per_row = 2
            rows = (len(soldiers) + cards_per_row - 1) // cards_per_row
            
            # Scale card dimensions
            card_width = int(WIDTH * 0.4)
            card_height = int(HEIGHT * 0.25)
            card_spacing = int(WIDTH * 0.05)
            
            for i, soldier in enumerate(soldiers):
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
                
                # Draw soldier image
                soldier_img = soldier_images[soldier['name']]
                soldier_img_rect = soldier_img.get_rect(center=(card_x + card_width//2, card_y + card_height * 0.3))
                screen.blit(soldier_img, soldier_img_rect)
                
                # Draw soldier info - just name and role now
                name_text = char_font.render(soldier['name'], True, YELLOW if is_selected else BEIGE)
                name_y = card_y + int(card_height * 0.6)
                screen.blit(name_text, (card_x + card_width//2 - name_text.get_width()//2, name_y))
                
                role_text = desc_font.render(soldier['role'], True, BEIGE)
                role_y = name_y + name_text.get_height() + 5
                screen.blit(role_text, (card_x + card_width//2 - role_text.get_width()//2, role_y))
                
                soldier_rects.append((card_rect, i))
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
            total_width = (card_width * len(soldiers)) + (card_spacing * (len(soldiers) - 1))
            start_x = (WIDTH - total_width) // 2
            
            # Reference vertical position
            base_card_y = dev_height // 2 - 150
            card_y = int(base_card_y * HEIGHT / dev_height)
            
            for i, soldier in enumerate(soldiers):
                is_selected = i == selected_index
                
                # Calculate card position
                card_x = start_x + i * (card_width + card_spacing)
                
                # Draw card background
                card_color = PURPLE if is_selected else GREY
                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                pygame.draw.rect(screen, card_color, card_rect, border_radius=10)
                
                if is_selected:
                    pygame.draw.rect(screen, YELLOW, card_rect, 3, border_radius=10)
                
                # Draw soldier image
                soldier_img = soldier_images[soldier['name']]
                soldier_img_rect = soldier_img.get_rect(center=(card_x + card_width//2, card_y + int(card_height * 0.25)))
                screen.blit(soldier_img, soldier_img_rect)
                
                # Draw soldier info - just name and role now
                name_text = char_font.render(soldier['name'], True, YELLOW if is_selected else BEIGE)
                name_y = card_y + int(card_height * 0.55)
                screen.blit(name_text, (card_x + card_width//2 - name_text.get_width()//2, name_y))
                
                role_text = desc_font.render(soldier['role'], True, BEIGE)
                role_y = name_y + name_text.get_height() + 5
                screen.blit(role_text, (card_x + card_width//2 - role_text.get_width()//2, role_y))
                
                soldier_rects.append((card_rect, i))
        
        # Soldier description - displayed in a dedicated box at the bottom
        soldier_desc = soldiers[selected_index]['description']
        
        # Reference description box dimensions and position
        base_desc_box = pygame.Rect(50, dev_height - 150, dev_width - 100, 80)
        desc_box_rect = scale_rect(base_desc_box, (WIDTH, HEIGHT))
        
        desc_box = pygame.Surface((desc_box_rect.width, desc_box_rect.height), pygame.SRCALPHA)
        desc_box.fill((30, 30, 30, 200))
        screen.blit(desc_box, (desc_box_rect.x, desc_box_rect.y))
        pygame.draw.rect(screen, (100, 100, 150), desc_box_rect, 2)
        
        # Draw description text
        max_desc_width = desc_box_rect.width - 40
        desc_lines = wrap_text(soldier_desc, desc_font, max_desc_width)
        
        for i, line in enumerate(desc_lines):
            if i >= 2:  # Limit to 2 lines for consistent display
                break
            desc_text = desc_font.render(line, True, BEIGE)
            text_x = WIDTH//2 - desc_text.get_width()//2
            text_y = desc_box_rect.y + 10 + i * (desc_text.get_height() + 5)
            screen.blit(desc_text, (text_x, text_y))
        
        # Reference button positions and dimensions
        base_select_button = pygame.Rect(dev_width//2 - 75, dev_height - 60, 150, 40)
        base_back_button = pygame.Rect(50, dev_height - 60, 100, 40)
        
#         # Scale buttons to current screen size
        back_button = scale_rect(base_back_button, (WIDTH, HEIGHT))
        
        # Draw Back button
        pygame.draw.rect(screen, GREY, back_button, border_radius=10)
        back_text = char_font.render("Back", True, BEIGE)
        back_text_x = back_button.centerx - back_text.get_width()//2
        back_text_y = back_button.centery - back_text.get_height()//2
        screen.blit(back_text, (back_text_x, back_text_y))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = (selected_index - 1) % len(soldiers)
                elif event.key == pygame.K_RIGHT:
                    selected_index = (selected_index + 1) % len(soldiers)
                elif event.key == pygame.K_RETURN:
                    # Return the selected soldier as a Soldier object
                    selected_soldier = soldiers[selected_index]
                    return Soldier(selected_soldier["name"], selected_soldier["role"])
                elif event.key == pygame.K_ESCAPE:
                    return "Menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Check for soldier card clicks
                for rect, idx in soldier_rects:
                    if rect.collidepoint(mouse_pos):
                        selected_index = idx
            
                if back_button.collidepoint(mouse_pos):
                    return "Menu"
        
        pygame.display.flip()
        clock.tick(60)        
        
# MAIN PROGRAM #
def main():
    # Initialize pygame
    pygame.init()
    pygame.display.set_caption("Squid-ish Games")
    
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
            soldier = soldier_select(screen)
            if soldier == "Menu":
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
    # Set to true when testing RPi mode
    os.environ['RPI_MODE'] = 'FALSE'
    
    main()
