from flask import Blueprint
from controllers.CalibrationController import barcodesVideoFeed, boxesAreaVideoFeed, omrVideoFeed

calibration_bp = Blueprint('calibration_bp', __name__)

@calibration_bp.route("/barcodes/feed")
def handleBarcodesVideoFeed():
    return barcodesVideoFeed()

@calibration_bp.route("/omr/feed")
def handleOMRVideoFeed():
    return omrVideoFeed()

@calibration_bp.route("/omr/boxesarea/feed")
def handleOMRBoxesAreaVideoFeed():
    return boxesAreaVideoFeed()

