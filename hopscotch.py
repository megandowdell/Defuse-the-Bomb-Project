# Hopscotch game
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
    
    # Hopscotch-specific instructions
    welcome_text = [
        "WELCOME TO HOPSCOTCH",
        "A game of skill and chance",
        "Your reflexes will be tested!"
    ]
    
    # Additional gameplay instructions
    gameplay_text = [
        "HOW TO PLAY:",
        "1. Each row has ONE safe tile",
        "2. Choose the correct tile to advance",
        "3. Safe tiles will flash green",
        "4. Wrong tiles will flash red",
        "5. Complete all 5 levels to win!",
        "",
        "Remember: Choose wisely. One wrong move and it's game over!"
    ]
    
    # Character options (buttons for 'Play')
    ag_items = ["Play"]  # Changed from ["Back", "Continue"] to just ["Play"]
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
        
# Imports
import pygame           # Main game engine
import random           # Used for randomly placing safe tiles
import sys              # System exit
# import RPi.GPIO as GPIO  # Uncomment if using GPIO on Raspberry Pi
# import time               # For delay/reset between turns

def show_hopscotch_game_screen(screen):
    # First show the instructions screen
    result = show_hopscotch_instructions_screen(screen)
    
    # Only proceed to the game if the player clicked "Play"
    if result == "Play":
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
        TILE_A_COLOR = (255, 64, 119)  # Light red
        TILE_B_COLOR = (0, 194, 176)  # Light blue
        TILE_C_COLOR = (134, 233, 0)  # Light green
        TILE_D_COLOR = (233, 219, 0)  # Light yellow

        # Create a list for easy reference
        TILE_COLORS = [TILE_A_COLOR, TILE_B_COLOR, TILE_C_COLOR, TILE_D_COLOR]
        
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
        def generate_board(successes_per_row=2):
            board = []
            for _ in range(ROWS):
                safe = random.sample(range(COLS), successes_per_row)
                board.append(safe)  # Each row has 1 correct tile (change for more)
            return board
        
        # Generate a new row for the board
        def generate_new_row(successes_per_row=2):
            return random.sample(range(COLS), successes_per_row)

        # Positioning Function 
        def get_tile_rect(row, col):
            # Keep positions fixed like in original code
            row_height = TILE_HEIGHT + 60
            x = (WIDTH - (COLS * TILE_WIDTH + (COLS - 1) * TILE_GAP)) // 2 + col * (TILE_WIDTH + TILE_GAP)
            y = 150 + row * row_height  # Use original y calculation
            return pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)

        # Board Drawing
        def draw_board(board, current_row, lives, rows_cleared=0, animation_offset=0, selected_tile=None, show_correct=False):
            screen.fill(BG)
            
            # Draw only visible rows
            for row_idx in range(min(VISIBLE_ROWS, len(board))):
                actual_row = row_idx + current_row
                if actual_row >= len(board):
                    continue
                    
                for col in range(COLS):
                    # Calculate position with animation offset
                    base_rect = get_tile_rect(row_idx, col)
                    # Adjust y position for animation
                    rect = pygame.Rect(base_rect.x, base_rect.y + animation_offset, base_rect.width, base_rect.height)
                    
                    # Determine tile color based on various conditions
                    if row_idx == 0:  # First visible row (current row)
                        # For current row - use the column's designated color
                        if show_correct and col in board[actual_row]:
                            color = SAFE  # Show safe tiles when appropriate
                        else:
                            color = TILE_COLORS[col]  # Use the specific color for each column
                    else:
                        # For future rows - use dimmed version of the column's color
                        base_color = TILE_COLORS[col]
                        color = tuple(max(c // 2, 0) for c in base_color)  # Dimmed version
                        
                    # Draw the tile with appropriate color
                    pygame.draw.rect(screen, color, rect)

                    # Add the letter label
                    label = FONT.render(chr(65 + col), True, TEXT)
                    screen.blit(label, (rect.x + TILE_WIDTH//2 - 10, rect.y + 15))

           
            # Level display
            level_text = FONT.render(f"Level: {rows_cleared + 1}/{ROWS}", True, TEXT)
            screen.blit(level_text, (20, 20))

            # Lives display - UPDATED
            lives_text = FONT.render(f"Lives: {lives}", True, TEXT)
            screen.blit(lives_text, (20, 60))  # Position under level text

            pygame.display.flip()

        def animate_row_clear(board, current_row, lives, rows_cleared, duration=500):
            start_time = pygame.time.get_ticks()
            row_height = TILE_HEIGHT + 60
            
            # Animate rows moving up
            while True:
                current_time = pygame.time.get_ticks()
                elapsed = current_time - start_time
                
                if elapsed >= duration:
                    break
                    
                progress = elapsed / duration
                offset = -int(row_height * progress)  # Negative offset to move up
                
                draw_board(board, current_row, lives, rows_cleared, offset)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                        
                clock.tick(60)
            
            # Move to next row in the board (don't modify the board structure)
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
                pygame.time.delay(300)  # Brief flash of green
            
                rows_cleared += 1
                current_row = animate_row_clear(board, current_row, lives, rows_cleared)
        
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
            board = generate_board(successes_per_row=2)
            current_row = 0
            lives = 5
            rows_cleared = 0

            while True:
                draw_board(board, current_row, lives, rows_cleared)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                
                        for col in range(COLS):
                            tile_rect = get_tile_rect(0, col)
                    
                            if tile_rect.collidepoint(mouse_pos):
                                if col in board[current_row]:
                            # Correct choice - flash green briefly
                                    pygame.draw.rect(screen, SAFE, tile_rect)
                                    label = FONT.render(chr(65 + col), True, TEXT)
                                    screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))
                                    pygame.display.flip()
                                    pygame.time.delay(300)
                            
                                    rows_cleared += 1
                                    current_row = animate_row_clear(board, current_row, lives, rows_cleared)
                            
                                    if rows_cleared >= ROWS:
                                        return True
                                else:
                            # Wrong choice - show red
                                    pygame.draw.rect(screen, FAIL, tile_rect)
                                    label = FONT.render(chr(65 + col), True, TEXT)
                                    screen.blit(label, (tile_rect.x + TILE_WIDTH//2 - 10, tile_rect.y + 15))
                                    pygame.display.flip()
                                    pygame.time.delay(800)
                            
                                    lives -= 1
                                    current_row = 0
                                    rows_cleared = 0
                                    if lives == 0:
                                        show_death_screen(screen)
                                        show_menu_screen(screen)
                                        return False
                                        
        

            clock.tick(60)

        won = play_game()
        screen.fill(BG)
        pygame.display.flip()