import socket
import pynput
from gevent import pywsgi
from flask_sockets import Sockets
from flask import Flask, request, render_template
from geventwebsocket.handler import WebSocketHandler


app = Flask(__name__)
sockets = Sockets(app)
mouse = pynput.mouse.Controller()


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/mouse/get/", methods=["GET"])
def getMousePosition():
    # y, x
    return str(int(mouse.position[0])) + "," + str(int(mouse.position[1])) 


@sockets.route('/mouse/set/')
def setMouse(ws):
    while not ws.closed:
        message = ws.receive()
        if message is not None:
            if message.startswith("move"):
                print("mouse move")
                xy = message[10:].split(",")
                mouse.position = (float(xy[1]), float(xy[0]))
            if message.startswith("scroll"):
                print("mouse scroll")
                xy = message[10:].split(",")
                mouse.scroll(float(xy[1]), float(xy[0]))
            ws.send("success")
        else:
            print("no receive")


@app.route("/mouse/click/", methods=["GET"])
def clickMouse():
    ms = request.args.get("mouse")
    print("mouse click " + ms)
    if ms == "left": 
        mouse.click(pynput.mouse.Button.left)
    else:
        mouse.click(pynput.mouse.Button.right)
    return "success"


def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == "__main__":
    # app.run("0.0.0.0", "8000", debug=True)
    server = pywsgi.WSGIServer(("0.0.0.0", 8000), app, handler_class=WebSocketHandler)
    print("server start at")
    print("http://{}:8000".format(getIp()))
    print("请在局域网另一个设备进行访问，可将那个设备作为本设备的触控板")
    print("注意请将设备顺时针旋转90度使用")
    server.serve_forever()