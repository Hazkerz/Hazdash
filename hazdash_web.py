import pygame
import sys
import os
import math
import asyncio

# --- Try to Import OpenCV for Video Support ---
cv2_available = False
try:
    import cv2
    cv2_available = True
    print("[OK] OpenCV loaded. Video backgrounds enabled.")
except ImportError:
    print("[!] OpenCV not found. Run 'pip install opencv-python' to enable video backgrounds.")

# --- Initialization ---
try:
    pygame.mixer.pre_init(44100, -16, 2, 2048)
except Exception:
    pass

pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Hazdash"
FPS = 67

# --- GLOBAL SETTINGS ---
MUSIC_VOLUME = 0.5      
VIDEO_FRAMERATE = 34    
VIDEO_ENABLED = True    
FONT_SCALE = 1.0
TITLE_SCALE = 1.0
GLITCH_EFFECT_ENABLED = True

# --- CUSTOMIZABLE TEXT SETTINGS ---
FONT_OPTIONS = ["impact", "arial", "courier", "comicsansms", "comicsans", "tahoma", "verdana", "timesnewroman"]
FONT_DISPLAY_NAMES = {
    "impact": "Impact",
    "arial": "Arial",
    "courier": "Courier New",
    "comicsansms": "Comic Sans",
    "comicsans": "Comic Sans",
    "tahoma": "Tahoma",
    "verdana": "Verdana",
    "timesnewroman": "Times New Roman"
}
CURRENT_TITLE_FONT = "impact"
CURRENT_TEXT_FONT = "impact"

COLOR_OPTIONS = [
    ("GREEN", (0, 255, 0)),
    ("RED", (255, 0, 0)),
    ("BLUE", (0, 100, 255)),
    ("PINK", (255, 20, 147)),
    ("GOLD", (255, 215, 0)),
    ("WHITE", (255, 255, 255)),
    ("ORANGE", (255, 165, 0)),
    ("GRAY", (128, 128, 128))
]

COLOR_HAZDASH_IDX = 0 # GREEN
COLOR_DEATH_IDX = 1   # RED
COLOR_COMPLETED_IDX = 4 # GOLD
COLOR_GENERAL_IDX = 5 # WHITE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0) 
ORANGE = (255, 165, 0) 
GRAY = (50, 50, 50)
BLUE_PLATFORM = (0, 100, 255) 
PURPLE_PORTAL = (148, 0, 211) 
PINK_PORTAL = (255, 20, 147) # New Secret Portal Color
GOLD = (255, 215, 0) 
DARK_GRAY = (30, 30, 30)

# --- User Customizations ---
LEVEL_4_PASSWORD = "1" 
ICON_FILENAME = "icon.png"

# --- Configuration ---
MUSIC_FILES = {
    "MENU": "menu_music.mp3",
    0: "level1.mp3", 
    1: "level2.mp3", 
    2: "level3.mp3", 
    3: "level4.mp3",
    4: "secret.mp3" # Secret Level Audio
}

VIDEO_FILES = {
    0: "bg1.mp4", 
    1: "bg2.mp4", 
    2: "bg3.mp4", 
    3: "bg4.mp4",
    4: "secret_bg.mp4" # Secret Level Video
}

# --- PATH FIXER ---
import sys
if getattr(sys, 'frozen', False):
    # If the script is running as an EXE
    SCRIPT_DIR = sys._MEIPASS
else:
    # If the script is running as a normal .py file
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Global variables
current_track_path = None
music_enabled = True

# --- SCREEN & SCALING SETUP ---
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
# --- FONT SETUP ---
font_large = None
font_small = None
font_tiny = None

def get_font(size, font_name=None):
    if font_name is None:
        font_name = CURRENT_TEXT_FONT
    try:
        return pygame.font.SysFont(font_name, int(size * FONT_SCALE))
    except Exception:
        return pygame.font.Font(None, int(size * FONT_SCALE))

def get_title_font(size):
    try:
        return pygame.font.SysFont(CURRENT_TITLE_FONT, int(size * TITLE_SCALE))
    except Exception:
        return pygame.font.Font(None, int(size * TITLE_SCALE))

def refresh_fonts():
    global font_large, font_small, font_tiny
    font_large = get_title_font(90)
    font_small = get_font(40)
    font_tiny = get_font(30)

refresh_fonts()

# --- ICON LOADER ---
icon_path = os.path.join(SCRIPT_DIR, ICON_FILENAME)
if os.path.exists(icon_path):
    try:
        app_icon = pygame.image.load(icon_path)
        pygame.display.set_icon(app_icon)
    except Exception: pass

# --- HELPER FUNCTIONS ---

def draw_and_flip():
    """Scales the 800x600 game screen to fit the actual window size."""
    scaled_surface = pygame.transform.scale(screen, window.get_size())
    window.blit(scaled_surface, (0, 0))
    pygame.display.flip()

def get_mouse_pos(event_pos):
    """Corrects mouse coordinates based on screen scaling."""
    win_w, win_h = window.get_size()
    scale_x = win_w / SCREEN_WIDTH
    scale_y = win_h / SCREEN_HEIGHT
    return (event_pos[0] / scale_x, event_pos[1] / scale_y)

def toggle_fullscreen_handler():
    global window
    is_fullscreen = window.get_flags() & pygame.FULLSCREEN
    if is_fullscreen:
        window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

def play_music(track_key, force_restart=False):
    global current_track_path, music_enabled
    filename = MUSIC_FILES.get(track_key)
    full_path = None
    if filename: full_path = os.path.join(SCRIPT_DIR, filename)

    if not music_enabled or not filename or not os.path.exists(full_path):
        pygame.mixer.music.stop() 
        current_track_path = None
        return

    if current_track_path == full_path and pygame.mixer.music.get_busy() and not force_restart:
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        return

    try:
        pygame.mixer.music.stop() 
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(MUSIC_VOLUME) 
        pygame.mixer.music.play(-1) 
        current_track_path = full_path
    except Exception as e:
        print(f"Error playing music: {e}")
        pygame.mixer.music.stop() 
        current_track_path = None

def draw_gear_icon(surface, x, y, size, color):
    center = (x + size // 2, y + size // 2)
    radius = size // 2 - 4
    for i in range(0, 360, 45):
        angle = math.radians(i)
        end_x = center[0] + math.cos(angle) * (size // 2)
        end_y = center[1] + math.sin(angle) * (size // 2)
        pygame.draw.line(surface, color, center, (end_x, end_y), 6)
    pygame.draw.circle(surface, color, center, radius, 4)
    pygame.draw.circle(surface, BLACK, center, radius - 4)
    pygame.draw.circle(surface, color, center, 4)

def draw_glitch_text(surface, text, font, center_pos, color=WHITE, max_width=None):
    """Renders text with a 'broken/electronic' glitch effect, auto-fitting to max_width."""
    import random
    x, y = center_pos
    
    # Auto-fit logic
    if max_width:
        current_font = font
        while current_font.size(text)[0] > max_width:
            ratio = max_width / current_font.size(text)[0]
            new_size = int(current_font.get_height() * ratio * 0.9) # 0.9 for safety
            if new_size < 10: break # Minimum size
            font_family = CURRENT_TITLE_FONT if font == font_large else CURRENT_TEXT_FONT
            current_font = pygame.font.SysFont(font_family, new_size)
        font = current_font

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    
    # Occasional RGB split glitch
    if GLITCH_EFFECT_ENABLED and random.random() < 0.15:
        for _ in range(2):
            off_x = random.randint(-5, 5)
            off_y = random.randint(-2, 2)
            glitch_color = random.choice([(255, 0, 0), (0, 255, 255), (255, 0, 255)])
            glitch_surf = font.render(text, True, glitch_color)
            surface.blit(glitch_surf, (text_rect.x + off_x, text_rect.y + off_y))
    
    # Main text with a slight 'shadow' for depth
    surface.blit(font.render(text, True, (20, 20, 20)), (text_rect.x + 3, text_rect.y + 3))
    surface.blit(text_surf, text_rect)

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 50
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - self.size - 50 
        self.vel_y = 0
        self.gravity = 1
        self.jump_strength = -20
        self.on_ground = False 
        self.mode = "CUBE" 
        self.spectator_mode = False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, obstacles):
        if self.spectator_mode: self.image.set_alpha(128) 
        else: self.image.set_alpha(255)

        if self.mode == "SHIP":
            self.image.fill(ORANGE)
            keys = pygame.key.get_pressed()
            mouse_down = pygame.mouse.get_pressed()[0] 
            if keys[pygame.K_SPACE] or mouse_down: self.vel_y -= 0.9 
            else: self.vel_y += 0.5 
            if self.vel_y > 8: self.vel_y = 8
            if self.vel_y < -8: self.vel_y = -8
        else:
            self.image.fill(GREEN)
            self.vel_y += self.gravity

        self.mask = pygame.mask.from_surface(self.image)
        self.rect.y += self.vel_y
        self.on_ground = False 

        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            if self.mode == "SHIP" and not self.spectator_mode: return "DEAD" 
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True

        if self.rect.top <= 0:
            if self.mode == "SHIP" and not self.spectator_mode: return "DEAD" 
            self.rect.top = 0
            self.vel_y = 0

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                # Precise mask overlap check
                offset_x = obstacle.rect.x - self.rect.x
                offset_y = obstacle.rect.y - self.rect.y
                if not self.mask.overlap(obstacle.mask, (offset_x, offset_y)):
                    continue
                
                # --- PORTAL LOGIC ---
                if obstacle.is_portal:
                    # 1. CHECK FOR SECRET PORTAL FIRST
                    if obstacle.color == PINK_PORTAL:
                        return "SECRET_FOUND"

                    # 2. Standard Portals
                    if self.mode == "CUBE":
                        self.mode = "SHIP"
                        self.vel_y = -5 
                        obstacle.kill() 
                        continue
                    elif self.mode == "SHIP":
                        self.mode = "CUBE"
                        self.vel_y = -10 
                        obstacle.kill()
                        continue 
                
                if self.spectator_mode: continue
                if self.mode == "SHIP": return "DEAD" 
                if obstacle.is_spike: return "DEAD"

                if not obstacle.is_spike and self.vel_y > 0: 
                    self.rect.y -= self.vel_y 
                    
                    # Land side collision check
                    offset_x = obstacle.rect.x - self.rect.x
                    offset_y = obstacle.rect.y - self.rect.y
                    if self.mask.overlap(obstacle.mask, (offset_x, offset_y)):
                        self.rect.y += self.vel_y
                        return "DEAD" 
                    self.rect.y += self.vel_y 
                    self.rect.bottom = obstacle.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                else: return "DEAD"
        return "ALIVE"

    def jump(self):
        if self.mode == "CUBE" and self.on_ground:
            self.vel_y = self.jump_strength

# --- Obstacle Class ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, is_spike=True, is_inverted=False, color=RED, is_portal=False):
        super().__init__()
        self.width = w
        self.height = h
        self.color = color
        self.is_spike = is_spike
        self.is_portal = is_portal
        self.is_inverted = is_inverted
        self.move_speed = 6 
        self.image = pygame.Surface([w, h], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw_shape()
        self.mask = pygame.mask.from_surface(self.image)

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        if self.is_portal:
            pygame.draw.rect(self.image, self.color, [0, 0, self.width, self.height])
            pygame.draw.rect(self.image, WHITE, [0, 0, self.width, self.height], 3)
        elif self.is_spike:
            if self.is_inverted: points = [(0, 0), (self.width // 2, self.height), (self.width, 0)]
            else: points = [(0, self.height), (self.width // 2, 0), (self.width, self.height)]
            pygame.draw.polygon(self.image, self.color, points)
        else:
            pygame.draw.rect(self.image, self.color, [0, 0, self.width, self.height])
            pygame.draw.rect(self.image, WHITE, [0, 0, self.width, self.height], 2)

    def update(self):
        self.rect.x -= self.move_speed

# Constants
RED_SPIKE, NORMAL_SPIKE, PORTAL, INVERTED, NORMAL = True, False, True, True, False

# --- SETUP LEVEL FUNCTION ---
def setup_level(level_data):
    obstacles = pygame.sprite.Group()
    for item in level_data:
        is_portal = False; is_inverted = False; color = RED; is_spike = RED_SPIKE 
        num_args = len(item)
        if num_args == 5: x_offset, y_pos, w, h, is_spike = item; color = RED if is_spike else GRAY
        elif num_args == 6: x_offset, y_pos, w, h, is_spike, color = item
        elif num_args == 7:
             if item[-1] == PORTAL: x_offset, y_pos, w, h, is_spike, color, is_portal = item
             else: x_offset, y_pos, w, h, is_spike, is_inverted, color = item
        elif num_args == 8: x_offset, y_pos, w, h, is_spike, is_inverted, color, is_portal = item
        obstacle = Obstacle(SCREEN_WIDTH + x_offset, y_pos, w, h, is_spike, is_inverted, color, is_portal)
        obstacles.add(obstacle)
    return obstacles

# --- LEVEL DATA ---
LEVEL_1_EASY = [
    (300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (1200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (1800, SCREEN_HEIGHT - 100, 100, 50, RED_SPIKE),
    (2500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (3000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (3500, SCREEN_HEIGHT - 150, 100, 100, NORMAL_SPIKE, GRAY), 
    (3800, SCREEN_HEIGHT - 200, 100, 150, NORMAL_SPIKE, GRAY), 
    (4100, SCREEN_HEIGHT - 250, 100, 200, NORMAL_SPIKE, GRAY),
    (4300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (4700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (5100, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (5700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (6000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (6400, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (6800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (7000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (7500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (7900, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (8200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (8800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (9100, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (9400, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (9800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (10500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (10900, SCREEN_HEIGHT - 200, 100, 150, NORMAL_SPIKE, GRAY),
    (11200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (11500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (11800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (12000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (12500, SCREEN_HEIGHT - 150, 100, 100, NORMAL_SPIKE, GRAY),
    (12800, SCREEN_HEIGHT - 200, 100, 150, NORMAL_SPIKE, GRAY),
    (13100, SCREEN_HEIGHT - 250, 100, 200, NORMAL_SPIKE, GRAY),
    (13500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (14000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (14500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (15000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
]
LEVEL_1_END_X = 16000

LEVEL_2_MEDIUM = [
    (300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (800, SCREEN_HEIGHT - 150, 100, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (1400, SCREEN_HEIGHT - 200, 100, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (2000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (2200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (3000, SCREEN_HEIGHT - 200, 150, 200, NORMAL_SPIKE, BLUE_PLATFORM),
    (4000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (4350, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (4700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (5100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (5400, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (5700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (6000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (6400, SCREEN_HEIGHT - 230, 100, 200, NORMAL_SPIKE, BLUE_PLATFORM), 
    (7000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (7300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (7600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (8000, SCREEN_HEIGHT - 200, 150, 200, NORMAL_SPIKE, BLUE_PLATFORM), 
    (8700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (9100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (9400, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (9700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (10000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (10400, SCREEN_HEIGHT - 230, 100, 200, NORMAL_SPIKE, BLUE_PLATFORM), 
    (11000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (11300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (11600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (12000, SCREEN_HEIGHT - 200, 150, 200, NORMAL_SPIKE, BLUE_PLATFORM), 
    (12700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (13100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (13400, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (13700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (14000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (14400, SCREEN_HEIGHT - 230, 100, 200, NORMAL_SPIKE, BLUE_PLATFORM),
    (15000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (15300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (15600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (16000, SCREEN_HEIGHT - 200, 150, 200, NORMAL_SPIKE, BLUE_PLATFORM),
    (16700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (17100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (17400, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (17700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (18000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (18400, SCREEN_HEIGHT - 230, 100, 200, NORMAL_SPIKE, BLUE_PLATFORM),
    (19000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (19300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (19600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (20000, SCREEN_HEIGHT - 200, 150, 200, NORMAL_SPIKE, BLUE_PLATFORM),
    (20700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (21100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (21400, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (21700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (22000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (12500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (22300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (22600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (23000, SCREEN_HEIGHT - 200, 150, 200, NORMAL_SPIKE, BLUE_PLATFORM),
    (23700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (24100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (24400, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, BLUE_PLATFORM), 
    (24700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (25000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (25500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (26000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (26500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (27000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (27500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (28000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (28500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (29000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (29500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (30000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (30500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (31000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (31500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (32000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (32500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (33000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (33500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (34000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (34500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (35000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (35500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (36000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (36500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (37000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (37500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (38000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (38500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (39000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (39500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (40000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (40500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (41000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (41500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (42000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (42500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (43000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (43500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (44000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (44500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (45000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (45500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (46000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (46500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (47000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (47300, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (47600, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (47900, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (48200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (48500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (48800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (49100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (49400, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (49700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (50000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (50300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (50600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (50900, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (51200, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (51500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (51800, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (52100, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (52400, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (52700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (53000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (53300, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (53600, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (53900, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (54200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (54500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (55000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (55200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (55500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (55800, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM), 
    (56100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (56400, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (56700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (57000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (57300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (57600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (57900, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (58200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (58500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (58800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (59100, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (59400, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (59700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (60000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (60300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (60600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (60900, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (61200, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (61500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (61800, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (62100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (62400, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (62700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (63000, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (63300, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (63600, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (63900, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (64200, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (64500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (64800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (65100, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (65400, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (65700, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (66000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (66300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (66600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (66900, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (67200, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
    (67500, SCREEN_HEIGHT - 150, 50, 100, NORMAL_SPIKE, BLUE_PLATFORM),
]
LEVEL_2_END_X = 68000

LEVEL_3_HARD = [
    (400, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),  
    (1200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (1600, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, NORMAL, PURPLE_PORTAL, PORTAL), 
    (2200, 0, 100, 300, NORMAL_SPIKE, NORMAL, GRAY), 
    (2200, SCREEN_HEIGHT - 100, 100, 50, RED_SPIKE, NORMAL, RED), 
    (2800, SCREEN_HEIGHT - 250, 100, 200, NORMAL_SPIKE, NORMAL, GRAY), 
    (3400, 0, 100, 250, NORMAL_SPIKE, NORMAL, GRAY),
    (3400, SCREEN_HEIGHT - 200, 100, 150, NORMAL_SPIKE, NORMAL, GRAY),
    (4000, SCREEN_HEIGHT // 2, 80, 80, NORMAL_SPIKE, NORMAL, GRAY), 
    (4600, 0, 200, 400, NORMAL_SPIKE, NORMAL, GRAY),
    (5000, SCREEN_HEIGHT - 300, 200, 250, NORMAL_SPIKE, NORMAL, GRAY),
    (6000, 0, 1000, 100, NORMAL_SPIKE, NORMAL, GRAY), 
    (6000, SCREEN_HEIGHT - 100, 1000, 50, NORMAL_SPIKE, NORMAL, GRAY), 
    (6150, 100, 50, 50, RED_SPIKE, INVERTED, RED),     
    (6300, SCREEN_HEIGHT - 150, 50, 50, RED_SPIKE, NORMAL, RED), 
    (6450, 100, 50, 50, RED_SPIKE, INVERTED, RED),    
    (6600, SCREEN_HEIGHT - 150, 50, 50, RED_SPIKE, NORMAL, RED), 
    (6750, 100, 50, 50, RED_SPIKE, INVERTED, RED),    
    (6900, SCREEN_HEIGHT - 150, 50, 50, RED_SPIKE, NORMAL, RED), 
]
LEVEL_3_END_X = 75000

# --- LEVEL 4 WITH HIDDEN PORTAL ---
LEVEL_4_IMPOSSIBLE = [
    (300, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (550, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE), 
    (1000, SCREEN_HEIGHT - 170, 200, 120, NORMAL_SPIKE, NORMAL, BLUE_PLATFORM),
    (1500, SCREEN_HEIGHT - 100, 100, 50, RED_SPIKE), 
    (2000, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, NORMAL, BLUE_PLATFORM),
    (2300, SCREEN_HEIGHT - 250, 50, 200, NORMAL_SPIKE, NORMAL, PURPLE_PORTAL, PORTAL), 
    
    # --- SHIP SECTION ---
    (2700, 0, 50, 150, NORMAL_SPIKE, NORMAL, GRAY),
    (2700, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE, NORMAL, RED), 
    (3000, SCREEN_HEIGHT - 100, 50, 50, NORMAL_SPIKE, NORMAL, GRAY), 
    (3000, 0, 50, 150, RED_SPIKE, INVERTED, RED), 
    
    # === SECRET PORTAL === 
    # High up in the air, needs precise flight
    (3200, 100, 50, 150, NORMAL_SPIKE, NORMAL, PINK_PORTAL, PORTAL), 

    (3500, 0, 500, 200, NORMAL_SPIKE, NORMAL, GRAY),
    (3500, SCREEN_HEIGHT - 150, 500, 100, NORMAL_SPIKE, NORMAL, GRAY),
    (4200, 0, 50, 50, RED_SPIKE, INVERTED, RED), 
    (4200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE, NORMAL, RED), 
    (4500, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, NORMAL, PURPLE_PORTAL, PORTAL), 
    (4800, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (5000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (5200, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
]
LEVEL_4_END_X = 55000

# --- LEVEL 5 (SECRET) ---
# Super hard gauntlet
LEVEL_5_SECRET = [
    # Immediate triple spike
    (400, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (450, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    
    # Tight Ship Tunnel
    (1000, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, NORMAL, PURPLE_PORTAL, PORTAL),
    
    (1500, 0, 800, 200, NORMAL_SPIKE, NORMAL, GRAY), # Ceiling
    (1500, SCREEN_HEIGHT - 100, 800, 100, NORMAL_SPIKE, NORMAL, GRAY), # Floor
    (1700, 200, 50, 50, RED_SPIKE, INVERTED, RED), # Mid-air spike
    (2000, SCREEN_HEIGHT - 150, 50, 50, RED_SPIKE, NORMAL, RED), # Floor spike
    
    # Fast switch back to cube
    (2500, SCREEN_HEIGHT - 200, 50, 150, NORMAL_SPIKE, NORMAL, PURPLE_PORTAL, PORTAL),
    
    # Precision Jumping
    (3000, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (3300, SCREEN_HEIGHT - 150, 50, 50, NORMAL_SPIKE, BLUE_PLATFORM), # 1 block wide
    (3600, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
    (3900, SCREEN_HEIGHT - 200, 50, 50, NORMAL_SPIKE, BLUE_PLATFORM), # 1 block wide high
    (4500, SCREEN_HEIGHT - 100, 50, 50, RED_SPIKE),
]
LEVEL_5_END_X = 5000

def draw_progress_bar(screen, progress, total_length):
    bar_width = 500; bar_height = 20
    x = (SCREEN_WIDTH - bar_width) // 2; y = 15
    pct = max(0, min(progress / total_length, 1))
    pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (x, y, int(bar_width * pct), bar_height))
    pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2)
    # Centered percentage text below the bar or on it
    pct_text = font_tiny.render(f"{int(pct * 100)}%", True, WHITE)
    screen.blit(pct_text, (x + bar_width // 2 - pct_text.get_width() // 2, y + bar_height + 5))

async def end_screen(message, background=None):
    alpha = 0
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    viewing_mode = False

    while True:
        if not viewing_mode:
            if background:
                screen.blit(background, (0, 0))
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
                if alpha < 200:
                    alpha += 5
            else:
                screen.fill(BLACK)
        
        # Color logic for Secret Found
        msg_color = COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
        if "DEAD" in message or "CRASHED" in message: msg_color = COLOR_OPTIONS[COLOR_DEATH_IDX][1]
        if "SECRET" in message: msg_color = PINK_PORTAL
        
        title_text = font_large.render(message, True, msg_color)
        draw_glitch_text(screen, message, font_large, (SCREEN_WIDTH // 2, 150), msg_color)
        
        restart_text = font_small.render("SPACE/Click: Replay Level", True, GREEN)
        menu_text = font_small.render("M: Main Menu", True, RED)
        
        if "SECRET" in message:
            restart_text = font_small.render("Press SPACE to go to Menu", True, GREEN)
            menu_text = font_small.render("", True, WHITE)

        restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 300, restart_text.get_width(), restart_text.get_height())
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 380, menu_text.get_width(), menu_text.get_height())
        view_rect = pygame.Rect(0, 0, 0, 0)

        if not viewing_mode:
            screen.blit(restart_text, (restart_rect.x, restart_rect.y))
            if "SECRET" not in message:
                screen.blit(menu_text, (menu_rect.x, menu_rect.y))
            if "DEAD" in message:
                view_text = font_small.render("V: View Death Location", True, ORANGE)
                view_rect = pygame.Rect(SCREEN_WIDTH // 2 - view_text.get_width() // 2, 460, view_text.get_width(), view_text.get_height())
                screen.blit(view_text, (view_rect.x, view_rect.y))
        else:
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            
            mode_text = font_small.render("DEATH VIEW MODE", True, ORANGE)
            instr_text = font_tiny.render("Press M or Tap to return to Menu", True, WHITE)
            screen.blit(mode_text, (10, 10))
            screen.blit(instr_text, (10, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if not viewing_mode:
                    if event.key == pygame.K_SPACE: return "MENU" if "SECRET" in message else "RESTART"
                    if event.key == pygame.K_v and "DEAD" in message: viewing_mode = True
                if event.key == pygame.K_m: return "MENU" 
                if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_SHIFT): toggle_fullscreen_handler()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                m_pos = get_mouse_pos(event.pos)
                if viewing_mode: return "MENU"
                if "DEAD" in message and view_rect.collidepoint(m_pos):
                    viewing_mode = True
                elif menu_rect.collidepoint(m_pos) and "SECRET" not in message:
                    return "MENU"
                elif restart_rect.collidepoint(m_pos):
                    return "MENU" if "SECRET" in message else "RESTART"
                else:
                    return "MENU" if "SECRET" in message else "RESTART"
        draw_and_flip(); clock.tick(FPS)
        await asyncio.sleep(0)

async def pause_screen():
    pygame.mixer.music.pause()
    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(5); overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        draw_glitch_text(screen, "PAUSED", font_large, (SCREEN_WIDTH // 2, 200), WHITE)
        cont_text = font_small.render("SPACE/Click: Continue", True, GREEN)
        menu_text = font_small.render("M: Main Menu", True, RED)
        
        cont_rect = pygame.Rect(SCREEN_WIDTH // 2 - cont_text.get_width() // 2, 300, cont_text.get_width(), cont_text.get_height())
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 360, menu_text.get_width(), menu_text.get_height())
        
        screen.blit(cont_text, (cont_rect.x, cont_rect.y))
        screen.blit(menu_text, (menu_rect.x, menu_rect.y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: pygame.mixer.music.unpause(); return "CONTINUE"
                if event.key == pygame.K_m: return "MENU"
                if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_SHIFT): toggle_fullscreen_handler()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                m_pos = get_mouse_pos(event.pos)
                if menu_rect.collidepoint(m_pos):
                    return "MENU"
                else:
                    pygame.mixer.music.unpause()
                    return "CONTINUE"
        draw_and_flip(); clock.tick(FPS)
        await asyncio.sleep(0)

async def spectator_query_screen():
    pygame.mixer.music.pause()
    selected_index = 0; options = ["NO", "YES"]
    while True:
        screen.fill(BLACK)
        draw_glitch_text(screen, "ENTER SPECTATOR MODE?", font_large, (SCREEN_WIDTH // 2, 150), WHITE, max_width=SCREEN_WIDTH - 40)
        desc_text = font_tiny.render("(Phase through objects)", True, GRAY)
        screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 210))

        no_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 50)
        yes_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 50)

        for i, option in enumerate(options):
            color = GREEN if i == selected_index else GRAY
            opt_text = font_large.render(f"> {option} <", True, color) if i == selected_index else font_small.render(option, True, color)
            screen.blit(opt_text, (SCREEN_WIDTH // 2 - opt_text.get_width() // 2, 300 + (i * 80)))

        instr_text = font_small.render("Arrow Keys or Tap options, ENTER to Confirm", True, WHITE)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, SCREEN_HEIGHT - 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN: selected_index = 1 - selected_index 
                if event.key == pygame.K_RETURN: pygame.mixer.music.unpause(); return options[selected_index] 
                if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_SHIFT): toggle_fullscreen_handler()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                m_pos = get_mouse_pos(event.pos)
                if no_rect.collidepoint(m_pos):
                    pygame.mixer.music.unpause()
                    return "NO"
                elif yes_rect.collidepoint(m_pos):
                    pygame.mixer.music.unpause()
                    return "YES"
        draw_and_flip(); clock.tick(FPS)
        await asyncio.sleep(0)

async def font_customizer_menu():
    global CURRENT_TITLE_FONT, CURRENT_TEXT_FONT, FONT_SCALE, TITLE_SCALE
    global COLOR_HAZDASH_IDX, COLOR_DEATH_IDX, COLOR_COMPLETED_IDX, COLOR_GENERAL_IDX
    selected_option = 0
    title_slider = pygame.Rect(300, 160, 200, 10)
    text_slider = pygame.Rect(300, 280, 200, 10)
    dragging_title = False
    dragging_text = False

    while True:
        screen.fill(DARK_GRAY)
        draw_glitch_text(screen, "TEXT & COLOR", font_large, (SCREEN_WIDTH // 2, 40), COLOR_OPTIONS[COLOR_GENERAL_IDX][1])

        def color_name(idx):
            return COLOR_OPTIONS[idx][0]

        def font_disp(f):
            return FONT_DISPLAY_NAMES.get(f, f).upper()

        options_data = [
            ("Title Font", f"[{font_disp(CURRENT_TITLE_FONT)}]"),
            ("Title Size", f"{int(TITLE_SCALE * 100)}%"),
            ("Text Font", f"[{font_disp(CURRENT_TEXT_FONT)}]"),
            ("Text Size", f"{int(FONT_SCALE * 100)}%"),
            ("HAZDASH Color", f"[{color_name(COLOR_HAZDASH_IDX)}]"),
            ("Death Screen Color", f"[{color_name(COLOR_DEATH_IDX)}]"),
            ("Completed Text Color", f"[{color_name(COLOR_COMPLETED_IDX)}]"),
            ("General Text Color", f"[{color_name(COLOR_GENERAL_IDX)}]"),
            ("BACK TO SETTINGS", "")
        ]

        for i, (label, val) in enumerate(options_data):
            opt_color = GREEN if selected_option == i else COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
            if label == "BACK TO SETTINGS":
                txt = font_small.render(label, True, opt_color)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 530))
            elif label == "Title Size":
                txt = font_small.render(f"{label}: {val}", True, opt_color)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 130))
                pygame.draw.rect(screen, GRAY, title_slider)
                pygame.draw.rect(screen, opt_color, (title_slider.x, title_slider.y, int((TITLE_SCALE - 0.5) * 200), title_slider.height))
                pygame.draw.rect(screen, WHITE, (title_slider.x + int((TITLE_SCALE - 0.5) * 200) - 10, title_slider.y - 10, 20, 30))
            elif label == "Text Size":
                txt = font_small.render(f"{label}: {val}", True, opt_color)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 250))
                pygame.draw.rect(screen, GRAY, text_slider)
                pygame.draw.rect(screen, opt_color, (text_slider.x, text_slider.y, int((FONT_SCALE - 0.5) * 200), text_slider.height))
                pygame.draw.rect(screen, WHITE, (text_slider.x + int((FONT_SCALE - 0.5) * 200) - 10, text_slider.y - 10, 20, 30))
            else:
                y_pos = 90
                if i == 0: y_pos = 90
                elif i == 2: y_pos = 210
                elif i == 4: y_pos = 330
                elif i == 5: y_pos = 380
                elif i == 6: y_pos = 430
                elif i == 7: y_pos = 480
                
                txt = font_small.render(f"{label}: {val}", True, opt_color)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y_pos))

        instr_text = font_tiny.render("UP/DOWN to select, LEFT/RIGHT or CLICK to cycle/adjust", True, GRAY)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 565))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_option = (selected_option - 1) % 9
                elif event.key == pygame.K_DOWN: selected_option = (selected_option + 1) % 9
                elif event.key == pygame.K_ESCAPE: return "SETTINGS"
                elif event.key == pygame.K_RETURN:
                    if selected_option == 8: return "SETTINGS"
                    
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    diff = 1 if event.key == pygame.K_RIGHT else -1
                    if selected_option == 0:
                        idx = FONT_OPTIONS.index(CURRENT_TITLE_FONT)
                        CURRENT_TITLE_FONT = FONT_OPTIONS[(idx + diff) % len(FONT_OPTIONS)]
                        refresh_fonts()
                    elif selected_option == 1:
                        TITLE_SCALE = max(0.5, min(1.5, TITLE_SCALE + diff * 0.05))
                        refresh_fonts()
                    elif selected_option == 2:
                        idx = FONT_OPTIONS.index(CURRENT_TEXT_FONT)
                        CURRENT_TEXT_FONT = FONT_OPTIONS[(idx + diff) % len(FONT_OPTIONS)]
                        refresh_fonts()
                    elif selected_option == 3:
                        FONT_SCALE = max(0.5, min(1.5, FONT_SCALE + diff * 0.05))
                        refresh_fonts()
                    elif selected_option == 4:
                        COLOR_HAZDASH_IDX = (COLOR_HAZDASH_IDX + diff) % len(COLOR_OPTIONS)
                    elif selected_option == 5:
                        COLOR_DEATH_IDX = (COLOR_DEATH_IDX + diff) % len(COLOR_OPTIONS)
                    elif selected_option == 6:
                        COLOR_COMPLETED_IDX = (COLOR_COMPLETED_IDX + diff) % len(COLOR_OPTIONS)
                    elif selected_option == 7:
                        COLOR_GENERAL_IDX = (COLOR_GENERAL_IDX + diff) % len(COLOR_OPTIONS)

            if event.type == pygame.MOUSEBUTTONDOWN:
                m_pos = get_mouse_pos(event.pos)
                if event.button == 1:
                    if title_slider.inflate(20, 40).collidepoint(m_pos):
                        selected_option = 1
                        dragging_title = True
                    elif text_slider.inflate(20, 40).collidepoint(m_pos):
                        selected_option = 3
                        dragging_text = True
                    
                    for i in range(9):
                        y_pos = 90
                        if i == 0: y_pos = 90
                        elif i == 1: y_pos = 130
                        elif i == 2: y_pos = 210
                        elif i == 3: y_pos = 250
                        elif i == 4: y_pos = 330
                        elif i == 5: y_pos = 380
                        elif i == 6: y_pos = 430
                        elif i == 7: y_pos = 480
                        elif i == 8: y_pos = 530
                        
                        opt_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, y_pos, 500, 40)
                        if opt_rect.collidepoint(m_pos):
                            selected_option = i
                            if i == 8: return "SETTINGS"
                            elif i == 0:
                                idx = FONT_OPTIONS.index(CURRENT_TITLE_FONT)
                                CURRENT_TITLE_FONT = FONT_OPTIONS[(idx + 1) % len(FONT_OPTIONS)]
                                refresh_fonts()
                            elif i == 2:
                                idx = FONT_OPTIONS.index(CURRENT_TEXT_FONT)
                                CURRENT_TEXT_FONT = FONT_OPTIONS[(idx + 1) % len(FONT_OPTIONS)]
                                refresh_fonts()
                            elif i == 4:
                                COLOR_HAZDASH_IDX = (COLOR_HAZDASH_IDX + 1) % len(COLOR_OPTIONS)
                            elif i == 5:
                                COLOR_DEATH_IDX = (COLOR_DEATH_IDX + 1) % len(COLOR_OPTIONS)
                            elif i == 6:
                                COLOR_COMPLETED_IDX = (COLOR_COMPLETED_IDX + 1) % len(COLOR_OPTIONS)
                            elif i == 7:
                                COLOR_GENERAL_IDX = (COLOR_GENERAL_IDX + 1) % len(COLOR_OPTIONS)

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_title = False
                dragging_text = False
                
            if event.type == pygame.MOUSEMOTION:
                m_pos = get_mouse_pos(event.pos)
                if dragging_title:
                    new_scale = 0.5 + (m_pos[0] - title_slider.x) / title_slider.width
                    TITLE_SCALE = max(0.5, min(1.5, new_scale))
                    refresh_fonts()
                elif dragging_text:
                    new_scale = 0.5 + (m_pos[0] - text_slider.x) / text_slider.width
                    FONT_SCALE = max(0.5, min(1.5, new_scale))
                    refresh_fonts()

        draw_and_flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

async def settings_menu():
    global MUSIC_VOLUME, VIDEO_ENABLED, GLITCH_EFFECT_ENABLED
    selected_option = 0
    vol_slider = pygame.Rect(300, 200, 200, 10)
    dragging_vol = False

    while True:
        screen.fill(DARK_GRAY)
        draw_glitch_text(screen, "SETTINGS", font_large, (SCREEN_WIDTH // 2, 50), COLOR_OPTIONS[COLOR_GENERAL_IDX][1])

        # Volume Slider
        vol_color = GREEN if selected_option == 0 else COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
        vol_label = font_small.render(f"Master Volume: {int(MUSIC_VOLUME * 100)}%", True, vol_color)
        screen.blit(vol_label, (SCREEN_WIDTH // 2 - vol_label.get_width() // 2, 150))
        pygame.draw.rect(screen, GRAY, vol_slider)
        pygame.draw.rect(screen, vol_color, (vol_slider.x, vol_slider.y, int(MUSIC_VOLUME * 200), vol_slider.height))
        pygame.draw.rect(screen, WHITE, (vol_slider.x + int(MUSIC_VOLUME * 200) - 10, vol_slider.y - 10, 20, 30))

        # Video Toggle
        vid_color = GREEN if selected_option == 1 else COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
        vid_status = "ON" if VIDEO_ENABLED else "OFF"
        vid_text = font_small.render(f"Video Backgrounds: [{vid_status}]", True, vid_color)
        screen.blit(vid_text, (SCREEN_WIDTH // 2 - vid_text.get_width() // 2, 250))

        # Glitch Toggle
        glitch_color = GREEN if selected_option == 2 else COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
        glitch_status = "ON" if GLITCH_EFFECT_ENABLED else "OFF"
        glitch_text = font_small.render(f"Glitch Text Effect: [{glitch_status}]", True, glitch_color)
        screen.blit(glitch_text, (SCREEN_WIDTH // 2 - glitch_text.get_width() // 2, 320))

        # Font & Color Customizer sub-tab
        fc_color = GREEN if selected_option == 3 else COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
        fc_text = font_small.render("Text & Color Settings", True, fc_color)
        screen.blit(fc_text, (SCREEN_WIDTH // 2 - fc_text.get_width() // 2, 390))

        # Back Button
        back_color = GREEN if selected_option == 4 else COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
        back_text = font_small.render("BACK TO MENU", True, back_color)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 470))

        instr_text = font_tiny.render("UP/DOWN to select, LEFT/RIGHT to adjust volume, ENTER to enter sub-menu", True, GRAY)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 560))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_option = (selected_option - 1) % 5
                elif event.key == pygame.K_DOWN: selected_option = (selected_option + 1) % 5
                elif event.key == pygame.K_RETURN:
                    if selected_option == 1: VIDEO_ENABLED = not VIDEO_ENABLED
                    elif selected_option == 2: GLITCH_EFFECT_ENABLED = not GLITCH_EFFECT_ENABLED
                    elif selected_option == 3:
                        res = await font_customizer_menu()
                        if res == "QUIT": return "QUIT"
                    elif selected_option == 4: return "MENU"
                elif event.key == pygame.K_ESCAPE: return "MENU"
                
                if selected_option == 0:
                    if event.key == pygame.K_LEFT: MUSIC_VOLUME = max(0.0, MUSIC_VOLUME - 0.05)
                    if event.key == pygame.K_RIGHT: MUSIC_VOLUME = min(1.0, MUSIC_VOLUME + 0.05)
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)

            if event.type == pygame.MOUSEBUTTONDOWN:
                m_pos = get_mouse_pos(event.pos)
                if event.button == 1:
                    if vol_slider.inflate(20, 40).collidepoint(m_pos): selected_option = 0; dragging_vol = True
                    vid_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 250, 300, 40)
                    if vid_rect.collidepoint(m_pos): selected_option = 1; VIDEO_ENABLED = not VIDEO_ENABLED
                    glitch_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 320, 300, 40)
                    if glitch_rect.collidepoint(m_pos): selected_option = 2; GLITCH_EFFECT_ENABLED = not GLITCH_EFFECT_ENABLED
                    fc_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 390, 300, 40)
                    if fc_rect.collidepoint(m_pos):
                        selected_option = 3
                        res = await font_customizer_menu()
                        if res == "QUIT": return "QUIT"
                    back_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 470, 200, 40)
                    if back_rect.collidepoint(m_pos): return "MENU"

            if event.type == pygame.MOUSEBUTTONUP: dragging_vol = False
            if event.type == pygame.MOUSEMOTION and dragging_vol:
                m_pos = get_mouse_pos(event.pos)
                new_vol = (m_pos[0] - vol_slider.x) / vol_slider.width
                MUSIC_VOLUME = max(0.0, min(1.0, new_vol))
                pygame.mixer.music.set_volume(MUSIC_VOLUME)

        draw_and_flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

async def game_loop(current_level_data, level_end_x, level_index):
    global music_enabled
    player = Player(); all_sprites = pygame.sprite.Group(); all_sprites.add(player)
    obstacles = setup_level(current_level_data)
    play_music(level_index, force_restart=True)
    music_btn_rect = pygame.Rect(10, 10, 100, 30)

    cap = None
    if cv2_available and VIDEO_ENABLED and level_index in VIDEO_FILES:
        video_path = os.path.join(SCRIPT_DIR, VIDEO_FILES[level_index])
        if os.path.exists(video_path): cap = cv2.VideoCapture(video_path)
    
    video_timer = 0
    video_surface = None

    pause_btn_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 30)

    running = True
    while running:
        dt = clock.get_time()
        video_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if cap: cap.release()
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: player.jump()
                if event.key == pygame.K_p:
                    action = await pause_screen()
                    if action == "MENU": 
                        if cap: cap.release()
                        return "MENU"
                    if action == "QUIT":
                        if cap: cap.release()
                        return "QUIT"
                if event.key == pygame.K_s:
                    choice = await spectator_query_screen()
                    if choice == "YES": player.spectator_mode = True
                    if choice == "QUIT":
                        if cap: cap.release()
                        return "QUIT"
                if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_SHIFT): toggle_fullscreen_handler()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game_pos = get_mouse_pos(event.pos)
                    if music_btn_rect.collidepoint(game_pos):
                        music_enabled = not music_enabled
                        if music_enabled: play_music(level_index, force_restart=False)
                        else: pygame.mixer.music.stop()
                    elif pause_btn_rect.collidepoint(game_pos):
                        action = await pause_screen()
                        if action == "MENU": 
                            if cap: cap.release()
                            return "MENU"
                        if action == "QUIT":
                            if cap: cap.release()
                            return "QUIT"
                    else: player.jump()

        game_state = player.update(obstacles); obstacles.update()
        
        current_progress = 0
        if obstacles.sprites(): current_progress = SCREEN_WIDTH - obstacles.sprites()[0].rect.x 
        
        # --- CHECK FOR SECRET PORTAL ---
        if game_state == "SECRET_FOUND":
            if cap: cap.release()
            result = await end_screen("SECRET LEVEL FOUND!")
            return "FOUND_SECRET" # Signal to main to unlock it

        if game_state == "DEAD":
            if video_surface and VIDEO_ENABLED: screen.blit(video_surface, (0, 0))
            else: screen.fill(BLACK)
            pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
            obstacles.draw(screen); all_sprites.draw(screen)
            draw_progress_bar(screen, current_progress, level_end_x)
            if player.spectator_mode: screen.blit(font_tiny.render("SPECTATOR MODE", True, BLUE_PLATFORM), (10, 50))
            background_surface = screen.copy()

            if cap: cap.release()
            result = await end_screen("YOU CRASHED!", background=background_surface)
            if result == "RESTART": return "RESTART"
            return result
        
        if current_progress > level_end_x:
            if cap: cap.release()
            result = await end_screen("LEVEL COMPLETE!")
            if result == "RESTART": return "RESTART"
            if result == "MENU": return "COMPLETE_MENU" 
            return result

        if cap and cap.isOpened() and VIDEO_ENABLED:
            if video_timer >= (1000 / VIDEO_FRAMERATE):
                video_timer = 0 
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_surface = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "RGB")
                else: cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if video_surface: screen.blit(video_surface, (0, 0))
            else: screen.fill(BLACK)
        else: screen.fill(BLACK)

        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        obstacles.draw(screen); all_sprites.draw(screen)
        draw_progress_bar(screen, current_progress, level_end_x)
        
        status_text = "ON" if music_enabled else "OFF"; btn_color = GREEN if music_enabled else RED
        # Adjusting Music Status Box to fit text and center
        music_status_txt = font_tiny.render(f"Music: {status_text}", True, btn_color)
        music_btn_rect.w = music_status_txt.get_width() + 10
        pygame.draw.rect(screen, GRAY, music_btn_rect); pygame.draw.rect(screen, WHITE, music_btn_rect, 2)
        screen.blit(music_status_txt, (music_btn_rect.x + 5, music_btn_rect.y + (music_btn_rect.h // 2 - music_status_txt.get_height() // 2)))
        
        # Draw Pause Button for touchscreen devices (at SCREEN_WIDTH - 60, 10, 50, 30)
        pygame.draw.rect(screen, GRAY, pause_btn_rect)
        pygame.draw.rect(screen, WHITE, pause_btn_rect, 2)
        pygame.draw.rect(screen, WHITE, (pause_btn_rect.x + 16, pause_btn_rect.y + 7, 5, 16))
        pygame.draw.rect(screen, WHITE, (pause_btn_rect.x + 28, pause_btn_rect.y + 7, 5, 16))

        if player.spectator_mode: 
            spec_txt = font_tiny.render("SPECTATOR MODE", True, BLUE_PLATFORM)
            screen.blit(spec_txt, (10, 50))
        draw_and_flip(); clock.tick(FPS)
        await asyncio.sleep(0)
        
    if cap: cap.release()
    return "QUIT"

async def password_entry(unlocked_levels):
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 50)
    text = ''; message = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", unlocked_levels
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if text.lower() == LEVEL_4_PASSWORD:
                        unlocked_levels.add(3); await asyncio.sleep(1.5); return "MENU", unlocked_levels 
                    else: message = "Incorrect Password."; text = '' 
                elif event.key == pygame.K_BACKSPACE: text = text[:-1]
                else: text += event.unicode
                if event.key == pygame.K_m: return "MENU", unlocked_levels 
                if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_SHIFT): toggle_fullscreen_handler()

        screen.fill(BLACK)
        draw_glitch_text(screen, "ENTER PASSWORD", font_large, (SCREEN_WIDTH // 2, 100), WHITE)
        txt_surface = font_small.render(text, True, WHITE)
        input_box.w = max(300, txt_surface.get_width()+10); input_box.x = SCREEN_WIDTH // 2 - input_box.w // 2
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5)); pygame.draw.rect(screen, GRAY, input_box, 2)
        msg_text = font_small.render(message, True, RED if "Incorrect" in message else GOLD)
        screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 400))
        instr_text = font_small.render("Press ENTER to submit | M for Menu", True, GRAY)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, SCREEN_HEIGHT - 50))
        draw_and_flip(); clock.tick(FPS)
        await asyncio.sleep(0)

async def main_menu(completed_levels, password_unlocked_level_4, secret_unlocked):
    menu_active = True; selected_level = 1 
    
    level_configs = [
        ("LEVEL 1 - EASY", LEVEL_1_EASY, LEVEL_1_END_X),
        ("LEVEL 2 - MEDIUM", LEVEL_2_MEDIUM, LEVEL_2_END_X), 
        ("LEVEL 3 - HARD (SHIP)", LEVEL_3_HARD, LEVEL_3_END_X), 
        ("LEVEL 4 - IMPOSSIBLE", LEVEL_4_IMPOSSIBLE, LEVEL_4_END_X),
    ]
    
    keybinds = [
        "SPACE/Click: Jump",
        "P: Pause Game",
        "S: Spectator Mode",
        "M: Menu (Screens)",
        "Shift+O: Fullscreen"
    ]
    
    play_music("MENU", force_restart=False)
    is_level_4_unlocked = (len(completed_levels) >= 3) or password_unlocked_level_4
    
    menu_options = [config[0] for config in level_configs]
    menu_options.append("UNLOCK LEVEL 4 (Password)")
    
    # Secret Level Option (Index 5 visually, Index 4 logically)
    if secret_unlocked:
        menu_options.append("SECRET LEVEL (FOUND!)")
    else:
        menu_options.append("??? (Hidden in Lvl 4)")
    
    menu_y_start = 200; menu_item_height = 60
    slider_x = 700; slider_width = 10; slider_track_height = 300; slider_thumb_height = slider_track_height / len(menu_options)
    settings_rect = pygame.Rect(SCREEN_WIDTH - 60, 20, 40, 40)

    while menu_active:
        screen.fill(BLACK)
        draw_glitch_text(screen, "HAZDASH", font_large, (SCREEN_WIDTH // 2, 50), COLOR_OPTIONS[COLOR_HAZDASH_IDX][1])
        
        # Display Keybinds on the left
        for idx, bind in enumerate(keybinds):
            bind_txt = font_tiny.render(bind, True, COLOR_OPTIONS[COLOR_GENERAL_IDX][1])
            screen.blit(bind_txt, (20, 400 + idx * 30))

        gear_color = GREEN if selected_level == 0 else GRAY
        draw_gear_icon(screen, settings_rect.x, settings_rect.y, 40, gear_color)

        for i, name in enumerate(menu_options):
            display_name = name; color = COLOR_OPTIONS[COLOR_GENERAL_IDX][1]
            if i == 2: display_name = "LEVEL 3 - HARD SHIP"
            
            is_locked = False
            if i == 3 and not is_level_4_unlocked: is_locked = True
            if i == 4 and is_level_4_unlocked: is_locked = True
            if i == 5 and not secret_unlocked: is_locked = True # Secret level lock
            
            if i == 4: color = ORANGE; 
            if i == 4 and is_level_4_unlocked: display_name = "UNLOCK LEVEL 4 (Password is already used)"
            
            if is_locked: color = GRAY
            if i == selected_level - 1: color = GREEN
            if i < 3 and i in completed_levels: display_name += " (Completed)"; color = COLOR_OPTIONS[COLOR_COMPLETED_IDX][1] 
            if i == 3 and is_level_4_unlocked: display_name += " (Unlocked!)"; color = COLOR_OPTIONS[COLOR_COMPLETED_IDX][1]
            if i == 5 and secret_unlocked: color = PINK_PORTAL # Special color for secret level
            
            level_text = font_small.render(display_name, True, color)
            text_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y_start + i * menu_item_height + 20))
            screen.blit(level_text, text_rect)

        pygame.draw.rect(screen, GRAY, (slider_x, menu_y_start, slider_width, slider_track_height))
        if selected_level > 0:
            thumb_y = menu_y_start + ((selected_level - 1) * slider_thumb_height)
            pygame.draw.rect(screen, GREEN, (slider_x, thumb_y, slider_width, slider_thumb_height))
        
        instr_text = font_small.render("UP/DOWN to Select, SPACE/Click to Play", True, GRAY)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, SCREEN_HEIGHT - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", None, None, False, False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: selected_level = max(0, selected_level - 1) 
                elif event.key == pygame.K_DOWN: 
                    selected_level = min(len(menu_options), selected_level + 1)
                    if selected_level == 0: selected_level = 1 
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if selected_level == 0:
                        res = await settings_menu()
                        if res == "QUIT": return "QUIT", None, None, False, False
                    else:
                        chosen_index = selected_level - 1
                        # Lvl 1-4 logic
                        if chosen_index <= 3:
                            if chosen_index == 3 and not is_level_4_unlocked: continue
                            return level_configs[chosen_index][1], level_configs[chosen_index][2], chosen_index, password_unlocked_level_4, False
                        # Password logic
                        elif chosen_index == 4:
                            if is_level_4_unlocked: continue
                            return "PASSWORD", None, None, password_unlocked_level_4, False
                        # Secret Level logic
                        elif chosen_index == 5:
                            if secret_unlocked:
                                return LEVEL_5_SECRET, LEVEL_5_END_X, 4, password_unlocked_level_4, False
                            else: continue

                if event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_SHIFT): toggle_fullscreen_handler()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = get_mouse_pos(event.pos)
                if settings_rect.collidepoint(mouse_pos):
                    res = await settings_menu()
                    if res == "QUIT": return "QUIT", None, None, False, False
                
                for i in range(len(menu_options)):
                    rect_center_y = menu_y_start + i * menu_item_height + 20
                    item_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, rect_center_y - 20, 400, 40)
                    if item_rect.collidepoint(mouse_pos):
                        selected_level = i + 1; chosen_index = selected_level - 1
                        if chosen_index <= 3:
                            if chosen_index == 3 and not is_level_4_unlocked: continue
                            return level_configs[chosen_index][1], level_configs[chosen_index][2], chosen_index, password_unlocked_level_4, False
                        elif chosen_index == 4:
                            if is_level_4_unlocked: continue
                            return "PASSWORD", None, None, password_unlocked_level_4, False
                        elif chosen_index == 5:
                            if secret_unlocked: return LEVEL_5_SECRET, LEVEL_5_END_X, 4, password_unlocked_level_4, False
                            else: continue
        draw_and_flip(); clock.tick(FPS)
        await asyncio.sleep(0)
    return "QUIT", None, None, False, False

async def main():
    completed_levels = set(); password_unlocked_level_4 = False; secret_unlocked = False
    current_data = None; current_end_x = None; current_level_idx = None 
    while True:
        if current_data is None: 
            current_data, current_end_x, current_level_idx, password_unlocked_level_4, _ = await main_menu(completed_levels, password_unlocked_level_4, secret_unlocked) 
        
        if current_data == "QUIT": break
        if current_data == "PASSWORD":
             unlocked_set = set(); 
             if password_unlocked_level_4: unlocked_set.add(3) 
             result, new_unlocked_set = await password_entry(unlocked_set)
             if 3 in new_unlocked_set: password_unlocked_level_4 = True 
             current_data = None 
        elif current_data:
            try: 
                result = await game_loop(current_data, current_end_x, current_level_idx) 
            except Exception as e: print(f"Error: {e}"); return 
            
            if result == "QUIT": break
            elif result == "MENU": current_data = None 
            elif result == "FOUND_SECRET":
                secret_unlocked = True
                current_data = None
            elif result == "COMPLETE_MENU":
                if current_level_idx is not None and current_level_idx != 4: # Don't mark secret as normal complete
                    completed_levels.add(current_level_idx)
                current_data = None
            elif result == "RESTART": pass 
    pygame.quit(); sys.exit()

if __name__ == "__main__": asyncio.run(main())