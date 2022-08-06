import cv2
from flask import jsonify
from pyzbar.pyzbar import decode
from models.Setting import Setting

def scanBarcodes():
    from app import app
    with app.app_context():
        BARCODES_CAMERA_ID = Setting.query.filter_by(name='BARCODES_CAMERA_ID').first()
        if BARCODES_CAMERA_ID is None:
            BARCODES_CAMERA_ID = app.config['BARCODES_CAMERA_ID']
        camera = cv2.VideoCapture(BARCODES_CAMERA_ID.value, cv2.CAP_DSHOW)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not camera.isOpened():
            return(jsonify({"message": "Could not initialize barcodes camera", "severity": "danger"}),401)
        iteration = 0
        while(iteration<3):
            success, frame = camera.read()
            if not success:
                return(jsonify({"message": "Could not read barcodes camera", "severity": "danger"}),401)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detectedBarcodes = decode(gray)
            iteration+=1
        if not detectedBarcodes:
            return(jsonify({"message": "Could not detect barcodes", "severity": "danger"}),401)
        else:
            barcodes=[]
            for barcode in detectedBarcodes:
                if barcode.data != "" and barcode.type == "EAN13":
                    barcodes.append(barcode.data.decode("utf-8"))
            camera.release()
            return(jsonify({"message": "Barcodes detected", "severity": "success", "barcodes": barcodes}),200)      