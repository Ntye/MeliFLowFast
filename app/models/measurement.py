"""
Measurement model for sensor data from hives.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, JSON
from app import db


class Measurement(db.Model):
    """
    Measurement model for storing sensor data from hives.
    
    Attributes:
        id: Primary key
        ruche_id: Foreign key to ruche (hive)
        recorded_at: Timestamp when measurement was taken
        weight: Hive weight in kg
        temperature: Temperature in Celsius
        humidity: Humidity percentage
        signal: Signal strength
        raw: Raw JSON data from sensors
    """
    __tablename__ = 'measurements'
    
    id = Column(Integer, primary_key=True)
    ruche_id = Column(Integer, ForeignKey('ruches.id'), nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    weight = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    signal = Column(Float, nullable=True)
    raw = Column(JSON, nullable=True)
    
    # Relationship
    ruche = db.relationship('Ruche', back_populates='measurements')
    
    def __repr__(self):
        return f'<Measurement {self.id}: Ruche {self.ruche_id} at {self.recorded_at}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'ruche_id': self.ruche_id,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'weight': self.weight,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'signal': self.signal,
            'raw': self.raw
        }
