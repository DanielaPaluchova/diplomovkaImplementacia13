"""
Bottleneck Analyzer Service
Detects resource bottlenecks and single points of failure
"""
from app.models.task import Task
from app.models.team_member import TeamMember
from typing import Dict, List
import uuid


class BottleneckAnalyzerService:
    """Service for detecting bottlenecks in project resources and dependencies"""
    
    OVERLOAD_THRESHOLD = 120  # Workload > 120% is a critical bottleneck
    CRITICAL_TASK_THRESHOLD = 3  # Member with 3+ critical/high priority tasks
    DEPENDENCY_BOTTLENECK_THRESHOLD = 3  # Task blocking 3+ other tasks
    
    def __init__(self):
        pass
    
    def find_resource_bottlenecks(
        self,
        team_members: List[TeamMember],
        tasks: List[Task],
        cross_project_workload: Dict[int, Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Find team members who are bottlenecks (too many critical tasks assigned)
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            cross_project_workload: Optional dict of cross-project workload {member_id: {'sp': float, 'pct': float}}
            
        Returns:
            List of bottleneck proposals
        """
        proposals = []
        
        # Analyze each member
        for member in team_members:
            # Get their tasks (Sprint Commitment - includes Done tasks for workload calc)
            member_tasks = [
                t for t in tasks if (
                    t.raci_responsible and member.id in t.raci_responsible
                )
            ]
            
            # Calculate current workload (use cross-project if available)
            if cross_project_workload and member.id in cross_project_workload:
                total_sp = cross_project_workload[member.id]['sp']
                member_workload_pct = cross_project_workload[member.id]['pct']
            else:
                total_sp = sum(t.story_points or 0 for t in member_tasks)
                member_workload_pct = (total_sp / member.max_story_points) * 100 if member.max_story_points else 0
            
            # Skip members with no tasks or zero workload
            if not member_tasks or member_workload_pct == 0:
                continue
            
            # Count high priority tasks
            high_priority_tasks = [
                t for t in member_tasks 
                if t.priority.lower() in ['high', 'critical']
            ]
            
            # Count tasks blocking others
            blocking_tasks = [
                t for t in member_tasks
                if self._count_dependent_tasks(t, tasks) > 0
            ]
            
            # Check if bottleneck
            # Bottleneck conditions:
            # 1. Workload > 120% (CRITICAL overload)
            # 2. OR 3+ high priority tasks (concentration risk)
            is_overloaded = member_workload_pct > self.OVERLOAD_THRESHOLD
            has_too_many_critical = len(high_priority_tasks) >= self.CRITICAL_TASK_THRESHOLD
            
            if is_overloaded or has_too_many_critical:
                # Determine bottleneck reason
                if is_overloaded and has_too_many_critical:
                    bottleneck_reason = f"{member.name} is overloaded ({round(member_workload_pct)}%) with {len(high_priority_tasks)} high-priority tasks"
                elif is_overloaded:
                    bottleneck_reason = f"{member.name} is overloaded ({round(member_workload_pct)}% workload)"
                else:
                    bottleneck_reason = f"{member.name} has too many critical tasks ({len(high_priority_tasks)})"
                
                # Find other members who could help
                other_members = [m for m in team_members if m.id != member.id]
                
                if other_members:
                    # Determine which tasks to suggest moving
                    # If overloaded, prioritize moving any tasks (start with low priority to free capacity)
                    # If too many critical tasks, focus on high priority tasks
                    if is_overloaded:
                        # Sort tasks by priority (low priority first) to free up capacity
                        tasks_to_move = sorted(
                            [t for t in member_tasks if t.status != 'Done'],
                            key=lambda t: {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}.get(t.priority.lower(), 1)
                        )[:2]  # Suggest moving top 2
                    else:
                        # Focus on high priority tasks
                        tasks_to_move = high_priority_tasks[:2]
                    
                    # Suggest redistributing tasks
                    for task in tasks_to_move:
                        task_sp = task.story_points or 0
                        
                        # Calculate workloads for all candidates (use cross-project if available)
                        candidate_workloads = {}
                        for candidate in other_members:
                            if cross_project_workload and candidate.id in cross_project_workload:
                                cand_sp = cross_project_workload[candidate.id]['sp']
                                cand_pct = cross_project_workload[candidate.id]['pct']
                            else:
                                # Sprint Commitment - includes Done tasks for workload calc
                                cand_tasks = [
                                    t for t in tasks if (
                                        t.raci_responsible and candidate.id in t.raci_responsible
                                    )
                                ]
                                cand_sp = sum(t.story_points or 0 for t in cand_tasks)
                                cand_pct = (cand_sp / candidate.max_story_points) * 100
                            
                            candidate_workloads[candidate.id] = {
                                'sp': cand_sp,
                                'pct': cand_pct,
                                'max_sp': candidate.max_story_points
                            }
                        
                        # Find best candidate (with skill matching)
                        best_candidate_result = self._find_best_candidate_for_task_with_details(
                            task, member, other_members, tasks, cross_project_workload
                        )
                        
                        if best_candidate_result:
                            best_candidate = best_candidate_result['member']
                            current_skill_match = best_candidate_result['current_skill_match']
                            new_skill_match = best_candidate_result['new_skill_match']
                            task_requirements = best_candidate_result['task_requirements']
                            
                            best_workload = candidate_workloads[best_candidate.id]
                            best_workload_pct = best_workload['pct']
                            new_workload_pct = ((best_workload['sp'] + task_sp) / best_workload['max_sp']) * 100
                            
                            # Build skill match info
                            current_match_pct = int(current_skill_match * 100)
                            new_match_pct = int(new_skill_match * 100)
                            
                            # Add skill warning if new candidate has poor match
                            skill_warning = ""
                            if new_match_pct < 30 and task_requirements:
                                required_skills_list = ", ".join(sorted(task_requirements))
                                skill_warning = f"\n\n*** SKILL MISMATCH WARNING ***\n{best_candidate.name} has {new_match_pct}% skill match! Missing required skills: {required_skills_list.upper()}\nConsider training or finding alternative candidate."
                            
                            # Update bottleneck_reason with skill info
                            skill_info = f" | Skill match: {current_match_pct}% → {new_match_pct}%"
                            
                            # Check if best candidate is also overloaded
                            if best_workload_pct > 80:
                                # All members overloaded - suggest backlog
                                proposals.append({
                                    'id': f"bottleneck-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'bottleneck',
                                    'severity': 'critical',
                                    'category': 'resources',
                                    'title': f"Bottleneck: Move '{task.name}' from {member.name}",
                                    'description': f"{bottleneck_reason}. All team members at capacity.",
                                    'reason': f"{bottleneck_reason}, risking project delays. All team members are overloaded. Consider moving to backlog or adding resources.{skill_warning if skill_warning else ''}",
                                    'score': 90,
                                    'taskName': task.name,
                                    'taskSp': task_sp,
                                    'impact': {
                                        'fromMember': member.name,
                                        'fromWorkload': round(member_workload_pct, 1),
                                        'taskSP': task_sp,
                                        'taskPriority': task.priority,
                                        'riskReduction': 'high',
                                        'suggestedAction': 'move_to_backlog',
                                        'reason': 'All team members are overloaded',
                                        'currentMatch': f"{current_match_pct}%",
                                        'requiredSkills': list(task_requirements) if task_requirements else [],
                                        'affectedMembers': [member.id],
                                        'workloadChange': -((task_sp / member.max_story_points) * 100),
                                        'riskChange': -1,
                                        'balanceChange': 5
                                    },
                                    'action': {
                                        'type': 'move_to_backlog',
                                        'taskId': task.id,
                                        'fromMemberId': member.id,
                                        'reason': 'All team members overloaded'
                                    }
                                })
                            else:
                                # Can reassign to less loaded member
                                from_workload_after = ((total_sp - task_sp) / member.max_story_points) * 100
                                
                                # Update description with skill info
                                description = f"{bottleneck_reason}{skill_info}"
                                if skill_warning:
                                    description += ". However, skills mismatch detected."
                                
                                proposals.append({
                                    'id': f"bottleneck-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'bottleneck',
                                    'severity': 'critical',
                                    'category': 'resources',
                                    'title': f"Bottleneck: Reassign '{task.name}' from {member.name} to {best_candidate.name}",
                                    'description': description,
                                    'reason': f"{bottleneck_reason}, risking project delays. Distribute load to prevent single point of failure.{skill_warning if skill_warning else ''}",
                                    'score': 90,
                                    'taskName': task.name,
                                    'taskSp': task_sp,
                                    'impact': self._build_bottleneck_impact(
                                        member, best_candidate, task_sp, 
                                        member_workload_pct, from_workload_after,
                                        best_workload_pct, new_workload_pct,
                                        task, task_requirements,
                                        current_match_pct, new_match_pct
                                    ),
                                    'action': {
                                        'type': 'reassign',
                                        'taskId': task.id,
                                        'fromMemberId': member.id,
                                        'toMemberId': best_candidate.id
                                    }
                                })
        
        return proposals
    
    def find_dependency_bottlenecks(self, tasks: List[Task]) -> List[Dict]:
        """
        Find tasks that are blocking many other tasks
        
        Args:
            tasks: List of tasks
            
        Returns:
            List of bottleneck proposals
        """
        proposals = []
        
        for task in tasks:
            if task.status == 'Done':
                continue
            
            # Count how many tasks depend on this one
            dependent_count = self._count_dependent_tasks(task, tasks)
            
            if dependent_count >= self.DEPENDENCY_BOTTLENECK_THRESHOLD:
                # This task is blocking many others
                dependent_tasks = self._get_dependent_tasks(task, tasks)
                
                # Calculate potential time savings
                task_duration = task.pert_expected or (task.story_points or 0) * 0.5
                dependent_total_duration = sum(
                    t.pert_expected or (t.story_points or 0) * 0.5 
                    for t in dependent_tasks
                )
                
                # Estimate impact
                duration_impact = -min(task_duration * 0.3, 5)  # Up to 5 days faster
                risk_impact = -1.5  # Reducing bottleneck reduces risk
                
                proposals.append({
                    'id': f"dep-bottleneck-{task.id}-{uuid.uuid4().hex[:8]}",
                    'type': 'bottleneck',
                    'severity': 'critical',
                    'category': 'timeline',
                    'title': f"Critical dependency: '{task.name}' blocks {dependent_count} tasks",
                    'description': f"This task is blocking {dependent_count} other tasks from starting",
                    'reason': f"Task '{task.name}' is a critical dependency blocking {dependent_count} tasks. Consider prioritizing or adding more resources.",
                    'score': 95,
                    'taskName': task.name,
                    'taskSp': task.story_points or 0,
                    'impact': {
                        'blockedTasks': dependent_count,
                        'blockedTaskNames': [t.name for t in dependent_tasks[:3]],
                        'recommendedAction': 'Prioritize or add more resources to this task',
                        'riskLevel': 'critical',
                        'taskDuration': round(task_duration, 1),
                        'dependentDuration': round(dependent_total_duration, 1),
                        'durationChange': round(duration_impact, 1),
                        'riskChange': round(risk_impact, 1),
                        'affectedMembers': []
                    },
                    'action': {
                        'type': 'priority_increase',
                        'taskId': task.id,
                        'newPriority': 'high',
                        'addResources': True
                    }
                })
        
        return proposals
    
    def _count_dependent_tasks(self, task: Task, all_tasks: List[Task]) -> int:
        """Count how many tasks depend on this task"""
        count = 0
        for t in all_tasks:
            if t.dependencies and task.id in t.dependencies:
                count += 1
        return count
    
    def _get_dependent_tasks(self, task: Task, all_tasks: List[Task]) -> List[Task]:
        """Get all tasks that depend on this task"""
        dependent = []
        for t in all_tasks:
            if t.dependencies and task.id in t.dependencies:
                dependent.append(t)
        return dependent
    
    def _build_bottleneck_impact(
        self,
        from_member: TeamMember,
        to_member: TeamMember,
        task_sp: float,
        from_workload_pct: float,
        from_workload_after: float,
        to_workload_before: float,
        to_workload_after: float,
        task: Task,
        task_requirements: set,
        current_match_pct: float,
        new_match_pct: float
    ) -> Dict:
        """Build impact dictionary with overload warning if needed"""
        impact = {
            'fromMember': from_member.name,
            'toMember': to_member.name,
            'fromWorkload': round(from_workload_pct, 1),
            'fromWorkloadAfter': round(from_workload_after, 1),
            'toWorkloadBefore': round(to_workload_before, 1),
            'toWorkload': round(to_workload_after, 1),
            'taskSP': task_sp,
            'taskPriority': task.priority,
            'riskReduction': 'high',
            'suggestedAction': 'reassign',
            'currentMatch': f"{current_match_pct}%",
            'newMatch': f"{new_match_pct}%",
            'requiredSkills': list(task_requirements) if task_requirements else [],
            'skillMatchChange': new_match_pct - current_match_pct,
            'affectedMembers': [from_member.id, to_member.id],
            'workloadChange': -((task_sp / from_member.max_story_points) * 100),
            'riskChange': -1,
            'balanceChange': 3
        }
        
        # Add warning if recipient will be overloaded after reassignment
        if to_workload_after > 100:
            impact['recipientOverloadWarning'] = True
            impact['recipientOverloadPercent'] = round(to_workload_after, 1)
        
        return impact
    
    def _find_best_candidate_for_task_with_details(
        self,
        task: Task,
        current_member: TeamMember,
        candidates: List[TeamMember],
        all_tasks: List[Task],
        cross_project_workload: Dict[int, Dict[str, float]] = None
    ) -> Dict:
        """Find best team member to take over a task with skill match details
        
        Returns:
            Dict with member, current_skill_match, new_skill_match, task_requirements
        """
        best_member = self._find_best_candidate_for_task(task, candidates, all_tasks, cross_project_workload)
        
        if not best_member:
            return None
        
        # Calculate skill matches
        task_requirements = set(skill.lower() for skill in (task.required_skills or []))
        
        # Current member skill match
        current_skills = set(skill.lower() for skill in (current_member.skills or []))
        if task_requirements:
            current_intersection = len(task_requirements.intersection(current_skills))
            current_skill_match = current_intersection / len(task_requirements)
        else:
            current_skill_match = 1.0
        
        # New member skill match
        new_skills = set(skill.lower() for skill in (best_member.skills or []))
        if task_requirements:
            new_intersection = len(task_requirements.intersection(new_skills))
            new_skill_match = new_intersection / len(task_requirements)
        else:
            new_skill_match = 1.0
        
        return {
            'member': best_member,
            'current_skill_match': current_skill_match,
            'new_skill_match': new_skill_match,
            'task_requirements': task_requirements
        }
    
    def _find_best_candidate_for_task(
        self,
        task: Task,
        candidates: List[TeamMember],
        all_tasks: List[Task],
        cross_project_workload: Dict[int, Dict[str, float]] = None
    ) -> TeamMember:
        """Find best team member to take over a task
        
        Selection criteria (in order of priority):
        1. Has required skills (if task has required_skills)
        2. Lowest workload
        3. If no one has skills, pick lowest workload anyway
        """
        if not candidates:
            return None
        
        # Get task required skills
        task_requirements = set(skill.lower() for skill in (task.required_skills or []))
        
        # Calculate workload and skill match for each candidate
        candidate_scores = []
        for member in candidates:
            # Calculate workload (use cross-project if available)
            if cross_project_workload and member.id in cross_project_workload:
                workload_pct = cross_project_workload[member.id]['pct']
            else:
                # Sprint Commitment - includes Done tasks for workload calc
                # Note: all_tasks should already be filtered to active sprint by caller
                member_tasks = [
                    t for t in all_tasks if (
                        t.raci_responsible and member.id in t.raci_responsible
                    )
                ]
                workload_sp = sum(t.story_points or 0 for t in member_tasks)
                workload_pct = (workload_sp / member.max_story_points) * 100 if member.max_story_points else 100
            
            # Calculate skill match
            member_skills = set(skill.lower() for skill in (member.skills or []))
            if task_requirements:
                intersection = len(task_requirements.intersection(member_skills))
                skill_match = intersection / len(task_requirements)
            else:
                # No required skills - everyone matches
                skill_match = 1.0
            
            candidate_scores.append({
                'member': member,
                'workload_pct': workload_pct,
                'skill_match': skill_match,
                # Combined score: prioritize workload capacity, then skills
                # Bottleneck is caused by overload, so prioritize available capacity
                # skill_match is 0-1, workload is 0-200+
                # Weight: 60% workload (inverted), 40% skills
                'score': ((100 - min(workload_pct, 100)) / 100 * 0.6) + (skill_match * 0.4)
            })
        
        # Sort by score (higher is better)
        candidate_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # If task has required skills, only consider candidates with some skill match
        if task_requirements:
            candidates_with_skills = [c for c in candidate_scores if c['skill_match'] > 0]
            if candidates_with_skills:
                return candidates_with_skills[0]['member']
        
        # No one has skills, or no required skills - return best workload
        return candidate_scores[0]['member']

