"""
Project model
"""
from app import db
from datetime import datetime


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    template = db.Column(db.String(100), nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    progress = db.Column(db.Integer, nullable=False, default=0)  # 0-100
    tasks_completed = db.Column(db.Integer, nullable=False, default=0)
    total_tasks = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False, default='In Progress')
    due_date = db.Column(db.DateTime, nullable=True)
    total_story_points = db.Column(db.Integer, nullable=False, default=0)
    estimated_duration = db.Column(db.Integer, nullable=False, default=0)  # in days
    team_member_ids = db.Column(db.JSON, nullable=True)  # Array of team member IDs
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sprints = db.relationship('Sprint', backref='project', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    roles = db.relationship('ProjectRole', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        """Convert project to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'icon': self.icon,
            'progress': self.progress,
            'tasksCompleted': self.tasks_completed,
            'totalTasks': self.total_tasks,
            'status': self.status,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'totalStoryPoints': self.total_story_points,
            'estimatedDuration': self.estimated_duration,
            'teamMemberIds': self.team_member_ids or [],
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_details:
            result['sprints'] = [sprint.to_dict() for sprint in self.sprints]
            result['tasks'] = [task.to_dict() for task in self.tasks]
            result['roles'] = [role.to_dict() for role in self.roles]
        
        return result
    
    def __repr__(self):
        return f'<Project {self.name}>'

