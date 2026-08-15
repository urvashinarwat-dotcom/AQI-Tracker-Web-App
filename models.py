from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class AQIReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200), nullable=False)
    aqi = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    pm25 = db.Column(db.Float, nullable=True)
    pm10 = db.Column(db.Float, nullable=True)
    no2 = db.Column(db.Float, nullable=True)
    co = db.Column(db.Float, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "location": self.location,
            "aqi": self.aqi,
            "status": self.status,
            "pm25": self.pm25,
            "pm10": self.pm10,
            "no2": self.no2,
            "co": self.co,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if self.timestamp else None
        }


def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()