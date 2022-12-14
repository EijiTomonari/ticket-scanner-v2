import cv2
from flask import jsonify
from pyzbar.pyzbar import decode
from models.Setting import Setting

def scanBarcodes():
    from app import app,barcodesCamera
    with app.app_context():
        camera = barcodesCamera
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not camera.isOpened():
            return(jsonify({"message": "Could not initialize barcodes camera", "severity": "danger"}),401)
        iteration = 0
        while(iteration<2):
            success, frame = camera.read()
            if not success:
                return(jsonify({"message": "Could not read barcodes camera", "severity": "danger"}),401)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detectedBarcodes = decode(gray)
            iteration+=1
        if not detectedBarcodes:
            return(jsonify({"message": "Could not detect barcodes", "severity": "success"}),201)
        else:
            barcodes=[]
            for barcode in detectedBarcodes:
                if barcode.data != "" and barcode.type == "EAN13":
                    barcodes.append(barcode.data.decode("utf-8"))
            return(jsonify({"message": "Barcodes detected", "severity": "success", "barcodes": barcodes}),200)      