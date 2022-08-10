from flask import Blueprint
from flask_cors import cross_origin
from controllers.OMRController import omr

omr_bp = Blueprint('omr_bp', __name__)

@omr_bp.route("/scan")
@cross_origin()
def handle_scan():
    return omr()