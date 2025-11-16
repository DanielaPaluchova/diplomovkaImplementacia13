"""
RACI Weights Configuration Model
Global configuration for RACI weights used across all projects
"""
from app import db
from datetime import datetime


class RaciWeightsConfig(db.Model):
    __tablename__ = 'raci_weights_config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # RACI Weights for Workload Calculation
    responsible_workload = db.Column(db.Float, nullable=False, default=1.0)
    accountable_workload = db.Column(db.Float, nullable=False, default=0.1)
    consulted_workload = db.Column(db.Float, nullable=False, default=0.05)
    informed_workload = db.Column(db.Float, nullable=False, default=0.01)
    
    # RACI Weights for Adjusted Duration Calculation
    responsible_duration = db.Column(db.Float, nullable=False, default=1.0)
    accountable_duration = db.Column(db.Float, nullable=False, default=0.1)
    consulted_duration = db.Column(db.Float, nullable=False, default=0.05)
    informed_duration = db.Column(db.Float, nullable=False, default=0.01)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_or_create():
        """Get the singleton configuration or create it with defaults"""
        config = RaciWeightsConfig.query.first()
        if not config:
            config = RaciWeightsConfig(
                responsible_workload=1.0,
                accountable_workload=0.1,
                consulted_workload=0.05,
                informed_workload=0.01,
                responsible_duration=1.0,
                accountable_duration=0.1,
                consulted_duration=0.05,
                informed_duration=0.01
            )
            db.session.add(config)
            db.session.commit()
        return config
    
    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            'id': self.id,
            'workload': {
                'responsible': self.responsible_workload,
                'accountable': self.accountable_workload,
                'consulted': self.consulted_workload,
                'informed': self.informed_workload
            },
            'duration': {
                'responsible': self.responsible_duration,
                'accountable': self.accountable_duration,
                'consulted': self.consulted_duration,
                'informed': self.informed_duration
            },
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_from_dict(self, data):
        """Update configuration from dictionary"""
        if 'workload' in data:
            workload = data['workload']
            self.responsible_workload = workload.get('responsible', self.responsible_workload)
            self.accountable_workload = workload.get('accountable', self.accountable_workload)
            self.consulted_workload = workload.get('consulted', self.consulted_workload)
            self.informed_workload = workload.get('informed', self.informed_workload)
        
        if 'duration' in data:
            duration = data['duration']
            self.responsible_duration = duration.get('responsible', self.responsible_duration)
            self.accountable_duration = duration.get('accountable', self.accountable_duration)
            self.consulted_duration = duration.get('consulted', self.consulted_duration)
            self.informed_duration = duration.get('informed', self.informed_duration)
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<RaciWeightsConfig id={self.id}>'

