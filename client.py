import socket
import json

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = '192.168.1.22'
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
        try:
            self.client.sendall((json.dumps(data) + '\n').encode('utf-8'))
        except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
            print(f"[CLIENT LOG] Lost connection to server while sending: {e}")

    def receive_all_packets(self):
        """
        Reads non-blocking network stream chunks and parses out a list 
        of complete JSON messages separated by newlines.
        """
        packets = []
        try:
            self.client.setblocking(False)
            data = self.client.recv(1024)
            if not data:
                # If recv() returns an empty byte string, the server closed gracefully
                return [{"type": "server_disconnect"}]
            self.buffer += data.decode('utf-8')

        except BlockingIOError:
            pass  # No data available right now
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            # The server crashed or was shut down abruptly
            return [{"type": "server_disconnect"}]

        # Process all full lines currently held inside our stream buffer
        while '\n' in self.buffer:
            msg_str, self.buffer = self.buffer.split('\n', 1)
            msg_str = msg_str.strip()
            if msg_str:
                try:
                    packets.append(json.loads(msg_str))
                except json.JSONDecodeError:
                    pass
        return packets