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
    # NOTE: tasks_completed and total_tasks are DEPRECATED database columns
    # They are now computed dynamically in to_dict() from the tasks relationship
    # progress is also computed dynamically from actual task counts
    tasks_completed = db.Column(db.Integer, nullable=False, default=0)  # DEPRECATED - use to_dict()
    total_tasks = db.Column(db.Integer, nullable=False, default=0)  # DEPRECATED - use to_dict()
    status = db.Column(db.String(50), nullable=False, default='In Progress')
    due_date = db.Column(db.DateTime, nullable=True)
    total_story_points = db.Column(db.Integer, nullable=False, default=0)
    estimated_duration = db.Column(db.Integer, nullable=False, default=0)  # in days
    team_member_ids = db.Column(db.JSON, nullable=True)  # Array of team member IDs
    
    # PERT diagram settings
    pert_manual_edges = db.Column(db.JSON, nullable=True)  # User-created connections separate from dependencies
    pert_layout_settings = db.Column(db.JSON, nullable=True)  # Zoom/pan state
    
    # RACI and PERT Configuration
    raci_weights = db.Column(db.JSON, nullable=True)  # RACI weights for combined formula
    pert_weights = db.Column(db.JSON, nullable=True)  # PERT formula weights
    max_story_points_per_person = db.Column(db.Integer, nullable=False, default=20)  # Maximum story points per person
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sprints = db.relationship('Sprint', backref='project', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    epics = db.relationship('Epic', backref='project', lazy=True, cascade='all, delete-orphan')
    roles = db.relationship('ProjectRole', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        """Convert project to dictionary"""
        # Always calculate task counts dynamically from actual tasks
        # Even if lazy loading hasn't triggered, we need to count tasks for accurate stats
        from app.models.task import Task
        
        # Query tasks for this project to ensure we have accurate counts
        all_project_tasks = Task.query.filter_by(project_id=self.id).all()
        total_tasks = len(all_project_tasks)
        tasks_completed = len([t for t in all_project_tasks if t.status == 'Done'])
        
        # Calculate progress dynamically
        progress = 0
        if total_tasks > 0:
            progress = int((tasks_completed / total_tasks) * 100)
        
        # Default RACI weights
        default_raci_weights = {
            'responsible': 0.6,
            'accountable': 0.45,
            'consulted': 0.3,
            'informed': 0.05
        }
        
        # Default PERT weights
        default_pert_weights = {
            'optimistic': 1,
            'mostLikely': 4,
            'pessimistic': 1
        }
        
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'icon': self.icon,
            'progress': progress,  # Computed dynamically from actual tasks
            'tasksCompleted': tasks_completed,  # Computed dynamically
            'totalTasks': total_tasks,  # Computed dynamically
            'status': self.status,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'totalStoryPoints': self.total_story_points,
            'estimatedDuration': self.estimated_duration,
            'teamMemberIds': self.team_member_ids or [],
            'pertManualEdges': self.pert_manual_edges or [],
            'pertLayoutSettings': self.pert_layout_settings or {},
            'raciWeights': self.raci_weights or default_raci_weights,
            'pertWeights': self.pert_weights or default_pert_weights,
            'maxStoryPointsPerPerson': self.max_story_points_per_person,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_details:
            result['sprints'] = [sprint.to_dict() for sprint in self.sprints]
            result['tasks'] = [task.to_dict() for task in self.tasks]
            result['roles'] = [role.to_dict() for role in self.roles]
        
        return result
    
    def __repr__(self):
        return f'<Project {self.name}>'

