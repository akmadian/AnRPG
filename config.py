"""
AnRPG Config File

Notes -
    Window Settings - Lots of stuff is hard coded to the 1200x800 value
                      in this config file, you can change it, but textures,
                      sprite spawn positions, and sprite sizes will not change.
"""
## Rendering
render_player_verts    = False
render_hitboxes        = True


## Window Settings
window_width  = 1300
window_height = 800


## Misc
mine_health            = 30
mine_damage            = 50
healthpack_heal_amount = 25
healthpack_create_freq = 500
shield_create_freq     = 600
dmgup_create_freq      = 450
max_enemy_boss         = 2
max_enemy_small        = 3
max_healthpacks        = 2
max_dmgup              = 1
dmgup_lifespan         = 160
dmgup_effect_amount    = 40
max_shield             = 0
shield_lifespan        = 150

## Projectile Attack Packages
#                 (damage, proj_speed, proj_lifepan)
player_atk1      = [30    , 10        , 140]
player_atk2      = [45    , 8         , 130]
enemy_small_atk1 = (10    , 10        , 120)
enemy_small_atk2 = (20    , 6         , 120)
enemy_boss_atk1  = (25    , 9         , 100)
enemy_boss_atk2  = (35    , 6         , 80)


##### Player #####
player_health               = 100
player_starting_x           = 100
player_starting_y           = 100
player_movespeed_vertical   = 13
player_movespeed_horizontal = 13
player_godmode              = True


##### Enemies #####
enemy_small_create_freq = 300 # Lower to spawn more often
enemy_boss_create_freq  = 800
enable_enemy_spawning   = True

## Small Enemies
enemy_small_health       = 150
enemy_small_atk1_freq    = 45  # Lower to attack more often
enemy_small_atk2_freq    = 20
enemy_small_score_val    = 30
enemy_small_move_dict    = {'x': {'min': 3, 'max': 9},
                            'y': {'min': 3, 'max': 9},
                            'ticks_to_move': 2}

## Boss Enemies
enemy_boss_health           = 300
enemy_boss_atk1_freq        = 50
enemy_boss_atk2_freq        = 80
enemy_boss_score_val        = 70
enemy_boss_move_properties  = {'x': {'min': 5, 'max': 12},
                               'y': {'min': 5, 'max': 12},
                               'ticks_to_move': 3}


## Generation ##
minmax_obstacles_perroom = (1, 4)
room_height = window_height
room_width  = window_width

