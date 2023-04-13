import paho.mqtt.client as mqtt


class ConnectPi:
    def __init__(self, ip, port):
        self.disconnect = None
        self.client = mqtt.Client("DeskApp")
        self.client.username_pw_set("user", "password")
        self.ip = ip
        self.port = port
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connected = False

    def connect_to_pi(self):
        self.client.connect(self.ip, self.port, keepalive=60, bind_address="")
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Successfully Connected to the Raspberry Pi")
        else:
            print(f"Connection failed: {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False

    def send_message(self, colour):
        self.client.publish("/test/topic", colour)
