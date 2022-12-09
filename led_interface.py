import config
import json
from buzzer import buzz_turn_on, buzz_turn_off
from machine import Pin
from time import sleep

class LEDDriver():
    lastTick = None

    def __init__(self, name, mqtt_client):
        self.mqtt_client = mqtt_client
        self.name = name

    def feed(self, isOn: bool):
        if self.lastTick != isOn or self.lastTick == None:
            self.lastTick = isOn
            self.call_server(isOn)

    def call_server(self, isOn):
        message_obj = {
            'IsLightOn': isOn,
            'Place': self.name
        }
        print(message_obj)
        
        self.mqtt_client.publish(config.MQTT_TOPIC, json.dumps(message_obj))
        if isOn:
            buzz_turn_on()
        else:
            buzz_turn_off()
        
        return
