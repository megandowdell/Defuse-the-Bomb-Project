from threading import Thread
from time import sleep
import board
from digitalio import DigitalInOut, Direction, Pull


class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name = name, daemon = True)
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

    # runs the thread
    def run(self):
        self._running = True
        while (True):
            # process keys when keypad key(s) are pressed
            if (self._keypad.pressed_keys):
                # debounce
                while (self._keypad.pressed_keys):
                    try:
                        key = self._keypad.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                # do we have an asterisk (*) (and it resets the passphrase)?
                if (key == "*" and STAR_CLEARS_PASS):
                    self._value = ""
                # we haven't yet reached the max pass length (otherwise, we just ignore the keypress)
                elif (len(self._value) < MAX_PASS_LEN):
                    # log the key
                    self._value += str(key)
            sleep(0.1)
        self._running = False

    def __str__(self):
        return self._value

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
 
 
if __name__ == "__main__":
    keypad_cols = [DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
    keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
    keypad_keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
    matrix_keypad = Matrix_Keypad(keypad_rows, keypad_cols, keypad_keys)
    keypad = Keypad(matrix_keypad)
    keypad.start()
