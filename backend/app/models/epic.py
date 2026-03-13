"""
Epic model for strategic planning
"""
from app import db
from datetime import datetime


class Epic(db.Model):
    __tablename__ = 'epics'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Epic status
    status = db.Column(db.String(50), nullable=False, default='to_do')  # to_do, in_progress, completed
    
    # Epic owner/assignee (team member, not user)
    owner_id = db.Column(db.Integer, db.ForeignKey('team_members.id', ondelete='SET NULL'), nullable=True)
    
    # Priority
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
    
    # Labels/Tags (JSON array)
    labels = db.Column(db.JSON, nullable=True)  # Array of string labels
    
    # Dates
    start_date = db.Column(db.Date, nullable=True)
    target_date = db.Column(db.Date, nullable=True)
    
    # PERT estimates (in days) - for the epic itself
    pert_optimistic = db.Column(db.Float, nullable=True)
    pert_most_likely = db.Column(db.Float, nullable=True)
    pert_pessimistic = db.Column(db.Float, nullable=True)
    pert_expected = db.Column(db.Float, nullable=True)  # Calculated: (O + 4M + P) / 6
    
    # Epic dependencies (JSON array of epic IDs)
    dependencies = db.Column(db.JSON, nullable=True)  # Array of epic IDs that this epic depends on
    
    # Business metadata
    business_value = db.Column(db.Integer, nullable=False, default=0)  # Business value score
    target_release = db.Column(db.String(100), nullable=True)  # Target release version/date
    
    # PERT diagram position
    diagram_position_x = db.Column(db.Float, nullable=True)  # Manual position X (null = use auto-layout)
    diagram_position_y = db.Column(db.Float, nullable=True)  # Manual position Y (null = use auto-layout)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='epic', lazy=True, foreign_keys='Task.epic_id')
    owner = db.relationship('TeamMember', backref='owned_epics', lazy=True, foreign_keys=[owner_id])
    
    def calculate_pert_expected(self):
        """Calculate PERT expected time"""
        if self.pert_optimistic and self.pert_most_likely and self.pert_pessimistic:
            self.pert_expected = round((self.pert_optimistic + 4 * self.pert_most_likely + self.pert_pessimistic) / 6, 2)
    
    def to_dict(self, include_tasks=False):
        """Convert epic to dictionary"""
        result = {
            'id': self.id,
            'projectId': self.project_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'ownerId': self.owner_id,
            'owner': self.owner.to_dict() if self.owner else None,
            'priority': self.priority,
            'labels': self.labels or [],
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'targetDate': self.target_date.isoformat() if self.target_date else None,
            'pert': {
                'optimistic': round(self.pert_optimistic, 2) if self.pert_optimistic is not None else None,
                'mostLikely': round(self.pert_most_likely, 2) if self.pert_most_likely is not None else None,
                'pessimistic': round(self.pert_pessimistic, 2) if self.pert_pessimistic is not None else None,
                'expected': round(self.pert_expected, 2) if self.pert_expected is not None else None
            },
            'dependencies': self.dependencies or [],
            'businessValue': self.business_value,
            'targetRelease': self.target_release,
            'diagramPositionX': self.diagram_position_x,
            'diagramPositionY': self.diagram_position_y,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_tasks:
            # Include tasks that belong to this epic
            result['tasks'] = [task.to_dict() for task in self.tasks]
            
            # Calculate total story points and progress
            total_sp = sum(task.story_points for task in self.tasks)
            completed_sp = sum(task.story_points for task in self.tasks if task.status == 'Done')
            progress = int((completed_sp / total_sp) * 100) if total_sp > 0 else 0
            
            result['totalStoryPoints'] = total_sp
            result['completedStoryPoints'] = completed_sp
            result['progress'] = progress
        
        return result
    
    def __repr__(self):
        return f'<Epic {self.name}>'
