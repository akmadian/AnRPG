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
#TODO: Source sprite spawn area ranges to config file
#TODO: Fix caching
#TODO: Fix effect blit overlap of multiple effects

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

enemies_killed = 0
last_enemy_boss_death = 0
last_enemy_small_death = 0
last_healthpack_used = 0
last_attackboost_used = 0
last_shield_used       = 0
active_healthpacks = 0
active_dmgup = 0
active_shield = 0


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

    def attack(self, atk_type, atk_tup):
        """Attacks the player

        :param atk_type: Which attack the enemy should do.s
        :param atk_tup: A tuple with the subclass's attack packages."""
        player.recalc_center()
        projectile_ = Projectile(self.pos,
                                 (player.center[0], player.center[1]),
                                 ticks, 'enemy',
                                 atk_tup[0] if atk_type == 1 else atk_tup[1])

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
            else:
                self.x -= randint(move_dict['x']['min'], move_dict['x']['max'])

            if choice(add_or_sub) == '+':
                self.y += randint(move_dict['y']['min'], move_dict['y']['max'])
            else:
                self.y -= randint(move_dict['y']['min'], move_dict['y']['max'])
            self.step = 0
            self.update_rect()
        self.step += 1

    def update_rect(self):
        self.rect = pygame.Rect(self.pos, self.img_size)

    def do_kill(self, kill_dict):
        global last_enemy_boss_death
        global last_enemy_small_death

        if kill_dict['type'] == 'boss': last_enemy_boss_death = ticks
        else: last_enemy_small_death = ticks
        try:
            del active_enemies_small[active_enemies_small.index(self)]
        except ValueError:
            del active_enemies_boss[active_enemies_boss.index(self)]

        player.score += kill_dict['score_val']

    def blit_health(self, health):
        game_display.blit(font_base.render('Health - ' + str(health), True, Color.Black),
                          (self.x + 10, self.y - 30))
class BossEnemy(Enemy):

    def __init__(self, x, y):
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
        Enemy.__init__(self, x, y, self.img_obj)
class SmallEnemy(Enemy):
    """The small enemy class

    :param x: The x position for the enemy to be created at
    :param y: The y position for the enemy to be created at
    :param tick: The tick the enemy was created at"""

    def __init__(self, x, y):
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
        Enemy.__init__(self, x, y, self.img_obj)

class Projectile(pygame.sprite.Sprite):
    """Projectile class

    :param origin: The starting position for the projectile,
                    the player or enemy's position
    :param target: Where the player or enemy intends for the
                    projectile to go, at mouseclick pos or
                    player position.
    :param tick: The tick the projectile was created at
    :param type_: The projectile type, either 'friendly' or 'enemy'"""

    def __init__(self, origin, target, tick, type_, attack_package):
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
        try:
            del active_projectiles[active_projectiles.index(self)]
        except ValueError:
            print('ERR - Value error on projectile kill attempt')

class Player(pygame.sprite.Sprite):
    """The player class"""

    health = config.player_health
    x = config.player_starting_y
    y = config.player_starting_y

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.player_name = None
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
        self.rect = pygame.Rect((self.x, self.y + 92),
                                (self.img_size[0], self.img_size[1] - 92))

    def refresh_rect(self):
        self.rect = pygame.Rect((self.x, self.y + 92),
                                (self.img_size[0], self.img_size[1] - 92))

    def attack(self, eventpos, atk_type):
        self.recalc_center()
        projectile_ = Projectile(self.center,
                                 eventpos,
                                 ticks, 'friendly',
                                 self.atks[0] if atk_type == 1
                                 else self.atks[1])
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

    def blit_effect(self):
        text = font_base.render(self.effect, True, Color.Black)
        game_display.blit(text, (1200 - 3 - font_base.size(self.effect)[0], 3))

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
            active_dmgup -= 1
        elif kill_type == 'shield':
            global last_shield_used
            global active_shield
            last_shield_used = ticks
            active_shield -= 1
        try:
            del active_powerups[active_powerups.index(self)]
        except ValueError:
            pass
        if self in active_effects: del active_effects[active_effects.index(self)]

    def render_kill(self):
        del active_powerups[active_powerups.index(self)]
class HealthPack(PowerUp): # INSTANT POWERUP
    """The class for the health pack
    :param x: The x position for the pack to be created at
    :param y: The y position for the pack to be created at"""

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.img_obj = health_pack_image
        self.max_active = config.max_healthpacks
        self.kill_type = 'healthpack'
        self.effect = '+ Health'
        PowerUp.__init__(self, x, y, self.img_obj, None, self.effect)

    def do_effect(self):
        player.health += config.healthpack_heal_amount
        new_effectblit = EffectBlit(ticks, '+ ' + str(config.healthpack_heal_amount) + ' Health')
        active_effectblits.append(new_effectblit)
        self.do_kill(self.kill_type)
class DamageUp(PowerUp): # TEMPORARY POWERUP
    def __init__(self,x ,y):
        self.img_obj = dmgup_image
        self.max_active = config.max_dmgup
        self.kill_type = 'dmgup'
        self.lifespan = config.dmgup_lifespan
        self.active_effect = 'Damage Buff'
        self.effect = '+ Damage'
        PowerUp.__init__(self, x, y, self.img_obj, self.active_effect, self.effect)
    def do_effect(self):
        for atk in player.atks: atk[0] += config.dmgup_effect_amount

        new_effectblit = EffectBlit(ticks, 'Damage Buff')
        active_effectblits.append(new_effectblit)

        new_effecttimer = EffectTimer(self.lifespan, self)
        active_effecttimers.append(new_effecttimer)
        active_effects.append(self)
        self.render_kill()

    @staticmethod
    def undo_effect():
        for atk in player.atks: atk[0] -= config.dmgup_effect_amount
class Shield(PowerUp):
    def __init__(self, x, y):
        self.img_obj = pygame.image.load(assets_base_path + '/shield.png')
        self.max_active = config.max_shield
        self.kill_type = 'shield'
        self.lifespan = config.shield_lifespan
        self.active_effect = 'Immunity'
        self.effect = 'Shield'
        PowerUp.__init__(self, x, y, self.img_obj, u'Immunity', u'Immunity')

    def do_effect(self):
        player.godmode = True
        new_effectblit = EffectBlit(ticks, 'Shield')
        active_effectblits.append(new_effectblit)
        new_effecttimer = EffectTimer(self.lifespan, self)
        active_effecttimers.append(new_effecttimer)
        active_effects.append(self)
        self.render_kill()

    @staticmethod
    def undo_effect():
        player.godmode = False

## EFFECT HELPER OBJECTS
class EffectBlit:
    def __init__(self, tickmade, effect_type):
        self.tickmade = tickmade
        self.effect_elev = 0
        self.effect_text = effect_type
        self.display_effect_text = font_base.render(self.effect_text, True, Color.Black)

    def do_kill(self):
        del active_effectblits[active_effectblits.index(self)]
class EffectTimer: # ONLY USED IN TEMPORARY POWERUPS
    def __init__(self, lifespan, parent_obj):
        self.tickmade = ticks
        self.lifespan = lifespan
        self.parent = parent_obj

    def check_timer(self):
        if ticks - self.tickmade >= self.lifespan:
            self.parent.undo_effect()
            self.do_kill()

    def do_kill(self):
        self.parent.do_kill(self.parent.kill_type)
        del active_effecttimers[active_effecttimers.index(self)]




pygame.display.set_caption(window_title)
pygame.display.set_icon(projectile_image)
game_display = pygame.display.set_mode((config.window_width, config.window_height),
                                       pygame.HWSURFACE)
active_keys           = {'w': None, 'a': None, 's': None, 'd': None}
active_projectiles    = []
active_mines          = []
active_enemies_small  = []
active_enemies_boss   = []
active_powerups       = []
active_effectblits    = []
active_effecttimers   = []
active_effects        = []

font_render_cache = []
tick_cache        = []


ticks = 0
pack = Shield(500, 400)
active_powerups.append(pack)

player = Player()
player.rect = pygame.image.load(player_sprite).get_rect()
name_text   = font_base.render(player.player_name, True, Color.Black)
font_render_cache.append(name_text)
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

title_screen()
gameExit = False
while not gameExit:
    # print(player.score)
    tick_start_time = datetime.now()
    ticks += 1

    ## ON EVENT
    for event in pygame.event.get():
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,
                                  pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP,
                                  pygame.MOUSEBUTTONDOWN])
        if event.type == pygame.QUIT:
            gameExit = True

        if player.health <= 0 and player.godmode is False:
            player.kill()

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
            # print((player.img_verts['cm'][0], player.img_verts['cm'][1]))
            # print(event.pos)
            player.attack(event.pos, 1)

        # Player Facing
        if event.type == pygame.MOUSEMOTION:
            if event.pos[0] > player.x: player.facing = 'right'
            else: player.facing = 'left'

    ## ENEMY ACTIONS
    for enemy in active_enemies_small + active_enemies_boss:
        for __, attack in enemy.atks_dict.items():
            if ticks - enemy.last_attack >= attack['freq']:
                enemy.attack(attack['type'], enemy.atk_tup)
                enemy.last_attack = ticks

        if enemy.health <= 0:
            enemy.do_kill(enemy.kill_dict)
            enemies_killed += 1
            print('TASK - Enemy killed - ' + str(enemies_killed) + ' Total')

        if player.x > enemy.x: enemy.facing = 'right'
        elif player.x < enemy.x: enemy.facing = 'left'

        enemy.move(enemy.move_dict)





    ## SPAWNING
    # BOSSES
    if ticks - last_enemy_boss_death > config.enemy_boss_create_freq and len(active_enemies_boss) <= config.max_enemy_boss:
        boss = BossEnemy(randint(200, 1000), randint(200, 600))
        active_enemies_boss.append(boss)

    # SMALL ENEMIES
    if ticks - last_enemy_small_death > config.enemy_small_create_freq and len(active_enemies_small) <= config.max_enemy_small:
        smallenemy = SmallEnemy(randint(200, 1000), randint(200, 600))
        active_enemies_small.append(smallenemy)

    # HEALTH PACKS
    if ticks - last_healthpack_used > config.healthpack_create_freq and active_healthpacks <= config.max_healthpacks:
        pack = HealthPack(randint(60, 1140), randint(40, 760))
        active_healthpacks += 1
        active_powerups.append(pack)

    # ATKUP
    if ticks - last_attackboost_used > config.dmgup_create_freq and active_dmgup <= config.max_dmgup:
        buff = DamageUp(randint(60, 1140), randint(40, 760))
        active_dmgup += 1
        active_powerups.append(buff)

    # SHIELD
    if ticks - last_shield_used > config.shield_create_freq and active_shield <= config.max_shield:
        if randint(0, 1) == 1:
            shield = Shield(randint(60, 1140), randint(40, 760))
            active_shield += 1
            active_powerups.append(shield)


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
        if (ticks - projectile.tickmade) > projectile.atk_package[2] or \
                        projectile.pos == projectile.target:
            projectile.kill()

        if projectile.collided_with(player.rect):
            if projectile.type == 'enemy':
                if player.godmode is False:
                    player.health = player.health - projectile.damage
                projectile.kill()

        if projectile.type != 'enemy':
            collisionslist = pygame.sprite.spritecollide(projectile, active_enemies_small, False)
            collisions_list = collisionslist + pygame.sprite.spritecollide(projectile, active_enemies_boss, False)
            # if len(collisionslist) != 0: print(collisionslist)
            if len(collisions_list) != 0:
                for enemy in collisions_list:
                    enemy.health = enemy.health - projectile.damage
                projectile.kill()

    # MINES
    if len(active_mines) != 0:
        for mine in active_mines:
            if mine.collided_with():
                player.health = player.health - mine.damage
                mine.kill()

    # HEALTHPACKS
    if len(active_powerups) != 0:
        for powerup in active_powerups:
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

    del tick_cache[:]
    tick_cache.append(fps)
    tick_cache.append(player.health)


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
    fps_text = font_base.render('FPS - ' + str(fps), True, Color.Black)
    game_display.blit(pygame.image.load(home), (0,0))
    game_display.blit(fps_text, (1130, 780))
    game_display.blit(player_health, (0, 0))
    game_display.blit(player_score, (0, 24))

    player.blit_facing()

    if len(active_projectiles) != 0:
        for projectile in active_projectiles:
            projectile.blit()

    if len(active_mines) != 0:
        for mine in active_mines:
            mine.blit()

    if len(active_enemies_small + active_enemies_boss) != 0:
        for enemy in active_enemies_small + active_enemies_boss:
            enemy.blit_facing(enemy.sprite_tup)
            enemy.blit_health(enemy.health)

    if len(active_powerups) != 0:
        for powerup in active_powerups:
            powerup.blit()

    if len(active_effectblits) != 0:
        for effect in active_effectblits:
            player.do_display_effect(effect)

    if len(active_effects) != 0:
        for effect in active_effects:
            effect.blit_effect()

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