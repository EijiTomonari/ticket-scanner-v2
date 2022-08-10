from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Setting(db.Model):
    # It creates a class called Setting that inherits from db.Model. It also creates a table called
    # settings with columns id, name, and value.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer)

    def __repr__(self):
        return f'<Setting {self.name}>'

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value
        }
