from flask import Flask

from config import PYZBARNAME

app = Flask(__name__)
app.config.from_object('config')


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Endpoint to write new settings to the config file


@app.route("/settings/write")
def write_settings():
    app.config.update(
        PYZBARNAME='New cool name'
    )
    return app.config['PYZBARNAME']

# Endpoint to read settings from the config file


@app.route("/settings/read")
def read_settings():
    return app.config['PYZBARNAME']
