import pygame
from pygame import mixer
import sys
from random import randint

# pygame inits
mixer.init()
pygame.init()

# sounds
start_screen_music = mixer.Sound("project/audio/music.wav")
level_screen_music = mixer.Sound("project/audio/level_music.mp3")
final_wave_music = mixer.Sound("project/audio/final_wave.mp3")
gexplosion = mixer.Sound("project/audio/effects/g_explosion.mp3")
gshot = mixer.Sound("project/audio/effects/gun_shot.mp3")

# sound booleans
playing = False
final_playing = False
 
# screen variables
SCREEN_WIDTH, SCREEN_HEIGHT = 1300, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Arena Dance")
main_font = pygame.font.Font("project/font/font.ttf", 40)
pygame.display.set_icon(pygame.image.load("project/player/attack/tile000.png").convert_alpha())
clock = pygame.time.Clock()
ENDGAME = False

# levels bgs
lvl0 = True # controls and phase 1
lvl1 = False # phase 2
lvl2 = False # phase 3
lvl3 = False # the last dance

# ------------- load images -------------

# main menu
main_surface = pygame.image.load(
    "project/backgrounds/first.png").convert_alpha()
start_surface = pygame.image.load(
    "project/icons/start.png").convert_alpha()

# death screen
death_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
death_surface.fill((0, 0, 0))

# game screen
ground_img = pygame.image.load("project/environment/map/ground.png").convert_alpha()
ground_img = pygame.transform.scale_by(ground_img, 3.5)

# first phase
level_one_bg = pygame.image.load(
    "project/backgrounds/levelonebg.jpg").convert_alpha()

# second phase
level_two_bg = pygame.image.load("project/backgrounds/test.jpg").convert_alpha()
level_two_bg = pygame.transform.scale(level_two_bg, (SCREEN_WIDTH+ 200, SCREEN_HEIGHT + 200))
level_two = level_two_bg.get_rect()

# third phase 
level_three_bg = pygame.image.load("project/backgrounds/levelthreebg.jpg").convert_alpha()
level_three_bg = pygame.transform.scale(level_three_bg, (SCREEN_WIDTH + 200, SCREEN_HEIGHT + 200))
level_three = level_two_bg.get_rect()

# final phase
final_bg = pygame.image.load("project/backgrounds/final.jpg").convert_alpha()
final_bg = pygame.transform.scale(final_bg, (SCREEN_WIDTH + 200, SCREEN_HEIGHT + 200))
final_rect = final_bg.get_rect()

# credits phase
thx = pygame.image.load("project/backgrounds/thx.png").convert_alpha()
text = pygame.image.load("project/icons/CONTROLS.png").convert_alpha()
text_rect = text.get_rect(center = (SCREEN_WIDTH / 2, 300))

# background movement variables
dr = 1
dx = 0
DY = 0

# text rendering
wave_completetxt = main_font.render("WAVE COMPLETE !", True, (85, 255, 0)).convert_alpha()
wave_completetxt_rect = wave_completetxt.get_rect(center = (SCREEN_WIDTH/2 - 20, 200))
finaltxt = main_font.render("THE LAST DANCE", True, (255, 0, 0)).convert_alpha()
finaltxt_rect = finaltxt.get_rect(center = (SCREEN_WIDTH/2 - 20, 300))
bonustxt = main_font.render("WAVE COMPLETE !", True, (85, 255, 0)).convert_alpha()
bonustxt_rect = wave_completetxt.get_rect(center = (SCREEN_WIDTH/2 - 20, 200))

# transition effect
start_music_volume = 1
fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
fade_surface.fill((0, 0, 0))
fade_alpha = 0
fade_speed = 255 / 90
fade_screen_1 = 255
 
# state management
not_loaded = [1, 1, 1]
TRANSITION = False
START_SCREEN = 0
LEVEL_ONE = 1
DEATH_SCREEN = 2
LEVEL_TWO = 3
LEVEL_THREE = 4
game_state = START_SCREEN

# wave management
WAVE = 0
cd = 150
 
# game physics variables
kills = 0
moving_right = False
moving_left = False
throw_grenade = False
crouch = False
shooting = False
reloading = False
crouch = False
jump=False
Gravity=0.74 
GROUND_LEVEL = 600
ground_rect = ground_img.get_rect(center = (700, GROUND_LEVEL + 240))

# soldier class
class Soldier(pygame.sprite.Sprite):
    def __init__(self, path, x, y, scale, speed, type: str, dir):
        pygame.sprite.Sprite.__init__(self)
        
        # soldier properties
        self.alive = True
        self.dead = False
        self.health = 100
        self.cooldown = 0
        self.gcooldown = 0
        self.rcooldown = 0
        self.type = type
        self.direction = dir
        self.speed = speed
        self.jump = False             
        self.state = 0 # [stop, run, shoot, reload]
        self.on_ground = True        
        self.y_vel = 0     
        self.s = False
        if dir > 0:
            self.flip = False
        else:
            self.flip = True
        self.death_cooldown = 100
        

        # inventory
        self.max_ammo = 30
        self.magazine = 30
        self.ammo = self.magazine
        self.grenades = 3
 
        # player animations
        self.run_animation = []
        self.idle_animation = []
        self.attack_stand = []
        self.crouchshoot = []
        self.rel_animation = []
        self.death_animation = []

        # g1 animations
        self.g1_idle_animation = []
        self.g1_shoot_animation = []
        self.g1_walk_animation = []
        self.g1_die_animation = []

        # g3 animations
        self.g3_idle_animation = []
        self.g3_shoot_animation = []
        self.g3_walk_animation = []
        self.g3_die_animation = []

        self.animation_index = 0

        # player animation loading
        for i in range(8): # idle
            img = pygame.image.load(f"project/player/idle/tile00{i}.png").convert_alpha()
            self.idle_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(9): # run
            img = pygame.image.load(f"project/player/run/tile00{i}.png").convert_alpha()
            self.run_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(2, 4): # shoot
            img = pygame.image.load(f"project/player/attack/tile00{i}.png").convert_alpha() 
            self.attack_stand.append(pygame.transform.scale_by(img, 2))
        for i in range(2, 4): # crouch shooting
            img = pygame.image.load(f"project/player/crouch/tile00{i}.png").convert_alpha()
            self.crouchshoot.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 7):
            img = pygame.image.load(f"project/player/reload/r{i}.png").convert_alpha()
            self.rel_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 4):
            img = pygame.image.load(f"project/player/dead/tile00{i}.png").convert_alpha()
            self.death_animation.append(pygame.transform.scale_by(img, 2))

        # gangster 1 animation loading
        for i in range(0, 5):
            img = pygame.image.load(f"project/enemy/gangsters/g1/idle/i{i}.png").convert_alpha()
            self.g1_idle_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 4):
            img = pygame.image.load(f"project/enemy/gangsters/g1/shoot/s{i}.png").convert_alpha()
            self.g1_shoot_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 10):
            img = pygame.image.load(f"project/enemy/gangsters/g1/walk/w{i}.png").convert_alpha()
            self.g1_walk_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 5):
            img = pygame.image.load(f"project/enemy/gangsters/g1/die/d{i}.png").convert_alpha()
            self.g1_die_animation.append(pygame.transform.scale_by(img, 2))

        # gangster 2 animation loading
        for i in range(0, 7):
            img = pygame.image.load(f"project/enemy/gangsters/g3/idle/i{i}.png").convert_alpha()
            self.g3_idle_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 9):
            img = pygame.image.load(f"project/enemy/gangsters/g3/shoot/s{i}.png").convert_alpha()
            self.g3_shoot_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 9):
            img = pygame.image.load(f"project/enemy/gangsters/g3/walk/w{i}.png").convert_alpha()
            self.g3_walk_animation.append(pygame.transform.scale_by(img, 2))
        for i in range(0, 5):
            img = pygame.image.load(f"project/enemy/gangsters/g3/death/d{i}.png").convert_alpha()
            self.g3_die_animation.append(pygame.transform.scale_by(img, 2))
        
        # Soldier image and rect
        self.path = path
        img = pygame.image.load(fr"{self.path}").convert_alpha()
        self.image = pygame.transform.scale(
            img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.image = pygame.transform.scale_by(self.image, 2)
        self.rect = self.image.get_rect() # fixed rect
        self.rect.midbottom = (x, y)

        # hitbox variable
        if self.type == 'player':
            self.hitbox = pygame.Rect(self.rect.left + self.rect.width/3, self.rect.top, self.rect.width / 2, self.rect.height)

        # ai behaviour variables
        self.idletime = 150
        self.alert = False
        self.originx = self.rect.centerx 
    
    # shooting method
    def shoot(self):
        head_position = self.rect.top
        if crouch:
            head_position += 25
        if self.ammo > 0:
            if self.cooldown == 0:
                self.cooldown = 10
                pygame.mixer.Channel(1).play(gshot, 0, 1000, 1)
                bullet.add(Bullet((self.rect.centerx + self.rect.width * self.direction), head_position + 35, self.direction, 'player'))
                bullet.draw(screen)
                self.ammo -= 1
    
    # reloading method
    def reload(self):
        self.animation_index = 0
        diff = self.magazine - self.ammo
        if self.max_ammo >= diff:
            self.ammo += diff
            self.max_ammo -= diff
        else:
            self.ammo += self.max_ammo
            self.max_ammo = 0
        if self.rcooldown == 0:
            self.rcooldown == 50

    # movement method
    def move(self):

        # reset movement variables
        dx = 0
        dy = 0

        # apply gravity
        if not self.on_ground:
            self.y_vel += Gravity  # Increase y_vel due to gravity #used to detect ground
        else:
            self.y_vel = 0  # Reset y_vel when on the ground

        # player movement
        if self.type == 'player' and not self.dead:
            if moving_left and moving_right: 
                self.state = 0
                dx = 0

            # reload
            elif reloading and self.max_ammo > 0:
                self.state = 3

            # shoot
            elif shooting and self.ammo > 0:
                self.shoot()
                self.state = 2

            # strafe
            elif moving_right:
                if self.rect.right >= ground_rect.right:
                    dx = 0
                else:
                    dx = self.speed
                self.state = 1
                self.direction = 1
                self.flip = False
            elif moving_left:
                if self.rect.left <= ground_rect.left:
                    dx = 0
                else:
                    dx = -self.speed
                self.state = 1
                self.direction = -1
                self.flip = True
            else:
                self.state = 0
                dx = 0

            # grenade throw
            if throw_grenade and not crouch and self.gcooldown == 0:
                self.gcooldown = 100
                if self.grenades > 0:
                    grenade.add(Grenade(self.rect.centerx, self.rect.centery, self.direction))
                    self.grenades -= 1

            # jump
            if self.jump and self.on_ground and not reloading:  # Allow jump only if on the ground
                self.y_vel = -12  # Set upward velocity for jump                     
                self.jump = False
                self.on_ground = False  # Player is no longer on the ground
            dy += self.y_vel
        
            # check for ground collision
            if self.rect.bottom + dy > GROUND_LEVEL:
                self.on_ground = True  # player is on the ground
                self.rect.bottom = GROUND_LEVEL - dy  # snap to ground level

        # gangsters movement (ai behaviour)
        elif (self.type == 'g1' or self.type == 'g3') and not self.dead:
            if self.rect.right > ground_rect.right:
                dy += 10
            elif self.rect.left < ground_rect.left:
                dy += 10

            dist = abs(self.rect.centerx - self.originx)
            if self.idletime > 0 and dist >= 200:
                self.state = 0
            else:
                self.state = 1
            if not self.alert:
                if dist <= 200:
                    if dist == 0 and not self.flip:
                        self.direction = 1
                        dx = self.speed
                    elif not self.flip and dist < 200:
                        if self.rect.right >= ground_rect.right:
                            dx = 0
                            self.flip = True
                        else:
                            dx = self.speed
                        self.direction = 1
                    elif dist >= 200 and self.idletime == 0:
                        self.idletime = 150
                        if self.flip:
                            self.direction = -1
                            dx = - self.speed
                        else:
                            self.direction = 1
                            dx = self.speed 
                    elif self.flip and dist < 200:
                        if self.rect.left <= ground_rect.left:
                            dx = 0
                            self.flip = False
                        else:
                            dx = -self.speed 
                        self.direction = -1
                else:
                    self.idletime = 0
                    if self.rect.centerx < self.originx:
                        self.direction = 1
                        self.flip = False
                        dx = self.speed
                    else:
                        self.direction = -1
                        dx = -self.speed
                        self.flip = True
                dy += self.y_vel
            else:
                
                # alert if player is detected
                if not player.sprite.dead:
                    self.state = 2
                    if player.sprite.rect.centerx < self.rect.centerx:
                        self.flip = True
                        self.direction = -1
                    elif player.sprite.rect.centerx > self.rect.centerx:
                        self.flip = False
                        self.direction = 1
                    if self.cooldown == 0:
                        channel_id = 0
                        if self.type == 'g1':
                            channel_id= 0
                            self.cooldown = 15
                        elif self.type == 'g3':
                            channel_id = 2
                            self.cooldown = 30
                        pygame.mixer.Channel(channel_id).play(gshot, 0, 1000, 1)
                        bullet.add(Bullet((self.rect.centerx + (self.rect.width - 5) * self.direction), self.rect.top + 65, self.direction, 'g1'))
                else:
                    self.alert = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy
        if self.type == 'player':
            self.hitbox.x += dx
            self.hitbox.y += dy
 
    # update the sprite per frame
    def update(self):

        # initialising global variables
        global reloading
        global TRANSITION
        global kills
        global start_music_volume

        # if enemy falls of ground kill it
        if self.rect.centery > SCREEN_HEIGHT:
            kills += 1
            self.kill()

        # cooldown for bullets
        if self.cooldown > 0:
            self.cooldown -= 1

        # cooldown for grenades
        if self.gcooldown > 0:
            self.gcooldown -= 1

        # cooldown for reload
        if self.rcooldown > 0:
            self.rcooldown -= 1
        
        # reload if empty bullets
        if self.ammo == 0 and self.max_ammo > 0:
            self.state = 3
            reloading = True
 
        self.move()
        self.animation()
        
        # debugging if/else
        # if self.type == 'player':
        #     pygame.draw.rect(screen, "Red", self.hitbox, 5)
        # pygame.draw.rect(screen, "Green", self.rect, 2)

        # check if player is in sight (ai behaviour)
        if self.type == 'g1' or self.type == 'g3':
            dist = abs(self.rect.centerx - player.sprite.rect.centerx)
            if self.direction == 1 and player.sprite.rect.centerx > self.rect.centerx and dist < 1000:
                self.alert = True
            elif self.direction == -1 and player.sprite.rect.centerx < self.rect.centerx and dist < 1000:
                self.alert = True
            elif dist > 1000:
                self.alert = False

        # ai idle time
        if self.idletime > 0 and self.state < 1:
            self.idletime -= 1

        # apply death cooldown if player is dead
        if self.dead and self.type == 'player':
            start_music_volume -= 0.01
            self.death_cooldown -= 1
        
        # apply death screen if death cooldown approches zero
        if self.death_cooldown <= 0:
            pygame.mixer_music.load("project/audio/death_music.mp3")
            hud.cd = 200
            kills = 0
            TRANSITION = True
 
        # soldier dies
        if self.health <= 0 and not self.dead:
            self.animation_index = 0
            self.dead = True
            if not self.type == 'player':
                kills += 1
 
        # delete the sprite after certain time
        if self.dead:
            self.rect.width = 0
    
    def animation(self):
        global reloading

        # player
        if self.type == 'player':
            self.hitbox.top = self.rect.top
            self.hitbox.height = self.rect.height
            if self.state == 2:
                self.animation_index += 0.3
            else:
                self.animation_index += 0.2

            # death animation
            if self.dead:
                if self.animation_index < len(self.death_animation):
                    screen.blit(pygame.transform.flip(self.death_animation[int(self.animation_index)], self.flip, False), self.rect)
                else:
                    screen.blit(pygame.transform.flip(self.death_animation[-1], self.flip, False), self.rect)
                    
            # reload animation
            elif self.state == 3:
                if not self.s:
                    self.s = True
                    self.rect.y -= 25
                if self.animation_index >= len(self.rel_animation):
                    reloading = False
                    self.reload()
                    self.rect.y += 25
                    self.s = False
                else:
                    screen.blit(pygame.transform.flip(self.rel_animation[int(self.animation_index)], self.flip, False), self.rect)

            # run animation
            elif self.state == 1: 
                if self.animation_index >= len(self.run_animation):
                    self.animation_index = 0
                screen.blit(pygame.transform.flip(self.run_animation[int(self.animation_index)], self.flip, False), self.rect)

            # crouch animation
            elif crouch:
                if self.hitbox.top == self.rect.top:
                    self.hitbox.top += 25
                    self.hitbox.height -= 25
                if self.animation_index >= len(self.crouchshoot):
                    self.animation_index = 0
                if self.state == 2:
                    screen.blit(pygame.transform.flip(self.crouchshoot[int(self.animation_index)], self.flip, False), self.rect)
                elif self.state == 0:
                    img = pygame.image.load("project/player/crouch/tile000.png").convert_alpha()
                    screen.blit(pygame.transform.flip(pygame.transform.scale_by(img , 2), self.flip, False), self.rect)

            # idle animation
            elif self.state == 0: 
                if self.animation_index >= len(self.idle_animation):
                    self.animation_index = 0
                screen.blit(pygame.transform.flip(self.idle_animation[int(self.animation_index)], self.flip, False), self.rect)

            # shoot animation
            elif self.state == 2 and self.ammo > 0: 
                if self.animation_index >= len(self.attack_stand):
                    self.animation_index = 0
                screen.blit(pygame.transform.flip(self.attack_stand[int(self.animation_index)], self.flip, False), self.rect)

        # gangster 1 animations
        elif self.type == 'g1':
            if not self.dead:
                if self.state == 2:
                    self.animation_index += 0.3
                else:
                    self.animation_index += 0.1
                if self.state == 1:
                    # walk
                    if self.animation_index >= len(self.g1_walk_animation):
                        self.animation_index = 0
                    screen.blit(pygame.transform.flip(self.g1_walk_animation[int(self.animation_index)], self.flip, False), self.rect)
                elif self.state == 0:
                    # idle
                    if self.animation_index >= len(self.g1_idle_animation):
                        self.animation_index = 0
                    screen.blit(pygame.transform.flip(self.g1_idle_animation[int(self.animation_index)], self.flip, False), self.rect)
                elif self.state == 2:
                    # shoot
                    if self.animation_index >= len(self.g1_shoot_animation):
                        self.animation_index = 0
                    screen.blit(pygame.transform.flip(self.g1_shoot_animation[int(self.animation_index)], self.flip, False), self.rect)
            else:
                # death
                self.animation_index += 0.1
                if self.animation_index >= len(self.g1_die_animation):
                    self.kill()
                else:
                    screen.blit(pygame.transform.flip(self.g1_die_animation[int(self.animation_index)], self.flip, False), self.rect)
        # gangster 2 animations
        elif self.type == 'g3':
            if not self.dead:
                if self.state == 2:
                    self.animation_index += 0.3
                else:
                    self.animation_index += 0.1
                if self.state == 1:
                    # walk
                    if self.animation_index >= len(self.g3_walk_animation):
                        self.animation_index = 0
                    screen.blit(pygame.transform.flip(self.g3_walk_animation[int(self.animation_index)], self.flip, False), self.rect)
                elif self.state == 0:
                    # idle
                    if self.animation_index >= len(self.g3_idle_animation):
                        self.animation_index = 0
                    screen.blit(pygame.transform.flip(self.g3_idle_animation[int(self.animation_index)], self.flip, False), self.rect)
                elif self.state == 2:
                    # shoot
                    if self.animation_index >= len(self.g3_shoot_animation):
                        self.animation_index = 0
                    screen.blit(pygame.transform.flip(self.g3_shoot_animation[int(self.animation_index)], self.flip, False), self.rect)
            else:
                # death
                self.animation_index += 0.1
                if self.animation_index >= len(self.g3_die_animation):
                    self.kill()
                else:
                    screen.blit(pygame.transform.flip(self.g3_die_animation[int(self.animation_index)], self.flip, False), self.rect)
                    
# bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, d, shooter):
        super().__init__()
        self.image = pygame.image.load("project/icons/bullet.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 1 / 40)
        self.rect = self.image.get_rect()
        self.shooter = shooter
        self.direction = d
        self.speed = 10 * self.direction
        self.rect.center = (x, y)
 
    # delete bullet if it hits the screen edges
    def vanish(self):
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()
    
    # method applies when colliding with enemy
    def enemy_collision(self):
        if self.shooter == 'player':
            for enemy in enemies.sprites():
                if self.rect.colliderect(enemy.rect):
                    enemy.alert = True
                    if enemy.type == 'g1':
                        enemy.health -= 40
                    elif enemy.type == 'g3':
                        enemy.health -= 20
                    self.kill()

    # method applies when colliding with player
    def player_collision(self):
        if self.rect.colliderect(player.sprite.hitbox):
            player.sprite.health -= 2
            self.kill()
    
    def update(self):
        self.player_collision()
        self.enemy_collision()
        self.vanish()

        # bullet movement
        self.rect.x += 55 * self.direction
 
# grenade class
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 80
        self.vel_y = -10
        self.speed = 7
        self.direction = direction
        self.animation_index = 0
        self.exploding = False
        self.cooldown = 100
        self.explosion_effect = 1
        self.player_invincibility = False
        self.enemy_invincibility = False
        self.affect_player = False
        self.affect_enemy = False
        self.enemies_hit = []
        self.grenade_img = pygame.transform.scale_by(pygame.image.load("project/icons/grenade.png").convert_alpha(), 0.5)
        self.scale = 1
        self.explosion_imgs = []
        for i in range(0, 9):
            img = pygame.image.load(f"project/environment/explosion/e{i}.png").convert_alpha()
            self.explosion_imgs.append(pygame.transform.scale_by(img, 0.5))
        self.image = pygame.transform.scale_by(self.grenade_img, self.scale)
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)

    def damage_nearby(self):
        explosion_radius = 200
        player_distx = self.rect.centerx - player.sprite.rect.centerx
        player_disty = self.rect.centery - player.sprite.rect.centery

        # apply damage if player is in range
        if abs(player_distx) <= explosion_radius and abs(player_disty) <= explosion_radius and not self.player_invincibility:
                try:
                    player.sprite.health = int(player.sprite.health - 500/(int(abs(player_distx/4))))
                except(ZeroDivisionError):
                    player.sprite.health = 0
                self.affect_player = True
                self.player_invincibility = True

        # apply damage if enemy is in range
        for enemy in enemies.sprites():
            enemy_distx = self.rect.centerx - enemy.rect.centerx
            enemy_disty = self.rect.centery - enemy.rect.centery
            if abs(enemy_distx) <= explosion_radius and abs(enemy_disty) <= explosion_radius and not self.enemy_invincibility:
                try:
                    enemy.health = int(enemy.health - 1500/(int(abs(enemy_distx/5))))
                except(ZeroDivisionError):
                    enemy.health = 0
                self.enemies_hit.append(enemy)
                self.affect_enemy = True
                self.enemy_invincibility = True

    # applies when the timer goes off
    def explode(self):
        explosion_rect = pygame.Rect(self.rect.left - 90, self.rect.top - 90, self.rect.width, self.rect.height)
        self.damage_nearby()
        self.animation_index += 0.19

        # animate the explosion
        if self.animation_index >= len(self.explosion_imgs):
            self.animation_index = 0
            self.exploding = False
            self.kill()
        self.image.set_alpha(0)
        screen.blit(pygame.transform.scale_by(self.explosion_imgs[int(self.animation_index)], 1), explosion_rect)

    def update(self):
        # update motion
        self.vel_y += Gravity
        dx = self.direction * self.speed
        dy = self.vel_y
        self.explosion_effect -= 1

        if self.cooldown > 0:
            self.cooldown -= 1

        # to avoid applying continous damage to player
        if self.player_invincibility:
            if self.cooldown == 0:
                self.cooldown = 100
                self.player_invincibility = False

        # apply explosion physics
        if self.affect_player and self.player_invincibility and player.sprite.alive:
            if player.sprite.rect.centerx < self.rect.centerx:
                player.sprite.rect.x += self.explosion_effect
                player.sprite.hitbox.x += self.explosion_effect
            elif player.sprite.rect.centerx >= self.rect.centerx:
                player.sprite.rect.x -= self.explosion_effect
                player.sprite.hitbox.x -= self.explosion_effect
            self.player_invincibility = False
        if self.affect_enemy and self.enemy_invincibility:
            for enemy in self.enemies_hit:
                if enemy.rect.centerx < self.rect.centerx:
                    enemy.rect.x += self.explosion_effect
                elif enemy.rect.centerx >= self.rect.centerx:
                    enemy.rect.x -= self.explosion_effect
            self.enemy_invincibility = False

        # check collision with floor
        if self.rect.bottom + dy >= GROUND_LEVEL and self.rect.right <= ground_rect.right and self.rect.left > ground_rect.left:
            dy = GROUND_LEVEL - self.rect.bottom  # Snap to ground
            self.speed = 0
        
        # grenade explosion
        if self.exploding:
            self.explode()

        # apply projectile motion
        self.rect.x += dx
        self.rect.y += dy

        # explosion countdown timer
        self.timer -=1
        if self.timer <= 0:
            pygame.mixer.Channel(7).play(gexplosion, 0, 3500, 0)
            self.timer = 100
            self.exploding = True
       
# pickup class
class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.health_img = pygame.image.load("project/environment/pickups/health_pickup.png").convert_alpha()
        self.ammo_img = pygame.image.load("project/environment/pickups/ammo_pickup.png").convert_alpha()
        self.grenade_img = pygame.image.load("project/environment/pickups/grenade_pickup.png").convert_alpha()
        self.deletion_cd = 500
        self.stable = False
        self.pr = False
        if self.type == 'health':
            self.speed = randint(4, 8)
            self.image = self.health_img
            self.rect = self.image.get_rect(midbottom=(x,y))
        elif self.type == 'grenade':
            self.speed = randint(4, 8)
            self.image = self.grenade_img 
            self.rect = self.image.get_rect(midbottom=(x,y))
        elif self.type == 'ammo':
            self.speed = randint(4, 8)
            self.image = self.ammo_img
            self.rect = self.image.get_rect(midbottom=(x,y))

    def update(self):

        # checks if a parachute is bounded to this care-package
        if not self.pr:
            self.pr = True
            parachute.add(Parachute(self.rect.centerx, self.rect.top, self))
        self.deletion_cd -= 1

        # deletes the care-package after certain time
        if self.deletion_cd <= 0:
            self.kill()
        
        # checks if player picks up the care-package
        if self.rect.colliderect(player.sprite.hitbox):
            if self.type == 'health' and not player.sprite.health >= 100 and not player.sprite.dead:
                if player.sprite.health + 75 >= 100: # ignore if player is maximum health
                    player.sprite.health = 100
                else:
                    player.sprite.health += 75
                self.kill()
            elif self.type == 'ammo':
                global reloading
                player.sprite.max_ammo += 30
                self.kill()
                if player.sprite.max_ammo == 0 and player.sprite.ammo == 0:
                    player.sprite.state = 3
                    reloading = True
            elif self.type == 'grenade':
                player.sprite.grenades += 1
                self.kill()
        if self.rect.bottom < GROUND_LEVEL + 20:
            self.rect.y += self.speed
        else:
            self.stable = True   
            

# parachute pickup class
class Parachute(pygame.sprite.Sprite):
    def __init__(self, x, y, bound: Pickup):
        super().__init__()
        self.image = pygame.image.load("project/icons/parachute.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom = (x, y))
        self.bound = bound
        self.speed = self.bound.speed
    def update(self):
        self.rect.y += self.speed

        # checks if the care-package touches the ground
        if self.bound.stable or not self.bound.alive():
            self.kill() # delete the parachute

class Background(pygame.sprite.Sprite):
    def __init__(self, cur_bg: pygame.Surface, cur_rect: pygame.Rect, next_bg: pygame.Surface, next_rect: pygame.Rect):
        super().__init__()
        self.current_bg = cur_bg
        self.current_rect = cur_rect
        self.next_bg = next_bg
        self.next_rect = next_rect

    def load_bg(self):
        if self.current_bg.get_alpha() <= 0:
            screen.blit(self.next_bg, self.next_rect)
# groups
player = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
bullet = pygame.sprite.Group()
grenade = pygame.sprite.Group()
pickup = pygame.sprite.Group()
parachute = pygame.sprite.Group()

# HUD Display
class HUD():
    def __init__(self):
        self.cd = 200
    def draw(self):
        if game_state == LEVEL_ONE:
            # player health bar
            player_rect = pygame.Rect(20, 20, 400, 50)
            player_health_rect = pygame.Rect(20, 20, player.sprite.health * 4, 50)
            pygame.draw.rect(screen, 'black', pygame.Rect(10, 10, 420, 70), 0, 10, 10, 10, 10, 10)
            pygame.draw.rect(screen, 'red', player_rect)
            pygame.draw.rect(screen, 'green', player_health_rect)

            # kill count, level/wave number
            score = main_font.render(f"{kills}", True, "Yellow")
            score_rect = score.get_rect(center = (SCREEN_WIDTH - 35, 70))
            skull = pygame.transform.scale_by(pygame.image.load("project/icons/skull.png").convert_alpha(), 0.06)
            skull_rect = skull.get_rect(center = (SCREEN_WIDTH - 100, 70))
            word = 0
            valuex = 100
            c = "Yellow"
            if WAVE == 8:
                word = 'BONUS'
                valuex = 150
                c = "Green"
            elif WAVE >= 10:
                word = 'FINAL'
                c = "Red"
                valuex = 150
            else:
                c = "Yellow"
                valuex = 100
                word = WAVE
            wave = main_font.render(f"LEVEL: {word}", True, c).convert_alpha()
            wave_rect = wave.get_rect(center = (SCREEN_WIDTH - valuex, 150))
            screen.blit(skull, skull_rect)
            screen.blit(score, score_rect)
            screen.blit(wave, wave_rect)
            for enemy in enemies.sprites():

                # enemy health bars
                enemy_rect = pygame.Rect(enemy.rect.left - 10, enemy.rect.top - 20, 100, 10)
                enemy_health_rect = pygame.Rect(enemy.rect.left - 10, enemy.rect.top - 20, enemy.health, 10)
                pygame.draw.rect(screen, 'black', pygame.Rect(enemy_rect.left-5, enemy_rect.top-5, 110, 20))
                pygame.draw.rect(screen, 'red', enemy_rect)
                pygame.draw.rect(screen, 'green', enemy_health_rect)

            # ammo and grenades
            ammo_title = main_font.render(f"Ammo: {player.sprite.ammo}/{player.sprite.max_ammo}", True, "yellow").convert_alpha()
            ammo_title_rect = ammo_title.get_rect(topleft=(20, 90))
            grenade_img = pygame.transform.scale_by(pygame.image.load("project/icons/grenade.png").convert_alpha(), 0.8)
            screen.blit(ammo_title, ammo_title_rect)
            if player.sprite.grenades > 5:
                grenade_title = main_font.render(f"X{player.sprite.grenades}", True, "Yellow")
                grenade_rect = grenade_img.get_rect(topleft=(300, 85))
                grenade_title_rect = grenade_title.get_rect(topleft=(350, 90))
                screen.blit(grenade_img, grenade_rect)
                screen.blit(grenade_title, grenade_title_rect)
            else:
                for i in range(player.sprite.grenades):
                    grenade_rect = grenade_img.get_rect(topleft=(280+(i * 50), 85))
                    screen.blit(grenade_img, grenade_rect)

        # death screen
        elif game_state == DEATH_SCREEN:
            self.cd -= 1
            you_died = main_font.render("YOU DIED !", True, "Red")
            play_again = main_font.render("Press 'Enter' to play again ", True, "White")
            you_died = pygame.transform.smoothscale_by(you_died, 3)
            you_died_rect = you_died.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
            play_again_rect = you_died.get_rect(center=(SCREEN_WIDTH/2 + 40, SCREEN_HEIGHT/2 + 200))
            screen.blit(you_died, you_died_rect)
            if self.cd <= 0:
                screen.blit(play_again, play_again_rect)

hud = HUD()

# load entry music
if game_state == START_SCREEN:
    pygame.mixer_music.load("project/audio/music.wav")
    pygame.mixer_music.set_volume(0.8)
    pygame.mixer_music.play(100, 0, 2000)


# game loop
running = True
while running:

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # keyboard input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if game_state == START_SCREEN or game_state == DEATH_SCREEN:
                    TRANSITION = True
                    fade_alpha = 0
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_a:
                moving_left = True
            if not game_state == START_SCREEN and event.key == pygame.K_w and player.sprite.on_ground and not reloading:
                player.sprite.jump=True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_s: 
                crouch = True
            if not (game_state == START_SCREEN or game_state == DEATH_SCREEN) and event.key == pygame.K_r and player.sprite.ammo < player.sprite.magazine and player.sprite.max_ammo > 0 and not reloading:
                reloading = True
                player.sprite.s = True
                player.sprite.animation_index = 0

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_s:
                crouch = False

        # mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            left, middle, right = pygame.mouse.get_pressed()
            if game_state == START_SCREEN and start_surface.get_rect(topleft = (280, 600)).collidepoint(pygame.mouse.get_pos()) and not TRANSITION:
                TRANSITION = True
                fade_alpha = 0
            if left:
                shooting = True
            if right:
                throw_grenade = True
        if event.type == pygame.MOUSEBUTTONUP:
            shooting = False
            throw_grenade = False

    # screen transition
    if TRANSITION:
        start_music_volume -= 0.02
        if start_music_volume < 0:
            start_music_volume = 0
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            if game_state == DEATH_SCREEN:
                playing = False
                game_state = LEVEL_ONE
                not_loaded[0] = 1
            else:
                game_state += 1
            TRANSITION = False
            start_music_volume = 1
            pygame.mixer_music.play(100, 0, 5000)
    else:
        fade_alpha = 0

    # Draw everything
    pygame.mixer_music.set_volume(start_music_volume)
    if TRANSITION:
        fade_surface.set_alpha(fade_alpha / 10)
        screen.blit(fade_surface, (0, 0))
    elif game_state == START_SCREEN:
        screen.blit(main_surface, (0, 0))
        screen.blit(start_surface, (280, 600))
    elif game_state == LEVEL_ONE:
        if not final_playing and WAVE == 10:
                pygame.mixer_music.load("project/audio/final_wave.mp3")
                pygame.mixer_music.set_volume(1)    
                pygame.mixer_music.play(100, 0, 5000)
                final_playing = True
        if not playing and WAVE < 10:
                pygame.mixer_music.load("project/audio/level_music.mp3")
                pygame.mixer_music.set_volume(1)    
                pygame.mixer_music.play(100, 0, 5000)
                playing = True
        if not_loaded[0]:

            # load player once
            player.add(Soldier("project/player/idle/tile000.png", 550, 610, 0.8, 5, 'player', 1)) 
            not_loaded[0] = 0

        # load backgrounds in parallel
        if lvl3:
            screen.blit(final_bg, final_rect)
        if lvl2:
            screen.blit(level_three_bg, level_three)
        if lvl1:
            screen.blit(level_two_bg, level_two)
        if lvl0:
            screen.blit(level_one_bg, (0, 0))
        screen.blit(ground_img, ground_rect)

        # if wave is cleared, move to next wave
        if len(enemies.sprites()) <=0:
            cd -= 1
            if WAVE > 0 and WAVE < 10:
                if WAVE == 8:
                    screen.blit(bonustxt, bonustxt_rect)
                else:
                    screen.blit(wave_completetxt, wave_completetxt_rect)
            if WAVE == 9:
                screen.blit(finaltxt, finaltxt_rect)

        # backgrounds motion
        if WAVE > 1 and WAVE < 5:
            level_two.x += dr   
            if level_two.left >= 0:
                dr = -1
            elif level_two.right <= SCREEN_WIDTH:
                dr = 1
        if WAVE >= 5 and WAVE < 10:
            level_three.x += dr   
            if level_three.left >= 0:
                dr = -1
            elif level_three.right <= SCREEN_WIDTH:
                dr = 1
        elif WAVE >= 10:
            final_rect.x += dr * 5
            if final_rect.left >= 0:
                dr = -1
            elif final_rect.right <= SCREEN_WIDTH:
                dr = 1

        # draw sprites 
        bullet.draw(screen)
        grenade.draw(screen)
        pickup.draw(screen)
        parachute.draw(screen)

        # update sprites
        pickup.update()
        parachute.update()
        player.update()
        enemies.update()
        grenade.update()
        bullet.update()

        # --------------------------------------- game waves ------------------------------------------------------
        if WAVE == 0:
            pygame.mouse.set_visible(0)
            if level_one_bg.get_alpha() == None or level_one_bg.get_alpha() < 255:
                level_one_bg.set_alpha(255)
            if level_two_bg.get_alpha() == None or level_two_bg.get_alpha() < 255:
                level_two_bg.set_alpha(255)
            if level_three_bg.get_alpha() == None or level_three_bg.get_alpha() < 255:
                level_three_bg.set_alpha(255)
            if final_bg.get_alpha() == None or final_bg.get_alpha() < 255:
                final_bg.set_alpha(255)
            screen.blit(text, text_rect)
            if cd <= 0:
                cd = 100

                # spawn enemies randomly
                if len(enemies.sprites()) == 0:
                    for i in range(3):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))

                    # spawn care-packages
                    pickup.add(Pickup(400, GROUND_LEVEL - 800, 'health'))
                    pickup.add(Pickup(600, GROUND_LEVEL - 800, 'ammo'))
                    WAVE += 1
        elif WAVE == 1:
            if cd <= 0:
                cd=300
                if len(enemies.sprites()) == 0:
                    for i in range(4):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    pickup.add(Pickup(400, GROUND_LEVEL - 1300, 'health'))
                    WAVE += 1
        elif WAVE == 2:
            lvl1 = True
            if level_one_bg.get_alpha() == None:
                level_one_bg.set_alpha(255)
            elif level_one_bg.get_alpha() > 0:
                level_one_bg.set_alpha(level_one_bg.get_alpha() - 2)
            elif level_one_bg.get_alpha() <= 0:
                lvl0 = False
            
            if cd <= 0:
                cd = 100

                # spawn enemies randomly
                if len(enemies.sprites()) == 0:
                    for i in range(5):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    
                    # spawn care-packages randomly
                    for i in range(2):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i == 0:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                    WAVE += 1
        elif WAVE == 3:
            if cd <= 0:
                cd = 100
                if len(enemies.sprites()) == 0:
                    for i in range(6):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 3:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(3):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 1:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                    WAVE += 1
        elif WAVE == 4:
            if cd <= 0:
                cd = 100
                if len(enemies.sprites()) == 0:
                    for i in range(7):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 4:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(3):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 1:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                    WAVE += 1
        elif WAVE == 5: # transition wave
            lvl2 = True
            if level_two_bg.get_alpha() == None:
                level_two_bg.set_alpha(255)
            elif level_two_bg.get_alpha() > 0:
                level_two_bg.set_alpha(level_two_bg.get_alpha() - 2)
                loaded = False
            elif level_two_bg.get_alpha() <= 0:
                lvl1 = False
            
            if cd <= 0:
                cd = 100
                if len(enemies.sprites()) == 0:
                    for i in range(8):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 5:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(5):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 1:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                    WAVE += 1
        elif WAVE == 6:
            if cd <= 0:
                cd = 100
                if len(enemies.sprites()) == 0:
                    for i in range(9):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 2:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(5):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 1:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                    WAVE += 1
        elif WAVE == 7:
            if cd <= 0:
                cd = 500
                for i in range(6):
                    posx = randint(300, 900)
                    type = randint(0, 2)
                    if i < 1:
                        type = 0
                    elif i < 4:
                        type = 2
                    if type == 0:
                        pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                    elif type == 1:
                        pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                    elif type == 2:
                        pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                WAVE += 1
        elif WAVE == 8: # bonus wave
            if cd <= 0:
                cd = 100
                if len(enemies.sprites()) == 0:
                    for i in range(randint(9, 10)):
                            type_int = randint(1, 3)
                            if type_int == 2:
                                type_int = 3
                            posx = randint(300, 900)
                            dir = randint(-1, 1)
                            if dir == 0:
                                dir = 1
                            if i < 2:
                                type_int = 1
                            enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(4):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 1:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                    WAVE += 1
        elif WAVE == 9:
            if cd <= 0:
                cd = 1
                if len(enemies.sprites()) == 0:
                    for i in range(randint(10, 11)):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 2:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(randint(3, 5)):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 2:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                WAVE += 1
        elif WAVE == 10: # final wave
            lvl3 = True
            if level_three_bg.get_alpha() == None:
                level_three_bg.set_alpha(255)
            elif level_three_bg.get_alpha() > 0:
                level_three_bg.set_alpha(level_three_bg.get_alpha() - 2)
            elif level_three_bg.get_alpha() <= 0:
                lvl2 = False

            if cd <= 0:
                cd = 1
                if len(enemies.sprites()) == 0:
                    for i in range(randint(11, 12)):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 2:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(randint(4, 6)):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 2:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                WAVE += 1
        elif WAVE == 11:
            if cd <= 0:
                cd = 300
                if len(enemies.sprites()) == 0:
                    for i in range(randint(11, 14)):
                        type_int = randint(1, 3)
                        if type_int == 2:
                            type_int = 3
                        posx = randint(300, 900)
                        dir = randint(-1, 1)
                        if dir == 0:
                            dir = 1
                        if i < 2:
                            type_int = 1
                        enemies.add(Soldier("project/enemy/gangsters/g3/idle/i0.png", posx, 600, 0.8, 1, f'g{type_int}', dir))
                    for i in range(randint(5, 7)):
                        posx = randint(300, 900)
                        type = randint(0, 2)
                        if i < 2:
                            type = 0
                        if type == 0:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'health'))
                        elif type == 1:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'ammo'))
                        elif type == 2:
                            pickup.add(Pickup(posx, GROUND_LEVEL - 1300, 'grenade'))
                WAVE += 1
        elif WAVE == 12: # THANKS FOR PLAYING !
            pygame.mouse.set_visible(1)
            if len(enemies.sprites()) <= 0:
                if DY + SCREEN_HEIGHT + 500 > SCREEN_HEIGHT / 2 + 200:
                    DY -= 10
                total_kills = main_font.render(f"Total kills: {kills}", True, "Yellow")
                total_kills_rect = total_kills.get_rect(center=(SCREEN_WIDTH/2 - 20, DY + SCREEN_HEIGHT + 500))
                screen.blit(thx, (0, 0))
                screen.blit(total_kills, total_kills_rect)
                for enemy in enemies.sprites():
                    enemy.kill()
                for pick in pickup.sprites():
                    pick.kill()
                ENDGAME = True


        if not ENDGAME:
            hud.draw()

    # clear entities after dying
    elif game_state == 2:
        lvl0 = True
        lvl1, lvl2, lvl3 = False, False, False
        pygame.mouse.set_visible(1)
        for enemy in enemies.sprites():
            enemy.kill()
        for pick in pickup.sprites():
            pick.kill()
        WAVE = 0
        cd = 100
        screen.blit(death_surface, (0, 0))
        hud.draw()
    pygame.display.update()
    clock.tick(60) # 60 fps

# quit game
pygame.quit()
sys.exit()