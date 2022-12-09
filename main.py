import _thread
import time
from time import sleep

import machine
import netman
from machine import Pin, PWM

import config
from led_interface import LEDDriver
from logger import LCDLogger, TerminalLogger
from umqttsimple import MQTTClient

#logger = TerminalLogger()
logger = LCDLogger()

led = Pin("LED", Pin.OUT)

tv = Pin(6, Pin.IN)
led_tv = None

trees = Pin(28, Pin.IN)
led_trees = None

loop_break = Pin(12, Pin.IN, Pin.PULL_UP)
second_thread_id = None

def log(text, x = None, y = None):
    if x != None and y != None:
        logger.move_to(x, y)
    else:
        logger.clear()
    
    logger.putstr(text)

def count_down(times, x = 15, y = 1):
    for n in range(times):
        logger.move_to(x, y)
        logger.putstr(str(times - n))
        sleep(1)

def disconnect():
    try:
        client_wifi.disconnect()
    except:
        pass
    try:
        client_mqtt.disconnect()
    except:
        pass

def restart():
    log('Restarting ...')
    count_down(3)
    disconnect()
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
    log('WiFi Connected!')
    sleep(1)
    return wifi_connection
    
def connect_mqtt():
    log("Connecting MQTT ... ")
    client = MQTTClient('PicoW', config.MQTT_SERVER, port=config.MQTT_PORT, user='admin', password='admin', keepalive=60)
    client.connect()
    log('MQTT Connected!')
    sleep(1)
    return client

def program_is_running_indicator():
    while True:
        if loop_break.value() == 0:
            break
        led.on()
        sleep(0.75)
        led.off()
        sleep(0.75)
        
def break_the_loop_if_necessary():
    if loop_break.value() == 0:
        log("Loop broken")
        log("Program stopped", 0, 1)
        second_thread_id.exit()
        raise RuntimeError('Loop stopped')

# PROGRAM

led.on()
log("Initializing ...")
count_down(2)

try:
    client_wifi = connect_wifi()
except Exception as e:
    log("ERR WiFi")
    count_down(1)
    log(str(e))
    count_down(5)
    restart()


ping_interval = 20000 # in ms
while True:
    break_the_loop_if_necessary()

    try:
        client_mqtt = connect_mqtt()
        led_tv = LEDDriver("tv", client_mqtt)
        led_trees = LEDDriver("trees", client_mqtt)
        led.off()
        second_thread_id = _thread.start_new_thread(program_is_running_indicator, ())

        log("Working ...")
    except OSError as e:
        log(str(e))
        restart()
    
    last_tick = time.ticks_ms()
    while True:
        break_the_loop_if_necessary()

        try:
            led_tv.feed(bool(tv.value()))
            led_trees.feed(bool(trees.value()))
            current_tick = time.ticks_ms()
            if(time.ticks_diff(current_tick, last_tick) >= ping_interval):
                last_tick = current_tick
                client_mqtt.publish('leds', msg='pico ping')
        except OSError as e:
            log(str(e))
            restart()
