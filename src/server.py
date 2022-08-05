import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import json

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'config/config.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer)

    def __repr__(self):
        return f'<Setting {self.name}>'

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value
        }


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
    """
    It takes all the settings from the database, converts them to JSON, and then puts them into a
    dictionary.
    :return: A JSON object with the settings.
    """
    settings = Setting.query.all()
    settingsObject = {}
    json_list = [i.toJSON() for i in settings]
    for setting in json_list:
        settingsObject[setting['name']] = setting
    print(settingsObject)
    return jsonify(settingsObject)
