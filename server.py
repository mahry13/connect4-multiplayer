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
    """Guarantees every outgoing data packet ends with a uniform newline character."""
    try:
        msg = (json.dumps(data) + '\n').encode('utf-8')
        conn.sendall(msg)
    except Exception as e:
        print(f"Error broadcasting message: {e}")

def handle_client(conn, player_id):
    global current_turn, game_active
    
    # Register connection
    send_json(conn, {"player_id": player_id})

    while True:
        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                break

            # Note: For simplicity on standard turns, assuming clean single-packet requests.
            # If clients spam inputs, apply the newline split technique used in client.py here too!
            data = json.loads(raw_data.decode('utf-8').strip())
            msg_type = data.get("type")

            if msg_type == "restart_request":
                with game_state_lock:
                    reset_shared_game()
                with clients_lock:
                    for c in connections:
                        send_json(c, {"type": "restart_request"})
                continue

            if "column" in data:
                col = data["column"]
                broadcast_payload = None
                error_message = None

                # Keep the lock execution path fast and drop-safe!
                with game_state_lock:
                    if not game_active:
                        error_message = "Game over! Waiting for restart."
                    elif current_turn != player_id:
                        error_message = "Not your turn!"
                    else:
                        # validate space on shared board
                        row = -1
                        for r in range(ROW_COUNT):
                            if shared_board[r][col] == -1:
                                row = r
                                break

                        if row == -1:
                            error_message = "Column full!"
                        else:
                            # Commit move securely
                            shared_board[row][col] = player_id
                            has_won = winning_move(shared_board, player_id)
                            
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

                # Send error responses safely outside of the state lock loop
                if error_message:
                    print(f"[SERVER LOG] Rejected move from Player {player_id} in Col {col}: {error_message}")
                    send_json(conn, {"type": "error", "message": error_message})
                    continue

                # Broadcast authorized change to all active clients
                if broadcast_payload:
                    print(f"[SERVER LOG] Authorized Player {player_id} move in Col {col}, Row {row}.")
                    with clients_lock:
                        for c in connections:
                            send_json(c, broadcast_payload)

        except Exception as e:
            print(f"Server tracking log error for Player {player_id}: {e}")
            break

    print(f"Player {player_id} disconnected.")
    with clients_lock:
        if conn in connections:
            connections.remove(conn)
        for c in connections:
            send_json(c, {"type": "disconnect"})
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