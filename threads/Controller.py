from pyqtgraph.Qt import QtCore
from misc_functions import xy_to_cylindrical
from inputs import devices, DeviceManager, get_gamepad
from time import sleep


class ControllerThread(QtCore.QThread):
    """ A QThread which monitors the controller key presses and emits the events.

    Attributes:
        dead_zone: determines how far the joystick needs to be moved to register. default 10000
        running (bool): used to control the state of the run loop from outside this thread
    """
    newGamepadEvent = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.dead_zone = 10000
        self.running = False

        # Initialize variables to keep track of x and y
        self.x = 0
        self.y = 0

    def run(self):
        """Runs when the start method is called on the thread.

        First, an event is read from the joystick and filtered for:
        Key (digital button), and Absolute (analog button). For the analog joystick, the xy coordinates are converted
        using my function xy_to_cylindrical, located in misc_functions.py.

        Once the key is filtered and determined to be relevant, it emits a list with the event code and state using the
        defined newGamepadEvent signal. eg. ['BTN_WEST', 1] or ['LJOY', 47.25]

        """
        self.running = True

        # Try connecting to the gamepad
        try:
            self.gamepad = devices.gamepads[0]
        except IndexError:
            print('No controller connected.')
            self.gamepad = None

        if self.gamepad is not None:
            while self.running:
                self.process_available_events()

    def filter_event(self, event):
        """Filter the events and emit the salient ones.

        Args:
            event: event object from process_available_events

        Returns:
            nothing, but emits salient events to QThread signal
        """
        # Filter unused events
        if event.ev_type == 'Sync':
            return
        if event.ev_type == 'Misc':
            return
        # Buttons
        if event.ev_type == 'Key':
            if event.state == 1:
                # print(str(event.code), event.state)
                self.newGamepadEvent.emit([str(event.code), event.state])
                # QtCore.QThread.msleep(10)
        # Joystick
        elif event.ev_type == 'Absolute':
            if event.code == 'ABS_X':  # X-Axis of the joystick
                self.x = event.state
            elif event.code == 'ABS_Y':  # Y-Axis of the joystick
                self.y = event.state
            magnitude, degrees = xy_to_cylindrical(self.x, self.y)  # Convert to cylindrical
            if magnitude > self.dead_zone:  # If its not in the dead zone, emit to the signal
                # print(['LJOY', degrees])
                self.newGamepadEvent.emit(['LJOY', degrees])

    def process_available_events(self):
        """Read the events from inputs module read function."""

        try:
            events = self.gamepad.read()
        except EOFError:
            events = []

        for event in events:
            self.filter_event(event)

