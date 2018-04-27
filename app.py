import platform
from flask import Flask, request, jsonify

from utils.runner import TestCase

app = Flask(__name__)


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
    testcase = TestCase(data)
    result = testcase.do_test()
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
