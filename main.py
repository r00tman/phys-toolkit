import urwid
from sympy import *

import ErrorView
import DataView

class MainMenu:
    choices = [u"Data series", u"Residuals and expressions", u"Exit"]
    def menu(self, title, choices):
        body = [urwid.Text(title), urwid.Divider()]
        for c in choices:
            button = urwid.Button(c)
            urwid.connect_signal(button, 'click', MainMenu.item_chosen, [c, self])
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(button, args):
        choice, self= args
        if choice == MainMenu.choices[0]:
            orwid = self.main.original_widget
            dv = DataView.DataView(MainMenu.exit_program, self, orwid)
            self.main.original_widget = dv.top
        elif choice == MainMenu.choices[1]:
            orwid = self.main.original_widget
            ev = ErrorView.ErrorView(MainMenu.exit_program, self, orwid) 
            self.main.original_widget = ev.top
        elif choice == MainMenu.choices[2]:
            raise urwid.ExitMainLoop()
    
    def exit_program(button, args):
        self, original_widget = args
        #raise urwid.ExitMainLoop()
        self.main.original_widget = original_widget
    
    def __init__(self):
        self.main = urwid.Padding(self.menu(u'Select activity', MainMenu.choices), left=2,right=2)
        self.top = urwid.Overlay(self.main, urwid.SolidFill(u'\m{MEDIUM SHADE}'), align='center', width=('relative', 80), valign='middle', height=('relative', 80), min_width=20, min_height=9)

mm = MainMenu()
urwid.MainLoop(mm.top, palette=[('reserved', 'standout', '')]).run()
