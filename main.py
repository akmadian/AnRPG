# -*- coding: utf-8 -*-
"""
    File Name: main.py
    Author: Ari Madian
    Created: July 23, 2017 2:02 PM
    Python Version: 3.6
"""

import pygame
import sys
import os
import time

# Game Resources
import classes
import functions
import inputbox
from colors_file import Color


#TODO: Blit a portion of an image so all related sprites can be in one image
#TODO: Projectiles with asyncio
#TODO: Config file implementation?
#TODO: Change projectile sprite to a circle to avoid dealing with the rotation stuff

x = pygame.init()

base_path = os.path.os.path.dirname(os.path.realpath(sys.argv[0]))
assets_base_path = base_path + '/Assets/'
fonts_path = base_path + '/Fonts/'
projectile_path = assets_base_path + '/projectiles'
projectile_color_path = assets_base_path + '/Projectiles/BAR'

fps_font = pygame.font.Font(fonts_path + 'Futura.ttf', 20)
home = assets_base_path + '/home_area_beige.jpg'
player_sprite = assets_base_path + '/player_sprite.png'
player_sprite_reversed = assets_base_path + '/player_sprite_reversed.png'
image = pygame.image.load(player_sprite)
image_size = image.get_rect().size


window_width = 1200
window_height = 800
window_title = 'RPG Game'
pygame.display.set_caption(window_title)
game_display = pygame.display.set_mode((window_width, window_height),
                                       pygame.HWSURFACE)
keys_down = {'w': None, 'a': None, 's': None, 'd': None}
active_projectiles = []
player_facing = None
ticks = 0
player = classes.Player
player.pos_x = 100
player.pos_y = 100
player.player_name = inputbox.ask(game_display, "Enter Player Name", fps_font)


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
        time.sleep(0.013)



title_screen()
gameExit = False
while not gameExit:
    ticks += 1
    player.img_verts = functions.player_verts((player.pos_x, player.pos_y), image_size)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True

        ## Character Movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: keys_down['w'] = True
            elif event.key == pygame.K_a: keys_down['a'] = True
            elif event.key == pygame.K_s: keys_down['s'] = True
            elif event.key == pygame.K_d: keys_down['d'] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w: keys_down['w'] = False
            elif event.key == pygame.K_a: keys_down['a'] = False
            elif event.key == pygame.K_s: keys_down['s'] = False
            elif event.key == pygame.K_d: keys_down['d'] = False

        ## Projectiles and Targeting
        # Making the projectile
        if event.type == pygame.MOUSEBUTTONDOWN:
            # print(dict(zip(('x', 'y'), (player.pos_x, player.pos_y))))
            # print(dict(zip(('x', 'y'), event.pos)))
            projectile = classes.Projectile(dict(zip(('x', 'y'), (player.img_verts['cm'][0],
                                                                  player.img_verts['cm'][1]))),
                                            dict(zip(('x', 'y'), event.pos)),
                                            ticks)
            projectile.imagename = '/blue_projectile.png'
            projectile.angle = functions.projectile_angle((player.img_verts['cm'][0],
                                                           player.img_verts['cm'][1]),
                                                           event.pos)
            active_projectiles.append(projectile)

            '''
            print('Angle: ' + str(projectile.angle))
            print('Origin: ' + str((player.pos_x, player.pos_y)))
            print('End: ' + str(event.pos))
            '''


        # Player Facing
        if event.type == pygame.MOUSEMOTION:
            if event.pos[0] > player.pos_x: player_facing = 'right'
            else: player_facing = 'left'

    ## Executing Movement
    if keys_down['w']: player.pos_y -= 5
    if keys_down['s']: player.pos_y += 5
    if keys_down['a']: player.pos_x -= 5
    if keys_down['d']: player.pos_x += 5


    for projectile in active_projectiles:
        if (ticks - projectile.tickmade) > 150:
            del active_projectiles[active_projectiles.index(projectile)]
        projectile.pos = functions.projectile_position(projectile, ticks)

    print(len(active_projectiles))

    ## Rendering
    ticks_text = fps_font.render(('Ticks: ' + str(ticks)), True, Color.Black)
    name_text = fps_font.render(player.player_name, True, Color.Black)
    player_pos = fps_font.render((str(player.pos_x) + ', ' + str(player.pos_y)), True, Color.Black)
    game_display.blit(pygame.image.load(home), (0,0))
    game_display.blit(ticks_text, (0, 25))
    game_display.blit(player_pos, (0, 0))
    game_display.blit(name_text, (player.img_verts['tm'][0], player.img_verts['tm'][1] - 25))

    ''' # To monitor player verts
    for _, coords in player.img_verts.items():
        pygame.draw.circle(game_display, Color.Goldenrod, coords, 10)
    '''

    if player_facing == 'right':
        game_display.blit(pygame.image.load(player_sprite), (player.pos_x, player.pos_y))
    elif player_facing == 'left':
        game_display.blit(pygame.image.load(player_sprite_reversed), (player.pos_x, player.pos_y))

    if len(active_projectiles) != 0:
        for projectile in active_projectiles:
            game_display.blit(pygame.image.load(projectile_color_path + projectile.imagename),
                              (projectile.pos[0], projectile.pos[1]))

    pygame.display.update()
    # time.sleep(0.01)


pygame.quit()
quit()