import platform
from flask import Flask, request, jsonify
import threading
from utils.runner import TestCase
from utils.scenario import Scenario
from pusher import Pusher

app = Flask(__name__)
#socketio = SocketIO(app)

@app.route('/')
def welcome():
    return jsonify(message="Welcome")


@app.route('/status')
def status():
    return jsonify(
        system=platform.system(),
        release=platform.release(),
        version=platform.version()
    )

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    scenario = Scenario(data)
    result = scenario.do_test()

    return jsonify(data)
    # startT = threading.Thread(target=scenario.do_test(), args=())
    # startT.daemon = True


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
