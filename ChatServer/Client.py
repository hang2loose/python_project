import socket
import threading
import json


class Client:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def sendMsg(self):
    while True:
      temp = {
        "event" : "miss",
        "load" : input("")
      }

      self.sock.send(bytes(json.dumps(temp), 'utf-8'))

  def __init__(self):
    self.sock.connect(("127.0.0.1", 8080))

    input_thread = threading.Thread(target=self.sendMsg)
    input_thread.daemon = True
    input_thread.start()

    while True:
      data = self.sock.recv(1024)
      if not data:
        break
      print(str(data, 'utf-8'))


client = Client()