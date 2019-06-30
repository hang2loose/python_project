import random
import socketio
from appJar import gui


class EventHandler:
    sio = socketio.Client()

    def __init__(self, functions: dict):
        global function_dict
        function_dict = functions
        self.sio.connect('http://localhost:8080')

    def shoot_at(self, pos):
        self.sio.emit('shoot_at', pos)

    @sio.on('hit')
    def on_hit(payload):
        function_dict['action'].__call__('hit', payload, "Target_Board")

    @sio.on('miss')
    def on_miss(payload):
        function_dict['action'].__call__('miss', payload, "Target_Board")

    @sio.on('ship_hit')
    def ship_hit(payload):
        function_dict['action'].__call__('hit', payload, "Ship_Board")

    @sio.on('ship_miss')
    def ship_miss(payload):
        function_dict['action'].__call__('miss', payload, "Ship_Board")

    @sio.on('ship')
    def set_ship(payload):
        function_dict['ship'].__call__(payload.pos, payload.orientation, payload.size)


class GUI:
    def __init__(self, framework):
        self.gui = framework
        self.coords = {}
        self.state = "game"
        self.event_type = "shoot"

        self.water = [
            "dark.gif",
            "medium.gif",
            "light.gif"
        ]

        self.functions = {
            "action": self.action,
            "ship": self.set_ship
        }

        self.event = EventHandler(self.functions)

    def shoot(self, pos):
        self.event.shoot_at(pos)

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
        self.gui.setImageLocation("./Client/images")

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
        self.canvas_board("Ships_Board")
        self.gui.stopFrame()

        self.gui.startFrame("Target", 1, 1)
        self.canvas_board("Target_Board")
        self.gui.setCanvasMap("Target_Board", self.shoot, self.coords)
        self.gui.stopFrame()

    def label_with_properties(self, name, title, align, row, column):
        self.gui.addLabel(name, title, row, column)
        self.gui.getLabelWidget(name).config(font=("Helvetica", "20", "bold"))
        self.gui.setLabelAlign(name, align)
        self.gui.setLabelSticky(name, "both")

    def draw(self):
        self.draw_parameters()

        self.gui.startFrame("Map_Title", 0, 0, 2)
        self.label_with_properties("Ships", "STRATEGY MAP", "left", 0, 0)
        self.label_with_properties("Target", "TARGET MAP", "right", 0, 1)
        self.gui.stopFrame()

        self.draw_board()

        self.gui.setFramePadding("Ships", [10, 10])
        self.gui.setFramePadding("Target", [10, 10])

        self.gui.startLabelFrame("Logic", 2, 0, 2)
        self.gui.addLabel("l2", "Label 2")
        self.gui.stopLabelFrame()


app = gui()
GUI(app).draw()
app.go()
