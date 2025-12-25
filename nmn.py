import pygame
import random
import os
import math
# --- 1. BASIC SETUP ---
WIDTH = 800
HEIGHT = 600
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 150, 255)
GREEN = (0, 255, 0)
BRIGHT_GREEN = (50, 255, 50) 
COLOR_INACTIVE = (100, 100, 100)
COLOR_ACTIVE = (0, 200, 0) 
COLOR_SELECTED = (255, 215, 0)
PURPLE = (128, 0, 128) # Màu cho Boss 2
# Game Clock
clock = pygame.time.Clock()
FPS = 60
# Font Settings
font_name = None 
def draw_text(surf, text, size, x, y, color=WHITE):
    global font_name
    if font_name is None:
        font_name = pygame.font.match_font('arial')
        
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_health_bar(surf, x, y, current_hp, max_hp):
    """Draws a small health bar for the Player."""
    if current_hp < 0: current_hp = 0
    if current_hp > max_hp: current_hp = max_hp
    
    BAR_WIDTH = 100
    BAR_HEIGHT = 10
    
    # --- 🔴 SỬA LỖI CHIA CHO 0 NẾU max_hp = 0 (hiếm) ---
    percent = 0
    if max_hp > 0:
        percent = current_hp / max_hp
        
    fill = percent * BAR_WIDTH
    
    color = GREEN
    if percent < 0.25: color = RED
    elif percent < 0.5: color = YELLOW
    
    outline_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_boss_health_bar(surf, x, y, current_hp, max_hp):
    """Draws a large health bar for the Boss."""
    if current_hp < 0: current_hp = 0
    BAR_WIDTH = WIDTH - 100
    BAR_HEIGHT = 15
    
    percent = 0
    if max_hp > 0:
        percent = current_hp / max_hp
        
    fill = percent * BAR_WIDTH
    outline_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    pygame.draw.rect(surf, BLACK, outline_rect)
    color = YELLOW
    if percent < 0.25: color = RED
    elif percent < 0.5: color = ORANGE
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_player_hud(surf, x, y, player_obj, label, color):
    """Draw a compact HUD for a player: colored square, label, rounded health bar and numeric HP."""
    if not player_obj:
        return
    hp = getattr(player_obj, 'hp', 0)
    max_hp = getattr(player_obj, 'max_hp', 0)
    if hp < 0: hp = 0
    percent = 0
    if max_hp > 0:
        percent = max(0.0, min(1.0, hp / max_hp))

    # Colored avatar box
    avatar_rect = pygame.Rect(x, y, 24, 24)
    try:
        pygame.draw.rect(surf, color, avatar_rect, border_radius=4)
        pygame.draw.rect(surf, WHITE, avatar_rect, 2, border_radius=4)
    except Exception:
        pygame.draw.rect(surf, color, avatar_rect)
        pygame.draw.rect(surf, WHITE, avatar_rect, 2)

    # Label
    draw_text(surf, label, 18, x + 12, y - 18)

    # Health bar
    BAR_W = 140
    BAR_H = 14
    bar_x = x + 34
    bar_y = y
    try:
        # background
        pygame.draw.rect(surf, (30, 30, 30), (bar_x, bar_y, BAR_W, BAR_H), border_radius=6)
        # fill
        fill_w = int(percent * BAR_W)
        fill_color = GREEN if percent > 0.5 else (YELLOW if percent > 0.25 else RED)
        pygame.draw.rect(surf, fill_color, (bar_x, bar_y, fill_w, BAR_H), border_radius=6)
        # border
        pygame.draw.rect(surf, WHITE, (bar_x, bar_y, BAR_W, BAR_H), 2, border_radius=6)
    except Exception:
        pygame.draw.rect(surf, (30, 30, 30), (bar_x, bar_y, BAR_W, BAR_H))
        fill_w = int(percent * BAR_W)
        pygame.draw.rect(surf, GREEN, (bar_x, bar_y, fill_w, BAR_H))
        pygame.draw.rect(surf, WHITE, (bar_x, bar_y, BAR_W, BAR_H), 2)

    # Numeric HP
    hp_text = f"{int(hp)}/{int(max_hp)}"
    draw_text(surf, hp_text, 16, bar_x + BAR_W + 40, bar_y - 2)


def draw_vertical_health_bar(surf, x, y, width, height, current_hp, max_hp):
    """Draw a vertical health bar with gradient from green (top) to red (bottom).
    current_hp and max_hp determine filled portion (bottom-up)."""
    if max_hp <= 0:
        percent = 0
    else:
        percent = max(0.0, min(1.0, current_hp / max_hp))

    # Background panel
    try:
        pygame.draw.rect(surf, (30, 30, 30), (x, y, width, height), border_radius=6)
        pygame.draw.rect(surf, WHITE, (x, y, width, height), 2, border_radius=6)
    except Exception:
        pygame.draw.rect(surf, (30, 30, 30), (x, y, width, height))
        pygame.draw.rect(surf, WHITE, (x, y, width, height), 2)

    # Fill with gradient: draw horizontal slices from bottom to top
    fill_h = int(percent * height)
    # Draw from bottom (red) up to filled height (green at top)
    for i in range(fill_h):
        t = i / max(1, height - 1)  # 0 at bottom, 1 at top
        # interpolate color: bottom -> RED, top -> GREEN
        r = int(RED[0] * (1 - t) + GREEN[0] * t)
        g = int(RED[1] * (1 - t) + GREEN[1] * t)
        b = int(RED[2] * (1 - t) + GREEN[2] * t)
        slice_y = y + height - 1 - i
        try:
            surf.fill((r, g, b), (x + 2, slice_y, width - 4, 1))
        except Exception:
            pygame.draw.rect(surf, (r, g, b), (x + 2, slice_y, max(1, width - 4), 1))

    # Numeric HP centered above the bar
    hp_text = f"{int(current_hp)}/{int(max_hp)}"
    draw_text(surf, hp_text, 14, x + width // 2, y - 18)


def draw_text_shadow(surf, text, size, x, y, color=WHITE, shadow=(0,0,0), shadow_offset=(2,2), center=True):
    """Draw text with a slight shadow for better legibility on busy backgrounds."""
    global font_name
    if font_name is None:
        font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    shadow_surf = font.render(text, True, shadow)
    text_surf = font.render(text, True, color)
    shadow_rect = shadow_surf.get_rect()
    text_rect = text_surf.get_rect()
    if center:
        shadow_rect.center = (x + shadow_offset[0], y + shadow_offset[1])
        text_rect.center = (x, y)
    else:
        shadow_rect.topleft = (x + shadow_offset[0], y + shadow_offset[1])
        text_rect.topleft = (x, y)
    surf.blit(shadow_surf, shadow_rect)
    surf.blit(text_surf, text_rect)


def draw_hud_panel(surf, x, y, w, h, title=None):
    """Draw a translucent panel used for Score / Wave to group info."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((10, 10, 20, 160))
    try:
        surf.blit(panel, (x, y))
        pygame.draw.rect(surf, WHITE, (x, y, w, h), 2, border_radius=6)
    except Exception:
        surf.blit(panel, (x, y))
        pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)
    if title:
        draw_text_shadow(surf, title, 16, x + 10, y + 6, color=WHITE, shadow=(0,0,0), center=False)


def draw_star_icon(surf, x, y, size, color):
    """Draw a simple 5-point star centered at x,y"""
    cx, cy = x, y
    pts = []
    for i in range(5):
        angle = i * (2 * math.pi / 5) - math.pi / 2
        outer_x = cx + math.cos(angle) * size
        outer_y = cy + math.sin(angle) * size
        pts.append((outer_x, outer_y))
        angle2 = angle + math.pi / 5
        inner_x = cx + math.cos(angle2) * (size * 0.5)
        inner_y = cy + math.sin(angle2) * (size * 0.5)
        pts.append((inner_x, inner_y))
    try:
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, WHITE, pts, 1)
    except Exception:
        pass


def draw_wave_icon(surf, x, y, width, height, color):
    """Draw a small wave-like icon (simple sine curve approximation)."""
    points = []
    steps = 8
    for i in range(steps + 1):
        t = i / steps
        px = x + t * width
        py = y + math.sin(t * math.pi * 2) * (height / 4)
        points.append((px, py))
    try:
        pygame.draw.lines(surf, color, False, points, 2)
    except Exception:
        pass


def get_live_player_obj():
    """Return the first alive player object (player, then player2) or None."""
    try:
        if 'player' in globals() and player is not None and getattr(player, 'hp', 0) > 0 and getattr(player, 'alive', lambda: True)():
            return player
    except Exception:
        pass
    try:
        if 'player2' in globals() and player2 is not None and getattr(player2, 'hp', 0) > 0 and getattr(player2, 'alive', lambda: True)():
            return player2
    except Exception:
        pass
    return None


# --- (!!!) HÀM ĐÃ THAY ĐỔI (!!!) ---
def game_over_screen():
    """Hiển thị màn hình Game Over (Bình thường hoặc Đặc biệt) và chờ input."""
    
    global final_boss_defeated # Lấy cờ toàn cục
    
    play_again_text = "Press [ENTER] to Play Again, [ESC] to Quit" if current_language == "en" else "Nhấn [ENTER] để chơi lại, [ESC] để thoát"

    if final_boss_defeated:
        # --- 1. MÀN HÌNH KẾT THÚC ĐẶC BIỆT ---
        
        # (a) Nổ trắng màn hình và giữ 0.5 giây
        screen.fill(WHITE)
        pygame.display.flip()
        pygame.time.wait(500) # Giữ màn hình trắng 0.5 giây

        # (b) Vẽ chữ "Chúc mừng" (màu đen)
        screen.fill(WHITE) # Giữ nền trắng
        game_over_text = "CHÚC MỪNG BẠN ĐÃ THUA" if current_language == "vi" else "CONGRATULATIONS, YOU LOST"
        
        # Chú ý: Dùng màu BLACK để chữ nổi lên nền WHITE
        draw_text(screen, game_over_text, 50, WIDTH // 2, HEIGHT // 3, BLACK) 
        draw_text(screen, play_again_text, 22, WIDTH // 2, HEIGHT * 3 / 4, BLACK)

    else:
        # --- 2. MÀN HÌNH GAME OVER BÌNH THƯỜNG ---
        screen.blit(background_img, (0, 0))
        game_over_text = "GAME OVER" if current_language == "en" else "KẾT THÚC"
        
        draw_text(screen, game_over_text, 64, WIDTH // 2, HEIGHT // 4)
        draw_text(screen, f"Final Score: {score}", 30, WIDTH // 2, HEIGHT // 2)
        draw_text(screen, play_again_text, 22, WIDTH // 2, HEIGHT * 3 / 4)

    # (c) Hiển thị mọi thứ lên màn hình
    pygame.display.flip()
    
    # --- 3. VÒNG LẶP CHỜ INPUT (Dùng chung cho cả 2) ---
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: # ENTER Key
                    final_boss_defeated = False # !! Quan trọng: Reset cờ
                    waiting = False
                    return True # Restart
                if event.key == pygame.K_ESCAPE: # ESC Key
                    final_boss_defeated = False # !! Quan trọng: Reset cờ
                    waiting = False
                    return False # Quit game

# --- (!!!) HÀM ĐÃ THAY ĐỔI (!!!) ---
def reset_game():
    """Resets variables and sprite groups to start a new game."""
    global all_sprites, mobs, player_bullets, enemy_bullets, vfx_group, pickups_group
    global player, player2, score, game_over, current_wave, boss, boss_defeated, player_is_upgraded
    global screen_shake_duration, screen_shake_intensity, boss_coming, boss_warning_start
    global elite_wave_count, boss_2, boss_2_coming, boss_2_defeated
    global final_boss_defeated # <-- (1) THÊM DÒNG NÀY

    all_sprites.empty()
    mobs.empty()
    player_bullets.empty()
    enemy_bullets.empty()
    vfx_group.empty()
    try:
        pickups_group.empty()
    except Exception:
        pass

    score = 0
    game_over = False
    current_wave = 0
    boss = None
    boss_defeated = False 
    player_is_upgraded = False 
    screen_shake_duration = 0
    screen_shake_intensity = 0
    boss_coming = False
    boss_warning_start = 0
    
    elite_wave_count = 0
    boss_2 = None
    boss_2_coming = False
    boss_2_defeated = False
    final_boss_defeated = False # <-- (2) THÊM DÒNG NÀY

    player = Player()
    all_sprites.add(player)

    # --- Co-op: create Player 2 (local) if enabled ---
    if enable_coop:
        try:
            player2 = Player2()
            all_sprites.add(player2)
        except Exception:
            # If Player2 class not available for some reason, ignore
            player2 = None
    else:
        player2 = None

    create_enemy_formation()
    if music_loaded and music_enabled: 
        pygame.mixer.music.play(loops=-1)


# --- 1. DUMMY ASSET INITIALIZATION ---
game_folder = os.path.dirname(__file__)
assets_folder = os.path.join(game_folder, "assets")

player_img = pygame.Surface((50, 40)); player_img.fill(BLUE)
player_upgraded_img = pygame.Surface((60, 50)); player_upgraded_img.fill(GREEN) 
bullet_img = pygame.Surface((8, 18)); bullet_img.fill(GREEN)
# Drumstick (health pickup) dummy image
drumstick_img = pygame.Surface((20, 20), pygame.SRCALPHA)
drumstick_img.fill((0, 0, 0, 0))
try:
    pygame.draw.circle(drumstick_img, (180, 90, 20), (8, 8), 7)
    pygame.draw.rect(drumstick_img, (220, 200, 180), (12, 5, 6, 10))
except Exception:
    drumstick_img.fill((180, 90, 20))
enemy_img = pygame.Surface((40, 35)); enemy_img.fill(RED)
elite_enemy_img = pygame.Surface((50, 45)); elite_enemy_img.fill(ORANGE) 
enemy_bullet_img = pygame.Surface((8, 18)); enemy_bullet_img.fill(WHITE)
background_img = pygame.Surface((WIDTH, HEIGHT)); background_img.fill(BLACK)
boss_img = pygame.Surface((120, 100)); boss_img.fill(YELLOW) 
boss_2_img = pygame.Surface((150, 130)); boss_2_img.fill(PURPLE) 

# Initialize Dummy Sounds
shoot_sound = type('DummySound', (object,), {'play': lambda self: None})()
expl_sound = type('DummySound', (object,), {'play': lambda self: None})()
boss_alert_sound = type('DummySound', (object,), {'play': lambda self: None})() 
music_loaded = False


# --- 2. ASSET LOADING FUNCTION ---
def load_all_assets():
    """
    Tải tất cả các file ảnh và âm thanh thật từ ổ đĩa.
    """
    global player_img, player_upgraded_img, enemy_img, elite_enemy_img
    global bullet_img, enemy_bullet_img, background_img, boss_img, boss_2_img 
    global shoot_sound, expl_sound, boss_alert_sound, music_loaded
    global assets_folder 
    
    try:
        # Load Images
        player_img = pygame.image.load(os.path.join(assets_folder, "player_ship.png")).convert_alpha()
        player_upgraded_img_raw = pygame.image.load(os.path.join(assets_folder, "player_upgraded_ship.png")).convert_alpha()
        player_upgraded_img = player_upgraded_img_raw.copy()
        player_upgraded_img.fill(GREEN, special_flags=pygame.BLEND_RGB_MULT)
        enemy_img_raw = pygame.image.load(os.path.join(assets_folder, "enemy_ship.png")).convert_alpha()
        enemy_img = enemy_img_raw.copy()
        enemy_img.fill(GREEN, special_flags=pygame.BLEND_RGB_MULT) 
        elite_enemy_img_raw = pygame.image.load(os.path.join(assets_folder, "elite_enemy_ship.png")).convert_alpha()
        elite_enemy_img = elite_enemy_img_raw.copy()
        elite_enemy_img.fill(GREEN, special_flags=pygame.BLEND_RGB_MULT)
        elite_enemy_img = pygame.transform.rotate(elite_enemy_img, 270) 
        bullet_img_raw = pygame.image.load(os.path.join(assets_folder, "bullet.png")).convert_alpha()
        bullet_img = bullet_img_raw.copy()
        bullet_img.fill(GREEN, special_flags=pygame.BLEND_RGB_MULT) 
        try:
            drumstick_img = pygame.image.load(os.path.join(assets_folder, "drumstick.png")).convert_alpha()
            drumstick_img = pygame.transform.scale(drumstick_img, (20, 20))
        except Exception:
            # keep dummy if not found
            pass
        enemy_bullet_img = pygame.image.load(os.path.join(assets_folder, "enemy_bullet.png")).convert_alpha()
        bg_raw = pygame.image.load(os.path.join(assets_folder, "background.png")).convert()
        background_img = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
        boss_img = pygame.image.load(os.path.join(assets_folder, "boss_ship.png")).convert_alpha() 
        
        try:
            boss_2_img = pygame.image.load(os.path.join(assets_folder, "boss_ship_2.png")).convert_alpha()
        except:
            print("Warning: boss_ship_2.png not found. Using dummy color.")
            boss_2_img = pygame.transform.scale(boss_img, (150, 130)) 
            boss_2_img.fill(PURPLE, special_flags=pygame.BLEND_RGB_MULT) 
            
        # Load Sounds
        try:
            shoot_sound = pygame.mixer.Sound(os.path.join(assets_folder, "laser_sound.wav"))
            expl_sound = pygame.mixer.Sound(os.path.join(assets_folder, "explosion_sound.wav"))
            boss_alert_sound = pygame.mixer.Sound(os.path.join(assets_folder, "boss_warning.wav"))
            boss_alert_sound.set_volume(0.8) 
        except Exception:
            print("Warning: Could not load one or more sound files.")
            pass 

        try:
            pygame.mixer.music.load(os.path.join(assets_folder, "background_music.ogg"))
            pygame.mixer.music.set_volume(0.5)
            music_loaded = True
        except pygame.error as e: 
            print(f"CẢNH BÁO: Không thể tải nhạc nền. Lỗi: {e}") 
            pass
            
        print("Asset loading complete.")
    except pygame.error as e:
        print(f"Warning: Could not load one or more main image files: {e}.")


# --- 2. SPRITE CLASSES ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        global player_is_upgraded
        self.upgraded = player_is_upgraded
        self.set_image_and_stats()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 15
        self.speedx = 0
        self.hp = 100
        self.max_hp = 100 
        # trail timer for ship trail VFX
        self.trail_timer = 0

    def set_image_and_stats(self):
        old_center = self.rect.center if hasattr(self, 'rect') else (0, 0)
        if self.upgraded:
            self.image = pygame.transform.scale(player_upgraded_img, (60, 50))
        else:
            self.image = pygame.transform.scale(player_img, (50, 40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() 
        if old_center != (0, 0):
            self.rect.center = old_center

    def update(self):
        # Free movement: allow left/right and up/down with arrow keys
        self.speedx = 0
        self.speedy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.speedx = -6
        if keys[pygame.K_RIGHT]: self.speedx = 6
        if keys[pygame.K_UP]: self.speedy = -6
        if keys[pygame.K_DOWN]: self.speedy = 6
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Keep inside screen bounds (allow full vertical movement)
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

        # Spawn a small trail particle while moving (every few frames)
        try:
            if self.speedx != 0 or self.speedy != 0:
                if getattr(self, 'trail_timer', 0) <= 0:
                    self.trail_timer = 4
                    tcol = BLUE if not getattr(self, 'upgraded', False) else GREEN
                    trail = TrailParticle(self.rect.center, color=tcol, size=int(self.rect.width * 0.4))
                    all_sprites.add(trail)
                    vfx_group.add(trail)
                else:
                    self.trail_timer -= 1
        except Exception:
            pass

    def shoot(self):
        if self.upgraded:
            bullet1 = PlayerBullet(self.rect.left + 5, self.rect.centery, is_upgraded=True)
            bullet2 = PlayerBullet(self.rect.centerx, self.rect.top, is_upgraded=True)
            bullet3 = PlayerBullet(self.rect.right - 5, self.rect.centery, is_upgraded=True)
            all_sprites.add(bullet1, bullet2, bullet3)
            player_bullets.add(bullet1, bullet2, bullet3)
        else:
            bullet = PlayerBullet(self.rect.centerx, self.rect.top, is_upgraded=False)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
        shoot_sound.play()

# --- NEW: Player2 (Co-op local player) ---
class Player2(pygame.sprite.Sprite):
    """Player 2: controls W/A/S/D to move, LEFT SHIFT to shoot.
    Uses same PlayerBullet and shared player_bullets group.
    Honors player_is_upgraded the same way as Player."""
    def __init__(self):
        super().__init__()
        global player_is_upgraded
        self.upgraded = player_is_upgraded
        self.set_image_and_stats()
        # Spawn slightly offset to the left so two players do not overlap
        self.rect.centerx = WIDTH // 2 - 100
        self.rect.bottom = HEIGHT - 15
        self.speedx = 0
        self.speedy = 0
        self.hp = 100
        self.max_hp = 100
        # trail timer for ship trail VFX
        self.trail_timer = 0

    def set_image_and_stats(self):
        # Use same images but make a red-tinted copy so Player2 is visually distinct
        old_center = self.rect.center if hasattr(self, 'rect') else (0, 0)
        if self.upgraded:
            img = pygame.transform.scale(player_upgraded_img, (60, 50)).copy()
        else:
            img = pygame.transform.scale(player_img, (50, 40)).copy()
        try:
            img.fill(RED, special_flags=pygame.BLEND_RGB_MULT)
        except Exception:
            pass
        img.set_colorkey(BLACK)
        self.image = img
        self.rect = self.image.get_rect()
        if old_center != (0, 0):
            self.rect.center = old_center

    def update(self):
        # WASD movement (independent vertical + horizontal movement)
        keys = pygame.key.get_pressed()
        self.speedx = 0
        self.speedy = 0
        if keys[pygame.K_a]: self.speedx = -6
        if keys[pygame.K_d]: self.speedx = 6
        if keys[pygame.K_w]: self.speedy = -6
        if keys[pygame.K_s]: self.speedy = 6
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Keep inside screen
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

        # Spawn trail for player2 as well
        try:
            if self.speedx != 0 or self.speedy != 0:
                if getattr(self, 'trail_timer', 0) <= 0:
                    self.trail_timer = 4
                    tcol = RED if not getattr(self, 'upgraded', False) else BRIGHT_GREEN
                    trail = TrailParticle(self.rect.center, color=tcol, size=int(self.rect.width * 0.4))
                    all_sprites.add(trail)
                    vfx_group.add(trail)
                else:
                    self.trail_timer -= 1
        except Exception:
            pass

    def shoot(self):
        # Use same upgraded logic as Player
        if self.upgraded:
            bullet1 = PlayerBullet(self.rect.left + 5, self.rect.centery, is_upgraded=True)
            bullet2 = PlayerBullet(self.rect.centerx, self.rect.top, is_upgraded=True)
            bullet3 = PlayerBullet(self.rect.right - 5, self.rect.centery, is_upgraded=True)
            all_sprites.add(bullet1, bullet2, bullet3)
            player_bullets.add(bullet1, bullet2, bullet3)
        else:
            bullet = PlayerBullet(self.rect.centerx, self.rect.top, is_upgraded=False)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
        shoot_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img, (40, 35))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.start_x, self.start_y = x, y
        self.rect.x, self.rect.y = x, y
        # Wave movement parameters (slow/choreographed, upper-half only)
        self.amplitude = random.uniform(12, 18)
        # slower, calmer movement suitable for upper-half choreography
        self.frequency = random.uniform(0.00004, 0.00008)
        self.time_offset = random.uniform(0, 2 * math.pi)
        # very slow downward drift; will be clamped to upper half
        self.downward_speed = random.uniform(0.01, 0.06)
        # State machine for Galaga-like behavior
        self.state = 'formation'  # 'formation' | 'dive' | 'evade'
        self.dive_target = None
        self.vx = 0.0
        self.vy = 0.0
        self.base_dive_speed = random.uniform(3.5, 5.0)
        # trajectory path params for dive
        self.path_type = None  # 'arc' or 'sine'
        self.path_t = 0.0
        self.path_duration = 140
        self.path_start = (self.rect.centerx, self.rect.centery)
        self.path_control = (self.rect.centerx, self.rect.centery)
        self.path_target = (self.rect.centerx, self.rect.centery)
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randrange(1400, 2600)
        self.dodge_cooldown = 0

    def update(self):
        now = pygame.time.get_ticks()
        # Simple dodge cooldown decrement
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1

        # Behavior scales slightly with wave number
        wave_factor = 1.0 + (current_wave * 0.12)

        if self.state == 'formation':
            time_value = now * self.frequency * wave_factor
            sine_offset = self.amplitude * math.sin(time_value + self.time_offset)
            self.rect.x = int(self.start_x + sine_offset)
            # slowly drift down
            self.start_y += self.downward_speed * wave_factor
            self.rect.y = int(self.start_y)

            # occasionally perform an attack along a preset trajectory (stay in upper half)
            if random.random() < 0.0009 * wave_factor:
                # begin dive following a predefined trajectory (arc or sine-offset)
                self.state = 'dive'
                # choose a target near the player if exists
                # target y MUST stay in the upper half of the screen
                top_limit = max(40, HEIGHT // 4)
                bottom_limit = max(80, HEIGHT // 2 - 60)
                target_obj = get_live_player_obj()
                if target_obj is not None:
                    tx = target_obj.rect.centerx + random.randrange(-30, 30)
                    ty = min(bottom_limit, max(top_limit, target_obj.rect.centery + random.randrange(-20, 20)))
                else:
                    tx = self.rect.centerx
                    ty = random.randrange(top_limit, bottom_limit)
                self.dive_target = (tx, ty)
                # choose path type
                self.path_type = random.choice(['arc', 'sine'])
                self.path_start = (self.rect.centerx, self.rect.centery)
                self.path_target = (tx, ty)
                # duration scales with wave but keep it long so motion remains slow
                base_dur = random.randint(140, 220)
                self.path_duration = max(80, int(base_dur / (1.0 + current_wave * 0.08)))
                self.path_t = 0.0
                if self.path_type == 'arc':
                    # control point above the line to create an arching curve
                    midx = (self.path_start[0] + tx) / 2
                    midy = (self.path_start[1] + ty) / 2
                    # offset control inward/upward but not too far so arc stays in upper half
                    offset = -random.uniform(40, 140)
                    self.path_control = (midx, max(top_limit, midy + offset))
                else:
                    # sine params: amplitude perpendicular to line, frequency
                    self.sine_amp = random.uniform(12, 48) * (1.0 + current_wave * 0.06)
                    self.sine_freq = random.uniform(1.2, 3.6)

            # shooting logic: aim at player if present
            if now - self.last_shot > int(self.shoot_delay / wave_factor):
                self.last_shot = now
                self.shoot()

            # simple dodge: if a player bullet is close and below (approaching), sidestep
            if self.dodge_cooldown <= 0 and 'player_bullets' in globals():
                for b in player_bullets:
                    if abs(b.rect.centerx - self.rect.centerx) < 36 and b.rect.centery > self.rect.centery and getattr(b, 'speedy', 0) < 0:
                        # dodge left or right depending on available space
                        dir_sign = -1 if (self.rect.centerx > WIDTH // 2) else 1
                        self.start_x += dir_sign * 40
                        self.dodge_cooldown = 30
                        break

        elif self.state == 'dive':
            # advance along path parameter t
            if self.path_duration <= 0:
                self.path_duration = 60
            self.path_t += 1.0 / float(self.path_duration)
            t = min(1.0, self.path_t)
            if self.path_type == 'arc':
                # quadratic Bezier: B(t) = (1-t)^2 P0 + 2(1-t)t C + t^2 P2
                x = (1 - t) * (1 - t) * self.path_start[0] + 2 * (1 - t) * t * self.path_control[0] + t * t * self.path_target[0]
                y = (1 - t) * (1 - t) * self.path_start[1] + 2 * (1 - t) * t * self.path_control[1] + t * t * self.path_target[1]
            else:
                # linear interpolation plus perpendicular sine offset
                sx, sy = self.path_start
                tx, ty = self.path_target
                lx = sx + (tx - sx) * t
                ly = sy + (ty - sy) * t
                # perpendicular vector
                dx = tx - sx
                dy = ty - sy
                dist = max(1.0, math.hypot(dx, dy))
                # normalized perpendicular
                px = -dy / dist
                py = dx / dist
                sine = math.sin(t * math.pi * self.sine_freq)
                x = lx + px * self.sine_amp * sine
                y = ly + py * self.sine_amp * sine
            self.rect.centerx = int(x)
            self.rect.centery = int(y)

            # If the primary target changed (e.g. player1 died and player2 is alive), retarget mid-dive
            try:
                live = get_live_player_obj()
                if live is not None:
                    lcx, lcy = live.rect.center
                    top_limit = max(40, HEIGHT // 4)
                    bottom_limit = max(80, HEIGHT // 2 - 60)
                    new_tx = lcx + random.randrange(-20, 20)
                    new_ty = min(bottom_limit, max(top_limit, lcy + random.randrange(-20, 20)))
                    if math.hypot(self.path_target[0] - new_tx, self.path_target[1] - new_ty) > 24:
                        self.path_target = (new_tx, new_ty)
                        if self.path_type == 'arc':
                            midx = (self.path_start[0] + new_tx) / 2
                            midy = (self.path_start[1] + new_ty) / 2
                            offset = -random.uniform(40, 140)
                            self.path_control = (midx, max(top_limit, midy + offset))
            except Exception:
                pass

            # fire while moving along path occasionally, aim at player but slow bullets
            if now - self.last_shot > int(self.shoot_delay / 1.5):
                self.last_shot = now
                self.shoot()

            # if path completed or off-screen, return to formation
            if t >= 1.0 or self.rect.top > HEIGHT // 2:
                self.state = 'formation'
                self.start_x = self.rect.x
                self.start_y = max(30, self.rect.y - 80)
                self.time_offset = random.uniform(0, 2 * math.pi)

        elif self.state == 'evade':
            # small evade behavior (not used heavily here). revert to formation after brief time
            self.rect.x += int(self.vx)
            self.rect.y += int(self.vy)
            if random.random() < 0.02:
                self.state = 'formation'
                self.time_offset = random.uniform(0, 2 * math.pi)

    def shoot(self):
        # Aim at player if possible, otherwise straight down
        target_obj = get_live_player_obj()
        target = target_obj.rect.center if target_obj is not None else None

        if target:
            dx = target[0] - self.rect.centerx
            dy = target[1] - self.rect.centery
            dist = max(1.0, math.hypot(dx, dy))
            # Slow, forgiving enemy bullets + small angle inaccuracy to avoid perfect homing
            base_speed = 3.0
            angle = math.atan2(dy, dx)
            # add a small random angular offset (±12 degrees)
            angle += random.uniform(-math.radians(12), math.radians(12))
            bx = EnemyBullet(self.rect.centerx, self.rect.bottom)
            bx.speedx = math.cos(angle) * base_speed
            bx.speedy = math.sin(angle) * base_speed
            all_sprites.add(bx)
            enemy_bullets.add(bx)
        else:
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            # ensure default straight-down bullets are slow
            enemy_bullet.speedy = 3
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)

    def explode(self):
        num_particles = random.randrange(5, 10)
        for _ in range(num_particles):
            particle_pos = (self.rect.centerx + random.randrange(-self.rect.width//3, self.rect.width//3),
                            self.rect.centery + random.randrange(-self.rect.height//3, self.rect.height//3))
            particle = MobExplosionParticle(particle_pos)
            all_sprites.add(particle)
            vfx_group.add(particle)
            
class EliteEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(elite_enemy_img, (45, 50)) 
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.start_x, self.start_y = x, y
        self.rect.x, self.rect.y = x, y
        # More aggressive wave params
        # Aggressive but still constrained to upper half and slower overall
        self.amplitude = random.uniform(14, 26)
        self.frequency = random.uniform(0.00005, 0.00012)
        self.time_offset = random.uniform(0, 2 * math.pi)
        self.downward_speed = random.uniform(0.02, 0.07)
        self.state = 'formation'
        self.dive_target = None
        self.vx = 0.0
        self.vy = 0.0
        self.base_dive_speed = random.uniform(6.0, 10.0)
        # trajectory path params for dive
        self.path_type = None
        self.path_t = 0.0
        self.path_duration = 50
        self.path_start = (self.rect.centerx, self.rect.centery)
        self.path_control = (self.rect.centerx, self.rect.centery)
        self.path_target = (self.rect.centerx, self.rect.centery)
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randrange(500, 1400)
        self.dodge_cooldown = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1

        wave_factor = 1.0 + (current_wave * 0.18)

        if self.state == 'formation':
            time_value = now * self.frequency * wave_factor
            sine_offset = self.amplitude * math.sin(time_value + self.time_offset)
            self.rect.x = int(self.start_x + sine_offset)
            self.start_y += self.downward_speed * wave_factor
            self.rect.y = int(self.start_y)

            # higher chance to dive than normal enemies
            if random.random() < 0.0028 * wave_factor:
                self.state = 'dive'
                # choose a target that remains in the upper half
                top_limit = max(40, HEIGHT // 4)
                bottom_limit = max(80, HEIGHT // 2 - 60)
                target_obj = get_live_player_obj()
                if target_obj is not None:
                    tx = target_obj.rect.centerx + random.randrange(-18, 18)
                    ty = min(bottom_limit, max(top_limit, target_obj.rect.centery + random.randrange(-16, 16)))
                else:
                    tx = self.rect.centerx
                    ty = random.randrange(top_limit, bottom_limit)
                self.dive_target = (tx, ty)
                self.path_type = random.choice(['arc', 'sine'])
                self.path_start = (self.rect.centerx, self.rect.centery)
                self.path_target = (tx, ty)
                base_dur = random.randint(120, 180)
                self.path_duration = max(60, int(base_dur / (1.0 + current_wave * 0.14)))
                self.path_t = 0.0
                if self.path_type == 'arc':
                    midx = (self.path_start[0] + tx) / 2
                    midy = (self.path_start[1] + ty) / 2
                    offset = -random.uniform(80, 200)
                    self.path_control = (midx, max(top_limit, midy + offset))
                else:
                    self.sine_amp = random.uniform(28, 84) * (1.0 + current_wave * 0.08)
                    self.sine_freq = random.uniform(1.8, 4.2)

            if now - self.last_shot > int(self.shoot_delay / wave_factor):
                self.last_shot = now
                self.shoot()

            if self.dodge_cooldown <= 0 and 'player_bullets' in globals():
                for b in player_bullets:
                    if abs(b.rect.centerx - self.rect.centerx) < 48 and b.rect.centery > self.rect.centery and getattr(b, 'speedy', 0) < 0:
                        dir_sign = -1 if (self.rect.centerx > WIDTH // 2) else 1
                        self.start_x += dir_sign * 60
                        self.dodge_cooldown = 20
                        break

        elif self.state == 'dive':
            # advance along parametric path
            if self.path_duration <= 0:
                self.path_duration = 50
            self.path_t += 1.0 / float(self.path_duration)
            t = min(1.0, self.path_t)
            if self.path_type == 'arc':
                x = (1 - t) * (1 - t) * self.path_start[0] + 2 * (1 - t) * t * self.path_control[0] + t * t * self.path_target[0]
                y = (1 - t) * (1 - t) * self.path_start[1] + 2 * (1 - t) * t * self.path_control[1] + t * t * self.path_target[1]
            else:
                sx, sy = self.path_start
                tx, ty = self.path_target
                lx = sx + (tx - sx) * t
                ly = sy + (ty - sy) * t
                dx = tx - sx
                dy = ty - sy
                dist = max(1.0, math.hypot(dx, dy))
                px = -dy / dist
                py = dx / dist
                sine = math.sin(t * math.pi * self.sine_freq)
                x = lx + px * self.sine_amp * sine
                y = ly + py * self.sine_amp * sine
            self.rect.centerx = int(x)
            self.rect.centery = int(y)
            # allow retarget to live player mid-dive (e.g. player1 died)
            try:
                live = get_live_player_obj()
                if live is not None:
                    lcx, lcy = live.rect.center
                    top_limit = max(40, HEIGHT // 4)
                    bottom_limit = max(80, HEIGHT // 2 - 60)
                    new_tx = lcx + random.randrange(-16, 16)
                    new_ty = min(bottom_limit, max(top_limit, lcy + random.randrange(-16, 16)))
                    if math.hypot(self.path_target[0] - new_tx, self.path_target[1] - new_ty) > 24:
                        self.path_target = (new_tx, new_ty)
                        if self.path_type == 'arc':
                            midx = (self.path_start[0] + new_tx) / 2
                            midy = (self.path_start[1] + new_ty) / 2
                            offset = -random.uniform(60, 180)
                            self.path_control = (midx, max(top_limit, midy + offset))
            except Exception:
                pass
            if now - self.last_shot > int(self.shoot_delay / 1.2):
                self.last_shot = now
                self.shoot()
            if t >= 1.0 or self.rect.top > HEIGHT + 50:
                self.state = 'formation'
                self.start_x = self.rect.x
                self.start_y = max(30, self.rect.y - 90)
                self.time_offset = random.uniform(0, 2 * math.pi)

    def shoot(self):
        # Aim with slow bullets and mild inaccuracy
        target = None
        if 'player' in globals() and player is not None:
            target = player.rect.center
        elif 'player2' in globals() and player2 is not None:
            target = player2.rect.center

        if target:
            dx = target[0] - self.rect.centerx
            dy = target[1] - self.rect.centery
            angle = math.atan2(dy, dx)
            angle += random.uniform(-math.radians(10), math.radians(10))
            speed = 3.2
            b = EnemyBullet(self.rect.centerx, self.rect.bottom)
            b.speedx = math.cos(angle) * speed
            b.speedy = math.sin(angle) * speed
            all_sprites.add(b)
            enemy_bullets.add(b)
        else:
            elite_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            elite_bullet.speedy = 3
            all_sprites.add(elite_bullet)
            enemy_bullets.add(elite_bullet)

    def explode(self):
        num_particles = random.randrange(8, 15)
        for _ in range(num_particles):
            particle_pos = (self.rect.centerx + random.randrange(-self.rect.width//3, self.rect.width//3),
                            self.rect.centery + random.randrange(-self.rect.height//3, self.rect.height//3))
            particle = EliteMobExplosionParticle(particle_pos)
            all_sprites.add(particle)
            vfx_group.add(particle)
            
class MobExplosionParticle(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = random.randrange(3, 10)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = random.choice([(100, 100, 100), GREEN, (0, 150, 0), YELLOW]) 
        pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedx = random.randrange(-5, 5)
        self.speedy = random.randrange(-5, 5)
        self.gravity = 0.1
        self.lifetime = 1200
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.speedy += self.gravity
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime: self.kill()

class EliteMobExplosionParticle(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = random.randrange(4, 12)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = random.choice([GREEN, BRIGHT_GREEN, (100, 100, 100)]) 
        pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedx = random.randrange(-6, 6)
        self.speedy = random.randrange(-6, 6)
        self.gravity = 0.15
        self.lifetime = 1500
        self.spawn_time = pygame.time.get_ticks()

    def update(self): 
        self.speedy += self.gravity
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime: self.kill()

class BossFireParticle(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = random.randrange(3, 8)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = random.choice([YELLOW, RED, ORANGE])
        pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = random.randrange(-3, 0)
        self.speedx = random.randrange(-2, 3)
        self.lifetime = 60
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime * 10: self.kill()

class ExplosionFragment(pygame.sprite.Sprite):
    def __init__(self, center, size, color, speed_vec):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedx, self.speedy = speed_vec[0], speed_vec[1]
        self.gravity = 0.2
        self.decay = 2000
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.speedy += self.gravity
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if pygame.time.get_ticks() - self.spawn_time > self.decay: self.kill()


# --- New VFX: hit sparks and ship trail (short-lived, lightweight particles) ---
class HitSpark(pygame.sprite.Sprite):
    """Small bright sparks when a bullet hits an enemy (short lifetime)."""
    def __init__(self, center):
        super().__init__()
        self.size = random.randrange(2, 6)
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        col = random.choice([YELLOW, WHITE, ORANGE])
        pygame.draw.circle(self.image, col, (self.size, self.size), self.size)
        self.rect = self.image.get_rect()
        jitter_x = random.randint(-8, 8)
        jitter_y = random.randint(-8, 8)
        self.rect.center = (center[0] + jitter_x, center[1] + jitter_y)
        self.cx = float(self.rect.x)
        self.cy = float(self.rect.y)
        self.vx = random.uniform(-2.2, 2.2)
        self.vy = random.uniform(-2.2, -0.4)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = random.randint(140, 300)

    def update(self):
        dt = 1.0
        self.vy += 0.08
        self.cx += self.vx * dt
        self.cy += self.vy * dt
        self.rect.x = int(self.cx)
        self.rect.y = int(self.cy)
        # Fade out by reducing alpha
        age = pygame.time.get_ticks() - self.spawn_time
        if age > self.lifetime:
            self.kill()
        else:
            alpha = max(0, int(255 * (1.0 - age / float(self.lifetime))))
            try:
                self.image.set_alpha(alpha)
            except Exception:
                pass


class TrailParticle(pygame.sprite.Sprite):
    """Afterimage/trail for the player ship. Fades and shrinks."""
    def __init__(self, center, color=BLUE, size=18):
        super().__init__()
        # elongated streak: narrow width, longer height
        s = max(6, size)
        w = max(3, int(s * 0.4))
        h = max(10, int(s * 1.8))
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # vertical gradient from bright (top) to transparent (bottom)
        try:
            for i in range(h):
                t = i / float(h)
                # emphasis towards the top
                a = int(200 * (1.0 - t) * (1.0 - t))
                col = (color[0], color[1], color[2], a)
                self.image.fill(col, (0, i, w, 1))
        except Exception:
            try:
                self.image.fill((color[0], color[1], color[2], 120))
            except Exception:
                pass
        self.rect = self.image.get_rect()
        # align the tail so it trails behind the ship (placed slightly above center)
        self.rect.center = (center[0], center[1] + int(h * 0.2))
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 400
        self.cx = float(self.rect.x)
        self.cy = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0

    def update(self):
        age = pygame.time.get_ticks() - self.spawn_time
        if age > self.lifetime:
            self.kill()
            return
        t = age / float(self.lifetime)
        # overall fade multiplier
        fade = max(0, int(220 * (1.0 - t)))
        try:
            # multiply overall alpha while preserving per-pixel alpha (set_alpha multiplies)
            self.image.set_alpha(fade)
        except Exception:
            pass
        # drift downward slowly so the trail lingers behind
        self.cy += 0.25 + 0.4 * t
        self.rect.x = int(self.cx)
        self.rect.y = int(self.cy)


# --- Parallax starfield helpers ---
def init_starfield(layers=None):
    """Return a list of star layers. Each layer is a list of star dicts."""
    if layers is None:
        layers = [
            {'count': 120, 'speed': 0.3, 'size': (1, 2), 'color': (120, 120, 120)},
            {'count': 70, 'speed': 0.9, 'size': (1, 2), 'color': (200, 200, 200)},
            {'count': 32, 'speed': 1.6, 'size': (2, 3), 'color': (255, 255, 255)},
        ]
    star_layers = []
    for layer in layers:
        stars = []
        for _ in range(layer['count']):
            x = random.uniform(0, WIDTH)
            y = random.uniform(0, HEIGHT)
            size = random.randint(layer['size'][0], layer['size'][1])
            speed = layer['speed'] * (0.9 + random.random() * 0.3)
            col = layer.get('color', (255, 255, 255))
            stars.append({'x': x, 'y': y, 'size': size, 'speed': speed, 'color': col})
        star_layers.append(stars)
    return star_layers


def update_and_draw_starfield(surf, star_layers, offset_x=0, offset_y=0):
    """Update positions and draw star layers onto `surf`. offset_x/y are screen shake offsets."""
    for i, layer in enumerate(star_layers):
        # draw each star
        for s in layer:
            s['y'] += s['speed']
            if s['y'] > HEIGHT:
                s['y'] -= HEIGHT
                s['x'] = random.uniform(0, WIDTH)
            # parallax: further layers move slightly with offset
            draw_x = int(s['x'] + offset_x * (0.06 * (i + 1)))
            draw_y = int(s['y'] + offset_y * (0.06 * (i + 1)))
            try:
                surf.fill(s['color'], (draw_x, draw_y, s['size'], s['size']))
            except Exception:
                try:
                    pygame.draw.rect(surf, s['color'], (draw_x, draw_y, s['size'], s['size']))
                except Exception:
                    pass


class BossEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.transform.scale(boss_img, (120, 100))
        self.original_image.set_colorkey(BLACK)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.top = -100
        self.hp = 1000
        self.max_hp = 1000
        self.speedx = 3
        self.target_y = 50
        self.active = False
        self.dying_threshold = self.max_hp * 0.25
        self.is_dying = False
        self.last_fire_spawn = pygame.time.get_ticks()
        self.fire_spawn_rate = 100
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 500
        self.shot_pattern = 0 
        self.pattern_change_time = pygame.time.get_ticks()
        self.pattern_change_delay = 5000 

    def update(self):
        if self.rect.y < self.target_y: self.rect.y += 2
        else: self.active = True
        if self.active:
            self.rect.x += self.speedx
            if self.rect.right > WIDTH or self.rect.left < 0: self.speedx *= -1
            now = pygame.time.get_ticks()
            if now - self.pattern_change_time > self.pattern_change_delay:
                self.pattern_change_time = now
                self.shot_pattern = random.randrange(0, 3) 
                if self.shot_pattern == 0: self.shoot_delay = 500
                if self.shot_pattern == 1: self.shoot_delay = 150
                if self.shot_pattern == 2: self.shoot_delay = 700
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.perform_shot() 
            if self.hp < self.dying_threshold and not self.is_dying: self.is_dying = True
            if self.is_dying: self.dying_effect()

    def perform_shot(self):
        if self.shot_pattern == 0: self.shoot_triple()
        elif self.shot_pattern == 1: self.shoot_wave()
        elif self.shot_pattern == 2: self.shoot_spread()
            
    def shoot_triple(self):
        wave4 = ('current_wave' in globals() and current_wave >= 4)
        for i in range(-1, 2):
            enemy_bullet = EnemyBullet(self.rect.centerx + i * 20, self.rect.bottom)
            if wave4:
                # slower, gently curving bullets so players can dodge more easily
                enemy_bullet.speedx = i * 1.0
                enemy_bullet.speedy = 4.0
                enemy_bullet.curve = i * 0.015
                enemy_bullet.wiggle = 0.0
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            
    def shoot_spread(self):
        num_bullets = 5
        base_speed = 5
        angle_spread = 60 
        for i in range(num_bullets):
            angle = math.radians(90 - angle_spread / 2 + (angle_spread / (num_bullets - 1)) * i)
            speedx = base_speed * math.cos(angle)
            speedy = base_speed * math.sin(angle)
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            # for wave 4, make bullets slightly slower and add mild wiggle
            if 'current_wave' in globals() and current_wave >= 4:
                # make spread bullets slower and slightly wavy but still dodgeable
                enemy_bullet.speedx = speedx * 0.55
                enemy_bullet.speedy = speedy * 0.6
                enemy_bullet.wiggle = 0.9
                enemy_bullet.curve = 0.008 * (1 if speedx >= 0 else -1)
            else:
                enemy_bullet.speedx = speedx
                enemy_bullet.speedy = speedy
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)

    def shoot_wave(self):
        enemy_bullet_left = EnemyBullet(self.rect.centerx - 10, self.rect.bottom)
        enemy_bullet_right = EnemyBullet(self.rect.centerx + 10, self.rect.bottom)
        if 'current_wave' in globals() and current_wave >= 4:
            enemy_bullet_left.speedy = 3.2
            enemy_bullet_right.speedy = 3.2
            enemy_bullet_left.wiggle = 0.6
            enemy_bullet_right.wiggle = 0.6
            enemy_bullet_left.curve = -0.01
            enemy_bullet_right.curve = 0.01
        else:
            enemy_bullet_left.speedy = 6
            enemy_bullet_right.speedy = 6
        all_sprites.add(enemy_bullet_left, enemy_bullet_right)
        enemy_bullets.add(enemy_bullet_left, enemy_bullet_right)
            
    def dying_effect(self):
        now = pygame.time.get_ticks()
        if now - self.last_fire_spawn > self.fire_spawn_rate:
            self.last_fire_spawn = now
            for _ in range(random.randrange(1, 4)):
                pos_x = random.randrange(self.rect.left, self.rect.right)
                pos_y = random.randrange(self.rect.bottom - 20, self.rect.bottom)
                fire = BossFireParticle((pos_x, pos_y))
                all_sprites.add(fire)
                vfx_group.add(fire) 
        if now % 200 < 100: self.image = self.original_image.copy()
        else:
            burnt_image = self.original_image.copy()
            burnt_image.fill((100, 0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
            self.image = burnt_image

    def shatter(self):
        global screen_shake_duration, screen_shake_intensity
        num_fragments = 30
        for _ in range(num_fragments):
            size = random.randrange(5, 15)
            center_x = random.randrange(self.rect.left, self.rect.right)
            center_y = random.randrange(self.rect.top, self.rect.bottom)
            angle = random.uniform(0, 2 * math.pi)
            speed_mag = random.uniform(3, 8)
            speed_vec = (speed_mag * math.cos(angle), speed_mag * math.sin(angle) - 3)
            color = random.choice([YELLOW, RED, BLUE, (50, 50, 50)])
            fragment = ExplosionFragment((center_x, center_y), size, color, speed_vec)
            all_sprites.add(fragment)
            vfx_group.add(fragment)
        screen_shake_duration = 20
        screen_shake_intensity = 8
        expl_sound.play()

# --- 🔴 CLASS BOSS ENEMY 2 (ĐÃ NÂNG CẤP ĐỘ KHÓ) 🔴 ---
# --- (!!!) PHIÊN BẢN DỄ HƠN VỚI ÍT ĐẠN (!!!) ---
class BossEnemy2(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.transform.scale(boss_2_img, (150, 130))
        self.original_image.set_colorkey(BLACK)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.top = -130 
        
        # --- THAY ĐỔI: 5000 MÁU ---
        self.hp = 5000
        self.max_hp = 5000
        
        self.speedx = 4 
        self.target_y = 50
        self.active = False
        self.dying_threshold = self.max_hp * 0.25
        self.is_dying = False
        self.last_fire_spawn = pygame.time.get_ticks()
        self.fire_spawn_rate = 80 
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 400 
        self.shot_pattern = 0 
        self.pattern_change_time = pygame.time.get_ticks()
        # --- THAY ĐỔI: Đổi kiểu tấn công nhanh hơn ---
        self.pattern_change_delay = 2500 # 2.5 giây

    def update(self):
        if self.rect.y < self.target_y: self.rect.y += 2
        else: self.active = True
        if self.active:
            self.rect.x += self.speedx
            if self.rect.right > WIDTH or self.rect.left < 0: self.speedx *= -1
            now = pygame.time.get_ticks()
            if now - self.pattern_change_time > self.pattern_change_delay:
                self.pattern_change_time = now
                self.shot_pattern = random.randrange(0, 3) 
                
                # --- THAY ĐỔI: Điều chỉnh delay cho các kiểu bắn mới ---
                if self.shot_pattern == 0: self.shoot_delay = 500 # Heavy Burst (nửa giây)
                if self.shot_pattern == 1: self.shoot_delay = 100 # Bullet Wall (rất nhanh)
                if self.shot_pattern == 2: self.shoot_delay = 800 # Tracking Spread (cần thời gian ngắm)
                        
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.perform_shot() 
            if self.hp < self.dying_threshold and not self.is_dying: self.is_dying = True
            if self.is_dying: self.dying_effect()

    def perform_shot(self):
        # --- THAY ĐỔI: Cần truy cập 'player' để ngắm bắn ---
        global player # Lấy player toàn cục
        
        if self.shot_pattern == 0: self.shoot_triple()
        elif self.shot_pattern == 1: self.shoot_wave()
        elif self.shot_pattern == 2:
            if player and player.alive(): # Chỉ bắn nếu player còn sống
                self.shoot_spread(player) 
            
    def shoot_triple(self):
        # --- NÂNG CẤP: "Heavy Burst" 5 đạn ---
        # --- (!!!) GIẢM ĐẠN: Giảm từ 5 viên (-2, 3) xuống 3 viên (-1, 2) ---
        for i in range(-1, 2): # Bắn 3 viên (-1, 0, 1)
            enemy_bullet = EnemyBullet(self.rect.centerx + i * 25, self.rect.bottom) # Rộng hơn (25px)
            enemy_bullet.speedy = 8 # Nhanh hơn
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            
    def shoot_spread(self, player_target):
        # --- NÂNG CẤP: "Tracking Spread" (Bắn 7 viên nhắm vào player) ---
        
        # 1. Tính góc tới player
        dx = player_target.rect.centerx - self.rect.centerx
        dy = player_target.rect.centery - self.rect.bottom 
        if dy == 0: dy = 1 
        
        player_angle_rad = math.atan2(dy, dx)
        player_angle_deg = math.degrees(player_angle_rad)

        # --- (!!!) GIẢM ĐẠN: Giảm từ 7 viên xuống 5 viên ---
        num_bullets = 5 
        base_speed = 6.5 # Tốc độ đạn nhanh hơn
        angle_spread = 60 # Góc bắn 60 độ

        for i in range(num_bullets):
            current_angle_deg = player_angle_deg - (angle_spread / 2) + (angle_spread / (num_bullets - 1)) * i
            angle_rad = math.radians(current_angle_deg)
            
            speedx = base_speed * math.cos(angle_rad)
            speedy = base_speed * math.sin(angle_rad)
            
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            enemy_bullet.speedx = speedx
            enemy_bullet.speedy = speedy
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)

    def shoot_wave(self):
        # --- NÂNG CẤP: "Bullet Wall" 8 đạn ---
        # --- (!!!) GIẢM ĐẠN: Giảm từ 8 viên xuống 6 viên ---
        num_bullets = 6
        spacing = 15 # Khoảng cách giữa các viên đạn
        
        for i in range(num_bullets):
            start_x = self.rect.centerx - (spacing * (num_bullets - 1) / 2) + (i * spacing)
            
            enemy_bullet = EnemyBullet(start_x, self.rect.bottom)
            enemy_bullet.speedy = 7 # Tốc độ cao
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            
    def dying_effect(self):
        now = pygame.time.get_ticks()
        if now - self.last_fire_spawn > self.fire_spawn_rate:
            self.last_fire_spawn = now
            for _ in range(random.randrange(2, 5)): 
                pos_x = random.randrange(self.rect.left, self.rect.right)
                pos_y = random.randrange(self.rect.bottom - 20, self.rect.bottom)
                fire = BossFireParticle((pos_x, pos_y))
                all_sprites.add(fire)
                vfx_group.add(fire) 
        if now % 200 < 100: self.image = self.original_image.copy()
        else:
            burnt_image = self.original_image.copy()
            burnt_image.fill((100, 0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
            self.image = burnt_image

    def shatter(self):
        global screen_shake_duration, screen_shake_intensity
        num_fragments = 45 
        for _ in range(num_fragments):
            size = random.randrange(5, 20)
            center_x = random.randrange(self.rect.left, self.rect.right)
            center_y = random.randrange(self.rect.top, self.rect.bottom)
            angle = random.uniform(0, 2 * math.pi)
            speed_mag = random.uniform(4, 10)
            speed_vec = (speed_mag * math.cos(angle), speed_mag * math.sin(angle) - 3)
            color = random.choice([YELLOW, RED, PURPLE, (100, 50, 100)])
            fragment = ExplosionFragment((center_x, center_y), size, color, speed_vec)
            all_sprites.add(fragment)
            vfx_group.add(fragment)
        screen_shake_duration = 25 
        screen_shake_intensity = 10 
        expl_sound.play()
            
class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_upgraded=False):
        super().__init__()
        if is_upgraded:
            upgraded_bullet_img = pygame.transform.scale(bullet_img, (10, 22)) 
            upgraded_bullet_img.fill(BRIGHT_GREEN, special_flags=pygame.BLEND_RGB_MULT) 
            self.image = upgraded_bullet_img
            self.speedy = -12
        else:
            self.image = pygame.transform.scale(bullet_img, (8, 18))
            self.speedy = -10
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0: self.kill()


class HealthPickup(pygame.sprite.Sprite):
    """Health pickup that falls down and restores HP when collected.
    Image uses drumstick_img."""
    def __init__(self, x, y):
        super().__init__()
        # create a green plus icon as base image
        try:
            # create 20x20 plus icon
            base = pygame.Surface((20, 20), pygame.SRCALPHA)
            base.fill((0, 0, 0, 0))
            try:
                pygame.draw.rect(base, (30, 180, 80), (9, 3, 2, 14))
                pygame.draw.rect(base, (30, 180, 80), (3, 9, 14, 2))
            except Exception:
                base.fill((30, 180, 80))
            self.base_image = base
        except Exception:
            self.base_image = pygame.Surface((16, 16), pygame.SRCALPHA)
            self.base_image.fill((30, 180, 80))

        self.image = self.base_image.copy()
        self.cx = float(x)
        self.cy = float(y)
        self.rect = self.image.get_rect(center=(self.cx, self.cy))
        # slower fall
        self.speedy = 1.5

    def update(self):
        # pulse ring/highlight around pickup
        now = pygame.time.get_ticks()
        pulse = (math.sin(now / 300.0) + 1) / 2  # 0..1
        glow_alpha = 90 + int(60 * pulse)
        # create surface slightly larger to hold glow
        w = max(40, self.base_image.get_width() + 16)
        h = max(40, self.base_image.get_height() + 16)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # draw glow circle
        try:
            pygame.draw.circle(surf, (50, 220, 120, glow_alpha), (w//2, h//2), max(w,h)//2 - 6)
            pygame.draw.circle(surf, (50, 220, 120, int(glow_alpha*0.6)), (w//2, h//2), max(w,h)//2 - 10, 6)
        except Exception:
            pass
        # blit base image centered
        bx = (w - self.base_image.get_width()) // 2
        by = (h - self.base_image.get_height()) // 2
        surf.blit(self.base_image, (bx, by))
        self.image = surf

        # move using float coords for smooth motion
        self.cy += self.speedy
        self.rect = self.image.get_rect(center=(self.cx, self.cy))
        if self.rect.top > HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a sharp, dangerous-looking bullet (diamond/pointed) with a thin streak
        try:
            bw, bh = 14, 28
            surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            # Draw a smooth core + soft tail (classic Chicken Invaders style)
            try:
                # tail: vertical gradient from core color downwards (fade out)
                core_rgb = (240, 120, 40)
                max_tail_alpha = 140
                tail_start = 8
                for yy in range(tail_start, bh):
                    t = (yy - tail_start) / float(max(1, bh - tail_start))
                    a = int(max_tail_alpha * (1.0 - t) * (1.0 - t))
                    col = (core_rgb[0], core_rgb[1], core_rgb[2], a)
                    surf.fill(col, (bw//2 - 2, yy, 4, 1))

                # soft glow around core (a faint ellipse)
                glow_col = (255, 160, 80, 80)
                try:
                    pygame.draw.ellipse(surf, glow_col, (1, 1, bw-2, 12))
                except Exception:
                    pass

                # core: small bright circle near the top
                core_y = 6
                core_radius = 4
                try:
                    pygame.draw.circle(surf, (255, 220, 120), (bw//2, core_y), core_radius)
                    pygame.draw.circle(surf, (255, 255, 255), (bw//2, core_y - 1), 2)
                except Exception:
                    pass
            except Exception:
                pass
            self.image = surf
        except Exception:
            # fallback to asset
            self.image = pygame.transform.scale(enemy_bullet_img, (8, 18))
            try:
                self.image.set_colorkey(BLACK)
            except Exception:
                pass
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.centerx = x
        # float positions for smooth motion and lateral wiggle
        self.cx = float(self.rect.centerx)
        self.cy = float(self.rect.top)
        # default speeds (can be overridden after creation)
        self.speedy = 5
        self.speedx = 0.0
        # optional curvature (per-frame added to speedx) and lateral wiggle amplitude
        self.curve = 0.0
        self.wiggle = 0.0
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        # apply curve as a small per-frame acceleration to speedx
        if getattr(self, 'curve', 0):
            self.speedx += self.curve
        # advance float positions
        self.cx += self.speedx
        self.cy += self.speedy
        # lateral wiggle (sinusoidal offset) applied on top of cx
        offset = 0
        if getattr(self, 'wiggle', 0):
            # frequency scaled so wiggle is noticeable but not too fast
            offset = self.wiggle * math.sin((now - self.spawn_time) / 250.0)
        self.rect.centerx = int(self.cx + offset)
        self.rect.y = int(self.cy)
        # kill if off-screen (with some margin)
        if self.rect.top > HEIGHT + 100 or self.rect.bottom < -100 or self.rect.right < -100 or self.rect.left > WIDTH + 100:
            self.kill()


# --- 3. ENEMY FORMATION FUNCTION ---
TOTAL_WAVES_BEFORE_BOSS = 4
ELITE_WAVES_BEFORE_BOSS_2 = 3 

def create_enemy_formation():
    global boss, current_wave, boss_coming, boss_warning_start 
    global elite_wave_count, boss_2, boss_2_coming, boss_2_warning_start
    
    if (boss and boss.alive()) or (boss_2 and boss_2.alive()): 
        return

    # --- 1. LOGIC GỌI BOSS 1 ---
    if not player_is_upgraded and current_wave + 1 >= TOTAL_WAVES_BEFORE_BOSS and not boss:
        if current_wave == TOTAL_WAVES_BEFORE_BOSS - 1:
            current_wave += 1
            boss_coming = True
            boss_warning_start = pygame.time.get_ticks()
            boss_alert_sound.play() 
            return
            
    # --- 2. LOGIC GỌI BOSS 2 ---
    if player_is_upgraded:
        if elite_wave_count + 1 >= ELITE_WAVES_BEFORE_BOSS_2 and not boss_2:
            if elite_wave_count == ELITE_WAVES_BEFORE_BOSS_2 - 1:
                elite_wave_count += 1 
                boss_2_coming = True
                boss_warning_start = pygame.time.get_ticks() 
                boss_alert_sound.play() 
                return
                
    # --- 3. LOGIC TẠO QUÁI THƯỜNG / ELITE ---
    if not boss_coming and not boss_2_coming:
        if player_is_upgraded:
            elite_wave_count += 1
        else:
            current_wave += 1

    is_elite_wave = player_is_upgraded
    
    num_enemies = 5
    enemy_size = 40
    spacing = 80
    formation_width = num_enemies * enemy_size + (num_enemies - 1) * spacing
    start_x = (WIDTH - formation_width) // 2

    # Special orchestrated group attack on wave 3 (staged, same path)
    group_attack_wave = (not player_is_upgraded) and (current_wave == 3)

    group_enemies = []
    for i in range(num_enemies):
        if is_elite_wave:
            e1 = EliteEnemy(start_x + i * (enemy_size + spacing), 50)
            e2 = EliteEnemy(start_x + i * (enemy_size + spacing) + 40, 120)
        else:
            e1 = Enemy(start_x + i * (enemy_size + spacing), 50)
            e2 = Enemy(start_x + i * (enemy_size + spacing) + 40, 120)
        all_sprites.add(e1)
        mobs.add(e1)
        all_sprites.add(e2)
        mobs.add(e2)
        # collect the top-row enemies for possible group attack sequencing
        group_enemies.append(e1)

    # If this is the special grouped wave, configure a shared path and staggered start times
    if group_attack_wave and group_enemies:
        path_type = random.choice(['arc', 'sine'])
        # choose a shared target in the upper half (do NOT go into player's area)
        top_limit = max(40, HEIGHT // 8)
        bottom_limit = max(80, HEIGHT // 2 - 80)
        target_x_base = WIDTH // 2 + random.randint(-60, 60)
        target_y = random.randint(top_limit + 10, bottom_limit)
        # shared control point for arc (arched flight)
        midx = (group_enemies[0].rect.centerx + target_x_base) / 2
        midy = (group_enemies[0].rect.centery + target_y) / 2
        control_offset = -random.uniform(60, 160)
        control_point = (midx, max(top_limit, midy + control_offset))
        # duration long to keep motion slow and graceful; small stagger between enemies
        base_duration = 160
        for idx, en in enumerate(group_enemies):
            en.state = 'dive'
            en.path_type = path_type
            en.path_start = (en.rect.centerx, en.rect.centery)
            en.path_target = (target_x_base + idx * 6, target_y)
            en.path_duration = max(80, int(base_duration / (1.0 + current_wave * 0.06)))
            # stagger starts so they follow in sequence
            en.path_t = - (idx * 0.12)
            if path_type == 'arc':
                # use shared control point shifted slightly per enemy for variety
                en.path_control = (control_point[0] + idx * 6, control_point[1] - idx * 4)
            else:
                en.sine_amp = random.uniform(18, 48)
                en.sine_freq = random.uniform(1.0, 3.0)

# --- 4. GAME LOOP ---

def draw_button(surf, text, x, y, width, height, inactive_color, active_color, text_color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    is_hovering = (x < mouse_pos[0] < x + width) and (y < mouse_pos[1] < y + height)
    # Draw subtle shadow
    shadow_color = (0, 0, 0, 60)
    try:
        # simple dark shadow rectangle
        pygame.draw.rect(surf, (0, 0, 0), (x + 3, y + 3, width, height), border_radius=8)
    except Exception:
        pygame.draw.rect(surf, (0, 0, 0), (x + 3, y + 3, width, height))

    # Button background with rounded corners when possible
    color = active_color if is_hovering else inactive_color
    try:
        pygame.draw.rect(surf, color, (x, y, width, height), border_radius=8)
        # border
        pygame.draw.rect(surf, WHITE, (x, y, width, height), 2, border_radius=8)
    except Exception:
        pygame.draw.rect(surf, color, (x, y, width, height))
        pygame.draw.rect(surf, WHITE, (x, y, width, height), 2)

    draw_text(surf, text, 22, x + (width / 2), y + (height / 2) - 11, text_color)
    return is_hovering


# --- Game State variables ---
music_enabled = True
enable_coop = False  # Toggle for local co-op (default OFF)
current_language = "vi" 

# --- Main Menu Screen ---
def main_menu_screen():
    global enable_coop
    if music_loaded and music_enabled:
        pygame.mixer.music.play(loops=-1)
    button_width, button_height = 220, 50
    button_x = (WIDTH - button_width) // 2
    # Move Co-op toggle to bottom-right corner
    coop_rect = pygame.Rect(WIDTH - button_width - 20, HEIGHT - button_height - 20, button_width, button_height)
    start_rect = pygame.Rect(button_x, HEIGHT // 2 - 30, button_width, button_height)
    settings_rect = pygame.Rect(button_x, HEIGHT // 2 + 40, button_width, button_height)
    quit_rect = pygame.Rect(button_x, HEIGHT // 2 + 110, button_width, button_height)
    while True:
        title_text = "SPACE SHOOTER"
        start_text = "Bắt đầu" if current_language == "vi" else "Start"
        settings_text = "Cài đặt" if current_language == "vi" else "Settings"
        quit_text = "Thoát" if current_language == "vi" else "Quit"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Toggle co-op from main menu
                if coop_rect.collidepoint(mouse_pos):
                    enable_coop = not enable_coop
                    # reflect immediately and continue showing menu
                    continue
                if start_rect.collidepoint(mouse_pos):
                    return "in_game"
                if settings_rect.collidepoint(mouse_pos):
                    return "settings"
                if quit_rect.collidepoint(mouse_pos):
                    return "quit"
        screen.blit(background_img, (0, 0))
        draw_text(screen, title_text, 64, WIDTH // 2, HEIGHT // 4 - 20)
        # Localised label: "Chế độ 2 người" (VI) / fallback (EN)
        if current_language == "vi":
            coop_label = "Chế độ 2 người"
        else:
            coop_label = "2-Player Mode"
        # Use green border when coop enabled, red when single-player
        coop_inactive = GREEN if enable_coop else RED
        draw_button(screen, coop_label, coop_rect.x, coop_rect.y, coop_rect.w, coop_rect.h, coop_inactive, COLOR_ACTIVE)
        draw_button(screen, start_text, start_rect.x, start_rect.y, start_rect.w, start_rect.h, COLOR_INACTIVE, COLOR_ACTIVE)
        draw_button(screen, settings_text, settings_rect.x, settings_rect.y, settings_rect.w, settings_rect.h, COLOR_INACTIVE, COLOR_ACTIVE)
        draw_button(screen, quit_text, quit_rect.x, quit_rect.y, quit_rect.w, quit_rect.h, COLOR_INACTIVE, COLOR_ACTIVE)
        # Small credit / group label at bottom-left
        try:
            draw_text_shadow(screen, "Nhóm TTNPB", 16, 12, HEIGHT - 28, color=WHITE, center=False)
        except Exception:
            draw_text(screen, "Nhóm TTNPB", 16, 12, HEIGHT - 28, WHITE)
        pygame.display.flip()
        clock.tick(FPS)

# --- Settings Screen ---
def settings_screen():
    global music_enabled, current_language
    sound_rect = pygame.Rect((WIDTH // 2) - 110, HEIGHT // 2 - 80, 220, 50)
    vi_rect = pygame.Rect((WIDTH // 2) - 120, HEIGHT // 2 + 50, 100, 50)
    en_rect = pygame.Rect((WIDTH // 2) + 20, HEIGHT // 2 + 50, 100, 50)
    back_rect = pygame.Rect((WIDTH // 2) - 110, HEIGHT - 100, 220, 50)
    while True:
        title_text = "Cài đặt" if current_language == "vi" else "Settings"
        sound_text = "Âm thanh" if current_language == "vi" else "Sound"
        lang_text = "Ngôn ngữ" if current_language == "vi" else "Language"
        back_text = "Quay lại" if current_language == "vi" else "Back"
        sound_on = "Bật" if current_language == "vi" else "On"
        sound_off = "Tắt" if current_language == "vi" else "Off"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if sound_rect.collidepoint(mouse_pos):
                    music_enabled = not music_enabled
                    if music_enabled:
                        if music_loaded: pygame.mixer.music.play(loops=-1)
                    else:
                        pygame.mixer.music.stop()
                if vi_rect.collidepoint(mouse_pos):
                    current_language = "vi"
                if en_rect.collidepoint(mouse_pos):
                    current_language = "en"
                if back_rect.collidepoint(mouse_pos):
                    return "main_menu"
        screen.blit(background_img, (0, 0))
        draw_text(screen, title_text, 64, WIDTH // 2, HEIGHT // 5)
        sound_status_text = f"{sound_text}: {sound_on if music_enabled else sound_off}"
        draw_button(screen, sound_status_text, sound_rect.x, sound_rect.y, sound_rect.w, sound_rect.h, COLOR_INACTIVE, COLOR_ACTIVE)
        draw_text(screen, lang_text, 30, WIDTH // 2, HEIGHT // 2)
        vi_color = COLOR_SELECTED if current_language == "vi" else COLOR_INACTIVE
        en_color = COLOR_SELECTED if current_language == "en" else COLOR_INACTIVE
        draw_button(screen, "Tiếng Việt", vi_rect.x, vi_rect.y, vi_rect.w, vi_rect.h, vi_color, COLOR_ACTIVE)
        draw_button(screen, "English", en_rect.x, en_rect.y, en_rect.w, en_rect.h, en_color, COLOR_ACTIVE)
        draw_button(screen, back_text, back_rect.x, back_rect.y, back_rect.w, back_rect.h, COLOR_INACTIVE, COLOR_ACTIVE)
        pygame.display.flip()
        clock.tick(FPS)

# --- (!!!) HÀM ĐÃ THAY ĐỔI (!!!) ---
# --- Toàn bộ vòng lặp game chính được đặt trong hàm này ---
def check_game_over():
    """Set game_over True only when both players are down.
    If player2 does not exist, fall back to single-player behavior."""
    global game_over, player, player2, music_loaded

    p1_down = getattr(player, 'hp', 0) <= 0
    p2_exists = 'player2' in globals() and player2 is not None
    p2_down = False
    if p2_exists:
        p2_down = getattr(player2, 'hp', 0) <= 0

    if p2_exists:
        if p1_down and p2_down:
            game_over = True
            if music_loaded: pygame.mixer.music.stop()
    else:
        if p1_down:
            game_over = True
            if music_loaded: pygame.mixer.music.stop()

def run_game():
    """Chạy vòng lặp game chính."""
    
    global all_sprites, mobs, player_bullets, enemy_bullets, vfx_group, pickups_group
    global player, player2, score, game_over, current_wave, boss, boss_defeated, player_is_upgraded
    global screen_shake_duration, screen_shake_intensity, boss_coming, boss_warning_start
    global elite_wave_count, boss_2, boss_2_coming, boss_2_defeated
    global final_boss_defeated
    
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    vfx_group = pygame.sprite.Group()
    pickups_group = pygame.sprite.Group()
    global star_layers
    star_layers = init_starfield()
    score = 0
    game_over = False
    current_wave = 0
    boss = None
    boss_defeated = False
    player_is_upgraded = False 
    screen_shake_duration = 0
    screen_shake_intensity = 0
    boss_coming = False
    boss_warning_start = 0
    BOSS_WARNING_DURATION = 1500
    
    elite_wave_count = 0
    boss_2 = None
    boss_2_coming = False
    boss_2_defeated = False
    final_boss_defeated = False

    player = Player()
    all_sprites.add(player)
    # Create Player2 for local co-op (only if enabled)
    if enable_coop:
        try:
            player2 = Player2()
            all_sprites.add(player2)
        except Exception:
            player2 = None
    else:
        player2 = None
    create_enemy_formation()

    if music_loaded and music_enabled:
        pygame.mixer.music.play(loops=-1)

    game_is_running = True
    while game_is_running:
        
        if game_over:
            play_again = game_over_screen()
            if play_again:
                reset_game()
                continue
            else:
                game_is_running = False 
                break

        clock.tick(FPS)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game_is_running = False 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Only allow Player 1 to shoot if still alive
                    try:
                        if 'player' in globals() and player is not None and getattr(player, 'hp', 0) > 0 and getattr(player, 'alive', lambda: True)():
                            try:
                                player.shoot()
                            except Exception:
                                pass
                    except Exception:
                        pass
                if event.key == pygame.K_LSHIFT:
                    # Left SHIFT triggers Player2 shoot (if exists)
                    if 'player2' in globals() and player2 is not None:
                        try:
                            player2.shoot()
                        except Exception:
                            pass
                    
        all_sprites.update()
        
        hits_player_bullet_mob = pygame.sprite.groupcollide(mobs, player_bullets, False, True)
        for mob, bullets_hit in hits_player_bullet_mob.items():
            if isinstance(mob, Enemy) or isinstance(mob, EliteEnemy): 
                score += 10
                expl_sound.play()
                mob.explode()
                # Small hit sparks for feedback
                try:
                    for _ in range(min(6, max(2, len(bullets_hit) * 3))):
                        spark = HitSpark(mob.rect.center)
                        all_sprites.add(spark)
                        vfx_group.add(spark)
                except Exception:
                    pass
                # Chance to drop health pickup (15%)
                try:
                    if random.random() < 0.15:
                        pickup = HealthPickup(mob.rect.centerx, mob.rect.centery)
                        all_sprites.add(pickup)
                        pickups_group.add(pickup)
                except Exception:
                    pass
                mob.kill()
            elif isinstance(mob, BossEnemy): # BOSS 1
                damage_per_bullet = 10
                mob.hp -= damage_per_bullet * len(bullets_hit)
                
                if mob.hp <= 0:
                    mob.shatter() 
                    mob.kill()
                    
                    player_is_upgraded = True 
                    player.upgraded = True
                    player.set_image_and_stats() 

                    # --- 🔴 THAY ĐỔI: NÂNG CẤP MÁU PLAYER LÊN 300 🔴 ---
                    player.max_hp = 300
                    player.hp = player.max_hp # Hồi đầy 300 máu
                    # Upgrade Player 2 too (if present)
                    if 'player2' in globals() and player2 is not None:
                        try:
                            player2.upgraded = True
                            player2.set_image_and_stats()
                        except Exception:
                            pass
                        player2.max_hp = 300
                        player2.hp = player2.max_hp
                    
                    score += 500
                    boss = None    
                    boss_defeated = True 
                    create_enemy_formation() 
            
            # --- (!!!) LOGIC BOSS 2 CHẾT ĐÃ THAY ĐỔI (!!!) ---
            elif isinstance(mob, BossEnemy2): # BOSS 2
                damage_per_bullet = 15 
                mob.hp -= damage_per_bullet * len(bullets_hit)
                # visual feedback for hitting boss: small sparks
                try:
                    for _ in range(min(18, 3 * len(bullets_hit))):
                        s = HitSpark((mob.rect.centerx + random.randint(-40,40), mob.rect.centery + random.randint(-20,20)))
                        all_sprites.add(s)
                        vfx_group.add(s)
                except Exception:
                    pass
                if mob.hp <= 0:
                    # --- LOGIC KẾT THÚC ĐẶC BIỆT ---
                    mob.shatter() # 1. Vẫn cho nổ tung
                    mob.kill()
                    score += 2000 # Vẫn cộng điểm
                    boss_2 = None 
                    
                    # 2. Đặt cờ đặc biệt
                    final_boss_defeated = True 
                    
                    # 3. Giết cả hai người chơi (để đảm bảo màn kết thúc đặc biệt)
                    try:
                        player.hp = 0
                    except Exception:
                        pass
                    if 'player2' in globals() and player2 is not None:
                        try:
                            player2.hp = 0
                        except Exception:
                            pass

                    # 4. Check end condition (this will set game_over True since both hp = 0)
                    check_game_over()

                    # 5. Tắt nhạc
                    if music_loaded: pygame.mixer.music.stop()
                    # --- KẾT THÚC LOGIC MỚI ---
        
        if not mobs: 
            if boss_coming:
                now = pygame.time.get_ticks()
                if now - boss_warning_start > BOSS_WARNING_DURATION:
                    boss_coming = False
                    boss = BossEnemy()
                    all_sprites.add(boss)
                    mobs.add(boss)
                    boss_defeated = False 
            
            elif boss_2_coming:
                now = pygame.time.get_ticks()
                if now - boss_warning_start > BOSS_WARNING_DURATION:
                    boss_2_coming = False
                    boss_2 = BossEnemy2() 
                    all_sprites.add(boss_2)
                    mobs.add(boss_2)
                    boss_2_defeated = False 

            elif current_wave < TOTAL_WAVES_BEFORE_BOSS:
                create_enemy_formation()
            elif boss_defeated:
                 create_enemy_formation()
            elif not boss:
                 create_enemy_formation()

        # --- Handle enemy bullets hitting players (supports 2 players) ---
        players_to_check = [player]
        if 'player2' in globals() and player2 is not None:
            players_to_check.append(player2)

        for p in players_to_check:
            if not p:
                continue
            hits = pygame.sprite.spritecollide(p, enemy_bullets, True)
            for hit in hits:
                damage = 10
                if getattr(hit, 'speedy', 0) > 5:
                    damage = 20
                p.hp -= damage
            # If hp falls below or equal 0, remove sprite (visual)
            if getattr(p, 'hp', 1) <= 0:
                try:
                    p.kill()
                except Exception:
                    pass

        # --- Handle pickups collection by players ---
        try:
            for p in players_to_check:
                if not p:
                    continue
                hits_pick = pygame.sprite.spritecollide(p, pickups_group, True)
                for pick in hits_pick:
                    # don't heal dead players
                    if getattr(p, 'hp', 0) <= 0:
                        continue
                    heal_amount = 10
                    p.hp = min(getattr(p, 'max_hp', p.hp), p.hp + heal_amount)
                    try:
                        expl_sound.play()
                    except Exception:
                        pass
        except Exception:
            pass

        # After processing both players, determine if game should end
        check_game_over()

    # --- Render ---
        offset_x, offset_y = 0, 0
        if screen_shake_duration > 0:
            offset_x = random.randint(-int(screen_shake_intensity), int(screen_shake_intensity))
            offset_y = random.randint(-int(screen_shake_intensity), int(screen_shake_intensity))
            screen_shake_duration -= 1
            screen_shake_intensity = max(1, screen_shake_intensity - 0.4)
            
        # Draw background and then parallax star layers on top of it (but behind sprites)
        try:
            screen.blit(background_img, (0 + offset_x, 0 + offset_y))
        except Exception:
            screen.fill(BLACK)
        try:
            # draw starfield layers (parallax)
            if 'star_layers' in globals():
                update_and_draw_starfield(screen, star_layers, offset_x, offset_y)
        except Exception:
            pass
        
        if boss_coming or boss_2_coming:
            now = pygame.time.get_ticks()
            if now % 400 < 200:
                red_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                red_overlay.fill((255, 0, 0, 50))
                screen.blit(red_overlay, (offset_x, offset_y))
            
            alert_text = "BOSS 2 ALERT!" if boss_2_coming else "BOSS ALERT!"
            draw_text(screen, alert_text, 64, WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y - 30)
            
        # Draw sprites in two passes: normal sprites, then VFX with additive blending for pop
        try:
            for entity in all_sprites:
                # draw non-vfx sprites normally
                if 'vfx_group' in globals() and entity in vfx_group:
                    continue
                screen.blit(entity.image, (entity.rect.x + offset_x, entity.rect.y + offset_y))
        except Exception:
            # fallback: draw everything
            for entity in all_sprites:
                screen.blit(entity.image, (entity.rect.x + offset_x, entity.rect.y + offset_y))

        # draw VFX (trail, sparks) with additive blending so they glow over the scene
        try:
            if 'vfx_group' in globals():
                for v in vfx_group:
                    try:
                        screen.blit(v.image, (v.rect.x + offset_x, v.rect.y + offset_y), special_flags=pygame.BLEND_ADD)
                    except Exception:
                        screen.blit(v.image, (v.rect.x + offset_x, v.rect.y + offset_y))
        except Exception:
            pass
        
        # --- HUD Panels: move to bottom so they don't overlap enemies ---
        # Score (bottom-left) - smaller
        draw_hud_panel(screen, 10, HEIGHT - 64, 160, 44, title="SCORE")
        draw_text_shadow(screen, str(score), 18, 10 + 80, HEIGHT - 64 + 24, color=YELLOW)

        # Wave (bottom-right) - smaller
        wave_display = elite_wave_count if player_is_upgraded else current_wave
        wave_prefix = "ELITE " if player_is_upgraded else ""
        draw_hud_panel(screen, WIDTH - 190, HEIGHT - 64, 160, 44, title=wave_prefix + "WAVE")
        draw_text_shadow(screen, str(wave_display), 18, WIDTH - 190 + 80, HEIGHT - 64 + 24, color=BRIGHT_GREEN)

        # Player vertical health bars (left and right) - placed to avoid overlapping enemies
        bar_h = 300
        bar_w = 22
        bar_y = 100
        # P1: left vertical bar
        draw_vertical_health_bar(screen, 10, bar_y, bar_w, bar_h, getattr(player, 'hp', 0), getattr(player, 'max_hp', 0))
        draw_text_shadow(screen, "P1", 16, 10 + bar_w // 2, bar_y + bar_h + 10, color=BLUE)
        # P2: right vertical bar if coop enabled
        if enable_coop and 'player2' in globals() and player2 is not None:
            draw_vertical_health_bar(screen, WIDTH - (10 + bar_w), bar_y, bar_w, bar_h, getattr(player2, 'hp', 0), getattr(player2, 'max_hp', 0))
            draw_text_shadow(screen, "P2", 16, WIDTH - (10 + bar_w // 2), bar_y + bar_h + 10, color=RED)

        # Boss health bar: show at top-center (above enemies) when boss present
        if boss and boss.alive():
            draw_text_shadow(screen, "BOSS HP", 18, WIDTH // 2, 12, color=YELLOW)
            draw_boss_health_bar(screen, 50, 32, boss.hp, boss.max_hp)
        elif boss_2 and boss_2.alive():
            draw_text_shadow(screen, "BOSS 2 HP", 18, WIDTH // 2, 12, color=PURPLE)
            draw_boss_health_bar(screen, 50, 32, boss_2.hp, boss_2.max_hp)
        
        pygame.display.flip()

    pygame.mixer.music.stop()
    return "main_menu"


# --- 5. Quit Game ---
def main():
    """Hàm main chính, điều khiển khởi tạo và các trạng thái game."""
    global screen, font_name
    
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter")
    
    font_name = pygame.font.match_font('arial')

    try:
        screen.fill(BLACK)
        draw_text(screen, "LOADING...", 40, WIDTH // 2, HEIGHT // 2 - 20)
        pygame.display.flip()
    except Exception as e:
        print(f"Lỗi khi vẽ màn hình loading: {e}")

    load_all_assets()
    
    current_state = "main_menu"
    
    while current_state != "quit":
        if current_state == "main_menu":
            current_state = main_menu_screen()
        elif current_state == "settings":
            current_state = settings_screen()
        elif current_state == "in_game":
            current_state = run_game() 
            
    pygame.quit()
    exit()

# --- Entry point ---
if __name__ == "__main__":
    main()