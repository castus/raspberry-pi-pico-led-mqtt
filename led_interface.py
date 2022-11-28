import config

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
        self.mqtt_client.publish(
            config.MQTT_TOPIC, msg='{ "place": "' + self.name + '" }')

        self.isConnecting = False
        self.serverCalled = True
        return
