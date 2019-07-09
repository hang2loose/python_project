import sys, os
import random
import socketio
from appJar import gui


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2",os.path.abspath("."))

    return os.path.join(base_path, relative_path)


# Function pointers for GUI functions
function_dict = {}
# Game room name send by server
game_room = None


# Sending and listening for events from and to the server
class EventHandler:
    # Initialize socket-io client
    sio = socketio.Client()

    def __init__(self, functions: dict):
        function_dict.update(functions)
        # Connect to server
        self.sio.connect('http://192.168.0.1:8080')

    def gui_loaded(self):
        """ Send gui loaded event to server """
        self.sio.emit('gui_loaded', game_room)

    def shoot_at(self, pos):
        """
        Send shoot at position event to server
        :param pos: 'x,y' position string
        """
        self.sio.emit('shoot_at', {'pos': pos, 'game_room': game_room})

    @sio.on('game_room')
    def game_room(payload):
        """
        Listen for which game room the client is connected to
        :param payload: message send from server
        """
        global game_room
        game_room = payload

    @sio.on('game_over')
    def game_over(payload):
        """
        Listen for the game over event
        :param payload: message send from server
        """
        function_dict['game_over'].__call__(payload)
        print(payload)

    @sio.on('player')
    def player_state(payload):
        """
        Listen for second player joined clients game
        :param payload: message send from server
        """
        function_dict['player'].__call__(payload)
        print('Player: ' + payload)

    @sio.on('turn')
    def player_state(payload):
        """
        Listen for clients turn event
        :param payload: message send from server
        """
        function_dict['turn'].__call__(payload)
        print('Turn: ' + payload)

    @sio.on('hit')
    def on_hit(payload):
        """
        Listen for response from server when shot hit enemy ship
        :param payload: message send from server
        """
        function_dict['action'].__call__('hit', payload, "Target_Board")

    @sio.on('miss')
    def on_miss(payload):
        """
        Listen for response from server when shot missed
        :param payload: message send from server
        """
        function_dict['action'].__call__('miss', payload, "Target_Board")

    @sio.on('ship_hit')
    def ship_hit(payload):
        """
        Listen for response from server when the enemy hit client ship
        :param payload: message send from server
        """
        print("ship_hit")
        function_dict['action'].__call__('hit', payload, "Ship_Board")

    @sio.on('ship_miss')
    def ship_miss(payload):
        """
        Listen for response from server when the enemy missed
        :param payload: message send from server
        """
        print("ship_miss")
        function_dict['action'].__call__('miss', payload, "Ship_Board")

    @sio.on('ship')
    def set_ship(payload):
        """
        Listen for initial ship placement from server
        :param payload: message send from server
        """
        print("setting ship....")
        function_dict['ship'].__call__(payload["pos"], payload["orientation"], payload["size"])


class GUI:
    def __init__(self, framework):
        self.gui = framework
        self.coords = {}

        self.water = [
            "dark.gif",
            "medium.gif",
            "light.gif"
        ]

        self.functions = {
            "action": self.action,
            "ship": self.set_ship,
            "player": self.player,
            "turn": self.turn,
            "game_over": self.game_over
        }

        self.event = EventHandler(self.functions)

    def shoot(self, pos):
        """
        Relay shoot at event to EventHandler for processing and change State Label
        :param pos: 'x,y' position string
        """
        self.event.shoot_at(pos)
        self.turn('wait')

    def action(self, event, pos, board):
        """
        Manipulate canvas to visualize hits and misses
        :param event: hit, miss, ship_hit or ship_miss
        :param pos: 'x,y' position string
        :param board: update Target_board or Ship_board
        """
        self.gui.addCanvasImage(board,
                                self.coords[pos][0] + 16,
                                self.coords[pos][1] + 16,
                                "{}.gif".format(event))

    def set_ship(self, pos, orientation, size):
        """
        Setup the ships on Ship_board canvas
        :param pos: 'x,y' position string
        :param orientation: (h)orizontal or (v)ertical
        :param size: integer length of ship
        """
        self.gui.addCanvasImage("Ship_Board",
                                self.coords[pos][0] + 16,
                                self.coords[pos][1] + 16,
                                "ship.gif")
        if orientation == 'h':
            ship_coords = -16
            for length in range(size):
                ship_coords += 32
                self.gui.addCanvasImage("Ship_Board",
                                        self.coords[pos][0] + ship_coords,
                                        self.coords[pos][1] + 16,
                                        "ship.gif")
        else:
            ship_coords = -16
            for length in range(size):
                ship_coords += 32
                self.gui.addCanvasImage("Ship_Board",
                                        self.coords[pos][0] + 16,
                                        self.coords[pos][1] + ship_coords,
                                        "ship.gif")

    def draw_parameters(self):
        """
        General parameters to setup the GUI window
        """
        self.gui.setTitle("Battleships")
        self.gui.setResizable(canResize=False)
        self.gui.setLocation("CENTER")
        self.gui.setBg("#3C3F41")
        self.gui.setFg("#BBBBBB")

        self.gui.setStretch("None")
        self.gui.setGuiPadding(100, 20)
        self.gui.setImageLocation(resource_path("images"))

    def canvas_board(self, board_name):
        """
        Setup for the canvas game board
        :param board_name: string
        """
        self.gui.addCanvas(board_name)
        self.gui.setCanvasWidth(board_name, 352)
        self.gui.setCanvasHeight(board_name, 352)
        self.gui.addCanvasImage(board_name, 192, 16, "top_bar.gif")
        self.gui.addCanvasImage(board_name, 16, 192, "left_bar.gif")
        x = 16
        for row in range(10):
            x += 32
            y = 16
            for column in range(10):
                y += 32
                self.gui.addCanvasImage(board_name, x, y, random.choice(self.water))
                self.coords.update({"{},{}".format(row, column): [x - 16, y - 16, x + 16, y + 16]})

    def draw_board(self):
        """
        Draw the game boards
        """
        self.gui.startFrame("Ships", 1, 0)
        self.canvas_board("Ship_Board")
        self.gui.stopFrame()

        self.gui.startFrame("Target", 1, 1)
        self.canvas_board("Target_Board")
        self.gui.setCanvasMap("Target_Board", self.shoot, self.coords)
        self.gui.stopFrame()

    def title_label(self, name, title, align, row, column):
        """
        Draw the title for the two canvas boards
        :param name: name of the label as string
        :param title: title string
        :param align: alignment in label
        :param row: row of window element grid
        :param column: column of window element grid
        """
        self.gui.addLabel(name, title, row, column)
        self.gui.getLabelWidget(name).config(font=("Helvetica", "20", "bold"))
        self.gui.setLabelAlign(name, align)
        self.gui.setLabelSticky(name, "both")

    def state_label(self, name, label):
        """
        Configure the state labels shown at the bottom of the game window
        :param name: name of the label as string
        :param label: content string
        """
        self.gui.addLabel(name, label, 3, 0, 2)
        self.gui.getLabelWidget(name).config(font=("Helvetica", "16"))
        self.gui.setLabelHeight(name, 5)
        self.gui.setLabelStretch(name, "both")
        self.gui.setLabelSticky(name, "nesw")
        self.gui.hideLabel(name)

    def player(self, event):
        """
        Set "wait for second player" label
        :param event: 'wait' or 'start'
        """
        if event == 'wait':
            self.gui.showLabel("Player")
        if event == 'start':
            self.gui.showLabel("Player")
            self.gui.showLabel("Turn")

    def turn(self, event):
        """
        Set label for who's turn it is
        :param event: 'turn' or 'wait'
        """
        if event == 'turn':
            self.gui.hideLabel("Wait")
            self.gui.showLabel("Turn")
        if event == 'wait':
            self.gui.hideLabel("Turn")
            self.gui.showLabel("Wait")

    def game_over(self, event):
        """
        Set "game over" label
        :param event: 'win' or 'loose'
        """
        if event == 'win':
            self.gui.addLabel("Win", "You Have Won", 0, 0, 2, 4)
            self.gui.getLabelWidget("Win").config(font=("Helvetica", "20", "bold"))
        if event == 'loose':
            self.gui.addLabel("Loose", "You Lost", 0, 0, 2, 4)
            self.gui.getLabelWidget("Loose").config(font=("Helvetica", "20", "bold"))

    def draw(self):
        """
        Draw all game frames in on function
        """
        self.draw_parameters()

        self.gui.startFrame("Map_Title", 0, 0, 2)
        self.title_label("Ships", "STRATEGY MAP", "left", 0, 0)
        self.title_label("Target", "TARGET MAP", "right", 0, 1)
        self.gui.stopFrame()

        self.draw_board()

        self.gui.setFramePadding("Ships", [10, 10])
        self.gui.setFramePadding("Target", [10, 10])

        self.state_label("Player", "Waiting for Player")
        self.state_label("Turn", "Shoot the Enemy Ships!")
        self.state_label("Wait", "Waiting for Turn")

        self.event.gui_loaded()


# Initialize GUI window
app = gui()
GUI(app).draw()
app.go()
