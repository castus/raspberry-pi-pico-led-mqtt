import network
import socket
import config
from time import sleep
    
class LEDDriver():
    isOn = False
    lastTick = False
    serverCalled = False
    isConnecting = False

    def __init__(self, name, mqtt_client):
        self.mqtt_client = mqtt_client
        self.name = name
    
    def feed(self, isOn: bool):
        if self.lastTick != isOn:
            self.lastTick = isOn
            self.isOn = isOn
        
        # Power is ON
        if self.isOn == True:
            if self.serverCalled == True:
                return
            else:
                self.call_server()

        # Power is OFF        
        if self.isOn == False:
            self.serverCalled = False

            
    def call_server(self):
        if self.isConnecting == True:
            return
        
        self.isConnecting = True
        self.mqtt_client.publish(config.MQTT_TOPIC, '{ "place": "' + self.name + '" }')
#         addr = socket.getaddrinfo(self.url, 80)[0][-1]
#         s = socket.socket()
# #        s.settimeout(0.5)
#         s.connect(addr)
#         s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % ("/", self.url), 'utf8'))
#         statusCode = s.recv(32).decode("utf-8").split(" ")[1]
#         print(statusCode)
#         s.close()
        self.isConnecting = False
        self.serverCalled = True
        return
       

