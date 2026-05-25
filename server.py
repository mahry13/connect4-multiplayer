import socket
import threading
import json

COL_COUNT = 7
ROW_COUNT = 6
WINNING_COUNT = 4

clients_lock = threading.Lock()
connections = []

# shared resources protected by game_state_lock
game_state_lock = threading.Lock()
shared_board = [[-1 for _ in range(7)] for _ in range(6)]  # 6 rows, 7 columns (-1 = empty)
current_turn = 0  # Player 0 goes first
game_active = True

def winning_move(board, player_id):
    # horizontal
    for col in range(COL_COUNT - WINNING_COUNT + 1):
        for row in range(ROW_COUNT):
            if board[row][col] == player_id and board[row][col + 1] == player_id and board[row][col + 2] == player_id and board[row][col + 3] == player_id:
                return True

    # vertical
    for col in range(COL_COUNT):
        for row in range(ROW_COUNT - WINNING_COUNT + 1):
            if board[row][col] == player_id and board[row + 1][col] == player_id and board[row + 2][col] == player_id and board[row + 3][col] == player_id:
                return True

    # positive diagonal
    for col in range(COL_COUNT - WINNING_COUNT + 1):
        for row in range(WINNING_COUNT - 1, ROW_COUNT):
            if board[row][col] == player_id and board[row - 1][col + 1] == player_id and board[row - 2][col + 2] == player_id and board[row - 3][col + 3] == player_id:
                return True

    # negative diagonal
    for col in range(COL_COUNT - WINNING_COUNT + 1):
        for row in range(ROW_COUNT - WINNING_COUNT + 1):
            if board[row][col] == player_id and board[row + 1][col + 1] == player_id and board[row + 2][col + 2] == player_id and board[row + 3][col + 3] == player_id:
                return True
    return False

def reset_shared_game():
    global shared_board, current_turn, game_active
    shared_board = [[-1 for _ in range(7)] for _ in range(6)]
    current_turn = 0
    game_active = True

def send_json(conn, data):
    """Helper wrapper to guarantee every packet string ends with a safe delimiter."""
    try:
        msg = (json.dumps(data) + "\n").encode('utf-8')
        conn.sendall(msg)
    except Exception as e:
        print(f"Error sending message: {e}")

def handle_client(conn, player_id):
    global current_turn, game_active
    conn.sendall((json.dumps({"player_id": player_id}) + '\n').encode('utf-8'))

    while True:
        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                break

            client_buffer += raw_data.decode('utf-8')
            
            # FIX 2: Process incoming stream chunks divided by newlines
            while "\n" in client_buffer:
                packet_str, client_buffer = client_buffer.split("\n", 1)
                packet_str = packet_str.strip()
                if not packet_str:
                    continue

            if msg_type == "restart_request":
                with game_state_lock:
                    reset_shared_game()
                with clients_lock:
                    for c in connections:
                        c.sendall((json.dumps({"type": "restart_request"}) + '\n').encode('utf-8'))
                continue

                # Handle Rematch requests
                if msg_type == "restart_request":
                    with game_state_lock:
                        reset_shared_game()
                    with clients_lock:
                        for c in connections:
                            send_json(c, {"type": "restart_request"})
                    continue

                with game_state_lock:
                    if not game_active:
                        conn.sendall((json.dumps({"type": "error", "message": "Game over! Waiting for restart."}) + '\n').encode('utf-8'))
                        continue
                        
                    if current_turn != player_id:
                        conn.sendall((json.dumps({"type": "error", "message": "Not your turn!"}) + '\n').encode('utf-8'))
                        continue

                        if has_won:
                            game_active = False
                        else:
                            current_turn = (current_turn + 1) % 2

                    if row == -1:
                        # column was full
                        conn.sendall((json.dumps({"type": "error", "message": "Column full!"}) + '\n').encode('utf-8'))
                        continue

                    # make a move on shared board
                    shared_board[row][col] = player_id
                    has_won = winning_move(shared_board, player_id)
                    
                    # Package state payload
                    broadcast_payload = (json.dumps({
                        "type": "move_success",
                        "player_id": player_id,
                        "column": col,
                        "row": row,
                        "won": has_won
                    }) + '\n').encode('utf-8')

                    if has_won:
                        game_active = False
                    else:
                        current_turn = (current_turn + 1) % 2
            #  broadcast change to all clients
            with clients_lock:
                for c in connections:
                        c.sendall(broadcast_payload)
        except Exception:
            # client abruptly closed the connection
            break

    print(f"Player {player_id} disconnected.")

    with clients_lock:
        if conn in connections:
            connections.remove(conn)
        # Inform remaining active clients about the drop
        for c in connections:
            try:
                c.sendall((json.dumps({"type": "disconnect"}) + '\n').encode('utf-8'))
            except Exception:
                pass
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555)) # listening on all interfaces
    server.listen(2)
    print("Server running...")

    player_id = 0
    while True:
        conn, addr = server.accept()
        print(f"Connection registered from IP: {addr[0]}")

        with clients_lock:
            if len(connections) < 2:
                connections.append(conn)
                threading.Thread(target=handle_client, args=(conn, player_id)).start()
                player_id = (player_id + 1) % 2

                if len(connections) == 2:
                    with game_state_lock:
                        reset_shared_game()
                    for c in connections:
                        try:
                            c.sendall((json.dumps({"type": "ready"})+ '\n').encode('utf-8'))
                        except Exception:
                            pass
            else:
                conn.close()
# dodac thread do przechwytywania inputu zeby wylaczyc serwer
if __name__ == "__main__":
    start_server()