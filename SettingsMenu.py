import tkinter as tk
import config

class SettingsMenu(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        #Player God Mode
        button_pgm = CheckBox(self.not_option, config.player_godmode)
        self.pgm = tk.Checkbutton(self, variable=button_pgm.setting, command=button_pgm.on_change, text='Player Godmode')
        if button_pgm.setting: self.pgm.select()
        self.pgm.pack(side='top')



    @staticmethod
    def not_option(parent):
        print(parent.setting)
        parent.setting = not parent.setting
        print(parent.setting)

class CheckBox(tk.Checkbutton):
    def __init__(self, callback, value):
        tk.Checkbutton.__init__(self)
        self.setting = value
        self.callback = callback

    def on_change(self):
        self.callback(self)

root = tk.Tk()
app = SettingsMenu(master=root)
app.mainloop()