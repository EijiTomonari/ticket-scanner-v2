from flask import Blueprint

from controllers.OMRController import omr

omr_bp = Blueprint('omr_bp', __name__)

@omr_bp.route("/scan")
def handle_scan():
    return omr()