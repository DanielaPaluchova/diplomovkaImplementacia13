"""
Smart Sprint Planning API endpoints
Intelligent sprint planning with multiple strategies
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.project import Project
from app.models.task import Task
from app.models.team_member import TeamMember
from app.models.sprint import Sprint
from app.models.optimization_log import OptimizationLog
from app.services.smart_sprint_planner import SmartSprintPlannerService
from app.utils.auth import token_required
from datetime import datetime
import uuid

smart_sprint_bp = Blueprint('smart_sprint', __name__)

# Initialize service
sprint_planner = SmartSprintPlannerService()


@smart_sprint_bp.route('/<int:project_id>/smart-sprint-planning', methods=['POST'])
@token_required
def generate_smart_sprint_plan(project_id):
    """
    Generate a smart sprint plan using the specified strategy
    
    Request body:
    {
        "strategy": "priority|workload-balanced|skill-match|dependency-aware|velocity-based|risk-optimized|value-driven|hybrid",
        "sprintName": "Sprint 1",
        "sprintGoal": "Complete user authentication",
        "startDate": "2024-01-01",
        "endDate": "2024-01-14",
        "sprintDuration": 14,
        "targetUtilization": 85,  // Optional, percentage of capacity to target
        "closeActiveSprint": false,  // Optional, whether to close active sprint first
        "parameters": {  // Optional, strategy-specific parameters
            "weights": {  // For hybrid strategy
                "priority": 0.25,
                "workload": 0.20,
                "skills": 0.25,
                "dependency": 0.15,
                "velocity": 0.15
            }
        }
    }
    
    Response:
    {
        "suggestedTasks": [...],
        "assignments": {...},
        "metrics": {...},
        "reasoning": {...},
        "sprintSummary": {...},
        "strategy": "...",
        "projectId": 123
    }
    """
    try:
        data = request.get_json() or {}
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Extract parameters
        strategy = data.get('strategy', 'priority')
        sprint_name = data.get('sprintName')
        sprint_goal = data.get('sprintGoal', '')
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate')
        target_utilization = data.get('targetUtilization', 85) / 100.0  # Convert to decimal
        close_active_sprint = data.get('closeActiveSprint', False)
        consider_cross_project = data.get('considerCrossProjectWorkload', True)
        parameters = data.get('parameters', {})
        
        # Validate required fields
        if not sprint_name:
            return jsonify({'error': 'Sprint name is required'}), 400
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        # Get team members
        team_members = TeamMember.query.filter(
            TeamMember.id.in_(project.team_member_ids or [])
        ).all()
        
        if not team_members:
            return jsonify({'error': 'No team members assigned to project'}), 400
        
        # Get active sprint if exists
        active_sprint = Sprint.query.filter_by(
            project_id=project_id,
            status='active'
        ).first()
        
        # Get all tasks for this project
        all_tasks = Task.query.filter_by(project_id=project_id).all()
        
        # Filter eligible tasks (not done, not in active sprint unless closing it)
        if active_sprint and not close_active_sprint:
            # Exclude tasks from active sprint
            eligible_tasks = [
                task for task in all_tasks
                if task.status != 'Done' and task.sprint_id != active_sprint.id
            ]
            active_sprint_id = active_sprint.id
        else:
            # Include all non-done tasks
            eligible_tasks = [
                task for task in all_tasks
                if task.status != 'Done'
            ]
            active_sprint_id = None
        
        # Calculate team capacity
        team_capacity = sum(member.max_story_points for member in team_members)
        target_capacity = team_capacity * target_utilization
        
        # Calculate cross-project workload if requested
        cross_project_workload = {}
        cross_project_priorities = {}
        
        if consider_cross_project:
            for member in team_members:
                # Get all projects where member is assigned
                # Use Python filtering instead of SQL to avoid JSON operator issues
                all_projects = [
                    proj for proj in Project.query.all()
                    if proj.team_member_ids and member.id in proj.team_member_ids
                ]
                
                total_sp = 0
                high_priority_count = 0
                
                for proj in all_projects:
                    if proj.id == project_id:
                        continue  # Skip current project
                    
                    # Get active sprints in other projects
                    other_active_sprints = Sprint.query.filter_by(
                        project_id=proj.id,
                        status='active'
                    ).all()
                    
                    for sprint in other_active_sprints:
                        # Get incomplete tasks assigned to this member
                        sprint_tasks = Task.query.filter_by(
                            sprint_id=sprint.id
                        ).filter(
                            Task.status != 'Done'
                        ).all()
                        
                        for task in sprint_tasks:
                            # Check if member is responsible
                            is_assigned = (
                                task.raci_responsible and member.id in task.raci_responsible
                            )
                            
                            if is_assigned:
                                total_sp += task.story_points or 0
                                if task.priority and task.priority.lower() == 'high':
                                    high_priority_count += 1
                
                cross_project_workload[member.id] = total_sp
                cross_project_priorities[member.id] = high_priority_count
        
        # Prepare sprint configuration
        sprint_config = {
            'name': sprint_name,
            'goal': sprint_goal,
            'startDate': start_date_str,
            'endDate': end_date_str,
            'targetCapacity': target_capacity,
            'activeSprintId': active_sprint_id,
            'closeActiveSprint': close_active_sprint,
            'considerCrossProject': consider_cross_project,
            'crossProjectWorkload': cross_project_workload,
            'crossProjectPriorities': cross_project_priorities
        }
        
        # Generate sprint plan
        result = sprint_planner.plan_sprint(
            strategy=strategy,
            project_id=project_id,
            tasks=eligible_tasks,
            team_members=team_members,
            sprint_config=sprint_config,
            parameters=parameters
        )
        
        # Add additional context
        result['sprintConfig'] = {
            'name': sprint_name,
            'goal': sprint_goal,
            'startDate': start_date_str,
            'endDate': end_date_str,
            'targetCapacity': target_capacity,
            'teamCapacity': team_capacity
        }
        
        if active_sprint:
            result['activeSprint'] = {
                'id': active_sprint.id,
                'name': active_sprint.name,
                'status': active_sprint.status,
                'willBeClosed': close_active_sprint
            }
        
        result['eligibleTasksCount'] = len(eligible_tasks)
        
        return jsonify(result), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate sprint plan',
            'message': str(e)
        }), 500


@smart_sprint_bp.route('/<int:project_id>/apply-sprint-plan', methods=['POST'])
@token_required
def apply_smart_sprint_plan(project_id):
    """
    Apply a smart sprint plan by creating a new sprint and assigning tasks
    
    Request body:
    {
        "sprintName": "Sprint 1",
        "sprintGoal": "Complete user authentication",
        "startDate": "2024-01-01",
        "endDate": "2024-01-14",
        "closeActiveSprint": false,
        "tasks": [task_id1, task_id2, ...],
        "assignments": {
            "task_id": {
                "memberId": 123,
                "role": "responsible"
            }
        }
    }
    
    Response:
    {
        "success": true,
        "sprint": {...},
        "tasksUpdated": 5,
        "assignmentsApplied": 5,
        "closedSprint": {...}  // Optional, if active sprint was closed
    }
    """
    try:
        data = request.get_json() or {}
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Extract parameters
        sprint_name = data.get('sprintName')
        sprint_goal = data.get('sprintGoal', '')
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate')
        close_active_sprint = data.get('closeActiveSprint', False)
        task_ids = data.get('tasks', [])
        assignments = data.get('assignments', {})
        
        # Validate required fields
        if not sprint_name or not start_date_str or not end_date_str:
            return jsonify({'error': 'Sprint name, start date, and end date are required'}), 400
        
        if not task_ids:
            return jsonify({'error': 'No tasks selected for the sprint'}), 400
        
        # Parse dates
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Check for existing active sprint and handle it
        closed_sprint = None
        active_sprint = Sprint.query.filter_by(
            project_id=project_id,
            status='active'
        ).first()
        
        # If active sprint exists and closeActiveSprint is false, return error
        if active_sprint and not close_active_sprint:
            return jsonify({
                'error': 'Cannot create new active sprint while another sprint is active',
                'message': f'Sprint "{active_sprint.name}" is currently active. Please close it first or enable "Close Active Sprint" option.',
                'activeSprint': active_sprint.to_dict()
            }), 400
        
        # Close active sprint if requested
        if close_active_sprint and active_sprint:
            active_sprint.status = 'completed'
            closed_sprint = active_sprint.to_dict()
        
        # Create new sprint
        new_sprint = Sprint(
            project_id=project_id,
            name=sprint_name,
            goal=sprint_goal,
            start_date=start_date,
            end_date=end_date,
            status='active',
            capacity=sum(
                TeamMember.query.get(member_id).max_story_points
                for member_id in (project.team_member_ids or [])
                if TeamMember.query.get(member_id)
            )
        )
        
        db.session.add(new_sprint)
        db.session.flush()  # Get the sprint ID
        
        # Update tasks
        tasks_updated = 0
        assignments_applied = 0
        
        for task_id in task_ids:
            # Convert task_id to int if it's a string
            try:
                task_id = int(task_id)
            except (ValueError, TypeError):
                continue
            
            task = Task.query.get(task_id)
            if not task or task.project_id != project_id:
                continue
            
            # Skip blocked tasks - they cannot be assigned to a sprint
            if task.status == 'Blocked':
                continue
            
            # Assign task to sprint
            task.sprint_id = new_sprint.id
            tasks_updated += 1
            
            # Apply assignment if provided
            assignment = assignments.get(str(task_id))
            if assignment:
                member_id = assignment.get('memberId')
                role = assignment.get('role', 'responsible')
                
                if member_id:
                    # Update RACI assignments
                    if role == 'responsible':
                        # Add to responsible list
                        responsible = task.raci_responsible or []
                        if member_id not in responsible:
                            responsible.append(member_id)
                        task.raci_responsible = responsible
                    elif role == 'accountable':
                        task.raci_accountable = member_id
                    
                    assignments_applied += 1
        
        # Calculate sprint story points
        sprint_tasks = Task.query.filter_by(
            project_id=project_id,
            sprint_id=new_sprint.id
        ).all()
        
        new_sprint.planned_story_points = sum(
            task.story_points or 0 for task in sprint_tasks
        )
        
        # Create OptimizationLog entry
        optimization_log = OptimizationLog(
            project_id=project_id,
            optimization_type='smart_sprint',
            proposals_count=len(task_ids),
            applied_count=tasks_updated,
            scope='sprint_planning',
            results={
                'sprintId': new_sprint.id,
                'sprintName': sprint_name,
                'tasksUpdated': tasks_updated,
                'assignmentsApplied': assignments_applied,
                'plannedStoryPoints': new_sprint.planned_story_points,
                'closedSprint': closed_sprint is not None
            }
        )
        db.session.add(optimization_log)
        
        # Commit all changes
        db.session.commit()
        
        response = {
            'success': True,
            'sprint': new_sprint.to_dict(),
            'tasksUpdated': tasks_updated,
            'assignmentsApplied': assignments_applied
        }
        
        if closed_sprint:
            response['closedSprint'] = closed_sprint
        
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to apply sprint plan',
            'message': str(e)
        }), 500


@smart_sprint_bp.route('/<int:project_id>/sprint-strategies', methods=['GET'])
@token_required
def get_sprint_strategies(project_id):
    """
    Get available sprint planning strategies with descriptions
    
    Response:
    {
        "strategies": [
            {
                "id": "priority",
                "name": "Priority-Based",
                "description": "Select highest priority tasks first",
                "parameters": []
            },
            ...
        ]
    }
    """
    strategies = [
        {
            'id': 'priority',
            'name': 'Priority-Based',
            'description': 'Select highest priority tasks first, ensuring critical work is completed',
            'parameters': [],
            'icon': 'priority_high',
            'recommended': 'When you need to focus on urgent and important tasks'
        },
        {
            'id': 'workload-balanced',
            'name': 'Workload-Balanced',
            'description': 'Distribute story points evenly across team members',
            'parameters': [],
            'icon': 'balance',
            'recommended': 'When you want to ensure fair distribution of work'
        },
        {
            'id': 'skill-match',
            'name': 'Skill-Match',
            'description': 'Assign tasks based on team member skills and expertise',
            'parameters': [],
            'icon': 'psychology',
            'recommended': 'When you have specialized tasks requiring specific skills'
        },
        {
            'id': 'velocity-based',
            'name': 'Velocity-Based',
            'description': 'Use historical velocity for realistic capacity planning',
            'parameters': [],
            'icon': 'speed',
            'recommended': 'When you want to plan based on actual team performance'
        },
        {
            'id': 'risk-optimized',
            'name': 'Risk-Optimized',
            'description': 'Minimize risk by prioritizing low-risk tasks',
            'parameters': [],
            'icon': 'security',
            'recommended': 'When you want to ensure sprint success with lower risk'
        },
        {
            'id': 'value-driven',
            'name': 'Value-Driven',
            'description': 'Maximize business value (story points × priority)',
            'parameters': [],
            'icon': 'trending_up',
            'recommended': 'When you want to maximize delivered business value'
        },
        {
            'id': 'balanced-priority',
            'name': 'Balanced Priority',
            'description': 'Balance high-priority tasks with fair workload distribution',
            'parameters': [
                {
                    'name': 'priority',
                    'label': 'Priority Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.6
                },
                {
                    'name': 'workload',
                    'label': 'Workload Balance Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.4
                }
            ],
            'icon': 'filter_list',
            'recommended': 'When you need to address important work while maintaining fair distribution'
        },
        {
            'id': 'safe-value',
            'name': 'Safe Value',
            'description': 'Maximize business value while minimizing risk for predictable delivery',
            'parameters': [
                {
                    'name': 'value',
                    'label': 'Value Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.5
                },
                {
                    'name': 'risk',
                    'label': 'Risk Mitigation Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.5
                }
            ],
            'icon': 'verified',
            'recommended': 'When you want high value delivery with controlled risk'
        },
        {
            'id': 'hybrid',
            'name': 'Hybrid (Recommended)',
            'description': 'Combine all factors with configurable weights for optimal results',
            'parameters': [
                {
                    'name': 'priority',
                    'label': 'Priority Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.25
                },
                {
                    'name': 'workload',
                    'label': 'Workload Balance Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.20
                },
                {
                    'name': 'skills',
                    'label': 'Skills Match Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.25
                },
                {
                    'name': 'dependency',
                    'label': 'Dependency Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.15
                },
                {
                    'name': 'velocity',
                    'label': 'Velocity Weight',
                    'type': 'slider',
                    'min': 0,
                    'max': 1,
                    'step': 0.05,
                    'default': 0.15
                }
            ],
            'icon': 'auto_awesome',
            'recommended': 'Best overall strategy that considers all factors'
        }
    ]
    
    return jsonify({
        'strategies': strategies,
        'defaultStrategy': 'hybrid'
    }), 200

