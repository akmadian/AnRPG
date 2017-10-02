# -*- coding: utf-8 -*-
"""
    File Name: classes.py
    Author: Ari Madian
    Created: October 1, 2017 5:17 PM
    Python Version: 3.6
"""
import sys
import os

class Player:
    """The player class"""

    def __init__(self):
        self.player_name = None
        self.sprite = os.path.os.path.dirname(os.path.realpath(sys.argv[0])) \
                      + '/Textures/' + '/player_sprite.png'
        self.obj_type = 'player'
        self.health = 100
        self.attack = 30


class Enemy_Grunt:
    """The basic Enemy Type"""


class Enemy_Boss:
    """The enemy boss type"""

    def __init__(self, enemy_name):
        self.boss_name = enemy_name
        self.obj_type = 'enemy'
        self.sprite_type = 'enemy_boss'
        self.health = 500

