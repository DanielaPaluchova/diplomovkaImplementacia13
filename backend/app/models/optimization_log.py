"""
Optimization Log model for tracking optimization operations
"""
from app import db
from datetime import datetime


class OptimizationLog(db.Model):
    __tablename__ = 'optimization_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    optimization_type = db.Column(db.String(50), nullable=False)  # 'auto', 'manual', 'split', 'merge', etc.
    proposals_count = db.Column(db.Integer, nullable=False, default=0)
    applied_count = db.Column(db.Integer, nullable=False, default=0)
    scope = db.Column(db.String(20), nullable=True)  # 'current_sprint', 'all_sprints', 'backlog'
    results = db.Column(db.JSON, nullable=True)  # Detailed results of what was applied
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    project = db.relationship('Project', backref='optimization_logs', foreign_keys=[project_id])
    
    def to_dict(self):
        """Convert optimization log to dictionary"""
        return {
            'id': self.id,
            'projectId': self.project_id,
            'optimizationType': self.optimization_type,
            'proposalsCount': self.proposals_count,
            'appliedCount': self.applied_count,
            'scope': self.scope,
            'results': self.results or {},
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OptimizationLog {self.optimization_type} on project {self.project_id}>'

