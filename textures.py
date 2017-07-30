import os
import sys


class Textures:
    textures_path = os.path.dirname(os.path.realpath(sys.argv[0])) + \
                    '/Textures/'

    # Terrain
    grass = textures_path + 'grass_path_top.png'
    stone = textures_path + 'stone.png'
    stone_brick = textures_path + 'stonebrick.png'
    gravel = textures_path + 'gravel.png'
    water = textures_path + 'lapis_block.png'