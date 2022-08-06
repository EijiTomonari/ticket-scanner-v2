import cv2
from flask import Response
from pyzbar.pyzbar import decode
from config import BARCODES_AREA_X1, BARCODES_BRIGHTNESS, BARCODES_CONTRAST, OMR_BOX_MAX_ASPECT_RATIO, OMR_BOX_MIN_ASPECT_RATIO, OMR_CAMERA_ID, OMR_CONTRAST
from models.Setting import Setting
from flask_sqlalchemy import SQLAlchemy
import numpy as np
db = SQLAlchemy()

####################################################################################################
# Barcodes Functions                                                                                                
####################################################################################################

def streamBarcodesFeed():
    """
    It reads the camera, converts the image to grayscale, crops the image to the area where the barcodes
    are, decodes the barcodes, draws a rectangle around them, rotates the image, and then returns the
    image.
    """
    from app import app,barcodesCamera
    # Default settings
    BARCODES_AREA_X1 = app.config['BARCODES_AREA_X1']
    BARCODES_AREA_X2 = app.config['BARCODES_AREA_X2']
    BARCODES_AREA_Y1 = app.config['BARCODES_AREA_Y1']
    BARCODES_AREA_Y2 = app.config['BARCODES_AREA_Y2']
    BARCODES_CAMERA_ID = app.config['BARCODES_CAMERA_ID']
    BARCODES_CAMERA_WIDTH = app.config['BARCODES_CAMERA_WIDTH']
    BARCODES_CAMERA_HEIGHT = app.config['BARCODES_CAMERA_HEIGHT']
    BARCODES_CONTRAST = app.config['BARCODES_CONTRAST']
    BARCODES_BRIGHTNESS = app.config['BARCODES_BRIGHTNESS']
    with app.app_context():
        camera = barcodesCamera
        # Getting the camera width and height from the database. If it is not found, it will use the default
        # camera width and height
        db_WIDTH = Setting.query.filter_by(name='BARCODES_CAMERA_WIDTH').first()
        db_HEIGHT = Setting.query.filter_by(name='BARCODES_CAMERA_HEIGHT').first()
        if db_WIDTH is not None and db_HEIGHT is not None:
            BARCODES_CAMERA_WIDTH = db_WIDTH.value
            BARCODES_CAMERA_HEIGHT = db_HEIGHT.value
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, BARCODES_CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, BARCODES_CAMERA_HEIGHT)
        while True:
            with app.app_context():
                success, frame = camera.read()
                if not success:
                    break
                else:
                    # Getting the values from the database and assigning them to the variables.
                    db_CONTRAST = Setting.query.filter_by(name='BARCODES_CONTRAST').first()
                    db_BRIGHTNESS = Setting.query.filter_by(name='BARCODES_BRIGHTNESS').first()
                    db_X1 = Setting.query.filter_by(name='BARCODES_AREA_X1').first()
                    db_X2 = Setting.query.filter_by(name='BARCODES_AREA_X2').first()
                    db_Y1 = Setting.query.filter_by(name='BARCODES_AREA_Y1').first()
                    db_Y2 = Setting.query.filter_by(name='BARCODES_AREA_Y2').first()
                    if db_CONTRAST is not None and db_BRIGHTNESS is not None:
                        BARCODES_CONTRAST = db_CONTRAST.value
                        BARCODES_BRIGHTNESS = db_BRIGHTNESS.value
                    if db_X1 is not None and db_X2 is not None and db_Y1 is not None and db_Y2 is not None:
                        BARCODES_AREA_X1 = db_X1.value
                        BARCODES_AREA_X2 = db_X2.value
                        BARCODES_AREA_Y1 = db_Y1.value
                        BARCODES_AREA_Y2 = db_Y2.value 
                    
                    # Converting the image to grayscale, then it is cropping the image to the area
                    # where the barcodes are, then it is decoding the barcodes and drawing a rectangle
                    # around them.
                    frame = cv2.convertScaleAbs(frame, alpha=BARCODES_CONTRAST, beta=BARCODES_BRIGHTNESS)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = gray[BARCODES_AREA_X1:BARCODES_AREA_X2, BARCODES_AREA_Y1:BARCODES_AREA_Y2]
                    detectedBarcodes = decode(gray)
                    for barcode in detectedBarcodes:
                        (x, y, w, h) = barcode.rect
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 5)
                    frame = frame[BARCODES_AREA_X1:BARCODES_AREA_X2, BARCODES_AREA_Y1:BARCODES_AREA_Y2]
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def barcodesVideoFeed():          
    """
    It returns a response object that is a stream of images from the camera, with each image with
    detected barcodes
    :return: A Response object with a stream of images.
    """
    return Response(streamBarcodesFeed(), mimetype='multipart/x-mixed-replace; boundary=frame')

####################################################################################################
# OMR Functions                                                                                                
####################################################################################################

def cutBoxesArea(app, originalImage,OMR_BOXES_AREA_X1, OMR_BOXES_AREA_X2, OMR_BOXES_AREA_Y1, OMR_BOXES_AREA_Y2,OMR_CONTRAST,OMR_BRIGHTNESS):
    """
    It takes the original image, and cuts out a section of it, based on the coordinates of the OMR boxes
    area
    
    :param app: the flask app
    :param originalImage: the original image
    :param OMR_BOXES_AREA_X1: The X1 coordinate of the top left corner of the area where the boxes are
    located
    :param OMR_BOXES_AREA_X2: The width of the image
    :param OMR_BOXES_AREA_Y1: The Y coordinate of the top left corner of the boxes area
    :param OMR_BOXES_AREA_Y2: The bottom of the boxes area
    :return: the image that has been rotated.
    """
    with app.app_context():
        db_BRIGHTNESS = Setting.query.filter_by(name='OMR_BRIGHTNESS').first()
        db_CONTRAST = Setting.query.filter_by(name='OMR_CONTRAST').first()
        db_X1 = Setting.query.filter_by(name='OMR_BOXES_AREA_X1').first()
        db_X2 = Setting.query.filter_by(name='OMR_BOXES_AREA_X2').first()
        db_Y1 = Setting.query.filter_by(name='OMR_BOXES_AREA_Y1').first()
        db_Y2 = Setting.query.filter_by(name='OMR_BOXES_AREA_Y2').first()
        if db_X1 is not None and db_X2 is not None and db_Y1 is not None and db_Y2 is not None:
            OMR_BOXES_AREA_X1 = db_X1.value
            OMR_BOXES_AREA_X2 = db_X2.value
            OMR_BOXES_AREA_Y1 = db_Y1.value
            OMR_BOXES_AREA_Y2 = db_Y2.value
        if db_CONTRAST is not None and db_BRIGHTNESS is not None:
            OMR_CONTRAST = db_CONTRAST.value
            OMR_BRIGHTNESS = db_BRIGHTNESS.value
        image = originalImage[OMR_BOXES_AREA_X1:OMR_BOXES_AREA_X2,OMR_BOXES_AREA_Y1:OMR_BOXES_AREA_Y2]
        image = cv2.convertScaleAbs(image, alpha=OMR_CONTRAST, beta=OMR_BRIGHTNESS)
        boxesArea = cv2.rotate(image,cv2.ROTATE_90_COUNTERCLOCKWISE)
        boxesAreaGray = cv2.cvtColor(boxesArea, cv2.COLOR_BGR2GRAY)
        return boxesAreaGray

def findBoxesContours(
    app,
    boxesArea,
    OMR_BLUR_KENEL_SIZE,
    OMR_MAX_THRESHOLD,
    OMR_THRESHOLD_BLOCK_SIZE,
    OMR_THRESHOLD_C,
    OMR_BOX_MIN_WIDTH,
    OMR_BOX_MIN_HEIGHT,
    OMR_BOX_MIN_ASPECT_RATIO,
    OMR_BOX_MAX_ASPECT_RATIO):

    """
    It takes an image, finds the contours of the boxes in the image, and returns the image with the
    contours drawn on it
    
    :param app: the Flask app
    :param boxesArea: The image that contains the boxes
    :param OMR_BLUR_KENEL_SIZE: The size of the kernel used to blur the image
    :param OMR_MAX_THRESHOLD: The maximum value to use with the cv2.adaptiveThreshold() function
    :param OMR_THRESHOLD_BLOCK_SIZE: The size of the block used to calculate the threshold value
    :param OMR_THRESHOLD_C: This is the constant that is subtracted from the mean or weighted mean.
    Normally, it is positive but may be zero or negative as well
    :param OMR_BOX_MIN_WIDTH: Minimum width of the box
    :param OMR_BOX_MIN_HEIGHT: Minimum height of the box
    :param OMR_BOX_MIN_ASPECT_RATIO: The minimum aspect ratio of the boxes
    :param OMR_BOX_MAX_ASPECT_RATIO: Maximum aspect ratio of a box
    """
    
    with app.app_context():
        db_BLUR_KENEL_SIZE = Setting.query.filter_by(name='OMR_BLUR_KENEL_SIZE').first()
        db_MAX_THRESHOLD = Setting.query.filter_by(name='OMR_MAX_THRESHOLD').first()
        db_THRESHOLD_BLOCK_SIZE = Setting.query.filter_by(name='OMR_THRESHOLD_BLOCK_SIZE').first()
        db_THRESHOLD_C = Setting.query.filter_by(name='OMR_THRESHOLD_C').first()
        if db_BLUR_KENEL_SIZE is not None and db_MAX_THRESHOLD is not None and db_THRESHOLD_BLOCK_SIZE is not None and db_THRESHOLD_C is not None:
            OMR_BLUR_KENEL_SIZE = db_BLUR_KENEL_SIZE.value
            OMR_MAX_THRESHOLD = db_MAX_THRESHOLD.value
            OMR_THRESHOLD_BLOCK_SIZE = db_THRESHOLD_BLOCK_SIZE.value
            OMR_THRESHOLD_C = db_THRESHOLD_C.value
        db_MIN_WIDTH = Setting.query.filter_by(name='OMR_BOX_MIN_WIDTH').first()
        db_MIN_HEIGHT = Setting.query.filter_by(name='OMR_BOX_MIN_HEIGHT').first()
        db_MIN_ASPECT_RATIO = Setting.query.filter_by(name='OMR_BOX_MIN_ASPECT_RATIO').first()
        db_MAX_ASPECT_RATIO = Setting.query.filter_by(name='OMR_BOX_MAX_ASPECT_RATIO').first()
        if db_MIN_WIDTH is not None and db_MIN_HEIGHT is not None and db_MIN_ASPECT_RATIO is not None and db_MAX_ASPECT_RATIO is not None:
            OMR_BOX_MIN_WIDTH = db_MIN_WIDTH.value
            OMR_BOX_MIN_HEIGHT = db_MIN_HEIGHT.value
            OMR_BOX_MIN_ASPECT_RATIO = db_MIN_ASPECT_RATIO.value
            OMR_BOX_MAX_ASPECT_RATIO = db_MAX_ASPECT_RATIO.value

    imgDraw = boxesArea.copy()
    imgGray = boxesArea.copy()
    imgBlurred = cv2.GaussianBlur(imgGray, (OMR_BLUR_KENEL_SIZE, OMR_BLUR_KENEL_SIZE), 0)
    thresh = cv2.adaptiveThreshold(imgBlurred, OMR_MAX_THRESHOLD,
                                  cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, OMR_THRESHOLD_BLOCK_SIZE, OMR_THRESHOLD_C)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxesContours = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        aspectRatio = w / float(h)
        if w >= OMR_BOX_MIN_WIDTH and h >= OMR_BOX_MIN_HEIGHT and aspectRatio >= OMR_BOX_MIN_ASPECT_RATIO and aspectRatio <= OMR_BOX_MAX_ASPECT_RATIO:
            boxesContours.append(c)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(imgDraw, (x, y), (x + w, y + h),
                         (0, 0, 255), -1)
    return imgBlurred, thresh, imgDraw, contours,boxesContours

def sortContours(contours, method="left-to-right"):
    """
    The function takes in a list of contours and sorts them from left to right, right to left, top to
    bottom, or bottom to top
    
    :param contours: a list of contours
    :param method: The sorting method to use, defaults to left-to-right (optional)
    :return: a tuple of two lists. The first list contains the contours sorted from left to right. The
    second list contains the bounding boxes sorted from left to right.
    """
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in contours]
    (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),key=lambda b: b[1][i], reverse=reverse))
    return (contours, boundingBoxes)

def processBoxes(app,contours, boxesArea, thresh,OMR_BOXES_PER_ROW,OMR_BOXES_ROWS,OMR_STANDARD_DEVIATION_THRESHOLD):
    """
    It takes a thresholded image, finds the contours, sorts them, and then checks if the boxes are
    checked or not
    
    :param app: Flask app
    :param contours: the contours of the boxes
    :param boxesArea: The image with the boxes drawn on it
    :param thresh: the thresholded image
    :param OMR_BOXES_PER_ROW: The number of boxes per row
    :param OMR_BOXES_ROWS: The number of rows of boxes in the OMR sheet
    :param OMR_STANDARD_DEVIATION_THRESHOLD: This is the threshold for the standard deviation of the
    pixel values
    :return: the following:
    """
    with app.app_context():
        db_BOXES_PER_ROW = Setting.query.filter_by(name='OMR_BOXES_PER_ROW').first()
        db_BOXES_ROWS = Setting.query.filter_by(name='OMR_BOXES_ROWS').first()
        db_STANDARD_DEVIATION_THRESHOLD = Setting.query.filter_by(name='OMR_STANDARD_DEVIATION_THRESHOLD').first()
        if db_BOXES_PER_ROW is not None and db_BOXES_ROWS is not None and db_STANDARD_DEVIATION_THRESHOLD is not None:
            OMR_BOXES_PER_ROW = db_BOXES_PER_ROW.value
            OMR_BOXES_ROWS = db_BOXES_ROWS.value
            OMR_STANDARD_DEVIATION_THRESHOLD = db_STANDARD_DEVIATION_THRESHOLD.value

    try:
        productsContours = sortContours(contours,method="top-to-bottom")[0]
        pixelValues = np.zeros((OMR_BOXES_ROWS, OMR_BOXES_PER_ROW), dtype=int)
        checked = np.zeros(OMR_BOXES_ROWS, dtype=int)
        checkedBoxes = boxesArea.copy()
        checkedBoxesArea = boxesArea.copy()
        for (index, i) in enumerate(np.arange(0, len(productsContours), OMR_BOXES_PER_ROW)):
            rowContours = sortContours(productsContours[i:i + OMR_BOXES_PER_ROW])[0]
            for c in rowContours:
                color = (0, 0, 0)
                if index%2==0:
                    color = (255, 255, 255)
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(checkedBoxesArea, (x, y), (x + w, y + h),color, -1)
            for (j, c) in enumerate(rowContours):
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [c], -1, 255, -1)
                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                total = cv2.countNonZero(mask)
                pixelValues[index][j] = total
        average = np.average(pixelValues)
        stDeviation = np.std(pixelValues)
        pixelThreshold = average + (stDeviation*OMR_STANDARD_DEVIATION_THRESHOLD)

        for (index, line) in enumerate(pixelValues):
            for value in line:
                if value >= pixelThreshold:
                    checked[index] += 1

        for (q, i) in enumerate(np.arange(0, len(productsContours), OMR_BOXES_PER_ROW)):
            rowContours = sortContours(productsContours[i:i + OMR_BOXES_PER_ROW])[0]
            for (j, c) in enumerate(rowContours):
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [c], -1, 255, -1)
                if pixelValues[q][j] >= pixelThreshold:
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(checkedBoxes, (x, y), (x + w, y + h),
                                (0, 255, 63), 5)

        return checkedBoxesArea, checkedBoxes, checked
    except Exception as e:
        return boxesArea, boxesArea, []

def streamOMRFeed():

    from app import app, omrCamera

    # Default settings
    OMR_BOXES_AREA_X1 = app.config['OMR_BOXES_AREA_X1']
    OMR_BOXES_AREA_X2 = app.config['OMR_BOXES_AREA_X2']
    OMR_BOXES_AREA_Y1 = app.config['OMR_BOXES_AREA_Y1']
    OMR_BOXES_AREA_Y2 = app.config['OMR_BOXES_AREA_Y2']
    OMR_CAMERA_WIDTH = app.config['OMR_CAMERA_WIDTH']
    OMR_CAMERA_HEIGHT = app.config['OMR_CAMERA_HEIGHT']
    OMR_CONTRAST = app.config['OMR_CONTRAST']
    OMR_BRIGHTNESS = app.config['OMR_BRIGHTNESS']
    OMR_BLUR_KENEL_SIZE = app.config['OMR_BLUR_KENEL_SIZE']
    OMR_MAX_THRESHOLD = app.config['OMR_MAX_THRESHOLD']
    OMR_THRESHOLD_BLOCK_SIZE = app.config['OMR_THRESHOLD_BLOCK_SIZE']
    OMR_THRESHOLD_C = app.config['OMR_THRESHOLD_C']
    OMR_BOX_MIN_WIDTH = app.config['OMR_BOX_MIN_WIDTH']
    OMR_BOX_MIN_HEIGHT =  app.config['OMR_BOX_MIN_HEIGHT']
    OMR_BOX_MIN_ASPECT_RATIO = app.config['OMR_BOX_MIN_ASPECT_RATIO']
    OMR_BOX_MAX_ASPECT_RATIO = app.config['OMR_BOX_MAX_ASPECT_RATIO']
    OMR_BOXES_PER_ROW = app.config['OMR_BOXES_PER_ROW']
    OMR_BOXES_ROWS = app.config['OMR_BOXES_ROWS']
    OMR_STANDARD_DEVIATION_THRESHOLD = app.config['OMR_STANDARD_DEVIATION_THRESHOLD']

    # Getting the camera ID from the database. If it is not found, it will use the default camera ID.
    with app.app_context():
        camera = omrCamera
        db_WIDTH = Setting.query.filter_by(name='OMR_CAMERA_WIDTH').first()
        db_HEIGHT = Setting.query.filter_by(name='OMR_CAMERA_HEIGHT').first()
        if db_WIDTH is not None and db_HEIGHT is not None:
            OMR_CAMERA_WIDTH = db_WIDTH.value
            OMR_CAMERA_HEIGHT = db_HEIGHT.value
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, OMR_CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, OMR_CAMERA_HEIGHT)

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            boxesArea = cutBoxesArea(app, frame,OMR_BOXES_AREA_X1, OMR_BOXES_AREA_X2, OMR_BOXES_AREA_Y1, OMR_BOXES_AREA_Y2,OMR_CONTRAST,OMR_BRIGHTNESS)
            imgBlurred, threshold, detectedBoxes, contours,boxesContours = findBoxesContours(app, boxesArea,OMR_BLUR_KENEL_SIZE,
            OMR_MAX_THRESHOLD,OMR_THRESHOLD_BLOCK_SIZE,OMR_THRESHOLD_C,OMR_BOX_MIN_WIDTH,OMR_BOX_MIN_HEIGHT,OMR_BOX_MIN_ASPECT_RATIO,OMR_BOX_MAX_ASPECT_RATIO)
            checkedBoxesArea, checkedBoxes, checked = processBoxes(app,boxesContours, boxesArea, threshold,OMR_BOXES_PER_ROW,OMR_BOXES_ROWS,OMR_STANDARD_DEVIATION_THRESHOLD)
            firstLine = np.column_stack((boxesArea,imgBlurred,threshold,detectedBoxes,checkedBoxesArea,checkedBoxes))
            ret, buffer = cv2.imencode('.jpg', firstLine)
            firstLine = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + firstLine + b'\r\n')

def omrVideoFeed():
    """
    It returns a response object that is a stream of images that are the result of the function
    streamOMRBoxesAreaFeed()
    :return: A response object with the streamOMRBoxesAreaFeed() function as the body.
    """
    return Response(streamOMRFeed(), mimetype='multipart/x-mixed-replace; boundary=frame')
