"""
This module houses a minimal mixin class that provider a pre-touch crosshair
graphics for positioning of the hand for the LeapHand input provider.
"""


class LeapHandApp:
    """
    Mixin class for rendering a pre-touch crosshair graphic for positioning of
    the hand when using the LeapHand input provider.
    """

    def on_start(self):
        print(f"Calling LeapHandApp.on_start. root = {self.root}")
        return super().on_start()  # pylint: disable=no-member
