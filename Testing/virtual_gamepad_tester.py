import vgamepad as vg
import json
import time

# Load buttons file 
buttons = {}
with open("buttons.json") as buttons:
    buttons = json.load(buttons)

    print("Type:", type(buttons))
    print(buttons["up"])

#create virtual gamepad
gamepad = vg.VX360Gamepad()

#time.sleep(2)
#test pressing and releasing A
while(True):
    gamepad.press_button(button=int(buttons["A"], 16))
    gamepad.update()
    print("Pressing A")
    time.sleep(2)
    gamepad.release_button(button=int(buttons["A"], 16))
    gamepad.update()
    print("Releasing A")
    time.sleep(2)