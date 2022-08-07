from flask import jsonify, request
from models.Setting import Setting
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def write_setting():
    """
    If the request method is POST, then get the name and value from the request form, and if the name
    and value are not None, then add the name and value to the database
    :return: The return value from the function is a tuple of the form (response, status, headers) and
    is created by using the jsonify() function.
    """
    if request.method == 'POST':
        try:
            settingName = request.form['name']
            value = float(request.form['value'])
            if settingName is None or value is None:
                return jsonify({'error': 'Bad request'}), 400
            setting = Setting.query.filter_by(name=settingName).first()
            if setting is None:
                setting = Setting(name=settingName, value=value)
            setting.name = settingName
            setting.value = value
            local_object = db.session.merge(setting)
            db.session.add(local_object)
            db.session.commit()
            return jsonify({'message': 'Setting added'}), 201
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Method not allowed'}), 405

def read_settings():
    """
    It takes all the settings from the database, converts them to JSON, and then puts them into a
    dictionary.
    :return: A JSON object with the settings.
    """
    settings = Setting.query.all()
    settingsObject = {}
    json_list = [i.toJSON() for i in settings]
    for setting in json_list:
        settingsObject[setting['name']] = setting
    return jsonify(settingsObject)