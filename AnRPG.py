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
from copy import copy
import configparser

# Proprietary Resources
import functions
import inputbox
import config
from colors_file import Color


#TODO: Blit a portion of an image so all related sprites can be in one image
#TODO: Source sprite spawn area ranges to config file
#TODO: Fix caching
#TODO: Fix controls thing when active collision with obstacle
#TODO: ??? Implement Dataclasses ???
#TODO: Projectiles dont get created if the event is far enough to the right
#TODO: Active damage up system gets messed up after first enemy kill
pygame_init = pygame.init()

# ASSET OBJECTS AND PATHS
base_path              = path.os.path.dirname(path.realpath(argv[0]))
assets_base_path       = base_path + '/Assets/'
fonts_path             = base_path + '/Fonts/'
projectiles_path       = assets_base_path + '/projectiles'
projectile             = projectiles_path + '/blue_projectile.png'
font_base              = pygame.font.Font(fonts_path + 'Futura.ttf', 20)
home                   = assets_base_path + '/home_area_beige.jpg'
player_sprite          = assets_base_path + 'player_sprite.tiff'
player_sprite_reversed = assets_base_path + 'player_sprite_reversed.tiff'
sprite_bad_thing       = projectiles_path + '/mine.png'
health_pack            = assets_base_path + '/healthpack.gif'
dmgup                  = assets_base_path + '/damage_up.png'
player_sprite_image    = pygame.image.load(player_sprite)
projectile_image       = pygame.image.load(projectile)
home_image             = pygame.image.load(home)
bad_thing_image        = pygame.image.load(sprite_bad_thing)
health_pack_image      = pygame.image.load(health_pack)
dmgup_image            = pygame.image.load(dmgup)
player_image_size      = player_sprite_image.get_rect().size
window_title           = 'RPG Game'

## TRACKERS
# COUNTERS
enemies_killed         = 0
last_enemy_boss_death  = 0
last_enemy_small_death = 0
last_healthpack_used   = 0
last_attackboost_used  = 0
last_shield_used       = 0
active_healthpacks     = 0
active_dmgup           = 0
active_shield          = 0
ticks                  = 0
# ACTIVE LISTS
active_keys            = {'w': None, 'a': None, 's': None, 'd': None}
active_projectiles     = []
active_mines           = []
active_enemies_small   = []
active_enemies_boss    = []
active_powerups        = []
active_effectblits     = []
active_effecttimers    = []
active_effects         = []
active_pillars         = []
active_walls           = []
active_rooms           = []
active_collective      = [active_keys, active_projectiles, active_mines, active_enemies_small,
                          active_enemies_boss, active_powerups, active_effectblits, active_effectblits,
                          active_effecttimers, active_effects, active_pillars, active_walls]
misc_blit_queue        = []
active_menus           = []

font_render_cache      = []
frame_times            = []

## INITIALIZATION
window_height = config.window_height
window_width  = config.window_width

pygame.display.set_caption(window_title)
pygame.display.set_icon(projectile_image)
game_display = pygame.display.set_mode((window_width, window_height),
                                       pygame.RESIZABLE)

persist_cfg = configparser.ConfigParser()
persist_cfg.read('config.ini')


start_t = time()

## CLASSES
# ENEMIES
class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, img_obj):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.pos = (self.x, self.y)
        self.facing = None
        self.step = 0
        self.last_attack = ticks
        self.img_size = img_obj.get_rect().size
        self.rect = pygame.Rect(self.pos, self.img_size)

    def attack(self, atk_type, atk_tup, nondefaultlist=None):
        """Attacks the player

        :param atk_type: Which attack the enemy should do.s
        :param atk_tup: A tuple with the subclass's attack packages.
        :param nondefaultlist: The list to add the projectile to, usually the
                               projectile list in the active room."""
        player.recalc_center()
        projectile_ = Projectile(self.pos,
                                 (player.center[0], player.center[1]),
                                 ticks, 'enemy',
                                 atk_tup[0] if atk_type == 1 else atk_tup[1],
                                 nondefaultlist=nondefaultlist)

        active_projectiles.append(projectile_)
        self.last_attack = ticks

    def blit_facing(self, sprite_tup):
        if self.facing == 'right':
            game_display.blit(sprite_tup[0], (self.x, self.y))
        elif self.facing == 'left':
            game_display.blit(sprite_tup[1], (self.x, self.y))


    def move(self, move_dict):
        if self.step >= move_dict['ticks_to_move']:
            add_or_sub = ('+', '-')
            if choice(add_or_sub) == '+':
                self.x += randint(move_dict['x']['min'], move_dict['x']['max'])
                self.update_rect()
            else:
                self.x -= randint(move_dict['x']['min'], move_dict['x']['max'])
                self.update_rect()

            if choice(add_or_sub) == '+':
                self.y += randint(move_dict['y']['min'], move_dict['y']['max'])
                self.update_rect()
            else:
                self.y -= randint(move_dict['y']['min'], move_dict['y']['max'])
                self.update_rect()
            self.step = 0
            self.update_rect()
        self.step += 1

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.img_size[0], self.img_size[1])

    def do_kill(self, kill_dict):
        global last_enemy_boss_death
        global last_enemy_small_death

        if kill_dict['type'] == 'boss': last_enemy_boss_death = ticks
        else: last_enemy_small_death = ticks
        try:
            del active_room.enemies_small[active_room.enemies_small.index(self)]
        except ValueError:
            del active_room.enemies_boss[active_room.enemies_boss.index(self)]

        player.score += kill_dict['score_val']

    def blit_health(self, health):
        game_display.blit(font_base.render('Health - ' + str(health), True, Color.Black),
                          (self.x + 10, self.y - 30))
class BossEnemy(Enemy):

    def __init__(self, x, y, nondefaultlist=None):
        pygame.sprite.Sprite.__init__(self)
        self.type        = 'enemy'
        self.img_obj     = pygame.image.load(assets_base_path + 'enemy_boss.png')
        self.health      = config.enemy_boss_health
        self.atk_tup     = (config.enemy_boss_atk1, config.enemy_boss_atk2)
        self.atks_dict   = {'atk1': {'freq': config.enemy_boss_atk1_freq,
                                     'atk_pack': self.atk_tup[0],
                                     'type': 1},
                            'atk_2': {'freq': config.enemy_boss_atk2_freq,
                                      'atk_pack': self.atk_tup[1],
                                      'type': 2}}
        self.sprite_tup  = (pygame.image.load(assets_base_path + 'enemy_boss.png'),
                            pygame.image.load(assets_base_path + 'enemy_boss_reversed.png'))
        self.move_dict   = config.enemy_boss_move_properties
        self.kill_dict   = {'score_val': config.enemy_boss_score_val,
                            'type': 'boss'}
        if nondefaultlist is None:
            active_enemies_boss.append(self)
        else:
            nondefaultlist.append(self)

        Enemy.__init__(self, x, y, self.img_obj)
class SmallEnemy(Enemy):
    """The small enemy class

    :param x: The x position for the enemy to be created at
    :param y: The y position for the enemy to be created at
    :param tick: The tick the enemy was created at"""

    def __init__(self, x, y, nondefaultlist=None):
        pygame.sprite.Sprite.__init__(self)
        self.type        = 'enemy'
        self.img_obj     = pygame.image.load(assets_base_path + '/enemy_sprite.png')
        self.health      = config.enemy_small_health
        self.atk_tup     = (config.enemy_small_atk1, config.enemy_small_atk2)
        self.atks_dict   = {'atk1': {'freq': config.enemy_small_atk1_freq,
                                     'atk_pack': self.atk_tup[0],
                                     'type': 1},
                            'atk_2': {'freq': config.enemy_small_atk2_freq,
                                      'atk_pack': self.atk_tup[1],
                                      'type': 2}}
        self.sprite_tup  = (pygame.image.load(assets_base_path + '/enemy_sprite.png'),
                            pygame.image.load(assets_base_path + '/enemy_sprite_reversed.png'))
        self.move_dict   = config.enemy_small_move_dict
        self.kill_dict   = {'score_val': config.enemy_small_score_val,
                            'type': 'small'}
        if nondefaultlist is None:
            active_enemies_small.append(self)
        else:
            nondefaultlist.append(self)
        Enemy.__init__(self, x, y, self.img_obj)
# PROJECTILE
class Projectile(pygame.sprite.Sprite):
    """Projectile class

    :param origin: The starting position for the projectile,
                    the player or enemy's position
    :param target: Where the player or enemy intends for the
                    projectile to go, at mouseclick pos or
                    player position.
    :param tick: The tick the projectile was created at
    :param type_: The projectile type, either 'friendly' or 'enemy'"""

    def __init__(self, origin, target, tick, type_, attack_package, nondefaultlist=None):
        pygame.sprite.Sprite.__init__(self)
        self.pos = origin
        self.type = type_
        self.target = target
        self.atk_package = attack_package
        self.damage = self.atk_package[0]
        self.lifepsan = self.atk_package[2]
        self.angle = functions.get_angle(self.pos, self.target)
        self.speed = self.atk_package[1]
        self.tickmade = tick
        self.rect = pygame.Rect(self.pos[0] + 8, self.pos[1] + 7, 17, 17)
        if nondefaultlist is None:
            pass
        else:
            nondefaultlist.append(self)


    def update(self):
        if self.pos == self.target:
            self.kill()
        self.angle = functions.get_angle(self.pos, self.target)
        self.pos = functions.project(self.pos, self.angle, self.speed)
        self.rect = pygame.Rect(self.pos[0] + 8, self.pos[1] + 7, 17, 17)

    def blit(self):
        if self.type == 'friendly':
            game_display.blit(projectile_image, (self.pos[0], self.pos[1]))
        elif self.type == 'enemy':
            game_display.blit(bad_thing_image, (self.pos[0], self.pos[1]))

    def collided_with(self, sprite_rect):
        return self.rect.colliderect(sprite_rect)

    def kill(self, list_):
        try:
            del list_[list_.index(self)]
        except ValueError:
            print('ERR - Value error on projectile kill attempt')
# PLAYER
class Player(pygame.sprite.Sprite):
    """The player class"""

    health = config.player_health
    x = config.player_starting_y
    y = config.player_starting_y

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.player_name = inputbox.ask(game_display, "Enter Player Name", font_base)
        self.img_verts = None
        self.center = None
        self.facing = None
        self.score = 0
        self.type = 'friendly'
        self.godmode = config.player_godmode
        self.atks = (config.player_atk1, config.player_atk2)
        self.img_size = player_sprite_image.get_rect().size
        self.last_display_effect_start = None
        self.name_text = font_base.render(self.player_name, True, Color.Black)
        self.rect = pygame.Rect(self.x + 8, self.y + 52, 67, 134)
        self.curr_room = 0

    def refresh_rect(self):
        self.rect = pygame.Rect(self.x + 8, self.y + 52, 67, 134)

    def attack(self, eventpos, atk_type, nondefaultlist=None):
        self.recalc_center()
        projectile_ = Projectile(self.center,
                                 eventpos,
                                 ticks, 'friendly',
                                 self.atks[0] if atk_type == 1
                                 else self.atks[1],
                                 nondefaultlist=nondefaultlist)
        active_projectiles.append(projectile_)

    def blit_facing(self):
        if self.facing == 'right':
            game_display.blit(pygame.image.load(player_sprite), (self.x, self.y))
        elif self.facing == 'left':
            game_display.blit(pygame.image.load(player_sprite_reversed), (self.x, self.y))

    def blit_name(self):
        game_display.blit(self.name_text,
                          ((self.img_size[0] / 2) - 10, (self.img_size[1] / 2) - 25))

    def recalc_center(self):
        self.center = functions.player_center((self.x, self.y), self.img_size)

    def recalc_img_verts(self):
        self.img_verts = functions.player_verts((self.x, self.y), self.img_size)

    def do_display_effect(self, object_):
        if object_.effect_elev <= 15:
            game_display.blit(object_.display_effect_text, (self.x, self.y - 20 - object_.effect_elev * 3))
            object_.effect_elev += 1
        else:
            object_.do_kill()

    def which_room_in(self):
        for room in active_rooms:
            if room.collided_with(player.rect):
                self.curr_room = room.room_id
                break

    def kill(self):
        death_screen()

# MINE
class Mine(pygame.sprite.Sprite):
    """The mine class

    :param x: The x position for the mine to be created at
    :param y: The y position for the mine to be created at"""

    health = config.mine_health
    damage = config.mine_damage

    def __init__(self, x, y, nondefaultlist=None):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(sprite_bad_thing)
        self.rect = pygame.Rect((self.x, self.y), (32, 32))
        if nondefaultlist is None:
            pass
        else:
            nondefaultlist.append(self)

    def blit(self):
        game_display.blit(self.image, (self.x, self.y))

    def collided_with(self):
        return self.rect.colliderect(player.rect)

    def kill(self):
        del active_mines[active_mines.index(self)]
# POWERUPS
class PowerUp(pygame.sprite.Sprite):

    def __init__(self, x, y, img_obj, effect_, effect_text):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.img_obj = img_obj
        self.effect = effect_
        self.tickmade = ticks
        self.img_size = img_obj.get_rect().size
        self.effect_text = effect_text
        self.rect = pygame.Rect(self.pos, self.img_size)

    def collided_with(self, sprite_rect):
        return self.rect.colliderect(sprite_rect)

    def blit(self):
        game_display.blit(self.img_obj, (self.x, self.y))
        text = font_base.render(self.effect_text, True, Color.Black)
        game_display.blit(text, ((self.x + self.img_size[0] / 2) - font_base.size(self.effect_text)[0] / 2,
                                  self.y - 3 - font_base.size(self.effect_text)[1]))

    def blit_effect(self, pos):
        text = font_base.render(self.effect, True, Color.Black)
        game_display.blit(text, (window_width - 3 - font_base.size(self.effect)[0], 3 + pos[1]))

    def do_kill(self, kill_type):
        if kill_type == 'healthpack':
            global last_healthpack_used
            global active_healthpacks
            last_healthpack_used = ticks
            active_healthpacks -= 1
        elif kill_type == 'dmgup':
            global last_attackboost_used
            global active_dmgup
            last_attackboost_used = ticks
        elif kill_type == 'shield':
            global last_shield_used
            global active_shield
            last_shield_used = ticks
            active_shield -= 1
        try:
            del active_room.powerups[active_room.powerups.index(self)]
        except ValueError:
            pass
        if self in active_effects: del active_effects[active_effects.index(self)]

    def render_kill(self):
        del active_room.powerups[active_room.powerups.index(self)]
class HealthPack(PowerUp): # INSTANT POWERUP
    """The class for the health pack
    :param x: The x position for the pack to be created at
    :param y: The y position for the pack to be created at"""

    def __init__(self, x, y, nondefaultlist=None):
        pygame.sprite.Sprite.__init__(self)
        self.img_obj = health_pack_image
        self.max_active = config.max_healthpacks
        self.kill_type = 'healthpack'
        self.effect = '+ Health'
        global active_healthpacks
        active_healthpacks += 1
        active_powerups.append(self)
        if nondefaultlist is None:
            pass
        else:
            nondefaultlist.append(self)
        PowerUp.__init__(self, x, y, self.img_obj, None, self.effect)

    def do_effect(self):
        player.health += config.healthpack_heal_amount
        new_effectblit = EffectBlit(ticks, '+ ' + str(config.healthpack_heal_amount) + ' Health', (0, 0, 0))
        active_effectblits.append(new_effectblit)
        self.do_kill(self.kill_type)
class DamageUp(PowerUp): # TEMPORARY POWERUP
    def __init__(self, x, y, nondefaultlist=None):
        self.img_obj = dmgup_image
        self.max_active = config.max_dmgup
        self.kill_type = 'dmgup'
        self.lifespan = config.dmgup_lifespan
        self.active_effect = 'Damage Buff'
        self.effect = '+ Damage'
        global active_dmgup
        active_dmgup += 1
        active_powerups.append(self)
        if nondefaultlist is None:
            pass
        else:
            nondefaultlist.append(self)
        PowerUp.__init__(self, x, y, self.img_obj, self.active_effect, self.effect)

    def do_effect(self):
        global active_dmgup
        active_dmgup += 1
        print('dmgup used')
        new_effectblit = EffectBlit(ticks, 'Damage Buff', (0, 0, 0))
        active_effectblits.append(new_effectblit)

        new_effecttimer = EffectTimer(self.lifespan, self)
        active_effecttimers.append(new_effecttimer)
        active_effects.append(self)
        self.render_kill()

    @staticmethod
    def undo_effect():
        global active_dmgup
        active_dmgup -= 1
        print('effect undone')
class Shield(PowerUp):
    def __init__(self, x, y, nondefaultlist=None):
        self.img_obj = pygame.image.load(assets_base_path + '/shield.png')
        self.max_active = config.max_shield
        self.kill_type = 'shield'
        self.lifespan = config.shield_lifespan
        self.active_effect = 'Immunity'
        self.effect = 'Shield'
        global active_shield
        active_shield += 1
        active_powerups.append(self)
        if nondefaultlist is None:
            pass
        else:
            nondefaultlist.append(self)
        PowerUp.__init__(self, x, y, self.img_obj, u'Immunity', u'Immunity')

    def do_effect(self):
        player.godmode = True
        new_effectblit = EffectBlit(ticks, 'Shield', (0, 0, 0))
        active_effectblits.append(new_effectblit)
        new_effecttimer = EffectTimer(self.lifespan, self)
        active_effecttimers.append(new_effecttimer)
        active_effects.append(self)
        self.render_kill()

    @staticmethod
    def undo_effect():
        player.godmode = False if config.player_godmode == False else True
# EFFECT HELPERS
class EffectBlit:
    def __init__(self, tickmade, effect_type, color):
        self.tickmade = tickmade
        self.effect_elev = 0
        self.effect_text = effect_type
        self.color = color
        self.display_effect_text = font_base.render(self.effect_text, True, self.color)
        active_effectblits.append(self)

    def do_kill(self):
        del active_effectblits[active_effectblits.index(self)]
class EffectTimer: # ONLY USED IN TEMPORARY POWERUPS
    def __init__(self, lifespan, parent_obj):
        self.tickmade = ticks
        self.lifespan = lifespan
        self.parent = parent_obj
        active_effecttimers.append(self)

    def check_timer(self):
        if ticks - self.tickmade >= self.lifespan:
            self.parent.undo_effect()
            self.do_kill()

    def do_kill(self):
        self.parent.do_kill(self.parent.kill_type)
        del active_effecttimers[active_effecttimers.index(self)]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, rect, img):
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.rect = rect
        self.img_obj = img
        pygame.sprite.Sprite.__init__(self)

    def collided_with(self, sprite_rect):
        return self.rect.colliderect(sprite_rect)

    def blit(self):
        try:
            game_display.blit(self.img_obj, (self.x, self.y))
        except TypeError as e:
            # print('TypeError in Obstacle Blit')
            # print(e)
            pass
class Pillar(Obstacle):
    def __init__(self, pos, nondefaultlist=None):
        self.img_obj = pygame.image.load(assets_base_path + '/pillar.png')
        self.img_size = self.img_obj.get_rect().size
        self.rect = pygame.Rect(pos[0] + 6, pos[1] + 19, 49, 107)
        self.solid_to_projectile = True
        self.solid_to_player = True
        if nondefaultlist is None:
            active_pillars.append(self)
        else:
            nondefaultlist.append(self)
        Obstacle.__init__(self, pos, self.rect, self.img_obj)
class Wall(Obstacle):
    def __init__(self, pos, nondefaultlist=None):
        self.img_obj = pygame.image.load(assets_base_path + '/wall.png')
        self.rect = pygame.Rect(pos[0] + 6, pos[1] + 19, 49, 107)
        self.solid_to_projectile = True
        self.solid_to_player = True
        if nondefaultlist is None:
            active_walls.append(self)
        else:
            nondefaultlist.append(self)
        Obstacle.__init__(self, pos, self.rect, self.img_obj)
class InvisWall(Obstacle):
    def __init__(self, pos, width, height, targetlist=None):
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.solid_to_projectile = False
        self.solid_to_player = True
        if targetlist is None:
            active_walls.append(self)
        else:
            targetlist.append(self)
        Obstacle.__init__(self, pos, self.rect, None)

class Menu(pygame.sprite.Sprite):
    def __init__(self):
        self.active = False
        pygame.sprite.Sprite.__init__(self)

    def set_active(self):
        pass
class SettingsMenu(Menu):
    def __init__(self):
        self.menu_width = 400
        self.menu_height = 400
        self.title = font_base.render('Settings', True, (255, 255, 255))
        self.toggled_true_img = pygame.image.load(assets_base_path + '/checkboxes_False.png')
        self.collapsed_img = pygame.image.load(assets_base_path + '/checkboxes_True.png')
        self.collapsed_img_size = self.collapsed_img.get_rect().size
        self.pos = (window_width - self.collapsed_img_size[0], 0)
        self.collapsed_rect = pygame.Rect(self.pos[0], self.pos[1], self.collapsed_img_size[0], self.collapsed_img_size[1])
        self.expanded_rect = pygame.Rect(window_width - self.menu_width, 0, self.menu_width, self.menu_height)
        self.settings_rects = [pygame.Rect(self.pos[0] + 30, self.pos[1] + 30, 32, 32)]
        self.settings_deps = {'player_godmode': [persist_cfg['Player'].getboolean('player_godmode'), False],
                              'render_player_verts': [persist_cfg['RuntimeSettings'].getboolean('render_player_verts'), True],
                              'render_hitboxes': [persist_cfg['RuntimeSettings'].getboolean('render_hitboxes'), False]}
        self.settings = {'GodMode': {'rect': pygame.Rect(window_width - 390, 0 * 45 + 35,
                                                         32, 32),
                                     'toggle_action': {'Section': 'Player', 'Setting': 'player_godmode', 'Value': self.settings_deps['player_godmode'][0]}},

                         'Render_player_verts': {'rect': pygame.Rect(window_width - 390, 1 * 45 + 35,
                                                                     32, 32),
                                                  'toggle_action': {'Section': 'RuntimeSettings', 'Setting': 'render_player_verts', 'Value': self.settings_deps['render_player_verts'][0]}},

                         'Render_hitboxes': {'rect': pygame.Rect(window_width - 390, 2 * 45 + 35,
                                                         32, 32),
                                             'toggle_action': {'Section': 'RuntimeSettings', 'Setting': 'render_hitboxes', 'Value': self.settings_deps['render_hitboxes'][0]}}}
        Menu.__init__(self)


    def update_settings(self, section, setting, value):
        print('Settings Change')
        print(section)
        print(setting)
        print(not value)

        persist_cfg.set(str(section), str(setting), str(not value))
        self.settings_deps[setting][1] = not self.settings_deps[setting][1]

    def blit(self):
        if self.active:
            count = 0
            backrect = pygame.Surface((self.expanded_rect[2], self.expanded_rect[3]))
            backrect.set_alpha(150)
            backrect.fill((0, 0, 0))
            game_display.blit(backrect, (window_width - self.menu_width, 0))
            game_display.blit(self.title, (window_width - self.menu_width + 10, 10))

            for key, value in self.settings.items():
                game_display.blit(self.toggled_true_img if self.settings_deps[value['toggle_action']['Setting']][1] else self.collapsed_img, (window_width - 390, count * 45 + 35))
                game_display.blit(font_base.render(str(key), True, (255, 255, 255)), (window_width - 343, count * 45 + 35))
                count += 1
        else:
            game_display.blit(self.collapsed_img, self.pos)

    def check_collision(self, eventpos):
        return self.collapsed_rect.collidepoint(eventpos[0], eventpos[1])

    def check_expanded_collision(self, eventpos):
        return self.expanded_rect.collidepoint(eventpos[0], eventpos[1])

    def check_which_setting_toggle(self, eventpos):
        for _, subdict in self.settings.items():
            if subdict['rect'].collidepoint(eventpos[0], eventpos[1]):
                self.update_settings(subdict['toggle_action']['Section'],
                                     subdict['toggle_action']['Setting'],
                                     subdict['toggle_action']['Value'])

    def toggle_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True

class Room:
    def __init__(self):
        self.size = (config.room_width, config.room_height)
        self.relative_pos = None
        self.obstacles = self.gen_obstacles()
        self.inviswalls = []
        self.entities = []
        self.projectiles = []
        self.enemies_boss = []
        self.enemies_small = []
        self.powerups = []
        self.mines = []
        self.room_id = len(active_rooms)
        self.rect = (0, 0, self.size[0], self.size[1])
        active_rooms.append(self)

    @staticmethod
    def gen_obstacles():
        num_obstacles_to_generate = choice(config.minmax_obstacles_perroom)
        generated_obstacles = []

        for _ in range(num_obstacles_to_generate):
            obstacle_to_generate = randint(0, 1)
            position_to_generate = (randint(200, window_width - 100), randint(100, window_height - 300))
            if obstacle_to_generate == 0:
                Pillar(position_to_generate, generated_obstacles)
            elif obstacle_to_generate == 1:
                Wall(position_to_generate, generated_obstacles)
        return generated_obstacles

    def gen_inviswalls(self, w, h):
        del self.inviswalls[:]
        InvisWall((-1, -1), w + 1, 1, self.inviswalls)
        InvisWall((window_width + 1, -1), 1, h + 1, self.inviswalls)
        InvisWall((-1, h + 1), w + 1, 1, self.inviswalls)
        InvisWall((-1, -1), 1, h + 1, self.inviswalls)



settings_menu = SettingsMenu()
active_menus.append(settings_menu)

## Init for border walls

player = Player()
startroom = Room()

def death_screen():
    quit() # Temporary

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

def kill_all_keys():
    for _, value in active_keys.items():
        active_keys[_] = False

def remake_inviswalls(w, h):
    del active_walls[:]
    InvisWall((-1, -1), w + 1, 1)
    InvisWall((window_width + 1, -1), 1, h + 1)
    InvisWall((-1, h + 1), w + 1, 1)
    InvisWall((-1, -1), 1, h + 1)




title_screen()
gameExit = False
while not gameExit:
    # print((player.x, player.y))
    # print(player.score)
    persist_cfg.read('config.ini')
    active_room = active_rooms[player.curr_room]
    tick_start_time = datetime.now()
    ticks += 1

    ## ON EVENT
    for event in pygame.event.get():
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,
                                  pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP,
                                  pygame.MOUSEBUTTONDOWN])
        if event.type == pygame.QUIT:
            gameExit = True

        if event.type == pygame.VIDEORESIZE:
            window_height = event.h
            window_width = event.w
            game_display = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
            home_image = pygame.transform.scale(home_image, (window_width, window_height))
            active_room.gen_inviswalls(window_width, window_height)

        ## Character Movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: active_keys['w'] = True
            elif event.key == pygame.K_a: active_keys['a'] = True
            elif event.key == pygame.K_s: active_keys['s'] = True
            elif event.key == pygame.K_d: active_keys['d'] = True
            elif event.key == pygame.K_r: kill_all_keys()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w: active_keys['w'] = False
            elif event.key == pygame.K_a: active_keys['a'] = False
            elif event.key == pygame.K_s: active_keys['s'] = False
            elif event.key == pygame.K_d: active_keys['d'] = False

        ## Projectiles and Targeting
        # Making the projectile
        if event.type == pygame.MOUSEBUTTONDOWN:
            if settings_menu.check_collision(event.pos):
                settings_menu.toggle_active()
            elif settings_menu.check_expanded_collision(event.pos):
                settings_menu.check_which_setting_toggle(event.pos)
            else:
                if pygame.mouse.get_pressed()[0] == 1:
                    player.attack(event.pos, 1, active_room.projectiles)
                elif pygame.mouse.get_pressed()[2] == 1:
                    pass

        # Player Facing
        if event.type == pygame.MOUSEMOTION:
            if event.pos[0] > player.x: player.facing = 'right'
            else: player.facing = 'left'


    if player.health <= 0 and player.godmode is False:
        player.kill()

    ## ENEMY ACTIONS
    for enemy in active_room.enemies_small + active_room.enemies_boss:
        # ATTACKING
        for __, attack in enemy.atks_dict.items():
            if ticks - enemy.last_attack >= attack['freq']:
                enemy.attack(attack['type'], enemy.atk_tup, active_room.projectiles)
                enemy.last_attack = ticks

        # HEALTH CHECK
        if enemy.health <= 0:
            enemy.do_kill(enemy.kill_dict)
            enemies_killed += 1
            print('TASK - Enemy killed - ' + str(enemies_killed) + ' Total')

        # FACING
        if player.x > enemy.x: enemy.facing = 'right'
        elif player.x < enemy.x: enemy.facing = 'left'

        enemy.move(enemy.move_dict)


    ## SPAWNING
    if config.enable_enemy_spawning:
        # BOSSES
        if ticks - last_enemy_boss_death > config.enemy_boss_create_freq and len(active_room.enemies_boss) <= config.max_enemy_boss:
            BossEnemy(randint(200, 1000), randint(200, 600), active_room.enemies_boss)

        # SMALL ENEMIES
        if ticks - last_enemy_small_death > config.enemy_small_create_freq and len(active_room.enemies_small) <= config.max_enemy_small:
            SmallEnemy(randint(200, 1000), randint(200, 600), active_room.enemies_small)
    # HEALTH PACKS
    if ticks - last_healthpack_used > config.healthpack_create_freq and active_healthpacks <= config.max_healthpacks:
        HealthPack(randint(60, 1140), randint(40, 760), active_room.powerups)

    # ATKUP
    if ticks - last_attackboost_used > config.dmgup_create_freq and active_dmgup <= config.max_dmgup:
        DamageUp(randint(60, 1140), randint(40, 760), active_room.powerups)

    # SHIELD
    if ticks - last_shield_used > config.shield_create_freq and active_shield <= config.max_shield:
        if randint(0, 5) == 1:
            Shield(randint(60, 1140), randint(40, 760), active_room.powerups)


    ## MOVEMENT, COLLISION, AND FPS
    rect_ = copy(player)
    if active_keys['w']: rect_.y -= config.player_movespeed_vertical
    if active_keys['s']: rect_.y += config.player_movespeed_vertical
    if active_keys['a']: rect_.x -= config.player_movespeed_horizontal
    if active_keys['d']: rect_.x += config.player_movespeed_horizontal
    rect_.refresh_rect()
    pillar_player_collisions_list = pygame.sprite.spritecollide(rect_, active_room.obstacles, False)
    wall_player_collisions_list = pygame.sprite.spritecollide(rect_, active_room.inviswalls, False)
    if len(pillar_player_collisions_list + wall_player_collisions_list) != 0:
        pass
    else:
        player = rect_

    # PROJECTILE COLLISION SCANNING
    # PROJECTILES
    # Update projectile position
    for projectile in active_room.projectiles:
        projectile.update()
        if (ticks - projectile.tickmade) > projectile.atk_package[2] or \
                        projectile.pos == projectile.target:
            projectile.kill(active_room.projectiles)

        # If enemy projectile collides with player
        if projectile.collided_with(player.rect):
            if projectile.type == 'enemy':
                if player.godmode is False:
                    print('Godmode Off')
                    player.health = player.health - projectile.damage
                    EffectBlit(ticks, '- ' + str(projectile.damage) + ' Health', (255, 0, 0))
                projectile.kill(active_room.projectiles)

        # If player projectile collides with enemy
        if projectile.type != 'enemy':
            collisionslist = pygame.sprite.spritecollide(projectile, active_room.enemies_small, False)
            collisions_list = collisionslist + pygame.sprite.spritecollide(projectile, active_room.enemies_boss, False)
            # if len(collisionslist) != 0: print(collisionslist)
            if len(collisions_list) != 0:
                for enemy in collisions_list:
                    print(enemy.health)
                    print('dmgup - ' + str(active_dmgup))
                    print(projectile.damage)
                    dmg_multiplier = active_dmgup if active_dmgup != 0 else 1
                    print(dmg_multiplier)

                    if projectile.damage < 0:
                        enemy.health = enemy.health + projectile.damage * dmg_multiplier
                    else:
                        enemy.health = enemy.health - projectile.damage * dmg_multiplier
                    print(enemy.health)
                    print('~~~~~')
                projectile.kill(active_room.projectiles)

        wall_projs_collisions_list = pygame.sprite.spritecollide(projectile, active_room.inviswalls, False)
        pillar_projs_collisions_list = pygame.sprite.spritecollide(projectile, active_room.obstacles, False)
        if len(pillar_projs_collisions_list + wall_projs_collisions_list) != 0:
            for obstacle in pillar_projs_collisions_list + wall_projs_collisions_list:
                if obstacle.solid_to_projectile:
                    projectile.kill(active_room.projectiles)

    # MINES
    if len(active_room.mines) != 0:
        for mine in active_room.mines:
            if mine.collided_with():
                player.health -= mine.damage
                mine.kill()

    # HEALTHPACKS
    if len(active_room.powerups) != 0:
        for powerup in active_room.powerups:
            if powerup.collided_with(player.rect):
                powerup.do_effect()

    if len(active_effecttimers) != 0:
        for timer in active_effecttimers:
            timer.check_timer()


    end_t = time()
    time_taken = end_t - start_t
    start_t = end_t
    frame_times.append(time_taken)
    frame_times = frame_times[-20:]
    fps = int(len(frame_times) / sum(frame_times))
    fps_string = 'FPS - ' + str(fps)


    ## Rendering
    '''
    if ticks <= 5:
        player_health = font_base.render('Health - ' + str(player.health), True, Color.Black)
        font_render_cache.append(player_health)

    if player.health != tick_cache[1]:
        player_health   = font_base.render('Health - ' + str(player.health), True, Color.Black)
        font_render_cache[2] = player_health
        '''

    player_health = font_base.render('Health - ' + str(player.health), True, Color.Black)
    player_score = font_base.render('Score - ' + str(player.score), True, Color.Black)
    fps_text = font_base.render(fps_string, True, Color.Black)
    game_display.blit(home_image, (0,0))
    game_display.blit(fps_text,
                      (window_width - font_base.size(fps_string)[0] - 15,
                       window_height - font_base.size(fps_string)[1] - 3))
    game_display.blit(player_health, (0, 0))
    game_display.blit(player_score, (0, 24))

    player.blit_facing()

    active_collective = [active_room.projectiles, active_room.mines, active_room.powerups,
                         active_room.obstacles, active_room.inviswalls]

    count = 0
    for list_ in active_collective:
        count += 1
        try:
            for thing_ in list_:
                thing_.blit()
        except ValueError:
            pass

    try:
        for enemy in active_room.enemies_small + active_room.enemies_boss:
            enemy.blit_facing(enemy.sprite_tup)
            enemy.blit_health(enemy.health)
    except ValueError:
        pass

    try:
        for effect in active_effectblits:
            player.do_display_effect(effect)
    except ValueError:
        pass

    try:
        i = 0
        for effect in active_effects:
            effect.blit_effect((None, i * 20 + 3 if i >= 1 else 0))
            i += 1 # Spacing between effects
    except ValueError:
        pass

    for obstacle in active_room.obstacles:
        obstacle.blit()


    settings_menu.blit()

    # OPTIONAL, TO ENABLE, SEE CONFIG FILE SETTINGS
    # To monitor player verts
    if config.render_hitboxes:
        if len(active_room.obstacles) != 0:
            for obstacle in active_room.obstacles:
                s = pygame.Surface((obstacle.rect[2], obstacle.rect[3]))
                s.set_alpha(150)
                s.fill((255, 0, 0))
                game_display.blit(s, (obstacle.rect[0], obstacle.rect[1]))

        if len(active_room.enemies_small + active_room.enemies_boss) != 0:
            for enemy in active_room.enemies_small + active_room.enemies_boss:
                s = pygame.Surface((enemy.rect[2], enemy.rect[3]))
                s.set_alpha(150)
                s.fill((255, 0, 0))
                game_display.blit(s, (enemy.rect[0], enemy.rect[1]))

        if len(active_room.inviswalls) != 0:
            for inviswall in active_room.inviswalls:
                s = pygame.Surface((inviswall.rect[2], inviswall.rect[3]))
                s.set_alpha(150)
                s.fill((255, 255, 0))
                game_display.blit(s, (inviswall.rect[0], inviswall.rect[1]))

        if len(active_room.projectiles) != 0:
            for projectile in active_room.projectiles:
                s = pygame.Surface((projectile.rect[2], projectile.rect[3]))
                s.set_alpha(150)
                s.fill((0, 0, 0))
                game_display.blit(s, (projectile.rect[0], projectile.rect[1]))

        s = pygame.Surface((player.rect[2], player.rect[3]))
        s.set_alpha(150)         
        s.fill((255, 0, 0))
        game_display.blit(s, (player.rect[0], player.rect[1]))


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
