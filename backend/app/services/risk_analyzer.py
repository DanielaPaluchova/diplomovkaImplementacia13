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
    
    DEADLINE_BUFFER_DAYS = 3  # Warn if less than 3 WORKING days buffer
    SKILL_MATCH_THRESHOLD = 0.3  # 30% skills match required
    
    def __init__(self):
        pass
    
    @staticmethod
    def _count_business_days(start_date: datetime, end_date: datetime) -> int:
        """
        Count business days (Mon-Fri) between two dates, excluding weekends
        Uses optimized algorithm for better performance
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of business days between dates
        """
        if start_date > end_date:
            return 0
        
        # Normalize to start of day for accurate counting
        start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate total days
        total_days = (end - start).days + 1
        
        # Calculate full weeks and remaining days
        full_weeks = total_days // 7
        remaining_days = total_days % 7
        
        # Full weeks contribute 5 business days each
        business_days = full_weeks * 5
        
        # Count business days in remaining days
        current = start + timedelta(days=full_weeks * 7)
        for _ in range(remaining_days):
            if current.weekday() < 5:  # Monday-Friday
                business_days += 1
            current += timedelta(days=1)
        
        return business_days
    
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
            
            # Calculate BUSINESS days remaining (Mon-Fri only)
            business_days_remaining = self._count_business_days(now, due_date)
            
            # Calculate estimated time needed (in working days)
            # PERT expected is already in days
            if task.pert_expected:
                estimated_days = task.pert_expected
            else:
                # Fallback: estimate 0.5 days per story point
                estimated_days = (task.story_points or 0) * 0.5
            
            buffer = business_days_remaining - estimated_days
            
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
                    'title': f"Deadline risk: '{task.name}' due in {business_days_remaining} working days",
                    'description': f"Task may miss deadline with only {round(buffer, 1)} working days buffer",
                    'reason': f"Task '{task.name}' needs {round(estimated_days, 1)} working days but deadline is in {business_days_remaining} working days (Mon-Fri). Buffer: {round(buffer, 1)} days.",
                    'score': 95 if severity == 'critical' else 85,
                    'taskName': task.name,
                    'taskSp': task.story_points or 0,
                    'impact': {
                        'daysRemaining': business_days_remaining,
                        'estimatedDays': round(estimated_days, 1),
                        'buffer': round(buffer, 1),
                        'riskLevel': severity,
                        'dueDate': due_date.isoformat(),
                        'taskSP': task.story_points or 0,
                        'durationChange': -round(time_savings, 1),
                        'riskChange': -1 if severity == 'critical' else -0.5,
                        'affectedMembers': [],
                        'isBusinessDays': True  # Flag to indicate business days calculation
                    },
                    'action': {
                        'type': 'priority_increase',
                        'taskId': task.id,
                        'newPriority': 'high',
                        'startImmediately': True
                    }
                })
        
        return proposals
    
    def _build_priority_conflict_impact(
        self,
        from_member: TeamMember,
        to_member: TeamMember,
        task_sp: float,
        from_workload_pct: float,
        from_workload_after: float,
        to_workload_before: float,
        to_workload_after: float,
        task: Task,
        skill_match_pct: float
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
            'suggestedAction': 'reassign',
            'currentWorkload': round(from_workload_pct, 1),
            'skillMatch': skill_match_pct,
            'affectedMembers': [from_member.id, to_member.id],
            'workloadChange': -((task_sp / from_member.max_story_points) * 100),
            'balanceChange': 3
        }
        
        # Add warning if recipient will be overloaded after reassignment
        if to_workload_after > 100:
            impact['recipientOverloadWarning'] = True
            impact['recipientOverloadPercent'] = round(to_workload_after, 1)
        
        return impact
    
    def _build_skill_mismatch_impact(
        self,
        from_member: TeamMember,
        to_member: TeamMember,
        task_sp: float,
        from_workload_pct: float,
        from_workload_after: float,
        to_workload_before: float,
        to_workload_after: float,
        from_skill_match: float,
        to_skill_match: float,
        task_requirements: set
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
            'currentMatch': f"{round(from_skill_match*100)}%",
            'newMatch': f"{round(to_skill_match*100)}%",
            'requiredSkills': list(task_requirements),
            'affectedMembers': [from_member.id, to_member.id],
            'riskChange': -0.5,
            'balanceChange': 2
        }
        
        # Add warning if recipient will be overloaded after reassignment
        if to_workload_after > 100:
            impact['recipientOverloadWarning'] = True
            impact['recipientOverloadPercent'] = round(to_workload_after, 1)
        
        return impact
    
    def find_priority_conflicts(
        self,
        team_members: List[TeamMember],
        tasks: List[Task],
        cross_project_workload: Dict[int, Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Find high priority tasks assigned to overloaded members
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            cross_project_workload: Optional dict of cross-project workload {member_id: {'sp': float, 'pct': float}}
            
        Returns:
            List of priority conflict proposals
        """
        proposals = []
        
        for member in team_members:
            # Get member's tasks (Sprint Commitment - includes Done tasks for workload calc)
            member_tasks = [
                t for t in tasks if (
                    t.raci_responsible and member.id in t.raci_responsible
                )
            ]
            
            # Calculate workload (use cross-project if available, otherwise current project only)
            if cross_project_workload and member.id in cross_project_workload:
                workload_pct = cross_project_workload[member.id]['pct']
                total_sp = cross_project_workload[member.id]['sp']
            else:
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
                            
                            # Find suitable candidates based on BOTH workload AND skills
                            task_requirements = set(skill.lower() for skill in (task.required_skills or []))
                            suitable_candidates = []
                            
                            for candidate in other_members:
                                cand_workload = candidate_workloads[candidate.id]
                                cand_sp = cand_workload['sp']
                                cand_pct = cand_workload['pct']
                                new_pct = ((cand_sp + task_sp) / cand_workload['max_sp']) * 100
                                
                                # CRITICAL: Don't suggest if it would overload the recipient (>100%)
                                if new_pct > 100:
                                    continue
                                
                                # Calculate skills match
                                member_skills = set(skill.lower() for skill in (candidate.skills or []))
                                if task_requirements and member_skills:
                                    intersection = len(task_requirements.intersection(member_skills))
                                    skill_match = intersection / len(task_requirements)
                                else:
                                    skill_match = 0.5  # Neutral if no skills defined
                                
                                # Combined score: prefer low workload + high skill match
                                # Workload weight: 60%, Skills weight: 40%
                                workload_score = max(0, 100 - new_pct) / 100  # 0-1, higher is better
                                combined_score = (0.6 * workload_score) + (0.4 * skill_match)
                                
                                suitable_candidates.append({
                                    'member': candidate,
                                    'current_pct': cand_pct,
                                    'new_pct': new_pct,
                                    'skill_match': skill_match,
                                    'combined_score': combined_score
                                })
                            
                            # Sort by combined score (best first)
                            suitable_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
                            
                            # Check if we have any suitable candidates
                            if not suitable_candidates:
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
                                # Use best candidate (highest combined score)
                                best = suitable_candidates[0]
                                best_member = best['member']
                                current_pct = best['current_pct']
                                new_pct = best['new_pct']
                                skill_match_pct = int(best['skill_match'] * 100)
                                
                                # Calculate workload after reassignment
                                from_workload_after = ((total_sp - task_sp) / member.max_story_points) * 100
                                
                                # Build message with skill info and warnings
                                skill_info = f" | Skill match: {skill_match_pct}%"
                                
                                # Add warning for low skill match
                                skill_warning = ""
                                if skill_match_pct < 30 and task_requirements:
                                    required_skills_list = ", ".join(sorted(task_requirements))
                                    skill_warning = f"\n\n*** SKILL MISMATCH WARNING ***\n{best_member.name} has {skill_match_pct}% skill match! Missing required skills: {required_skills_list.upper()}\nConsider training or finding alternative candidate."
                                
                                description = f"High priority task assigned to overloaded team member. Better candidate found."
                                if skill_warning:
                                    description += " However, skills mismatch detected."
                                
                                proposals.append({
                                    'id': f"priority-conflict-{task.id}-{uuid.uuid4().hex[:8]}",
                                    'type': 'priority_conflict',
                                    'severity': 'critical',
                                    'category': 'workload',
                                    'title': f"Priority conflict: Move '{task.name}' from overloaded {member.name}",
                                    'description': description,
                                    'reason': f"{member.name} is overloaded ({round(workload_pct, 1)}%) but has high-priority task '{task.name}'. Reassign to {best_member.name} ({round(current_pct, 1)}% → {round(new_pct, 1)}%){skill_info}.{skill_warning}",
                                    'score': 90,
                                    'taskName': task.name,
                                    'taskSp': task_sp,
                                    'impact': self._build_priority_conflict_impact(
                                        member, best_member, task_sp,
                                        workload_pct, from_workload_after,
                                        current_pct, new_pct,
                                        task, skill_match_pct
                                    ),
                                    'action': {
                                        'type': 'reassign',
                                        'taskId': task.id,
                                        'fromMemberId': member.id,
                                        'toMemberId': best_member.id
                                    }
                                })
        
        return proposals
    
    def find_skill_mismatches(
        self,
        team_members: List[TeamMember],
        tasks: List[Task],
        cross_project_workload: Dict[int, Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Find tasks where assignee lacks required skills
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            cross_project_workload: Optional dict of cross-project workload {member_id: {'sp': float, 'pct': float}}
            
        Returns:
            List of skill mismatch proposals
        """
        proposals = []
        
        for task in tasks:
            if task.status == 'Done':
                continue
            
            # Get assignees - ONLY check Responsible (who does the work)
            # Accountable (who approves) doesn't need technical skills
            assignees = []
            if task.raci_responsible:
                assignees.extend([m for m in team_members if m.id in task.raci_responsible])
            
            # Check skills match using required_skills (not labels)
            task_requirements = set(skill.lower() for skill in (task.required_skills or []))
            
            # Skip if task has no required skills
            if not task_requirements:
                continue
            
            for assignee in assignees:
                member_skills = set(skill.lower() for skill in (assignee.skills or []))
                
                # Calculate match (if member has NO skills, match is 0)
                intersection = len(task_requirements.intersection(member_skills))
                match_score = intersection / len(task_requirements) if task_requirements else 1.0
                
                # Only check if task has requirements and match is below threshold
                if task_requirements and match_score < self.SKILL_MATCH_THRESHOLD:
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
                    
                    # Always create proposal (even without better candidates)
                    if better_candidates:
                        # Sort by match score
                        better_candidates.sort(key=lambda x: x[1], reverse=True)
                        best_candidate, best_match = better_candidates[0]
                        
                        # Calculate workloads (use cross-project if available)
                        task_sp = task.story_points or 0
                        
                        if cross_project_workload and assignee.id in cross_project_workload:
                            assignee_sp = cross_project_workload[assignee.id]['sp']
                            assignee_workload_pct = cross_project_workload[assignee.id]['pct']
                        else:
                            # Sprint Commitment - includes Done tasks for workload calc
                            assignee_tasks = [t for t in tasks if (
                                t.raci_responsible and assignee.id in t.raci_responsible
                            )]
                            assignee_sp = sum(t.story_points or 0 for t in assignee_tasks)
                            assignee_workload_pct = (assignee_sp / assignee.max_story_points) * 100 if assignee.max_story_points else 0
                        
                        if cross_project_workload and best_candidate.id in cross_project_workload:
                            candidate_sp = cross_project_workload[best_candidate.id]['sp']
                            candidate_workload_pct = cross_project_workload[best_candidate.id]['pct']
                        else:
                            # Sprint Commitment - includes Done tasks for workload calc
                            candidate_tasks = [t for t in tasks if (
                                t.raci_responsible and best_candidate.id in t.raci_responsible
                            )]
                            candidate_sp = sum(t.story_points or 0 for t in candidate_tasks)
                            candidate_workload_pct = (candidate_sp / best_candidate.max_story_points) * 100 if best_candidate.max_story_points else 0
                        
                        new_candidate_workload_pct = ((candidate_sp + task_sp) / best_candidate.max_story_points) * 100 if best_candidate.max_story_points else 0
                        assignee_workload_after = ((assignee_sp - task_sp) / assignee.max_story_points) * 100 if assignee.max_story_points else 0
                        
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
                            'impact': self._build_skill_mismatch_impact(
                                assignee, best_candidate, task_sp,
                                assignee_workload_pct, assignee_workload_after,
                                candidate_workload_pct, new_candidate_workload_pct,
                                match_score, best_match, task_requirements
                            ),
                            'action': {
                                'type': 'reassign',
                                'taskId': task.id,
                                'fromMemberId': assignee.id,
                                'toMemberId': best_candidate.id
                            }
                        })
                    else:
                        # No better candidate found - create warning proposal
                        task_sp = task.story_points or 0
                        
                        if cross_project_workload and assignee.id in cross_project_workload:
                            assignee_workload_pct = cross_project_workload[assignee.id]['pct']
                        else:
                            assignee_tasks = [t for t in tasks if (
                                t.raci_responsible and assignee.id in t.raci_responsible
                            )]
                            assignee_sp = sum(t.story_points or 0 for t in assignee_tasks)
                            assignee_workload_pct = (assignee_sp / assignee.max_story_points) * 100 if assignee.max_story_points else 0
                        
                        required_skills_list = ", ".join(sorted(task_requirements))
                        severity = 'critical' if task.priority.lower() in ['high', 'critical'] else 'important'
                        
                        warning_msg = f"\n\n*** NO SUITABLE CANDIDATE WARNING ***\nNo team member has the required skills: {required_skills_list.upper()}\nConsider training {assignee.name} or hiring external resources."
                        
                        proposals.append({
                            'id': f"skill-mismatch-{task.id}-{assignee.id}-{uuid.uuid4().hex[:8]}",
                            'type': 'skill_mismatch',
                            'severity': severity,
                            'category': 'resources',
                            'title': f"Skill gap: '{task.name}' assigned to {assignee.name}",
                            'description': f"Critical skill mismatch detected. No team member has required skills.",
                            'reason': f"{assignee.name} has {round(match_score*100)}% skills match for '{task.name}'. Required skills: {required_skills_list}.{warning_msg}",
                            'score': 85,
                            'taskName': task.name,
                            'taskSp': task_sp,
                            'impact': {
                                'currentMember': assignee.name,
                                'currentWorkload': round(assignee_workload_pct, 1),
                                'taskSP': task_sp,
                                'currentMatch': f"{round(match_score*100)}%",
                                'requiredSkills': list(task_requirements),
                                'availableCandidates': 0,
                                'suggestedAction': 'training_or_hiring',
                                'affectedMembers': [assignee.id],
                                'riskChange': 0,
                                'balanceChange': 0
                            },
                            'action': {
                                'type': 'flag_skill_gap',
                                'taskId': task.id,
                                'memberId': assignee.id,
                                'reason': 'No suitable candidate with required skills'
                            }
                        })
        
        return proposals
    
    def find_idle_resources(
        self,
        team_members: List[TeamMember],
        tasks: List[Task],
        cross_project_workload: Dict[int, Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Find team members with very low workload
        
        Args:
            team_members: List of team members
            tasks: List of tasks
            cross_project_workload: Optional dict of cross-project workload {member_id: {'sp': float, 'pct': float}}
            
        Returns:
            List of idle resource proposals
        """
        proposals = []
        
        # Find unassigned tasks (check only Responsible, not Accountable)
        unassigned_tasks = [
            t for t in tasks if t.status != 'Done' and
            not t.raci_responsible  # Only check Responsible (Accountable is just oversight)
        ]
        
        print(f"\n=== Idle Resource Detection Debug ===")
        print(f"Total tasks analyzed: {len(tasks)}")
        print(f"Unassigned tasks found (no Responsible): {len(unassigned_tasks)}")
        if unassigned_tasks:
            print(f"Unassigned task names: {[t.name for t in unassigned_tasks]}")
        else:
            print("⚠️ No unassigned tasks - Idle Resource proposals cannot be generated")
            print("Tip: Create a task without RACI Responsible assignment")
        
        for member in team_members:
            # Calculate workload (use cross-project if available)
            if cross_project_workload and member.id in cross_project_workload:
                total_sp = cross_project_workload[member.id]['sp']
                workload_pct = cross_project_workload[member.id]['pct']
            else:
                # Sprint Commitment - includes Done tasks for workload calc
                member_tasks = [
                    t for t in tasks if (
                        t.raci_responsible and member.id in t.raci_responsible
                    )
                ]
                total_sp = sum(t.story_points or 0 for t in member_tasks)
                workload_pct = (total_sp / member.max_story_points) * 100
            
            if workload_pct <= 40 and unassigned_tasks:  # Less than or equal to 40% utilized
                print(f"✓ {member.name} is idle ({round(workload_pct, 1)}%), suggesting task assignment")
                # Suggest assigning unassigned tasks with skill matching
                for task in unassigned_tasks[:2]:  # Suggest top 2
                    task_sp = task.story_points or 0
                    new_workload = round(workload_pct + (task_sp / member.max_story_points * 100), 1)
                    
                    # Calculate skill match
                    task_requirements = set(skill.lower() for skill in (task.required_skills or []))
                    member_skills = set(skill.lower() for skill in (member.skills or []))
                    
                    if task_requirements:
                        intersection = len(task_requirements.intersection(member_skills))
                        skill_match = (intersection / len(task_requirements)) * 100
                    else:
                        skill_match = 50  # Neutral if no requirements
                    
                    # Build reason with skill info
                    base_reason = f"{member.name} is underutilized at {round(workload_pct, 1)}% capacity. Can take on more work (skill match: {round(skill_match)}%)."
                    
                    # Add warning if skill match is low (<30%)
                    skill_warning = ""
                    if skill_match < 30 and task_requirements:
                        required_skills_list = ", ".join(sorted(task_requirements))
                        skill_warning = f"\n\n*** SKILL MISMATCH WARNING ***\n{member.name} has {round(skill_match)}% skill match! Missing required skills: {required_skills_list.upper()}\nConsider training or assigning to someone with better skills."
                    
                    description = f"{member.name} has low workload ({round(workload_pct, 1)}%)"
                    if skill_warning:
                        description += ". However, skills mismatch detected."
                    
                    # Build impact with overload warning check
                    impact_data = {
                        'toMember': member.name,
                        'currentWorkload': round(workload_pct, 1),
                        'toWorkload': new_workload,
                        'taskSP': task_sp,
                        'skillMatch': round(skill_match),
                        'workloadChange': new_workload - workload_pct,
                        'balanceChange': 2,
                        'affectedMembers': [member.id]
                    }
                    
                    # Add warning if recipient will be overloaded after assignment
                    if new_workload > 100:
                        impact_data['recipientOverloadWarning'] = True
                        impact_data['recipientOverloadPercent'] = round(new_workload, 1)
                    
                    proposals.append({
                        'id': f"idle-resource-{member.id}-{task.id}-{uuid.uuid4().hex[:8]}",
                        'type': 'idle_resource',
                        'severity': 'recommended',
                        'category': 'resources',
                        'title': f"Utilize idle resource: Assign '{task.name}' to {member.name}",
                        'description': description,
                        'reason': base_reason + skill_warning,
                        'score': 65,
                        'taskName': task.name,
                        'taskSp': task_sp,
                        'impact': impact_data,
                        'action': {
                            'type': 'assign_task',
                            'taskId': task.id,
                            'toMemberId': member.id
                        }
                    })
        
        return proposals

