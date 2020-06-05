import displayio
import time
#import board
#import digitalio
import terminalio
from adafruit_display_text.label import Label
from adafruit_gizmo import tft_gizmo
#from adafruit_circuitplayground import cp

display = tft_gizmo.TFT_Gizmo()

def imagedisplay(word):
    #display_group = displayio.Group()
    # Display graphic from the root directory of the CIRCUITPY drive
    filename = "/" + word + ".bmp"
    file = open(filename, "rb")
    picture = displayio.OnDiskBitmap(file)
    # Create a Tilegrid with the bitmap and put in the displayio group
    sprite = displayio.TileGrid(picture, pixel_shader=displayio.ColorConverter())
    group.append(sprite)
    #display.refresh(target_frames_per_second=60)
    # Place the display group on the screen
    #display.show(group)
    #display.refresh()

def message(text, axisX, axisY, color):
    text_group = displayio.Group(max_size=1, scale=2)
    label = Label(terminalio.FONT, text=text)
    if color == "white":
        color = 0xFFFFFF
    if color == "red":
        color = 0xFF0000
    if color == "blue": 
        color = 0x0000FF
    if color == "green":
        color = 0x00CC00
    label.color = color
    #if bgcolor == "white":
    #    bgcolor = 0xFFFFFF
    #if bgcolor == "red":
    #    bgcolor = 0xFF0000
    #if bgcolor == "blue": 
    #    bgcolor = 0x0000FF
    #if bgcolor == "green":
    #    bgcolor = 0x00FF00
    #label.background_color = bgcolor
    (x, y, w, h) = label.bounding_box
    #label.x = (80 - w // 2)
    label.x = axisX
    #label.y = (64 - h // 2)
    label.y = axisY
    text_group.append(label)
    #group.append(label)
    group.append(text_group)

def splashScreen(color):
    splashBitmap = displayio.Bitmap(20, 20, 1)
    splashPalette = displayio.Palette(1)
    if color == "white":
        color = 0xFFFFFF
    if color == "red":
        color = 0xFF0000
    if color == "blue": 
        color = 0x0000FF
    if color == "green":
        color = 0x00FF00
    splashPalette[0] = color
    splashSprite = displayio.TileGrid(splashBitmap, pixel_shader=splashPalette, x=0, y=0)
    group.append(splashSprite)

group = displayio.Group(max_size=3)
display.show(group)
imagedisplay("white")
time.sleep(4)
def displayloop():
    imagedisplay("swimbikeruntop")
    #time.sleep(2)
    #imagedisplay("bikerunswimside")
    #time.sleep(2)
    #message("Total Activities: %s" % summaryList["Total Activities"], 30, 40)
    message("7 Day Totals \n Activities: %s \n Time: %s" %(summaryList["Total Activities"], summaryList["Total Time"]), 1, 70, "green")
    time.sleep(8)
    #group.pop()
    group.pop()
    group.pop()
    time.sleep(2)
    #for i in range(100):
    #    display.brightness = 0.01 * i
    #    time.sleep(0.05)
    imagedisplay("bike")
    message("Rides: %s \n Distance: %s \n Avg Watts: %s" %(summaryList["Total Rides"], summaryList["Total Ride Miles"], summaryList["Average Watts"]), 1, 90, "blue")
    time.sleep(8)
    group.pop()
    group.pop()
    time.sleep(2)
    imagedisplay("run")
    message("Runs: %s \n Distance: %s \n Avg Pace: %s" %(summaryList["Total Runs"], summaryList["Total Run Miles"], summaryList["Average Run Pace"]), 1, 90, "red")
    time.sleep(8)
    group.pop()
    group.pop()
    time.sleep(2)

with open('/stats.json') as filehandle:
    filecontents = filehandle.readlines()
filehandle.close()

summaryList = {}
for line in filecontents:
    # remove linebreak which is the last character of the string
    if len((line[:-1]).split(":")) == 2:
        key = (line[:-1]).split(":")[0]
        value = line[:-1].split(":")[1]
        summaryList[key] = value
    else:
        key = (line[:-1]).split(":")[0]
        value = line[:-1].split(":")[1] + ":" + line[:-1].split(":")[2]
        summaryList[key] = value

while True:
    displayloop()
    #pass