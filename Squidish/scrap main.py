# def main():
#     # Initialize pygame
#     pygame.init()
#     pygame.display.set_caption("Squid-ish Games")
#     
#     # Screen setup with toggle for different displays
#     # Check if RPI_MODE environment variable is set
#     if os.environ.get('RPI_MODE', 'False').lower() == 'true':
#         # Running on Raspberry Pi with 576x1024 display 288, 512
#         WIDTH, HEIGHT = 288, 512
#         print("Running in Raspberry Pi mode (576x1024)")
#     else:
#         # Running on desktop with 800x700 display for testing
#         WIDTH, HEIGHT = 800, 700
#         print("Running in desktop mode (800x700)")
#         
#     screen = pygame.display.set_mode((WIDTH, HEIGHT))
#     
#     # Main variables
#     game_running = True # Controls game loop
#     game_state = "Menu" # Controls current state/screen of game
#     completed_games = set()
#     all_games = {"Hopscotch", "Tic Tac Toe", "Simon Says", "Red Light Green Light"}
# 
#     # Main game loop
#     while game_running:
# 
#         if game_state == "Menu":
#             menu_choice = show_menu_screen(screen)
#             if menu_choice == "Start":
#                 pygame.mixer.music.stop()
#                 pygame.mixer.music.load("round_round.mp3")
#                 pygame.mixer.music.play(-1)  
#                 game_state = random.choice(["Hopscotch", "Tic Tac Toe"])
#             elif menu_choice == "About Game":  
#                 game_state = "About Game"  
#             elif menu_choice == "Meet Team":
#                 game_state = "Meet Team"
# 
#         elif game_state == "About Game":
#             about_choice = show_about_game_screen(screen)
#             if about_choice == "Back":
#                 game_state = "Menu"
#             else:
#                 pygame.mixer.music.stop()
#                 game_state = random.choice(["Hopscotch", "Tic Tac Toe"])
# #                 
# #         elif game_state == "Hopscotch":
# #             pygame.mixer.music.load("round_round.mp3") #Replace with instructions audio
# #             pygame.mixer.music.play(-1) 
# #             game_choice = show_hopscotch_game_screen(screen)
# #             if game_choice == "Menu":
# #                 game_state = "Menu"
#         
#         elif game_state == "Hopscotch":
#             pygame.mixer.music.load("round_round.mp3")
#             pygame.mixer.music.play(-1)
#             game_choice = show_hopscotch_game_screen(screen)
# 
#             if game_choice == "win":
#                 completed_games.add("Hopscotch")
#             elif game_choice == "Menu" or game_choice == "lose":
#                 show_death_screen(screen)
#                 completed_games.clear()
#                 game_state = "Menu"
#                 continue  # Skip to next loop iteration
# 
#             # After result, check if all games are done
#             if completed_games == all_games:
#                 game_state = "Win Screen"
#             else:
#                 remaining_games = list(all_games - completed_games)
#                 game_state = random.choice(remaining_games)
#         
#         
#         
#         
#         
#         
#         
#         
#         
# #         elif game_state == "Simon Says":
# #             pygame.mixer.music.load("salesman_sound.mp3")#Replace with instructions audio
# #             pygame.mixer.music.play(-1) 
# #             game_choice = show_hopscotch_game_screen(screen)
# #             if game_choice == "Menu":
# #                 game_state = "Menu"
#         elif game_state == "Tic Tac Toe":
#             pygame.mixer.music.load("way_forward.mp3") #Replace with instructions audio
#             pygame.mixer.music.play(-1) 
#             game_choice = show_tictactoe_game_screen(screen)
#             
#             if game_choice == "win":
#                 completed_games.add("Tic Tac Toe")
#             elif game_choice == "Menu" or game_choice == "lose":
#                 show_death_screen(screen)
#                 completed_games.clear()
#                 game_state = "Menu"
#                 continue  # Skip to next loop iteration
# 
#             # After result, check if all games are done
#             if completed_games == all_games:
#                 game_state = "Win Screen"
#             else:
#                 remaining_games = list(all_games - completed_games)
#                 game_state = random.choice(remaining_games)
#                 
# #             if game_choice == "Menu":
# #                 game_state = "Menu"
# #         elif game_state == "Red Light Green Light": #Replace with instructions audio
# #             pygame.mixer.music.load("game_doll.mp3")
# #             pygame.mixer.music.play(-1) 
# #             game_choice = show_hopscotch_game_screen(screen)
# #             if game_choice == "Menu":
# #                 game_state = "Menu"
#         
#         elif game_state == "Meet Team":  
#             meet_team_choice = show_meet_team(screen)
#             if meet_team_choice == "Back":
#                 game_state = "Menu"
#             else:
#                 game_state = "Menu"
#        
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 game_running = False
#     
#     pygame.quit()
#     sys.exit()