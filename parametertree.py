from pyqtgraph.Qt import QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from PyQt5.QtCore import Qt, QEventLoop, QTimer
import numpy as np


class MyParamTree(ParameterTree):
    """The parameter tree widget that lives in the bottom of the main window.

    This is where the current parameters of the application live. When a parameter here is changed by ANY method
    (UI, gamepad, keyboard), this object sends a signal to the MainWindow to get forward to the salient thread/object.
    The values are initialized from the config parameter passed in when instantiating this object.

    Attributes:
        params: a nested dictionary which contains the visable and edit-able parameters during program run-time
        p: the actual parameter tree object that contains the values

    """
    paramChange = QtCore.pyqtSignal(object, object)  # MyParamTree outputs a signal with param and changes.

    def __init__(self, config):
        super().__init__()
        self.params = [
            {'name': 'Signal Design Parameters', 'type': 'group', 'children': [
                {'name': 'Toggle Output', 'type': 'bool', 'value': False, 'tip': "Toggle the output"},
                {'name': 'Voltage Multiplier', 'type': 'float', 'value': config.defaults['vmulti'], 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': config.defaults['freq'], 'step': 10, 'siPrefix': True, 'suffix': 'Hz'},
                {'name': 'Z-Phase', 'type': 'float', 'value': config.defaults['zphase'], 'step': 90},
                {'name': 'Field Camber', 'type': 'int', 'value': config.defaults['camber'], 'step': 1, 'siPrefix': True, 'suffix': '°'}
            ]},
            {'name': 'Calibration', 'type': 'group', 'children': [
                {'name': 'Output Mode', 'type': 'list', 'values': ['Normal', 'Calibration'], 'value': 'Normal'},
                {'name': 'Calibration X-Voltage Ampl.', 'type': 'float', 'value': config.defaults['calib_xamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name': 'Calibration Y-Voltage Ampl.', 'type': 'float', 'value': config.defaults['calib_yamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name': 'Calibration Z-Voltage Ampl.', 'type': 'float', 'value': config.defaults['calib_zamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name': 'Z-Coefficient', 'type': 'float', 'value': config.defaults['zcoeff'], 'step': 0.001}

            ]}
        ]

        # Create my parameter object and link it to methods
        self.p = Parameter.create(name='self.params', type='group', children=self.params)
        self.setParameters(self.p, showTop=False)

        self.p.sigTreeStateChanged.connect(self.sendChange)  # When the params change, send to method to emit.

        # Connect keyPresses
        self.setFocusPolicy(Qt.NoFocus)

        self.running_explode = False

    def sendChange(self, param, changes):
        self.paramChange.emit(param, changes)

    # Convienience methods for modifying parameter values.
    def getParamValue(self, child, branch='Signal Design Parameters'):
        """Get the current value of a parameter."""
        return self.p.param(branch, child).value()

    def setParamValue(self, child, value, branch='Signal Design Parameters'):
        """Set the current value of a parameter."""
        return self.p.param(branch, child).setValue(value)

    def stepParamValue(self, child, delta, branch='Signal Design Parameters'):
        """Change a parameter by a delta. Can be negative or positive."""
        param = self.p.param(branch, child)
        curVal = param.value()
        newVal = curVal + delta
        return param.setValue(newVal)

    def on_key(self, key):
        """ On a keypress on the plot widget, forward the keypress to the correct function below."""
        qtk = QtCore.Qt
        # Its necessary to have this func map because the key is simply an integer I need to check against
        # the key dictionary in QtCore.Qt.
        func_map ={
            qtk.Key_Left: self.Key_Left,
            qtk.Key_Right: self.Key_Right,
            qtk.Key_Up: self.Key_Up,
            qtk.Key_Down: self.Key_Down,
            qtk.Key_G: self.Key_G,
            qtk.Key_F: self.Key_F,
            qtk.Key_B: self.Key_B,
            qtk.Key_V: self.Key_V,
            qtk.Key_Q: self.Key_Q,
            qtk.Key_W: self.Key_W,
            qtk.Key_T: self.Key_T
        }
        func = func_map.get(key, lambda: 'Not bound yet')
        return func()


    def Key_Left(self):
        self.setParamValue('Z-Phase', 90)

    def Key_Right(self):
        self.setParamValue('Z-Phase', 270)

    def Key_Up(self):
        self.setParamValue('Z-Phase', 0)

    def Key_Down(self):
        self.setParamValue('Z-Phase', 180)

    def Key_G(self):
        self.stepParamValue('Frequency', 10)

    def Key_F(self):
        self.stepParamValue('Frequency', -10)

    def Key_B(self):
        self.stepParamValue('Field Camber', 10)

    def Key_V(self):
        self.stepParamValue('Field Camber', -10)

    def Key_Q(self):
        self.stepParamValue('Voltage Multiplier', -0.25)

    def Key_W(self):
        self.stepParamValue('Voltage Multiplier', 0.25)

    def Key_T(self):
        """Toggles the toggle value"""
        curbool = self.getParamValue('Toggle Output')
        setbool = not curbool
        self.setParamValue('Toggle Output', setbool)

    def twirl(self):
        """Rotate the z-phase 360 degrees in a given time."""
        runs = 5
        time_between_runs = 0.4
        time = 0.2  # time in seconds for the zphase to be moved around.
        steps = 10  # how many steps to divide twirl into
        time_between_steps = time / steps
        phase_increment = 360 / steps

        for _ in range(runs):
            z_phase = self.getParamValue('Z-Phase')
            for _ in range(steps):
                z_phase += phase_increment

                self.setParamValue('Z-Phase', z_phase % 360)  # change z-phase

                # sleep using PyQt5
                loop = QEventLoop()
                QTimer.singleShot(time_between_steps * 1000, loop.quit)
                loop.exec_()

            # Sleep between runs
            loop = QEventLoop()
            QTimer.singleShot(time_between_runs * 1000, loop.quit)
            loop.exec_()

    def wiggle(self):
        """Wiggle the wheel from a positive camber to negative camber to shear wheels apart."""
        num = 1  # number of wiggles
        time = 0.1  # time in seconds where the wheel completes a "wiggle" cycle
        steps = 2  # how many steps to divide one half of the wiggle into
        time_between_steps = time / steps

        camber = self.getParamValue('Field Camber')
        camber_increment = (2 * camber) / steps

        for _ in range(num):
            # Advance positive
            for _ in range(steps):
                camber -= camber_increment

                self.setParamValue('Field Camber', camber)  # change z-phase

                # sleep using PyQt5
                loop = QEventLoop()
                QTimer.singleShot(time_between_steps * 1000, loop.quit)
                loop.exec_()

            # Advance negative
            for _ in range(steps):
                camber += camber_increment

                self.setParamValue('Field Camber', camber)  # change z-phase

                # sleep using PyQt5
                loop = QEventLoop()
                QTimer.singleShot(time_between_steps * 1000, loop.quit)
                loop.exec_()

    def explode(self):
        """Explode the wheel by applying an orthogonal camber angle briefly."""
        camber = self.getParamValue("Field Camber")
        heading = self.getParamValue('Z-Phase')
        ortho = camber - 90
        time = 0.2

        self.setParamValue('Field Camber', ortho)
        if ortho > 91:
            self.setParamValue('Z-Phase', (heading - 180) % 360)
        # sleep using PyQt5
        loop = QEventLoop()
        QTimer.singleShot(time * 1000, loop.quit)
        loop.exec_()

        self.setParamValue('Field Camber', camber)
        if ortho > 91:
            self.setParamValue('Z-Phase', heading)

    def explode_toggle(self):
        time_between_explodes = 0.5
        self.running_explode = not self.running_explode
        while self.running_explode:
            self.explode()
            # wait
            loop = QEventLoop()
            QTimer.singleShot(time_between_explodes * 1000, loop.quit)
            loop.exec_()

    def switch_sides(self):
        """Explode the wheel by switching the rotation side."""
        camber = self.getParamValue("Field Camber")
        heading = self.getParamValue('Z-Phase')
        opposite = camber - 180
        time = 0.5

        self.setParamValue('Field Camber', opposite)
        self.setParamValue('Z-Phase', (heading - 180) % 360)
        # sleep using PyQt5
        loop = QEventLoop()
        QTimer.singleShot(time * 1000, loop.quit)
        loop.exec_()

        self.setParamValue('Field Camber', camber)
        self.setParamValue('Z-Phase', heading)

    def corkscrew(self):
        """Corkscrew motion."""
        time = 2.0  # time to complete one spiral
        forward_steps = 2
        first_turn_steps = 1
        backwards_steps = 1
        second_turn_steps = 1
        sub_turn_steps = 4  # must be even!
        steps = forward_steps + first_turn_steps + backwards_steps + second_turn_steps
        step_time = time / steps  # time for each step of the movement
        sub_turn_step_time = step_time / sub_turn_steps

        # Use camber of 10 degrees for original
        start_camber = 30
        heading = self.getParamValue('Z-Phase')

        # Move forward
        for step in range(forward_steps):
            self.setParamValue("Field Camber", start_camber)
            self.setParamValue("Z-Phase", heading)
            # sleep using PyQt5
            loop = QEventLoop()
            QTimer.singleShot(step_time * 1000, loop.quit)
            loop.exec_()

        # Make the first turn
        # I want to duck the camber angle down to 70 degrees then bring it back up for the backwards movement
        # At the same time, step the heading angle 180 degrees.
        camber = start_camber
        bow_camber = 80
        end_first_turn_heading = (heading - 180)
        camber_step_length = 2 * (bow_camber - start_camber) / sub_turn_steps
        heading_step_length = np.abs(heading - end_first_turn_heading) / sub_turn_steps

        # First half of movement, bow down to the high camber angle
        for step in range(sub_turn_steps // 2):
            camber += camber_step_length  # step camber
            heading = (heading - heading_step_length) % 360
            self.setParamValue('Field Camber', camber)  # set camber
            self.setParamValue('Z-Phase', heading)  # set heading
            # pause
            loop = QEventLoop()
            QTimer.singleShot(sub_turn_step_time * 1000, loop.quit)
            loop.exec_()

        # second half of movement, rise back up to starting camber
        for step in range(sub_turn_steps // 2):
            camber -= camber_step_length  # step camber
            heading = (heading - heading_step_length) % 360
            self.setParamValue('Field Camber', camber)  # set camber
            self.setParamValue('Z-Phase', heading)  # set heading
            # pause
            loop = QEventLoop()
            QTimer.singleShot(sub_turn_step_time * 1000, loop.quit)
            loop.exec_()

        # Move backward
        for step in range(backwards_steps):
            # wait
            loop = QEventLoop()
            QTimer.singleShot(step_time * 1000, loop.quit)
            loop.exec_()

        # Perform second turn
        for step in range(sub_turn_steps // 2):
            camber += camber_step_length  # step camber
            heading = (heading - heading_step_length) % 360
            self.setParamValue('Field Camber', camber)  # set camber
            self.setParamValue('Z-Phase', heading)  # set heading
            # pause
            loop = QEventLoop()
            QTimer.singleShot(sub_turn_step_time * 1000, loop.quit)
            loop.exec_()

        for step in range(sub_turn_steps // 2):
            camber -= camber_step_length  # step camber
            heading = (heading - heading_step_length) % 360
            self.setParamValue('Field Camber', camber)  # set camber
            self.setParamValue('Z-Phase', heading)  # set heading
            # pause
            loop = QEventLoop()
            QTimer.singleShot(sub_turn_step_time * 1000, loop.quit)
            loop.exec_()

    def on_gamepad_event(self, gamepadEvent):
        """
        Parses the incoming gamepad events and forwards it to the appropriate keybind function below.
        For ease and less repetition, some buttons are forwarded to the keyboard functions.
        Args:
            gamepadEvent (list): incoming list from the controller class of format ['button', val]. ex. ['LJOY', 45]
        """
        func_map = {
            'X': self.Key_F,
            'Y': self.Key_G,
            'B': self.Key_B,
            'A': self.Key_V,
            'LEFT_SHOULDER': self.Key_Q,
            'RIGHT_SHOULDER': self.Key_W,
            'LEFT_THUMB': self.Key_T,
            'LJOY': self.Joystick_Left,
            'START': self.explode,
            'BACK': self.explode_toggle
        }
        func = func_map.get(gamepadEvent[0], lambda: 'Not bound yet')
        if gamepadEvent[0] == 'LJOY':
            return func(gamepadEvent[1])
        else:
            return func()

    def Joystick_Left(self, degree):
        degree = 360 - degree  # convert joystick degrees to a zphase that makes sense
        self.setParamValue('Z-Phase', degree)

