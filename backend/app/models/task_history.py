"""
Task History model for tracking task completion and performance
"""
from app import db
from datetime import datetime


class TaskHistory(db.Model):
    __tablename__ = 'task_history'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('team_members.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # 'assigned', 'completed', 'reassigned', etc.
    story_points = db.Column(db.Integer, nullable=True)
    actual_hours = db.Column(db.Integer, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    performance_score = db.Column(db.Float, nullable=True)  # 0-100 score based on speed/quality
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task', backref='history', foreign_keys=[task_id])
    member = db.relationship('TeamMember', backref='task_history', foreign_keys=[member_id])
    
    def to_dict(self):
        """Convert task history entry to dictionary"""
        return {
            'id': self.id,
            'taskId': self.task_id,
            'memberId': self.member_id,
            'action': self.action,
            'storyPoints': self.story_points,
            'actualHours': self.actual_hours,
            'completedDate': self.completed_date.isoformat() if self.completed_date else None,
            'performanceScore': self.performance_score,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TaskHistory {self.action} on task {self.task_id}>'

