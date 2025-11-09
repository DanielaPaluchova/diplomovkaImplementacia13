"""
Risk Analyzer Service
Detects deadline risks, priority conflicts, and skill gaps
"""
from app.models.task import Task
from app.models.team_member import TeamMember
from datetime import datetime, timedelta
from typing import Dict, List
import uuid


class RiskAnalyzerService:
    """Service for analyzing project risks"""
    
    DEADLINE_BUFFER_DAYS = 3  # Warn if less than 3 days buffer
    SKILL_MATCH_THRESHOLD = 0.3  # 30% skills match required
    
    def __init__(self):
        pass
    
    def find_deadline_risks(self, tasks: List[Task]) -> List[Dict]:
        """
        Find tasks at risk of missing their deadline
        
        Args:
            tasks: List of tasks
            
        Returns:
            List of deadline risk proposals
        """
        proposals = []
        now = datetime.utcnow()
        
        for task in tasks:
            if task.status == 'Done' or not task.due_date:
                continue
            
            # Parse due date
            if isinstance(task.due_date, str):
                due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
            else:
                due_date = task.due_date
            
            # Calculate time remaining
            days_remaining = (due_date - now).days
            
            # Calculate estimated time needed
            estimated_days = task.pert_expected or (task.story_points or 0) * 0.5
            buffer = days_remaining - estimated_days
            
            # Check if at risk
            if buffer < self.DEADLINE_BUFFER_DAYS and task.status != 'In Progress':
                severity = 'critical' if buffer < 1 else 'important'
                
                # Calculate potential time savings from prioritization
                time_savings = min(estimated_days * 0.2, 2)  # Up to 2 days faster
                
                proposals.append({
                    'id': f"deadline-risk-{task.id}-{uuid.uuid4().hex[:8]}",
                    'type': 'deadline_risk',
                    'severity': severity,
                    'category': 'timeline',
                    'title': f"Deadline risk: '{task.name}' due in {days_remaining} days",
                    'description': f"Task may miss deadline with only {round(buffer, 1)} days buffer",
                    'reason': f"Task '{task.name}' needs {round(estimated_days, 1)} days but deadline is in {days_remaining} days. Buffer: {round(buffer, 1)} days.",
                    'score': 95 if severity == 'critical' else 85,
                    'taskName': task.name,
                    'taskSp': task.story_points or 0,
                    'impact': {
                        'daysRemaining': days_remaining,
                        'estimatedDays': round(estimated_days, 1),
                        'buffer': round(buffer, 1),
                        'riskLevel': severity,
                        'dueDate': due_date.isoformat(),
                        'taskSP': task.story_points or 0,
                        'durationChange': -round(time_savings, 1),
                        'riskChange': -1 if severity == 'critical' else -0.5,
                        'affectedMembers': []
                    },
                    'action': {
                        'type': 'priority_increase',
                        'taskId': task.id,
                        'newPriority': 'high',
                        'startImmediately': True
                    }
                })
        
        return proposals
    
    def find_priority_conflicts(
        self,
        team_members: List[TeamMember],
        tasks: List[Task]
    ) -> List[Dict]:
        """
        Find high priority tasks assigned to overloaded members
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            
        Returns:
            List of priority conflict proposals
        """
        proposals = []
        
        for member in team_members:
            # Get member's tasks
            member_tasks = [
                t for t in tasks if t.status != 'Done' and (
                    (t.raci_responsible and member.id in t.raci_responsible) or
                    t.raci_accountable == member.id
                )
            ]
            
            # Calculate workload
            total_sp = sum(t.story_points or 0 for t in member_tasks)
            workload_pct = (total_sp / member.max_story_points) * 100
            
            # Check if overloaded
            if workload_pct > 85:
                # Find high priority tasks
                high_priority = [
                    t for t in member_tasks
                    if t.priority.lower() in ['high', 'critical']
                ]
                
                if high_priority:
                    # Suggest moving to less loaded members
                    for task in high_priority[:1]:  # Focus on top priority
                        task_sp = task.story_points or 0
                        
                        # Find alternative assignees
                        other_members = [m for m in team_members if m.id != member.id]
                        
                        if other_members:
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
                            
                            # Find least loaded
                            best_candidate = min(
                                other_members,
                                key=lambda m: candidate_workloads[m.id]['pct']
                            )
                            
                            best_workload = candidate_workloads[best_candidate.id]
                            best_workload_pct = best_workload['pct']
                            new_workload_pct = ((best_workload['sp'] + task_sp) / best_workload['max_sp']) * 100
                            
                            # Check if best candidate is also overloaded
                            if best_workload_pct > 80:
                                # All members overloaded - suggest backlog
                                proposals.append({
                                    'id': f"priority-conflict-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'priority_conflict',
                                    'severity': 'critical',
                                    'category': 'workload',
                                    'title': f"Priority conflict: Move '{task.name}' from overloaded {member.name}",
                                    'description': f"High priority task assigned to overloaded team member. All team members at capacity.",
                                    'reason': f"{member.name} is overloaded ({round(workload_pct, 1)}%) but has high-priority task '{task.name}'. All team members are overloaded. Consider moving to backlog or adding resources.",
                                    'score': 90,
                                    'taskName': task.name,
                                    'taskSp': task_sp,
                                    'impact': {
                                        'fromMember': member.name,
                                        'fromWorkload': round(workload_pct, 1),
                                        'taskSP': task_sp,
                                        'taskPriority': task.priority,
                                        'suggestedAction': 'move_to_backlog',
                                        'reason': 'All team members are overloaded',
                                        'affectedMembers': [member.id],
                                        'workloadChange': -((task_sp / member.max_story_points) * 100),
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
                                    'id': f"priority-conflict-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'priority_conflict',
                                    'severity': 'critical',
                                    'category': 'workload',
                                    'title': f"Priority conflict: Move '{task.name}' from overloaded {member.name}",
                                    'description': f"High priority task assigned to overloaded team member",
                                    'reason': f"{member.name} is overloaded ({round(workload_pct, 1)}%) but has high-priority task '{task.name}'. Risk of delays.",
                                    'score': 90,
                                    'taskName': task.name,
                                    'taskSp': task_sp,
                                    'impact': {
                                        'fromMember': member.name,
                                        'toMember': best_candidate.name,
                                        'fromWorkload': round(workload_pct, 1),
                                        'toWorkload': round(new_workload_pct, 1),
                                        'taskSP': task_sp,
                                        'taskPriority': task.priority,
                                        'suggestedAction': 'reassign',
                                        'currentWorkload': round(workload_pct, 1),
                                        'affectedMembers': [member.id, best_candidate.id],
                                        'workloadChange': -((task_sp / member.max_story_points) * 100),
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
    
    def find_skill_mismatches(
        self,
        team_members: List[TeamMember],
        tasks: List[Task]
    ) -> List[Dict]:
        """
        Find tasks where assignee lacks required skills
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            
        Returns:
            List of skill mismatch proposals
        """
        proposals = []
        
        for task in tasks:
            if task.status == 'Done' or not task.labels:
                continue
            
            # Get assignees
            assignees = []
            if task.raci_responsible:
                assignees.extend([m for m in team_members if m.id in task.raci_responsible])
            if task.raci_accountable:
                assignee = next((m for m in team_members if m.id == task.raci_accountable), None)
                if assignee and assignee not in assignees:
                    assignees.append(assignee)
            
            # Check skills match
            task_requirements = set(label.lower() for label in task.labels)
            
            for assignee in assignees:
                member_skills = set(skill.lower() for skill in (assignee.skills or []))
                
                if member_skills:
                    # Calculate match
                    intersection = len(task_requirements.intersection(member_skills))
                    match_score = intersection / len(task_requirements) if task_requirements else 1.0
                    
                    if match_score < self.SKILL_MATCH_THRESHOLD:
                        # Find better match
                        better_candidates = []
                        for candidate in team_members:
                            if candidate.id == assignee.id:
                                continue
                            
                            cand_skills = set(skill.lower() for skill in (candidate.skills or []))
                            cand_intersection = len(task_requirements.intersection(cand_skills))
                            cand_match = cand_intersection / len(task_requirements) if task_requirements else 0
                            
                            if cand_match > match_score + 0.2:  # At least 20% better
                                better_candidates.append((candidate, cand_match))
                        
                        if better_candidates:
                            # Sort by match score
                            better_candidates.sort(key=lambda x: x[1], reverse=True)
                            best_candidate, best_match = better_candidates[0]
                            
                            # Calculate workloads
                            task_sp = task.story_points or 0
                            assignee_tasks = [t for t in tasks if t.status != 'Done' and (
                                (t.raci_responsible and assignee.id in t.raci_responsible) or
                                t.raci_accountable == assignee.id
                            )]
                            assignee_sp = sum(t.story_points or 0 for t in assignee_tasks)
                            assignee_workload_pct = (assignee_sp / assignee.max_story_points) * 100 if assignee.max_story_points else 0
                            
                            candidate_tasks = [t for t in tasks if t.status != 'Done' and (
                                (t.raci_responsible and best_candidate.id in t.raci_responsible) or
                                t.raci_accountable == best_candidate.id
                            )]
                            candidate_sp = sum(t.story_points or 0 for t in candidate_tasks)
                            candidate_workload_pct = (candidate_sp / best_candidate.max_story_points) * 100 if best_candidate.max_story_points else 0
                            new_candidate_workload_pct = ((candidate_sp + task_sp) / best_candidate.max_story_points) * 100 if best_candidate.max_story_points else 0
                            
                            severity = 'important' if task.priority.lower() in ['high', 'critical'] else 'recommended'
                            
                            proposals.append({
                                'id': f"skill-mismatch-{task.id}-{assignee.id}-{uuid.uuid4().hex[:8]}",
                                'type': 'skill_mismatch',
                                'severity': severity,
                                'category': 'resources',
                                'title': f"Skill mismatch: Reassign '{task.name}' to {best_candidate.name}",
                                'description': f"Current assignee lacks required skills",
                                'reason': f"{assignee.name} has {round(match_score*100)}% skills match for '{task.name}'. {best_candidate.name} has {round(best_match*100)}% match.",
                                'score': 75,
                                'taskName': task.name,
                                'taskSp': task_sp,
                                'impact': {
                                    'fromMember': assignee.name,
                                    'toMember': best_candidate.name,
                                    'fromWorkload': round(assignee_workload_pct, 1),
                                    'toWorkload': round(new_candidate_workload_pct, 1),
                                    'taskSP': task_sp,
                                    'currentMatch': f"{round(match_score*100)}%",
                                    'newMatch': f"{round(best_match*100)}%",
                                    'requiredSkills': list(task_requirements),
                                    'affectedMembers': [assignee.id, best_candidate.id],
                                    'riskChange': -0.5,
                                    'balanceChange': 2
                                },
                                'action': {
                                    'type': 'reassign',
                                    'taskId': task.id,
                                    'fromMemberId': assignee.id,
                                    'toMemberId': best_candidate.id
                                }
                            })
        
        return proposals
    
    def find_idle_resources(
        self,
        team_members: List[TeamMember],
        tasks: List[Task]
    ) -> List[Dict]:
        """
        Find team members with very low workload
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            
        Returns:
            List of idle resource proposals
        """
        proposals = []
        
        # Find unassigned tasks
        unassigned_tasks = [
            t for t in tasks if t.status != 'Done' and
            not t.raci_responsible and not t.raci_accountable
        ]
        
        for member in team_members:
            # Calculate workload
            member_tasks = [
                t for t in tasks if t.status != 'Done' and (
                    (t.raci_responsible and member.id in t.raci_responsible) or
                    t.raci_accountable == member.id
                )
            ]
            
            total_sp = sum(t.story_points or 0 for t in member_tasks)
            workload_pct = (total_sp / member.max_story_points) * 100
            
            if workload_pct < 40 and unassigned_tasks:  # Less than 40% utilized
                # Suggest assigning unassigned tasks
                for task in unassigned_tasks[:2]:  # Suggest top 2
                    task_sp = task.story_points or 0
                    new_workload = round(workload_pct + (task_sp / member.max_story_points * 100), 1)
                    
                    proposals.append({
                        'id': f"idle-resource-{member.id}-{task.id}-{uuid.uuid4().hex[:8]}",
                        'type': 'idle_resource',
                        'severity': 'recommended',
                        'category': 'resources',
                        'title': f"Utilize idle resource: Assign '{task.name}' to {member.name}",
                        'description': f"{member.name} has low workload ({round(workload_pct, 1)}%)",
                        'reason': f"{member.name} is underutilized at {round(workload_pct, 1)}% capacity. Can take on more work.",
                        'score': 65,
                        'taskName': task.name,
                        'taskSp': task_sp,
                        'impact': {
                            'toMember': member.name,
                            'currentWorkload': round(workload_pct, 1),
                            'toWorkload': new_workload,
                            'taskSP': task_sp,
                            'workloadChange': new_workload - workload_pct,
                            'balanceChange': 2,
                            'affectedMembers': [member.id]
                        },
                        'action': {
                            'type': 'assign_task',
                            'taskId': task.id,
                            'toMemberId': member.id
                        }
                    })
        
        return proposals

