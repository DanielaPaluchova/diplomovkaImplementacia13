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
    
    CRITICAL_TASK_THRESHOLD = 3  # Member with 3+ critical/high priority tasks
    DEPENDENCY_BOTTLENECK_THRESHOLD = 3  # Task blocking 3+ other tasks
    
    def __init__(self):
        pass
    
    def find_resource_bottlenecks(
        self,
        team_members: List[TeamMember],
        tasks: List[Task]
    ) -> List[Dict]:
        """
        Find team members who are bottlenecks (too many critical tasks assigned)
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            
        Returns:
            List of bottleneck proposals
        """
        proposals = []
        
        # Analyze each member
        for member in team_members:
            # Get their tasks
            member_tasks = [
                t for t in tasks if t.status != 'Done' and (
                    (t.raci_responsible and member.id in t.raci_responsible) or
                    t.raci_accountable == member.id
                )
            ]
            
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
            if len(high_priority_tasks) >= self.CRITICAL_TASK_THRESHOLD:
                # Calculate current workload
                total_sp = sum(t.story_points or 0 for t in member_tasks)
                member_workload_pct = (total_sp / member.max_story_points) * 100
                
                # Find other members who could help
                other_members = [m for m in team_members if m.id != member.id]
                
                if other_members:
                    # Suggest redistributing some high priority tasks
                    for task in high_priority_tasks[:2]:  # Suggest moving top 2
                        task_sp = task.story_points or 0
                        
                        # Calculate workloads for all candidates
                        candidate_workloads = {}
                        for candidate in other_members:
                            cand_tasks = [
                                t for t in tasks if t.status != 'Done' and (
                                    (t.raci_responsible and candidate.id in t.raci_responsible) or
                                    t.raci_accountable == candidate.id
                                )
                            ]
                            cand_sp = sum(t.story_points or 0 for t in cand_tasks)
                            candidate_workloads[candidate.id] = {
                                'sp': cand_sp,
                                'pct': (cand_sp / candidate.max_story_points) * 100,
                                'max_sp': candidate.max_story_points
                            }
                        
                        # Find best candidate
                        best_candidate = self._find_best_candidate_for_task(
                            task, other_members, tasks
                        )
                        
                        if best_candidate:
                            best_workload = candidate_workloads[best_candidate.id]
                            best_workload_pct = best_workload['pct']
                            new_workload_pct = ((best_workload['sp'] + task_sp) / best_workload['max_sp']) * 100
                            
                            # Check if best candidate is also overloaded
                            if best_workload_pct > 80:
                                # All members overloaded - suggest backlog
                                proposals.append({
                                    'id': f"bottleneck-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'bottleneck',
                                    'severity': 'critical',
                                    'category': 'resources',
                                    'title': f"Relieve bottleneck: Move '{task.name}' from {member.name}",
                                    'description': f"{member.name} is a bottleneck with {len(high_priority_tasks)} high-priority tasks. All team members at capacity.",
                                    'reason': f"{member.name} has too many critical tasks ({len(high_priority_tasks)}), risking project delays. All team members are overloaded. Consider moving to backlog or adding resources.",
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
                                proposals.append({
                                    'id': f"bottleneck-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'bottleneck',
                                    'severity': 'critical',
                                    'category': 'resources',
                                    'title': f"Relieve bottleneck: Move '{task.name}' from {member.name}",
                                    'description': f"{member.name} is a bottleneck with {len(high_priority_tasks)} high-priority tasks",
                                    'reason': f"{member.name} has too many critical tasks ({len(high_priority_tasks)}), risking project delays. Distribute load to prevent single point of failure.",
                                    'score': 90,
                                    'taskName': task.name,
                                    'taskSp': task_sp,
                                    'impact': {
                                        'fromMember': member.name,
                                        'toMember': best_candidate.name,
                                        'fromWorkload': round(member_workload_pct, 1),
                                        'toWorkload': round(new_workload_pct, 1),
                                        'taskSP': task_sp,
                                        'taskPriority': task.priority,
                                        'riskReduction': 'high',
                                        'suggestedAction': 'reassign',
                                        'affectedMembers': [member.id, best_candidate.id],
                                        'workloadChange': -((task_sp / member.max_story_points) * 100),
                                        'riskChange': -1,
                                        'balanceChange': 3
                                    },
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
    
    def _find_best_candidate_for_task(
        self,
        task: Task,
        candidates: List[TeamMember],
        all_tasks: List[Task]
    ) -> TeamMember:
        """Find best team member to take over a task"""
        if not candidates:
            return None
        
        # Calculate workload for each candidate
        candidate_workloads = {}
        for member in candidates:
            member_tasks = [
                t for t in all_tasks if t.status != 'Done' and (
                    (t.raci_responsible and member.id in t.raci_responsible) or
                    t.raci_accountable == member.id
                )
            ]
            workload_sp = sum(t.story_points or 0 for t in member_tasks)
            workload_pct = (workload_sp / member.max_story_points) * 100
            candidate_workloads[member.id] = workload_pct
        
        # Find member with lowest workload
        best_candidate = min(candidates, key=lambda m: candidate_workloads.get(m.id, 100))
        
        return best_candidate

