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
                        return random.choice(["Hopscotch", "Simon Says","Tic Tac Toe", "Red Light Green Light"]) 
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for rect, item in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if item == "Back":
                            return "Menu"  
                        elif item == "Continue":
                            return random.choice(["Hop"])  
        
        pygame.display.flip()
        clock.tick(60)
        