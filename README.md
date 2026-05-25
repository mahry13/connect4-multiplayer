# **Multiplayer Game of Connect 4**

Concurrent and Distributed Processing 2026

Maria Gałkowska  
Natalia Sarbiewska 

## 

## I) Game Description

“Connect Four \[...\] is a game in which the players choose a color and then take turns dropping colored tokens into a six-row, seven-column vertically suspended grid. The pieces fall straight down, occupying the lowest available space within the column. The objective of the game is to be the first to form a horizontal, vertical, or diagonal line of four of one's own tokens.”1

Visualization of possible final states of the game with a vertical, horizontal or diagonal win:

## II) File Structure

Below is a detailed explanation of each folder and key files:

**Root Scripts**

* *connect4\_console\_ver.py* – Runs the singleplayer version of the game implemented in Command Line.  
* *connect4.py* – Runs the multiplayer version of the game with GUI implemented.  
* *client.py* – Contains the Network class; handles the socket network connection on the client side, sends column drop requests to the server and receives messages asynchronously; described in more detail in section IV.  
* *server.py* – Starts server, hosts the shared board protected with locks, restarts it, handles client requests and checks for winning moves; described in more detail in section IV.

---

## **elements folder**

* *board.py* – Contains Board class; It manages the underlying 6x7 game matrix structure for both the client and the server, tracks open rows, places player tokens onto the board and checks for winners.  
* *game.py* – Contains GameUI class (handles Pygame graphic renders, asset loading and House/Wilson win screens) and Game class (manages local inputs, audio streams, and network event parsing).  
* *player.py* – Contains Player class; maintains individual player profiles, tracks their IDs and names.

---

## **sounds folder**

Contains .mp3 files used as intro and game music.  
---

## **graphics folder**

Contains .png and .jpg files used for player, board and different background representations.

## III) Our GUI Implementation

When joining a new game players are welcomed by a welcome screen with intro background music. After a key is pressed, both the screen and the background music change. If only one player joins the game they are asked to wait for their opponent, after both players have successfully connected they can start the match. 

Welcome and waiting screen

Players can use LEFT and RIGHT arrows to position their token above the desired column and DOWN arrow to drop their token onto the board. 

Game screen

If an incorrect key is pressed, a message will pop up on the screen informing them of the possible actions. Players will also be alerted if they try to make a move while it’s their opponent’s turn.

Incorrect actions screens

If one of them manages to form a line of four tokens both of them are moved to the winner screen with the winner announced. From there they can decide whether they want to play again \- press Y, or quit \- press N. 

Winner screen

Players can also exit the game at any point during the match by closing the window. If one of them exits the game, their opponent is informed about that and instructed to also exit the game by pressing N.

Disconnected screen

## IV) Concurrent Programming Methods

### **TCP Socket Stream  and Data Serialization**

For our network transport layer, we chose TCP sockets (*socket.SOCK\_STREAM*). Since Connect 4 is a turn-based game we need to have a guarantee that the packets will arrive. If a packet got dropped or arrived out of order, the players could end up with different board states. We use structured JSON dictionaries for all client-server communications. Here’s how the communication process looks like:

1. Every time a client or server sends a data dictionary, it converts it to a string using *json.dumps().*  
2. We append a newline character (*\\n*) to the end of the string as a delimiter.  
3. The data is encoded into bytes and sent over the socket using *sendall*().  
4. The receiver reads chunks into a string buffer and splits them by *\\n* to process each packet individually.

### **Threading**

* **Implementation:** Uses *threading.Thread* to scale up connection handling.  
* **Methods:**  
  * *start\_server()* \- Spawns a new independent execution thread for every connecting client.  
  * *handle\_client()* \- Worker thread task assigned to each player to handle incoming data streams asynchronously.  
* **Purpose:** Allows the server to process concurrent TCP reads and writes simultaneously for multiple clients without blocking incoming connections.

### **Mutual Exclusion**

* **Implementation:** Uses *threading.Lock()* wrapped in thread-safe context managers (*with lock:*).  
* **Our Locks:**  
  * *game\_state\_lock* \- Guards the shared board grid and active game flags. Ensures that multi-threaded column checking, piece placement, and win condition checks happen atomically.  
  * *clients*\_lock \- Protects the global list of active client sockets. Prevents race conditions when broadcasting data or removing a player from the network pool upon a disconnection.

### **Non-blocking Client Communication**

* **Implementation:** Network loop with non-blocking socket state flags.  
* **Methods:**  
  * *socket.setblocking(False) \-* Configured right before polling to prevent network calls from hanging the thread.  
  * *receive\_all\_packets()* \- Continuously reads non-blocking network chunks into a persistent data buffer without freezing user input or lowering frame update speeds.

## V) Libraries Used

**External Libraries:**

* *pygame* \- Handles the graphics \- loads the House/Wilson and background images, tracks keyboard inputs and plays the music.  
* *numpy* – Used for managing multi-dimensional arrays and grids in the CL version of the game.

### **Python Built-in Libraries:**

* *socket* – Creates the network connection pipeline allowing the client and server to communicate over the network.  
* *json* – Converts game data into text strings so it can be sent through the network sockets.  
* *threading* – Lets the server run multiple connections at once so both players can play simultaneously without lag.

## VI) Contributions

Maria

* **Console version implementation** \- game logic, win \- checking  
* **Enhancing the GUI** \- background images, information about authors, appropriate messages, and error banners  
* **Server implementation** \- establishing a connection, basic client handling, bidirectional client communication using JSON payloads  
* **Server/client extension** \- debugging, handling server crashes, closing server, implementing background threading  
* **Code cleaning** \- redundant code cleaning, adding comments, and restructuring functions  
* **Testing**

Natalia

* **Initial GUI implementation** \- integrated assets: background graphics, player representations, and background music.  
* **README.md** **Documentation** \- created detailed project documentation  
* **Client implementation** \- Implemented the client-side network class, managing non-blocking sockets and the split stream buffer processing loop  
* **Server/client extension** \- debugging, handling clients connecting from different machines, implementing a mock Player, shared resources and locks.  
* **Testing**

