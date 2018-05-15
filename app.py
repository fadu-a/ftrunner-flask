import platform
from flask import Flask, request, jsonify
from celery import Celery
import settings
from utils.scenario import Scenario

app = Flask(__name__)
app.config.from_object(settings)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@celery.task(name="tasks.start_fio_test")
def start_fio_test(data):
    scenario = Scenario(data)
    scenario.do_test()

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
    result = start_fio_test.delay(data)
    print(data)
    return jsonify(message="start fio")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
