"""
Activity Log model for tracking user actions across the application
"""
from app import db
from datetime import datetime


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(80), nullable=False)  # page/route identifier
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)  # task_id, epic_id, etc.
    details = db.Column(db.JSON, nullable=True)
    route = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='activity_logs', foreign_keys=[user_id])
    project = db.relationship('Project', backref='activity_logs', foreign_keys=[project_id])

    def to_dict(self):
        """Convert activity log to dictionary"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'userName': self.user.name if self.user else None,
            'userEmail': self.user.email if self.user else None,
            'action': self.action,
            'entityType': self.entity_type,
            'projectId': self.project_id,
            'projectName': self.project.name if self.project else None,
            'entityId': self.entity_id,
            'details': self.details or {},
            'route': self.route,
            'ipAddress': self.ip_address,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<ActivityLog {self.action} by user {self.user_id}>'
