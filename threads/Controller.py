from pyqtgraph.Qt import QtCore
from misc_functions import xy_to_cylindrical
from inputs import devices


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

    def run(self):
        """Runs when the start method is called on the thread.

        First, an event is read from the joystick and filtered for:
        Key (digital button), and Absolute (analog button). For the analog joystick, the xy coordinates are converted
        using my function xy_to_cylindrical, located in misc_functions.py.

        Once the key is filtered and determined to be relevent, it emits a list with the event code and state using the
        defined newGamepadEvent signal. eg. ['BTN_WEST', 1] or ['LJOY', 47.25]

        """
        self.running = True

        # Try connecting to the gamepad
        try:
            gamepad = devices.gamepads[0]
        except IndexError:
            print('No controller connected.')
            gamepad = None

        # Initialize variables to keep track of x and y
        x = 0
        y = 0

        if gamepad is not None:
            while self.running:
                # QtCore.QThread.msleep(1)
                events = None
                events = gamepad.read()
                event = events[0]

                # Buttons
                if event.ev_type == 'Key':
                    if event.state == 1:
                        # print(str(event.code))
                        self.newGamepadEvent.emit([str(event.code), event.state])
                        QtCore.QThread.msleep(10)
                # Joystick
                elif event.ev_type == 'Absolute':
                    if event.code == 'ABS_X':  # X-Axis of the joystick
                        x = event.state
                    elif event.code == 'ABS_Y':  # Y-Axis of the joystick
                        y = event.state
                    magnitude, degrees = xy_to_cylindrical(x, y)  # Convert to cylindrical
                    if magnitude > self.dead_zone:  # If its not in the dead zone, emit to the signal
                        self.newGamepadEvent.emit(['LJOY', degrees])
                        # QtCore.QThread.msleep(10)


