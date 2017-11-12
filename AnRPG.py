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
projectiles_path        = assets_base_path + '/projectiles'
projectile             = projectiles_path + '/blue_projectile.png'
font_base              = pygame.font.Font(fonts_path + 'Futura.ttf', 20)
home                   = assets_base_path + '/home_area_beige.jpg'
player_sprite          = assets_base_path + '/player_sprite.png'
player_sprite_reversed = assets_base_path + '/player_sprite_reversed.png'
sprite_mine            = projectiles_path + '/mine.png'
player_sprite_image    = pygame.image.load(player_sprite)
projectile_image       = pygame.image.load(projectile)
home_image             = pygame.image.load(home)
mine_image             = pygame.image.load(sprite_mine)
image_size             = player_sprite_image.get_rect().size
print(image_size)
window_title           = 'RPG Game'
# clock                  = pygame.time.Clock()

class Projectile(pygame.sprite.Sprite):
    """Projectile class"""

    damage = config.projectile_damage
    lifespan = config.projectile_lifespan
    img_rect = projectile_image.get_rect()

    def __init__(self, origin, target, tick):
        pygame.sprite.Sprite.__init__(self)
        self.pos = origin
        self.target = target
        self.angle = functions.get_angle(self.pos, self.target)
        self.speed = config.projectile_speed
        self.tickmade = tick
        self.img_rect = pygame.Rect((self.pos[0], self.pos[1]), (32, 32))

    def update(self):
        self.angle = functions.get_angle(self.pos, self.target)
        self.pos = functions.project(self.pos, self.angle, self.speed)
        self.img_rect.center = self.pos

    def blit(self):
        game_display.blit(projectile_image, (self.pos[0], self.pos[1]))

    def collided_with(self, sprite_rect):
        return self.img_rect.colliderect(sprite_rect)

    def kill(self):
        del active_projectiles[active_projectiles.index(self)]


class Player(pygame.sprite.Sprite):
    """The player class"""

    health = config.player_health
    x = config.player_starting_y
    y = config.player_starting_y

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.player_name = None
        self.img_verts = None
        self.facing = None
        self.img_size = player_sprite_image.get_rect().size
        self.img_rect = pygame.Rect((self.x, self.y),
                                    (self.img_size[0], self.img_size[1]))

    def refresh_rect(self):
        self.img_rect = pygame.Rect((self.x, self.y),
                                    (self.img_size[0], self.img_size[1]))

    def blit_facing(self):
        if self.facing == 'right':
            game_display.blit(pygame.image.load(player_sprite), (self.x, self.y))
        elif self.facing == 'left':
            game_display.blit(pygame.image.load(player_sprite_reversed), (self.x, self.y))

    def kill(self):
        death_screen()


class Mine(pygame.sprite.Sprite):

    health = config.mine_health
    damage = config.mine_damage

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(sprite_mine)
        self.img_rect = pygame.Rect((self.x, self.y), (32, 32))

    def render(self):
        game_display.blit(self.image, (self.x, self.y))

    def collided_with(self):
        return self.img_rect.colliderect(player.img_rect)

    def kill(self):
        del active_mines[active_mines.index(self)]


pygame.display.set_caption(window_title)
game_display = pygame.display.set_mode((config.window_width, config.window_height),
                                       pygame.HWSURFACE)
active_keys        = {'w': None, 'a': None, 's': None, 'd': None}
active_projectiles = []
active_mines       = []

ticks = 0
player = Player()
player.img_rect = pygame.image.load(player_sprite).get_rect()
player.player_name = inputbox.ask(game_display, "Enter Player Name", font_base)

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
    background = assets_base_path + 'title_screen.jpg'
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
                                     ticks)
            active_projectiles.append(projectile)


        # Player Facing
        if event.type == pygame.MOUSEMOTION:
            if event.pos[0] > player.x: player.facing = 'right'
            else: player.facing = 'left'


    ## MOVEMENT, COLLISION, AND FPS
    if active_keys['w']: player.y -= config.player_movespeed_vertical
    if active_keys['s']: player.y += config.player_movespeed_vertical
    if active_keys['a']: player.x -= config.player_movespeed_horizontal
    if active_keys['d']: player.x += config.player_movespeed_horizontal
    player.refresh_rect()
    for projectile in active_projectiles:
        projectile.update()
        if (ticks - projectile.tickmade) > config.projectile_lifespan:
            projectile.kill()


    if len(active_mines) != 0:
        for mine in active_mines:
            if mine.collided_with():
                print('collision')
                player.health = player.health - mine.damage
                mine.kill()

    end_t = time()
    time_taken = end_t - start_t
    start_t = end_t
    frame_times.append(time_taken)
    frame_times = frame_times[-20:]
    fps = len(frame_times) / sum(frame_times)

    ## Rendering
    fps_text        = font_base.render('FPS - ' + str(int(fps)), True, Color.Black)
    name_text       = font_base.render(player.player_name, True, Color.Black)
    player_health   = font_base.render(str(player.health), True, Color.Black)
    game_display.blit(pygame.image.load(home), (0,0))
    game_display.blit(fps_text, (1130, 780))
    game_display.blit(player_health, (0, 0))
    game_display.blit(name_text, (player.img_verts['tm'][0], player.img_verts['tm'][1] - 25))

    player.blit_facing()

    if len(active_projectiles) != 0:
        for projectile in active_projectiles:
            projectile.blit()

    if len(active_mines) != 0:
        for mine in active_mines:
            mine.render()


    # OPTIONAL, TO ENABLE, SEE CONFIG FILE SETTINGS
    # To monitor player verts
    if config.render_player_verts:
        for _, coords in player.img_verts.items():
            pygame.draw.circle(game_display, Color.Goldenrod, coords, 10)


    pygame.display.update()

    tick_end_time = datetime.now()
    tick_time = tick_end_time - tick_start_time
    # print(str(tick_time) + ' fps - ' + str(fps))
    with open('tick_times.txt', 'a') as f:
        f.write(str(tick_time)[6:] + 'fps - %s' + '\n') %fps


pygame.quit()
quit()