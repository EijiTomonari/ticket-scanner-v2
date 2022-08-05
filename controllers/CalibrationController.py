import cv2
from flask import Response
from pyzbar.pyzbar import decode
from models.Setting import Setting
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def streamBarcodesFeed():
    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detectedBarcodes = decode(gray)
            for barcode in detectedBarcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 5)
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def barcodesVideoFeed():          
    return Response(streamBarcodesFeed(), mimetype='multipart/x-mixed-replace; boundary=frame')

def streamOMRBoxesAreaFeed():
    from app import app
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            with app.app_context():
                OMR_BOXES_AREA_X1 = Setting.query.filter_by(name='OMR_BOXES_AREA_X1').first()
                OMR_BOXES_AREA_X2 = Setting.query.filter_by(name='OMR_BOXES_AREA_X2').first()
                OMR_BOXES_AREA_Y1 = Setting.query.filter_by(name='OMR_BOXES_AREA_Y1').first()
                OMR_BOXES_AREA_Y2 = Setting.query.filter_by(name='OMR_BOXES_AREA_Y2').first()
                image = frame[OMR_BOXES_AREA_X1.value:OMR_BOXES_AREA_X2.value,OMR_BOXES_AREA_Y1.value:OMR_BOXES_AREA_Y2.value]
                boxesArea = cv2.rotate(image,cv2.ROTATE_90_COUNTERCLOCKWISE)
                ret, buffer = cv2.imencode('.jpg', boxesArea)
                boxesArea = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + boxesArea + b'\r\n')

def omrBoxesAreaVideoFeed():
    return Response(streamOMRBoxesAreaFeed(), mimetype='multipart/x-mixed-replace; boundary=frame')