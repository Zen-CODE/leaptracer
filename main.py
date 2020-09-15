'''
Touch Tracer Line Drawing Demonstration
=======================================

This demonstrates tracking each touch registered to a device. You should
see a basic background image. When you press and hold the mouse, you
should see cross-hairs with the coordinates written next to them. As
you drag, it leaves a trail. Additional information, like pressure,
will be shown if they are in your device's touch.profile.

.. note::

   A function `calculate_points` handling the points which will be drawn
   has by default implemented a delay of 5 steps. To get more precise visual
   results lower the value of the optional keyword argument `steps`.

This program specifies an icon, the file icon.png, in its App subclass.
It also uses the particle.png file as the source for drawing the trails which
are white on transparent. The file leaptracer.kv describes the application.

The file android.txt is used to package the application for use with the
Kivy Launcher Android application. For Android devices, you can
copy/paste this directory into /sdcard/kivy/leaptracer on your Android device.

'''
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException, Line
from random import random
from math import sqrt
from kivy.core.window import Window
from kivy.properties import BooleanProperty


def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o


class Leaptracer(FloatLayout):
    """
    The Main layout file. For styling and contents, please see the leaptracer.kv
    file.
    """
    draw_motion = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_motion=self.on_motion)
        self._hand_lines = None

    @staticmethod
    def get_pos(motion):
        """ Return the position in screen co-ordinates for the motion event."""
        return motion.sx * Window.width, motion.sy * Window.height

    def on_motion(self, widget, etype, motionevent):
        cross_width = 6.0
        pos = self.get_pos(motionevent)
        if self._hand_lines is None:
            with self.canvas:
                Color(0.2, 1, 1, mode='hsv')
                self._hand_lines = [
                    Line(points=[pos[0] - cross_width, pos[1],
                                 pos[0] + cross_width, pos[1]]),
                    Line(points=[pos[0], pos[1] - cross_width,
                                 pos[0], pos[1] + cross_width])]
        else:
            self._hand_lines[0].points = [
                pos[0] - cross_width, pos[1],
                pos[0] + cross_width, pos[1]]
            self._hand_lines[1].points = [
                pos[0], pos[1] - cross_width,
                pos[0], pos[1] + cross_width]

    def on_touch_down(self, touch):
        if self.draw_motion:
            win = self.get_parent_window()
            ud = touch.ud
            ud['group'] = g = str(touch.uid)
            pointsize = 5
            if 'pressure' in touch.profile:
                ud['pressure'] = touch.pressure
                pointsize = (touch.pressure * 100000) ** 2
            ud['color'] = random()

            with self.canvas:
                Color(ud['color'], 1, 1, mode='hsv', group=g)
                ud['lines'] = [
                    Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                    Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                    Point(points=(touch.x, touch.y), source='particle.png',
                          pointsize=pointsize, group=g)]

            ud['label'] = Label(size_hint=(None, None))
            self.update_touch_label(ud['label'], touch)
            self.add_widget(ud['label'])
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self or self.draw_motion:
            ud = touch.ud
            ud['lines'][0].pos = touch.x, 0
            ud['lines'][1].pos = 0, touch.y

            index = -1

            while True:
                try:
                    points = ud['lines'][index].points
                    oldx, oldy = points[-2], points[-1]
                    break
                except Exception:
                    index -= 1

            points = calculate_points(oldx, oldy, touch.x, touch.y)
            if points:
                try:
                    lp = ud['lines'][-1].add_point
                    for idx in range(0, len(points), 2):
                        lp(points[idx], points[idx + 1])
                except GraphicException:
                    pass

            ud['label'].pos = touch.pos
            self.update_touch_label(ud['label'], touch)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current:
            touch.ungrab(self)
            ud = touch.ud
            self.canvas.remove_group(ud['group'])
            self.remove_widget(ud['label'])
        return super().on_touch_up(touch)

    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20


class LeaptracerApp(App):
    title = 'Leaptracer'
    icon = 'icon.png'

    def build(self):
        return Leaptracer()

    def on_pause(self):
        return True


if __name__ == '__main__':
    LeaptracerApp().run()
