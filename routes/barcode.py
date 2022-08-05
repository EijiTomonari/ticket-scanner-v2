from flask import Blueprint

from controllers.BarcodeController import scanBarcodes

barcode_bp = Blueprint('barcode_bp', __name__)

@barcode_bp.route("/scan")
def handle_scan():
    return scanBarcodes()