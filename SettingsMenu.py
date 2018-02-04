from appJar import gui
import configparser
from sys import argv
from os import path

SettingsMenu = gui()
SettingsMenu.setFont(12)
SettingsMenu.setTitle('AnRPG Settings')
SettingsMenu.setIcon(path.os.path.dirname(path.realpath(argv[0])) + '/Assets/' + '/projectiles' + '/blue_projectile.png')
config = configparser.ConfigParser()
config.read('config.ini')

reread_config = False

def refresh_settings():
    global reread_config
    print(SettingsMenu.getAllCheckBoxes())
    for setting, value in SettingsMenu.getAllCheckBoxes().items():
        config.set('DEFAULT', setting, str(value))
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    reread_config = True
    SettingsMenu.stop()


def populate_settings_window():
    SettingsMenu.addCheckBox('Player Godmode')
    SettingsMenu.addCheckBox('Render Player Vertices')
    SettingsMenu.addCheckBox('Render Hitboxes')
    SettingsMenu.addCheckBox('Enable Enemy Spawning')


    for setting in config['DEFAULT']:
        if config.getboolean('DEFAULT', setting) is True:
            SettingsMenu.setCheckBox(setting.title(), callFunction=False)

    SettingsMenu.addButton('Save and Exit', refresh_settings)


populate_settings_window()
SettingsMenu.go()
