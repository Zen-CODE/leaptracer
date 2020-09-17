"""
This module houses a minimal mixin class that provider a pre-touch crosshair
graphics for positioning of the hand for the LeapHand input provider.
"""
from kivy.core.window import Window
from kivy.graphics import Color, Line


class LeapHandOverlay:
    """
    This class handles the rendering of the pre-touch crosshairs for
    positioning the LeapHand prior to starting the touch event (via a grab).
    """
    def __init__(self, root):
        Window.bind(on_motion=self.on_motion)
        with root.canvas:
            Color(0.2, 1, 1, mode='hsv')
            self._hand_lines = [Line(), Line()]

    @staticmethod
    def get_pos(motion):
        """ Return the position in screen co-ordinates for the motion event."""
        return motion.sx * Window.width, motion.sy * Window.height

    def draw_crosshair(self, pos, cross_width):
        """ Draw the crosshairs indicating the hands current positions."""
        self._hand_lines[0].points = [
            pos[0] - cross_width, pos[1], pos[0] + cross_width, pos[1]]
        self._hand_lines[1].points = [
            pos[0], pos[1] - cross_width, pos[0], pos[1] + cross_width]

    def on_motion(self, widget, etype, motionevent):
        """Draw the crosshairs at the position of the hands."""
        cross_width = 6.0
        self.draw_crosshair(self.get_pos(motionevent), cross_width)


class LeapHandApp:
    """
    Mixin class for rendering a pre-touch crosshair graphic for positioning of
    the hand when using the LeapHand input provider.

    Usage
    =====

    When declaring your Kivy app, add this mixing as the superclas of your
    main application object. e.g.::

        from kivy.app import App


        class LeaptracerApp(LeapHandApp, App):
            ...

    """
    leaphand_overlay = None

    def on_start(self):
        self.leaphand_overlay = LeapHandOverlay(self.root)
        print(f"leaphandoverlay.py: on_start. Binding to {self.root}")
        return super().on_start()  # pylint: disable=no-member
