"""
Experiment model for research data
"""
from app import db
from datetime import datetime


class Experiment(db.Model):
    __tablename__ = 'experiments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    hypothesis = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='planning')  # planning, running, completed, cancelled
    methodology = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    participants = db.Column(db.Integer, nullable=False, default=0)
    
    # Results (stored as JSON)
    results = db.Column(db.JSON, nullable=True)  # { success: bool, improvement: number, confidence: number }
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert experiment to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'hypothesis': self.hypothesis,
            'status': self.status,
            'methodology': self.methodology,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'participants': self.participants,
            'results': self.results
        }
    
    def __repr__(self):
        return f'<Experiment {self.name}>'

