import network
from machine import Pin
from machine import I2C
from i2c_lcd import I2cLcd
import socket
import time
from time import sleep
from led_interface import LEDDriver
import _thread
import config

from umqttsimple import MQTTClient
import ubinascii

led = Pin("LED", Pin.OUT)
tv = Pin(6, Pin.IN)
trees = Pin(28, Pin.IN)
loop_break = Pin(12, Pin.IN, Pin.PULL_UP)

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
lcd.display_on()

wifi = None
mqtt_client = None

def count_down(times, x = 0, y = 1):
    for n in range(times):
        lcd.move_to(x,y)
        lcd.putstr(str(times - n - 1))
        sleep(1)

def restart():
    log('Restarting ...')
    count_down(10)
    lcd.clear()
    machine.reset()

def log(text, timeout = 0.25):
    lcd.clear()
    lcd.putstr(text)

def blink(times, timeout = 0.25):
    for i in range(times):
        led.on()
        sleep(timeout)
        led.off()

def mqtt_callback(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')

def connect_wifi():
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    count_down(5)
    
    while not nic.isconnected():
        machine.idle()
    log('Connected to WiFi!')
    return nic
    
def connect_mqtt():
    mqtt_server = config.MQTT_SERVER
    client_id = ubinascii.hexlify(machine.unique_id())
    topic_sub = b'leds'
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(mqtt_callback)
    client.connect()
    count_down(2)
    client.subscribe(topic_sub)
    return client

def program_is_running_indicator():
    while True:
        if loop_break.value() == 0:
            break
        led.on()
        sleep(1)
        led.off()
        sleep(1)

# PROGRAM

led.on()
log("Initializing ...")
count_down(5)

try:
    log("Connecting WiFi ... ")
    wifi = connect_wifi()
    log('WiFi connected!')
except OSError as e:
    log("ERR WiFi")
    count_down(3)
    log(str(e))
    count_down(10)
    restart()

try:
    log('Connecting MQTT ...')
    mqtt_client = connect_mqtt()
    log('MQTT connected!')
except OSError as e:
    log("ERR MQTT")
    count_down(3)
    log(str(e))
    count_down(10)
    restart()

log("Program is running ...")
led.off()

led_tv = LEDDriver("tv", mqtt_client)
led_trees = LEDDriver("trees", mqtt_client)

_thread.start_new_thread(program_is_running_indicator, ())

while True:
    led_tv.feed(bool(tv.value()))
    led_trees.feed(bool(trees.value()))
    if loop_break.value() == 0:
        lcd.clear()
        break
    sleep(0.25)
