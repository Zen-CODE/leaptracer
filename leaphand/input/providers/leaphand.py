'''
Leap Motion - Hand only
=======================

This module provides access to the hand objects generated by the
LeapMotion input provider. The provider generates
:class:`~kivy.input.motionevent.MotionEvent`\s based
on the hand positions within the Leap Interaction box.

.. include:: ../../doc/sources/leapmotion.rst

LeapHand Mechanics
------------------

In order to initiate the touch gesture, the `LeapHand` uses the grab
gesture. A grab initiates :meth:`~kivy.core.window.WindowBase.on_touch_down`,
:meth:`~kivy.core.window.WindowBase.on_touch_move` and
:meth:`~kivy.core.window.WindowBase.on_touch_up` events.
'''

__all__ = ('LeapHandEventProvider', 'LeapHandEvent')

from collections import deque
from kivy.logger import Logger
from kivy.input.provider import MotionEventProvider
from kivy.input.factory import MotionEventFactory
from kivy.input.motionevent import MotionEvent

_LEAP_QUEUE = deque()

Leap = InteractionBox = None


def normalize(value, minimum, maximum):
    """Convert the *value* from leapmotion coordinate system to a value between
    o and 1.
    """
    return (value - minimum) / float(maximum - minimum)


class LeapHandEvent(MotionEvent):
    def __init__(self, device, id, args, is_touch, is_right):
        super().__init__(device, id, args)
        self.is_touch = is_touch
        self.hand = "right" if is_right else "left"

    def depack(self, args):
        super(LeapHandEvent, self).depack(args)
        if args[0] is None:
            return
        self.profile = ('pos', 'pos3d', 'pressure')
        x, y, z = args
        self.sx = normalize(x, -100, 150)
        self.sy = normalize(y, 80, 400)
        self.sz = normalize(z, -350, 350)
        self.z = z  # Ranges from 0 (directly above) to about 300
        norm = normalize(z, 0, 300)
        norm = 0 if norm <= 0 else min(norm, 1)
        self.pressure = 1 - norm # Invert, so pressure closer to screen
        print(f"pressure = {self.pressure}")


class LeapHandEventProvider(MotionEventProvider):

    def start(self):
        # Don't import at the start, or the error will be displayed
        # for users who don't have Leap
        global Leap, InteractionBox
        import Leap
        from Leap import InteractionBox

        class LeapHandListener(Leap.Listener):

            def on_init(self, controller):
                Logger.info('leaphand: Initialized')

            def on_connect(self, controller):
                Logger.info('leaphand: Connected')

            def on_disconnect(self, controller):
                Logger.info('leaphand: Disconnected')

            def on_frame(self, controller):
                frame = controller.frame()
                _LEAP_QUEUE.append(frame)

            def on_exit(self, controller):
                pass

        self.touches = {}
        self.listener = LeapHandListener()
        self.controller = Leap.Controller(self.listener)

    def update(self, dispatch_fn):
        try:
            while True:
                frame = _LEAP_QUEUE.popleft()
                events = self.process_frame(frame)
                for ev in events:
                    dispatch_fn(*ev)
        except IndexError:
            pass

    def process_frame(self, frame):
        events = []
        touches = self.touches
        available_uid = []
        for hand in frame.hands:
            is_touch = bool(hand.grab_strength > 0.75)
            uid = hand.id
            available_uid.append(uid)
            position = hand.palm_position
            args = (position.x, position.y, position.z)
            if uid not in touches:
                touch = LeapHandEvent(
                    self.device, uid, args, is_touch, hand.is_right)
                events.append(('begin', touch))
                touches[uid] = touch
            else:
                touch = touches[uid]
                if touch.is_touch != is_touch:
                    # Switched from a touch to non-touch event
                    events.append(('end', touch))
                    del touches[uid]
                else:
                    touch.move(args)
                    events.append(('update', touch))
        for key in list(touches.keys())[:]:
            if key not in available_uid:
                events.append(('end', touches[key]))
                del touches[key]
        return events


# registers
MotionEventFactory.register('leaphand', LeapHandEventProvider)
