"""
Dependency Optimizer Service
Analyzes dependencies and suggests parallel work opportunities
"""
from app.models.task import Task
from app.models.sprint import Sprint
from typing import Dict, List, Set
import uuid


class DependencyOptimizerService:
    """Service for optimizing task dependencies and finding parallelization opportunities"""
    
    def __init__(self):
        pass
    
    def find_parallel_opportunities(self, tasks: List[Task]) -> List[Dict]:
        """
        Find tasks that could run in parallel (no actual dependency)
        
        Args:
            tasks: List of tasks
            
        Returns:
            List of proposals for removing unnecessary dependencies
        """
        proposals = []
        
        for task in tasks:
            if task.status == 'Done' or not task.dependencies:
                continue
            
            # Check each dependency
            for dep_id in task.dependencies:
                dep_task = next((t for t in tasks if t.id == dep_id), None)
                if not dep_task or dep_task.status == 'Done':
                    continue
                
                # Check if dependency is really necessary
                # Heuristics: if tasks have different types and no shared resources
                if self._can_run_parallel(task, dep_task, tasks):
                    time_savings = self._estimate_time_savings(task, dep_task)
                    
                    proposals.append({
                        'id': f"parallel-{task.id}-{dep_id}-{uuid.uuid4().hex[:8]}",
                        'type': 'parallel_opportunity',
                        'severity': 'recommended',
                        'category': 'timeline',
                        'title': f"Enable parallel work: '{task.name}' and '{dep_task.name}'",
                        'description': f"These tasks can potentially run in parallel",
                        'reason': f"Tasks '{task.name}' and '{dep_task.name}' appear to have no true dependency. Running in parallel could save {time_savings} days.",
                        'score': 70,
                        'taskName': task.name,
                        'taskSp': task.story_points or 0,
                        'impact': {
                            'task1': task.name,
                            'task2': dep_task.name,
                            'task1SP': task.story_points or 0,
                            'task2SP': dep_task.story_points or 0,
                            'potentialTimeSavings': time_savings,
                            'timeSavingsDays': time_savings,
                            'durationChange': -time_savings,
                            'riskLevel': 'low',
                            'riskChange': -0.5,
                            'affectedMembers': []
                        },
                        'action': {
                            'type': 'remove_dependency',
                            'taskId': task.id,
                            'removeDependency': dep_id
                        }
                    })
        
        return proposals
    
    def find_cross_sprint_dependencies(
        self,
        tasks: List[Task],
        sprints: List[Sprint]
    ) -> List[Dict]:
        """
        Find dependencies between tasks in different sprints
        
        Args:
            tasks: List of tasks
            sprints: List of sprints
            
        Returns:
            List of proposals for fixing cross-sprint dependencies
        """
        proposals = []
        
        for task in tasks:
            if task.status == 'Done' or not task.dependencies or not task.sprint_id:
                continue
            
            for dep_id in task.dependencies:
                dep_task = next((t for t in tasks if t.id == dep_id), None)
                if not dep_task or not dep_task.sprint_id:
                    continue
                
                # Check if in different sprints
                if task.sprint_id != dep_task.sprint_id:
                    # Get sprint info
                    task_sprint = next((s for s in sprints if s.id == task.sprint_id), None)
                    dep_sprint = next((s for s in sprints if s.id == dep_task.sprint_id), None)
                    
                    if task_sprint and dep_sprint:
                        # Check sprint order
                        task_sprint_date = task_sprint.start_date
                        dep_sprint_date = dep_sprint.start_date
                        
                        # If dependent task is in later sprint, suggest moving
                        if dep_sprint_date > task_sprint_date:
                            proposals.append({
                                'id': f"cross-sprint-{task.id}-{dep_id}-{uuid.uuid4().hex[:8]}",
                                'type': 'cross_sprint_dep',
                                'severity': 'important',
                                'category': 'quality',
                                'title': f"Fix cross-sprint dependency: Move '{task.name}'",
                                'description': f"Task depends on another task in a later sprint",
                                'reason': f"Task '{task.name}' (Sprint: {task_sprint.name}) depends on '{dep_task.name}' (Sprint: {dep_sprint.name}), which is scheduled later. This creates planning issues.",
                                'score': 80,
                                'taskId': task.id,
                                'taskName': task.name,
                                'taskSp': task.story_points or 0,
                                'fromSprintId': task.sprint_id,
                                'fromSprintName': task_sprint.name,
                                'toSprintId': dep_sprint.id,
                                'toSprintName': dep_sprint.name,
                                'impact': {
                                    'task': task.name,
                                    'taskSP': task.story_points or 0,
                                    'dependentTask': dep_task.name,
                                    'taskSprint': task_sprint.name,
                                    'depSprint': dep_sprint.name,
                                    'issue': 'Dependency in wrong order',
                                    'riskChange': -1,
                                    'balanceChange': 2,
                                    'affectedMembers': []
                                },
                                'action': {
                                    'type': 'sprint_move',
                                    'taskId': task.id,
                                    'toSprintId': dep_sprint.id
                                }
                            })
        
        return proposals
    
    def _can_run_parallel(self, task1: Task, task2: Task, all_tasks: List[Task]) -> bool:
        """
        Check if two tasks can run in parallel
        
        Criteria:
        - Different types (feature vs bug)
        - No shared assignees
        - Not in same critical path
        """
        # Different types is a good indicator
        if task1.type != task2.type:
            # Check if they have different assignees
            task1_assignees = set(task1.raci_responsible or [])
            if task1.raci_accountable:
                task1_assignees.add(task1.raci_accountable)
            
            task2_assignees = set(task2.raci_responsible or [])
            if task2.raci_accountable:
                task2_assignees.add(task2.raci_accountable)
            
            # If no shared assignees, can probably run parallel
            if not task1_assignees.intersection(task2_assignees):
                return True
        
        return False
    
    def _estimate_time_savings(self, task1: Task, task2: Task) -> float:
        """Estimate time savings from parallel execution"""
        task1_duration = task1.pert_expected or (task1.story_points or 0) * 0.5
        task2_duration = task2.pert_expected or (task2.story_points or 0) * 0.5
        
        # Time savings is the smaller of the two durations
        return round(min(task1_duration, task2_duration), 1)

