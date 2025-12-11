"""
Alert model for triggered alerts.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, JSON
from app import db


class Alert(db.Model):
    """
    Alert model for storing triggered alerts.
    
    Attributes:
        id: Primary key
        rule_id: Foreign key to alert_rule
        ruche_id: Foreign key to ruche (hive)
        triggered_at: Timestamp when alert was triggered
        payload: JSON payload with alert details
        sent_whatsapp: Whether WhatsApp notification was sent
    """
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('alert_rules.id'), nullable=False)
    ruche_id = Column(Integer, ForeignKey('ruches.id'), nullable=False)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    payload = Column(JSON, nullable=True)
    sent_whatsapp = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    rule = db.relationship('AlertRule', back_populates='alerts')
    ruche = db.relationship('Ruche', back_populates='alerts')
    
    def __repr__(self):
        return f'<Alert {self.id}: Rule {self.rule_id} at {self.triggered_at}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'ruche_id': self.ruche_id,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'payload': self.payload,
            'sent_whatsapp': self.sent_whatsapp
        }
