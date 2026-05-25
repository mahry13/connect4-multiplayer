import socket
import threading
import json
import os
from elements.board import Board 

# locks to prevent race conditions when multiple threads access the same data
clients_lock = threading.Lock()
game_state_lock = threading.Lock()


connections = []
shared_board = Board()
current_turn = 0
game_active = True
restart_votes = set()  # using a set so even if one player spams 'yes' it counts as one vote

# lightweight mock player to pass to the Board methods
class ServerPlayerMock:
    def __init__(self, player_id):
        self.id = player_id
    def get_id(self):
        return self.id


def reset_shared_game():
    global current_turn, game_active, restart_votes
    shared_board.clear()
    current_turn = 0
    game_active = True
    restart_votes.clear()

def send_json(conn, data):
    # package and send data safely
    try:
        # attach a newline so the receiver knows where the packet ends
        msg = (json.dumps(data) + "\n").encode('utf-8')
        conn.sendall(msg)
    except Exception as e:
        print(f"Error sending message: {e}")

def handle_client(conn, player_id):
    global current_turn, game_active

    client_buffer = ""
    current_player_mock = ServerPlayerMock(player_id)

    while True:
        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                break # connection closed naturally

            client_buffer += raw_data.decode('utf-8')

            # pull complete messages, separated by newline, out of the raw stream
            while "\n" in client_buffer:
                packet_str, client_buffer = client_buffer.split("\n", 1)
                packet_str = packet_str.strip()

                if not packet_str:
                    continue

                try:
                    data = json.loads(packet_str)
                except json.JSONDecodeError:
                    continue

                msg_type = data.get("type")

                # handle restart voting
                if msg_type == "restart_request":
                    with game_state_lock:
                        restart_votes.add(player_id)
                        if len(restart_votes) == 2:
                            reset_shared_game()
                            with clients_lock:
                                for c in connections:
                                    send_json(c, {"type": "restart_request"})
                    continue

                # handle a game move
                if "column" in data:
                    col = data["column"]
                    broadcast_payload = None
                    error_message = None

                    with game_state_lock:
                        if not game_active:
                            error_message = "Game over! Waiting for restart."
                        elif current_turn != player_id:
                            error_message = "Not your turn!"
                        else:
                            row = shared_board.get_next_open_row(current_player_mock, col)

                            if row == -1:
                                error_message = "Column full!"
                            else:
                                shared_board.place_piece(current_player_mock, col, row)
                                has_won = shared_board.winning_move(current_player_mock)
                                
                                broadcast_payload = {
                                    "type": "move_success",
                                    "player_id": player_id,
                                    "column": col,
                                    "row": row,
                                    "won": has_won
                                }

                                if has_won:
                                    game_active = False
                                else:
                                    current_turn = (current_turn + 1) % 2
                    # route result back to clients
                    if error_message:
                        print(f"[SERVER LOG] Rejected move from Player {player_id}: {error_message}")
                        send_json(conn, {"type": "error", "message": error_message})
                        continue

                    if broadcast_payload:
                        print(f"[SERVER LOG] Player {player_id} placed piece in Col {col}, Row {row}. Won: {broadcast_payload['won']}")
                        with clients_lock:
                            for c in connections:
                                send_json(c, broadcast_payload)

        except Exception as e:
            print(f"Exception handling network transmission: {e}")
            break
    # handle cleanup when someone disconnects
    print(f"Player {player_id} disconnected.")
    with clients_lock:
        if conn in connections:
            connections.remove(conn)
        for c in connections:
            send_json(c, {"type": "disconnect"})
    conn.close()


def accept_connections(server):
    player_id = 0
    while True:
        try:
            conn, addr = server.accept()
        except Exception:
            break  # triggers when the server socket is forcefully closed by the main thread

        with clients_lock:
            if len(connections) < 2:
                connections.append(conn)

                send_json(conn, {"player_id": player_id})

                # launch the client's dedicated listening loop in the background
                threading.Thread(target=handle_client, args=(conn, player_id), daemon=True).start()
                player_id = (player_id + 1) % 2

                # wake up both clients once the lobby is full
                if len(connections) == 2:
                    with game_state_lock:
                        reset_shared_game()
                    for c in connections:
                        send_json(c, {"type": "ready"})
            else:
                conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555)) 
    server.listen(2)
    print("Server running... Type 'q' and press Enter to shut down.")

    accept_thread = threading.Thread(target=accept_connections, args=(server,), daemon=True)
    accept_thread.start()

    # wait for user to manually kill the server from the terminal
    while True:
        cmd = input()
        if cmd.lower() == 'q':
            print("Shutting down server...")
            server.close()
            with clients_lock:
                for c in connections:
                    c.close()
            os._exit(0)  # force quit the program and kill all threads immediately

if __name__ == "__main__":
    start_server()