"""
Teams API endpoints
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.team_member import TeamMember
from app.utils.auth import token_required
from datetime import datetime

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/', methods=['GET'])
@token_required
def get_teams():
    """Get all team members"""
    try:
        team_members = TeamMember.query.all()
        return jsonify([member.to_dict() for member in team_members]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get team members', 'message': str(e)}), 500


@teams_bp.route('/<int:member_id>', methods=['GET'])
@token_required
def get_team_member(member_id):
    """Get single team member"""
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        return jsonify(member.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get team member', 'message': str(e)}), 500


@teams_bp.route('/', methods=['POST'])
@token_required
def create_team_member():
    """Create new team member"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('email') or not data.get('role'):
            return jsonify({'error': 'Name, email, and role are required'}), 400
        
        # Check if email already exists
        if TeamMember.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        member = TeamMember(
            name=data['name'],
            email=data['email'],
            role=data['role'],
            system_role=data.get('systemRole'),
            avatar=data.get('avatar', 'https://cdn.quasar.dev/img/avatar.png'),
            status=data.get('status', 'offline'),
            workload=data.get('workload', 0),
            skills=data.get('skills', [])
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify(member.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create team member', 'message': str(e)}), 500


@teams_bp.route('/<int:member_id>', methods=['PUT'])
@token_required
def update_team_member(member_id):
    """Update team member"""
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            member.name = data['name']
        if 'email' in data:
            member.email = data['email']
        if 'role' in data:
            member.role = data['role']
        if 'systemRole' in data:
            member.system_role = data['systemRole']
        if 'avatar' in data:
            member.avatar = data['avatar']
        if 'status' in data:
            member.status = data['status']
        if 'workload' in data:
            member.workload = data['workload']
        if 'skills' in data:
            member.skills = data['skills']
        if 'activeProjects' in data:
            member.active_projects = data['activeProjects']
        
        member.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(member.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update team member', 'message': str(e)}), 500


@teams_bp.route('/<int:member_id>', methods=['DELETE'])
@token_required
def delete_team_member(member_id):
    """Delete team member"""
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({'message': 'Team member deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete team member', 'message': str(e)}), 500

