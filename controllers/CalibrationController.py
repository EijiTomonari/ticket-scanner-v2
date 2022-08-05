import cv2
from flask import Response
from pyzbar.pyzbar import decode


def barcodes_video_feed():
    print("test")
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
                   
    return Response(streamBarcodesFeed(), mimetype='multipart/x-mixed-replace; boundary=frame')