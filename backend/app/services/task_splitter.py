"""
Task Splitter Service
Logic for detecting and splitting large tasks (21+ SP)
"""
from app.models.task import Task
from typing import Dict, List, Optional
import uuid


class TaskSplitterService:
    """Service for splitting large tasks into smaller subtasks"""
    
    SPLIT_THRESHOLD = 21  # Story points threshold for splitting
    
    def __init__(self):
        pass
    
    def should_split_task(self, task: Task) -> bool:
        """
        Determine if a task should be split based on story points
        
        Args:
            task: Task object
            
        Returns:
            True if task has 21+ story points
        """
        return (task.story_points or 0) >= self.SPLIT_THRESHOLD
    
    def suggest_split(self, task: Task, num_parts: int = 2) -> Dict:
        """
        Suggest how to split a task into subtasks
        
        Args:
            task: Task object to split
            num_parts: Number of subtasks to create (2-3)
            
        Returns:
            Dict with split proposal
        """
        if not self.should_split_task(task):
            return {
                'should_split': False,
                'reason': f'Task has {task.story_points} SP, below threshold of {self.SPLIT_THRESHOLD}'
            }
        
        # Determine optimal number of parts if not specified
        story_points = task.story_points
        if num_parts is None or num_parts < 2:
            if story_points >= 34:  # Fibonacci: 34 = 13 + 13 + 8
                num_parts = 3
            else:
                num_parts = 2
        
        # Calculate split story points (try to keep them balanced)
        split_sps = self._calculate_split_story_points(story_points, num_parts)
        
        # Calculate split PERT times
        pert_splits = self._calculate_split_pert(task, num_parts)
        
        # Create subtask proposals
        subtasks = []
        for i in range(num_parts):
            subtask = {
                'name': f"{task.name} {i+1}",
                'title': f"{task.title} {i+1}" if task.title else f"{task.name} {i+1}",
                'description': task.description or '',
                'story_points': split_sps[i],
                'type': task.type,
                'priority': task.priority,
                'labels': task.labels or [],
                'complexity': task.complexity,
                'pert': pert_splits[i] if pert_splits else None,
                'status': 'To Do'
            }
            subtasks.append(subtask)
        
        return {
            'should_split': True,
            'reason': f'Task has {story_points} SP (threshold: {self.SPLIT_THRESHOLD}). Optimal split: {num_parts} parts',
            'original_task_id': task.id,
            'original_sp': story_points,
            'num_parts': num_parts,
            'subtasks': subtasks,
            'split_story_points': split_sps,
            'estimated_improvement': self._estimate_improvement(story_points, num_parts)
        }
    
    def _calculate_split_story_points(self, total_sp: int, num_parts: int) -> List[int]:
        """
        Calculate how to split story points across subtasks
        Tries to use Fibonacci numbers when possible
        """
        # Fibonacci sequence up to 34
        fib = [1, 2, 3, 5, 8, 13, 21, 34]
        
        if num_parts == 2:
            # Try to split into two Fibonacci numbers
            half = total_sp // 2
            # Find closest Fibonacci numbers that sum to total
            best_split = [half, total_sp - half]
            
            # Try to find better Fibonacci-based split
            for f1 in fib:
                f2 = total_sp - f1
                if f2 in fib and abs(f1 - f2) <= 13:  # Keep them relatively balanced
                    best_split = [f1, f2]
                    break
            
            return sorted(best_split, reverse=True)
        
        elif num_parts == 3:
            # Split into three parts (try to keep balanced)
            third = total_sp // 3
            remainder = total_sp % 3
            
            splits = [third] * 3
            # Distribute remainder
            for i in range(remainder):
                splits[i] += 1
            
            # Try to adjust to Fibonacci if close
            adjusted = []
            for sp in splits:
                closest_fib = min(fib, key=lambda x: abs(x - sp))
                if abs(closest_fib - sp) <= 2:
                    adjusted.append(closest_fib)
                else:
                    adjusted.append(sp)
            
            # Verify sum and adjust if needed
            diff = total_sp - sum(adjusted)
            if diff != 0:
                adjusted[0] += diff
            
            return sorted(adjusted, reverse=True)
        
        else:
            # Generic split for other cases
            base = total_sp // num_parts
            remainder = total_sp % num_parts
            splits = [base] * num_parts
            for i in range(remainder):
                splits[i] += 1
            return sorted(splits, reverse=True)
    
    def _calculate_split_pert(self, task: Task, num_parts: int) -> Optional[List[Dict]]:
        """
        Split PERT estimates across subtasks with uncertainty reduction
        
        Uses advanced PERT methodology:
        - Distributes duration proportionally to story points
        - Applies uncertainty reduction factor: 1 / sqrt(num_parts)
        - Smaller tasks have lower uncertainty (narrower range)
        
        Reference: NASA Program Management Guide, PMI PMBOK
        """
        if not task.pert_optimistic or not task.pert_most_likely or not task.pert_pessimistic:
            return None
        
        if not task.pert_expected or task.pert_expected == 0:
            return None
        
        # Calculate subtask story points distribution
        subtask_sps = self._calculate_split_story_points(task.story_points or num_parts, num_parts)
        total_sp = task.story_points or num_parts
        
        # Original task parameters
        original_expected = task.pert_expected
        original_range = task.pert_pessimistic - task.pert_optimistic
        
        # Uncertainty reduction factor: sqrt(N)
        # Smaller tasks have proportionally lower uncertainty
        uncertainty_reduction_factor = 1.0 / (num_parts ** 0.5)
        
        pert_splits = []
        
        for i in range(num_parts):
            # Proportional expected duration based on story points
            sp_ratio = subtask_sps[i] / total_sp
            subtask_expected = original_expected * sp_ratio
            
            # Calculate reduced uncertainty range for subtask
            # Original range scaled by SP ratio and uncertainty reduction
            subtask_range = original_range * sp_ratio * uncertainty_reduction_factor
            
            # Distribute range: 30% below expected, 70% above (realistic distribution)
            subtask_optimistic = max(0.5, subtask_expected - (subtask_range * 0.3))
            subtask_pessimistic = subtask_expected + (subtask_range * 0.7)
            
            # Most likely: closer to optimistic (40% into range from optimistic)
            subtask_most_likely = subtask_optimistic + (subtask_range * 0.4)
            
            pert_splits.append({
                'optimistic': round(subtask_optimistic, 1),
                'mostLikely': round(subtask_most_likely, 1),
                'pessimistic': round(subtask_pessimistic, 1)
            })
        
        return pert_splits
    
    def _estimate_improvement(self, original_sp: int, num_parts: int) -> Dict:
        """
        Estimate the improvement from splitting
        """
        # Smaller tasks are easier to estimate and manage
        avg_sp_after = original_sp / num_parts
        
        # Estimated benefits
        estimation_accuracy_improvement = min(30, (original_sp - self.SPLIT_THRESHOLD) * 2)
        parallelization_potential = 20 if num_parts >= 2 else 0
        risk_reduction = min(25, (original_sp - self.SPLIT_THRESHOLD) * 1.5)
        
        return {
            'estimation_accuracy': f'+{int(estimation_accuracy_improvement)}%',
            'parallelization_potential': f'+{int(parallelization_potential)}%',
            'risk_reduction': f'-{int(risk_reduction)}%',
            'average_sp_after_split': round(avg_sp_after, 1)
        }
    
    def create_split_proposals(self, tasks: List[Task]) -> List[Dict]:
        """
        Analyze all tasks and create split proposals for large ones
        
        Args:
            tasks: List of tasks to analyze
            
        Returns:
            List of split proposals
        """
        proposals = []
        
        for task in tasks:
            if self.should_split_task(task) and task.status != 'Done':
                split_suggestion = self.suggest_split(task)
                if split_suggestion.get('should_split'):
                    num_parts = split_suggestion.get('num_parts', 2)
                    original_sp = task.story_points or 0
                    avg_sp_after = original_sp / num_parts
                    
                    proposals.append({
                        'id': f"split-{task.id}-{uuid.uuid4().hex[:8]}",
                        'type': 'split',
                        'severity': 'important',
                        'category': 'quality',
                        'title': f"Split large task: '{task.name}' ({original_sp} SP)",
                        'description': f"Task is too large ({original_sp} SP). Split into {num_parts} smaller subtasks.",
                        'reason': split_suggestion.get('reason', f'Task exceeds recommended size (21+ SP)'),
                        'score': 80,
                        'taskId': task.id,
                        'taskName': task.name,
                        'taskSp': original_sp,
                        'proposal': split_suggestion,
                        'impact': {
                            'originalSP': original_sp,
                            'splitInto': num_parts,
                            'averageSP': round(avg_sp_after, 1),
                            'improvement': split_suggestion.get('estimated_improvement', {}),
                            'riskChange': -1,
                            'balanceChange': 5,
                            'affectedMembers': []
                        },
                        'action': {
                            'type': 'split',
                            'taskId': task.id,
                            'subtasks': split_suggestion.get('subtasks', [])
                        }
                    })
        
        return proposals

