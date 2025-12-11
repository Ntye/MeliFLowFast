"""
Rucher (Apiary) model with PostGIS geometry support.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from geoalchemy2 import Geometry
from app import db


class Rucher(db.Model):
    """
    Rucher (Apiary) model representing beekeeping locations.
    
    Attributes:
        id: Primary key
        name: Apiary name
        description: Description of the apiary
        geom: PostGIS Point or Polygon geometry
        created_at: Timestamp of creation
    """
    __tablename__ = 'ruchers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    geom = Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    ruches = db.relationship('Ruche', back_populates='rucher')
    
    def __repr__(self):
        return f'<Rucher {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
