"""
Sprint Analyzer Service
Analyzes sprint capacity and suggests task reallocation
"""
from app.models.sprint import Sprint
from app.models.task import Task
from app.models.team_member import TeamMember
from app.models.project import Project
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class SprintAnalyzerService:
    """Service for analyzing sprint capacity and task allocation"""
    
    def __init__(self):
        pass
    
    def analyze_sprint_capacity(
        self, 
        sprint: Sprint, 
        tasks: List[Task],
        team_members: List[TeamMember]
    ) -> Dict:
        """
        Analyze capacity and utilization of a sprint
        
        Args:
            sprint: Sprint object
            tasks: Tasks assigned to this sprint
            team_members: Team members in the project
            
        Returns:
            Dict with capacity analysis
        """
        # Filter tasks for this sprint (Sprint Commitment - includes Done tasks)
        sprint_tasks = [t for t in tasks if t.sprint_id == sprint.id]
        
        # Calculate total story points (all tasks in sprint)
        total_sp = sum(task.story_points or 0 for task in sprint_tasks)
        
        # Calculate remaining work (only incomplete tasks)
        incomplete_tasks = [t for t in sprint_tasks if t.status != 'Done']
        remaining_sp = sum(task.story_points or 0 for task in incomplete_tasks)
        
        # Calculate team capacity
        team_capacity = sum(member.max_story_points for member in team_members)
        
        # Calculate utilization based on committed work (Sprint Commitment)
        utilization_percentage = (total_sp / team_capacity * 100) if team_capacity > 0 else 0
        
        # Calculate remaining capacity
        remaining_capacity = max(0, team_capacity - total_sp)
        
        # Determine status
        if utilization_percentage > 100:
            status = 'overloaded'
        elif utilization_percentage > 85:
            status = 'at_capacity'
        elif utilization_percentage > 50:
            status = 'healthy'
        else:
            status = 'underutilized'
        
        return {
            'sprint_id': sprint.id,
            'sprint_name': sprint.name,
            'total_sp': total_sp,
            'team_capacity': team_capacity,
            'remaining_capacity': remaining_capacity,
            'utilization_percentage': round(utilization_percentage, 1),
            'status': status,
            'task_count': len(sprint_tasks),
            'can_accept_more': remaining_capacity > 0
        }
    
    def analyze_all_sprints(
        self,
        sprints: List[Sprint],
        tasks: List[Task],
        team_members: List[TeamMember]
    ) -> Dict:
        """
        Analyze all sprints in a project
        
        Returns:
            Dict with analysis of all sprints
        """
        sprint_analyses = []
        
        for sprint in sprints:
            if sprint.status != 'completed':  # Only analyze active/planned sprints
                analysis = self.analyze_sprint_capacity(sprint, tasks, team_members)
                sprint_analyses.append(analysis)
        
        # Sort by status priority (overloaded first, then underutilized)
        priority_map = {'overloaded': 0, 'at_capacity': 1, 'healthy': 2, 'underutilized': 3}
        sprint_analyses.sort(key=lambda x: priority_map.get(x['status'], 4))
        
        return {
            'sprints': sprint_analyses,
            'total_sprints': len(sprint_analyses),
            'overloaded_count': sum(1 for s in sprint_analyses if s['status'] == 'overloaded'),
            'underutilized_count': sum(1 for s in sprint_analyses if s['status'] == 'underutilized')
        }
    
    def suggest_sprint_reallocation(
        self,
        sprints: List[Sprint],
        tasks: List[Task],
        team_members: List[TeamMember]
    ) -> List[Dict]:
        """
        Suggest moving tasks between sprints to balance capacity
        
        Returns:
            List of reallocation proposals
        """
        proposals = []
        
        # Analyze all sprints
        analysis = self.analyze_all_sprints(sprints, tasks, team_members)
        sprint_data = {s['sprint_id']: s for s in analysis['sprints']}
        
        # Find overloaded and underutilized sprints
        overloaded = [s for s in analysis['sprints'] if s['status'] == 'overloaded']
        underutilized = [s for s in analysis['sprints'] if s['remaining_capacity'] > 5]
        
        if not overloaded or not underutilized:
            return proposals
        
        # Try to move tasks from overloaded to underutilized sprints
        for overloaded_sprint in overloaded:
            sprint_id = overloaded_sprint['sprint_id']
            # Sprint Commitment - includes all tasks
            sprint_tasks = [t for t in tasks if t.sprint_id == sprint_id]
            
            # Sort tasks by story points (move smaller tasks first for easier fit)
            sprint_tasks.sort(key=lambda t: t.story_points or 0)
            
            for task in sprint_tasks:
                task_sp = task.story_points or 0
                if task_sp == 0:
                    continue
                
                # Find a suitable target sprint
                for target_sprint in underutilized:
                    if target_sprint['sprint_id'] == sprint_id:
                        continue
                    
                    if target_sprint['remaining_capacity'] >= task_sp:
                        # Create proposal
                        proposals.append({
                            'id': f"sprint-move-{task.id}-{uuid.uuid4().hex[:8]}",
                            'type': 'sprint_move',
                            'severity': 'important',
                            'category': 'timeline',
                            'title': f"Sprint reallocation: Move '{task.name}' to {target_sprint['sprint_name']}",
                            'description': f"Rebalance sprint workload by moving task to less loaded sprint",
                            'reason': f"Sprint '{overloaded_sprint['sprint_name']}' is overloaded ({overloaded_sprint['utilization_percentage']}% utilized)",
                            'score': 75,
                            'taskId': task.id,
                            'taskName': task.name,
                            'taskSp': task_sp,
                            'fromSprintId': sprint_id,
                            'fromSprintName': overloaded_sprint['sprint_name'],
                            'toSprintId': target_sprint['sprint_id'],
                            'toSprintName': target_sprint['sprint_name'],
                            'impact': {
                                'fromSprintNewUtilization': round(
                                    (overloaded_sprint['total_sp'] - task_sp) / overloaded_sprint['team_capacity'] * 100, 1
                                ),
                                'toSprintNewUtilization': round(
                                    (target_sprint['team_capacity'] - target_sprint['remaining_capacity'] + task_sp) / target_sprint['team_capacity'] * 100, 1
                                ),
                                'taskSP': task_sp,
                                'balanceChange': 3,
                                'affectedMembers': []
                            },
                            'action': {
                                'type': 'sprint_move',
                                'taskId': task.id,
                                'toSprintId': target_sprint['sprint_id']
                            }
                        })
                        
                        # Update target sprint remaining capacity for next iteration
                        target_sprint['remaining_capacity'] -= task_sp
                        break
        
        return proposals
    
    def calculate_project_timeline(
        self,
        sprints: List[Sprint],
        tasks: List[Task],
        team_members: List[TeamMember]
    ) -> Dict:
        """
        Calculate overall project timeline based on sprint allocations
        """
        if not sprints:
            return {'total_duration_days': 0, 'sprints_needed': 0}
        
        # Sort sprints by date
        sorted_sprints = sorted(
            [s for s in sprints if s.start_date and s.end_date],
            key=lambda s: s.start_date
        )
        
        if not sorted_sprints:
            return {'total_duration_days': 0, 'sprints_needed': len(sprints)}
        
        # Calculate total duration
        first_sprint = sorted_sprints[0]
        last_sprint = sorted_sprints[-1]
        
        if isinstance(first_sprint.start_date, str):
            start_date = datetime.fromisoformat(first_sprint.start_date.replace('Z', '+00:00'))
        else:
            start_date = first_sprint.start_date
        
        if isinstance(last_sprint.end_date, str):
            end_date = datetime.fromisoformat(last_sprint.end_date.replace('Z', '+00:00'))
        else:
            end_date = last_sprint.end_date
        
        duration_days = (end_date - start_date).days
        
        # Calculate total workload
        total_sp = sum(task.story_points or 0 for task in tasks if task.status != 'Done')
        team_capacity_per_sprint = sum(member.max_story_points for member in team_members)
        
        sprints_needed = (total_sp / team_capacity_per_sprint) if team_capacity_per_sprint > 0 else 0
        
        return {
            'total_duration_days': duration_days,
            'sprints_needed': int(sprints_needed) + 1,
            'total_sp': total_sp,
            'team_capacity_per_sprint': team_capacity_per_sprint,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }

