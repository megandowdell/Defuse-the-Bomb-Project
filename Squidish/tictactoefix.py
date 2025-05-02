import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

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


def show_tictactoe_screen(screen):
    # First show the instructions screen
    result = show_hopscotch_instructions_screen(screen)
    
    # Only proceed to the game if the player clicked "Play"
    if result == "Play":
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
        BG_COLOR = (28, 170, 156)       # Background
        LINE_COLOR = (23, 145, 135)     # Grid lines
        CIRCLE_COLOR = (239, 231, 200)  # CPU's move
        CROSS_COLOR = (66, 66, 66)      # Player's move
        WIN_LINE_COLOR = (255, 50, 50)  # Winning line

        # Fonts
        SCORE_FONT = pygame.font.SysFont("Arial", 26)
        ROUND_FONT = pygame.font.SysFont("Arial", 42)
        MESSAGE_FONT = pygame.font.SysFont("Arial", 36)

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
            score_text = SCORE_FONT.render(f"Round {round_num} | You: {player_score}  CPU: {cpu_score}", True, (255, 255, 255))
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
            text = ROUND_FONT.render(f"Round {round_num} starts!", True, (255, 255, 255))
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
                    return "lose"

                # Prepare for next round
                round_number += 1
                show_next_round(round_number)

# # Run this file standalone for testing
# if __name__ == "__main__":
#     result = play_tic_tac_toe()
#     print("Result:", result)
#     pygame.quit()