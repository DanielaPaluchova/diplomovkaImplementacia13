"""
Task Merger Service
Logic for detecting and merging small similar tasks
"""
from app.models.task import Task
from typing import Dict, List, Optional
import uuid


class TaskMergerService:
    """Service for merging small similar tasks into larger ones"""
    
    MERGE_THRESHOLD_MIN = 1  # Minimum SP to consider for merge
    MERGE_THRESHOLD_MAX = 3  # Maximum SP to consider for merge
    MIN_TASKS_FOR_MERGE = 2  # At least 2 tasks needed
    
    def __init__(self):
        pass
    
    def should_merge_tasks(self, tasks: List[Task]) -> bool:
        """
        Determine if tasks should be merged
        
        Args:
            tasks: List of tasks to evaluate
            
        Returns:
            True if tasks are good candidates for merging
        """
        if len(tasks) < self.MIN_TASKS_FOR_MERGE:
            return False
        
        # All tasks should be small
        for task in tasks:
            sp = task.story_points or 0
            if sp < self.MERGE_THRESHOLD_MIN or sp > self.MERGE_THRESHOLD_MAX:
                return False
        
        # All tasks should be incomplete
        if any(task.status == 'Done' for task in tasks):
            return False
        
        return True
    
    def find_similar_tasks(self, tasks: List[Task]) -> List[List[Task]]:
        """
        Find groups of similar tasks that could be merged
        
        Similarity criteria:
        - Same type (feature, bug, task)
        - Same sprint
        - Similar labels
        - Assigned to same person
        - Small story points (1-3)
        
        Returns:
            List of task groups that could be merged
        """
        groups = []
        
        # Filter to small tasks only
        small_tasks = [
            t for t in tasks 
            if t.status != 'Done' and 
            self.MERGE_THRESHOLD_MIN <= (t.story_points or 0) <= self.MERGE_THRESHOLD_MAX
        ]
        
        # Group by sprint, type, and assignee
        grouped_by_criteria: Dict[tuple, List[Task]] = {}
        
        for task in small_tasks:
            # Get primary assignee
            assignee = None
            if task.raci_responsible and len(task.raci_responsible) > 0:
                assignee = task.raci_responsible[0]
            elif task.raci_accountable:
                assignee = task.raci_accountable
            
            # Create grouping key
            key = (
                task.sprint_id or 0,
                task.type or 'task',
                assignee or 0
            )
            
            if key not in grouped_by_criteria:
                grouped_by_criteria[key] = []
            grouped_by_criteria[key].append(task)
        
        # Find groups with 2+ tasks
        for key, task_group in grouped_by_criteria.items():
            if len(task_group) >= self.MIN_TASKS_FOR_MERGE:
                # Further filter by label similarity
                similar_groups = self._group_by_label_similarity(task_group)
                for group in similar_groups:
                    if len(group) >= self.MIN_TASKS_FOR_MERGE:
                        groups.append(group)
        
        return groups
    
    def _group_by_label_similarity(self, tasks: List[Task]) -> List[List[Task]]:
        """Group tasks by label similarity"""
        if not tasks:
            return []
        
        groups = []
        remaining = tasks[:]
        
        while remaining:
            current_task = remaining.pop(0)
            current_labels = set(current_task.labels or [])
            
            # Find similar tasks
            similar = [current_task]
            still_remaining = []
            
            for task in remaining:
                task_labels = set(task.labels or [])
                
                # Calculate similarity (Jaccard index)
                if current_labels or task_labels:
                    intersection = len(current_labels.intersection(task_labels))
                    union = len(current_labels.union(task_labels))
                    similarity = intersection / union if union > 0 else 0
                    
                    if similarity > 0.5:  # 50% similarity threshold
                        similar.append(task)
                    else:
                        still_remaining.append(task)
                else:
                    # Both have no labels - consider similar
                    similar.append(task)
            
            remaining = still_remaining
            if len(similar) >= self.MIN_TASKS_FOR_MERGE:
                groups.append(similar)
        
        return groups
    
    def suggest_merge(self, tasks: List[Task]) -> Dict:
        """
        Suggest how to merge tasks
        
        Args:
            tasks: List of tasks to merge
            
        Returns:
            Dict with merge proposal
        """
        if not self.should_merge_tasks(tasks):
            return {
                'should_merge': False,
                'reason': f'Tasks do not meet merge criteria'
            }
        
        # Calculate merged task properties
        total_sp = sum(task.story_points or 0 for task in tasks)
        
        # Combine names
        task_names = [t.name for t in tasks]
        merged_name = self._create_merged_name(task_names)
        
        # Combine descriptions
        merged_description = self._create_merged_description(tasks)
        
        # Get common properties
        task_type = tasks[0].type
        priority = max([t.priority for t in tasks], key=lambda p: {'high': 3, 'medium': 2, 'low': 1}.get(p, 0))
        sprint_id = tasks[0].sprint_id
        
        # Combine labels
        all_labels = set()
        for task in tasks:
            if task.labels:
                all_labels.update(task.labels)
        
        # Get RACI from first task
        raci_responsible = tasks[0].raci_responsible or []
        raci_accountable = tasks[0].raci_accountable
        
        # Calculate merged PERT
        merged_pert = self._calculate_merged_pert(tasks)
        
        return {
            'should_merge': True,
            'reason': f'Merging {len(tasks)} small similar tasks into one larger task improves organization',
            'original_task_ids': [t.id for t in tasks],
            'original_total_sp': total_sp,
            'num_tasks': len(tasks),
            'merged_task': {
                'name': merged_name,
                'title': merged_name,
                'description': merged_description,
                'story_points': total_sp,
                'type': task_type,
                'priority': priority,
                'sprint_id': sprint_id,
                'labels': list(all_labels),
                'raci_responsible': raci_responsible,
                'raci_accountable': raci_accountable,
                'pert': merged_pert,
                'status': 'To Do'
            },
            'estimated_improvement': {
                'organization': '+25%',
                'tracking_overhead': f'-{len(tasks)-1} tasks to track',
                'context_switching': '-20%'
            }
        }
    
    def _create_merged_name(self, names: List[str]) -> str:
        """Create a name for merged task"""
        if len(names) <= 2:
            return f"{names[0]} + {names[1]}"
        
        # Find common prefix/theme
        common_words = set(names[0].lower().split())
        for name in names[1:]:
            common_words.intersection_update(set(name.lower().split()))
        
        if common_words:
            theme = ' '.join(sorted(common_words)[:2]).title()
            return f"{theme} - Combined Task ({len(names)} items)"
        
        return f"Combined Task: {names[0][:30]}... ({len(names)} items)"
    
    def _create_merged_description(self, tasks: List[Task]) -> str:
        """Create description for merged task"""
        desc_parts = [f"This task combines {len(tasks)} related items:\n"]
        
        for i, task in enumerate(tasks, 1):
            desc_parts.append(f"\n{i}. {task.name}")
            if task.description:
                desc_parts.append(f"   - {task.description[:100]}")
        
        return ''.join(desc_parts)
    
    def _calculate_merged_pert(self, tasks: List[Task]) -> Optional[Dict]:
        """Calculate PERT estimates for merged task"""
        # Sum up PERT times if available
        has_pert = any(t.pert_optimistic is not None for t in tasks)
        
        if not has_pert:
            return None
        
        total_opt = sum(t.pert_optimistic or 0 for t in tasks)
        total_most = sum(t.pert_most_likely or 0 for t in tasks)
        total_pess = sum(t.pert_pessimistic or 0 for t in tasks)
        
        # Add small overhead for context switching (5%)
        overhead = 1.05
        
        return {
            'optimistic': round(total_opt * overhead, 1),
            'mostLikely': round(total_most * overhead, 1),
            'pessimistic': round(total_pess * overhead, 1)
        }
    
    def create_merge_proposals(self, tasks: List[Task]) -> List[Dict]:
        """
        Analyze all tasks and create merge proposals
        
        Args:
            tasks: List of tasks to analyze
            
        Returns:
            List of merge proposals
        """
        proposals = []
        
        # Find groups of similar tasks
        similar_groups = self.find_similar_tasks(tasks)
        
        for group in similar_groups:
            merge_suggestion = self.suggest_merge(group)
            if merge_suggestion.get('should_merge'):
                total_sp = sum(t.story_points or 0 for t in group)
                merged_sp = merge_suggestion.get('story_points', total_sp)
                
                proposals.append({
                    'id': f"merge-{'-'.join(str(t.id) for t in group)}-{uuid.uuid4().hex[:8]}",
                    'type': 'merge',
                    'severity': 'recommended',
                    'category': 'quality',
                    'title': f"Merge {len(group)} similar small tasks",
                    'description': f"Combine {len(group)} related tasks into one for better efficiency",
                    'reason': merge_suggestion.get('reason', f'Tasks are small and similar, better managed as one'),
                    'score': 70,
                    'taskIds': [t.id for t in group],
                    'taskNames': [t.name for t in group],
                    'proposal': merge_suggestion,
                    'impact': {
                        'taskCount': len(group),
                        'totalSP': total_sp,
                        'mergedSP': merged_sp,
                        'spSavings': total_sp - merged_sp if merged_sp < total_sp else 0,
                        'balanceChange': 2,
                        'riskChange': -0.5,
                        'affectedMembers': []
                    },
                    'action': {
                        'type': 'merge',
                        'originalTaskIds': [t.id for t in group],
                        'mergedTask': merge_suggestion.get('merged_task', {})
                    }
                })
        
        return proposals

