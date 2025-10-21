"""
Team Member model
"""
from app import db
from datetime import datetime


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(100), nullable=False)  # Team role (e.g. "Frontend Developer")
    system_role = db.Column(db.String(20), nullable=True)  # admin, manager, developer, viewer
    avatar = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='offline')  # online, busy, away, offline
    active_projects = db.Column(db.Integer, nullable=False, default=0)
    workload = db.Column(db.Integer, nullable=False, default=0)  # 0-100
    skills = db.Column(db.JSON, nullable=True)  # Array of skills
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert team member to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'systemRole': self.system_role,
            'avatar': self.avatar,
            'status': self.status,
            'activeProjects': self.active_projects,
            'workload': self.workload,
            'skills': self.skills or []
        }
    
    def __repr__(self):
        return f'<TeamMember {self.name}>'

