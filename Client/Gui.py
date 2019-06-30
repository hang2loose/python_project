import random
import socketio
from appJar import gui


class EventHandler:
    sio = socketio.Client()

    def __init__(self, functions: dict):
        global function_dict
        function_dict = functions
        self.sio.connect('http://localhost:8080')

    @sio.on('hit')
    def on_hit(self):
        function_dict['hit'].__call__(self)

    @sio.on('miss')
    def on_miss(self):
        function_dict['miss'].__call__(self)

    @sio.on('ship')
    def set_ship(self):
        function_dict['ship'].__call__(self.pos, self.orientation, self.size)

    def shoot_at(self, pos):
        self.sio.emit('shoot_at', pos)


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
            "set": self.shoot,
            "hit": self.hit_target,
            "miss": self.miss_target,
            "ship": self.set_ship
        }

        self.event = EventHandler(self.functions)

    def shoot(self, pos):
        self.event.shoot_at(pos)

    def hit_target(self, pos):
        self.gui.addCanvasImage("Target_Board",
                                self.coords[pos][0] + 16,
                                self.coords[pos][1] + 16,
                                "hit.gif")

    def miss_target(self, pos):
        self.gui.addCanvasImage("Target_Board",
                                self.coords[pos][0] + 16,
                                self.coords[pos][1] + 16,
                                "miss.gif")

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

    def draw_board(self):
        self.gui.startFrame("Ships", 1, 0)

        self.gui.addCanvas("Ships_Board")
        self.gui.setCanvasWidth("Ships_Board", 352)
        self.gui.setCanvasHeight("Ships_Board", 352)

        self.gui.addCanvasImage("Ships_Board", 192, 16, "top_bar.gif")
        self.gui.addCanvasImage("Ships_Board", 16, 192, "left_bar.gif")

        x = 16
        for row in range(10):
            x += 32
            y = 16
            for column in range(10):
                y += 32
                self.gui.addCanvasImage("Ships_Board", x, y, random.choice(self.water))
                self.coords.update({"{},{}".format(row, column): [x-16, y-16, x+16, y+16]})

        self.gui.stopFrame()

        self.gui.startFrame("Target", 1, 1)

        self.gui.addCanvas("Target_Board")
        self.gui.setCanvasWidth("Target_Board", 352)
        self.gui.setCanvasHeight("Target_Board", 352)

        self.gui.addCanvasImage("Target_Board", 160, 16, "top_bar.gif")
        self.gui.addCanvasImage("Target_Board", 336, 192, "right_bar.gif")

        x = -16
        for row in range(10):
            x += 32
            y = 16
            for column in range(10):
                y += 32
                self.gui.addCanvasImage("Target_Board", x, y, random.choice(self.water))
                self.coords.update({"{},{}".format(row, column): [x - 16, y - 16, x + 16, y + 16]})

        self.gui.setCanvasMap("Target_Board", self.shoot, self.coords)

        self.gui.stopFrame()

    def draw(self):
        self.draw_parameters()

        self.gui.startFrame("State", 0, 0, 2)
        self.gui.addLabel("Ships", "STRATEGY MAP", 0, 0)
        self.gui.addLabel("Target", "TARGET MAP", 0, 1)

        self.gui.getLabelWidget("Ships").config(font=("Helvetica", "20", "bold"))
        self.gui.setLabelAlign("Ships", "left")
        self.gui.setLabelSticky("Ships", "both")
        self.gui.getLabelWidget("Target").config(font=("Helvetica", "20", "bold"))
        self.gui.setLabelAlign("Target", "right")
        self.gui.setLabelSticky("Target", "both")
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
