"""
This module houses a minimal mixin class that provider a pre-touch crosshair
graphics for positioning of the hand for the LeapHand input provider.
"""
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.factory import Factory
from textwrap import dedent


Builder.load_string(dedent("""
<LeapHandCrosshair@Widget>:
    cross_color: [0.2, 1, 1, 1]
    size: 12.0, 12.0
    pos_hint: {}
    size_hint: [None, None]
    canvas:
        Color:
            rgba: self.cross_color
        Line:
            width: 2
            points: self.x, self.y + 0.5 * self.height, self.right, self.y + 0.5 * self.height  # noqa: E501
        Line:
            width: 2
            points: self.x + 0.5 * self.width, self.y, self.x + 0.5 * self.width, self.top
"""))


class LeapHandOverlay:
    """
    This class handles the rendering of the pre-touch crosshairs for
    positioning the LeapHand prior to starting the touch event (via a grab).
    """
    def __init__(self, root):
        Window.bind(on_motion=self.on_motion)
        self._crosshairs = {}
        self.root = root

    def _get_crosshair(self, hand, is_touch):
        """Return the LeapHandCrossHair widget for displaying the position."""
        widget = self._crosshairs.get(hand)
        if widget is None:
            widget = Factory.LeapHandCrosshair()
            self._crosshairs[hand] = widget
            self.root.add_widget(widget)
        widget.cross_color = [0.2, 1, 0, 1] if is_touch else \
            [0.5, 0.5, 0.5, 0.75]
        return widget

    @staticmethod
    def get_pos(motion):
        """ Return the position in screen co-ordinates for the motion event."""
        return motion.sx * Window.width, motion.sy * Window.height

    def place_crosshair(self, pos, hand, is_touch):
        """ Draw the crosshairs indicating the hands current positions."""
        widget = self._get_crosshair(hand, is_touch)
        widget.pos = pos[0] - 0.5 * widget.width, \
            pos[1] - 0.5 * widget.height

    def on_motion(self, widget, etype, motionevent):
        """Draw the crosshairs at the position of the hands."""
        if hasattr(motionevent, "hand"):
            self.place_crosshair(
                self.get_pos(motionevent),
                motionevent.hand,
                motionevent.is_touch)


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
