from flask import Flask
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from controllers.CamerasController import initBarcodesCamera, initOMRCamera
from models.Setting import db
from routes.settings import settings_bp
from routes.calibration import calibration_bp
from routes.barcode import barcode_bp
from routes.omr import omr_bp
from waitress import serve

app = Flask(__name__)
cors = CORS(app)
app.config.from_object('config')
app.config['CORS_HEADERS'] = 'Content-Type'

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(calibration_bp, url_prefix='/calibration')
app.register_blueprint(barcode_bp, url_prefix='/barcodes')
app.register_blueprint(omr_bp, url_prefix='/omr')

omrCamera = initOMRCamera()
barcodesCamera = initBarcodesCamera()

@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    # app.debug = True
    # app.run()
    serve(app, host='127.0.0.1', port=5000,threads=8)