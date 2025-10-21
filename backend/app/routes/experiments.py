"""
Experiments API endpoints for research data
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.experiment import Experiment
from app.utils.auth import token_required, manager_required
from datetime import datetime

experiments_bp = Blueprint('experiments', __name__)


@experiments_bp.route('/', methods=['GET'])
@token_required
def get_experiments():
    """Get all experiments"""
    try:
        status = request.args.get('status')
        
        if status:
            experiments = Experiment.query.filter_by(status=status).all()
        else:
            experiments = Experiment.query.all()
        
        return jsonify([exp.to_dict() for exp in experiments]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get experiments', 'message': str(e)}), 500


@experiments_bp.route('/<int:experiment_id>', methods=['GET'])
@token_required
def get_experiment(experiment_id):
    """Get single experiment"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        return jsonify(experiment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get experiment', 'message': str(e)}), 500


@experiments_bp.route('/', methods=['POST'])
@manager_required
def create_experiment():
    """Create new experiment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Experiment name is required'}), 400
        
        experiment = Experiment(
            name=data['name'],
            description=data.get('description', ''),
            hypothesis=data.get('hypothesis', ''),
            status=data.get('status', 'planning'),
            methodology=data.get('methodology', ''),
            start_date=datetime.fromisoformat(data['startDate']) if data.get('startDate') else None,
            end_date=datetime.fromisoformat(data['endDate']) if data.get('endDate') else None,
            participants=data.get('participants', 0),
            results=data.get('results')
        )
        
        db.session.add(experiment)
        db.session.commit()
        
        return jsonify(experiment.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create experiment', 'message': str(e)}), 500


@experiments_bp.route('/<int:experiment_id>', methods=['PUT'])
@manager_required
def update_experiment(experiment_id):
    """Update experiment"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            experiment.name = data['name']
        if 'description' in data:
            experiment.description = data['description']
        if 'hypothesis' in data:
            experiment.hypothesis = data['hypothesis']
        if 'status' in data:
            experiment.status = data['status']
        if 'methodology' in data:
            experiment.methodology = data['methodology']
        if 'startDate' in data:
            experiment.start_date = datetime.fromisoformat(data['startDate']) if data['startDate'] else None
        if 'endDate' in data:
            experiment.end_date = datetime.fromisoformat(data['endDate']) if data['endDate'] else None
        if 'participants' in data:
            experiment.participants = data['participants']
        if 'results' in data:
            experiment.results = data['results']
        
        experiment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(experiment.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update experiment', 'message': str(e)}), 500


@experiments_bp.route('/<int:experiment_id>', methods=['DELETE'])
@manager_required
def delete_experiment(experiment_id):
    """Delete experiment"""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        db.session.delete(experiment)
        db.session.commit()
        
        return jsonify({'message': 'Experiment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete experiment', 'message': str(e)}), 500


@experiments_bp.route('/stats', methods=['GET'])
@token_required
def get_experiment_stats():
    """Get experiment statistics"""
    try:
        total = Experiment.query.count()
        completed = Experiment.query.filter_by(status='completed').count()
        running = Experiment.query.filter_by(status='running').count()
        planning = Experiment.query.filter_by(status='planning').count()
        
        # Calculate average improvement from completed experiments
        completed_experiments = Experiment.query.filter_by(status='completed').all()
        improvements = [exp.results.get('improvement', 0) for exp in completed_experiments if exp.results]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Calculate average confidence
        confidences = [exp.results.get('confidence', 0) for exp in completed_experiments if exp.results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return jsonify({
            'total': total,
            'completed': completed,
            'running': running,
            'planning': planning,
            'avgImprovement': round(avg_improvement, 1),
            'avgConfidence': round(avg_confidence, 1)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get experiment stats', 'message': str(e)}), 500

