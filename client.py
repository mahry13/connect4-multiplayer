import socket
import json


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = ('127.0.0.1', 5555)
        self.player_id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        data = json.loads(self.client.recv(1024).decode('utf-8'))
        return data['player_id']

    def send(self, data):
        self.client.sendall(json.dumps(data).encode('utf-8'))

    def receive(self):
        try:
            self.client.setblocking(False)
            data = self.client.recv(1024)
            if data:
                return json.loads(data.decode('utf-8'))
        except BlockingIOError:
            pass
        return None