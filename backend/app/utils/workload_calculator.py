"""
Workload Calculator Utility
Calculate cross-project workload for team members
"""
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.task import Task
from typing import Dict, List, Optional


def calculate_cross_project_workload(
    team_members: List[TeamMember],
    exclude_project_id: Optional[int] = None
) -> Dict[int, Dict[str, float]]:
    """
    Calculate workload for team members across all projects (from active sprints only).
    
    By default, includes all projects. Use exclude_project_id when planning future sprints
    to see available capacity without the current project's load.
    
    Args:
        team_members: List of team members to calculate workload for
        exclude_project_id: Optional project ID to exclude from calculation (default: None = include all)
        
    Returns:
        Dict mapping member_id to {'sp': total_sp, 'pct': workload_percentage}
    """
    cross_project_workload = {}
    
    for member in team_members:
        # Get all projects where member is assigned
        all_projects = [
            proj for proj in Project.query.all()
            if proj.team_member_ids and member.id in proj.team_member_ids
        ]
        
        total_sp = 0
        
        for proj in all_projects:
            # Skip excluded project if specified
            if exclude_project_id and proj.id == exclude_project_id:
                continue
            
            # Get active sprints in this project
            active_sprints = Sprint.query.filter_by(
                project_id=proj.id,
                status='active'
            ).all()
            
            for sprint in active_sprints:
                # Get all tasks assigned to this member in this sprint (Sprint Commitment)
                sprint_tasks = Task.query.filter_by(
                    sprint_id=sprint.id
                ).all()
                
                for task in sprint_tasks:
                    # Check if member is responsible
                    is_assigned = (
                        task.raci_responsible and member.id in task.raci_responsible
                    )
                    
                    if is_assigned:
                        total_sp += task.story_points or 0
        
        # Calculate workload percentage
        workload_pct = (total_sp / member.max_story_points) * 100 if member.max_story_points > 0 else 0
        
        cross_project_workload[member.id] = {
            'sp': total_sp,
            'pct': workload_pct
        }
    
    return cross_project_workload


def calculate_cross_project_raci_workload(
    team_members: List[TeamMember],
    sprint_id: Optional[int] = None,
    exclude_project_id: Optional[int] = None
) -> Dict[int, Dict[str, float]]:
    """
    Calculate RACI-weighted workload for team members across ALL projects.
    Matches the frontend calculation in PertRaciOptimizationPage.vue
    
    RACI Weights (same as frontend):
    - Responsible: 1.0
    - Accountable: 0.1
    - Consulted: 0.05
    - Informed: 0.01
    
    Args:
        team_members: List of team members
        sprint_id: Optional sprint ID to filter by (usually active sprint)
        exclude_project_id: Optional project ID to exclude
        
    Returns:
        Dict mapping member_id to {'weighted_sp': float, 'pct': float}
    """
    RACI_WEIGHTS = {
        'responsible': 1.0,
        'accountable': 0.1,
        'consulted': 0.05,
        'informed': 0.01
    }
    
    raci_workload = {}
    
    # Initialize for all members
    for member in team_members:
        raci_workload[member.id] = {
            'weighted_sp': 0.0,
            'pct': 0.0
        }
    
    # Get all projects where team members work
    all_projects = Project.query.all()
    
    for proj in all_projects:
        # Skip excluded project if specified
        if exclude_project_id and proj.id == exclude_project_id:
            continue
        
        # Get tasks from project
        if sprint_id:
            # Filter by specific sprint across all projects
            tasks = Task.query.filter_by(
                project_id=proj.id,
                sprint_id=sprint_id
            ).all()
        else:
            # Get tasks from active sprints in this project
            active_sprints = Sprint.query.filter_by(
                project_id=proj.id,
                status='active'
            ).all()
            
            tasks = []
            for sprint in active_sprints:
                sprint_tasks = Task.query.filter_by(sprint_id=sprint.id).all()
                tasks.extend(sprint_tasks)
        
        # Calculate RACI weighted workload
        for task in tasks:
            task_sp = task.story_points or 0
            if task_sp == 0:
                continue
            
            # Responsible
            if task.raci_responsible:
                for member_id in task.raci_responsible:
                    if member_id in raci_workload:
                        raci_workload[member_id]['weighted_sp'] += task_sp * RACI_WEIGHTS['responsible']
            
            # Accountable
            if task.raci_accountable:
                member_id = task.raci_accountable
                if member_id in raci_workload:
                    raci_workload[member_id]['weighted_sp'] += task_sp * RACI_WEIGHTS['accountable']
            
            # Consulted
            if task.raci_consulted:
                for member_id in task.raci_consulted:
                    if member_id in raci_workload:
                        raci_workload[member_id]['weighted_sp'] += task_sp * RACI_WEIGHTS['consulted']
            
            # Informed
            if task.raci_informed:
                for member_id in task.raci_informed:
                    if member_id in raci_workload:
                        raci_workload[member_id]['weighted_sp'] += task_sp * RACI_WEIGHTS['informed']
    
    # Calculate percentages
    for member in team_members:
        if member.id in raci_workload:
            weighted_sp = raci_workload[member.id]['weighted_sp']
            max_sp = member.max_story_points or 20
            raci_workload[member.id]['pct'] = (weighted_sp / max_sp) * 100 if max_sp > 0 else 0
    
    return raci_workload

