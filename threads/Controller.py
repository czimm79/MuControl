from pyqtgraph.Qt import QtCore
from misc_functions import xy_to_cylindrical
from time import sleep
import XInput as xi


class ControllerThread(QtCore.QThread):
    """ A QThread which monitors the controller key presses and emits the events.

    Attributes:
        SLEEP (float): the time that the while loop pauses while checking controller events. Higher sleep constants
            equals better performance.
        running (bool): used to control the state of the run loop from outside this thread
    """
    newGamepadEvent = QtCore.pyqtSignal(object)

    def __init__(self, sleep_constant=0.01):
        super().__init__()

        self.running = False
        self.sleep_constant = sleep_constant
        # Initialize variables to keep track of x and y
        self.x = 0
        self.y = 0

    def run(self):
        """
        """
        self.running = True

        # Try connecting to the gamepad
        connected = xi.get_connected()

        if any(controller is True for controller in connected):
            print("A controller is connected!")
        else:
            print("No controller connected.")
            self.running = False

        # Start the process loop
        while self.running:
            sleep(self.sleep_constant)
            events = xi.get_events()
            for event in events:
                self.filter_events(event)

    def filter_events(self, event):
        """Filter the events and emit the salient ones.

        Args:
            event: event dictionary with format: {'user_index': 1, 'type': 4, 'button': 'X', 'button_id': 16384}
                Type 4 = Button Pressed, Type 6 = Stick Moved

        Returns:
            nothing, but emits salient events to QThread signal
        """
        # Filter unused events
        if event.type == 3:  # Button is released, won't track this
            return

        # Buttons
        if event.type == 4:
            print(event.button)
            self.newGamepadEvent.emit([event.button, 1])
            # QtCore.QThread.msleep(10)

        # Joystick
        elif event.type == 6:
            if event.dir[0] != 0.00 and event.dir[1] != 0.0:  # Ignore signal that comes when joystick is let go
                self.x, self.y = event.dir

            magnitude, degrees = xy_to_cylindrical(self.x, self.y)  # Convert to cylindrical
            self.newGamepadEvent.emit(['LJOY', degrees])



