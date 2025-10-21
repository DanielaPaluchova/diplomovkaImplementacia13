"""
Project Role model for team member permissions
"""
from app import db
from datetime import datetime


class ProjectRole(db.Model):
    __tablename__ = 'project_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    member_id = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='developer')  # owner, admin, developer, viewer
    can_edit = db.Column(db.Boolean, nullable=False, default=True)
    can_delete = db.Column(db.Boolean, nullable=False, default=False)
    can_manage_team = db.Column(db.Boolean, nullable=False, default=False)
    can_manage_sprints = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert project role to dictionary"""
        return {
            'memberId': self.member_id,
            'role': self.role,
            'permissions': {
                'canEdit': self.can_edit,
                'canDelete': self.can_delete,
                'canManageTeam': self.can_manage_team,
                'canManageSprints': self.can_manage_sprints
            }
        }
    
    def __repr__(self):
        return f'<ProjectRole {self.role} for member {self.member_id}>'

