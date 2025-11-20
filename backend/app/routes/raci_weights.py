"""
RACI Weights Configuration Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.raci_weights_config import RaciWeightsConfig

raci_weights_bp = Blueprint('raci_weights', __name__)


@raci_weights_bp.route('', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_raci_weights():
    """
    Get RACI weights configuration
    """
    try:
        config = RaciWeightsConfig.get_or_create()
        return jsonify(config.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@raci_weights_bp.route('', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_raci_weights():
    """
    Update RACI weights configuration
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate data structure
        if 'workload' in data:
            workload = data['workload']
            required_keys = ['responsible', 'accountable', 'consulted', 'informed']
            if not all(key in workload for key in required_keys):
                return jsonify({'error': 'Missing required workload weights'}), 400
            
            # Validate that all values are numbers
            for key in required_keys:
                if not isinstance(workload[key], (int, float)):
                    return jsonify({'error': f'Invalid value for workload.{key}'}), 400
        
        if 'duration' in data:
            duration = data['duration']
            required_keys = ['responsible', 'accountable', 'consulted', 'informed']
            if not all(key in duration for key in required_keys):
                return jsonify({'error': 'Missing required duration weights'}), 400
            
            # Validate that all values are numbers
            for key in required_keys:
                if not isinstance(duration[key], (int, float)):
                    return jsonify({'error': f'Invalid value for duration.{key}'}), 400
        
        # Get or create configuration
        config = RaciWeightsConfig.get_or_create()
        
        # Update configuration
        config.update_from_dict(data)
        
        # Save to database
        db.session.commit()
        
        return jsonify(config.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


