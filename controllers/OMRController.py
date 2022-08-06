import cv2
from flask import jsonify
import numpy as np
from models.Setting import Setting

def findBoxesArea(camera,OMR_FRAMES_OFFSET,OMR_BOXES_AREA_X1, OMR_BOXES_AREA_X2, OMR_BOXES_AREA_Y1, OMR_BOXES_AREA_Y2,OMR_CONTRAST,OMR_BRIGHTNESS):
    for i in range(0, OMR_FRAMES_OFFSET):
        ret, frame = camera.read()
    img = frame[OMR_BOXES_AREA_X1:OMR_BOXES_AREA_X2, OMR_BOXES_AREA_Y1:OMR_BOXES_AREA_Y2]
    img = cv2.convertScaleAbs(img, alpha=OMR_CONTRAST, beta=OMR_BRIGHTNESS)
    boxesArea = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return boxesArea

def findBoxesContours(img,OMR_BLUR_KENEL_SIZE,OMR_MAX_THRESHOLD,OMR_THRESHOLD_BLOCK_SIZE,OMR_THRESHOLD_C,OMR_BOX_MIN_WIDTH,OMR_BOX_MIN_HEIGHT,OMR_BOX_MIN_ASPECT_RATIO,OMR_BOX_MAX_ASPECT_RATIO):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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

    return boxesContours, thresh

def sort_contours(cnts, method="left-to-right"):
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return (cnts, boundingBoxes)

def processBoxes(contours, thresh,OMR_BOXES_PER_ROW,OMR_BOXES_ROWS,OMR_STANDARD_DEVIATION_THRESHOLD):
    productsContours = sort_contours(
        contours, method="top-to-bottom")[0]
    pixelValues = np.zeros((OMR_BOXES_ROWS, OMR_BOXES_PER_ROW), dtype=int)
    checked = np.zeros(OMR_BOXES_ROWS, dtype=int)
    for (q, i) in enumerate(np.arange(0, len(productsContours), OMR_BOXES_PER_ROW)):
        rowContours = sort_contours(productsContours[i:i + OMR_BOXES_PER_ROW])[0]

        for (j, c) in enumerate(rowContours):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)
            pixelValues[q][j] = total

    average = np.average(pixelValues)
    stDeviation = np.std(pixelValues)
    pixelThreshold = average + (stDeviation*OMR_STANDARD_DEVIATION_THRESHOLD)

    for (index, line) in enumerate(pixelValues):
        for value in line:
            if value >= pixelThreshold:
                checked[index] += 1

    return checked

def omr():
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
    OMR_FRAMES_OFFSET = app.config['OMR_FRAMES_OFFSET']

    with app.app_context():
        db_WIDTH = Setting.query.filter_by(name='OMR_CAMERA_WIDTH').first()
        db_HEIGHT = Setting.query.filter_by(name='OMR_CAMERA_HEIGHT').first()
        if db_WIDTH is not None and db_HEIGHT is not None:
            OMR_CAMERA_WIDTH = db_WIDTH.value
            OMR_CAMERA_HEIGHT = db_HEIGHT.value
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
        db_BOXES_PER_ROW = Setting.query.filter_by(name='OMR_BOXES_PER_ROW').first()
        db_BOXES_ROWS = Setting.query.filter_by(name='OMR_BOXES_ROWS').first()
        db_STANDARD_DEVIATION_THRESHOLD = Setting.query.filter_by(name='OMR_STANDARD_DEVIATION_THRESHOLD').first()
        if db_BOXES_PER_ROW is not None and db_BOXES_ROWS is not None and db_STANDARD_DEVIATION_THRESHOLD is not None:
            OMR_BOXES_PER_ROW = db_BOXES_PER_ROW.value
            OMR_BOXES_ROWS = db_BOXES_ROWS.value
            OMR_STANDARD_DEVIATION_THRESHOLD = db_STANDARD_DEVIATION_THRESHOLD.value
        db_FRAMES_OFFSET = Setting.query.filter_by(name='OMR_FRAMES_OFFSET').first()
        if db_FRAMES_OFFSET is not None:
            OMR_FRAMES_OFFSET = db_FRAMES_OFFSET.value
        

        #camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        camera = omrCamera
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, OMR_CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, OMR_CAMERA_HEIGHT)
        
    try:
        boxesArea = findBoxesArea(camera,OMR_FRAMES_OFFSET,OMR_BOXES_AREA_X1, OMR_BOXES_AREA_X2, OMR_BOXES_AREA_Y1, OMR_BOXES_AREA_Y2,OMR_CONTRAST,OMR_BRIGHTNESS)
        boxesContours, thresh = findBoxesContours(boxesArea,OMR_BLUR_KENEL_SIZE,OMR_MAX_THRESHOLD,OMR_THRESHOLD_BLOCK_SIZE,OMR_THRESHOLD_C,OMR_BOX_MIN_WIDTH,OMR_BOX_MIN_HEIGHT,OMR_BOX_MIN_ASPECT_RATIO,OMR_BOX_MAX_ASPECT_RATIO)
        checked = processBoxes(boxesContours, thresh,OMR_BOXES_PER_ROW,OMR_BOXES_ROWS,OMR_STANDARD_DEVIATION_THRESHOLD)
        return(jsonify({"message": checked.tolist(), "severity": "success"}),201)
    except Exception as e:
        return(jsonify({"message": e.__repr__(), "severity": "danger"}),401)