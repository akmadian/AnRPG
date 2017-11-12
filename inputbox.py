# by Timothy Downs, inputbox written for my map editor
# Modified by Ari Madian for python 3.x and bad word filtering

# This program needs a little cleaning up
# It ignores the shift key
# And, for reasons of my own, this program converts "-" to "_"

# A program to get user input, allowing backspace etc
# shown in a box in the middle of the screen
# Called by:
# import inputbox
# answer = inputbox.ask(screen, "Your name")
#
# For bad word filtering, just modify the bad_words_file path to get
#   your text file of choice.
#
# Only near the center of the screen is blitted to

import pygame
import pygame.font
import pygame.event
import pygame.draw
import os
import sys
from pygame.locals import *


bad_words_file = os.path.os.path.dirname(os.path.realpath(sys.argv[0])) \
                 + '/bad_words.txt'

def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass


def display_box(screen, message, fontpath):
    "Print a message in a box in the middle of the screen"
    fontobject = fontpath
    '''
    pygame.draw.rect(screen, (0, 0, 0),
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 10,
                      500, 40), 0)
    pygame.draw.rect(screen, (255, 255, 255),
                     ((screen.get_width() / 2) - 102,
                      (screen.get_height() / 2) - 12,
                      400, 40), 1)
                      '''
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                    ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


def ask(screen, question, font):
    "ask(screen, question) -> answer"
    pygame.font.init()
    current_string = []
    display_box(screen, question + ": " + "".join(current_string), font)
    while 1:
        inkey = get_key()
        if inkey == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == K_RETURN:
            file = open(bad_words_file, 'r').readlines()
            if "".join(current_string) in [thing[:-1] for thing in file]:
                current_string = []
            else:
                break
        elif inkey == K_MINUS:
            current_string.append("_")
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ": " + "".join(current_string), font)
    return "".join(current_string)


def main():
    screen = pygame.display.set_mode((320, 240))
    print(ask(screen, "Name") + " was entered")


if __name__ == '__main__': main()
