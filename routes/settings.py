from flask import Blueprint
from flask_cors import cross_origin

from controllers.SettingsController import read_settings, write_setting

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route("/write", methods=(['POST']))
@cross_origin()
def handle_write_setting():
    return write_setting()

@settings_bp.route("/read")
@cross_origin()
def handle_read_settings():
    return read_settings()

