from flask import Flask
from flask_migrate import Migrate
from models.Setting import db
from routes.settings import settings_bp
from routes.calibration import calibration_bp

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(calibration_bp, url_prefix='/calibration')

@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    app.debug = True
    app.run()