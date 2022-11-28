import _thread
import time
from time import sleep

import machine
import netman
from machine import Pin

import config
from led_interface import LEDDriver
from logger import LCDLogger, TerminalLogger
from umqttsimple import MQTTClient

#logger = TerminalLogger()
logger = LCDLogger()

led = Pin("LED", Pin.OUT)
tv = Pin(6, Pin.IN)
trees = Pin(28, Pin.IN)
loop_break = Pin(12, Pin.IN, Pin.PULL_UP)

mqtt_client = None

def log(text, time = 0):
    logger.clear()
    logger.putstr(text)

def count_down(times, x = 15, y = 1):
    for n in range(times):
        logger.move_to(x, y)
        logger.putstr(str(times - n - 1))
        sleep(1)

def restart():
    log('Restarting ...')
    count_down(5)
    logger.clear()
    machine.reset()

def blink(times, timeout = 0.25):
    for i in range(times):
        led.on()
        sleep(timeout)
        led.off()

def connect_wifi():
    log("Connecting WiFi ... ")
    wifi_connection = netman.connectWiFi(config.WIFI_SSID,config.WIFI_PASSWORD,"PL")
    log('Connected to WiFi!')
    return wifi_connection
    
def connect_mqtt():
    client = MQTTClient('PicoW', config.MQTT_SERVER, port=config.MQTT_PORT, user='admin', password='admin', keepalive=60)
    client.connect()
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
count_down(3)

try:
    connect_wifi()
except Exception as e:
    log("ERR WiFi")
    count_down(1)
    log(str(e))
    count_down(5)
    restart()

_thread.start_new_thread(program_is_running_indicator, ())
log("Executing main loop ...")
led.off()

ping_interval = 20000 # in ms
while True:
    if loop_break.value() == 0:
        raise RuntimeError('Break the loop')

    try:
        client = connect_mqtt()
        led_tv = LEDDriver("tv", client)
        led_trees = LEDDriver("trees", client)
    except OSError as e:
        restart()
    
    last_tick = time.ticks_ms()
    while True:
        if loop_break.value() == 0:
            raise RuntimeError('Break the loop')

        try:
            led_tv.feed(bool(tv.value()))
            led_trees.feed(bool(trees.value()))
            current_tick = time.ticks_ms()
            if(time.ticks_diff(current_tick, last_tick) >= ping_interval):
                last_tick = current_tick
                client.publish('leds', msg='pico ping')
        except:
            restart()
            pass
        
    client.disconnect()
