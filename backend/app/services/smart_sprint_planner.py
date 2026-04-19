"""
Smart Sprint Planning Service
Intelligent sprint planning with multiple algorithms/strategies
"""
from app.models.sprint import Sprint
from app.models.task import Task
from app.models.team_member import TeamMember
from app.services.pert_raci_analyzer import PertRaciAnalyzerService
from app.services.team_scoring import TeamScoringService
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid


class SmartSprintPlannerService:
    """Service for intelligent sprint planning with multiple strategies"""
    
    def __init__(self):
        self.team_scoring = TeamScoringService()
        self.pert_raci_analyzer = PertRaciAnalyzerService()
    
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

        # PERT strategies use 60h per member (2-week sprint ~80h, 60h for buffer)
        PERT_HOURS_PER_MEMBER = 60
        pert_strategies = (
            'pert', 'pert-workload', 'pert-raci-integration', 'pert-raci-integration-skills',
            'pert-raci-integration-priority', 'pert-raci-integration-value',
            'pert-skills', 'pert-priority', 'pert-value',
            'pert-workload-skills', 'pert-workload-priority', 'pert-workload-value'
        )
        # Hybrid with pertMode 'pert' or 'pert-raci' also uses PERT capacity
        hybrid_pert_mode = (strategy == 'hybrid' and
            (parameters or {}).get('weights', {}).get('pertMode') in ('pert', 'pert-raci'))
        if strategy in pert_strategies or hybrid_pert_mode:
            target_capacity = PERT_HOURS_PER_MEMBER * len(team_members)
            sprint_config['targetCapacityHours'] = target_capacity
            sprint_config['capacityPerMemberHours'] = PERT_HOURS_PER_MEMBER
            sprint_config['pertMode'] = True
        
        # Get cross-project workload information
        cross_project_workload = sprint_config.get('crossProjectWorkload', {})
        cross_project_priorities = sprint_config.get('crossProjectPriorities', {})
        consider_cross_project = sprint_config.get('considerCrossProject', False)
        
        # Filter eligible tasks (not completed, not already in an active sprint)
        eligible_tasks = [
            task for task in tasks
            if task.status != 'Done' and not self._is_in_active_sprint(task, sprint_config)
        ]

        # PERT strategies: only tasks with pert_expected (incl. hybrid with pertMode)
        if strategy in pert_strategies or hybrid_pert_mode:
            eligible_tasks = [
                task for task in eligible_tasks
                if task.pert_expected is not None and task.pert_expected > 0
            ]
        
        # Call appropriate strategy
        strategy_map = {
            'priority': self._plan_priority_based,
            'workload-balanced': self._plan_workload_balanced,
            'skill-match': self._plan_skill_match,
            'skill-priority': self._plan_skill_priority,
            'skill-value': self._plan_skill_value,
            'value-driven': self._plan_value_driven,
            'hybrid': self._plan_hybrid,
            'pert': self._plan_pert_cv,
            'pert-workload': self._plan_pert_workload,
            'pert-raci-integration': self._plan_pert_raci_integration,
            'pert-raci-integration-skills': self._plan_pert_raci_integration_skills,
            'pert-raci-integration-priority': self._plan_pert_raci_integration_priority,
            'pert-raci-integration-value': self._plan_pert_raci_integration_value,
            'pert-skills': self._plan_pert_cv_skills,
            'pert-priority': self._plan_pert_cv_priority,
            'pert-value': self._plan_pert_cv_value,
            'pert-workload-skills': self._plan_pert_workload_skills,
            'pert-workload-priority': self._plan_pert_workload_priority,
            'pert-workload-value': self._plan_pert_workload_value,
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
            'parameters': parameters or {},
            'pert_mode': strategy in pert_strategies,
            'target_capacity_hours': target_capacity if strategy in pert_strategies else None
        }
        if (strategy and strategy.startswith('pert-raci-integration')) or hybrid_pert_mode:
            planning_context['raci_duration_weights'] = sprint_config.get('raciDurationWeights')
        
        # Execute planning strategy
        result = planner_func(
            eligible_tasks,
            team_members,
            target_capacity,
            planning_context
        )
        
        # Add summary metrics
        summary_capacity = target_capacity if strategy in pert_strategies else team_capacity
        result['sprintSummary'] = self._calculate_sprint_summary(
            result['suggestedTasks'],
            result['assignments'],
            team_members,
            summary_capacity,
            pert_mode=strategy in pert_strategies or hybrid_pert_mode
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
                (t.story_points or 0)  # Within same priority, prefer higher SP
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
        Uses DYNAMIC REORDERING - recalculates scores after each assignment
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
        selected_task_ids = set()
        
        total_sp = 0
        
        # Create pool of remaining tasks (exclude 0 SP tasks)
        remaining_tasks = [t for t in tasks if (t.story_points or 0) > 0]
        
        # DYNAMIC REORDERING: Recalculate scores in each iteration
        while remaining_tasks:
            # Calculate scores for ALL remaining tasks with CURRENT workloads
            current_task_scores = []
            
            for task in remaining_tasks:
                task_sp = task.story_points or 0
                
                # Check if adding this task would exceed sprint capacity
                if total_sp + task_sp > target_capacity:
                    continue
                
                # Check dependencies
                deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
                if not deps_satisfied:
                    # Store reasoning for rejected task
                    if task.id not in reasoning:
                        reasoning[task.id] = {
                            'selected': False,
                            'reason': deps_reason
                        }
                    continue
                
                # Get task requirements
                task_requirements = {
                    'required_skills': task.required_skills or [],
                    'type': task.type,
                    'priority': task.priority
                }
                
                # Score all members for this task with CURRENT workloads
                member_scores = self.team_scoring.rank_members_for_task(
                    team_members,
                    task_requirements,
                    [],  # No task history needed for sprint planning
                    member_workloads  # CURRENT workloads - this changes each iteration!
                )
                
                if not member_scores:
                    continue
                
                # Try to find a member with capacity and acceptable score
                # Minimum score threshold - prevents assigning to completely unsuitable members
                MIN_ACCEPTABLE_SCORE = 40
                
                best_available_member = None
                best_available_score = None
                best_available_rank = None
                
                for idx, member_score in enumerate(member_scores):  # Try ALL members
                    # Skip members with too low skill match score
                    if member_score['final_score'] < MIN_ACCEPTABLE_SCORE:
                        continue
                    
                    candidate_id = member_score['member_id']
                    candidate_member = next((m for m in team_members if m.id == candidate_id), None)
                    
                    if not candidate_member:
                        continue
                    
                    # Check if this member has capacity
                    if member_workloads[candidate_id] + task_sp <= candidate_member.max_story_points:
                        best_available_member = member_score
                        best_available_score = member_score['final_score']
                        best_available_rank = idx + 1
                        break
                
                # If we found someone who can do this task, add it to candidates
                if best_available_member:
                    current_task_scores.append({
                        'task': task,
                        'member_score': best_available_member,
                        'score': best_available_score,
                        'rank': best_available_rank,
                        'all_member_scores': member_scores
                    })
                else:
                    # No member found - either all at capacity or all below minimum score
                    if task.id not in reasoning:
                        # Check if issue is capacity or low scores
                        has_acceptable_scores = any(m['final_score'] >= 40 for m in member_scores)
                        if has_acceptable_scores:
                            reasoning[task.id] = self._build_capacity_rejection_reason(
                                task_sp, team_members, member_workloads,
                                cross_project_workload, consider_cross_project
                            )
                        else:
                            # All members have too low skill match score
                            best_score = member_scores[0]['final_score'] if member_scores else 0
                            reasoning[task.id] = {
                                'selected': False,
                                'reason': f'No suitable team member - best skill match score is {best_score:.1f} (minimum required: 40)'
                            }
            
            # If no tasks can be added, stop
            if not current_task_scores:
                # Store reasoning for remaining tasks
                for task in remaining_tasks:
                    if task.id not in reasoning:
                        task_sp = task.story_points or 0
                        if total_sp + task_sp > target_capacity:
                            reasoning[task.id] = {
                                'selected': False,
                                'reason': f'Would exceed sprint capacity ({total_sp + task_sp:.0f} > {target_capacity:.0f} SP)'
                            }
                        else:
                            reasoning[task.id] = self._build_capacity_rejection_reason(
                                task_sp, team_members, member_workloads,
                                cross_project_workload, consider_cross_project
                            )
                break
            
            # Sort by score (highest first) and pick the BEST one in THIS iteration
            current_task_scores.sort(key=lambda x: -x['score'])
            best_item = current_task_scores[0]
            
            task = best_item['task']
            task_sp = task.story_points or 0
            member_score = best_item['member_score']
            member_id = member_score['member_id']
            member_name = member_score['member_name']
            final_score = best_item['score']
            rank = best_item['rank']
            
            # Assign this task
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': member_id,
                'memberName': member_name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            
            # Update workloads (this affects next iteration's scoring!)
            member_workloads[member_id] += task_sp
            total_sp += task_sp
            
            # Build reasoning based on rank
            if rank == 1:
                reason_text = f'Best skill match with {member_name} (score: {final_score:.1f})'
            elif rank == 2:
                reason_text = f'Assigned to {member_name} (2nd best match, score: {final_score:.1f}) - best match at capacity'
            elif rank == 3:
                reason_text = f'Assigned to {member_name} (3rd best match, score: {final_score:.1f}) - better matches at capacity'
            else:
                reason_text = f'Assigned to {member_name} (#{rank} match, score: {final_score:.1f}) - better matches at capacity'
            
            reasoning[task.id] = {
                'selected': True,
                'reason': reason_text,
                'assignedTo': member_name,
                'skillScore': member_score['breakdown']['skills'],
                'matchScore': final_score,
                'rank': rank
            }
            
            # Remove assigned task from remaining pool
            remaining_tasks.remove(task)
            
            # Loop continues - scores will be RECALCULATED for remaining tasks!
        
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
        Uses DYNAMIC REORDERING - recalculates scores after each assignment
        """
        # Extract context
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        parameters = context.get('parameters', {})
        
        # Get weights from parameters or use defaults
        weights = parameters.get('weights', {
            'skills': 0.4,
            'priority': 0.6
        })
        
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        MIN_ACCEPTABLE_SCORE = 40
        
        selected_tasks = []
        assignments = {}
        reasoning = {}
        member_workloads = {
            member.id: cross_project_workload.get(member.id, 0) if consider_cross_project else 0
            for member in team_members
        }
        selected_task_ids = set()
        total_sp = 0
        
        # Create pool of remaining tasks
        remaining_tasks = [t for t in tasks if (t.story_points or 0) > 0]
        
        # DYNAMIC REORDERING: Recalculate scores in each iteration
        while remaining_tasks:
            current_task_scores = []
            
            for task in remaining_tasks:
                task_sp = task.story_points or 0
                
                if total_sp + task_sp > target_capacity:
                    continue
                
                # Check dependencies
                deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
                if not deps_satisfied:
                    if task.id not in reasoning:
                        reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                    continue
                
                # Priority score (0-100)
                priority_score = priority_map.get((task.priority or 'medium').lower(), 2) * 33.33
                
                # Get task requirements
                task_requirements = {
                    'required_skills': task.required_skills or [],
                    'type': task.type,
                    'priority': task.priority
                }
                
                # Score all members with CURRENT workloads
                member_scores = self.team_scoring.rank_members_for_task(
                    team_members,
                    task_requirements,
                    [],
                    member_workloads
                )
                
                if not member_scores:
                    continue
                
                # Try to find member with capacity and acceptable score
                best_available_member = None
                best_available_rank = None
                best_composite_score = None
                
                for idx, member_score in enumerate(member_scores):
                    skills_score = member_score['breakdown']['skills']
                    composite_score = (
                        weights.get('skills', 0.4) * skills_score +
                        weights.get('priority', 0.6) * priority_score
                    )
                    
                    # Skip if composite score too low
                    if composite_score < MIN_ACCEPTABLE_SCORE:
                        continue
                    
                    candidate_id = member_score['member_id']
                    candidate_member = next((m for m in team_members if m.id == candidate_id), None)
                    
                    if not candidate_member:
                        continue
                    
                    if member_workloads[candidate_id] + task_sp <= candidate_member.max_story_points:
                        best_available_member = member_score
                        best_available_rank = idx + 1
                        best_composite_score = composite_score
                        break
                
                if best_available_member:
                    current_task_scores.append({
                        'task': task,
                        'member_score': best_available_member,
                        'composite_score': best_composite_score,
                        'rank': best_available_rank,
                        'breakdown': {
                            'skills': best_available_member['breakdown']['skills'],
                            'priority': priority_score
                        }
                    })
                else:
                    if task.id not in reasoning:
                        has_acceptable_scores = any(
                            (weights.get('skills', 0.4) * m['breakdown']['skills'] + 
                             weights.get('priority', 0.6) * priority_score) >= MIN_ACCEPTABLE_SCORE
                            for m in member_scores
                        )
                        if has_acceptable_scores:
                            reasoning[task.id] = self._build_capacity_rejection_reason(
                                task_sp, team_members, member_workloads,
                                cross_project_workload, consider_cross_project
                            )
                        else:
                            reasoning[task.id] = {
                                'selected': False,
                                'reason': f'No suitable team member - composite score below minimum (40)'
                            }
            
            if not current_task_scores:
                for task in remaining_tasks:
                    if task.id not in reasoning:
                        task_sp = task.story_points or 0
                        if total_sp + task_sp > target_capacity:
                            reasoning[task.id] = {
                                'selected': False,
                                'reason': f'Would exceed sprint capacity ({total_sp + task_sp:.0f} > {target_capacity:.0f} SP)'
                            }
                        else:
                            reasoning[task.id] = self._build_capacity_rejection_reason(
                                task_sp, team_members, member_workloads,
                                cross_project_workload, consider_cross_project
                            )
                break
            
            # Pick best task in this iteration
            current_task_scores.sort(key=lambda x: -x['composite_score'])
            best_item = current_task_scores[0]
            
            task = best_item['task']
            task_sp = task.story_points or 0
            member_score = best_item['member_score']
            member_id = member_score['member_id']
            member_name = member_score['member_name']
            rank = best_item['rank']
            
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': member_id,
                'memberName': member_name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            
            member_workloads[member_id] += task_sp
            total_sp += task_sp
            
            # Build reasoning
            if rank == 1:
                reason_text = f'Priority: {task.priority}, best match with {member_name} (score: {best_item["composite_score"]:.1f})'
            elif rank == 2:
                reason_text = f'Priority: {task.priority}, assigned to {member_name} (2nd best, score: {best_item["composite_score"]:.1f})'
            else:
                reason_text = f'Priority: {task.priority}, assigned to {member_name} (#{rank} match, score: {best_item["composite_score"]:.1f})'
            
            reasoning[task.id] = {
                'selected': True,
                'reason': reason_text,
                'assignedTo': member_name,
                'compositeScore': best_item['composite_score'],
                'scoreBreakdown': best_item['breakdown'],
                'rank': rank
            }
            
            remaining_tasks.remove(task)
        
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
        Uses DYNAMIC REORDERING - recalculates scores after each assignment
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
        MIN_ACCEPTABLE_SCORE = 40
        
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
        
        # Create pool of remaining tasks
        remaining_tasks = [t for t in tasks if (t.story_points or 0) > 0]
        
        # DYNAMIC REORDERING: Recalculate scores in each iteration
        while remaining_tasks:
            current_task_scores = []
            
            for task in remaining_tasks:
                task_sp = task.story_points or 0
                
                if total_sp + task_sp > target_capacity:
                    continue
                
                # Check dependencies
                deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
                if not deps_satisfied:
                    if task.id not in reasoning:
                        reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                    continue
                
                # Value score (0-100)
                priority_weight = priority_weights.get((task.priority or 'medium').lower(), 2.0)
                value_score = min(100, (task_sp * priority_weight * 3.33))
                task_value = task_sp * priority_weight
                
                # Get task requirements
                task_requirements = {
                    'required_skills': task.required_skills or [],
                    'type': task.type,
                    'priority': task.priority
                }
                
                # Score all members with CURRENT workloads
                member_scores = self.team_scoring.rank_members_for_task(
                    team_members,
                    task_requirements,
                    [],
                    member_workloads
                )
                
                if not member_scores:
                    continue
                
                # Try to find member with capacity and acceptable score
                best_available_member = None
                best_available_rank = None
                best_composite_score = None
                
                for idx, member_score in enumerate(member_scores):
                    skills_score = member_score['breakdown']['skills']
                    composite_score = (
                        weights.get('skills', 0.5) * skills_score +
                        weights.get('value', 0.5) * value_score
                    )
                    
                    # Skip if composite score too low
                    if composite_score < MIN_ACCEPTABLE_SCORE:
                        continue
                    
                    candidate_id = member_score['member_id']
                    candidate_member = next((m for m in team_members if m.id == candidate_id), None)
                    
                    if not candidate_member:
                        continue
                    
                    if member_workloads[candidate_id] + task_sp <= candidate_member.max_story_points:
                        best_available_member = member_score
                        best_available_rank = idx + 1
                        best_composite_score = composite_score
                        break
                
                if best_available_member:
                    current_task_scores.append({
                        'task': task,
                        'member_score': best_available_member,
                        'composite_score': best_composite_score,
                        'rank': best_available_rank,
                        'value': task_value,
                        'breakdown': {
                            'skills': best_available_member['breakdown']['skills'],
                            'value': value_score
                        }
                    })
                else:
                    if task.id not in reasoning:
                        has_acceptable_scores = any(
                            (weights.get('skills', 0.5) * m['breakdown']['skills'] + 
                             weights.get('value', 0.5) * value_score) >= MIN_ACCEPTABLE_SCORE
                            for m in member_scores
                        )
                        if has_acceptable_scores:
                            reasoning[task.id] = self._build_capacity_rejection_reason(
                                task_sp, team_members, member_workloads,
                                cross_project_workload, consider_cross_project
                            )
                        else:
                            reasoning[task.id] = {
                                'selected': False,
                                'reason': f'No suitable team member - composite score below minimum (40)'
                            }
            
            if not current_task_scores:
                for task in remaining_tasks:
                    if task.id not in reasoning:
                        task_sp = task.story_points or 0
                        if total_sp + task_sp > target_capacity:
                            reasoning[task.id] = {
                                'selected': False,
                                'reason': f'Would exceed sprint capacity ({total_sp + task_sp:.0f} > {target_capacity:.0f} SP)'
                            }
                        else:
                            reasoning[task.id] = self._build_capacity_rejection_reason(
                                task_sp, team_members, member_workloads,
                                cross_project_workload, consider_cross_project
                            )
                break
            
            # Pick best task in this iteration
            current_task_scores.sort(key=lambda x: -x['composite_score'])
            best_item = current_task_scores[0]
            
            task = best_item['task']
            task_sp = task.story_points or 0
            member_score = best_item['member_score']
            member_id = member_score['member_id']
            member_name = member_score['member_name']
            rank = best_item['rank']
            
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': member_id,
                'memberName': member_name,
                'role': 'responsible',
                'storyPoints': task_sp
            }
            
            member_workloads[member_id] += task_sp
            total_sp += task_sp
            total_value += best_item['value']
            
            # Build reasoning
            if rank == 1:
                reason_text = f'High-value task ({best_item["value"]:.1f}), best match with {member_name} (score: {best_item["composite_score"]:.1f})'
            elif rank == 2:
                reason_text = f'High-value task ({best_item["value"]:.1f}), assigned to {member_name} (2nd best, score: {best_item["composite_score"]:.1f})'
            else:
                reason_text = f'High-value task ({best_item["value"]:.1f}), assigned to {member_name} (#{rank} match, score: {best_item["composite_score"]:.1f})'
            
            reasoning[task.id] = {
                'selected': True,
                'reason': reason_text,
                'assignedTo': member_name,
                'compositeScore': best_item['composite_score'],
                'scoreBreakdown': best_item['breakdown'],
                'value': best_item['value'],
                'rank': rank
            }
            
            remaining_tasks.remove(task)
        
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
    
    def _calc_pert_cv(self, task: Task) -> float:
        """CV = (σ / expected) × 100. Lower = more predictable. Returns 0 if O/P missing."""
        o = task.pert_optimistic
        p = task.pert_pessimistic
        expected = task.pert_expected
        if expected is None or expected <= 0 or o is None or p is None:
            return 0.0
        sigma = (p - o) / 6
        return (sigma / expected) * 100

    def _plan_pert_cv(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        PERT CV-based: Select predictable tasks first (lower CV).
        Tiebreaker: larger pert.expected first.
        Capacity: 60h per member (target_capacity = total hours).
        Task PERT expected is in hours.
        """
        capacity_per_member = 60.0
        member_workloads = {m.id: 0.0 for m in team_members}
        selected_tasks = []
        assignments = {}
        reasoning = {}
        selected_task_ids = set()
        total_hours = 0.0

        # Sort: CV asc (lower first), tiebreaker: expected desc (larger first)
        def sort_key(t: Task):
            cv = self._calc_pert_cv(t)
            expected = t.pert_expected or 0
            return (cv, -expected)

        sorted_tasks = sorted(tasks, key=sort_key)

        for task in sorted_tasks:
            task_hours = float(task.pert_expected or 0)
            if task_hours <= 0:
                continue

            deps_satisfied, deps_reason = self._check_dependencies_satisfied(
                task, tasks, selected_task_ids
            )
            if not deps_satisfied:
                reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                continue

            if total_hours + task_hours > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'Would exceed sprint capacity ({total_hours + task_hours:.1f}h > {target_capacity:.0f}h)'
                }
                continue

            eligible = [
                m for m in team_members
                if member_workloads[m.id] + task_hours <= capacity_per_member
            ]
            if not eligible:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'No member has capacity for {task_hours:.1f}h (60h max each)'
                }
                continue

            best_member = min(eligible, key=lambda m: member_workloads[m.id])
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': best_member.id,
                'memberName': best_member.name,
                'role': 'responsible',
                'storyPoints': task.story_points or 0,
                'pertHours': task_hours
            }
            member_workloads[best_member.id] += task_hours
            total_hours += task_hours

            cv = self._calc_pert_cv(task)
            reasoning[task.id] = {
                'selected': True,
                'reason': f'CV {cv:.1f}% (predictable), {task_hours:.1f}h → {best_member.name}',
                'assignedTo': best_member.name,
                'pertHours': task_hours,
                'cv': cv
            }

        metrics = self._calculate_metrics_pert(
            selected_tasks, member_workloads, team_members, target_capacity
        )
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }

    def _plan_pert_workload(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        PERT workload-style: Use pert.expected (hours), balance across members.
        Capacity: 60h per member. Sort by hours (larger first for packing).
        """
        capacity_per_member = 60.0
        member_workloads = {m.id: 0.0 for m in team_members}
        selected_tasks = []
        assignments = {}
        reasoning = {}
        selected_task_ids = set()
        total_hours = 0.0

        # Sort by pert.expected desc (larger first, like workload-balanced with SP)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: -(float(t.pert_expected or 0))
        )

        for task in sorted_tasks:
            task_hours = float(task.pert_expected or 0)
            if task_hours <= 0:
                continue

            deps_satisfied, deps_reason = self._check_dependencies_satisfied(
                task, tasks, selected_task_ids
            )
            if not deps_satisfied:
                reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                continue

            if total_hours + task_hours > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'Would exceed sprint capacity ({total_hours + task_hours:.1f}h > {target_capacity:.0f}h)'
                }
                continue

            eligible = [
                m for m in team_members
                if member_workloads[m.id] + task_hours <= capacity_per_member
            ]
            if not eligible:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'No member has capacity for {task_hours:.1f}h (60h max each)'
                }
                continue

            best_member = min(eligible, key=lambda m: member_workloads[m.id])
            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': best_member.id,
                'memberName': best_member.name,
                'role': 'responsible',
                'storyPoints': task.story_points or 0,
                'pertHours': task_hours
            }
            member_workloads[best_member.id] += task_hours
            total_hours += task_hours

            reasoning[task.id] = {
                'selected': True,
                'reason': f'{task_hours:.1f}h → {best_member.name} (workload balance)',
                'assignedTo': best_member.name,
                'pertHours': task_hours
            }

        metrics = self._calculate_metrics_pert(
            selected_tasks, member_workloads, team_members, target_capacity
        )
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_pert_raci_integration(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        PERT + RACI Integration: Like PERT workload, but uses adjusted duration.
        T_adjusted = T × (1 + (w_R×L_R) + (w_A×L_A) + (w_C×L_C) + (w_I×L_I))
        Duration weights from RaciWeightsConfig (context['raci_duration_weights']).
        """
        capacity_per_member = 60.0
        member_workloads_hours = {m.id: 0.0 for m in team_members}
        selected_tasks = []
        assignments = {}
        reasoning = {}
        selected_task_ids = set()
        total_hours = 0.0
        
        # Duration weights from RaciWeightsConfig (PERT + RACI page)
        raci_duration = context.get('raci_duration_weights') or {
            'responsible': 1.0, 'accountable': 0.1, 'consulted': 0.05, 'informed': 0.01
        }
        
        remaining_tasks = [t for t in tasks if (t.pert_expected or 0) > 0]
        
        while remaining_tasks:
            # Build RACI workloads from selected tasks (sprint_id=None => no filter)
            member_workloads = self.pert_raci_analyzer._calculate_raci_workloads(
                team_members, selected_tasks, sprint_id=None
            )
            
            # Compute adjusted duration for each remaining task
            task_adjusted = []
            for task in remaining_tasks:
                adj = self.pert_raci_analyzer._calculate_task_adjusted_duration(
                    task, team_members, member_workloads, duration_weights=raci_duration
                )
                task_adjusted.append((task, adj))
            
            # Sort by adjusted duration descending (larger first)
            task_adjusted.sort(key=lambda x: -x[1])
            
            added = False
            for task, task_hours in task_adjusted:
                if task_hours <= 0:
                    continue
                
                deps_satisfied, deps_reason = self._check_dependencies_satisfied(
                    task, tasks, selected_task_ids
                )
                if not deps_satisfied:
                    reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                    continue
                
                if total_hours + task_hours > target_capacity:
                    reasoning[task.id] = {
                        'selected': False,
                        'reason': f'Would exceed sprint capacity ({total_hours + task_hours:.1f}h > {target_capacity:.0f}h)'
                    }
                    continue
                
                eligible = [
                    m for m in team_members
                    if member_workloads_hours[m.id] + task_hours <= capacity_per_member
                ]
                if not eligible:
                    reasoning[task.id] = {
                        'selected': False,
                        'reason': f'No member has capacity for {task_hours:.1f}h (60h max each)'
                    }
                    continue
                
                best_member = min(eligible, key=lambda m: member_workloads_hours[m.id])
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id,
                    'taskName': task.name,
                    'memberId': best_member.id,
                    'memberName': best_member.name,
                    'role': 'responsible',
                    'storyPoints': task.story_points or 0,
                    'pertHours': task_hours,
                    'adjustedDuration': task_hours
                }
                member_workloads_hours[best_member.id] += task_hours
                total_hours += task_hours
                
                pert_raw = float(task.pert_expected or 0)
                adj_note = f' (adj from {pert_raw:.1f}h)' if abs(task_hours - pert_raw) > 0.01 else ''
                reasoning[task.id] = {
                    'selected': True,
                    'reason': f'{task_hours:.1f}h{adj_note} → {best_member.name} (RACI-adjusted workload)',
                    'assignedTo': best_member.name,
                    'pertHours': task_hours,
                    'adjustedDuration': task_hours
                }
                
                remaining_tasks.remove(task)
                added = True
                break
            
            if not added:
                for task, _ in task_adjusted:
                    if task.id not in reasoning:
                        reasoning[task.id] = {
                            'selected': False,
                            'reason': 'No capacity or dependencies not satisfied'
                        }
                break
        
        metrics = self._calculate_metrics_pert(
            selected_tasks, member_workloads_hours, team_members, target_capacity
        )
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _plan_pert_raci_integration_skills(
        self, tasks, team_members, target_capacity, context
    ) -> Dict:
        """PERT + RACI Integration + Skills: Adjusted duration order, assign to best skill match."""
        return self._plan_pert_raci_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='adjusted_hours', assign_by='skills'
        )
    
    def _plan_pert_raci_integration_priority(
        self, tasks, team_members, target_capacity, context
    ) -> Dict:
        """PERT + RACI Integration + Priority: Adjusted duration then priority, assign by workload."""
        return self._plan_pert_raci_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='adjusted_hours_priority', assign_by='workload'
        )
    
    def _plan_pert_raci_integration_value(
        self, tasks, team_members, target_capacity, context
    ) -> Dict:
        """PERT + RACI Integration + Value: Order by value (SP×priority), assign by workload."""
        return self._plan_pert_raci_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='value', assign_by='workload'
        )
    
    def _plan_pert_raci_with_assignment(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict,
        task_sort: str,
        assign_by: str
    ) -> Dict:
        """
        Shared PERT + RACI planning with adjusted duration.
        task_sort: 'adjusted_hours' | 'adjusted_hours_priority' | 'value'
        assign_by: 'workload' | 'skills'
        """
        capacity_per_member = 60.0
        member_workloads_hours = {m.id: 0.0 for m in team_members}
        selected_tasks = []
        assignments = {}
        reasoning = {}
        selected_task_ids = set()
        total_hours = 0.0
        
        raci_duration = context.get('raci_duration_weights') or {
            'responsible': 1.0, 'accountable': 0.1, 'consulted': 0.05, 'informed': 0.01
        }
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        priority_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        MIN_SKILL_SCORE = 40
        
        remaining_tasks = [t for t in tasks if (t.pert_expected or 0) > 0]
        
        while remaining_tasks:
            member_workloads = self.pert_raci_analyzer._calculate_raci_workloads(
                team_members, selected_tasks, sprint_id=None
            )
            
            task_adjusted = []
            for task in remaining_tasks:
                adj = self.pert_raci_analyzer._calculate_task_adjusted_duration(
                    task, team_members, member_workloads, duration_weights=raci_duration
                )
                task_adjusted.append((task, adj))
            
            if task_sort == 'adjusted_hours':
                task_adjusted.sort(key=lambda x: -x[1])
            elif task_sort == 'adjusted_hours_priority':
                task_adjusted.sort(key=lambda x: (
                    -x[1], -priority_map.get((x[0].priority or 'medium').lower(), 2)
                ))
            elif task_sort == 'value':
                def value_key(item):
                    t, adj = item
                    sp = t.story_points or 0
                    pw = priority_weights.get((t.priority or 'medium').lower(), 2.0)
                    return -(sp * pw)
                task_adjusted.sort(key=value_key)
            else:
                task_adjusted.sort(key=lambda x: -x[1])
            
            added = False
            for task, task_hours in task_adjusted:
                if task_hours <= 0:
                    continue
                
                deps_satisfied, deps_reason = self._check_dependencies_satisfied(
                    task, tasks, selected_task_ids
                )
                if not deps_satisfied:
                    reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                    continue
                
                if total_hours + task_hours > target_capacity:
                    reasoning[task.id] = {
                        'selected': False,
                        'reason': f'Would exceed sprint capacity ({total_hours + task_hours:.1f}h > {target_capacity:.0f}h)'
                    }
                    continue
                
                eligible = [
                    m for m in team_members
                    if member_workloads_hours[m.id] + task_hours <= capacity_per_member
                ]
                if not eligible:
                    reasoning[task.id] = {
                        'selected': False,
                        'reason': f'No member has capacity for {task_hours:.1f}h (60h max each)'
                    }
                    continue
                
                if assign_by == 'skills':
                    workload_for_scoring = self._pert_workload_for_scoring(
                        member_workloads_hours, team_members, capacity_per_member
                    )
                    task_reqs = {
                        'required_skills': task.required_skills or [],
                        'type': task.type,
                        'priority': task.priority
                    }
                    member_scores = self.team_scoring.rank_members_for_task(
                        team_members, task_reqs, [], workload_for_scoring
                    )
                    eligible_ids = {e.id for e in eligible}
                    best_member = None
                    for ms in member_scores:
                        if ms['final_score'] < MIN_SKILL_SCORE:
                            continue
                        mid = ms['member_id']
                        if mid in eligible_ids:
                            best_member = next(m for m in team_members if m.id == mid)
                            break
                    if best_member is None:
                        best_member = min(eligible, key=lambda m: member_workloads_hours[m.id])
                else:
                    best_member = min(eligible, key=lambda m: member_workloads_hours[m.id])
                
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id,
                    'taskName': task.name,
                    'memberId': best_member.id,
                    'memberName': best_member.name,
                    'role': 'responsible',
                    'storyPoints': task.story_points or 0,
                    'pertHours': task_hours,
                    'adjustedDuration': task_hours
                }
                member_workloads_hours[best_member.id] += task_hours
                total_hours += task_hours
                
                pert_raw = float(task.pert_expected or 0)
                adj_note = f' (adj from {pert_raw:.1f}h)' if abs(task_hours - pert_raw) > 0.01 else ''
                reason_suffix = 'skill match' if assign_by == 'skills' else 'RACI-adjusted workload'
                reasoning[task.id] = {
                    'selected': True,
                    'reason': f'{task_hours:.1f}h{adj_note} → {best_member.name} ({reason_suffix})',
                    'assignedTo': best_member.name,
                    'pertHours': task_hours,
                    'adjustedDuration': task_hours
                }
                
                remaining_tasks.remove(task)
                added = True
                break
            
            if not added:
                for task, _ in task_adjusted:
                    if task.id not in reasoning:
                        reasoning[task.id] = {
                            'selected': False,
                            'reason': 'No capacity or dependencies not satisfied'
                        }
                break
        
        metrics = self._calculate_metrics_pert(
            selected_tasks, member_workloads_hours, team_members, target_capacity
        )
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments,
            'metrics': metrics,
            'reasoning': reasoning
        }
    
    def _pert_workload_for_scoring(
        self,
        member_workloads_hours: Dict[int, float],
        team_members: List[TeamMember],
        capacity_per_member: float = 60.0
    ) -> Dict[int, float]:
        """Convert PERT hours to SP-equivalent for team_scoring (uses max_story_points)."""
        return {
            m.id: (member_workloads_hours.get(m.id, 0) / capacity_per_member) * m.max_story_points
            for m in team_members
        }

    def _plan_pert_cv_skills(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """PERT CV + Skills: Task order by CV, assign to best skill match with capacity."""
        return self._plan_pert_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='cv', assign_by='skills'
        )

    def _plan_pert_cv_priority(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """PERT CV + Priority: Task order by CV then priority, assign by workload balance."""
        return self._plan_pert_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='cv_priority', assign_by='workload'
        )

    def _plan_pert_cv_value(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """PERT CV + Value: Task order by value (SP×priority), assign by workload balance."""
        return self._plan_pert_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='value', assign_by='workload'
        )

    def _plan_pert_workload_skills(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """PERT Workload + Skills: Task order by hours (larger first), assign to best skill match."""
        return self._plan_pert_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='hours', assign_by='skills'
        )

    def _plan_pert_workload_priority(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """PERT Workload + Priority: Task order by hours then priority, assign by workload."""
        return self._plan_pert_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='hours_priority', assign_by='workload'
        )

    def _plan_pert_workload_value(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """PERT Workload + Value: Task order by value, assign by workload balance."""
        return self._plan_pert_with_assignment(
            tasks, team_members, target_capacity, context,
            task_sort='value', assign_by='workload'
        )

    def _plan_pert_with_assignment(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict,
        task_sort: str,
        assign_by: str
    ) -> Dict:
        """
        Shared PERT planning with configurable task order and assignment.
        task_sort: 'cv' | 'cv_priority' | 'hours' | 'hours_priority' | 'value'
        assign_by: 'workload' | 'skills'
        """
        capacity_per_member = 60.0
        member_workloads = {m.id: 0.0 for m in team_members}
        selected_tasks = []
        assignments = {}
        reasoning = {}
        selected_task_ids = set()
        total_hours = 0.0

        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        priority_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}

        # Sort tasks
        if task_sort == 'cv':
            sorted_tasks = sorted(tasks, key=lambda t: (self._calc_pert_cv(t), -(t.pert_expected or 0)))
        elif task_sort == 'cv_priority':
            sorted_tasks = sorted(
                tasks,
                key=lambda t: (
                    self._calc_pert_cv(t),
                    -priority_map.get((t.priority or 'medium').lower(), 2),
                    -(t.pert_expected or 0)
                )
            )
        elif task_sort == 'hours':
            sorted_tasks = sorted(tasks, key=lambda t: -(float(t.pert_expected or 0)))
        elif task_sort == 'hours_priority':
            sorted_tasks = sorted(
                tasks,
                key=lambda t: (
                    -(float(t.pert_expected or 0)),
                    -priority_map.get((t.priority or 'medium').lower(), 2)
                )
            )
        elif task_sort == 'value':
            def value_key(t):
                sp = t.story_points or 0
                pw = priority_weights.get((t.priority or 'medium').lower(), 2.0)
                return -(sp * pw)
            sorted_tasks = sorted(tasks, key=value_key)
        else:
            sorted_tasks = sorted(tasks, key=lambda t: -(float(t.pert_expected or 0)))

        MIN_SKILL_SCORE = 40

        for task in sorted_tasks:
            task_hours = float(task.pert_expected or 0)
            if task_hours <= 0:
                continue

            deps_satisfied, deps_reason = self._check_dependencies_satisfied(
                task, tasks, selected_task_ids
            )
            if not deps_satisfied:
                reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                continue

            if total_hours + task_hours > target_capacity:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'Would exceed sprint capacity ({total_hours + task_hours:.1f}h > {target_capacity:.0f}h)'
                }
                continue

            eligible = [
                m for m in team_members
                if member_workloads[m.id] + task_hours <= capacity_per_member
            ]
            if not eligible:
                reasoning[task.id] = {
                    'selected': False,
                    'reason': f'No member has capacity for {task_hours:.1f}h (60h max each)'
                }
                continue

            if assign_by == 'skills':
                workload_for_scoring = self._pert_workload_for_scoring(
                    member_workloads, team_members, capacity_per_member
                )
                task_reqs = {
                    'required_skills': task.required_skills or [],
                    'type': task.type,
                    'priority': task.priority
                }
                member_scores = self.team_scoring.rank_members_for_task(
                    team_members, task_reqs, [], workload_for_scoring
                )
                eligible_ids = {e.id for e in eligible}
                best_member = None
                for ms in member_scores:
                    if ms['final_score'] < MIN_SKILL_SCORE:
                        continue
                    mid = ms['member_id']
                    if mid in eligible_ids:
                        best_member = next(m for m in team_members if m.id == mid)
                        break
                if best_member is None:
                    best_member = min(eligible, key=lambda m: member_workloads[m.id])
            else:
                best_member = min(eligible, key=lambda m: member_workloads[m.id])

            selected_tasks.append(task)
            selected_task_ids.add(task.id)
            assignments[task.id] = {
                'taskId': task.id,
                'taskName': task.name,
                'memberId': best_member.id,
                'memberName': best_member.name,
                'role': 'responsible',
                'storyPoints': task.story_points or 0,
                'pertHours': task_hours
            }
            member_workloads[best_member.id] += task_hours
            total_hours += task_hours

            cv = self._calc_pert_cv(task)
            reasoning[task.id] = {
                'selected': True,
                'reason': f'{task_hours:.1f}h → {best_member.name}',
                'assignedTo': best_member.name,
                'pertHours': task_hours,
                'cv': cv
            }

        metrics = self._calculate_metrics_pert(
            selected_tasks, member_workloads, team_members, target_capacity
        )
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
    def _plan_hybrid(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        target_capacity: float,
        context: Dict
    ) -> Dict:
        """
        Hybrid planning: Combine all factors with configurable weights.
        Supports pertMode: none (SP), pert (raw hours), pert-raci (adjusted duration).
        pertPredictability adds CV (lower CV = more predictable = higher score).
        """
        parameters = context.get('parameters', {})
        weights = parameters.get('weights', {
            'priority': 0.30, 'workload': 0.25, 'skills': 0.30, 'dependency': 0.15
        })
        pert_mode = weights.get('pertMode', 'none')
        pert_predictability = weights.get('pertPredictability', 0.1)
        raci_duration = context.get('raci_duration_weights')
        
        if pert_mode in ('pert', 'pert-raci'):
            return self._plan_hybrid_pert(
                tasks, team_members, target_capacity, context,
                weights, pert_mode, pert_predictability, raci_duration
            )
        return self._plan_hybrid_sp(tasks, team_members, target_capacity, context, weights)
    
    def _plan_hybrid_sp(
        self, tasks, team_members, target_capacity, context, weights
    ) -> Dict:
        """Hybrid SP-based (original logic)."""
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        risk_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        
        blocker_count = {t.id: 0 for t in tasks}
        for task in tasks:
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id in blocker_count:
                        blocker_count[dep_id] += 1
        
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
            # Based on how many OTHER tasks depend ON this task (blocker count)
            # More blockers = higher score (should be done first to unblock work)
            blocked_tasks = blocker_count.get(task.id, 0)
            dependency_score = min(100, 50 + (blocked_tasks * 10))
            
            # Risk score (0-100, inverse - lower risk = higher score)
            risk_level = getattr(task, 'risk_level', 'medium').lower()
            risk_score = 100 - (risk_map.get(risk_level, 2) * 25)
            
            # Get best member match for this task
            task_requirements = {
                'required_skills': task.required_skills or [],
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
            
            # Calculate weighted composite score
            composite_score = (
                weights.get('priority', 0.30) * priority_score +
                weights.get('workload', 0.25) * workload_score +
                weights.get('skills', 0.30) * skills_score +
                weights.get('dependency', 0.15) * dependency_score
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
                    'risk': risk_score,
                    'blockedTasksCount': blocked_tasks
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
            
            # Build reason text with blocker info
            blocked_tasks_count = item['breakdown'].get('blockedTasksCount', 0)
            reason_parts = [f'Hybrid score: {item["score"]:.1f}']
            if blocked_tasks_count > 0:
                reason_parts.append(f'blocks {blocked_tasks_count} task{"s" if blocked_tasks_count > 1 else ""}')
            reason_parts.append(f'assigned to {member.name}')
            
            reasoning[task.id] = {
                'selected': True,
                'reason': ' - '.join(reason_parts),
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
    
    def _plan_hybrid_pert(
        self, tasks, team_members, target_capacity, context,
        weights, pert_mode, pert_predictability, raci_duration
    ) -> Dict:
        """Hybrid with PERT or PERT+RACI capacity. Dynamic iteration for pert-raci."""
        cross_project_workload = context.get('cross_project_workload', {})
        consider_cross_project = context.get('consider_cross_project', False)
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        capacity_per_member = 60.0
        raci_duration = raci_duration or {
            'responsible': 1.0, 'accountable': 0.1, 'consulted': 0.05, 'informed': 0.01
        }
        
        blocker_count = {t.id: 0 for t in tasks}
        for task in tasks:
            if task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id in blocker_count:
                        blocker_count[dep_id] += 1
        
        member_workloads_hours = {m.id: 0.0 for m in team_members}
        selected_tasks, assignments, reasoning = [], {}, {}
        selected_task_ids, total_hours = set(), 0.0
        remaining = [t for t in tasks if (t.pert_expected or 0) > 0]
        
        while remaining:
            if pert_mode == 'pert-raci':
                raci_workloads = self.pert_raci_analyzer._calculate_raci_workloads(
                    team_members, selected_tasks, sprint_id=None
                )
            
            workload_for_scoring = self._pert_workload_for_scoring(
                member_workloads_hours, team_members, capacity_per_member
            )
            
            task_scores = []
            for task in remaining:
                task_hours = float(task.pert_expected or 0)
                if pert_mode == 'pert-raci':
                    task_hours = self.pert_raci_analyzer._calculate_task_adjusted_duration(
                        task, team_members, raci_workloads, duration_weights=raci_duration
                    )
                if task_hours <= 0:
                    continue
                
                priority_score = priority_map.get((task.priority or 'medium').lower(), 2) * 33.33
                blocked_tasks = blocker_count.get(task.id, 0)
                dependency_score = min(100, 50 + (blocked_tasks * 10))
                
                task_reqs = {'required_skills': task.required_skills or [], 'type': task.type, 'priority': task.priority}
                member_scores = self.team_scoring.rank_members_for_task(team_members, task_reqs, [], workload_for_scoring)
                if not member_scores:
                    continue
                best = member_scores[0]
                cv = self._calc_pert_cv(task)
                predictability_score = max(0, 100 - cv)
                composite_score = (
                    weights.get('priority', 0.30) * priority_score +
                    weights.get('workload', 0.25) * best['breakdown']['workload'] +
                    weights.get('skills', 0.30) * best['breakdown']['skills'] +
                    weights.get('dependency', 0.15) * dependency_score +
                    pert_predictability * predictability_score
                )
                task_scores.append({
                    'task': task, 'task_hours': task_hours, 'score': composite_score,
                    'member_id': best['member_id'], 'member_name': best['member_name'],
                    'breakdown': {
                        'priority': priority_score, 'workload': best['breakdown']['workload'],
                        'skills': best['breakdown']['skills'], 'dependency': dependency_score,
                        'blockedTasksCount': blocked_tasks, 'cv': cv
                    }
                })
            
            task_scores.sort(key=lambda x: -x['score'])
            added = False
            for item in task_scores:
                task, task_hours = item['task'], item['task_hours']
                deps_satisfied, deps_reason = self._check_dependencies_satisfied(task, tasks, selected_task_ids)
                if not deps_satisfied:
                    reasoning[task.id] = {'selected': False, 'reason': deps_reason}
                    continue
                if total_hours + task_hours > target_capacity:
                    reasoning[task.id] = {'selected': False, 'reason': f'Would exceed capacity ({total_hours + task_hours:.1f}h > {target_capacity:.0f}h)'}
                    continue
                
                eligible = [m for m in team_members if member_workloads_hours[m.id] + task_hours <= capacity_per_member]
                if not eligible:
                    reasoning[task.id] = {'selected': False, 'reason': f'No member has capacity for {task_hours:.1f}h'}
                    continue
                
                best_member = min(eligible, key=lambda m: member_workloads_hours[m.id])
                selected_tasks.append(task)
                selected_task_ids.add(task.id)
                assignments[task.id] = {
                    'taskId': task.id, 'taskName': task.name,
                    'memberId': best_member.id, 'memberName': best_member.name,
                    'role': 'responsible', 'storyPoints': task.story_points or 0,
                    'pertHours': task_hours, 'adjustedDuration': task_hours
                }
                member_workloads_hours[best_member.id] += task_hours
                total_hours += task_hours
                
                blocked = item['breakdown'].get('blockedTasksCount', 0)
                reason_parts = [f'Hybrid {pert_mode}: {item["score"]:.1f}']
                if blocked > 0:
                    reason_parts.append(f'blocks {blocked}')
                reason_parts.append(f'{task_hours:.1f}h → {best_member.name}')
                reasoning[task.id] = {
                    'selected': True, 'reason': ' - '.join(reason_parts),
                    'assignedTo': best_member.name, 'compositeScore': item['score'],
                    'scoreBreakdown': item['breakdown'], 'pertHours': task_hours
                }
                remaining.remove(task)
                added = True
                break
            
            if not added:
                for item in task_scores:
                    if item['task'].id not in reasoning:
                        reasoning[item['task'].id] = {'selected': False, 'reason': 'No capacity'}
                break
        
        metrics = self._calculate_metrics_pert(
            selected_tasks, member_workloads_hours, team_members, target_capacity
        )
        metrics['weights'] = weights
        return {
            'suggestedTasks': [self._task_to_dict(t) for t in selected_tasks],
            'assignments': assignments, 'metrics': metrics, 'reasoning': reasoning
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

    def _calculate_metrics_pert(
        self,
        selected_tasks: List[Task],
        member_workloads: Dict[int, float],
        team_members: List[TeamMember],
        target_capacity_hours: float
    ) -> Dict:
        """PERT metrics: hours-based capacity (60h per member). Task PERT expected in hours."""
        total_hours = sum(float(t.pert_expected or 0) for t in selected_tasks)
        total_sp = sum(t.story_points or 0 for t in selected_tasks)
        utilization = (total_hours / target_capacity_hours * 100) if target_capacity_hours > 0 else 0

        # Balance score: workload hours per member (60h max each)
        capacity_per_member = 60.0
        workload_pcts = [
            (member_workloads.get(m.id, 0) / capacity_per_member * 100)
            for m in team_members
        ]
        if workload_pcts:
            avg = sum(workload_pcts) / len(workload_pcts)
            variance = sum((x - avg) ** 2 for x in workload_pcts) / len(workload_pcts)
            std_dev = variance ** 0.5
            balance_score = max(0, 100 - (std_dev * 2))
        else:
            balance_score = 100.0

        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for task in selected_tasks:
            p = (task.priority or 'medium').lower()
            if p in priority_counts:
                priority_counts[p] += 1

        return {
            'totalStoryPoints': total_sp,
            'totalHours': round(total_hours, 1),
            'teamCapacity': target_capacity_hours,
            'teamCapacityHours': target_capacity_hours,
            'utilization': round(utilization, 1),
            'balanceScore': round(balance_score, 1),
            'riskScore': 0,
            'taskCount': len(selected_tasks),
            'priorityDistribution': priority_counts,
            'pertMode': True
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
        pert_mode = planning_context.get('pert_mode', False)
        capacity_per_member = 60.0 if pert_mode else None

        team_analysis = []

        # Calculate workload assigned in this sprint for each member
        member_sprint_workload = {}
        for assignment in assignments.values():
            member_id = assignment['memberId']
            if pert_mode:
                workload = assignment.get('pertHours', 0)
            else:
                workload = assignment['storyPoints']
            member_sprint_workload[member_id] = member_sprint_workload.get(member_id, 0) + workload

        for member in team_members:
            if pert_mode:
                max_cap = capacity_per_member
                cross_proj = 0  # PERT mode: no cross-project hours
            else:
                max_cap = member.max_story_points
                cross_proj = cross_project_workload.get(member.id, 0) if consider_cross_project else 0

            sprint_workload = member_sprint_workload.get(member.id, 0)
            total_workload = cross_proj + sprint_workload
            available = max_cap - total_workload

            status = 'available'
            if total_workload >= max_cap:
                status = 'at_capacity'
            elif total_workload > max_cap * 0.9:
                status = 'nearly_full'
            elif sprint_workload > 0:
                status = 'assigned'

            analysis = {
                'memberId': member.id,
                'memberName': member.name,
                'maxCapacity': max_cap,
                'assignedInThisSprint': sprint_workload,
                'crossProjectWorkload': cross_proj,
                'totalWorkload': total_workload,
                'availableCapacity': max(0, available),
                'utilizationPercentage': (total_workload / max_cap * 100) if max_cap > 0 else 0,
                'status': status,
                'taskCount': len([a for a in assignments.values() if a['memberId'] == member.id])
            }
            if pert_mode:
                analysis['assignedHours'] = sprint_workload

            # Add reasoning for members who didn't get tasks
            if sprint_workload == 0:
                if pert_mode:
                    analysis['reason'] = 'Not assigned - tasks matched better with other team members'
                elif consider_cross_project and cross_proj > 0:
                    high_priority = cross_project_priorities.get(member.id, 0)
                    if high_priority > 0:
                        analysis['reason'] = f'Not assigned - has {cross_proj:.0f} SP in other projects ({high_priority} high-priority tasks)'
                    else:
                        analysis['reason'] = f'Not assigned - has {cross_proj:.0f} SP in other projects'
                elif total_workload >= max_cap:
                    analysis['reason'] = 'Not assigned - at maximum capacity'
                else:
                    analysis['reason'] = 'Not assigned - tasks matched better with other team members'
            else:
                if pert_mode:
                    analysis['reason'] = f'Assigned {sprint_workload:.1f}h'
                elif consider_cross_project and cross_proj > 0:
                    analysis['reason'] = f'Assigned {sprint_workload:.0f} SP (considering {cross_proj:.0f} SP from other projects)'
                else:
                    analysis['reason'] = f'Assigned {sprint_workload:.0f} SP'

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
        team_capacity: float,
        pert_mode: bool = False
    ) -> Dict:
        """Calculate summary statistics for the sprint plan"""
        total_sp = sum(task['storyPoints'] for task in selected_tasks)
        capacity_per_member = 60.0 if pert_mode else None

        # Member workload breakdown
        member_breakdown = {}
        for assignment in assignments.values():
            member_id = assignment['memberId']
            member_name = assignment['memberName']
            sp = assignment['storyPoints']
            hours = assignment.get('pertHours', 0) if pert_mode else 0

            if member_id not in member_breakdown:
                member = next((m for m in team_members if m.id == member_id), None)
                max_sp = capacity_per_member if pert_mode else (member.max_story_points if member else 20)
                member_breakdown[member_id] = {
                    'memberId': member_id,
                    'memberName': member_name,
                    'assignedSP': 0,
                    'assignedHours': 0.0,
                    'maxCapacity': max_sp,
                    'utilization': 0,
                    'taskCount': 0
                }

            member_breakdown[member_id]['assignedSP'] += sp
            member_breakdown[member_id]['taskCount'] += 1
            if pert_mode:
                member_breakdown[member_id]['assignedHours'] += hours

        # Calculate utilization for each member
        for member_data in member_breakdown.values():
            workload = member_data['assignedHours'] if pert_mode else member_data['assignedSP']
            member_data['utilization'] = (
                workload / member_data['maxCapacity'] * 100
            ) if member_data['maxCapacity'] > 0 else 0

        total_workload = sum(m['assignedHours'] for m in member_breakdown.values()) if pert_mode else total_sp
        return {
            'totalStoryPoints': total_sp,
            'totalHours': round(total_workload, 1) if pert_mode else None,
            'teamCapacity': team_capacity,
            'utilizationPercentage': (total_workload / team_capacity * 100) if team_capacity > 0 else 0,
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

