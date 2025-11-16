"""
Requirement Changes API endpoints
Analyzes requirement changes and suggests adaptations
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.project import Project
from app.models.task import Task
from app.models.team_member import TeamMember
from app.models.sprint import Sprint
from app.models.optimization_log import OptimizationLog
from app.services.team_scoring import TeamScoringService
from app.services.task_splitter import TaskSplitterService
from app.services.sprint_analyzer import SprintAnalyzerService
from app.services.task_merger import TaskMergerService
from app.services.bottleneck_analyzer import BottleneckAnalyzerService
from app.services.dependency_optimizer import DependencyOptimizerService
from app.services.risk_analyzer import RiskAnalyzerService
from app.services.pert_raci_analyzer import PertRaciAnalyzerService
from app.utils.auth import token_required
from app.utils.workload_calculator import calculate_cross_project_workload
from datetime import datetime
import uuid

requirement_changes_bp = Blueprint('requirement_changes', __name__)

# Initialize services
team_scoring = TeamScoringService()
task_splitter = TaskSplitterService()
sprint_analyzer = SprintAnalyzerService()
task_merger = TaskMergerService()
bottleneck_analyzer = BottleneckAnalyzerService()
dependency_optimizer = DependencyOptimizerService()
risk_analyzer = RiskAnalyzerService()
pert_raci_analyzer = PertRaciAnalyzerService()


@requirement_changes_bp.route('/<int:project_id>/auto-optimize', methods=['POST'])
@token_required
def auto_optimize_project(project_id):
    """
    Automatically analyze entire project and suggest all possible improvements
    Supports scope: current_sprint, backlog, or all_sprints
    """
    try:
        data = request.get_json() or {}
        scope = data.get('scope', 'backlog')  # 'current_sprint', 'backlog', or 'all_sprints'
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get project data
        all_tasks = Task.query.filter_by(project_id=project_id).all()
        team_members = TeamMember.query.filter(
            TeamMember.id.in_(project.team_member_ids or [])
        ).all()
        sprints = Sprint.query.filter_by(project_id=project_id).all()
        
        # Filter out Split tasks (already processed, should not be analyzed again)
        active_tasks = [t for t in all_tasks if t.status != 'Split']
        
        # Filter tasks by scope
        if scope == 'current_sprint':
            # Get active sprint
            active_sprint = next((s for s in sprints if s.status == 'active'), None)
            if active_sprint:
                tasks = [t for t in active_tasks if t.sprint_id == active_sprint.id]
            else:
                tasks = []
        elif scope == 'backlog':
            # Get only tasks not assigned to any sprint
            tasks = [t for t in active_tasks if t.sprint_id is None]
        else:  # all_sprints
            tasks = active_tasks
        
        # Calculate current state
        current_state = _calculate_current_state(project, tasks, team_members, sprints)
        
        # Calculate cross-project workload for more accurate recommendations (include current project)
        cross_project_workload = calculate_cross_project_workload(team_members, exclude_project_id=None)
        
        # Generate all possible optimization proposals
        proposals = []
        
        # Workload-based optimizations only make sense for current_sprint scope
        # Backlog tasks are not in a sprint yet, so workload analysis is not applicable
        is_sprint_scope = (scope == 'current_sprint')
        
        # 1. CRITICAL: Deadline risks
        deadline_proposals = risk_analyzer.find_deadline_risks(tasks)
        proposals.extend(deadline_proposals)
        
        # 2. CRITICAL: Priority conflicts (only for sprint scope - backlog priority doesn't affect current workload)
        if is_sprint_scope:
            priority_proposals = risk_analyzer.find_priority_conflicts(team_members, tasks, cross_project_workload)
            proposals.extend(priority_proposals)
        
        # 3. CRITICAL: Resource bottlenecks (only for sprint scope - backlog doesn't contribute to current workload)
        if is_sprint_scope:
            bottleneck_proposals = bottleneck_analyzer.find_resource_bottlenecks(team_members, tasks, cross_project_workload)
            proposals.extend(bottleneck_proposals)
        
        # 4. IMPORTANT: Task splits (21+ SP) - applies to both backlog and sprint
        split_proposals = task_splitter.create_split_proposals(tasks)
        proposals.extend(split_proposals)
        
        # 6. IMPORTANT: Sprint overflow (only for sprint scope)
        if is_sprint_scope:
            sprint_proposals = sprint_analyzer.suggest_sprint_reallocation(sprints, all_tasks, team_members)
            proposals.extend(sprint_proposals)
        
        # 7. IMPORTANT: Skill mismatches - applies to both backlog and sprint
        # Better to detect skill mismatches BEFORE task goes into sprint
        # Even though backlog assignments can be changed easily, it's preventive to flag them early
        skill_proposals = risk_analyzer.find_skill_mismatches(team_members, tasks, cross_project_workload)
        proposals.extend(skill_proposals)
        
        # 8. RECOMMENDED: Workload rebalancing (only for sprint scope - backlog doesn't affect current workload)
        if is_sprint_scope:
            rebalance_proposals = _generate_workload_rebalancing_proposals(team_members, tasks, sprints, cross_project_workload)
            proposals.extend(rebalance_proposals)
        
        # 9. RECOMMENDED: Task merges - applies to both backlog and sprint
        merge_proposals = task_merger.create_merge_proposals(tasks)
        proposals.extend(merge_proposals)
        
        # 10. RECOMMENDED: Idle resources (only for sprint scope - backlog doesn't show who is idle)
        if is_sprint_scope:
            idle_proposals = risk_analyzer.find_idle_resources(team_members, tasks, cross_project_workload)
            proposals.extend(idle_proposals)
        
        # Categorize by severity
        categorized = {
            'critical': [p for p in proposals if p.get('severity') == 'critical'],
            'important': [p for p in proposals if p.get('severity') == 'important'],
            'recommended': [p for p in proposals if p.get('severity') == 'recommended']
        }
        
        # Calculate projected state
        projected_state = _calculate_projected_state_from_proposals(current_state, proposals)
        
        return jsonify({
            'currentState': current_state,
            'proposals': proposals,
            'categorized': categorized,
            'projectedState': projected_state,
            'totalProposals': len(proposals),
            'scope': scope,
            'message': f'Found {len(proposals)} optimization opportunities ({len(categorized["critical"])} critical, {len(categorized["important"])} important, {len(categorized["recommended"])} recommended)'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to auto-optimize project', 'message': str(e)}), 500


def _generate_workload_rebalancing_proposals(team_members, tasks, sprints, cross_project_workload=None):
    """Generate proposals to rebalance workload across team members"""
    proposals = []
    
    if not team_members or len(team_members) < 2:
        return proposals
    
    # Get active sprint
    active_sprint = next((s for s in sprints if s.status == 'active'), None)
    
    # Calculate current workload for each member (use cross-project if available)
    member_workloads = {}
    member_tasks = {}
    
    for member in team_members:
        # Only count tasks in active sprint (Sprint Commitment)
        member_tasks[member.id] = [
            t for t in tasks 
            if (active_sprint and t.sprint_id == active_sprint.id) and (
                (t.raci_responsible and member.id in t.raci_responsible) or
                t.raci_accountable == member.id
            )
        ]
        
        # Use cross-project workload if available, otherwise calculate from current project
        if cross_project_workload and member.id in cross_project_workload:
            member_workloads[member.id] = cross_project_workload[member.id]['sp']
        else:
            member_workloads[member.id] = sum(t.story_points or 0 for t in member_tasks[member.id])
    
    # Find overloaded and underloaded members
    avg_workload = sum(member_workloads.values()) / len(member_workloads) if member_workloads else 0
    
    overloaded = [
        (m, member_workloads[m.id]) for m in team_members
        if (member_workloads[m.id] / m.max_story_points * 100) > 85
    ]
    
    underloaded = [
        (m, member_workloads[m.id]) for m in team_members
        if (member_workloads[m.id] / m.max_story_points * 100) < 50
    ]
    
    # Suggest reassignments from overloaded to underloaded
    for overloaded_member, overloaded_sp in overloaded:
        # Get their tasks sorted by SP (smallest first for easier rebalancing)
        their_tasks = sorted(member_tasks[overloaded_member.id], key=lambda t: t.story_points or 0)
        
        for task in their_tasks:
            task_sp = task.story_points or 0
            if task_sp == 0:
                continue
            
            # Find best candidate from underloaded members
            for underloaded_member, underloaded_sp in underloaded:
                if underloaded_member.id == overloaded_member.id:
                    continue
                
                # Check if underloaded member has capacity
                if (underloaded_sp + task_sp) <= underloaded_member.max_story_points:
                    # Score the underloaded member for this task
                    task_requirements = {
                        'labels': task.labels or [],
                        'type': task.type,
                        'priority': task.priority
                    }
                    
                    score = team_scoring.score_member_for_task(
                        underloaded_member, task_requirements, tasks, underloaded_sp
                    )
                    
                    # Only suggest if score is reasonable
                    if score['final_score'] > 50:
                        proposals.append({
                            'id': f"rebalance-{task.id}-{uuid.uuid4().hex[:8]}",
                            'type': 'reassign',
                            'severity': 'recommended',
                            'category': 'workload',
                            'title': f"Rebalance: Move '{task.name}' to {underloaded_member.name}",
                            'description': f"Move task from overloaded {overloaded_member.name} to {underloaded_member.name}",
                            'reason': f"{overloaded_member.name} is overloaded ({round((overloaded_sp/overloaded_member.max_story_points)*100, 1)}% capacity). {underloaded_member.name} has capacity ({round((underloaded_sp/underloaded_member.max_story_points)*100, 1)}%).",
                            'score': score['final_score'],
                            'impact': {
                                'fromMember': overloaded_member.name,
                                'toMember': underloaded_member.name,
                                'fromWorkload': round((overloaded_sp/overloaded_member.max_story_points)*100, 1),
                                'fromWorkloadAfter': round(((overloaded_sp - task_sp)/overloaded_member.max_story_points)*100, 1),
                                'toWorkloadBefore': round((underloaded_sp/underloaded_member.max_story_points)*100, 1),
                                'toWorkload': round(((underloaded_sp + task_sp)/underloaded_member.max_story_points)*100, 1),
                                'taskSP': task_sp,
                                'affectedMembers': [overloaded_member.id, underloaded_member.id]
                            },
                            'action': {
                                'type': 'reassign',
                                'taskId': task.id,
                                'fromMemberId': overloaded_member.id,
                                'toMemberId': underloaded_member.id
                            }
                        })
                        
                        # Update tracking for next iteration
                        underloaded_sp += task_sp
                        break
    
    return proposals


def _calculate_projected_state_from_proposals(current_state, proposals):
    """Calculate projected state from all proposals"""
    projected = current_state.copy()
    
    # Count proposal types
    split_count = sum(1 for p in proposals if p.get('type') == 'split')
    reassign_count = sum(1 for p in proposals if p.get('type') == 'reassign')
    sprint_move_count = sum(1 for p in proposals if p.get('type') == 'sprint_move')
    
    # Estimate improvements
    if split_count > 0:
        projected['riskScore'] = max(3.0, projected['riskScore'] - (split_count * 0.5))
        projected['balanceScore'] = min(100, projected['balanceScore'] + (split_count * 3))
    
    if reassign_count > 0:
        projected['balanceScore'] = min(100, projected['balanceScore'] + (reassign_count * 5))
        projected['workload'] = max(50, projected['workload'] - (reassign_count * 2))
    
    if sprint_move_count > 0:
        projected['balanceScore'] = min(100, projected['balanceScore'] + (sprint_move_count * 2))
    
    return projected


@requirement_changes_bp.route('/<int:project_id>/analyze-pert-raci', methods=['POST'])
@token_required
def analyze_pert_raci(project_id):
    """
    Analyze project using PERT and RACI metrics
    Generate specialized proposals for PERT uncertainty, RACI overload, and duration risks
    
    Body:
        scope: "current_sprint" | "backlog" | "all_sprints" (default: "backlog")
    """
    try:
        data = request.get_json() or {}
        scope = data.get('scope', 'backlog')
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get project data
        all_tasks = Task.query.filter_by(project_id=project_id).all()
        team_members = TeamMember.query.filter(
            TeamMember.id.in_(project.team_member_ids or [])
        ).all()
        sprints = Sprint.query.filter_by(project_id=project_id).all()
        
        # Filter out Split tasks (already processed, should not be analyzed again)
        active_tasks = [t for t in all_tasks if t.status != 'Split']
        
        # Filter tasks by scope for analysis
        if scope == 'current_sprint':
            # Get active sprint
            active_sprint = next((s for s in sprints if s.status == 'active'), None)
            if active_sprint:
                tasks = [t for t in active_tasks if t.sprint_id == active_sprint.id]
                sprint_id = active_sprint.id
            else:
                tasks = []
                sprint_id = None
        elif scope == 'backlog':
            # Get only tasks not assigned to any sprint
            tasks = [t for t in active_tasks if t.sprint_id is None]
            sprint_id = None
        else:  # all_sprints
            tasks = active_tasks
            sprint_id = None
        
        # Calculate current state (always passes all tasks for accurate workload)
        current_state = _calculate_current_state(project, all_tasks, team_members, sprints)
        
        # Generate PERT/RACI specific proposals
        proposals = []
        
        # RACI workload-based analyses only make sense for current_sprint scope
        # Backlog tasks are not in a sprint yet, so RACI workload and duration adjustments don't apply
        is_sprint_scope = (scope == 'current_sprint')
        
        # 1. PERT Uncertainty Risks (analyze filtered tasks) - applies to ALL scopes
        # Uncertainty in estimates is relevant regardless of whether task is in backlog or sprint
        pert_uncertainty_proposals = pert_raci_analyzer.find_pert_uncertainty_risks(tasks)
        proposals.extend(pert_uncertainty_proposals)
        
        # 2. RACI Overload Risks (only for sprint scope - backlog doesn't contribute to current workload)
        if is_sprint_scope:
            raci_overload_proposals = pert_raci_analyzer.find_raci_overload_risks(
                team_members, tasks, sprint_id, all_tasks
            )
            proposals.extend(raci_overload_proposals)
        
        # 3. Adjusted Duration Risks (only for sprint scope - backlog doesn't affect current workload/duration)
        if is_sprint_scope:
            duration_risk_proposals = pert_raci_analyzer.find_adjusted_duration_risks(
                tasks, team_members, sprint_id, all_tasks
            )
            proposals.extend(duration_risk_proposals)
        
        # Categorize by severity
        categorized = {
            'critical': [p for p in proposals if p.get('severity') == 'critical'],
            'important': [p for p in proposals if p.get('severity') == 'important'],
            'recommended': [p for p in proposals if p.get('severity') == 'recommended']
        }
        
        # Calculate projected state
        projected_state = _calculate_projected_state_from_proposals(current_state, proposals)
        
        return jsonify({
            'currentState': current_state,
            'proposals': proposals,
            'categorized': categorized,
            'projectedState': projected_state,
            'totalProposals': len(proposals),
            'scope': scope,
            'message': f'Found {len(proposals)} PERT+RACI optimization opportunities ({len(categorized["critical"])} critical, {len(categorized["important"])} important, {len(categorized["recommended"])} recommended)'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to analyze PERT+RACI', 'message': str(e)}), 500


@requirement_changes_bp.route('/<int:project_id>/analyze-requirement-change', methods=['POST'])
@token_required
def analyze_requirement_change(project_id):
    """
    Analyze a requirement change and generate adaptation proposals
    
    Body:
        changeType: "add_task" | "increase_sp" | "change_priority" | "add_dependency"
        changeData: {...} - depends on changeType
        priorityStrategy: "minimize_duration" | "balance_workload" | "skills_match" | "balanced"
    """
    try:
        data = request.get_json()
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        change_type = data.get('changeType')
        change_data = data.get('changeData', {})
        priority_strategy = data.get('priorityStrategy', 'balanced')
        
        if not change_type:
            return jsonify({'error': 'changeType is required'}), 400
        
        # Get project data
        all_tasks = Task.query.filter_by(project_id=project_id).all()
        team_members = TeamMember.query.filter(
            TeamMember.id.in_(project.team_member_ids or [])
        ).all()
        sprints = Sprint.query.filter_by(project_id=project_id).all()
        
        # Filter out Split tasks (already processed, should not be analyzed again)
        tasks = [t for t in all_tasks if t.status != 'Split']
        
        # Calculate current state
        current_state = _calculate_current_state(project, tasks, team_members, sprints)
        
        # Generate proposals based on change type
        proposals = []
        
        if change_type == 'add_task':
            proposals.extend(_generate_add_task_proposals(
                change_data, team_members, tasks, sprints, priority_strategy
            ))
        elif change_type == 'increase_sp':
            # Calculate cross-project workload (include current project)
            cross_project_workload = calculate_cross_project_workload(team_members, exclude_project_id=None)
            proposals.extend(_generate_increase_sp_proposals(
                change_data, team_members, tasks, sprints, priority_strategy, cross_project_workload
            ))
        elif change_type == 'change_priority':
            proposals.extend(_generate_priority_change_proposals(
                change_data, team_members, tasks, priority_strategy
            ))
        elif change_type == 'add_dependency':
            proposals.extend(_generate_dependency_proposals(
                change_data, tasks
            ))
        else:
            return jsonify({'error': f'Unknown changeType: {change_type}'}), 400
        
        # Always check for split opportunities
        split_proposals = task_splitter.create_split_proposals(tasks)
        proposals.extend(split_proposals)
        
        # Always check for sprint reallocation opportunities
        sprint_proposals = sprint_analyzer.suggest_sprint_reallocation(sprints, tasks, team_members)
        proposals.extend(sprint_proposals)
        
        # Calculate projected state after applying all proposals
        projected_state = _calculate_projected_state(
            current_state, proposals, change_type, change_data
        )
        
        return jsonify({
            'currentState': current_state,
            'proposals': proposals,
            'projectedState': projected_state,
            'changeType': change_type,
            'priorityStrategy': priority_strategy
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to analyze requirement change', 'message': str(e)}), 500


@requirement_changes_bp.route('/<int:project_id>/apply-requirement-changes', methods=['POST'])
@token_required
def apply_requirement_changes(project_id):
    """
    Apply selected requirement change proposals
    
    Body:
        proposals: [{ id, type, action }]
        scope: Optional['current_sprint' | 'all_sprints' | 'backlog']
        optimizationType: Optional[str] - Type of optimization (default: 'manual')
    """
    try:
        data = request.get_json()
        proposals = data.get('proposals', [])
        scope = data.get('scope', None)
        optimization_type = data.get('optimizationType', 'manual')
        
        if not proposals:
            return jsonify({'error': 'No proposals provided'}), 400
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        applied = 0
        failed = 0
        errors = []
        applied_results = []
        
        for proposal in proposals:
            try:
                proposal_type = proposal.get('type')
                action = proposal.get('action', {})
                
                if proposal_type == 'reassign':
                    _apply_reassignment(action)
                    applied += 1
                    applied_results.append({'type': 'reassign', 'taskId': action.get('taskId')})
                elif proposal_type == 'split':
                    _apply_task_split(action, project_id)
                    applied += 1
                    applied_results.append({'type': 'split', 'taskId': action.get('taskId')})
                elif proposal_type == 'merge':
                    _apply_task_merge(action, project_id)
                    applied += 1
                    applied_results.append({'type': 'merge', 'taskIds': action.get('originalTaskIds', [])})
                elif proposal_type == 'sprint_move':
                    _apply_sprint_move(action)
                    applied += 1
                    applied_results.append({'type': 'sprint_move', 'taskId': action.get('taskId')})
                elif proposal_type == 'deadline_adjust':
                    _apply_deadline_adjustment(action)
                    applied += 1
                    applied_results.append({'type': 'deadline_adjust', 'taskId': action.get('taskId')})
                elif proposal_type == 'add_task':
                    _apply_add_task(action, project_id)
                    applied += 1
                    applied_results.append({'type': 'add_task', 'taskName': action.get('taskData', {}).get('name')})
                elif proposal_type == 'increase_sp':
                    _apply_increase_sp(action)
                    applied += 1
                    applied_results.append({'type': 'increase_sp', 'taskId': action.get('taskId')})
                elif proposal_type in ['bottleneck', 'priority_conflict', 'deadline_risk', 'skill_mismatch']:
                    # These are all reassignments, priority changes, or backlog moves
                    if action.get('type') == 'reassign':
                        _apply_reassignment(action)
                        applied += 1
                        applied_results.append({'type': proposal_type, 'action': 'reassign', 'taskId': action.get('taskId')})
                    elif action.get('type') == 'priority_increase':
                        _apply_priority_change(action)
                        applied += 1
                        applied_results.append({'type': proposal_type, 'action': 'priority_increase', 'taskId': action.get('taskId')})
                    elif action.get('type') == 'move_to_backlog':
                        _apply_move_to_backlog(action)
                        applied += 1
                        applied_results.append({'type': proposal_type, 'action': 'move_to_backlog', 'taskId': action.get('taskId')})
                    else:
                        failed += 1
                        errors.append(f"Unknown action type for {proposal_type}")
                elif proposal_type == 'idle_resource':
                    _apply_assign_task(action)
                    applied += 1
                    applied_results.append({'type': 'idle_resource', 'taskId': action.get('taskId')})
                elif proposal_type == 'pert_uncertainty':
                    # PERT uncertainty typically results in split action
                    if action.get('type') == 'split':
                        _apply_task_split(action, project_id)
                        applied += 1
                        applied_results.append({'type': 'pert_uncertainty', 'action': 'split', 'taskId': action.get('taskId')})
                    else:
                        failed += 1
                        errors.append(f"Unsupported action for pert_uncertainty: {action.get('type')}")
                elif proposal_type == 'duration_risk':
                    # Duration risk typically results in sprint move
                    if action.get('type') == 'sprint_move':
                        _apply_sprint_move(action)
                        applied += 1
                        applied_results.append({'type': 'duration_risk', 'action': 'sprint_move', 'taskId': action.get('taskId')})
                    else:
                        failed += 1
                        errors.append(f"Unsupported action for duration_risk: {action.get('type')}")
                elif proposal_type == 'raci_overload':
                    # RACI overload typically results in reassignment
                    if action.get('type') == 'reassign':
                        _apply_reassignment(action)
                        applied += 1
                        applied_results.append({'type': 'raci_overload', 'action': 'reassign', 'taskId': action.get('taskId')})
                    else:
                        failed += 1
                        errors.append(f"Unsupported action for raci_overload: {action.get('type')}")
                else:
                    failed += 1
                    errors.append(f"Unknown proposal type: {proposal_type}")
                    
            except Exception as e:
                failed += 1
                errors.append(str(e))
        
        # Create OptimizationLog entry
        if applied > 0:
            optimization_log = OptimizationLog(
                project_id=project_id,
                optimization_type=optimization_type,
                proposals_count=len(proposals),
                applied_count=applied,
                scope=scope,
                results={
                    'applied': applied_results,
                    'failed': failed,
                    'errors': errors if errors else None
                }
            )
            db.session.add(optimization_log)
        
        db.session.commit()
        
        # Reload project with updated data
        updated_project = Project.query.get(project_id)
        
        return jsonify({
            'applied': applied,
            'failed': failed,
            'errors': errors if errors else None,
            'message': f'Applied {applied} changes, {failed} failed'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to apply changes', 'message': str(e)}), 500


# Helper functions

def _calculate_current_state(project, tasks, team_members, sprints):
    """Calculate current project state metrics (including PERT/RACI metrics)"""
    
    # Filter out Split tasks (should not be counted in current state)
    active_tasks = [t for t in tasks if t.status != 'Split']
    
    # Get active sprint
    active_sprint = next((s for s in sprints if s.status == 'active'), None)
    
    # Calculate total story points from active sprint (Sprint Commitment)
    active_sprint_tasks = [t for t in active_tasks if active_sprint and t.sprint_id == active_sprint.id]
    total_sp = sum(task.story_points or 0 for task in active_sprint_tasks)
    completed_sp = sum(task.story_points or 0 for task in active_sprint_tasks if task.status == 'Done')
    
    # Calculate team workload based on active sprint
    team_capacity = sum(member.max_story_points for member in team_members)
    avg_workload = (total_sp / team_capacity * 100) if team_capacity > 0 else 0
    
    # Calculate duration from PERT for active sprint
    total_duration = sum(task.pert_expected or (task.story_points * 0.5) or 0 
                        for task in active_sprint_tasks)
    
    # Calculate risk score based on uncertainty
    risk_scores = []
    for task in active_sprint_tasks:
        if task.pert_optimistic and task.pert_pessimistic and task.pert_expected:
            uncertainty = (task.pert_pessimistic - task.pert_optimistic) / task.pert_expected
            risk_scores.append(uncertainty * 10)
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 5.0
    
    # Calculate balance score based on active sprint workload
    member_workloads = []
    for member in team_members:
        member_tasks = [t for t in active_sprint_tasks if (
            (t.raci_responsible and member.id in t.raci_responsible) or
            t.raci_accountable == member.id
        )]
        member_sp = sum(t.story_points or 0 for t in member_tasks)
        member_workloads.append((member_sp / member.max_story_points) * 100)
    
    if member_workloads:
        avg_load = sum(member_workloads) / len(member_workloads)
        variance = sum((w - avg_load) ** 2 for w in member_workloads) / len(member_workloads)
        balance_score = max(0, 100 - (variance ** 0.5))
    else:
        balance_score = 100
    
    # === NEW: PERT/RACI Metrics ===
    
    # 1. Total PERT Duration
    total_pert_duration = sum(
        task.pert_expected or 0 for task in active_sprint_tasks
    )
    
    # 2. Total Adjusted Duration (RACI-adjusted)
    # Calculate CROSS-PROJECT RACI-weighted workload (matches frontend)
    # This includes ALL projects where team members work, not just this project
    from app.utils.workload_calculator import calculate_cross_project_raci_workload
    
    cross_project_raci_workload = calculate_cross_project_raci_workload(
        team_members,
        sprint_id=active_sprint.id if active_sprint else None
    )
    
    # Convert to format expected by _calculate_task_adjusted_duration
    member_workloads_dict = {}
    for member in team_members:
        if member.id in cross_project_raci_workload:
            weighted_sp = cross_project_raci_workload[member.id]['weighted_sp']
            member_workloads_dict[member.id] = {
                'weighted_sp': weighted_sp,
                'roles': {}  # Not needed for duration calculation
            }
    
    total_adjusted_duration = 0
    for task in active_sprint_tasks:
        adjusted_duration = pert_raci_analyzer._calculate_task_adjusted_duration(
            task, team_members, member_workloads_dict
        )
        total_adjusted_duration += adjusted_duration
    
    # 3. Average PERT Uncertainty (Coefficient of Variation)
    # Using standard PERT formula: CV = σ / Expected, where σ = (P - O) / 6
    cv_values = []
    for task in active_sprint_tasks:
        if task.pert_optimistic and task.pert_pessimistic and task.pert_expected and task.pert_expected > 0:
            std_dev = (task.pert_pessimistic - task.pert_optimistic) / 6.0
            cv = std_dev / task.pert_expected
            cv_values.append(cv)
    avg_pert_uncertainty = (sum(cv_values) / len(cv_values)) if cv_values else 0
    
    # 4. RACI Workload (average weighted workload percentage)
    # Only count members with at least 1 weighted SP (same as frontend filter)
    raci_workload_percentages = []
    for member in team_members:
        if member.id in member_workloads_dict:
            weighted_sp = member_workloads_dict[member.id]['weighted_sp']
            # Only include members with at least 1 weighted SP
            if weighted_sp >= 1:
                workload_pct = (weighted_sp / member.max_story_points * 100) if member.max_story_points > 0 else 0
                raci_workload_percentages.append(workload_pct)
    avg_raci_workload = (sum(raci_workload_percentages) / len(raci_workload_percentages)) if raci_workload_percentages else 0
    
    # 5. Duration Overhead (percentage increase)
    duration_overhead = 0
    if total_pert_duration > 0:
        duration_overhead = ((total_adjusted_duration - total_pert_duration) / total_pert_duration) * 100
    
    return {
        'totalStoryPoints': total_sp,
        'completedStoryPoints': completed_sp,
        'duration': round(total_duration, 1),
        'workload': round(avg_workload, 1),
        'riskScore': round(avg_risk, 1),
        'balanceScore': round(balance_score, 1),
        'teamCapacity': team_capacity,
        'taskCount': len(active_tasks),
        'sprintCount': len(sprints),
        # PERT/RACI metrics
        'totalPertDuration': round(total_pert_duration, 1),
        'totalAdjustedDuration': round(total_adjusted_duration, 1),
        'avgPertUncertainty': round(avg_pert_uncertainty * 100, 1),  # as percentage
        'raciWorkload': round(avg_raci_workload, 1),
        'durationOverhead': round(duration_overhead, 1)  # as percentage
    }


def _calculate_projected_state(current_state, proposals, change_type, change_data):
    """Calculate projected state after applying proposals"""
    
    projected = current_state.copy()
    
    # Adjust based on change type
    if change_type == 'add_task':
        new_sp = change_data.get('storyPoints', 0)
        projected['totalStoryPoints'] += new_sp
        projected['taskCount'] += 1
        
        # Recalculate workload
        projected['workload'] = round(
            (projected['totalStoryPoints'] / projected['teamCapacity']) * 100, 1
        ) if projected['teamCapacity'] > 0 else 0
        
    elif change_type == 'increase_sp':
        sp_increase = change_data.get('additionalSP', 0)
        projected['totalStoryPoints'] += sp_increase
        projected['workload'] = round(
            (projected['totalStoryPoints'] / projected['teamCapacity']) * 100, 1
        ) if projected['teamCapacity'] > 0 else 0
    
    # Apply proposal impacts
    for proposal in proposals:
        if proposal.get('type') == 'split':
            # Splitting doesn't change total SP but improves metrics
            projected['riskScore'] = max(3.0, projected['riskScore'] - 0.5)
            projected['balanceScore'] = min(100, projected['balanceScore'] + 5)
            
        elif proposal.get('type') == 'reassign':
            # Reassignment improves balance
            projected['balanceScore'] = min(100, projected['balanceScore'] + 3)
            
        elif proposal.get('type') == 'sprint_move':
            # Sprint reallocation improves planning
            projected['balanceScore'] = min(100, projected['balanceScore'] + 2)
    
    return projected


def _generate_add_task_proposals(change_data, team_members, tasks, sprints, strategy):
    """Generate proposals for adding a new task"""
    proposals = []
    
    # Get active sprint
    active_sprint = next((s for s in sprints if s.status == 'active'), None)
    
    # Calculate member workloads from active sprint (Sprint Commitment)
    member_workloads = {}
    for member in team_members:
        member_tasks = [t for t in tasks 
            if (active_sprint and t.sprint_id == active_sprint.id) and (
                (t.raci_responsible and member.id in t.raci_responsible) or
                t.raci_accountable == member.id
            )]
        member_workloads[member.id] = sum(t.story_points or 0 for t in member_tasks)
    
    # Score team members for this task
    task_requirements = {
        'labels': change_data.get('labels', []),
        'type': change_data.get('type', 'task'),
        'priority': change_data.get('priority', 'medium')
    }
    
    rankings = team_scoring.rank_members_for_task(
        team_members, task_requirements, tasks, member_workloads
    )
    
    # Get top candidates based on strategy
    if strategy == 'balance_workload':
        # Sort by workload (ascending)
        rankings.sort(key=lambda x: x['current_sp'])
    elif strategy == 'skills_match':
        # Sort by skills score
        rankings.sort(key=lambda x: x['breakdown']['skills'], reverse=True)
    elif strategy == 'minimize_duration':
        # Sort by availability and experience
        rankings.sort(key=lambda x: x['breakdown']['availability'] + x['breakdown']['history'], reverse=True)
    # else: use default balanced scoring
    
    # Create assignment proposal
    if rankings:
        best_member = rankings[0]
        
        proposals.append({
            'id': f"add-task-assign-{uuid.uuid4().hex[:8]}",
            'type': 'add_task',
            'title': f"Assign new task to {best_member['member_name']}",
            'description': f"Add new task '{change_data.get('name', 'New Task')}' and assign to {best_member['member_name']}",
            'reason': f"Best match based on {strategy} strategy. Score: {best_member['final_score']}/100",
            'score': best_member['final_score'],
            'impact': {
                'assignedMember': best_member['member_name'],
                'workloadChange': {
                    'before': best_member['workload_percentage'],
                    'after': round((best_member['current_sp'] + change_data.get('storyPoints', 0)) / best_member['max_sp'] * 100, 1)
                },
                'affectedMembers': [best_member['member_id']]
            },
            'action': {
                'type': 'add_task',
                'taskData': change_data,
                'assignTo': best_member['member_id']
            }
        })
        
        # Also show alternative candidates
        if len(rankings) > 1:
            for alt_member in rankings[1:3]:  # Show top 2 alternatives
                proposals.append({
                    'id': f"add-task-assign-alt-{alt_member['member_id']}-{uuid.uuid4().hex[:8]}",
                    'type': 'add_task',
                    'title': f"Alternative: Assign to {alt_member['member_name']}",
                    'description': f"Alternative assignment option",
                    'reason': f"Alternative candidate. Score: {alt_member['final_score']}/100",
                    'score': alt_member['final_score'],
                    'impact': {
                        'assignedMember': alt_member['member_name'],
                        'workloadChange': {
                            'before': alt_member['workload_percentage'],
                            'after': round((alt_member['current_sp'] + change_data.get('storyPoints', 0)) / alt_member['max_sp'] * 100, 1)
                        },
                        'affectedMembers': [alt_member['member_id']]
                    },
                    'action': {
                        'type': 'add_task',
                        'taskData': change_data,
                        'assignTo': alt_member['member_id']
                    }
                })
    
    return proposals


def _generate_increase_sp_proposals(change_data, team_members, tasks, sprints, strategy, cross_project_workload=None):
    """Generate proposals for increasing task story points"""
    proposals = []
    
    task_id = change_data.get('taskId')
    additional_sp = change_data.get('additionalSP', 0)
    
    if not task_id:
        return proposals
    
    task = Task.query.get(task_id)
    if not task:
        return proposals
    
    new_sp = (task.story_points or 0) + additional_sp
    
    # Check if task should be split after increase
    if new_sp >= 21:
        split_suggestion = task_splitter.suggest_split(task)
        if split_suggestion.get('should_split'):
            proposals.append({
                'id': f"increase-sp-split-{task_id}-{uuid.uuid4().hex[:8]}",
                'type': 'split',
                'title': f"Split task '{task.name}' after SP increase",
                'description': f"Task will have {new_sp} SP after increase. Consider splitting.",
                'reason': split_suggestion['reason'],
                'score': 85,
                'impact': {
                    'originalSP': task.story_points,
                    'newSP': new_sp,
                    'splitInto': split_suggestion['num_parts'],
                    'improvement': split_suggestion['estimated_improvement']
                },
                'action': {
                    'type': 'split',
                    'taskId': task_id,
                    'subtasks': split_suggestion['subtasks']
                }
            })
    
    # Get active sprint
    active_sprint = next((s for s in sprints if s.status == 'active'), None)
    
    # Check if current assignee can handle increased workload
    if task.raci_responsible:
        for member_id in task.raci_responsible:
            member = TeamMember.query.get(member_id)
            if member:
                # Calculate current and new workload from active sprint (Sprint Commitment)
                member_tasks = [t for t in tasks 
                    if t.id != task_id and (active_sprint and t.sprint_id == active_sprint.id) and (
                        (t.raci_responsible and member.id in t.raci_responsible) or
                        t.raci_accountable == member.id
                    )]
                current_sp = sum(t.story_points or 0 for t in member_tasks) + (task.story_points or 0)
                new_total_sp = current_sp + additional_sp
                
                new_workload_pct = (new_total_sp / member.max_story_points) * 100
                
                # If workload exceeds 90%, suggest reassignment
                if new_workload_pct > 90:
                    # Find better candidate (use cross-project workload if available)
                    member_workloads = {}
                    for tm in team_members:
                        if cross_project_workload and tm.id in cross_project_workload:
                            member_workloads[tm.id] = cross_project_workload[tm.id]['sp']
                        else:
                            # Calculate from active sprint (Sprint Commitment)
                            tm_tasks = [t for t in tasks 
                                if (active_sprint and t.sprint_id == active_sprint.id) and (
                                    (t.raci_responsible and tm.id in t.raci_responsible) or
                                    t.raci_accountable == tm.id
                                )]
                            member_workloads[tm.id] = sum(t.story_points or 0 for t in tm_tasks)
                    
                    task_requirements = {
                        'labels': task.labels or [],
                        'type': task.type,
                        'priority': task.priority
                    }
                    
                    rankings = team_scoring.rank_members_for_task(
                        team_members, task_requirements, tasks, member_workloads
                    )
                    
                    # Find someone other than current assignee
                    for candidate in rankings:
                        if candidate['member_id'] != member_id:
                            # Calculate workload after reassignment
                            from_workload_after = ((current_sp - (task.story_points or 0)) / member.max_story_points) * 100
                            candidate_member = TeamMember.query.get(candidate['member_id'])
                            to_workload = ((member_workloads.get(candidate['member_id'], 0) + new_sp) / candidate_member.max_story_points) * 100 if candidate_member else candidate['workload_percentage']
                            
                            proposals.append({
                                'id': f"increase-sp-reassign-{task_id}-{uuid.uuid4().hex[:8]}",
                                'type': 'reassign',
                                'title': f"Reassign '{task.name}' after SP increase",
                                'description': f"Reassign from {member.name} to {candidate['member_name']}",
                                'reason': f"{member.name} would be overloaded ({round(new_workload_pct, 1)}% workload)",
                                'score': candidate['final_score'],
                                'impact': {
                                    'fromMember': member.name,
                                    'toMember': candidate['member_name'],
                                    'fromWorkload': round(new_workload_pct, 1),
                                    'fromWorkloadAfter': round(from_workload_after, 1),
                                    'toWorkloadBefore': candidate['workload_percentage'],
                                    'toWorkload': round(to_workload, 1),
                                    'affectedMembers': [member_id, candidate['member_id']]
                                },
                                'action': {
                                    'type': 'reassign',
                                    'taskId': task_id,
                                    'fromMemberId': member_id,
                                    'toMemberId': candidate['member_id']
                                }
                            })
                            break
    
    # Always create the increase SP proposal
    proposals.append({
        'id': f"increase-sp-{task_id}-{uuid.uuid4().hex[:8]}",
        'type': 'increase_sp',
        'title': f"Increase SP for '{task.name}'",
        'description': f"Increase story points from {task.story_points} to {new_sp}",
        'reason': "Required by client",
        'score': 100,
        'impact': {
            'spBefore': task.story_points,
            'spAfter': new_sp,
            'increase': additional_sp
        },
        'action': {
            'type': 'increase_sp',
            'taskId': task_id,
            'newSP': new_sp
        }
    })
    
    return proposals


def _generate_priority_change_proposals(change_data, team_members, tasks, strategy):
    """Generate proposals for changing task priority"""
    proposals = []
    
    task_id = change_data.get('taskId')
    new_priority = change_data.get('newPriority')
    
    if not task_id or not new_priority:
        return proposals
    
    task = Task.query.get(task_id)
    if not task:
        return proposals
    
    # Create priority change proposal
    proposals.append({
        'id': f"priority-change-{task_id}-{uuid.uuid4().hex[:8]}",
        'type': 'priority_change',
        'title': f"Change priority of '{task.name}'",
        'description': f"Change priority from {task.priority} to {new_priority}",
        'reason': "Required by client",
        'score': 100,
        'impact': {
            'priorityBefore': task.priority,
            'priorityAfter': new_priority
        },
        'action': {
            'type': 'priority_change',
            'taskId': task_id,
            'newPriority': new_priority
        }
    })
    
    return proposals


def _generate_dependency_proposals(change_data, tasks):
    """Generate proposals for adding dependencies"""
    proposals = []
    
    # Implementation for dependency proposals
    # This would analyze critical path and suggest optimizations
    
    return proposals


# Application functions

def _apply_reassignment(action):
    """Apply task reassignment"""
    task_id = action.get('taskId')
    from_member_id = action.get('fromMemberId')
    to_member_id = action.get('toMemberId')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    # Update RACI responsible
    if task.raci_responsible and from_member_id in task.raci_responsible:
        task.raci_responsible = [m for m in task.raci_responsible if m != from_member_id]
        if to_member_id not in task.raci_responsible:
            task.raci_responsible.append(to_member_id)
    
    db.session.add(task)


def _apply_task_split(action, project_id):
    """Apply task split into subtasks"""
    task_id = action.get('taskId')
    subtasks_data = action.get('subtasks', [])
    
    original_task = Task.query.get(task_id)
    if not original_task:
        raise ValueError(f"Task {task_id} not found")
    
    # If no subtasks provided (e.g., from PERT uncertainty), generate them
    if not subtasks_data:
        # Determine number of subtasks based on CV or SP
        num_parts = 2
        if original_task.pert_expected and original_task.pert_optimistic and original_task.pert_pessimistic:
            # Calculate CV
            std_dev = (original_task.pert_pessimistic - original_task.pert_optimistic) / 6.0
            cv = std_dev / original_task.pert_expected if original_task.pert_expected > 0 else 0
            
            if cv >= 0.50:
                num_parts = 4
            elif cv >= 0.33:
                num_parts = 3
            else:
                num_parts = 2
        elif original_task.story_points and original_task.story_points >= 34:
            num_parts = 3
        
        # Generate subtasks using TaskSplitterService
        split_result = task_splitter.suggest_split(original_task, num_parts)
        subtasks_data = split_result.get('subtasks', [])
    
    # Save original task data before deletion
    saved_sprint_id = original_task.sprint_id
    saved_project_id = original_task.project_id
    saved_raci_responsible = original_task.raci_responsible
    saved_raci_accountable = original_task.raci_accountable
    saved_raci_consulted = original_task.raci_consulted
    saved_raci_informed = original_task.raci_informed
    
    # Create subtasks (no parent reference needed - original will be deleted)
    for subtask_data in subtasks_data:
        new_task = Task(
            project_id=project_id,
            sprint_id=saved_sprint_id,
            name=subtask_data['name'],
            title=subtask_data['title'],
            description=subtask_data['description'],
            story_points=subtask_data['story_points'],
            type=subtask_data['type'],
            priority=subtask_data['priority'],
            labels=subtask_data['labels'],
            complexity=subtask_data['complexity'],
            status=subtask_data['status']
        )
        
        # Copy PERT if available
        if subtask_data.get('pert'):
            pert = subtask_data['pert']
            new_task.pert_optimistic = pert.get('optimistic')
            new_task.pert_most_likely = pert.get('mostLikely')
            new_task.pert_pessimistic = pert.get('pessimistic')
            new_task.calculate_pert_expected()
        
        # Copy RACI from original task
        new_task.raci_responsible = saved_raci_responsible
        new_task.raci_accountable = saved_raci_accountable
        new_task.raci_consulted = saved_raci_consulted
        new_task.raci_informed = saved_raci_informed
        
        db.session.add(new_task)
    
    # Delete original task (subtasks replace it completely)
    db.session.delete(original_task)


def _apply_sprint_move(action):
    """Apply sprint reallocation"""
    task_id = action.get('taskId')
    to_sprint_id = action.get('toSprintId')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    # Cannot assign blocked tasks to a sprint
    if task.status == 'Blocked' and to_sprint_id is not None:
        raise ValueError(f"Cannot assign blocked task '{task.name}' to sprint. Task must have all dependencies completed first.")
    
    task.sprint_id = to_sprint_id
    db.session.add(task)


def _apply_deadline_adjustment(action):
    """Apply deadline adjustment"""
    task_id = action.get('taskId')
    new_due_date = action.get('newDueDate')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    if new_due_date:
        task.due_date = datetime.fromisoformat(new_due_date)
        db.session.add(task)


def _apply_add_task(action, project_id):
    """Apply adding new task"""
    task_data = action.get('taskData', {})
    assign_to = action.get('assignTo')
    
    new_task = Task(
        project_id=project_id,
        name=task_data.get('name', 'New Task'),
        title=task_data.get('title', task_data.get('name', 'New Task')),
        description=task_data.get('description', ''),
        story_points=task_data.get('storyPoints', 0),
        type=task_data.get('type', 'task'),
        priority=task_data.get('priority', 'medium'),
        labels=task_data.get('labels', []),
        status='To Do',
        complexity=task_data.get('complexity', 0),
        completed=False,
        required_skills=task_data.get('requiredSkills', []),
        estimated_hours=task_data.get('estimatedHours', 0),
        actual_hours=0,
        risk_level=task_data.get('riskLevel', 'low')
    )
    
    # Assign to member
    if assign_to:
        new_task.raci_responsible = [assign_to]
        new_task.raci_accountable = assign_to
    
    # PERT if provided
    if 'pert' in task_data:
        pert = task_data['pert']
        new_task.pert_optimistic = pert.get('optimistic')
        new_task.pert_most_likely = pert.get('mostLikely')
        new_task.pert_pessimistic = pert.get('pessimistic')
        new_task.calculate_pert_expected()
    
    db.session.add(new_task)
    
    # Update project stats (total_tasks is now computed dynamically)
    project = Project.query.get(project_id)
    if project:
        if new_task.story_points:
            project.total_story_points += new_task.story_points


def _apply_increase_sp(action):
    """Apply story points increase"""
    task_id = action.get('taskId')
    new_sp = action.get('newSP')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    old_sp = task.story_points or 0
    task.story_points = new_sp
    
    # Update project total
    project = Project.query.get(task.project_id)
    if project:
        project.total_story_points = (project.total_story_points or 0) - old_sp + new_sp
    
    db.session.add(task)


def _apply_task_merge(action, project_id):
    """Apply task merge - combine multiple tasks into one"""
    merged_task_data = action.get('mergedTask', {})
    original_task_ids = action.get('originalTaskIds', [])
    
    # Create merged task
    new_task = Task(
        project_id=project_id,
        name=merged_task_data.get('name'),
        title=merged_task_data.get('title'),
        description=merged_task_data.get('description'),
        story_points=merged_task_data.get('story_points'),
        type=merged_task_data.get('type'),
        priority=merged_task_data.get('priority'),
        sprint_id=merged_task_data.get('sprint_id'),
        labels=merged_task_data.get('labels'),
        status=merged_task_data.get('status', 'To Do')
    )
    
    # Copy PERT if available
    if merged_task_data.get('pert'):
        pert = merged_task_data['pert']
        new_task.pert_optimistic = pert.get('optimistic')
        new_task.pert_most_likely = pert.get('mostLikely')
        new_task.pert_pessimistic = pert.get('pessimistic')
        new_task.calculate_pert_expected()
    
    # Copy RACI
    new_task.raci_responsible = merged_task_data.get('raci_responsible')
    new_task.raci_accountable = merged_task_data.get('raci_accountable')
    
    db.session.add(new_task)
    
    # Mark original tasks as Done
    for task_id in original_task_ids:
        original_task = Task.query.get(task_id)
        if original_task:
            original_task.status = 'Done'
            original_task.completed = True
            db.session.add(original_task)


def _apply_priority_change(action):
    """Apply priority change to task"""
    task_id = action.get('taskId')
    new_priority = action.get('newPriority')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    task.priority = new_priority
    db.session.add(task)


def _apply_assign_task(action):
    """Assign task to a member"""
    task_id = action.get('taskId')
    to_member_id = action.get('toMemberId')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    # Assign as responsible and accountable
    task.raci_responsible = [to_member_id]
    task.raci_accountable = to_member_id
    db.session.add(task)


def _apply_move_to_backlog(action):
    """Move task to backlog (unassign and mark for future sprint)"""
    task_id = action.get('taskId')
    from_member_id = action.get('fromMemberId')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    # Unassign from member
    if task.raci_responsible and from_member_id:
        task.raci_responsible = [m for m in task.raci_responsible if m != from_member_id]
    
    # If no other responsible members, unassign completely
    if not task.raci_responsible:
        task.raci_accountable = None
    
    # Remove from current sprint
    task.sprint_id = None
    
    # Add backlog label
    if not task.labels:
        task.labels = []
    if 'backlog' not in task.labels:
        task.labels.append('backlog')
    
    db.session.add(task)



