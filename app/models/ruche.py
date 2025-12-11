"""
Ruche (Hive) model with PostGIS geometry support.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from geoalchemy2 import Geometry
from app import db


class Ruche(db.Model):
    """
    Ruche (Hive) model representing individual beehives.
    
    Attributes:
        id: Primary key
        name: Hive name/identifier
        rucher_id: Foreign key to rucher (apiary)
        queen_info: JSON information about the queen bee
        created_at: Timestamp of creation
        geom: PostGIS Point geometry (location)
        active: Whether the hive is currently active
    """
    __tablename__ = 'ruches'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    rucher_id = Column(Integer, ForeignKey('ruchers.id'), nullable=True)
    queen_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    rucher = db.relationship('Rucher', back_populates='ruches')
    measurements = db.relationship('Measurement', back_populates='ruche', cascade='all, delete-orphan')
    alert_rules = db.relationship('AlertRule', back_populates='ruche', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', back_populates='ruche', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ruche {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'rucher_id': self.rucher_id,
            'queen_info': self.queen_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'active': self.active
        }
