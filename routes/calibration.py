from flask import Blueprint
from controllers.CalibrationController import barcodesVideoFeed

calibration_bp = Blueprint('calibration_bp', __name__)

@calibration_bp.route("/barcodes/feed")
def video_feed():
    return barcodesVideoFeed()