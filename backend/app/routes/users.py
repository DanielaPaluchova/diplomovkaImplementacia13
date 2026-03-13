"""
User API endpoints
"""
from flask import Blueprint, jsonify
from app.models.user import User
from app.models.team_member import TeamMember
from app.utils.auth import token_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """Get all users (for owner/assignee selection)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'message': str(e)}), 500


@users_bp.route('/team-members', methods=['GET'])
@token_required
def get_team_members():
    """Get all team members (for epic owner/task assignee selection)"""
    try:
        members = TeamMember.query.all()
        return jsonify([member.to_dict() for member in members]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get team members', 'message': str(e)}), 500


@users_bp.route('/projects/<int:project_id>/team-members', methods=['GET'])
@token_required
def get_project_team_members(project_id):
    """Get team members assigned to a specific project"""
    try:
        from app.models.project_role import ProjectRole
        
        # Get all member IDs for this project
        project_roles = ProjectRole.query.filter_by(project_id=project_id).all()
        member_ids = [role.member_id for role in project_roles]
        
        # Get team members with those IDs
        members = TeamMember.query.filter(TeamMember.id.in_(member_ids)).all()
        return jsonify([member.to_dict() for member in members]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get project team members', 'message': str(e)}), 500
