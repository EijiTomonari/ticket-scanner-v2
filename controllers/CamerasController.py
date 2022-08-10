import cv2
from models.Setting import Setting

def initOMRCamera():
    """
    It's a function that initializes the camera
    :return: A camera object
    """
    from app import app
    OMR_CAMERA_ID = app.config['OMR_CAMERA_ID']
    with app.app_context():
        db_ID = Setting.query.filter_by(name='OMR_CAMERA_ID').first()
        if db_ID is not None:
            OMR_CAMERA_ID= db_ID.value
    camera = cv2.VideoCapture(OMR_CAMERA_ID, cv2.CAP_DSHOW)
    return camera

def initBarcodesCamera():
    from app import app
    BARCODES_CAMERA_ID = app.config['BARCODES_CAMERA_ID']
    with app.app_context():
        db_ID = Setting.query.filter_by(name='BARCODES_CAMERA_ID').first()
        if db_ID is not None:
            BARCODES_CAMERA_ID= db_ID.value
    camera = cv2.VideoCapture(BARCODES_CAMERA_ID, cv2.CAP_DSHOW)
    return camera