import socket
import threading
import json


def handle_client(conn, player_id, connections):
    conn.sendall(json.dumps({"player_id": player_id}).encode('utf-8'))

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            # passing the move
            for c in connections:
                if c != conn:
                    c.sendall(data)
        except:
            break

    conn.close()
    connections.remove(conn)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))
    server.listen(2)
    print("Server running. Waiting for 2 players...")

    connections = []
    player_id = 0

    while len(connections) < 2:
        conn, addr = server.accept()
        connections.append(conn)
        threading.Thread(target=handle_client, args=(conn, player_id, connections)).start()
        player_id += 1


if __name__ == "__main__":
    start_server()