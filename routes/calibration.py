from flask import Blueprint
from controllers.CalibrationController import barcodes_video_feed

calibration_bp = Blueprint('calibration_bp', __name__)

@calibration_bp.route("/barcodes/feed")
def video_feed():
    return barcodes_video_feed()