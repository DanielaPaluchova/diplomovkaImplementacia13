"""
Fázovaný seed veľkej DB — každá fáza sa volá samostatným HTTP requestom (Render timeout).
Kroky 1 = foundation, 2–9 = projekty z seed_projects.py v tom istom poradí ako seed_all_projects().
"""
from __future__ import annotations

from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.user import User
from seed_database import get_member_ids, seed_team_members, seed_users

# Musí sedieť s názvami projektov v seed_projects.py
STEP_SPECS: list[dict] = [
    {
        'step': 1,
        'key': 'foundation',
        'label': 'Používatelia (demo) + 12 team members',
        'project_name': None,
    },
    {
        'step': 2,
        'key': 'ecommerce',
        'label': 'E-commerce Platform Redesign',
        'project_name': 'E-commerce Platform Redesign',
    },
    {
        'step': 3,
        'key': 'banking',
        'label': 'Mobile Banking App',
        'project_name': 'Mobile Banking App',
    },
    {
        'step': 4,
        'key': 'healthcare',
        'label': 'Healthcare Patient Portal',
        'project_name': 'Healthcare Patient Portal',
    },
    {
        'step': 5,
        'key': 'logistics',
        'label': 'Logistics Tracking Dashboard',
        'project_name': 'Logistics Tracking Dashboard',
    },
    {
        'step': 6,
        'key': 'social',
        'label': 'Social Media Platform',
        'project_name': 'Social Media Platform',
    },
    {
        'step': 7,
        'key': 'ai',
        'label': 'AI Content Generator',
        'project_name': 'AI Content Generator',
    },
    {
        'step': 8,
        'key': 'iot',
        'label': 'IoT Device Manager',
        'project_name': 'IoT Device Manager',
    },
    {
        'step': 9,
        'key': 'education',
        'label': 'Education Learning Management System',
        'project_name': 'Education Learning Management System',
    },
]


def _spec_for_step(step: int) -> dict:
    for s in STEP_SPECS:
        if s['step'] == step:
            return s
    raise ValueError(f'Neplatný krok {step}; použite 1–9.')


def foundation_ready() -> bool:
    """Pre kroky 2–9 musia existovať seednutí členovia tímu."""
    return TeamMember.query.count() >= 12


def step_done(step: int) -> bool:
    spec = _spec_for_step(step)
    if step == 1:
        return User.query.filter_by(email='admin@example.com').first() is not None and foundation_ready()
    return Project.query.filter_by(name=spec['project_name']).first() is not None


def build_status_payload() -> dict:
    phases = []
    for s in STEP_SPECS:
        phases.append(
            {
                'step': s['step'],
                'key': s['key'],
                'label': s['label'],
                'done': step_done(s['step']),
            }
        )
    return {'steps': phases, 'foundation_ready': foundation_ready()}


def run_seed_step(step: int) -> dict:
    spec = _spec_for_step(step)

    if step == 1:
        if step_done(1):
            return {
                'ok': True,
                'skipped': True,
                'step': 1,
                'message': 'Foundation už je (admin + team). Pokračuj krokom 2.',
            }
        seed_users()
        seed_team_members()
        return {
            'ok': True,
            'skipped': False,
            'step': 1,
            'message': 'Hotovo: demo users + team. Ďalej POST .../seed/step/2 až 9.',
        }

    if not foundation_ready():
        return {
            'ok': False,
            'error': 'Najprv dokonči krok 1 (foundation — chýba 12 team members).',
            'step_required': 1,
        }

    pname = spec['project_name']
    if Project.query.filter_by(name=pname).first():
        return {
            'ok': True,
            'skipped': True,
            'step': step,
            'message': f'Projekt „{pname}“ už v DB je.',
        }

    m = get_member_ids()

    from seed_projects import (
        seed_ai_generator,
        seed_banking,
        seed_ecommerce,
        seed_education,
        seed_healthcare,
        seed_iot,
        seed_logistics,
        seed_social_media,
    )

    runners = {
        2: seed_ecommerce,
        3: seed_banking,
        4: seed_healthcare,
        5: seed_logistics,
        6: seed_social_media,
        7: seed_ai_generator,
        8: seed_iot,
        9: seed_education,
    }

    fn = runners[step]
    fn(m)

    return {
        'ok': True,
        'skipped': False,
        'step': step,
        'message': f'Nasadený projekt: {pname}. Ďalší krok: {step + 1}' if step < 9 else f'Nasadený posledný projekt: {pname}.',
    }
