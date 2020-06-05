import time
import board
import adafruit_touchscreen
import displayio
from adafruit_display_text.label import Label
import terminalio
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt as MQTT
import adafruit_pyportal

pyportal = adafruit_pyportal.PyPortal()
display = board.DISPLAY
### WiFi ###

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# pylint: disable=protected-access
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(pyportal._esp, secrets, None)

# ------------- MQTT Topic Setup ------------- #
mqtt_topic = "activestats/current"

### Code ###
# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Subscribing to %s" % (mqtt_topic))
    client.subscribe(mqtt_topic)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT Broker!")


def message(client, topic, message):
    print("New message on topic {0}: {1}".format(topic, message))
    global currentmessage
    currentmessage = message

# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

# Initialize MQTT interface with the esp interface


# Connect the client to the MQTT broker.
#mqtt_client.connect()

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

def writemessage(text, axisX, axisY, color):
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
    splashBitmap = displayio.Bitmap(320, 240, 1)
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
#imagedisplay("white")
splashScreen("white")
time.sleep(1)
def displayloop():
    if runcount > 0:
        group.pop()
        group.pop()
        time.sleep(1)
    else:
        imagedisplay("swimbikeruntop")
        #time.sleep(2)
        #imagedisplay("bikerunswimside")
        #time.sleep(2)
        #message("Total Activities: %s" % summaryList["Total Activities"], 30, 40)
        writemessage("7 Day Totals \n Activities: %s \n Time: %s" %(summaryList["Total Activities"], summaryList["Total Time"]), 1, 70, "green")
        time.sleep(8)
        #group.pop()
        group.pop()
        group.pop()
        time.sleep(1)
    #for i in range(100):
    #    display.brightness = 0.01 * i
    #    time.sleep(0.05)
    imagedisplay("bike")
    writemessage("Rides: %s \n Distance: %s \n Avg Watts: %s" %(summaryList["Total Rides"], summaryList["Total Ride Miles"], summaryList["Average Watts"]), 1, 90, "blue")
    time.sleep(8)
    group.pop()
    group.pop()
    time.sleep(1)
    imagedisplay("run")
    writemessage("Runs: %s \n Distance: %s \n Avg Pace: %s" %(summaryList["Total Runs"], summaryList["Total Run Miles"], summaryList["Average Run Pace"]), 1, 90, "red")
    time.sleep(8)
    group.pop()
    group.pop()
    time.sleep(1)
    imagedisplay("swimbikeruntop")
    writemessage("7 Day Totals \n Activities: %s \n Time: %s" %(summaryList["Total Activities"], summaryList["Total Time"]), 1, 70, "green")

def MQSetup():
    # pylint: disable=protected-access
        MQTT.set_socket(socket, pyportal._esp)

        # Set up a MiniMQTT Client
        mqtt_client = MQTT.MQTT(broker=secrets["broker"], username=secrets["user"], password=secrets["pass"], is_ssl=False, port=16392)

        # Setup the callback methods above
        mqtt_client.on_connect = connected
        mqtt_client.on_disconnect = disconnected
        mqtt_client.on_message = message
        
        mqtt_client.connect()
        time.sleep(3)
        mqtt_client.loop()
        time.sleep(3)
        mqtt_client.disconnect()

currentmessage = "null"
mqstatus = "null"
wifistatus = "null"
runcount = 0
while True:
    # Poll the message queue
    try:
        wifi.ping(secrets["broker"])
    except:
        print("Wifi disconnected, reconnecting")
        wifi.connect()
        print("Connected!")

    #mqtt_client.connect()
    
    try:
        MQSetup()
        mqstatus = "Ok"
    except Exception as err:
        print("OS error: {0}".format(err))
        print("Couldn't connect, we'll need to reset wifi and try again")
        mqstatus = "Failed"

    #try:
    #    mqtt_client.disconnect()
    #    mqstatus = "Ok"
    #except:
    #    print("Couldn't connect, we'll need to reset wifi and try again")
    #    mqstatus = "Failed"
    


    #try:
    #    mqtt_client.loop()
    #except:
    #    print("looks like we disconnected, trying to reconnect MQTT")
    #    try:
    #        mqtt_client.connect()
    #    except:
    #        print("Couldn't connect, we'll need to reset wifi and try again")
    #        try:
    #            wifi.reset()
    #            mqtt_client.connect()
    #        except:
    #            print("wifi and reconnect failed, we're boned")
    #print("still running")
    #time.sleep(2)
    #print(currentmessage)
    if currentmessage != "null":
        summaryList = eval(currentmessage)
        displayloop()
        #global runcount
        runcount = runcount + 1
    else:
        print("No data from MQTT!")
        time.sleep(10)
    
