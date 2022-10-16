from inputs import get_gamepad
import vgamepad as vg
import math
import threading
import time
import json
import asyncio
import websockets
import socket
from base64 import b64decode

# Variables filled by server
lastCouple = [0,0,0,0,0,0]
limit = -1.3

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
        gamepad.left_joystick(x_value=0, y_value=0)
        for i in range(0, len(lastCouple)):
            if(lastCouple[i] < limit):
                gamepad.left_joystick_float(x_value_float=value_x, y_value_float=value_y)
                break
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

# Below is the code for the server
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def print_server_info():
    hostname = socket.gethostname()
    IPAddr = get_ip()
    print("Your Computer Name is: " + hostname)
    print("Your Computer IP Address is: " + IPAddr)
    print(
        "* Enter {0}:5000 in the app.\n* Press the 'Set IP Address' button.\n* Select the sensors to stream.\n* Update the 'update interval' by entering a value in ms.".format(IPAddr))

def process_values(y,z):
    avg_z = 1.614977
    avg_y = -7.93195
    std_z = 3.441466
    std_y = 5.032324

    norm_z = (z-avg_z)/std_z
    norm_y = (y-avg_y)/std_y
    return (norm_z/norm_y)

async def echo(websocket, path):
    index = 0
    print(">>>>>>>>>>>>Starting<<<<<<<<<<<<")
    async for message in websocket:
        if path == '/accelerometer':
            data = await websocket.recv()
            jsonData = json.loads(data)
            y = float(jsonData["y"])
            z = float(jsonData["z"])
            
            test_value = process_values(y,z)
            # state = ">>>>>>>>>><<<<<<<<<<"
            # if(test_value < limit):
            #     state = "moving"
            # else:
            #     for i in range(0, len(lastCouple)):
            #         if(lastCouple[i] < limit):
            #             state = "running"
            #             break
            
            lastCouple[index] = test_value
            index += 1
            if(index >= len(lastCouple)):
                index = 0
            # print(state)
            # print(data)
            # f = open("accelerometer.txt", "a")
            # f.write(data+"\n")

if __name__ == '__main__':
    joy = XboxController()
    print_server_info()
    asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000))
    asyncio.get_event_loop().run_forever()

    # while True:
    #     time.sleep(.1)