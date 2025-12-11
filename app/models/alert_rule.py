"""
Alert Rule model for configuring monitoring alerts.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from app import db


class AlertRule(db.Model):
    """
    Alert Rule model for defining monitoring thresholds and notifications.
    
    Attributes:
        id: Primary key
        ruche_id: Foreign key to ruche (hive)
        rule_type: Type of alert rule (e.g., 'temperature', 'weight', 'humidity')
        params: JSON parameters for the rule (thresholds, etc.)
        notify_in_app: Whether to notify in application
        notify_whatsapp: Whether to send WhatsApp notification
        whatsapp_number: WhatsApp number for notifications
        active: Whether the rule is active
    """
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True)
    ruche_id = Column(Integer, ForeignKey('ruches.id'), nullable=False)
    rule_type = Column(String(100), nullable=False)
    params = Column(JSON, nullable=True)
    notify_in_app = Column(Boolean, default=True, nullable=False)
    notify_whatsapp = Column(Boolean, default=False, nullable=False)
    whatsapp_number = Column(String(50), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    ruche = db.relationship('Ruche', back_populates='alert_rules')
    alerts = db.relationship('Alert', back_populates='rule', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AlertRule {self.id}: {self.rule_type} for Ruche {self.ruche_id}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'ruche_id': self.ruche_id,
            'rule_type': self.rule_type,
            'params': self.params,
            'notify_in_app': self.notify_in_app,
            'notify_whatsapp': self.notify_whatsapp,
            'whatsapp_number': self.whatsapp_number,
            'active': self.active
        }
