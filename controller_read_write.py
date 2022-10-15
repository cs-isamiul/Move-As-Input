from inputs import get_gamepad
import vgamepad as vg
import math
import threading
import time
import json

# Import buttons
buttons = {}
with open("buttons.json") as buttons:
    buttons = json.load(buttons)

# Create virtual gamepad
gamepad = vg.VX360Gamepad()

# Function to change button state
def change_vg_button(button, value):
    if(value > 0):
        gamepad.press_button(button=int(buttons[button], 16))
    else:
        gamepad.release_button(button=int(buttons[button], 16))

    gamepad.update()
    # print("Value to change is ", button, "Value passed in is ", value)

def change_vg_thumbstick(trigger, value_x, value_y=0):
    if(trigger == "left_trigger"):
        gamepad.left_trigger(value_x)
    elif(trigger == "right_trigger"):
        gamepad.right_trigger(value_x)
    elif(trigger == "left_joystick"):
        gamepad.left_joystick_float(x_value_float=value_x, y_value_float=value_y)
    elif(trigger == "right_joystick"):
        gamepad.right_joystick_float(x_value_float=value_x, y_value_float=value_y)
    gamepad.update()


# Below We are reading xbox inputs
class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                    change_vg_thumbstick("left_joystick", self.LeftJoystickX, self.LeftJoystickY)
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                    change_vg_thumbstick("left_joystick", self.LeftJoystickX, self.LeftJoystickY)
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                    change_vg_thumbstick("right_joystick", self.RightJoystickX, self.RightJoystickY)
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                    change_vg_thumbstick("right_joystick", self.RightJoystickX, self.RightJoystickY)
                elif event.code == 'ABS_Z':
                    change_vg_thumbstick("left_trigger", event.state)
                elif event.code == 'ABS_RZ':
                    change_vg_thumbstick("right_trigger", event.state)
                elif event.code == 'BTN_TL':
                    change_vg_button("left_shoulder", event.state)
                elif event.code == 'BTN_TR':
                    change_vg_button("right_shoulder", event.state)
                elif event.code == 'BTN_SOUTH':
                    change_vg_button("A", event.state)
                elif event.code == 'BTN_NORTH':
                    change_vg_button("Y", event.state)
                elif event.code == 'BTN_WEST':
                    change_vg_button("X", event.state)
                elif event.code == 'BTN_EAST':
                    change_vg_button("B", event.state)
                elif event.code == 'BTN_THUMBL':
                    change_vg_button("left_thumb", event.state)
                elif event.code == 'BTN_THUMBR':
                    change_vg_button("right_thumb", event.state)
                elif event.code == 'BTN_SELECT':
                    change_vg_button("start", event.state)
                elif event.code == 'BTN_START':
                    change_vg_button("back", event.state)
                elif event.code == 'ABS_HAT0Y':
                    if(event.state < 0):
                        change_vg_button("up", 1)
                    elif(event.state > 0):
                        change_vg_button("down", 1)
                    else:
                        change_vg_button("down", 0)
                        change_vg_button("up", 0)
                elif event.code == 'ABS_HAT0X':
                    if(event.state > 0):
                        change_vg_button("right", 1)
                    elif(event.state < 0):
                        change_vg_button("left", 1)
                    else:
                        change_vg_button("right", 0)
                        change_vg_button("left", 0)




if __name__ == '__main__':
    joy = XboxController()
    while True:
        time.sleep(.1)