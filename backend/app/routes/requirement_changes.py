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
from app.services.team_scoring import TeamScoringService
from app.services.task_splitter import TaskSplitterService
from app.services.sprint_analyzer import SprintAnalyzerService
from app.services.task_merger import TaskMergerService
from app.services.bottleneck_analyzer import BottleneckAnalyzerService
from app.services.dependency_optimizer import DependencyOptimizerService
from app.services.risk_analyzer import RiskAnalyzerService
from app.utils.auth import token_required
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


@requirement_changes_bp.route('/<int:project_id>/auto-optimize', methods=['POST'])
@token_required
def auto_optimize_project(project_id):
    """
    Automatically analyze entire project and suggest all possible improvements
    Supports scope: current_sprint or all_sprints
    """
    try:
        data = request.get_json() or {}
        scope = data.get('scope', 'all_sprints')  # 'current_sprint' or 'all_sprints'
        
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
        
        # Filter tasks by scope
        if scope == 'current_sprint':
            # Get active sprint
            active_sprint = next((s for s in sprints if s.status == 'active'), None)
            if active_sprint:
                tasks = [t for t in all_tasks if t.sprint_id == active_sprint.id]
            else:
                tasks = []
        else:
            tasks = all_tasks
        
        # Calculate current state
        current_state = _calculate_current_state(project, tasks, team_members, sprints)
        
        # Generate all possible optimization proposals
        proposals = []
        
        # 1. CRITICAL: Deadline risks
        deadline_proposals = risk_analyzer.find_deadline_risks(tasks)
        proposals.extend(deadline_proposals)
        
        # 2. CRITICAL: Priority conflicts  
        priority_proposals = risk_analyzer.find_priority_conflicts(team_members, tasks)
        proposals.extend(priority_proposals)
        
        # 3. CRITICAL: Resource bottlenecks
        bottleneck_proposals = bottleneck_analyzer.find_resource_bottlenecks(team_members, tasks)
        proposals.extend(bottleneck_proposals)
        
        # 4. CRITICAL: Dependency bottlenecks
        dep_bottleneck_proposals = bottleneck_analyzer.find_dependency_bottlenecks(tasks)
        proposals.extend(dep_bottleneck_proposals)
        
        # 5. IMPORTANT: Task splits (21+ SP)
        split_proposals = task_splitter.create_split_proposals(tasks)
        proposals.extend(split_proposals)
        
        # 6. IMPORTANT: Sprint overflow
        sprint_proposals = sprint_analyzer.suggest_sprint_reallocation(sprints, all_tasks, team_members)
        proposals.extend(sprint_proposals)
        
        # 7. IMPORTANT: Skill mismatches
        skill_proposals = risk_analyzer.find_skill_mismatches(team_members, tasks)
        proposals.extend(skill_proposals)
        
        # 8. IMPORTANT: Cross-sprint dependencies
        cross_sprint_proposals = dependency_optimizer.find_cross_sprint_dependencies(all_tasks, sprints)
        proposals.extend(cross_sprint_proposals)
        
        # 9. RECOMMENDED: Workload rebalancing
        rebalance_proposals = _generate_workload_rebalancing_proposals(team_members, tasks, sprints)
        proposals.extend(rebalance_proposals)
        
        # 10. RECOMMENDED: Task merges
        merge_proposals = task_merger.create_merge_proposals(tasks)
        proposals.extend(merge_proposals)
        
        # 11. RECOMMENDED: Parallel opportunities
        parallel_proposals = dependency_optimizer.find_parallel_opportunities(tasks)
        proposals.extend(parallel_proposals)
        
        # 12. RECOMMENDED: Idle resources
        idle_proposals = risk_analyzer.find_idle_resources(team_members, tasks)
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


def _generate_workload_rebalancing_proposals(team_members, tasks, sprints):
    """Generate proposals to rebalance workload across team members"""
    proposals = []
    
    if not team_members or len(team_members) < 2:
        return proposals
    
    # Calculate current workload for each member
    member_workloads = {}
    member_tasks = {}
    
    for member in team_members:
        member_tasks[member.id] = [
            t for t in tasks if t.status != 'Done' and (
                (t.raci_responsible and member.id in t.raci_responsible) or
                t.raci_accountable == member.id
            )
        ]
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
        tasks = Task.query.filter_by(project_id=project_id).all()
        team_members = TeamMember.query.filter(
            TeamMember.id.in_(project.team_member_ids or [])
        ).all()
        sprints = Sprint.query.filter_by(project_id=project_id).all()
        
        # Calculate current state
        current_state = _calculate_current_state(project, tasks, team_members, sprints)
        
        # Generate proposals based on change type
        proposals = []
        
        if change_type == 'add_task':
            proposals.extend(_generate_add_task_proposals(
                change_data, team_members, tasks, sprints, priority_strategy
            ))
        elif change_type == 'increase_sp':
            proposals.extend(_generate_increase_sp_proposals(
                change_data, team_members, tasks, sprints, priority_strategy
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
    """
    try:
        data = request.get_json()
        proposals = data.get('proposals', [])
        
        if not proposals:
            return jsonify({'error': 'No proposals provided'}), 400
        
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        applied = 0
        failed = 0
        errors = []
        
        for proposal in proposals:
            try:
                proposal_type = proposal.get('type')
                action = proposal.get('action', {})
                
                if proposal_type == 'reassign':
                    _apply_reassignment(action)
                    applied += 1
                elif proposal_type == 'split':
                    _apply_task_split(action, project_id)
                    applied += 1
                elif proposal_type == 'merge':
                    _apply_task_merge(action, project_id)
                    applied += 1
                elif proposal_type == 'sprint_move':
                    _apply_sprint_move(action)
                    applied += 1
                elif proposal_type == 'deadline_adjust':
                    _apply_deadline_adjustment(action)
                    applied += 1
                elif proposal_type == 'add_task':
                    _apply_add_task(action, project_id)
                    applied += 1
                elif proposal_type == 'increase_sp':
                    _apply_increase_sp(action)
                    applied += 1
                elif proposal_type in ['bottleneck', 'priority_conflict', 'deadline_risk', 'skill_mismatch']:
                    # These are all reassignments, priority changes, or backlog moves
                    if action.get('type') == 'reassign':
                        _apply_reassignment(action)
                        applied += 1
                    elif action.get('type') == 'priority_increase':
                        _apply_priority_change(action)
                        applied += 1
                    elif action.get('type') == 'move_to_backlog':
                        _apply_move_to_backlog(action)
                        applied += 1
                    else:
                        failed += 1
                        errors.append(f"Unknown action type for {proposal_type}")
                elif proposal_type == 'cross_sprint_dep':
                    _apply_sprint_move(action)
                    applied += 1
                elif proposal_type == 'parallel_opportunity':
                    _apply_remove_dependency(action)
                    applied += 1
                elif proposal_type == 'idle_resource':
                    _apply_assign_task(action)
                    applied += 1
                else:
                    failed += 1
                    errors.append(f"Unknown proposal type: {proposal_type}")
                    
            except Exception as e:
                failed += 1
                errors.append(str(e))
        
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
    """Calculate current project state metrics"""
    
    # Calculate total story points
    total_sp = sum(task.story_points or 0 for task in tasks if task.status != 'Done')
    completed_sp = sum(task.story_points or 0 for task in tasks if task.status == 'Done')
    
    # Calculate team workload
    team_capacity = sum(member.max_story_points for member in team_members)
    avg_workload = (total_sp / team_capacity * 100) if team_capacity > 0 else 0
    
    # Calculate duration from PERT
    total_duration = sum(task.pert_expected or (task.story_points * 0.5) or 0 
                        for task in tasks if task.status != 'Done')
    
    # Calculate risk score based on uncertainty
    risk_scores = []
    for task in tasks:
        if task.pert_optimistic and task.pert_pessimistic and task.pert_expected:
            uncertainty = (task.pert_pessimistic - task.pert_optimistic) / task.pert_expected
            risk_scores.append(uncertainty * 10)
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 5.0
    
    # Calculate balance score
    member_workloads = []
    for member in team_members:
        member_tasks = [t for t in tasks if t.status != 'Done' and (
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
    
    return {
        'totalStoryPoints': total_sp,
        'completedStoryPoints': completed_sp,
        'duration': round(total_duration, 1),
        'workload': round(avg_workload, 1),
        'riskScore': round(avg_risk, 1),
        'balanceScore': round(balance_score, 1),
        'teamCapacity': team_capacity,
        'taskCount': len(tasks),
        'sprintCount': len(sprints)
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
    
    # Calculate member workloads
    member_workloads = {}
    for member in team_members:
        member_tasks = [t for t in tasks if t.status != 'Done' and (
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


def _generate_increase_sp_proposals(change_data, team_members, tasks, sprints, strategy):
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
    
    # Check if current assignee can handle increased workload
    if task.raci_responsible:
        for member_id in task.raci_responsible:
            member = TeamMember.query.get(member_id)
            if member:
                # Calculate current and new workload
                member_tasks = [t for t in tasks if t.id != task_id and t.status != 'Done' and (
                    (t.raci_responsible and member.id in t.raci_responsible) or
                    t.raci_accountable == member.id
                )]
                current_sp = sum(t.story_points or 0 for t in member_tasks) + (task.story_points or 0)
                new_total_sp = current_sp + additional_sp
                
                new_workload_pct = (new_total_sp / member.max_story_points) * 100
                
                # If workload exceeds 90%, suggest reassignment
                if new_workload_pct > 90:
                    # Find better candidate
                    member_workloads = {}
                    for tm in team_members:
                        tm_tasks = [t for t in tasks if t.status != 'Done' and (
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
                                    'toWorkload': candidate['workload_percentage'],
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
    
    # Mark original task as Done or remove it
    original_task.status = 'Done'
    original_task.completed = True
    db.session.add(original_task)
    
    # Create subtasks
    for subtask_data in subtasks_data:
        new_task = Task(
            project_id=project_id,
            sprint_id=original_task.sprint_id,
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
        
        # Copy RACI from original
        new_task.raci_responsible = original_task.raci_responsible
        new_task.raci_accountable = original_task.raci_accountable
        new_task.raci_consulted = original_task.raci_consulted
        new_task.raci_informed = original_task.raci_informed
        
        db.session.add(new_task)


def _apply_sprint_move(action):
    """Apply sprint reallocation"""
    task_id = action.get('taskId')
    to_sprint_id = action.get('toSprintId')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
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


def _apply_remove_dependency(action):
    """Remove a dependency from task"""
    task_id = action.get('taskId')
    remove_dependency = action.get('removeDependency')
    
    task = Task.query.get(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    if task.dependencies and remove_dependency in task.dependencies:
        task.dependencies.remove(remove_dependency)
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

