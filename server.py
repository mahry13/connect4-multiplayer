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

def handle_client(conn, player_id):
    global current_turn, game_active
    conn.sendall(json.dumps({"player_id": player_id}).encode('utf-8'))

    while True:
        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                break

            data = json.loads(raw_data.decode('utf-8'))
            msg_type = data.get("type")

            if msg_type == "restart_request":
                with game_state_lock:
                    reset_shared_game()
                with clients_lock:
                    for c in connections:
                        c.sendall(json.dumps({"type": "restart_request"}).encode('utf-8'))
                continue

            if "column" in data:
                col = data["column"]

                with game_state_lock:
                    if not game_active:
                        conn.sendall(json.dumps({"type": "error", "message": "Game over! Waiting for restart."}).encode('utf-8'))
                        continue
                        
                    if current_turn != player_id:
                        conn.sendall(json.dumps({"type": "error", "message": "Not your turn!"}).encode('utf-8'))
                        continue

                    # validate space on shared board
                    row = -1
                    for r in range(6):
                        if shared_board[r][col] == -1:
                            row = r
                            break

                    if row == -1:
                        # column was full
                        conn.sendall(json.dumps({"type": "error", "message": "Column full!"}).encode('utf-8'))
                        continue

                    # make a move on shared board
                    shared_board[row][col] = player_id
                    has_won = winning_move(shared_board, player_id)
                    
                    # Package state payload
                    broadcast_payload = json.dumps({
                        "type": "move_success",
                        "player_id": player_id,
                        "column": col,
                        "row": row,
                        "won": has_won
                    }).encode('utf-8')

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
        # tell about the disconnect
        for c in connections:
            try:
                c.sendall(json.dumps({"type": "disconnect"}).encode('utf-8'))
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
                            c.sendall(json.dumps({"type": "ready"}).encode('utf-8'))
                        except Exception:
                            pass
            else:
                conn.close()

if __name__ == "__main__":
    start_server()