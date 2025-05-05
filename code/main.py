import pygame
import os
from random import randint



pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
running: bool = True
clock = pygame.time.Clock()
FPS : int = 60

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join('..',"images", "player.png")).convert_alpha()
        self.frect = self.image.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))

# surface
surf_coord : list = [100,100]
surf : pygame.Surface = pygame.Surface((100,200))
# Surfaces (doesnt allow collisions)
# player_surf: pygame.image = pygame.image.load(os.path.join('..','images','player.png')).convert_alpha()
all_sprites: pygame.sprite.Group = pygame.sprite.Group()
player = Player(all_sprites)
star_surf: pygame.Surface = pygame.image.load(os.path.join('..','images','star.png')).convert_alpha()
laser_surf: pygame.Surface = pygame.image.load(os.path.join('..','images','laser.png')).convert_alpha()
star_positions: list = []
for _ in range(20):
    star_positions.append((randint(50,WINDOW_WIDTH-50),randint(50,WINDOW_HEIGHT-50)))

# FRects
# player_rect: pygame.FRect = player_surf.get_frect(topleft=surf_coord)
laser_buffer : list[pygame.FRect] = []

#movement
# player_mov_direction: float = 1
player_mov_direction: pygame.math.Vector2 = pygame.math.Vector2(0,0)
player_mov_speed: float = 0.01
laser_speed: float = 0.02
laser_reload_speed: float = 0

while running:
    dt = clock.tick(FPS)
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running  = False

    keys_pressed = pygame.key.get_pressed()
    player_mov_direction.x = int(keys_pressed[pygame.K_RIGHT])-int(keys_pressed[pygame.K_LEFT])
    player_mov_direction.y = int(keys_pressed[pygame.K_DOWN])-int(keys_pressed[pygame.K_UP])
    player_mov_direction = player_mov_direction.normalize() if player_mov_direction else player_mov_direction
    player.frect.center += player_mov_direction*player_mov_speed*dt*FPS

    if keys_pressed[pygame.K_SPACE] and laser_reload_speed*dt*FPS==0:
        laser_buffer.append(laser_surf.get_frect(midbottom=player.frect.midtop))
        laser_reload_speed = 30

    if laser_reload_speed:
        laser_reload_speed-=1
    if player.frect.left <= 0:
        player.frect.left = 0
    if player.frect.right >= WINDOW_WIDTH:
        player.frect.right = WINDOW_WIDTH
    if player.frect.top <= 0:
        player.frect.top=0
    if player.frect.bottom >= WINDOW_HEIGHT:
        player.frect.bottom = WINDOW_HEIGHT

    all_sprites.update()

    # draw the game
    display_surface.fill((20,20,20))
    # [display_surface.blit(star_surf, star_position) for star_position in star_positions]
    # display_surface.blit(player.image, player.frect)
    for laser in laser_buffer:
        display_surface.blit(laser_surf, laser)
        laser.centery -= laser_speed*dt*FPS
    all_sprites.draw(display_surface)
    pygame.display.update()

pygame.quit()