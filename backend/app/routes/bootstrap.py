"""
Bootstrap seed cez HTTP (BOOTSTRAP_SECRET).

- GET  /api/bootstrap/seed/status  — prehľad krokov 1–9 (čo už je v DB)
- POST /api/bootstrap/seed/step/<1-9> — spustí jednu fázu (veľká DB rozdelená na viac requestov)
"""
import os
import secrets as stdlib_secrets

from flask import Blueprint, jsonify, request

from app import db
from seed_phases import build_status_payload, run_seed_step

bootstrap_bp = Blueprint('bootstrap', __name__)


def _bootstrap_secret_ok() -> bool:
    configured = os.getenv('BOOTSTRAP_SECRET', '').strip()
    if not configured:
        return False
    provided = (request.headers.get('X-Bootstrap-Secret') or '').strip()
    if not provided or len(provided) != len(configured):
        return False
    return stdlib_secrets.compare_digest(provided, configured)


def _require_secret():
    if not os.getenv('BOOTSTRAP_SECRET', '').strip():
        return jsonify({'error': 'Bootstrap is not configured'}), 404
    if not _bootstrap_secret_ok():
        return jsonify({'error': 'Invalid or missing secret'}), 401
    return None


@bootstrap_bp.route('/seed', methods=['POST'])
def bootstrap_seed_legacy():
    err = _require_secret()
    if err:
        return err
    return jsonify(
        {
            'message': 'Starý jednorazový POST /seed je nahradený viacerými krokmi.',
            'get_status': 'GET /api/bootstrap/seed/status',
            'run_steps': 'POST /api/bootstrap/seed/step/1 … /step/9 (1 = users+team, 2–9 = 8 projektov)',
        }
    )


@bootstrap_bp.route('/seed/status', methods=['GET'])
def bootstrap_seed_status():
    err = _require_secret()
    if err:
        return err
    return jsonify(build_status_payload())


@bootstrap_bp.route('/seed/step/<int:step>', methods=['POST'])
def bootstrap_seed_step(step: int):
    err = _require_secret()
    if err:
        return err
    try:
        result = run_seed_step(step)
        if result.get('ok') is False:
            return jsonify(result), 400
        return jsonify(result)
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500
