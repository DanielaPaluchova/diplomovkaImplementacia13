"""
Sprint model
"""
from app import db
from datetime import datetime


class Sprint(db.Model):
    __tablename__ = 'sprints'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    goal = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='planned')  # planned, active, completed
    total_tasks = db.Column(db.Integer, nullable=False, default=0)
    completed_tasks = db.Column(db.Integer, nullable=False, default=0)
    task_ids = db.Column(db.JSON, nullable=True)  # Array of task IDs in this sprint
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert sprint to dictionary"""
        return {
            'id': self.id,
            'projectId': self.project_id,
            'name': self.name,
            'goal': self.goal,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'totalTasks': self.total_tasks,
            'completedTasks': self.completed_tasks,
            'taskIds': self.task_ids or []
        }
    
    def __repr__(self):
        return f'<Sprint {self.name}>'

