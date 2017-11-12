# -*- coding: utf-8 -*-
"""
    File Name: main.py
    Author: Ari Madian
    Created: July 23, 2017 2:02 PM
    Python Version: 3.6
"""

import pygame
from os import path
from time import sleep, time
from sys import argv
from datetime import datetime
from random import randint, choice

# Proprietary Resources
import functions
import inputbox
import config
from colors_file import Color


#TODO: Blit a portion of an image so all related sprites can be in one image

pygame_init = pygame.init()

base_path              = path.os.path.dirname(path.realpath(argv[0]))
assets_base_path       = base_path + '/Assets/'
fonts_path             = base_path + '/Fonts/'
projectiles_path       = assets_base_path + '/projectiles'
projectile             = projectiles_path + '/blue_projectile.png'
font_base              = pygame.font.Font(fonts_path + 'Futura.ttf', 20)
home                   = assets_base_path + '/home_area_beige.jpg'
player_sprite          = assets_base_path + 'player_sprite.tiff'
player_sprite_reversed = assets_base_path + 'player_sprite_reversed.tiff'
enemy_sprite           = assets_base_path + '/enemy_sprite.png'
enemy_sprite_reversed  = assets_base_path + '/enemy_sprite_reversed.png'
sprite_bad_thing       = projectiles_path + '/mine.png'
health_pack            = assets_base_path + '/healthpack.gif'
player_sprite_image    = pygame.image.load(player_sprite)
projectile_image       = pygame.image.load(projectile)
home_image             = pygame.image.load(home)
bad_thing_image        = pygame.image.load(sprite_bad_thing)
enemy_sprite_image     = pygame.image.load(enemy_sprite)
health_pack_image      = pygame.image.load(health_pack)
image_size             = player_sprite_image.get_rect().size
print(image_size)
window_title           = 'RPG Game'

class Projectile(pygame.sprite.Sprite):
    """Projectile class

    :param origin: The starting position for the projectile,
                    the player or enemy's position
    :param target: Where the player or enemy intends for the
                    projectile to go, at mouseclick pos or
                    player position.
    :param tick: The tick the projectile was created at
    :param type_: The projectile type, either 'friendly' or 'enemy'"""

    damage = config.player_damage
    lifespan = config.projectile_lifespan
    rect = projectile_image.get_rect()

    def __init__(self, origin, target, tick, type_):
        pygame.sprite.Sprite.__init__(self)
        self.pos = origin
        self.type = type_
        self.target = target
        self.angle = functions.get_angle(self.pos, self.target)
        self.speed = config.projectile_speed
        self.tickmade = tick
        self.rect = pygame.Rect((self.pos[0], self.pos[1]), (32, 32))

    def update(self):
        self.angle = functions.get_angle(self.pos, self.target)
        self.pos = functions.project(self.pos, self.angle, self.speed)
        self.rect.center = self.pos

    def blit(self):
        if self.type == 'friendly':
            game_display.blit(projectile_image, (self.pos[0], self.pos[1]))
        elif self.type == 'enemy':
            game_display.blit(bad_thing_image, (self.pos[0], self.pos[1]))

    def collided_with(self, sprite_rect):
        return self.rect.colliderect(sprite_rect)

    def kill(self):
        del active_projectiles[active_projectiles.index(self)]


class Player(pygame.sprite.Sprite):
    """The player class"""

    health = config.player_health
    x = config.player_starting_y
    y = config.player_starting_y

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.player_name = ''
        self.img_verts = None
        self.facing = None
        self.type = 'friendly'
        self.img_size = player_sprite_image.get_rect().size
        self.rect = pygame.Rect((self.x, self.y + 92),
                                (self.img_size[0], self.img_size[1] - 92))

    def refresh_rect(self):
        self.rect = pygame.Rect((self.x, self.y + 92),
                                (self.img_size[0], self.img_size[1] - 92))

    def blit_facing(self):
        if self.facing == 'right':
            game_display.blit(pygame.image.load(player_sprite), (self.x, self.y))
        elif self.facing == 'left':
            game_display.blit(pygame.image.load(player_sprite_reversed), (self.x, self.y))

    def kill(self):
        death_screen()


class Mine(pygame.sprite.Sprite):
    """The mine class

    :param x: The x position for the mine to be created at
    :param y: The y position for the mine to be created at"""

    health = config.mine_health
    damage = config.mine_damage

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(sprite_bad_thing)
        self.rect = pygame.Rect((self.x, self.y), (32, 32))

    def blit(self):
        game_display.blit(self.image, (self.x, self.y))

    def collided_with(self):
        return self.rect.colliderect(player.rect)

    def kill(self):
        del active_mines[active_mines.index(self)]


class SmallEnemy(pygame.sprite.Sprite):
    """The small enemy class

    :param x: The x position for the enemy to be created at
    :param y: The y position for the enemy to be created at
    :param tick: The tick the enemy was created at"""

    health = config.small_enemy_health
    damage = config.small_enemy_damage
    step = 0

    def __init__(self, x, y, tick):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.type = 'enemy'
        self. name = 'Small Enemy'
        self.facing = None
        self.img_size = None
        self.rect = pygame.Rect((self.x, self.y),
                                (200, 119))
        self.last_attack = tick

    def attack(self):
        projectile_ = Projectile((self.x, self.y),
                                 (player.img_verts['cm'][0], player.img_verts['cm'][1]),
                                 ticks, 'enemy')
        active_projectiles.append(projectile_)

    def blit_facing(self):
        if self.facing == 'right':
            game_display.blit(pygame.image.load(enemy_sprite), (self.x, self.y))
        elif self.facing == 'left':
            game_display.blit(pygame.image.load(enemy_sprite_reversed), (self.x, self.y))


    def blit_health(self):
        game_display.blit(font_base.render('Health - ' + str(self.health), True, Color.Black),
                          (self.x + 10, self.y - 30))


    def move(self):
        if self.step >= config.enemy_small_tickstomove:
            add_or_sub = ('+', '-')
            if choice(add_or_sub) == '+':
                self.x += randint(config.enemy_small_movex_min, config.enemy_small_movex_max)
            else:
                self.x -= randint(config.enemy_small_movex_min, config.enemy_small_movex_max)

            if choice(add_or_sub) == '+':
                self.y += randint(config.enemy_small_movey_min, config.enemy_small_movey_max)
            else:
                self.y -= randint(config.enemy_small_movey_min, config.enemy_small_movey_max)
            self.step = 0
            self.update_rect()
        self.step += 1

    def update_rect(self):
        self.rect = pygame.Rect((self.x, self.y),
                                (200, 119))

    def kill(self):
        del active_enemies[active_enemies.index(self)]


class HealthPack(pygame.sprite.Sprite):
    """The class for the health pack

    :param x: The x position for the pack to be created at
    :param y: The y position for the pack to be created at"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rect = pygame.Rect((self.x, self.y), (46, 31))

    def collided_with(self, sprite_rect):
        return self.rect.colliderect(sprite_rect)

    def blit(self):
        game_display.blit(health_pack_image, (self.x, self.y))

    def heal(self):
        player.health += config.healthpack_heal_amount
        self.kill()

    def kill(self):
        del active_health_packs[active_health_packs.index(self)]


pygame.display.set_caption(window_title)
game_display = pygame.display.set_mode((config.window_width, config.window_height),
                                       pygame.HWSURFACE)
active_keys          = {'w': None, 'a': None, 's': None, 'd': None}
active_projectiles   = []
active_mines         = []
active_enemies       = []
active_health_packs  = []


ticks = 0
enemy = SmallEnemy(900, 600, ticks)
active_enemies.append(enemy)

pack = HealthPack(500, 400)
active_health_packs.append(pack)

player = Player()
player.rect = pygame.image.load(player_sprite).get_rect()
# player.player_name = inputbox.ask(game_display, "Enter Player Name", font_base)

frame_times = []
start_t = time()


def death_screen():
    alpha = 100
    game_exit = False
    print('death screen started')
    background = assets_base_path + 'gameoverbackground.jpg'
    while not game_exit:
        game_display.blit(pygame.image.load(background), (0, 0))

    '''
    quit_game = False
    background       = assets_base_path + 'gameoverbackground.jpg'
    background_image = pygame.image.load(background).convert()

    while True:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                quit()


        game_over_text = font_base.render('You Died', True, Color.White)
        game_over_text.set_alpha(alpha)

        game_display.blit(background_image, (0, 0))
        game_display.blit(game_over_text, (500, 111))

        alpha += 3
    '''


def title_screen():
    background = assets_base_path + 'title_screen.png'
    font_size = 0
    frames = 0
    enter_game = False
    while not enter_game:
        for event_ in pygame.event.get():
            if event_.type == pygame.QUIT:
                quit()
            elif event_.type == pygame.KEYDOWN:
                if event_.key == pygame.K_KP_ENTER or pygame.K_SPACE:
                    enter_game = True
            # print(event_)

        game_display.blit(pygame.image.load(background), (0, 0))
        font = pygame.font.Font(fonts_path + 'Futura.ttf', font_size)
        game_display.blit(font.render(str('An RPG'), True, Color.Black), (500, 111))
        # game_display.blit(font.render(str(frames), True, Color.Goldenrod), (0, 0))

        if font_size < 65: font_size += 1
        if font_size == 65:
            game_display.blit(font.render(str('Press Enter To Play'), True, Color.Black), (345, 400))

        pygame.display.update()
        frames += 1
        sleep(0.013)


title_screen()
gameExit = False
while not gameExit:
    tick_start_time = datetime.now()
    ticks += 1
    player.img_verts = functions.player_verts((player.x, player.y), image_size)

    ## ON EVENT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True

        if player.health <= 0 and config.player_godmode is False:
            player.kill()

        ## Character Movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: active_keys['w'] = True
            elif event.key == pygame.K_a: active_keys['a'] = True
            elif event.key == pygame.K_s: active_keys['s'] = True
            elif event.key == pygame.K_d: active_keys['d'] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w: active_keys['w'] = False
            elif event.key == pygame.K_a: active_keys['a'] = False
            elif event.key == pygame.K_s: active_keys['s'] = False
            elif event.key == pygame.K_d: active_keys['d'] = False

        ## Projectiles and Targeting
        # Making the projectile
        if event.type == pygame.MOUSEBUTTONDOWN:
            print((player.img_verts['cm'][0], player.img_verts['cm'][1]))
            print(event.pos)
            projectile = Projectile((player.img_verts['cm'][0],
                                     player.img_verts['cm'][1]),
                                     event.pos,
                                     ticks, 'friendly')
            active_projectiles.append(projectile)

        # Player Facing
        if event.type == pygame.MOUSEMOTION:
            if event.pos[0] > player.x: player.facing = 'right'
            else: player.facing = 'left'

    ## ENEMY ACTIONS
    for enemy in active_enemies:
        if ticks - enemy.last_attack >= config.small_enemy_attack_freq:
            enemy.attack()
            enemy.last_attack = ticks

        if enemy.health <= 0:
            enemy.kill()

        if player.x > enemy.x:
            enemy.facing = 'right'
        elif player.x < enemy.x:
            enemy.facing = 'left'

        enemy.move()

    ## MOVEMENT, COLLISION, AND FPS
    if active_keys['w']: player.y -= config.player_movespeed_vertical
    if active_keys['s']: player.y += config.player_movespeed_vertical
    if active_keys['a']: player.x -= config.player_movespeed_horizontal
    if active_keys['d']: player.x += config.player_movespeed_horizontal
    player.refresh_rect()

    # PROJECTILE COLLISION SCANNING
    # PROJECTILES
    for projectile in active_projectiles:
        projectile.update()
        if (ticks - projectile.tickmade) > config.projectile_lifespan or \
                        projectile.pos == projectile.target:
            projectile.kill()

        if projectile.collided_with(player.rect):
            if projectile.type == 'enemy':
                player.health = player.health - config.small_enemy_damage
                projectile.kill()

        if projectile.type != 'enemy':
            collisionslist = pygame.sprite.spritecollide(projectile, active_enemies, False)
            if len(collisionslist) != 0: print(collisionslist)
            if len(collisionslist) != 0:
                for enemy in collisionslist:
                    enemy.health = enemy.health - config.player_damage
                projectile.kill()

    # MINES
    if len(active_mines) != 0:
        for mine in active_mines:
            if mine.collided_with():
                player.health = player.health - mine.damage
                mine.kill()

    # HEALTHPACKS
    if len(active_health_packs) != 0:
        for pack in active_health_packs:
            if pack.collided_with(player.rect):
                pack.heal()

    end_t = time()
    time_taken = end_t - start_t
    start_t = end_t
    frame_times.append(time_taken)
    frame_times = frame_times[-20:]
    fps = len(frame_times) / sum(frame_times)

    ## Rendering
    fps_text        = font_base.render('FPS - ' + str(int(fps)), True, Color.Black)
    name_text       = font_base.render(player.player_name, True, Color.Black)
    player_health   = font_base.render('Health - ' + str(player.health), True, Color.Black)
    game_display.blit(pygame.image.load(home), (0,0))
    game_display.blit(fps_text, (1130, 780))
    game_display.blit(player_health, (0, 0))
    game_display.blit(name_text, (player.img_verts['tm'][0] - 10, player.img_verts['tm'][1] - 25))

    player.blit_facing()

    if len(active_projectiles) != 0:
        for projectile in active_projectiles:
            projectile.blit()

    if len(active_mines) != 0:
        for mine in active_mines:
            mine.blit()

    if len(active_enemies) != 0:
        for enemy in active_enemies:
            enemy.blit_facing()
            enemy.blit_health()

    if len(active_health_packs) != 0:
        for pack in active_health_packs:
            pack.blit()

    # OPTIONAL, TO ENABLE, SEE CONFIG FILE SETTINGS
    # To monitor player verts
    if config.render_player_verts:
        for _, coords in player.img_verts.items():
            pygame.draw.circle(game_display, Color.Goldenrod, coords, 10)


    pygame.display.update()

    ''' For monitoring tick times and fps for performance eval
    tick_end_time = datetime.now()
    tick_time = tick_end_time - tick_start_time
    # print(str(tick_time) + ' fps - ' + str(fps))
    with open('tick_times.txt', 'a') as f:
        f.write(str(tick_time)[6:] + 'fps - %s' + '\n') %fps
    '''

pygame.quit()
quit()