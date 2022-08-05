from flask import Blueprint

from controllers.SettingsController import read_settings, write_setting

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route("/write", methods=(['POST']))
def handle_write_setting():
    return write_setting()

@settings_bp.route("/read")
def handle_read_settings():
    return read_settings()

