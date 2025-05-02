import pygame
import cv2
import numpy as np

pygame.mixer.init()
pygame.mixer.music.load("coins1.mp3")
pygame.mixer.music.play(-1)


def show_win_screen(screen):
    # Setup
    WIDTH, HEIGHT = screen.get_size()
    background = pygame.image.load("win2.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    # Create "YOU WON" text
    font = pygame.font.Font("font1.otf", int(WIDTH * 0.08))
    win_text = font.render("YOU WON", True, (0, 255, 128))
    text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT * 0.2))
    
    # Load video
    video = cv2.VideoCapture("coins.mp4")
    
    # Video settings
    video_width, video_height = 800, 700
    video_x = (WIDTH - video_width) // 2
    video_y = (HEIGHT - video_height) // 2
    video_duration = 5000  # 5 seconds
    
    # Main loop
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    running = True
    music_started = False 
    
    while running:
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - start_time
        
        # First phase: Play video (first 5 seconds)
        if time_elapsed < video_duration:
            ret, frame = video.read()
            
            # If we reach the end of video, loop back to beginning
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = video.read()
            
            # Convert frame to pygame surface
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (video_width, video_height))
            video_surface = pygame.surfarray.make_surface(np.rot90(frame))
            
            # Draw video
            screen.fill((0, 0, 0))
            screen.blit(video_surface, (video_x, video_y))
        
        # Second phase: Show background with text
        else:
            if not music_started:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("fly_me.mp3")
                pygame.mixer.music.play(-1)
                music_started = True
                
            screen.blit(background, (0, 0))
            screen.blit(win_text, text_rect)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if time_elapsed >= video_duration:  # Only allow exit after video
                    running = False
        
        pygame.display.flip()
        clock.tick(60)
    
    video.release()

    
if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 288, 512
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Win Screen")
    show_win_screen(screen)
    pygame.quit()