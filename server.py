import socket
import threading
import json

clients_lock = threading.Lock()
connections = []


def handle_client(conn, player_id):
    conn.sendall(json.dumps({"player_id": player_id}).encode('utf-8'))

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            with clients_lock:
                for c in connections:
                    if c != conn:
                        c.sendall(data)
        except Exception:
            # client abruptly closed the connection
            break

    print(f"Player {player_id} disconnected.")

    with clients_lock:
        if conn in connections:
            connections.remove(conn)
        # tell about the disconnect
        for c in connections:
            try:
                c.sendall(json.dumps({"type": "disconnect"}).encode('utf-8'))
            except Exception:
                pass
    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))
    server.listen(2)
    print("Server running...")

    player_id = 0
    while True:
        conn, addr = server.accept()

        with clients_lock:
            if len(connections) < 2:
                connections.append(conn)
                threading.Thread(target=handle_client, args=(conn, player_id)).start()
                player_id = (player_id + 1) % 2

                if len(connections) == 2:
                    for c in connections:
                        try:
                            c.sendall(json.dumps({"type": "ready"}).encode('utf-8'))
                        except Exception:
                            pass
            else:
                conn.close()

if __name__ == "__main__":
    start_server()