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
        
        # Load GIF only once
        self.video = cv2.VideoCapture("redlightgreenlightdoll.gif")
        
        # If GIF can't be loaded, print warning
        if not self.video.isOpened():
            print("Warning: Could not open GIF file.")
        
        # Get total frame count for reverse playback
        self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Current frame position
        self.current_frame = 0
        
        # Animation timing
        self.animation_time = time.time()
        self.frame_delay = 0.05  # 50ms between frames, adjust as needed
        
        # Direction (1 for forward, -1 for reverse)
        self.direction = 1
    
    def update(self):
        # Change light color every 2-5 seconds
        current_time = time.time()
        if current_time - self.last_change_time > random.uniform(2, 5):
            self.light_color = "green" if self.light_color == "red" else "red"
            
            # Change direction based on light color
            self.direction = 1 if self.light_color == "green" else -1
            
            self.last_change_time = current_time
    
    def get_current_frame(self):
        current_time = time.time()
        
        # Only advance the frame if enough time has passed
        if current_time - self.animation_time >= self.frame_delay:
            self.animation_time = current_time
            
            # Update frame position based on direction
            if self.direction == 1:  # Forward (green light)
                self.current_frame = (self.current_frame + 1) % self.total_frames
            else:  # Reverse (red light)
                self.current_frame = (self.current_frame - 1) % self.total_frames
            
            # Set video to the specific frame
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        
        # Read the current frame
        ret, frame = self.video.read()
        
        # If we've reached the end of the video or have an error
        if not ret:
            # Reset position and try again
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video.read()
        
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
    if hasattr(game, 'video'):
        game.video.release()
    pygame.quit()

if __name__ == "__main__":
    main()