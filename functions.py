# -*- coding: utf-8 -*-
"""
    File Name: functions.py
    Author: Ari Madian
    Created: October 4, 2017 3:30 PM
    Python Version: 3.6

    get_angle and project were taken from a pygame forum.
"""
from math import sin, cos, atan2, pi, sqrt

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

def player_center(player_pos, size):
    return int(player_pos[0] + (size[0] / 2)), int(player_pos[1] + (size[1] / 2))



def get_angle(origin, destination):
    """Returns angle in radians from origin to destination.
    This is the angle that you would get if the points were
    on a cartesian grid. Arguments of (0,0), (1, -1)
    return .25pi(45 deg) rather than 1.75pi(315 deg).
    """
    x_dist = destination[0] - origin[0]
    y_dist = destination[1] - origin[1]
    return atan2(-y_dist, x_dist) % (2 * pi)

def project(pos, angle, distance):
    """Returns tuple of pos projected distance at angle
    adjusted for pygame's y-axis.
    """
    return (pos[0] + (cos(angle) * distance),
            pos[1] - (sin(angle) * distance))

def distance(p1, p2):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

