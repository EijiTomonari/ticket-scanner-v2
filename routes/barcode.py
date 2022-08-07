from flask import Blueprint
from flask_cors import cross_origin

from controllers.BarcodeController import scanBarcodes

barcode_bp = Blueprint('barcode_bp', __name__)

@barcode_bp.route("/scan")
@cross_origin()
def handle_scan():
    return scanBarcodes()