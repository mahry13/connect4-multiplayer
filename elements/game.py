import pygame
from client import Network
from elements.board import Board
from elements.player import Player

class GameUI:
    def __init__(self, player):
        self.PIECE_SIZE = 80  
        self.OFFSET = 60
        self.PIECE_OFFSET = 20
        self.BOARD_HEIGHT = 700
        self.PIECE_RADIUS = int(self.PIECE_SIZE / 2)

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Connect 4')

        self.screen = pygame.display.set_mode((800, 800))
        self.board_img = pygame.image.load("./graphics/board.png")
        self.font = pygame.font.SysFont('Arial', 30)
        self.yellow_piece = pygame.image.load("./graphics/wilson.png")
        self.red_piece = pygame.image.load("./graphics/house1.png")

        self.welcome_bg = pygame.image.load("./graphics/welcome.png")
        self.welcome_bg = pygame.transform.scale(self.welcome_bg, (800, 800))

        self.win_house = pygame.image.load("./graphics/win_house.jpg")
        self.win_house = pygame.transform.scale(self.win_house, (800, 800))

        self.win_wilson = pygame.image.load("./graphics/win_wilson.jpg")
        self.win_wilson = pygame.transform.scale(self.win_wilson, (800, 800))

        self.background = pygame.image.load("./graphics/background.png")
        self.background = pygame.transform.scale(self.background, (800, 800))
        self.init_ui(player)

        self.blink_timer = 0
        self.show_text = True

    def init_ui(self, player):
        self.screen.blit(self.background, (0, 0))
        self.draw_board()
        self.draw_player_info(player)
    
    def draw_player_info(self, current_player, local_player_id=None):
        pygame.draw.rect(self.screen, (255,255,255), [0, 0, 800, 100], 0)
        
        if local_player_id is not None and current_player.get_id() == local_player_id:
            text = "Your Turn!"
        else:
            text = "Current Player: " + current_player.get_name()
        text = self.font.render(text, True, (0,0,0))
        self.screen.blit(text, (50, 10))
        pygame.display.flip()
    
    def draw_win_screen(self, winner, local_player_id):
        # 1. Clean the upper row spacing area
        pygame.draw.rect(self.screen, (255,255,255), [0, 0, 800, 100], 0)

        if winner.get_id() == 0:
            self.screen.blit(self.win_house, (0, 0))
        else:
            self.screen.blit(self.win_wilson, (0, 0))
        
        pygame.draw.rect(self.screen, (255, 255, 255), [0, 0, 800, 100], 0)
        
        if winner.get_id() == local_player_id:
            text = "You won!!! Play again? (y | n)?"
        else:
            text = winner.get_name() + " won!!! Play again? (y | n)?"

        text = self.font.render(text, True, (0,0,0))
        self.screen.blit(text, (50, 10))
        pygame.display.flip()
        
    def get_piece_image(self, player):
        if player.get_id() == 0:
            return self.red_piece
        else:
            return self.yellow_piece
        
    def draw_welcome_screen(self):
        self.screen.blit(self.welcome_bg, (0, 0))

        title_font = pygame.font.SysFont('Arial', 60)
        small_font = pygame.font.SysFont('Arial', 30)
        tiny_font = pygame.font.SysFont('Arial', 15)

        title = title_font.render("Connect 4", True, (0, 0, 0))
        info = small_font.render("Press any key to play", True, (0, 0, 0))
        authors = tiny_font.render("Created by: Natalia Sarbiewska & Maria Galkowska", True, (0, 0, 0))

        self.screen.blit(authors, (30, 750))
        self.screen.blit(title, (300, 300))

        self.blink_timer += 1
        if self.blink_timer >= 30:  # speed
            self.show_text = not self.show_text
            self.blink_timer = 0

        if self.show_text:
            self.screen.blit(info, (297, 370))

        pygame.display.flip()

    def draw_board(self, player = None, row = -1, column = -1, selected_column=None):
        if player is not None and selected_column is not None:
            pygame.draw.rect(self.screen, (255,255,255), [0, self.OFFSET, 800, 80], 0) #[0, self.offset, 800, 80]
            piece_img = self.get_piece_image(player)
            self.screen.blit(piece_img,
              (self.OFFSET + self.PIECE_OFFSET * selected_column + self.PIECE_SIZE * selected_column, 
              self.OFFSET + 40 - self.PIECE_RADIUS)
            )

        if player is not None and row > -1:
            piece_img = self.get_piece_image(player)
            self.screen.blit(piece_img,
              (self.OFFSET + self.PIECE_OFFSET * column + self.PIECE_SIZE * column, 
              self.BOARD_HEIGHT - self.PIECE_SIZE * row - self.PIECE_OFFSET * row - self.PIECE_RADIUS)
            )

        self.screen.blit(self.board_img, (self.OFFSET - 10, self.OFFSET + 90))
        pygame.display.flip()

    def draw_disconnect(self):
        pygame.draw.rect(self.screen, (255, 0, 0), [0, 0, 800, 140], 0)
        text = self.font.render("Opponent disconnected! Press 'N' to quit.", True, (255, 255, 255))
        self.screen.blit(text, (50, 10))
        pygame.display.flip()

    def draw_waiting(self):
        pygame.draw.rect(self.screen, (0, 0, 255), [0, 0, 800, 100], 0)
        text = self.font.render("Waiting for opponent to connect...", True, (255, 255, 255))
        self.screen.blit(text, (50, 10))
        pygame.display.flip()


class Game:
    def __init__(self):
        self.network = Network()
        self.local_player_id = self.network.player_id

        self._current_player = 0
        self._selected_column = 0
        self._players = [Player(0), Player(1)]
        self._board = Board()
        self.game_ready = False
        self._gameUI = GameUI(self._players[self.local_player_id])

    def welcome_loop(self):
        self.start_welcome_music()
        waiting = True

        while waiting:
            self._gameUI.draw_welcome_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    pygame.mixer.music.fadeout(1000)
                    waiting = False
                    
        self._gameUI.init_ui(self.get_current_player())         

    def game_loop(self):
            update_ui = True
            done = False
            player_won = False
            opponent_disconnected = False

            self.start_game_music()

            while not done:
                # --- 1. LISTEN FOR OPPONENT'S DATA ---
                if not opponent_disconnected:
                    # FIX 1: Grab the parsed list of packets from our buffer
                    incoming_packets = self.network.receive_all_packets()
                    
                    # FIX 2: Iterate through every received message in sequence
                    for incoming_data in incoming_packets:
                        msg_type = incoming_data.get("type") 

                        # Handle disconnections
                        if msg_type == "disconnect":
                            opponent_disconnected = True
                            update_ui = True
                        
                        # Handle ready status
                        elif msg_type == "ready":
                            self.game_ready = True
                            opponent_disconnected = False
                            update_ui = True
                        
                        # Handle a restart request
                        elif msg_type == "restart_request":
                            player_won = False
                            self._current_player = 0  # reset turn to player 0
                            self.restart()
                            update_ui = True
                            
                        elif msg_type == "error":
                            error_msg = incoming_data.get("message")
                            print(f"[CLIENT LOG] Error from server: {error_msg}")
                            update_ui = True

                        elif msg_type == "move_success":
                            p_id = incoming_data.get("player_id")
                            column = incoming_data.get("column")
                            row = incoming_data.get("row")
                            has_won = incoming_data.get("won")

                            print(f"Player {p_id} placed a piece in Col {column}, Row {row}.")

                            self._board.place_piece(self.get_player(p_id), column, row)
                            self._gameUI.draw_board(self.get_player(p_id), row, column, self._selected_column)

                            if has_won:
                                player_won = True
                                update_ui = True
                            else:
                                self.switch_player()
                                update_ui = True

                # --- 2. HANDLE PLAYER INPUTS ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True

                    elif event.type == pygame.KEYUP:
                        # Play again options
                        if player_won or opponent_disconnected:
                            if event.key == 110: # 'N' Key
                                done = True
                            elif event.key in [121, 122] and not opponent_disconnected: # 'Y' Key
                                self.network.send({"type": "restart_request"})
                        else:
                            # Only allow keyboard input if the game is completely unblocked and it is OUR turn
                            if self.game_ready and self._current_player == self.local_player_id:
                                # LEFT arrow
                                if event.key == pygame.K_LEFT:
                                    self._selected_column = max(0, self._selected_column - 1)
                                # RIGHT arrow
                                elif event.key == pygame.K_RIGHT:
                                    self._selected_column = min(6, self._selected_column + 1)
                                # DROP (DOWN arrow or ENTER)
                                elif event.key in [pygame.K_DOWN, pygame.K_RETURN]:
                                    print(f"[CLIENT INPUT] Request to drop piece in Column {self._selected_column}")
                                    self.network.send({"column": self._selected_column})

                # Only track active hover/preview indicators when a player hasn't already won!
                if not player_won and not opponent_disconnected and self.game_ready:
                    self._gameUI.draw_board(self.get_current_player(), -1, -1, self._selected_column)

                # --- 3. REFRESH GENERAL GAME STATE UI OVERLAYS ---
                if update_ui:
                    if opponent_disconnected:
                        self._gameUI.draw_disconnect()
                    elif not self.game_ready:
                        self._gameUI.draw_waiting()
                    elif player_won:
                        self._gameUI.draw_win_screen(self.get_current_player(), self.network.player_id)
                    else:
                        self._gameUI.draw_player_info(self.get_current_player(), self.network.player_id)
                    update_ui = False

    def switch_player(self):
        self._current_player += 1
        self._current_player = self._current_player % 2

    def restart(self):
        self._board.clear()
        pygame.mixer.music.fadeout(1000)
        self.start_game_music()
        self._current_player = 0  
        self._selected_column = 0
        self._gameUI.init_ui(self.get_current_player())
        self._gameUI.init_ui(self.get_current_player())

    def get_board(self):
        return self._board

    def get_player(self, id):
        return self._players[id]

    def get_current_player(self):
        return self._players[self._current_player]

    def start_welcome_music(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            pygame.mixer.music.load("./sounds/house_intro.mp3")
            pygame.mixer.music.play(-1, 0.0)
        except pygame.error as e:
            print(f"Could not load music: {e}")

    def start_game_music(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        try:
            pygame.mixer.music.load("./sounds/house_game.mp3")
            pygame.mixer.music.play(-1, 0.0)
        except pygame.error as e:
            print(f"Could not load music: {e}")