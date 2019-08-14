from pyqtgraph.Qt import QtCore
from misc_functions import xy_to_cylindrical
from inputs import devices


class ControllerThread(QtCore.QThread):
    """
    A thread object which monitors the controller and emits the events.
    """
    newGamepadEvent = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.last_x = 0
        self.last_y = 0
        self.dead_zone = 5000

    def run(self):
        """
        This method runs when the thread is started. First, an event is read from the joystick and filtered for:
        Key (digital button), and Absolute (analog button). For the analog joystick, the xy coordinates are converted
        using my function xy_to_cylindrical.

        Emits:
            a list with the event code and state. ex. ['BTN_WEST', 1] or ['LJOY', 47.25]
        """
        try:
            gamepad = devices.gamepads[0]
        except IndexError:
            print('No controller connected.')
            gamepad = None
        last_x = 0
        last_y = 0
        dead_zone = 10000

        if gamepad is not None:
            while True:
                events = gamepad.read()
                event = events[0]
                # Buttons
                if event.ev_type == 'Key':
                    if event.state == 1:
                        print(str(event.code))
                        self.newGamepadEvent.emit([str(event.code), event.state])
                        QtCore.QThread.msleep(10)
                # Joystick
                elif event.ev_type == 'Absolute':  # If its an analog input
                    if event.code == 'ABS_X':
                        last_x = event.state
                    elif event.code == 'ABS_Y':
                        last_y = event.state
                    magnitude, degrees = xy_to_cylindrical(last_x, last_y)
                    if magnitude > dead_zone:
                        self.newGamepadEvent.emit(['LJOY', degrees])
                        # QtCore.QThread.msleep(10)


