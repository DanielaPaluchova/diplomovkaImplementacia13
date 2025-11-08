"""
Task model with PERT and RACI
"""
from app import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprints.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='To Do')  # To Do, In Progress, Done
    priority = db.Column(db.String(20), nullable=False, default='medium')  # high, medium, low
    type = db.Column(db.String(20), nullable=False, default='task')  # feature, bug, task
    story_points = db.Column(db.Integer, nullable=False, default=0)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    labels = db.Column(db.JSON, nullable=True)  # Array of labels
    complexity = db.Column(db.Integer, nullable=False, default=0)
    
    # PERT estimates (in hours)
    pert_optimistic = db.Column(db.Float, nullable=True)
    pert_most_likely = db.Column(db.Float, nullable=True)
    pert_pessimistic = db.Column(db.Float, nullable=True)
    pert_expected = db.Column(db.Float, nullable=True)  # Calculated: (O + 4M + P) / 6
    
    # RACI matrix (stored as JSON arrays of team member IDs)
    raci_responsible = db.Column(db.JSON, nullable=True)  # Array of IDs
    raci_accountable = db.Column(db.Integer, nullable=True)  # Single ID
    raci_consulted = db.Column(db.JSON, nullable=True)  # Array of IDs
    raci_informed = db.Column(db.JSON, nullable=True)  # Array of IDs
    
    # Gantt chart fields
    start_date = db.Column(db.DateTime, nullable=True)  # Task start date
    end_date = db.Column(db.DateTime, nullable=True)  # Task end date
    dependencies = db.Column(db.JSON, nullable=True)  # Array of task IDs that this task depends on
    
    # PERT diagram position overrides
    diagram_position_x = db.Column(db.Float, nullable=True)  # Manual position X (null = use auto-layout)
    diagram_position_y = db.Column(db.Float, nullable=True)  # Manual position Y (null = use auto-layout)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_pert_expected(self):
        """Calculate PERT expected time"""
        if self.pert_optimistic and self.pert_most_likely and self.pert_pessimistic:
            self.pert_expected = round((self.pert_optimistic + 4 * self.pert_most_likely + self.pert_pessimistic) / 6, 2)
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'projectId': self.project_id,
            'sprintId': self.sprint_id,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'type': self.type,
            'storyPoints': self.story_points,
            'dueDate': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'labels': self.labels or [],
            'complexity': self.complexity,
            'pert': {
                'optimistic': round(self.pert_optimistic, 2) if self.pert_optimistic is not None else None,
                'mostLikely': round(self.pert_most_likely, 2) if self.pert_most_likely is not None else None,
                'pessimistic': round(self.pert_pessimistic, 2) if self.pert_pessimistic is not None else None,
                'expected': round(self.pert_expected, 2) if self.pert_expected is not None else None
            },
            'raci': {
                'responsible': self.raci_responsible or [],
                'accountable': self.raci_accountable,
                'consulted': self.raci_consulted or [],
                'informed': self.raci_informed or []
            },
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'dependencies': self.dependencies or [],
            'diagramPositionX': self.diagram_position_x,
            'diagramPositionY': self.diagram_position_y
        }
    
    def __repr__(self):
        return f'<Task {self.name}>'

