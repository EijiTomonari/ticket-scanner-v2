from flask import Blueprint
from controllers.CalibrationController import barcodesVideoFeed, omrBoxesAreaVideoFeed

calibration_bp = Blueprint('calibration_bp', __name__)

@calibration_bp.route("/barcodes/feed")
def handleBarcodesVideoFeed():
    return barcodesVideoFeed()

@calibration_bp.route("/omr/boxes-area/feed")
def handleOMRBoxesAreaVideoFeed():
    return omrBoxesAreaVideoFeed()
