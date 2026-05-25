import socket
import json


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = '192.168.1.205' # use ipconfig in a diff terminal to find the IP address of the local machine(the server machine)
        self.addr = (self.server_ip, 5555)
        self.buffer = ""
        self.player_id = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        while '\n' not in self.buffer:
            self.buffer += self.client.recv(1024).decode('utf-8')

        msg, self.buffer = self.buffer.split('\n', 1)
        return json.loads(msg)['player_id']

    def send(self, data):
        self.client.sendall((json.dumps(data) + '\n').encode('utf-8'))

    def receive(self):
        try:
            self.client.setblocking(False)
            data = self.client.recv(1024)
            if data:
                return json.loads(data.decode('utf-8'))
        except BlockingIOError:
            pass
        if '\n' in self.buffer:
            msg, self.buffer = self.buffer.split('\n', 1)
            return json.loads(msg)
        return None
