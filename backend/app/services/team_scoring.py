"""
Team Scoring Service
Scoring algorithm for team member assignment based on multiple factors
"""
from app.models.team_member import TeamMember
from app.models.task import Task
from typing import List, Dict, Optional


class TeamScoringService:
    """Service for scoring team members for task assignments"""
    
    # Scoring weights
    WEIGHT_WORKLOAD = 0.4    # 40% - lower workload = higher score
    WEIGHT_SKILLS = 0.3      # 30% - skills match with task
    WEIGHT_HISTORY = 0.2     # 20% - RACI history on similar tasks
    WEIGHT_AVAILABILITY = 0.1 # 10% - online status
    
    def __init__(self):
        pass
    
    def score_member_for_task(
        self, 
        member: TeamMember, 
        task_requirements: Dict,
        all_tasks: List[Task],
        member_current_sp: int
    ) -> Dict:
        """
        Score a team member for a specific task
        
        Args:
            member: TeamMember object
            task_requirements: Dict with 'labels', 'type', 'priority', etc.
            all_tasks: List of all tasks (for history analysis)
            member_current_sp: Current story points assigned to member
            
        Returns:
            Dict with score breakdown and final score
        """
        workload_score = self._calculate_workload_score(member, member_current_sp)
        skills_score = self._calculate_skills_score(member, task_requirements)
        history_score = self._calculate_history_score(member, task_requirements, all_tasks)
        availability_score = self._calculate_availability_score(member)
        
        final_score = (
            self.WEIGHT_WORKLOAD * workload_score +
            self.WEIGHT_SKILLS * skills_score +
            self.WEIGHT_HISTORY * history_score +
            self.WEIGHT_AVAILABILITY * availability_score
        )
        
        return {
            'member_id': member.id,
            'member_name': member.name,
            'final_score': round(final_score, 2),
            'breakdown': {
                'workload': round(workload_score, 2),
                'skills': round(skills_score, 2),
                'history': round(history_score, 2),
                'availability': round(availability_score, 2)
            },
            'current_sp': member_current_sp,
            'max_sp': member.max_story_points,
            'workload_percentage': round((member_current_sp / member.max_story_points) * 100, 1)
        }
    
    def _calculate_workload_score(self, member: TeamMember, current_sp: int) -> float:
        """
        Calculate workload score (0-100)
        Lower workload = higher score
        """
        max_sp = member.max_story_points
        workload_percentage = (current_sp / max_sp) * 100
        
        # Inverse relationship: 0% workload = 100 score, 100% workload = 0 score
        # Add small bonus if workload is very low (< 50%)
        if workload_percentage < 50:
            score = 100 - workload_percentage + 10  # Bonus points
        else:
            score = 100 - workload_percentage
        
        return max(0, min(100, score))  # Clamp between 0-100
    
    def _calculate_skills_score(self, member: TeamMember, task_requirements: Dict) -> float:
        """
        Calculate skills match score (0-100)
        Matches member skills with task labels/type
        """
        member_skills = set(skill.lower() for skill in (member.skills or []))
        
        if not member_skills:
            return 50  # Neutral score if no skills defined
        
        # Extract requirements from task
        task_labels = set(label.lower() for label in (task_requirements.get('labels') or []))
        task_type = task_requirements.get('type', '').lower()
        
        # Add task type to requirements
        if task_type:
            task_labels.add(task_type)
        
        if not task_labels:
            return 50  # Neutral score if no requirements
        
        # Calculate match percentage
        matches = member_skills.intersection(task_labels)
        match_percentage = (len(matches) / len(task_labels)) * 100
        
        # Bonus for exact matches or many skills
        if len(matches) >= len(task_labels):
            match_percentage += 20  # All requirements met
        elif len(matches) > 0:
            match_percentage += 10  # Some requirements met
        
        return min(100, match_percentage)
    
    def _calculate_history_score(
        self, 
        member: TeamMember, 
        task_requirements: Dict,
        all_tasks: List[Task]
    ) -> float:
        """
        Calculate history score based on similar tasks completed (0-100)
        """
        task_type = task_requirements.get('type', '').lower()
        task_labels = set(label.lower() for label in (task_requirements.get('labels') or []))
        
        # Find tasks where member was responsible or accountable
        member_tasks = [
            task for task in all_tasks
            if (task.raci_responsible and member.id in task.raci_responsible) or
               task.raci_accountable == member.id
        ]
        
        if not member_tasks:
            return 30  # Low score if no history
        
        # Find similar tasks
        similar_tasks = []
        for task in member_tasks:
            # Check type match
            if task.type and task.type.lower() == task_type:
                similar_tasks.append(task)
                continue
            
            # Check label match
            if task.labels:
                task_task_labels = set(label.lower() for label in task.labels)
                if task_labels and task_task_labels.intersection(task_labels):
                    similar_tasks.append(task)
        
        # Calculate score based on experience
        total_tasks = len(member_tasks)
        similar_count = len(similar_tasks)
        
        # Base score from total experience
        experience_score = min(50, total_tasks * 5)  # Up to 50 points from experience
        
        # Bonus from similar tasks
        if similar_count > 0:
            similarity_bonus = min(50, similar_count * 10)  # Up to 50 points from similarity
        else:
            similarity_bonus = 0
        
        return min(100, experience_score + similarity_bonus)
    
    def _calculate_availability_score(self, member: TeamMember) -> float:
        """
        Calculate availability score based on status (0-100)
        """
        status = (member.status or 'offline').lower()
        
        status_scores = {
            'online': 100,
            'away': 70,
            'busy': 50,
            'offline': 30
        }
        
        return status_scores.get(status, 50)
    
    def rank_members_for_task(
        self,
        members: List[TeamMember],
        task_requirements: Dict,
        all_tasks: List[Task],
        member_workloads: Dict[int, int]
    ) -> List[Dict]:
        """
        Rank all members for a task and return sorted by score
        
        Args:
            members: List of TeamMember objects
            task_requirements: Task requirements dict
            all_tasks: All tasks for history analysis
            member_workloads: Dict mapping member_id to current SP count
            
        Returns:
            List of score dicts sorted by final_score (highest first)
        """
        scores = []
        
        for member in members:
            current_sp = member_workloads.get(member.id, 0)
            score = self.score_member_for_task(member, task_requirements, all_tasks, current_sp)
            scores.append(score)
        
        # Sort by final score descending
        scores.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scores

