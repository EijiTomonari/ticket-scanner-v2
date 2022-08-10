from flask import Blueprint
from flask_cors import cross_origin
from controllers.CalibrationController import barcodesVideoFeed, boxesAreaVideoFeed, omrVideoFeed

calibration_bp = Blueprint('calibration_bp', __name__)

@calibration_bp.route("/barcodes/feed")
@cross_origin()
def handleBarcodesVideoFeed():
    return barcodesVideoFeed()

@calibration_bp.route("/omr/feed")
@cross_origin()
def handleOMRVideoFeed():
    return omrVideoFeed()

@calibration_bp.route("/omr/boxesarea/feed")
@cross_origin()
def handleOMRBoxesAreaVideoFeed():
    return boxesAreaVideoFeed()

