import pygame

from client import Network
from elements.board import Board
from elements.player import Player
import time


#try making the balls fall down instead of just appearing in the right place, maybe with some animation?
#if an incorrect move is performed make the background of the screen pulsate in red for a moment, to indicate the error
#display our names, indexes numbers and title in a welcoming screen with a play button that takes us to the main game screen, maybe have some welcoming animation, like the pieces falling down one by one

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

        self.background = pygame.image.load("./graphics/background.png")
        self.background = pygame.transform.scale(self.background, (800, 800))
        self.init_ui(player)

        self.blink_timer = 0
        self.show_text = True

    def init_ui(self, player):
        self.screen.blit(self.background, (0, 0))
        self.draw_board()
        self.draw_player_info(player)
    
    def draw_player_info(self, player):
        pygame.draw.rect(self.screen, (255,255,255), [0, 0, 800, 100], 0)

        text = "Current Player: " + player.get_name()
        
        text = self.font.render(text, True, (0,0,0))
        self.screen.blit(text, (50, 10))

        pygame.display.flip()
    
    def draw_player_won(self, player):
        pygame.draw.rect(self.screen, (255,255,255), [0, 0, 800, 50], 0)

        text = player.get_name() + " won! Restart (y | n)?"
        
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

        #self.screen.blit(self.background, (0, 0))
        if player is not None and selected_column is not None:

            pygame.draw.rect(self.screen, (255,255,255), [0, self.OFFSET, 800, 80], 0)

            piece_img = self.get_piece_image(player)
            self.screen.blit(piece_img,
              (self.OFFSET + self.PIECE_OFFSET * selected_column + self.PIECE_SIZE * selected_column, #clear the screen
              self.OFFSET + 40 - self.PIECE_RADIUS)
            )

        if player is not None and row > -1:

            piece_img = self.get_piece_image(player)
            self.screen.blit(piece_img,
              (self.OFFSET + self.PIECE_OFFSET * column + self.PIECE_SIZE * column, #clear the screen
              self.BOARD_HEIGHT - self.PIECE_SIZE * row - self.PIECE_OFFSET * row - self.PIECE_RADIUS)
            )

        self.screen.blit(self.board_img, (self.OFFSET - 10, self.OFFSET + 90))

        pygame.display.flip()

    def draw_disconnect(self):
        pygame.draw.rect(self.screen, (255, 255, 255), [0, 0, 800, 100], 0)
        text = self.font.render("Opponent disconnected! Press 'N' to quit.", True, (255, 0, 0))
        self.screen.blit(text, (50, 10))
        pygame.display.flip()

    def draw_waiting(self):
        pygame.draw.rect(self.screen, (255, 255, 255), [0, 0, 800, 100], 0)
        text = self.font.render("Waiting for opponent to connect...", True, (0, 0, 255))
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
      row = -1
      column = -1

      self.start_game_music()

      while not done:
          # Listen for opponent's move
          if not opponent_disconnected:
              incoming_data = self.network.receive()
              if incoming_data:
                  if incoming_data.get("type") == "disconnect":
                      opponent_disconnected = True
                      update_ui = True
                  elif incoming_data.get("type") == "ready":
                      self.game_ready = True
                      opponent_disconnected = False
                      update_ui = True
                  elif self._current_player != self.local_player_id and not player_won:
                      column = incoming_data.get("column")
                      if column is not None:
                          row = self.get_next_open_row(column)
                          if row > -1:
                              self._selected_column = column
                              player_won = self.winning_move(self.get_current_player())
                              update_ui = True
          # check for player input events
          for event in pygame.event.get():
              if event.type == pygame.QUIT:
                  done = True

              elif event.type == pygame.KEYUP:
                  if player_won or opponent_disconnected:
                      # N key
                      if event.key == 110:
                          done = True
                      # Y key
                      elif event.key in [121, 122] and not opponent_disconnected:
                          player_won = False
                          done = False
                          self.restart()
                          update_ui = True
                  else:
                      # Only allow keyboard input if it's our turn
                      if self.game_ready and self._current_player == self.local_player_id:
                          # Try to insert to a column
                          if event.key == pygame.K_LEFT:
                              self._selected_column = max(0, self._selected_column - 1)
                          # RIGHT arrow
                          elif event.key == pygame.K_RIGHT:
                              self._selected_column = min(6, self._selected_column + 1)
                          # DROP (DOWN arrow or ENTER)
                          elif event.key in [pygame.K_DOWN, pygame.K_RETURN]:
                              column = self._selected_column
                              row = self.get_next_open_row(column)

                              if row > -1:
                                  self.network.send({"column": column})
                                  player_won = self.winning_move(self.get_current_player())
                                  update_ui = True

          self._gameUI.draw_board(self.get_current_player(), -1, -1, self._selected_column)

          # UI has to be updated
          if update_ui:
              self._gameUI.draw_board(self.get_current_player(), row, column, self._selected_column)
              if opponent_disconnected:
                  self._gameUI.draw_disconnect()
              elif not self.game_ready:
                  self._gameUI.draw_waiting()
              elif player_won:
                  self._gameUI.draw_player_won(self.get_current_player())
              else:
                  if row > -1:
                      self.switch_player()
                      row = -1
                  self._gameUI.draw_player_info(self.get_current_player())
              update_ui = False

  def switch_player(self):
    self._current_player += 1
    self._current_player = self._current_player % 2

  def restart(self):
    self._board.clear()
    pygame.mixer.music.fadeout(1000)
    self.start_game_music()
    self._gameUI.init_ui(self.get_current_player())

  def get_next_open_row(self, column):
    player=self.get_current_player()
    return self._board.get_next_open_row(player, column)

  def winning_move(self, player):
    return self._board.winning_move(player)

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
            pygame.mixer.music.load("house_intro.mp3")
            pygame.mixer.music.play(-1, 0.0)
        except pygame.error as e:
            print(f"Could not load music: {e}")

  def start_game_music(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
     
        try:
            pygame.mixer.music.load("house_game.mp3")
            pygame.mixer.music.play(-1, 0.0)
        except pygame.error as e:
            print(f"Could not load music: {e}")
