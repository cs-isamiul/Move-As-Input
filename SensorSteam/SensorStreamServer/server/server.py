#!/usr/bin/env python

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json
import math

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


hostname = socket.gethostname()
IPAddr = get_ip()
print("Your Computer Name is: " + hostname)
print("Your Computer IP Address is: " + IPAddr)
print(
    "* Enter {0}:5000 in the app.\n* Press the 'Set IP Address' button.\n* Select the sensors to stream.\n* Update the 'update interval' by entering a value in ms.".format(IPAddr))


async def echo(websocket, path):
    lastCouple = [2.27,2.27]
    index = 0
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>henlo")
    async for message in websocket:
        if path == '/accelerometer':
            data = await websocket.recv()
            jsonData = json.loads(data)
            y = abs(float(jsonData["y"]))
            if(y == 0):
                y = 0.1
            y = math.log(y)
            diff = .2
            upper = 2.27*(1+diff)
            lower = 2.27*(1-diff)
            
            state = ">>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<"
            if(upper - y < 0 or y - lower < 0):
                state = "running"
            else:
                for i in range(0, len(lastCouple)):
                    if(upper - lastCouple[i] < 0 or lastCouple[i] - lower < 0):
                        state = "running"
                        break
            
            lastCouple[index] = y
            index += 1
            if(index >= len(lastCouple)):
                index = 0
            print(state)
            # print(data)
            # f = open("accelerometer.txt", "a")
            # f.write(data+"\n")

        if path == '/gyroscope':
            data = await websocket.recv()
            print(data)
            f = open("gyroscope.txt", "a")
            f.write(data+"\n")

        if path == '/magnetometer':
            data = await websocket.recv()
            print(data)
            f = open("magnetometer.txt", "a")
            f.write(data+"\n")

        if path == '/orientation':
            data = await websocket.recv()
            print(data)
            f = open("orientation.txt", "a")
            f.write(data+"\n")

        if path == '/stepcounter':
            data = await websocket.recv()
            print(data)
            f = open("stepcounter.txt", "a")
            f.write(data+"\n")

        if path == '/thermometer':
            data = await websocket.recv()
            print(data)
            f = open("thermometer.txt", "a")
            f.write(data+"\n")

        if path == '/lightsensor':
            print("connected")
            data = await websocket.recv()
            print(data)
            f = open("lightsensor.txt", "a")
            f.write(data+"\n")

        if path == '/proximity':
            data = await websocket.recv()
            print(data)
            f = open("proximity.txt", "a")
            f.write(data+"\n")

        if path == '/geolocation':
            data = await websocket.recv()
            print(data)
            f = open("geolocation.txt", "a")
            f.write(data+"\n")

        if path == '/camera':
            try:
                print("Device connected to camera endpoint")
                data = await websocket.recv()
                print("Image received for parsing")
                parsed_response = json.loads(data)
                fh = open(str(parsed_response['Timestamp']) + ".png", "wb")
                fh.write(b64decode(parsed_response['Base64Data']))
                print("Wrote image with timestamp " +str(parsed_response['Timestamp']))
            except Exception:
                print('Connection closed due to error')
                await websocket.close()

        if path == '/audio':
            print("Device connected to audio endpoint")
            data = await websocket.recv()
            print(data)
            decoded_data = b64decode(data, ' /')
            with open('temp.pcm', 'ab') as pcm:
                pcm.write(decoded_data)
            with open('temp.pcm', 'rb') as pcm:
                pcmdata = pcm.read()
            with wave.open('audio.wav', 'wb') as wav:
                #(nchannels, sampwidth, framerate, nframes, comptype, compname)
                #wav.setparams((1, 16, 32000, 32, 'NONE', 'NONE'))
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(48000)
                wav.setcomptype('NONE', 'NONE')
                wav.writeframesraw(pcmdata)
            print("Wrote to audio.wav")


asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000))
asyncio.get_event_loop().run_forever()
