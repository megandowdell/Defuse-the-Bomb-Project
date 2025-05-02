import pygame
import time
import random
import cv2
import numpy as np
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Light, Green Light")

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Game:
    def __init__(self):
        self.light_color = "red"
        self.last_change_time = time.time()
        
        # Load GIFs
        self.front_video = cv2.VideoCapture("redlightgreenlightdoll.gif")  # Front-facing for red light
        self.back_video = cv2.VideoCapture("redlightgreenlightdoll.gif")    # Back-facing for green light
        
        # If GIFs can't be loaded, create fallback placeholders
        if not self.front_video.isOpened() or not self.back_video.isOpened():
            print("Warning: Could not open one or both GIF files.")
            
        # Animation timing
        self.animation_time = time.time()
        self.frame_delay = 25  # seconds between frames
    
    def update(self):
        # Change light color every 2-5 seconds
        current_time = time.time()
        if current_time - self.last_change_time > random.uniform(2, 5):
            self.light_color = "green" if self.light_color == "red" else "red"
            self.last_change_time = current_time
    
    def get_current_frame(self):
        # Choose which animation to use based on light color
        if self.light_color == "red":
            video = self.front_video  # Front-facing when red light
        else:
            video = self.back_video   # Back-facing when green light
        
        # Read the current frame from video
        ret, frame = video.read()
        
        # If we've reached the end of the video, loop back
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = video.read()
        
        # Convert frame to pygame surface
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calculate dimensions to fit in the center of the screen
            video_height, video_width = frame.shape[:2]
            aspect_ratio = video_width / video_height
            
            new_width = min(300, WIDTH // 2)  # Max width is 300px or half the screen
            new_height = int(new_width / aspect_ratio)
            
            frame = cv2.resize(frame, (new_width, new_height))
            video_surface = pygame.surfarray.make_surface(frame)
            return video_surface
        
        # If there's an error, return a placeholder
        placeholder = pygame.Surface((150, 200))
        if self.light_color == "red":
            placeholder.fill(RED)
        else:
            placeholder.fill(GREEN)
        return placeholder
    
    def draw(self, screen):
        # Clear screen - black background
        screen.fill(BLACK)
        
        # Draw light indicator (small circle in the corner)
        light_color_rgb = GREEN if self.light_color == "green" else RED
        pygame.draw.circle(screen, light_color_rgb, (50, 50), 20)
        
        # Draw current GIF frame
        current_frame = self.get_current_frame()
        frame_rect = current_frame.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(current_frame, frame_rect)

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Control game speed
        clock.tick(60)
    
    # Clean up
    if hasattr(game, 'front_video'):
        game.front_video.release()
    if hasattr(game, 'back_video'):
        game.back_video.release()
    pygame.quit()

if __name__ == "__main__":
    main()