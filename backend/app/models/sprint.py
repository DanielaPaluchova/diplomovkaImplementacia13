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
    task_ids = db.Column(db.JSON, nullable=True)  # Deprecated - computed from tasks relationship
    
    # Optimization fields
    capacity = db.Column(db.Integer, nullable=False, default=100)  # Maximum story points capacity
    planned_story_points = db.Column(db.Integer, nullable=False, default=0)  # Total SP planned
    velocity = db.Column(db.Float, nullable=False, default=0.0)  # Actual velocity (completed SP)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to get tasks in this sprint
    tasks = db.relationship('Task', backref='sprint', lazy=True, foreign_keys='Task.sprint_id')
    
    def to_dict(self):
        """Convert sprint to dictionary"""
        # Dynamically compute task_ids from tasks relationship
        task_ids = [task.id for task in self.tasks]
        
        # For completed sprints, use stored values (preserved at completion time)
        # since incomplete tasks are moved to backlog and no longer in tasks
        if self.status == 'completed' and self.total_tasks > 0:
            total_tasks = self.total_tasks
            completed_tasks = self.completed_tasks
        else:
            total_tasks = len(self.tasks)
            completed_tasks = sum(1 for task in self.tasks if task.completed or task.status == 'Done')
        
        return {
            'id': self.id,
            'projectId': self.project_id,
            'name': self.name,
            'goal': self.goal,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'totalTasks': total_tasks,  # Computed from tasks
            'completedTasks': completed_tasks,  # Computed from tasks
            'taskIds': task_ids,  # Computed from tasks
            'capacity': self.capacity,
            'plannedStoryPoints': self.planned_story_points,
            'velocity': self.velocity
        }
    
    def __repr__(self):
        return f'<Sprint {self.name}>'

