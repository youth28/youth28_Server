from flask import Flask
from flask_socketio import SocketIO

socket = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    from .main import bp as main_blueprint
    app.register_blueprint(main_blueprint)

    socket.init_app(app)
    return app
