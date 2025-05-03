from threading import Thread
from time import sleep
import pygame
import sys
import random
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixkeypad import Matrix_Keypad


class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
        self._running = False
        self._value = None

    def reset(self):
        self._value = None


class Keypad(PhaseThread):
    def __init__(self, keypad, name="Keypad"):
        super().__init__(name)
        self._value = ""
        # the keypad pins
        self._keypad = keypad
        # Track the last pressed key for the game
        self.last_key = None
        self.key_pressed = False

    # runs the thread
    def run(self):
        self._running = True
        while True:
            # process keys when keypad key(s) are pressed
            if self._keypad.pressed_keys:
                # debounce
                while self._keypad.pressed_keys:
                    try:
                        key = self._keypad.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                
                # Save the last key press for the game to use
                if key in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    self.last_key = key
                    self.key_pressed = True
                
                # do we have an asterisk (*) (and it resets the passphrase)?
                if key == "*" and STAR_CLEARS_PASS:
                    self._value = ""
                # we haven't yet reached the max pass length (otherwise, we just ignore the keypress)
                elif len(self._value) < MAX_PASS_LEN:
                    # log the key
                    self._value += str(key)
            sleep(0.1)
        self._running = False

    def get_key_press(self):
        """Get the last key press and reset the flag"""
        if self.key_pressed:
            key = self.last_key
            self.key_pressed = False
            return key
        return None

    def __str__(self):
        return self._value


def show_tictactoe_instructions_screen(screen):
    # Placeholder function for instructions screen
    # In a real implementation, this would show game instructions
    pygame.time.delay(500)
    return "Play"


def show_death_screen(screen):
    # Placeholder function for death screen
    # In a real implementation, this would show a game over screen
    pygame.time.delay(1000)
    return


def show_tictactoe_game_screen(screen, keypad):
    # Initialize pygame if not already initialized
    if not pygame.get_init():
        pygame.init()
        pygame.mixer.init()
    
    # First show the instructions screen
    result = show_tictactoe_instructions_screen(screen)
    
    # Only proceed to the game if the player clicked "Play"
    if result == "Play":
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("way_forward.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Music file not found or pygame mixer issue")
        
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
        CIRCLE_COLOR = (255, 255, 255)
        CROSS_COLOR = (66, 66, 66)      # Player's move
        WIN_LINE_COLOR = (255, 50, 50)  # Winning line

        # Fonts - use default if custom fonts are not available
        try:
            SCORE_FONT = pygame.font.Font("font1.otf", 26)
            ROUND_FONT = pygame.font.Font("font1.otf", 38)
            MESSAGE_FONT = pygame.font.Font("font1.otf", 30)
        except:
            SCORE_FONT = pygame.font.SysFont('Arial', 26)
            ROUND_FONT = pygame.font.SysFont('Arial', 38)
            MESSAGE_FONT = pygame.font.SysFont('Arial', 30)

        # Key mapping for the board positions
        # The keys 1-9 on the keypad correspond to positions on the board:
        # 7 8 9
        # 4 5 6
        # 1 2 3
        # But on a Tic Tac Toe board, positions are typically:
        # 0,0 0,1 0,2
        # 1,0 1,1 1,2
        # 2,0 2,1 2,2
        KEY_TO_POSITION = {
            7: (0, 0),  # top left
            8: (0, 1),  # top middle
            9: (0, 2),  # top right
            4: (1, 0),  # middle left
            5: (1, 1),  # middle
            6: (1, 2),  # middle right
            1: (2, 0),  # bottom left
            2: (2, 1),  # bottom middle
            3: (2, 2)   # bottom right
        }

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
                    if board[row][col] == 1:  # Player move (X)
                        pygame.draw.line(screen, CROSS_COLOR, 
                                         (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE + BOARD_TOP),
                                         (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE + BOARD_TOP),
                                         CROSS_WIDTH)
                        pygame.draw.line(screen, CROSS_COLOR,
                                         (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE + BOARD_TOP),
                                         (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE + BOARD_TOP),
                                         CROSS_WIDTH)
                    elif board[row][col] == 2:  # CPU move (O)
                        pygame.draw.circle(screen, CIRCLE_COLOR,
                                           (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_TOP),
                                           CIRCLE_RADIUS, CIRCLE_WIDTH)

        # Draw key mapping hints on the board
        def draw_key_hints(board):
            hint_font = pygame.font.SysFont('Arial', 12)
            for key, (row, col) in KEY_TO_POSITION.items():
                if board[row][col] == 0:  # Only show hints for empty squares
                    text = hint_font.render(str(key), True, (100, 100, 100))
                    x = col * SQUARE_SIZE + 10
                    y = row * SQUARE_SIZE + BOARD_TOP + 10
                    screen.blit(text, (x, y))

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
                    # Process events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                            
                    # Check for keypad input during player's turn
                    if player == 1 and not game_over:
                        key = keypad.get_key_press()
                        if key in KEY_TO_POSITION:
                            row, col = KEY_TO_POSITION[key]
                            if available_square(board, row, col):
                                mark_square(board, row, col, 1)
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
                        pygame.time.delay(750)  # Add delay for better user experience
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

                    # Draw shapes and update display
                    draw_lines()
                    draw_figures(board)
                    if player == 1 and not game_over:
                        draw_key_hints(board)  # Show the keypad number hints
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

    return None


if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Constants for keypad
    MAX_PASS_LEN = 10
    STAR_CLEARS_PASS = True
    
    # Set up the screen
    screen = pygame.display.set_mode((288, 512))
    pygame.display.set_caption('Tic Tac Toe')
    
    # Set up the keypad
    keypad_cols = [DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
    keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
    keypad_keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
    matrix_keypad = Matrix_Keypad(keypad_rows, keypad_cols, keypad_keys)
    keypad = Keypad(matrix_keypad)
    keypad.start()
    
    # Run the game
    show_tictactoe_game_screen(screen, keypad)
    
    # Clean up after game ends
    pygame.quit()