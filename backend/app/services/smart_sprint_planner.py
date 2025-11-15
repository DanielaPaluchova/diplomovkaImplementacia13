"""
Smart Sprint Planning Service
Intelligent sprint planning with multiple algorithms/strategies
"""
from app.models.sprint import Sprint
from app.models.task import Task
from app.models.team_member import TeamMember
from app.services.team_scoring import TeamScoringService
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid


class SmartSprintPlannerService:
    """Service for intelligent sprint planning with multiple strategies"""
    
    def __init__(self):
        self.team_scoring = TeamScoringService()
    
    def plan_sprint(
        self,
        strategy: str,
        project_id: int,
        tasks: List[Task],
        team_members: List[TeamMember],
        sprint_config: Dict,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Plan a sprint using the specified strategy
        
        Args:
            strategy: Algorithm name (priority, workload-balanced, skill-match, etc.)
            project_id: Project ID
            tasks: Available tasks (unassigned or in backlog)
            team_members: Team members available for the sprint
            sprint_config: Sprint configuration (duration, capacity, etc.)
            parameters: Additional parameters for the algorithm
            
        Returns:
            Dict with selected tasks, assignments, metrics, and reasoning
        """
        if not team_members:
            return {
                'error': 'No team members available',
                'suggestedTasks': [],
                'assignments': {},
                'metrics': {},
                'reasoning': {}
            }
        
        # Calculate team capacity
        team_capacity = sum(member.max_story_points for member in team_members)
        target_capacity = sprint_config.get('targetCapacity', team_capacity * 0.85)  # 85% utilization target
        
        # Get cross-project workload information
        cross_project_workload = sprint_config.get('crossProjectWorkload', {})
        cross_project_priorities = sprint_config.get('crossProjectPriorities', {})
        consider_cross_project = sprint_config.get('considerCrossProject', False)
        
        # Filter eligible tasks (not completed, not already in an active sprint)
        eligible_tasks = [
            task for task in tasks
            if task.status != 'Done' and not self._is_in_active_sprint(task, sprint_config)
        ]
        
        # Call appropriate strategy
        strategy_map = {
            'priority': self._plan_priority_based,
            'workload-balanced': self._plan_workload_balanced,
            'skill-match': self._plan_skill_match,
            'skill-priority': self._plan_skill_priority,
            'skill-balanced': self._plan_skill_balanced,
            'skill-value': self._plan_skill_value,
            'value-driven': self._plan_value_driven,
            'balanced-priority': self._plan_balanced_priority,
            'hybrid': self._plan_hybrid
        }
        
        planner_func = strategy_map.get(strategy)
        if not planner_func:
            return {
                'error': f'Unknown strategy: {strategy}',
                'suggestedTasks': [],
                'assignments': {},
                'metrics': {},
                'reasoning': {}
            }
        
        # Prepare context for planning
        planning_context = {
            'cross_project_workload': cross_project_workload,
            'cross_project_priorities': cross_project_priorities,
            'consider_cross_project': consider_cross_project,
            'parameters': parameters or {}
        }
        
        # Execute planning strategy
        result = planner_func(
            eligible_tasks,
            team_members,
            target_capacity,
            planning_context
        )
        
        # Add summary metrics
        result['sprintSummary'] = self._calculate_sprint_summary(
            result['suggestedTasks'],
            result['assignments'],
            team_members,
            team_capacity
        )
        
        # Add team member analysis (especially important when considering cross-project workload)
        result['teamAnalysis'] = self._build_team_analysis(
            team_members,
            result.get('assignments', {}),
            planning_context
        )
        
        result['strategy'] = strategy
        result['projectId'] = project_id
        
        return result
    
    def _is_in_active_sprint(self, task: Task, sprint_config: Dict) -> bool:
        """Check if task is already in an active sprint"""
        # If sprint_config has activeSprintId and task is in that sprint, exclude it
        if sprint_config.get('activeSprintId') and task.sprint_id == sprint_config['activeSprintId']:
            return True
        return False
    
    def _build_capacity_rejection_reason(
        self,
        task_sp: int,
        team_members: List[TeamMember],
        member_workloads: Dict[int, float],
        cross_project_workload: Dict[int, float],
        consider_cross_project: bool
    ) -> Dict:
        """Build detailed reason why task cannot be assigned due to capacity"""
        capacity_details = []
        
        for member in sorted(team_members, key=lambda m: member_workloads[m.id]):
            current_load = member_workloads[member.id]
            cross_proj = cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            available = member.max_story_points - current_load
            
            if consider_cross_project and cross_proj > 0:
                capacity_details.append(
                    f"{member.name}: {current_load:.0f}/{member.max_story_points} SP "
                    f"({cross_proj:.0f} SP in other projects, needs {task_sp} SP more)"
                )
            else:
                capacity_details.append(
                    f"{member.name}: {current_load:.0f}/{member.max_story_points} SP "
                    f"(needs {task_sp} SP more)"
                )
        
        reason_text = "Cannot assign - all team members at/over capacity. "
        if consider_cross_project:
            reason_text += "Team workload across all projects: "
        else:
            reason_text += "Team workload: "
        reason_text += "; ".join(capacity_details[:3])  # Show top 3
        
        return {
            'selected': False,
            'reason': reason_text,
            'teamCapacityDetails': capacity_details
        }
    
    def _plan_priority_based(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Priority-based planning: Select highest priority tasks first
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        cross_project_priorities = context.get('cross_project_priorities', {})
        consider_cross_project = context.get('consider_cross_project', False)
        
        # Priority mapping
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        
        # Sort tasks by priority (high to low)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                priority_map.get((t.priority or 'medium').lower(), 2),
                -(t.story_points or 0)  # Within same priority, prefer higher SP
            ),
            reverse=True
        )
        
        selected_tasks = []
        assignments = {}
        reasoning = {}
        # Initialize with cross-project workload if considering it
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        
        for task in sorted_tasks:
            task_sp = task.story_points or 0
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check if adding this task exceeds capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'Would exceed sprint capacity ({total_sp + task_sp:.0f} > {target_capacity:.0f} SP)'
                }
                continue
            
            # Find team member with lowest current workload
            best_member = min(team_members, key=lambda m: member_workloads[m.id])
            
            # Check if ANY member has capacity
            members_with_capacity = [
                m for m in team_members
                if member_workloads[m.id] + task_sp <= m.max_story_points
            ]
            
            if members_with_capacity:
                # Use the best member (lowest workload)
                best_member = min(members_with_capacity, key=lambda m: member_workloads[m.id])
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id,
                    'taskName': task.name,
                    'memberId': best_member.id,
                    'memberName': best_member.name,
                    'role': 'responsible',
                    'storyPoints': task_sp
                }
                
                # Build reasoning
                reason_parts = [f'Priority: {task.priority}']
                
                cross_proj_sp = cross_project_workload.get(best_member.id, 0) if consider_cross_project else 0
                current_sprint_sp = member_workloads[best_member.id] - cross_proj_sp
                
                if consider_cross_project and cross_proj_sp > 0:
                    cross_proj_high = cross_project_priorities.get(best_member.id, 0)
                    reason_parts.append(f'{best_member.name} has {cross_proj_sp} SP in other projects')
                    if cross_proj_high > 0 and task.priority and task.priority.lower() == 'high':
                        reason_parts.append(f'Note: {best_member.name} already has {cross_proj_high} high-priority tasks elsewhere')
                else:
                    reason_parts.append(f'Assigned to {best_member.name} (lowest workload in team)')
                
                member_workloads[best_member.id] += task_sp
                total_sp += task_sp
                
                reasoning[task.id] = {
                    'selected': True,
                    'reason': '. '.join(reason_parts),
                    'priority': task.priority,
                    'assignedTo': best_member.name,
                    'crossProjectSP': cross_proj_sp if consider_cross_project else 0,
                    'crossProjectHighPriority': cross_project_priorities.get(best_member.id, 0) if consider_cross_project else 0
                }
            else:
                # Use helper to build detailed capacity rejection reason
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_workload_balanced(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Workload-balanced planning: Distribute story points evenly across team
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        cross_project_priorities = context.get('cross_project_priorities', {})
        consider_cross_project = context.get('consider_cross_project', False)
        
        # Sort tasks by story points (larger first for better packing)
        sorted_tasks = sorted(tasks, key=lambda t: -(t.story_points or 0))
        
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        
        for task in sorted_tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0:
                continue
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'Would exceed sprint capacity'
                }
                continue
            
            # Find member with lowest workload who can handle this task
            eligible_members = [
                m for m in team_members
                if member_workloads[m.id] + task_sp <= m.max_story_points
            ]
            
            if not eligible_members:
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
                continue
            
            # Assign to member with lowest current workload
            best_member = min(eligible_members, key=lambda m: member_workloads[m.id])
            
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': best_member.id,
                'memberName': best_member.name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            member_workloads[best_member.id] += task_sp
            total_sp += task_sp
            
            reasoning[task.id] = {
                'selected': True,
                'reason': f'Assigned to {best_member.name} for workload balance ({member_workloads[best_member.id]} SP total)',
                'assignedTo': best_member.name,
                'balanceScore': self._calculate_balance_score(
                    member_workloads, team_members,
                    cross_project_workload if consider_cross_project else None
                )
            }
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_skill_match(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Skill-match planning: Assign tasks based on team member skills
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        
        total_sp = 0
        
        # Score each task-member combination
        task_scores = []
        
        for task in tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0 or total_sp + task_sp > target_capacity:
                continue
            
            # Get task requirements
            task_requirements = {
                'labels': task.labels or [],
                'type': task.type,
                'priority': task.priority,
                'required_skills': task.required_skills if hasattr(task, 'required_skills') else []
            }
            
            # Score all members for this task
            member_scores = self.team_scoring.rank_members_for_task(
                team_members,
                task_requirements,
                [],  # No task history needed for sprint planning
                member_workloads
            )
            
            if member_scores:
                best_score = member_scores[0]
                task_scores.append({
                    'task': task,
                    'member_id': best_score['member_id'],
                    'member_name': best_score['member_name'],
                    'score': best_score['final_score'],
                    'breakdown': best_score['breakdown']
                })
        
        # Sort by score (highest first) and select tasks
        task_scores.sort(key=lambda x: -x['score'])
        selected_task_ids = set()
        
        for item in task_scores:
            task = item['task']
            task_sp = task.story_points or 0
            member_id = item['member_id']
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check if this member still has capacity
            member = next((m for m in team_members if m.id == member_id), None)
            if not member:
                continue
            
            if member_workloads[member_id] + task_sp <= member.max_story_points:
                if total_sp + task_sp <= target_capacity:
                    selected_tasks.append(task)
                    selected_task_ids.add(task.id)
                    assignments[task.id] = {
                        'taskId': task.id,
                        'taskName': task.name,
                        'memberId': member_id,
                        'memberName': item['member_name'],
                        'role': 'responsible',
                        'storyPoints': task_sp
                    }
                    member_workloads[member_id] += task_sp
                    total_sp += task_sp
                    
                    reasoning[task.id] = {
                        'selected': True,
                        'reason': f'Best skill match with {item["member_name"]} (score: {item["score"]:.1f})',
                        'assignedTo': item['member_name'],
                        'skillScore': item['breakdown']['skills'],
                        'matchScore': item['score']
                    }
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_skill_priority(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Skill-Priority planning: Combine skill matching with priority
        Best skill match for high-priority tasks
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        parameters = context.get('parameters', {})
        
        # Get weights from parameters or use defaults
        weights = parameters.get('weights', {
            'skills': 0.6,
            'priority': 0.4
        })
        
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        
        # Calculate composite score for each task
        task_scores = []
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        
        for task in tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0:
                continue
            
            # Priority score (0-100)
            priority_score = priority_map.get((task.priority or 'medium').lower(), 2) * 33.33
            
            # Get task requirements
            task_requirements = {
                'labels': task.labels or [],
                'type': task.type,
                'priority': task.priority,
                'required_skills': task.required_skills if hasattr(task, 'required_skills') else []
            }
            
            # Score all members for this task
            member_scores = self.team_scoring.rank_members_for_task(
                team_members,
                task_requirements,
                [],
                member_workloads
            )
            
            if not member_scores:
                continue
            
            best_score = member_scores[0]
            skills_score = best_score['breakdown']['skills']
            
            # Calculate weighted composite score
            composite_score = (
                weights.get('skills', 0.6) * skills_score +
                weights.get('priority', 0.4) * priority_score
            )
            
            task_scores.append({
                'task': task,
                'score': composite_score,
                'member_id': best_score['member_id'],
                'member_name': best_score['member_name'],
                'breakdown': {
                    'skills': skills_score,
                    'priority': priority_score
                }
            })
        
        # Sort by composite score (highest first)
        task_scores.sort(key=lambda x: -x['score'])
        
        # Select tasks up to capacity
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        
        for item in task_scores:
            task = item['task']
            task_sp = task.story_points or 0
            member_id = item['member_id']
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': 'Would exceed sprint capacity'
                }
                continue
            
            # Check if this member still has capacity
            member = next((m for m in team_members if m.id == member_id), None)
            if not member:
                continue
            
            if member_workloads[member_id] + task_sp <= member.max_story_points:
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id,
                    'taskName': task.name,
                    'memberId': member_id,
                    'memberName': item['member_name'],
                    'role': 'responsible',
                    'storyPoints': task_sp
                }
                member_workloads[member_id] += task_sp
                total_sp += task_sp
                
                reasoning[task.id] = {
                    'selected': True,
                    'reason': f'Priority: {task.priority}, best skill match with {item["member_name"]} (score: {item["score"]:.1f})',
                    'assignedTo': item['member_name'],
                    'compositeScore': item['score'],
                    'scoreBreakdown': item['breakdown']
                }
            else:
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        metrics['weights'] = weights
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_skill_balanced(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Skill-Balanced planning: Combine skill matching with workload balance
        Good skill match while keeping fair distribution
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        parameters = context.get('parameters', {})
        
        # Get weights from parameters or use defaults
        weights = parameters.get('weights', {
            'skills': 0.5,
            'workload': 0.5
        })
        
        # Calculate composite score for each task
        task_scores = []
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        
        for task in tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0:
                continue
            
            # Get task requirements
            task_requirements = {
                'labels': task.labels or [],
                'type': task.type,
                'priority': task.priority,
                'required_skills': task.required_skills if hasattr(task, 'required_skills') else []
            }
            
            # Score all members for this task
            member_scores = self.team_scoring.rank_members_for_task(
                team_members,
                task_requirements,
                [],
                member_workloads
            )
            
            if not member_scores:
                continue
            
            best_score = member_scores[0]
            skills_score = best_score['breakdown']['skills']
            workload_score = best_score['breakdown']['workload']
            
            # Calculate weighted composite score
            composite_score = (
                weights.get('skills', 0.5) * skills_score +
                weights.get('workload', 0.5) * workload_score
            )
            
            task_scores.append({
                'task': task,
                'score': composite_score,
                'member_id': best_score['member_id'],
                'member_name': best_score['member_name'],
                'breakdown': {
                    'skills': skills_score,
                    'workload': workload_score
                }
            })
        
        # Sort by composite score (highest first)
        task_scores.sort(key=lambda x: -x['score'])
        
        # Select tasks up to capacity
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        
        for item in task_scores:
            task = item['task']
            task_sp = task.story_points or 0
            member_id = item['member_id']
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': 'Would exceed sprint capacity'
                }
                continue
            
            # Check if this member still has capacity
            member = next((m for m in team_members if m.id == member_id), None)
            if not member:
                continue
            
            if member_workloads[member_id] + task_sp <= member.max_story_points:
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id,
                    'taskName': task.name,
                    'memberId': member_id,
                    'memberName': item['member_name'],
                    'role': 'responsible',
                    'storyPoints': task_sp
                }
                member_workloads[member_id] += task_sp
                total_sp += task_sp
                
                reasoning[task.id] = {
                    'selected': True,
                    'reason': f'Skill match with {item["member_name"]}, balanced workload (score: {item["score"]:.1f})',
                    'assignedTo': item['member_name'],
                    'compositeScore': item['score'],
                    'scoreBreakdown': item['breakdown']
                }
            else:
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        metrics['weights'] = weights
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_skill_value(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Skill-Value planning: Combine skill matching with business value
        Best skill match for high-value tasks
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        parameters = context.get('parameters', {})
        
        # Get weights from parameters or use defaults
        weights = parameters.get('weights', {
            'skills': 0.5,
            'value': 0.5
        })
        
        priority_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        
        # Calculate composite score for each task
        task_scores = []
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        
        for task in tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0:
                continue
            
            # Value score (0-100)
            priority_weight = priority_weights.get((task.priority or 'medium').lower(), 2.0)
            value_score = min(100, (task_sp * priority_weight * 3.33))
            
            # Get task requirements
            task_requirements = {
                'labels': task.labels or [],
                'type': task.type,
                'priority': task.priority,
                'required_skills': task.required_skills if hasattr(task, 'required_skills') else []
            }
            
            # Score all members for this task
            member_scores = self.team_scoring.rank_members_for_task(
                team_members,
                task_requirements,
                [],
                member_workloads
            )
            
            if not member_scores:
                continue
            
            best_score = member_scores[0]
            skills_score = best_score['breakdown']['skills']
            
            # Calculate weighted composite score
            composite_score = (
                weights.get('skills', 0.5) * skills_score +
                weights.get('value', 0.5) * value_score
            )
            
            task_scores.append({
                'task': task,
                'score': composite_score,
                'member_id': best_score['member_id'],
                'member_name': best_score['member_name'],
                'value': task_sp * priority_weight,
                'breakdown': {
                    'skills': skills_score,
                    'value': value_score
                }
            })
        
        # Sort by composite score (highest first)
        task_scores.sort(key=lambda x: -x['score'])
        
        # Select tasks up to capacity
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        total_value = 0
        
        for item in task_scores:
            task = item['task']
            task_sp = task.story_points or 0
            member_id = item['member_id']
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': 'Would exceed sprint capacity'
                }
                continue
            
            # Check if this member still has capacity
            member = next((m for m in team_members if m.id == member_id), None)
            if not member:
                continue
            
            if member_workloads[member_id] + task_sp <= member.max_story_points:
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id,
                    'taskName': task.name,
                    'memberId': member_id,
                    'memberName': item['member_name'],
                    'role': 'responsible',
                    'storyPoints': task_sp
                }
                member_workloads[member_id] += task_sp
                total_sp += task_sp
                total_value += item['value']
                
                reasoning[task.id] = {
                    'selected': True,
                    'reason': f'High-value task ({item["value"]:.1f}), best skill match with {item["member_name"]} (score: {item["score"]:.1f})',
                    'assignedTo': item['member_name'],
                    'compositeScore': item['score'],
                    'scoreBreakdown': item['breakdown'],
                    'value': item['value']
                }
            else:
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        metrics['weights'] = weights
        metrics['totalValue'] = total_value
        metrics['averageValue'] = total_value / len(selected_tasks) if selected_tasks else 0
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _check_dependencies_satisfied(
        self,
        task: Task,
        all_tasks: List[Task],
        selected_task_ids: set
    ) -> Tuple[bool, str]:
        """
        Check if task dependencies are satisfied
        Returns: (is_satisfied, reason_if_not)
        """
        if not task.dependencies:
            return True, ""
        
        # Build task map for lookup
        task_map = {t.id: t for t in all_tasks}
        
        unsatisfied_deps = []
        for dep_id in task.dependencies:
            dep_task = task_map.get(dep_id)
            if not dep_task:
                continue
            
            # Dependency is satisfied if:
            # 1. The dependent task is Done, OR
            # 2. The dependent task is already selected for this sprint
            if dep_task.status != 'Done' and dep_id not in selected_task_ids:
                unsatisfied_deps.append(dep_id)
        
        if unsatisfied_deps:
            return False, f'Cannot add - has {len(unsatisfied_deps)} unsatisfied dependencies (tasks must be completed or included in sprint first)'
        
        return True, ""
    
    def _plan_value_driven(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Value-driven planning: Maximize business value (story points × priority weight)
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        
        priority_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        
        # Calculate value score for each task
        def calculate_value(task: Task) -> float:
            sp = task.story_points or 0
            priority_weight = priority_weights.get((task.priority or 'medium').lower(), 2.0)
            return sp * priority_weight
        
        # Sort by value (highest first)
        sorted_tasks = sorted(tasks, key=calculate_value, reverse=True)
        
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        total_value = 0
        
        for task in sorted_tasks:
            task_sp = task.story_points or 0
            task_value = calculate_value(task)
            
            if task_sp == 0:
                continue
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': 'Would exceed sprint capacity'
                }
                continue
            
            # Assign to best available member
            eligible_members = [
                m for m in team_members
                if member_workloads[m.id] + task_sp <= m.max_story_points
            ]
            
            if not eligible_members:
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
                continue
            
            best_member = min(eligible_members, key=lambda m: member_workloads[m.id])
            
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': best_member.id,
                'memberName': best_member.name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            member_workloads[best_member.id] += task_sp
            total_sp += task_sp
            total_value += task_value
            
            reasoning[task.id] = {
                'selected': True,
                'reason': f'High value task (value: {task_value:.1f}) assigned to {best_member.name}',
                'assignedTo': best_member.name,
                'valueScore': task_value,
                'priority': task.priority,
                'storyPoints': task_sp
            }
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        metrics['totalValue'] = total_value
        metrics['averageValue'] = total_value / len(selected_tasks) if selected_tasks else 0
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_balanced_priority(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Balanced Priority planning: Balance high-priority tasks with fair workload distribution
        Combines priority-based and workload-balanced strategies
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        parameters = context.get('parameters', {})
        
        # Get weights from parameters or use defaults
        weights = parameters.get('weights', {
            'priority': 0.6,
            'workload': 0.4
        })
        
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        
        # Calculate composite score for each task
        task_scores = []
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        
        for task in tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0:
                continue
            
            # Priority score (0-100)
            priority_score = priority_map.get((task.priority or 'medium').lower(), 2) * 33.33
            
            # Find best member for workload balance
            best_member = min(team_members, key=lambda m: member_workloads[m.id])
            
            # Calculate workload balance score based on how balanced this assignment would be
            temp_workloads = {m.id: member_workloads[m.id] for m in team_members}
            temp_workloads[best_member.id] += task_sp
            workload_score = self._calculate_balance_score(temp_workloads, team_members)
            
            # Calculate weighted composite score
            composite_score = (
                weights.get('priority', 0.6) * priority_score +
                weights.get('workload', 0.4) * workload_score
            )
            
            task_scores.append({
                'task': task,
                'score': composite_score,
                'member_id': best_member.id,
                'member_name': best_member.name,
                'breakdown': {
                    'priority': priority_score,
                    'workload': workload_score
                }
            })
        
        # Sort by composite score (highest first)
        task_scores.sort(key=lambda x: -x['score'])
        
        # Select tasks up to capacity
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        
        for item in task_scores:
            task = item['task']
            task_sp = task.story_points or 0
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': 'Would exceed sprint capacity'
                }
                continue
            
            # Find member with lowest workload who can handle this task
            eligible_members = [
                m for m in team_members
                if member_workloads[m.id] + task_sp <= m.max_story_points
            ]
            
            if not eligible_members:
                reasoning[task.id] = self._build_capacity_rejection_reason(
                    task_sp, team_members, member_workloads,
                    cross_project_workload, consider_cross_project
                )
                continue
            
            best_member = min(eligible_members, key=lambda m: member_workloads[m.id])
            
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': best_member.id,
                'memberName': best_member.name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            member_workloads[best_member.id] += task_sp
            total_sp += task_sp
            
            reasoning[task.id] = {
                'selected': True,
                'reason': f'Priority: {task.priority}, balanced assignment to {best_member.name} (score: {item["score"]:.1f})',
                'assignedTo': best_member.name,
                'compositeScore': item['score'],
                'scoreBreakdown': item['breakdown']
            }
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        metrics['weights'] = weights
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_hybrid(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Hybrid planning: Combine all factors with configurable weights
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        parameters = context.get('parameters', {})
        
        # Get weights from parameters or use defaults
        weights = parameters.get('weights', {
            'priority': 0.25,
            'workload': 0.20,
            'skills': 0.25,
            'dependency': 0.15,
            'velocity': 0.15
        })
        
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        risk_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        
        # Calculate composite score for each task
        task_scores = []
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        
        for task in tasks:
            task_sp = task.story_points or 0
            
            if task_sp == 0:
                continue
            
            # Priority score (0-100)
            priority_score = priority_map.get((task.priority or 'medium').lower(), 2) * 33.33
            
            # Dependency score (0-100)
            dependency_score = 100
            if task.dependencies:
                # Penalize tasks with many dependencies
                dependency_score = max(0, 100 - (len(task.dependencies) * 20))
            
            # Risk score (0-100, inverse - lower risk = higher score)
            risk_level = getattr(task, 'risk_level', 'medium').lower()
            risk_score = 100 - (risk_map.get(risk_level, 2) * 25)
            
            # Get best member match for this task
            task_requirements = {
                'labels': task.labels or [],
                'type': task.type,
                'priority': task.priority
            }
            
            member_scores = self.team_scoring.rank_members_for_task(
                team_members,
                task_requirements,
                [],
                member_workloads
            )
            
            if not member_scores:
                continue
            
            best_member_score = member_scores[0]
            skills_score = best_member_score['breakdown']['skills']
            workload_score = best_member_score['breakdown']['workload']
            
            # Velocity score
            best_member = next((m for m in team_members if m.id == best_member_score['member_id']), None)
            if best_member:
                velocity = best_member.historical_velocity or best_member.max_story_points * 0.8
                velocity_score = min(100, (velocity / best_member.max_story_points) * 100)
            else:
                velocity_score = 50
            
            # Calculate weighted composite score
            composite_score = (
                weights.get('priority', 0.25) * priority_score +
                weights.get('workload', 0.20) * workload_score +
                weights.get('skills', 0.25) * skills_score +
                weights.get('dependency', 0.15) * dependency_score +
                weights.get('velocity', 0.15) * velocity_score
            )
            
            task_scores.append({
                'task': task,
                'score': composite_score,
                'member_id': best_member_score['member_id'],
                'member_name': best_member_score['member_name'],
                'breakdown': {
                    'priority': priority_score,
                    'workload': workload_score,
                    'skills': skills_score,
                    'dependency': dependency_score,
                    'velocity': velocity_score,
                    'risk': risk_score
                }
            })
        
        # Sort by composite score (highest first)
        task_scores.sort(key=lambda x: -x['score'])
        
        # Select tasks up to capacity
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        
        total_sp = 0
        
        for item in task_scores:
            task = item['task']
            task_sp = task.story_points or 0
            member_id = item['member_id']
            
            # Check dependencies first
            deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
            if not deps_satisfied:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': deps_reason
                }
                continue
            
            # Check capacity
            if total_sp + task_sp > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': 'Would exceed sprint capacity'
                }
                continue
            
            # Check member capacity
            member = next((m for m in team_members if m.id == member_id), None)
            if not member or member_workloads[member_id] + task_sp > member.max_story_points:
                # Try to find alternative member
                eligible_members = [
                    m for m in team_members
                    if member_workloads[m.id] + task_sp <= m.max_story_points
                ]
                
                if not eligible_members:
                    reasoning[task.id] = self._build_capacity_rejection_reason(
                        task_sp, team_members, member_workloads,
                        cross_project_workload, consider_cross_project
                    )
                    continue
                
                member = min(eligible_members, key=lambda m: member_workloads[m.id])
                member_id = member.id
            
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': member_id,
                'memberName': member.name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            member_workloads[member_id] += task_sp
            total_sp += task_sp
            
            reasoning[task.id] = {
                'selected': True,
                'reason': f'Hybrid score: {item["score"]:.1f} - assigned to {member.name}',
                'assignedTo': member.name,
                'compositeScore': item['score'],
                'scoreBreakdown': item['breakdown']
            }
        
        metrics = self._calculate_metrics(
            selected_tasks, member_workloads, team_members,
            cross_project_workload, consider_cross_project
        )
        metrics['weights'] = weights
        
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _calculate_metrics(
        self,
        selected_tasks: List[Task],
        member_workloads: Dict[int, float],
        team_members: List[TeamMember],
        cross_project_workload: Dict[int, float] = None,
        consider_cross_project: bool = False
    ) -> Dict:
        """Calculate metrics for the selected tasks and assignments"""
        total_sp = sum(task.story_points or 0 for task in selected_tasks)
        team_capacity = sum(member.max_story_points for member in team_members)
        
        # If considering cross-project, calculate utilization based on total workload
        if consider_cross_project and cross_project_workload:
            # Total workload = current sprint SP + cross-project SP
            total_current_sprint_sp = sum(member_workloads.get(m.id, 0) for m in team_members)
            utilization = (total_current_sprint_sp / team_capacity * 100) if team_capacity > 0 else 0
        else:
            # Standard utilization calculation
            utilization = (total_sp / team_capacity * 100) if team_capacity > 0 else 0
        
        # Balance score should consider total workload if cross-project is enabled
        balance_score = self._calculate_balance_score(
            member_workloads,
            team_members,
            cross_project_workload if consider_cross_project else None
        )
        
        # Risk score
        risk_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        avg_risk = 0
        if selected_tasks:
            risk_sum = sum(
                risk_scores.get(getattr(task, 'risk_level', 'medium').lower(), 2)
                for task in selected_tasks
            )
            avg_risk = (risk_sum / len(selected_tasks)) * 25  # Scale to 0-100
        
        # Priority distribution
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for task in selected_tasks:
            priority = (task.priority or 'medium').lower()
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'totalStoryPoints': total_sp,
            'teamCapacity': team_capacity,
            'utilization': round(utilization, 1),
            'balanceScore': round(balance_score, 1),
            'riskScore': round(avg_risk, 1),
            'taskCount': len(selected_tasks),
            'priorityDistribution': priority_counts
        }
    
    def _calculate_balance_score(
        self,
        member_workloads: Dict[int, float],
        team_members: List[TeamMember],
        cross_project_workload: Dict[int, float] = None
    ) -> float:
        """
        Calculate workload balance score (0-100)
        Higher = more balanced
        """
        if not member_workloads or len(team_members) < 2:
            return 100.0
        
        # Calculate workload percentages
        workload_percentages = []
        for member in team_members:
            # If considering cross-project, add it to the workload
            current_workload = member_workloads.get(member.id, 0)
            if cross_project_workload:
                current_workload += cross_project_workload.get(member.id, 0)
            
            percentage = (current_workload / member.max_story_points * 100) if member.max_story_points > 0 else 0
            workload_percentages.append(percentage)
        
        if not workload_percentages:
            return 100.0
        
        # Calculate variance
        avg = sum(workload_percentages) / len(workload_percentages)
        variance = sum((x - avg) ** 2 for x in workload_percentages) / len(workload_percentages)
        std_dev = variance ** 0.5
        
        # Convert to score (lower std_dev = higher score)
        # Perfect balance (std_dev = 0) = 100, high imbalance (std_dev = 50) = 0
        balance_score = max(0, 100 - (std_dev * 2))
        
        return balance_score
    
    def _build_team_analysis(
        self,
        team_members: List[TeamMember],
        assignments: Dict,
        planning_context: Dict
    ) -> Dict:
        """Build detailed analysis of team capacity and workload"""
        cross_project_workload = planning_context.get('cross_project_workload', {})
        cross_project_priorities = planning_context.get('cross_project_priorities', {})
        consider_cross_project = planning_context.get('consider_cross_project', False)
        
        team_analysis = []
        
        # Calculate SP assigned in this sprint for each member
        member_sprint_sp = {}
        for assignment in assignments.values():
            member_id = assignment['memberId']
            sp = assignment['storyPoints']
            member_sprint_sp[member_id] = member_sprint_sp.get(member_id, 0) + sp
        
        for member in team_members:
            cross_proj_sp = cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            sprint_sp = member_sprint_sp.get(member.id, 0)
            total_sp = cross_proj_sp + sprint_sp
            available_sp = member.max_story_points - total_sp
            
            status = 'available'
            if total_sp >= member.max_story_points:
                status = 'at_capacity'
            elif total_sp > member.max_story_points * 0.9:
                status = 'nearly_full'
            elif sprint_sp > 0:
                status = 'assigned'
            
            analysis = {
                'memberId': member.id,
                'memberName': member.name,
                'maxCapacity': member.max_story_points,
                'assignedInThisSprint': sprint_sp,
                'crossProjectWorkload': cross_proj_sp,
                'totalWorkload': total_sp,
                'availableCapacity': max(0, available_sp),
                'utilizationPercentage': (total_sp / member.max_story_points * 100) if member.max_story_points > 0 else 0,
                'status': status,
                'taskCount': len([a for a in assignments.values() if a['memberId'] == member.id])
            }
            
            # Add reasoning for members who didn't get tasks
            if sprint_sp == 0:
                if consider_cross_project and cross_proj_sp > 0:
                    high_priority = cross_project_priorities.get(member.id, 0)
                    if high_priority > 0:
                        analysis['reason'] = f'Not assigned - has {cross_proj_sp:.0f} SP in other projects ({high_priority} high-priority tasks)'
                    else:
                        analysis['reason'] = f'Not assigned - has {cross_proj_sp:.0f} SP in other projects'
                elif total_sp >= member.max_story_points:
                    analysis['reason'] = 'Not assigned - at maximum capacity'
                else:
                    analysis['reason'] = 'Not assigned - tasks matched better with other team members'
            else:
                if consider_cross_project and cross_proj_sp > 0:
                    analysis['reason'] = f'Assigned {sprint_sp:.0f} SP (considering {cross_proj_sp:.0f} SP from other projects)'
                else:
                    analysis['reason'] = f'Assigned {sprint_sp:.0f} SP'
            
            team_analysis.append(analysis)
        
        # Sort by total workload (most loaded first)
        team_analysis.sort(key=lambda x: -x['totalWorkload'])
        
        return {
            'members': team_analysis,
            'considerCrossProject': consider_cross_project,
            'summary': {
                'totalMembers': len(team_members),
                'assignedMembers': len([m for m in team_analysis if m['assignedInThisSprint'] > 0]),
                'atCapacity': len([m for m in team_analysis if m['status'] == 'at_capacity']),
                'available': len([m for m in team_analysis if m['status'] == 'available'])
            }
        }
    
    def _calculate_sprint_summary(
        self,
        selected_tasks: List[Dict],
        assignments: Dict,
        team_members: List[TeamMember],
        team_capacity: float
    ) -> Dict:
        """Calculate summary statistics for the sprint plan"""
        total_sp = sum(task['storyPoints'] for task in selected_tasks)
        
        # Member workload breakdown
        member_breakdown = {}
        for assignment in assignments.values():
            member_id = assignment['memberId']
            member_name = assignment['memberName']
            sp = assignment['storyPoints']
            
            if member_id not in member_breakdown:
                member = next((m for m in team_members if m.id == member_id), None)
                max_sp = member.max_story_points if member else 20
                member_breakdown[member_id] = {
                    'memberId': member_id,
                    'memberName': member_name,
                    'assignedSP': 0,
                    'maxCapacity': max_sp,
                    'utilization': 0,
                    'taskCount': 0
                }
            
            member_breakdown[member_id]['assignedSP'] += sp
            member_breakdown[member_id]['taskCount'] += 1
        
        # Calculate utilization for each member
        for member_data in member_breakdown.values():
            member_data['utilization'] = (
                member_data['assignedSP'] / member_data['maxCapacity'] * 100
            ) if member_data['maxCapacity'] > 0 else 0
        
        return {
            'totalStoryPoints': total_sp,
            'teamCapacity': team_capacity,
            'utilizationPercentage': (total_sp / team_capacity * 100) if team_capacity > 0 else 0,
            'taskCount': len(selected_tasks),
            'memberBreakdown': list(member_breakdown.values())
        }
    
    def _task_to_dict(self, task: Task) -> Dict:
        """Convert Task object to dictionary"""
        return {
            'id': task.id,
            'name': task.name,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'type': task.type,
            'storyPoints': task.story_points or 0,
            'labels': task.labels or [],
            'complexity': task.complexity or 0,
            'dependencies': task.dependencies or [],
            'riskLevel': getattr(task, 'risk_level', 'medium')
        }

