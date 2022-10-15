import json

with open("buttons.json") as buttons:
    buttons = json.load(buttons)

    print("Type:", type(buttons))
    
    a = int(buttons["A"], 16)
    print(a)
    print(type(a))