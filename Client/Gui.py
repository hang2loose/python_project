import sys, os
import random
import socketio
from appJar import gui


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2",os.path.abspath("."))

    return os.path.join(base_path, relative_path)


class EventHandler:
    sio = socketio.Client()

    def __init__(self, functions: dict):
        global function_dict
        function_dict = functions
        self.sio.connect('http://localhost:8080')

    def gui_loaded(self):
        self.sio.emit('gui_loaded')

    def shoot_at(self, pos):
        self.sio.emit('shoot_at', pos)

    @sio.on('game_over')
    def game_over(payload):
        function_dict['game_over'].__call__(payload)
        print(payload)

    @sio.on('player')
    def player_state(payload):
        function_dict['player'].__call__(payload)
        print('Player: ' + payload)

    @sio.on('turn')
    def player_state(payload):
        function_dict['turn'].__call__(payload)
        print('Turn: ' + payload)

    @sio.on('hit')
    def on_hit(payload):
        function_dict['action'].__call__('hit', payload, "Target_Board")

    @sio.on('miss')
    def on_miss(payload):
        function_dict['action'].__call__('miss', payload, "Target_Board")

    @sio.on('ship_hit')
    def ship_hit(payload):
        print("ship_hit")
        function_dict['action'].__call__('hit', payload, "Ship_Board")

    @sio.on('ship_miss')
    def ship_miss(payload):
        print("ship_miss")
        function_dict['action'].__call__('miss', payload, "Ship_Board")

    @sio.on('ship')
    def set_ship(payload):
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
        self.event.shoot_at(pos)
        self.turn('wait')

    def action(self, event, pos, board):
        self.gui.addCanvasImage(board,
                                self.coords[pos][0] + 16,
                                self.coords[pos][1] + 16,
                                "{}.gif".format(event))

    def set_ship(self, pos, orientation, size):
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
        self.gui.setTitle("Battleships")
        self.gui.setResizable(canResize=False)
        self.gui.setLocation("CENTER")
        self.gui.setBg("#3C3F41")
        self.gui.setFg("#BBBBBB")

        self.gui.setStretch("None")
        self.gui.setGuiPadding(100, 20)
        self.gui.setImageLocation(resource_path("images"))

    def canvas_board(self, board_name):
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
        self.gui.startFrame("Ships", 1, 0)
        self.canvas_board("Ship_Board")
        self.gui.stopFrame()

        self.gui.startFrame("Target", 1, 1)
        self.canvas_board("Target_Board")
        self.gui.setCanvasMap("Target_Board", self.shoot, self.coords)
        self.gui.stopFrame()

    def title_label(self, name, title, align, row, column):
        self.gui.addLabel(name, title, row, column)
        self.gui.getLabelWidget(name).config(font=("Helvetica", "20", "bold"))
        self.gui.setLabelAlign(name, align)
        self.gui.setLabelSticky(name, "both")

    def state_label(self, name, label):
        self.gui.addLabel(name, label, 3, 0, 2)
        self.gui.getLabelWidget(name).config(font=("Helvetica", "16"))
        self.gui.setLabelHeight(name, 5)
        self.gui.setLabelStretch(name, "both")
        self.gui.setLabelSticky(name, "nesw")
        self.gui.hideLabel(name)

    def player(self, event):
        if event == 'wait':
            self.gui.showLabel("Player")
        if event == 'start':
            self.gui.showLabel("Player")
            self.gui.showLabel("Turn")

    def turn(self, event):
        if event == 'turn':
            self.gui.hideLabel("Wait")
            self.gui.showLabel("Turn")
        if event == 'wait':
            self.gui.hideLabel("Turn")
            self.gui.showLabel("Wait")

    def game_over(self, event):
        if event == 'win':
            self.gui.addLabel("Win", "You Have Won", 0, 0, 2, 4)
            self.gui.getLabelWidget("Win").config(font=("Helvetica", "20", "bold"))
        if event == 'loose':
            self.gui.addLabel("Loose", "You Lost", 0, 0, 2, 4)
            self.gui.getLabelWidget("Loose").config(font=("Helvetica", "20", "bold"))

    def draw(self):
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


app = gui()
GUI(app).draw()
app.go()
