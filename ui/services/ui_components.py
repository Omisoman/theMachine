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

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        widget_pos = self.to_widget(*pos)
        if not self.collide_point(*widget_pos):
            self.text_color = [0.5, 0.5, 0.5, 1]  # Dimmed
        else:
            self.text_color = [1, 1, 1, 1]  # Brighten on hover


class HoverImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(HoverImage, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        widget_pos = self.to_widget(*pos)
        if not self.collide_point(*widget_pos):
            self.size = [170, 80]  # Default size
        else:
            self.size = [200, 100]  # Enlarged on hover
