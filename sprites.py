import pygame
import random
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GREEN,
    WHITE,
    RED,
    PLAYER_PIXELS,
    SQUID_PIXELS,
    CRAB_PIXELS,
    OCTOPUS_PIXELS,
    UFO_PIXELS
)

def make_surface(pixels, color, scale=3):
    height = len(pixels)
    width = len(pixels[0])
    surf = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    for y, row in enumerate(pixels):
        for x, char in enumerate(row):
            if char == '1':
                pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))
    return surf

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
