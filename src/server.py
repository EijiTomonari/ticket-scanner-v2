from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<Hello, World!"

# Endpoint to write new settings to the config file


@app.route("/settings/write")
def write_settings():
    return "Write settings"

# Endpoint to read settings from the config file


@app.route("/settings/read")
def read_settings():
    return "Read settings"
