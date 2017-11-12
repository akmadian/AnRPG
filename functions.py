# -*- coding: utf-8 -*-
"""
    File Name: functions.py
    Author: Ari Madian
    Created: October 4, 2017 3:30 PM
    Python Version: 3.6
"""
import math
import numpy

def player_verts(player_pos, size):
    """Calulates the vertices of the player sprite"""

    verts = {'tl': player_pos,
             'tm': (int(player_pos[0] + (size[0] / 2)), int(player_pos[1])),
             'tr': (int(player_pos[0] + size[0]), int(player_pos[1])),

             'cl': (int(player_pos[0]), int(player_pos[1] + (size[1] / 2))),
             'cm': (int(player_pos[0] + (size[0] / 2)), int(player_pos[1] + (size[1] / 2))),
             'cr': (int(player_pos[0] + size[0]), int(player_pos[1] + (size[1] / 2))),

             'bl': (int(player_pos[0]), int(player_pos[1] + size[1])),
             'bm': (int(player_pos[0] + (size[0] / 2)), int(player_pos[1] + size[1])),
             'br': (int(player_pos[0] + size[0]), int(player_pos[1] + size[1]))}
    return verts


def projectile_angle(origin, mousepos):
    """"""
    side_lengths = numpy.subtract(mousepos, origin)
    degree = math.degrees(math.atan(side_lengths[0] / side_lengths[1]))
    abs_value = math.fabs(degree)
    if origin[0] < mousepos[0]:
        if origin[1] > mousepos[1]: return abs_value
        else: return 270 + abs_value
    if origin[0] > mousepos[0]:
        if origin[1] > mousepos[1]: return 90 + abs_value
        else: return 180 + abs_value


def projectile_position(proj_obj, curr_tick):
    """"""
    angle = proj_obj.angle
    ticks = curr_tick - proj_obj.tickmade


    vertical = math.sin(angle) * ticks
    horizontal = math.cos(angle) * ticks

    if proj_obj.mousepos['x'] > proj_obj.origin['x']:
        if proj_obj.mousepos['y'] > proj_obj.origin['y']:
            return vertical + proj_obj.origin['y'], horizontal + proj_obj.origin['x']
        else:
            return vertical - proj_obj.origin['y'], horizontal + proj_obj.origin['x']
    else:
        if proj_obj.mousepos['y'] > proj_obj.origin['y']:
            return vertical + proj_obj.origin['y'], horizontal - proj_obj.origin['x']
        else:
            return vertical - proj_obj.origin['y'], horizontal - proj_obj.origin['x']




'''
def projectile_rotation(origin, mousepos):
    """Calculates the rotation of a projectile object
    I'll probably make this based on math stuff at some point

    :param origin: Expects dict with the character postion at
                    the time of projectile creation
    :param mousepos: Expects dict with the mouse position at
                     the time of projectile creation
    :return: Degree rotation
    """
    # Vertical/ Horizontal Angles
    if origin['y'] + 103 == mousepos['y']:
        if origin['x'] < mousepos['x']: return '0'
        if origin['x'] > mousepos['x']: return '180'
    if origin['x'] + 56 == mousepos['x']:
        if origin['y'] < mousepos['y']: return '270'
        if origin['y'] > mousepos['y']: return '90'

    # Diagonal Angles
    if origin['x'] < mousepos['x']: # If mouse is to the right of player
        if origin['y'] < mousepos['y']: return '315'
        if origin['y'] > mousepos['y']: return '45'
    if origin['x'] > mousepos['x']: # If mouse is to the left of player
        if origin['y'] < mousepos['y']: return '225'
        if origin['y'] > mousepos['y']: return '135'
'''

if __name__ == '__main__': projectile_position(None, 225, 50)