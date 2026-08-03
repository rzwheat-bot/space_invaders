import pygame
import random
import json
import os

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Colors (Retro Arcade Style)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game States
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_ENTER_NAME = "ENTER_NAME"
STATE_LEADERBOARD = "LEADERBOARD"

# High Scores File
HIGH_SCORES_FILE = "high_scores.json"

# --- Sprite Bitmaps (Retro Pixel Art) ---
PLAYER_PIXELS = [
    "      11      ",
    "     1111     ",
    "     1111     ",
    " 111111111111 ",
    "11111111111111",
    "11111111111111",
    "11111111111111",
]

SQUID_PIXELS = [
    "   110011   ",
    "  11111111  ",
    " 1111111111 ",
    "111001100111",
    "111111111111",
    "  11011011  ",
    " 1100000011 ",
    "  11    11  ",
]

CRAB_PIXELS = [
    "  10000001  ",
    "   100001   ",
    "  11111111  ",
    " 1101110111 ",
    "111111111111",
    "1 11111111 1",
    "1 1      1 1",
    "   11  11   ",
]

OCTOPUS_PIXELS = [
    "    1111    ",
    " 1111111111 ",
    "111111111111",
    "111001100111",
    "111111111111",
    "  11100111  ",
    " 1101111011 ",
    "11      1111",
]

UFO_PIXELS = [
    "     111111     ",
    "   1111111111   ",
    "  111111111111  ",
    " 11011011011011 ",
    "1111111111111111",
    "  111      111  ",
]

def make_surface(pixels, color, scale=3):
    height = len(pixels)
    width = len(pixels[0])
    surf = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    for y, row in enumerate(pixels):
        for x, char in enumerate(row):
            if char == '1':
                pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))
    return surf

# --- Classes ---
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = make_surface(PLAYER_PIXELS, GREEN, scale=3)
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = 4

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Boundary checks
        if self.rect.left < 10:
            self.rect.left = 10
        if self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10

class Invader(pygame.sprite.Sprite):
    def __init__(self, x, y, invader_type):
        super().__init__()
        self.type = invader_type
        if invader_type == "squid":
            self.image = make_surface(SQUID_PIXELS, WHITE, scale=3)
            self.points = 30
        elif invader_type == "crab":
            self.image = make_surface(CRAB_PIXELS, WHITE, scale=3)
            self.points = 20
        else:
            self.image = make_surface(OCTOPUS_PIXELS, WHITE, scale=3)
            self.points = 10
            
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, direction_x, step_down):
        self.rect.x += direction_x
        if step_down:
            self.rect.y += 8

class UFO(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = make_surface(UFO_PIXELS, RED, scale=3)
        self.speed = 3
        # Spawn left or right
        if random.choice([True, False]):
            self.rect = self.image.get_rect(topleft=(-60, 60))
            self.direction = 1
        else:
            self.rect = self.image.get_rect(topright=(SCREEN_WIDTH + 60, 60))
            self.direction = -1

    def update(self):
        self.rect.x += self.speed * self.direction
        if (self.direction == 1 and self.rect.left > SCREEN_WIDTH) or (self.direction == -1 and self.rect.right < 0):
            self.kill()

class BunkerBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Game Manager ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SPACE INVADERS")
        self.clock = pygame.time.Clock()
        self.state = STATE_START
        
        # Fonts
        self.font_title = pygame.font.SysFont("Courier New", 48, bold=True)
        self.font_menu = pygame.font.SysFont("Courier New", 24, bold=True)
        self.font_hud = pygame.font.SysFont("Courier New", 20, bold=True)
        
        # High Scores Load
        self.high_scores = self.load_high_scores()
        
        # Player Input Init
        self.player_initials = ""
        self.new_high_score = 0
        
        # Active Game state
        self.reset_game_stats()

    def reset_game_stats(self):
        self.score = 0
        self.lives = 3
        self.last_extra_life_score = 0
        
        # Sprite groups
        self.player_group = pygame.sprite.GroupSingle()
        self.player = Player()
        self.player_group.add(self.player)
        
        self.invaders = pygame.sprite.Group()
        self.ufo_group = pygame.sprite.GroupSingle()
        self.player_lasers = pygame.sprite.Group()
        self.invader_lasers = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        
        self.invader_direction = 1
        self.invader_speed = 1.0
        self.ufo_timer = pygame.time.get_ticks()
        self.laser_cooldown = 0
        
        self.create_invader_grid()
        self.create_all_bunkers()

    def create_invader_grid(self):
        # 4 rows of 8 invaders (making it easier to clear before they descend)
        row_types = ["squid", "crab", "octopus", "octopus"]
        for row, r_type in enumerate(row_types):
            for col in range(8):
                x = 80 + col * 55
                y = 120 + row * 45
                self.invaders.add(Invader(x, y, r_type))

    def create_bunker(self, start_x, start_y):
        # Bunker layout
        # 1 = block, 0 = empty space
        layout = [
            [0,0,1,1,1,1,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,0,0,0,0,1,1,1,1],
            [1,1,1,0,0,0,0,0,0,1,1,1],
            [1,1,0,0,0,0,0,0,0,0,1,1]
        ]
        for row_idx, row in enumerate(layout):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    x = start_x + col_idx * 6
                    y = start_y + row_idx * 6
                    self.bunkers.add(BunkerBlock(x, y, GREEN))

    def create_all_bunkers(self):
        bunker_xs = [80, 200, 320, 440]
        for bx in bunker_xs:
            self.create_bunker(bx, SCREEN_HEIGHT - 130)

    def load_high_scores(self):
        if os.path.exists(HIGH_SCORES_FILE):
            try:
                with open(HIGH_SCORES_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default retro fallback list
        default_scores = [
            {"name": "AAA", "score": 1000},
            {"name": "COM", "score": 900},
            {"name": "RET", "score": 800},
            {"name": "PLR", "score": 700},
            {"name": "ARC", "score": 600},
            {"name": "MID", "score": 500},
            {"name": "CAP", "score": 400},
            {"name": "GAL", "score": 300},
            {"name": "NES", "score": 200},
            {"name": "INV", "score": 100}
        ]
        self.save_high_scores(default_scores)
        return default_scores

    def save_high_scores(self, scores):
        try:
            with open(HIGH_SCORES_FILE, "w") as f:
                json.dump(scores, f, indent=4)
        except Exception as e:
            print(f"Error saving high scores: {e}")

    def update_high_scores(self, name, score):
        self.high_scores.append({"name": name.upper(), "score": score})
        # Sort descending by score, keep top 10
        self.high_scores = sorted(self.high_scores, key=lambda x: x["score"], reverse=True)[:10]
        self.save_high_scores(self.high_scores)

    def is_new_high_score(self, score):
        if score == 0:
            return False
        if len(self.high_scores) < 10:
            return True
        return score > self.high_scores[-1]["score"]

    def fire_laser(self):
        if self.laser_cooldown <= 0:
            # Spawn laser from player top center (faster laser speed and lower cooldown)
            self.player_lasers.add(Laser(self.player.rect.centerx, self.player.rect.top, -9, GREEN))
            self.laser_cooldown = 18 # frames cooldown (~0.3s)

    def invaders_shoot(self):
        # Pick random column invaders to shoot
        if self.invaders:
            # Group invaders by columns
            cols = {}
            for inv in self.invaders:
                col_key = inv.rect.x
                if col_key not in cols or inv.rect.y > cols[col_key].rect.y:
                    cols[col_key] = inv # Bottom-most invader in the column
            
            shooters = list(cols.values())
            if shooters and random.random() < 0.02 + (0.005 * (4 - self.lives)): # Shoot probability increases as player loses lives
                shooter = random.choice(shooters)
                self.invader_lasers.add(Laser(shooter.rect.centerx, shooter.rect.bottom, 4, RED))

    def check_collisions(self):
        # 1. Player lasers hitting invaders
        for laser in self.player_lasers:
            hit_invaders = pygame.sprite.spritecollide(laser, self.invaders, True)
            if hit_invaders:
                laser.kill()
                for inv in hit_invaders:
                    self.score += inv.points
                
                # Check extra life award (Every 1000 points)
                if (self.score // 1000) > (self.last_extra_life_score // 1000):
                    self.lives += 1
                    self.last_extra_life_score = self.score
                break

        # 2. Player lasers hitting UFO
        if self.ufo_group:
            ufo = self.ufo_group.sprite
            hit_ufo = pygame.sprite.spritecollide(ufo, self.player_lasers, True)
            if hit_ufo:
                ufo.kill()
                # Mystery points
                mystery_points = random.choice([50, 100, 150, 300])
                self.score += mystery_points

        # 3. Invader lasers hitting Player
        if self.player_group:
            hit_player = pygame.sprite.spritecollide(self.player, self.invader_lasers, True)
            if hit_player:
                self.lives -= 1
                if self.lives > 0:
                    self.player = Player()
                    self.player_group.add(self.player)
                else:
                    self.end_game()

        # 4. Player lasers hitting Bunker Blocks
        pygame.sprite.groupcollide(self.player_lasers, self.bunkers, True, True)

        # 5. Invader lasers hitting Bunker Blocks
        pygame.sprite.groupcollide(self.invader_lasers, self.bunkers, True, True)

        # 6. Invaders colliding directly with Bunker Blocks
        pygame.sprite.groupcollide(self.invaders, self.bunkers, False, True)

        # 7. Invaders reaching player bottom line
        for inv in self.invaders:
            if inv.rect.bottom >= SCREEN_HEIGHT - 80:
                self.end_game()
                break

    def end_game(self):
        if self.is_new_high_score(self.score):
            self.new_high_score = self.score
            self.player_initials = ""
            self.state = STATE_ENTER_NAME
        else:
            self.state = STATE_LEADERBOARD

    def update_invaders(self):
        # Determine if invaders hit bounds
        reached_boundary = False
        for inv in self.invaders:
            if inv.rect.left < 10 and self.invader_direction == -1:
                reached_boundary = True
                break
            if inv.rect.right > SCREEN_WIDTH - 10 and self.invader_direction == 1:
                reached_boundary = True
                break

        step_down = False
        if reached_boundary:
            self.invader_direction *= -1
            step_down = True
            # Speed increases slightly on step down (slower increase rate)
            self.invader_speed += 0.05

        self.invaders.update(self.invader_direction * self.invader_speed, step_down)

        # Spawn a new grid of invaders if they are all cleared
        if not self.invaders:
            self.invader_speed = 1.0 + (self.score // 3000) * 0.5 # Difficulty scales
            self.create_invader_grid()

    def update(self):
        if self.state == STATE_PLAYING:
            # Cooldowns
            if self.laser_cooldown > 0:
                self.laser_cooldown -= 1
                
            # Inputs
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.fire_laser()
                
            # Entity Updates
            self.player_group.update()
            self.update_invaders()
            self.invaders_shoot()
            
            # Laser updates
            self.player_lasers.update()
            self.invader_lasers.update()
            
            # UFO Spawn & Update
            now = pygame.time.get_ticks()
            if not self.ufo_group.sprite and now - self.ufo_timer > random.randint(15000, 25000): # ~15-25 seconds
                self.ufo_group.add(UFO())
                self.ufo_timer = now
            self.ufo_group.update()
            
            # Checks
            self.check_collisions()

    def draw_hud(self):
        # Top HUD (Score / Lives / Next Extra Life info)
        score_surf = self.font_hud.render(f"SCORE: {self.score:05d}", True, WHITE)
        self.screen.blit(score_surf, (20, 15))
        
        # Draw Lives as mini player icons
        lives_label = self.font_hud.render("SHIPS: ", True, WHITE)
        self.screen.blit(lives_label, (SCREEN_WIDTH - 180, 15))
        for i in range(self.lives):
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 110 + i * 28, 18, 16, 10))
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 110 + i * 28 + 4, 14, 8, 4))
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 110 + i * 28 + 7, 10, 2, 4))

        # Green bottom separator line
        pygame.draw.line(self.screen, GREEN, (0, SCREEN_HEIGHT - 40), (SCREEN_WIDTH, SCREEN_HEIGHT - 40), 2)

    def draw_start_screen(self):
        self.screen.fill(BLACK)
        
        # Title
        title_surf = self.font_title.render("SPACE INVADERS", True, GREEN)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 100))
        
        # Subtitle
        play_surf = self.font_menu.render("PRESS SPACE TO PLAY", True, WHITE)
        self.screen.blit(play_surf, (SCREEN_WIDTH // 2 - play_surf.get_width() // 2, 220))
        
        # Leaderboard Quick View
        lead_title = self.font_menu.render("TOP TEN COMMANDERS", True, YELLOW)
        self.screen.blit(lead_title, (SCREEN_WIDTH // 2 - lead_title.get_width() // 2, 320))
        
        for idx, item in enumerate(self.high_scores[:5]):
            row_str = f"{idx+1:02d}. {item['name']:<5} {item['score']:05d}"
            row_surf = self.font_menu.render(row_str, True, WHITE)
            self.screen.blit(row_surf, (SCREEN_WIDTH // 2 - 120, 380 + idx * 35))

        credit_surf = self.font_hud.render("EXTRA SHIP AWARDED EVERY 1000 PTS", True, RED)
        self.screen.blit(credit_surf, (SCREEN_WIDTH // 2 - credit_surf.get_width() // 2, SCREEN_HEIGHT - 80))

    def draw_enter_name_screen(self):
        self.screen.fill(BLACK)
        
        title_surf = self.font_title.render("GAME OVER", True, RED)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 150))
        
        score_surf = self.font_menu.render(f"NEW HIGH SCORE: {self.new_high_score}", True, GREEN)
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 250))
        
        prompt_surf = self.font_menu.render("ENTER YOUR INITIALS (3 CHARS):", True, WHITE)
        self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 330))
        
        # Display name entry
        cursor_display = "_" if pygame.time.get_ticks() % 1000 < 500 else " "
        entry_str = f"{self.player_initials:<3}".replace(" ", "_")
        if len(self.player_initials) < 3:
            entry_str = self.player_initials + cursor_display + "_" * (2 - len(self.player_initials))
            
        entry_surf = self.font_title.render(entry_str, True, YELLOW)
        self.screen.blit(entry_surf, (SCREEN_WIDTH // 2 - entry_surf.get_width() // 2, 420))
        
        tip_surf = self.font_hud.render("PRESS ENTER TO SUBMIT", True, GREEN)
        self.screen.blit(tip_surf, (SCREEN_WIDTH // 2 - tip_surf.get_width() // 2, 530))

    def draw_leaderboard_screen(self):
        self.screen.fill(BLACK)
        
        title_surf = self.font_title.render("LEADERBOARD", True, GREEN)
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 80))
        
        for idx, item in enumerate(self.high_scores):
            row_str = f"{idx+1:02d}. {item['name']:<5} {item['score']:05d}"
            row_surf = self.font_menu.render(row_str, True, WHITE)
            self.screen.blit(row_surf, (SCREEN_WIDTH // 2 - 120, 160 + idx * 40))
            
        prompt_surf = self.font_menu.render("PRESS SPACE FOR MAIN MENU", True, YELLOW)
        self.screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, SCREEN_HEIGHT - 100))

    def draw(self):
        if self.state == STATE_START:
            self.draw_start_screen()
        elif self.state == STATE_PLAYING:
            self.screen.fill(BLACK)
            self.player_group.draw(self.screen)
            self.invaders.draw(self.screen)
            self.ufo_group.draw(self.screen)
            self.player_lasers.draw(self.screen)
            self.invader_lasers.draw(self.screen)
            self.bunkers.draw(self.screen)
            self.draw_hud()
        elif self.state == STATE_ENTER_NAME:
            self.draw_enter_name_screen()
        elif self.state == STATE_LEADERBOARD:
            self.draw_leaderboard_screen()
            
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            # Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if self.state == STATE_START:
                        if event.key == pygame.K_SPACE:
                            self.reset_game_stats()
                            self.state = STATE_PLAYING
                            
                    elif self.state == STATE_ENTER_NAME:
                        if event.key == pygame.K_RETURN and len(self.player_initials) == 3:
                            self.update_high_scores(self.player_initials, self.new_high_score)
                            self.state = STATE_LEADERBOARD
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_initials = self.player_initials[:-1]
                        elif len(self.player_initials) < 3 and event.unicode.isalpha():
                            self.player_initials += event.unicode.upper()
                            
                    elif self.state == STATE_LEADERBOARD:
                        if event.key == pygame.K_SPACE:
                            self.state = STATE_START
            
            self.update()
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
