import displayio
import digitalio
import board
#import terminalio
import random
import time
#from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
#from adafruit_bitmap_font import bitmap_font
from adafruit_circuitplayground import cp

#A1 - Top is Control, Middle is Hot, Bottom is neutral

#For an LED
pin = digitalio.DigitalInOut(board.A1)

#For a switch
pin.switch_to_input()
pin.switch_to_input(pull=digitalio.Pull.UP)

def NewLetter():

    display_group = displayio.Group()
    rand = "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    select = random.randrange(9)
    fname = "/" + rand[select] + ".bmp"
    file = open(fname, "rb")

    picture = displayio.OnDiskBitmap(file)
    # Create a Tilegrid with the bitmap and put in the displayio group
    sprite = displayio.TileGrid(picture, pixel_shader=displayio.ColorConverter())
    display_group.append(sprite)

    # Place the display group on the screen
    display.show(display_group)
    display.refresh()

    #cp.play_file("n.wav")

    #font = bitmap_font.load_font("knxt.bdf")

display = tft_gizmo.TFT_Gizmo()

NewLetter()
while True:
    #pass
    time.sleep(1)
    if pin.value == False:
        NewLetter()