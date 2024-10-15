"""UI Components Module"""
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.properties import ListProperty

class HoverButton(ButtonBehavior, Label):
    text_color = ListProperty([0.5, 0.5, 0.5, 1])

    def __init__(self, **kwargs):
        super(HoverButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = self.to_widget(*args[1])
        if not self.collide_point(*pos):
            self.text_color = [0.5, 0.5, 0.5, 1]  # Dimmed
        else:
            self.text_color = [1, 1, 1, 1]  # Brighten on hover

class HoverImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(HoverImage, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.collide_point(self.to_widget(*args[1])):
            self.size = [170, 80]  # Correct assignment
        else:
            self.size = [200, 100]  # Correct assignment
