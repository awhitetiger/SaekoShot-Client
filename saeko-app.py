import keyboard
import time
from pynput import mouse
from PIL import ImageGrab, Image
import requests
import os
import pyperclip
import configparser
import pystray
import pyautogui

image = Image.open("ssicon48.png")

config = configparser.ConfigParser()

if (os.path.exists('./config.ini')):
    config.read('./config.ini')
    
else:
    config['DEFAULT'] = {'saekoWebUrl': 'http://127.0.0.1/upload',
                        'api_key': '123'}
    with open('./config.ini', 'w') as config_file:
        config.write(config_file)    
    


screenshotMode = False
ssx1, ssx2, ssy1, ssy2 = 0, 0, 0, 0
saekoWebUrl = config.get('DEFAULT', 'saekoWebUrl')
api_key = config.get('DEFAULT', 'api_key')

def toggleScreenshotMode():
    global screenshotMode
    screenshotMode = not screenshotMode

def takeScreenShot(x1, y1, x2, y2):
    global ssx1, ssx2, ssy1, ssy2
    ssx1, ssx2, ssy1, ssy2 = 0, 0, 0, 0
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    timestamp = int(time.time())
    filename = f"screenshot_{timestamp}.png"
    screenshot.save(filename)
    uploadScreenshot(filename)

def takeWholeScreenShot():
    screenshot = pyautogui.screenshot()
    timestamp = int(time.time())
    filename = f"screenshot_{timestamp}.png"
    screenshot.save(filename)
    uploadScreenshot(filename)  

def uploadScreenshot(imagefname):
    global api_key
    image_path = imagefname
    with open(image_path, 'rb') as image_file:
        files = {'image': (image_path, image_file, 'image/png')}
        data = {'api_key': api_key}
        response = requests.post(saekoWebUrl, files=files, data=data)

        if response.status_code == 200:
            pyperclip.copy(response.text)
        else:
            print(f"Failed to upload image. Status code: {response.status_code}")
            print(response.text)

    

def screenshotBounds(x, y, button, pressed):
    global screenshotMode, ssx1, ssy1, ssx2, ssy2
    if (screenshotMode):
        if (pressed and button == mouse.Button.left and ssx1+ssy1 <= 0):
            ssx1 = x
            ssy1 = y
        elif (pressed and button == mouse.Button.left and ssx1+ssy1 > 0):
            ssx2 = x
            ssy2 = y
            screenshotMode = False
            takeScreenShot(ssx1, ssy1, ssx2, ssy2)

def exitSaeko():
    icon.stop()
    os._exit(0)

icon = pystray.Icon("SaekoShot", image, menu=pystray.Menu(
    pystray.MenuItem("Capture Screen", takeWholeScreenShot),
    pystray.MenuItem("Exit", exitSaeko)
))
icon.run_detached()

keyboard.add_hotkey("ctrl+shift+z", toggleScreenshotMode)

with mouse.Listener(on_click=screenshotBounds) as listener:
    try:
        listener.join()
    except:
        print("error")
