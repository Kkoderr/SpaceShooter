import pygame
import os
from random import randint, uniform, random

pygame.init()

WINDOW_WIDTH=1280
WINDOW_HEIGHT=720
main_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
running: bool = True
clock : pygame.time.Clock = pygame.time.Clock()
FPS: int = 60

class Player(pygame.sprite.Sprite):
    def __init__(self, groups: pygame.sprite.Group, laser_sprites: pygame.sprite.Group, laser_sound):
        super().__init__(groups)
        self.groups = groups
        self.image = pygame.image.load(os.path.join('images','player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH//2,WINDOW_HEIGHT//2))
        self.direction = pygame.math.Vector2()
        self.speed = 0.01
        self.can_shoot = True
        self.last_shot = 0
        self.laser_sprites = laser_sprites
        self.mask = pygame.mask.from_surface(self.image)
        self.laser_sound = laser_sound

    def update(self, dt_fps):
        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
        if self.rect.top <= 0:
            self.rect.top = 0

        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction*self.speed*dt_fps

        curr_time = pygame.time.get_ticks()
        if (not self.can_shoot) and (curr_time - self.last_shot) > (1000 - 0.1*dt_fps):
            self.can_shoot=True

        recent_key = pygame.key.get_just_pressed()
        if recent_key[pygame.K_SPACE] and self.can_shoot:
            Laser((self.groups, self.laser_sprites), self.rect.midtop)
            self.laser_sound.play()
            self.can_shoot = False
            self.last_shot = pygame.time.get_ticks()

class Stars(pygame.sprite.Sprite):
    def __init__(self,groups,stars_surface):
        super().__init__(groups)
        self.original_image = stars_surface
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=(randint(50,WINDOW_WIDTH-50), randint(50,WINDOW_HEIGHT-50)))
        self.dimming = -1
        self.alpha_val = randint(0,255)
        self.fade_speed = uniform(0.01,0.04)
    def update(self, dt_fps):
        self.alpha_val += self.dimming*dt_fps*self.fade_speed
        if self.alpha_val>=255 or self.alpha_val<=0:
            self.dimming *= -1
        self.image = self.original_image.copy()
        self.image.set_alpha(self.alpha_val)

class Meteor(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.original_image = pygame.image.load(os.path.join('images','meteor.png')).convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(midtop=(randint(0,WINDOW_WIDTH),0))
        self.mov_direction = pygame.math.Vector2((randint(-1,1), 1))
        self.speed = randint(1,10)*0.0005
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation = 0
        self.rotation_speed= randint(2,4)*0.0001

    def update(self, dt_fps):
        self.mov_direction = self.mov_direction.normalize() if self.mov_direction else self.mov_direction
        self.rect.center += self.mov_direction*self.speed*dt_fps
        self.rotation += self.rotation_speed*dt_fps
        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        if self.rect.centery > WINDOW_HEIGHT+50 or self.rect.centerx < -50 or self.rect.centerx > WINDOW_WIDTH+50:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, initital_position:tuple):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join('images','laser.png')).convert_alpha()
        self.rect = self.image.get_frect(midbottom=initital_position)
        self.speed = 0.06
        self.mask = pygame.mask.from_surface(self.image)

    def update(self,dt_fps):
        self.rect.y -= self.speed*dt_fps
        if self.rect.bottom < 0:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self,groups: pygame.sprite.Group,frames,pos):
        super().__init__(groups)
        self.index = 0
        self.frames = frames
        self.image = self.frames[self.index]
        self.rect = self.image.get_frect(center=pos)
    def update(self, dt_fps):
        self.index += dt_fps*0.001
        if self.index >= len(self.frames)-1:
            self.kill()
        self.image = self.frames[int(self.index) % len(self.frames)]

# def collisions(score):
#     collision_sprites = pygame.sprite.spritecollide(player,meteor_sprites,True, pygame.sprite.collide_mask)
#     if collision_sprites:
#         running = False
#
#     if pygame.sprite.groupcollide(laser_sprites,meteor_sprites,True,True) :
#         score+=1
#         AnimatedExplosion()

all_sprites: pygame.sprite.Group = pygame.sprite.Group()
stars_surf = pygame.image.load(os.path.join('images','star.png')).convert_alpha()
for _ in range(20):
    Stars(all_sprites,stars_surf)

laser_sprites = pygame.sprite.Group()
laser_sound = pygame.mixer.Sound(os.path.join('audio','laser.wav'))
laser_sound.set_volume(0.1)
player = Player(all_sprites,laser_sprites,laser_sound)
meteor_sprites = pygame.sprite.Group()

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,1000)

explosion_frames = [pygame.image.load(os.path.join('images','explosion',f'{i}.png')).convert_alpha() for i in range(21)]
explosion_sound = pygame.mixer.Sound(os.path.join('audio','explosion.wav'))
explosion_sound.set_volume(0.1)

# damage_sound = pygame.mixer.Sound(os.path.join('..','audio','damage.ogg'))
main_theme = pygame.mixer.Sound(os.path.join('audio','game_music.wav'))
main_theme.set_volume(0.2)
main_theme.play(loops=-1)
score : int = 0

def display_score(score:int):
    font = pygame.font.Font(None,40)
    text_surf = font.render(f"{score}", True, (255,255,255))
    return text_surf

game_speed : int = 1

while running:
    dt: int = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor((all_sprites,meteor_sprites))

    all_sprites.update(dt*FPS*game_speed)
    main_screen.fill((10,10,10))
    all_sprites.draw(main_screen)
    player_meteor_collision = pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask)
    if player_meteor_collision:
        running = False
        print(player_meteor_collision)

    laser_meteor_collision = pygame.sprite.groupcollide(laser_sprites,meteor_sprites,True,True)
    if laser_meteor_collision:
        score+=1
        game_speed += 0.01
        # print(list(laser_meteor_collision.values())[0][0].rect.center)
        for i in range(len(list(laser_meteor_collision.values())[0])):
            AnimatedExplosion(all_sprites, explosion_frames, list(laser_meteor_collision.values())[0][i].rect.center)
            explosion_sound.play()
    main_screen.blit(display_score(score), (WINDOW_WIDTH//2,WINDOW_HEIGHT-50))
    pygame.display.update()

pygame.quit()
