from pyqtgraph.Qt import QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from PyQt5.QtCore import Qt
import numpy as np
from misc_functions import qtsleep

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
                {'name': 'Field Camber', 'type': 'int', 'value': config.defaults['camber'], 'step': 1, 'siPrefix': True, 'suffix': '°'},
                {'name': 'Swarm Mode', 'type': 'list', 'values': ['Rolling', 'Corkscrew', 'Flipping', 'Switchback'], 'value': 'Rolling'}
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

    # Convenience methods for modifying parameter values.
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
            qtk.Key_T: self.Key_T,
            qtk.Key_U: self.Key_U
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

    def Key_U(self):
        self.toggle_swarm()

    def explode(self):
        """Explode the wheel by applying an orthogonal camber angle briefly."""
        camber = self.getParamValue("Field Camber")
        heading = self.getParamValue('Z-Phase')
        ortho = camber - 90
        time = 0.2  # default 0.2

        # Tilt
        self.setParamValue('Field Camber', ortho)
        if np.abs(ortho) > 91:
            self.setParamValue('Z-Phase', (heading - 180) % 360)

        qtsleep(time)  # sleep using PyQt5


        # Reset
        self.setParamValue('Field Camber', camber)
        if np.abs(ortho) > 91:
            self.setParamValue('Z-Phase', heading)

    def toggle_explode(self):
        time_between_explodes = 0.5  # default 0.5
        self.running_explode = not self.running_explode
        while self.running_explode:
            self.explode()

            qtsleep(time_between_explodes)  # wait


    def switchback(self, time, driving_heading, wiggle_angle):
        """Switchback swarm execution code.

        Args:
            time (float): time constant between each turn
            driving_heading (int): uphill direction, overall movement direction
            wiggle_angle (int): deviation from centerline, determines angle of switchbacks
        """
        
        # turn left
        new_heading_1 = (driving_heading - wiggle_angle) % 360
        self.setParamValue('Z-Phase', new_heading_1)
        qtsleep(time)  # sleep using PyQt5

        # turn right
        new_heading_2 = (driving_heading + wiggle_angle) % 360
        self.setParamValue('Z-Phase', new_heading_2)
        qtsleep(time)

    def toggle_switchback(self):
        """Toggle the switchback field."""
        time_between_turn = 0.2
        wiggle_angle = 35

        self.running_explode = not self.running_explode
        driving_heading = self.getParamValue('Z-Phase')
        while self.running_explode:
            self.switchback(time_between_turn, driving_heading, wiggle_angle)

            # After running climb at least once, the wheel is currently in `right` formation. To update the driving heading, we'll
            # read what it is now, and subtract the wiggle angle.
            # driving_heading = (self.getParamValue('Z-Phase') - wiggle_angle) % 360

            # If there has been a change to the z-phase from the user, update the driving heading.
            if driving_heading != (self.getParamValue('Z-Phase') - wiggle_angle) % 360:
                driving_heading = self.getParamValue('Z-Phase')

        # reset back to original heading
        self.setParamValue('Z-Phase', driving_heading)


    def my_corkscrew(self):
        """My version of the corkscrew motion, described in signal_sandbox notebook."""
        print('running corkscrew')
        z_start = self.getParamValue('Z-Phase')
        camber = self.getParamValue('Field Camber')
        camber_max = 70
        total_steps = 10  # Must be an even number
        camber_half_steps = (camber_max - camber) / (total_steps // 2)

        total_time = 1.0
        step_time = total_time / total_steps
        alpha = 0.4
        beta = total_time - alpha
        a = 360 / (2 * beta + alpha)

        time = np.linspace(0, total_time, num=total_steps)

        for seconds in time:  
            # Calculate z_phase given current time
            if seconds <= alpha:
                z_phase = a * seconds + z_start
            elif seconds > alpha:
                z_phase = 2 * a * seconds - a * alpha + z_start
            else:
                print('Something went terribly wrong with the corkscrew code.')

            # Calculate camber angle
            if seconds <= total_time / 2: # first half of time steps, bow down camber
                camber += camber_half_steps
            elif seconds > total_time / 2: # second half, rise up
                camber -= camber_half_steps

            print(z_phase)
            print(camber)
            self.setParamValue('Z-Phase', z_phase % 360)  # set z-phase
            self.setParamValue('Field Camber', camber)  # set camber

            # Wait
            qtsleep(step_time)

    def toggle_my_corkscrew(self):
        time_between_explodes = 0.01
        self.running_explode = not self.running_explode
        while self.running_explode:
            self.my_corkscrew()
            
            qtsleep(time_between_explodes)  # wait

        
    def toggle_swarm(self):
        swarm = self.getParamValue('Swarm Mode')

        if swarm == 'Corkscrew':
            self.toggle_my_corkscrew()
        elif swarm == 'Flipping':
            self.toggle_explode()
        elif swarm == 'Switchback':
            self.toggle_switchback()
        elif swarm == 'Rolling':
            return


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
            'START': self.toggle_swarm
            # 'BACK': self.toggle_my_corkscrew
        }
        func = func_map.get(gamepadEvent[0], lambda: 'Not bound yet')
        if gamepadEvent[0] == 'LJOY':
            return func(gamepadEvent[1])
        else:
            return func()

    def Joystick_Left(self, degree):
        degree = 360 - degree  # convert joystick degrees to a zphase that makes sense
        self.setParamValue('Z-Phase', degree)

