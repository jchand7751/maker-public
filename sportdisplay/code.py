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
import microcontroller

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

### Variables ###
pyportal = adafruit_pyportal.PyPortal()
display = board.DISPLAY
currentmessage = "null"
mqstatus = "null"
wifistatus = "null"
runcount = 0
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(pyportal._esp, secrets, None)
mqtt_topic = secrets["mqtopic"]

### Code - Definitions ###

def MQSetup():
    global mqtt_client
    time.sleep(3)
    try:
        # Get the retained message (wait until it shows up)
        mqtt_client.loop()
    except Exception as err:
        print("Except: {0}".format(err))
        print("Failed to pull the retained message")
        wifi.reset()
        mqtt_client.reconnect()
    time.sleep(3)

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

def displayloop():
    # Definition for display looping
    # The first run won't have any images but on all the following runs pop the groups showing the last image
    # This is used to cover the MQTT reconnect and still have a pretty thing to show
    if runcount > 0:
        group.pop()
        group.pop()
        time.sleep(1)
    else:
        # Show the 7 day stat page (only for the first run)
        imagedisplay("swimbikeruntop")
        writemessage("7 Day Totals \n Activities: %s \n Time: %s" %(summaryList["Total Activities"], summaryList["Total Time"]), 1, 70, "green")
        time.sleep(8)
        group.pop()
        group.pop()
        time.sleep(1)
    #for i in range(100):
    #    display.brightness = 0.01 * i
    #    time.sleep(0.05)

    # Todo - Show the swim stats
    # Todo - Make this an if swims > 0

    # Show the bike stats
    # Todo - Make this an if rides > 0
    imagedisplay("bike")
    writemessage("Rides: %s \n Distance: %s \n Avg Watts: %s" %(summaryList["Total Rides"], summaryList["Total Ride Miles"], summaryList["Average Watts"]), 1, 90, "blue")
    time.sleep(8)
    group.pop()
    group.pop()
    time.sleep(1)

    # Show the run stats
    # Todo - Make this an if runs > 0
    imagedisplay("run")
    writemessage("Runs: %s \n Distance: %s \n Avg Pace: %s" %(summaryList["Total Runs"], summaryList["Total Run Miles"], summaryList["Average Run Pace"]), 1, 90, "red")
    time.sleep(8)
    group.pop()
    group.pop()
    time.sleep(1)

    # Show the 7 day stat page to cover the MQTT reconnect (start of next loop)
    imagedisplay("swimbikeruntop")
    writemessage("7 Day Totals \n Activities: %s \n Time: %s" %(summaryList["Total Activities"], summaryList["Total Time"]), 1, 70, "green")

def imagedisplay(word):
    # Display a graphic from the root directory
    filename = "/" + word + ".bmp"
    file = open(filename, "rb")
    picture = displayio.OnDiskBitmap(file)
    # Create a Tilegrid with the bitmap and put in the displayio group
    sprite = displayio.TileGrid(picture, pixel_shader=displayio.ColorConverter())
    group.append(sprite)
    
def writemessage(text, axisX, axisY, color):
    # Definition for adding a text label
    text_group = displayio.Group(max_size=1, scale=2)
    label = Label(terminalio.FONT, text=text)
    # Section for label font colors
    if color == "white":
        color = 0xFFFFFF
    if color == "red":
        color = 0xFF0000
    if color == "blue": 
        color = 0x0000FF
    if color == "green":
        color = 0x00CC00
    label.color = color
    # Section for label background colors
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
    # Definition for setting a background color
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

### Code ###

### WiFi ###
# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

### Display Setup ###
# Create the display group
group = displayio.Group(max_size=3)
# Try to fix the weird refresh thing
display.refresh(target_frames_per_second=60)
# Show the initial solid color background
splashScreen("white")
display.show(group)

### MQTT Setup ###
MQTT.set_socket(socket, pyportal._esp)
try:
    # Set up a MiniMQTT Client
    mqtt_client = MQTT.MQTT(broker=secrets["broker"], username=secrets["user"], password=secrets["pass"], client_id=secrets["clientid"], is_ssl=False, port=16392)
except Exception as err:
    print("Except: {0}".format(err))
    print("Failed to create MQTT Client")
    

# Setup the callback methods
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

try:
    # Connect and wait for fully established connection
    mqtt_client.connect()
except Exception as err:
    print("Except: {0}".format(err))
    print("Failed to connect the MQTT client")

### Main Loop ###
while True:
    if runcount == 0:
        # Time for a reboot
        #microcontroller.reset()
        # Run MQSetup on the first run only
        #MQSetup()
        print("First run!")
    # Test wifi connectivity to the MQTT broker
    try:
        print("Testing wifi")
        wifi.ping(secrets["broker"])
        print("Wifi confirmed")
    except:
        print("Wifi disconnected, reconnecting")
        wifi.connect()
        print("Connected!")

    # Call the MQTT definition to subscribe, check for the retained message, and then disconnect
    #try:
    #    print("Starting MQTT")
        #MQSetup()
        #mqstatus = "Ok"
    #    print("MQTT confirmed")
        #mqtt_client.loop()
    #except Exception as err:
    #    print("Except: {0}".format(err))
    #    print("Couldn't connect via MQTT")
        #mqstatus = "Failed"

    time.sleep(3)
    try:
        print("Starting MQTT")
        # Get the retained message (wait until it shows up)
        mqtt_client.loop()
        mqstatus = "Ok"
        print("MQTT confirmed")
    except Exception as err:
        print("Except: {0}".format(err))
        print("Failed to pull the retained message")
        mqstatus = "Failed"
        #wifi.reset()
        #mqtt_client.reconnect()
    time.sleep(3)

    if mqstatus == "Failed":
        try:
            mqtt_client.reconnect()
        except Exception as err:
            print("Except: {0}".format(err))
            print("Failed to reconnect to broker")
            wifi.reset()
            MQTT.set_socket(socket, pyportal._esp)
            try:
                # Set up a MiniMQTT Client
                mqtt_client = MQTT.MQTT(broker=secrets["broker"], username=secrets["user"], password=secrets["pass"], client_id=secrets["clientid"], is_ssl=False, port=16392)
            except Exception as err:
                print("Except: {0}".format(err))
                print("Failed to create MQTT Client")
                

            # Setup the callback methods
            mqtt_client.on_connect = connected
            mqtt_client.on_disconnect = disconnected
            mqtt_client.on_message = message

            try:
                # Connect and wait for fully established connection
                mqtt_client.connect()
            except Exception as err:
                print("Except: {0}".format(err))
                print("Failed to connect the MQTT client")

            try:
                # Get the retained message (wait until it shows up)
                mqtt_client.loop()
                mqstatus = "Ok"
            except Exception as err:
                print("Except: {0}".format(err))
                print("Failed to pull the retained message")
                mqstatus = "Failed"
                #wifi.reset()
                mqtt_client.reconnect()


    # Run the display loop if the message isn't blank
    if currentmessage != "null":
        print("Starting display loop")
        summaryList = eval(currentmessage)
        displayloop()
        print("Finishing display loop")
        runcount = runcount + 1
        print(runcount)
    else:
        print("No data from MQTT!")
        time.sleep(10)