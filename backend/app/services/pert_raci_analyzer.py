"""
PERT + RACI Analyzer Service
Detects PERT uncertainty risks, RACI overload, and duration overhead issues
"""
from app.models.task import Task
from app.models.team_member import TeamMember
from typing import Dict, List
import uuid


class PertRaciAnalyzerService:
    """Service for analyzing PERT and RACI-based risks and optimization opportunities"""
    
    # PERT uncertainty thresholds - using Coefficient of Variation (CV)
    # CV = standard_deviation / expected_duration
    # Based on industry best practices (PMI PMBOK, NASA standards)
    HIGH_UNCERTAINTY_CV = 0.33  # 33% - high volatility, task needs breakdown
    MEDIUM_UNCERTAINTY_CV = 0.20  # 20% - moderate uncertainty, monitor closely
    
    # RACI workload thresholds
    RACI_OVERLOAD_THRESHOLD = 1.0  # 100% of max capacity (weighted)
    RACI_HIGH_LOAD_THRESHOLD = 0.85  # 85% of max capacity
    
    # Duration overhead threshold
    DURATION_OVERHEAD_THRESHOLD = 0.2  # 20% increase over PERT
    
    # RACI weights for workload calculation
    RACI_WEIGHTS = {
        'responsible': 1.0,
        'accountable': 0.1,
        'consulted': 0.05,
        'informed': 0.01
    }
    
    def __init__(self):
        pass
    
    def find_pert_uncertainty_risks(self, tasks: List[Task]) -> List[Dict]:
        """
        Identify tasks with high PERT uncertainty using Coefficient of Variation (CV)
        
        Uses standard PERT statistical approach:
        - Standard Deviation (σ) = (Pessimistic - Optimistic) / 6
        - Coefficient of Variation (CV) = σ / Expected
        - CV > 33% indicates high volatility (needs breakdown)
        - CV > 20% indicates moderate uncertainty (monitor)
        
        Reference: PMI PMBOK Guide, NASA Program Management Guide
        
        Args:
            tasks: List of tasks with PERT estimates
            
        Returns:
            List of PERT uncertainty risk proposals
        """
        proposals = []
        
        for task in tasks:
            if task.status == 'Done':
                continue
            
            # Check if task has PERT estimates
            if not (task.pert_optimistic and task.pert_pessimistic and task.pert_expected):
                continue
            
            if task.pert_expected <= 0:
                continue
            
            # Standard PERT statistical calculations
            # Standard Deviation: σ = (P - O) / 6
            # This represents ±1σ confidence interval (68% probability)
            std_dev = (task.pert_pessimistic - task.pert_optimistic) / 6.0
            
            # Coefficient of Variation: CV = σ / E
            # Normalized measure of dispersion - industry standard for comparing uncertainty
            cv = std_dev / task.pert_expected
            
            # Variance (optional, for statistical completeness)
            variance = std_dev ** 2
            
            # Determine severity based on CV thresholds
            if cv >= self.HIGH_UNCERTAINTY_CV:
                severity = 'critical'
                score = 90
            elif cv >= self.MEDIUM_UNCERTAINTY_CV:
                severity = 'important'
                score = 75
            else:
                continue  # Acceptable uncertainty level
            
            # Calculate confidence intervals (68% and 95%)
            # 68% confidence: Expected ± 1σ
            conf_68_lower = max(0, task.pert_expected - std_dev)
            conf_68_upper = task.pert_expected + std_dev
            
            # 95% confidence: Expected ± 2σ
            conf_95_lower = max(0, task.pert_expected - (2 * std_dev))
            conf_95_upper = task.pert_expected + (2 * std_dev)
            
            # Suggested buffer: use 1 standard deviation as safety margin
            suggested_buffer = std_dev
            
            proposals.append({
                'id': f"pert-uncertainty-{task.id}-{uuid.uuid4().hex[:8]}",
                'type': 'pert_uncertainty',
                'severity': severity,
                'category': 'timeline',
                'title': f"High PERT uncertainty: '{task.name}' (CV: {round(cv * 100)}%)",
                'description': f"Task has high coefficient of variation (CV={round(cv * 100)}%). Consider breaking down into smaller subtasks.",
                'reason': f"Task shows CV of {round(cv * 100, 1)}% (σ={round(std_dev, 1)}d), indicating {'high volatility' if severity == 'critical' else 'moderate uncertainty'}. Range: {task.pert_optimistic}d - {task.pert_pessimistic}d (expected: {task.pert_expected}d). Industry threshold: CV > 33% requires breakdown.",
                'score': score,
                'source': 'pert_raci',
                'taskName': task.name,
                'taskSp': task.story_points or 0,
                'impact': {
                    'optimistic': round(task.pert_optimistic, 1),
                    'mostLikely': round(task.pert_most_likely, 1) if task.pert_most_likely else None,
                    'pessimistic': round(task.pert_pessimistic, 1),
                    'expected': round(task.pert_expected, 1),
                    # Standard PERT metrics
                    'stdDev': round(std_dev, 2),
                    'variance': round(variance, 3),
                    'coefficientOfVariation': round(cv * 100, 1),  # as percentage
                    # Confidence intervals
                    'conf68Lower': round(conf_68_lower, 1),
                    'conf68Upper': round(conf_68_upper, 1),
                    'conf95Lower': round(conf_95_lower, 1),
                    'conf95Upper': round(conf_95_upper, 1),
                    # Legacy fields for backward compatibility
                    'uncertainty': round(task.pert_pessimistic - task.pert_optimistic, 1),
                    'uncertaintyRatio': round(cv * 100, 1),  # Now using CV
                    'suggestedBuffer': round(suggested_buffer, 1),
                    'taskSP': task.story_points or 0,
                    'riskChange': -1.0 if severity == 'critical' else -0.5,
                    'affectedMembers': (task.raci_responsible or []) + ([task.raci_accountable] if task.raci_accountable else [])
                },
                'action': {
                    'type': 'split',
                    'taskId': task.id,
                    'reason': f'High CV ({round(cv * 100)}%) indicates task should be broken down for better estimation accuracy'
                }
            })
        
        return proposals
    
    def find_raci_overload_risks(
        self,
        team_members: List[TeamMember],
        tasks: List[Task],
        sprint_id: int = None,
        all_tasks: List[Task] = None
    ) -> List[Dict]:
        """
        Detect team members with RACI-weighted workload exceeding capacity
        
        Args:
            team_members: List of team members
            tasks: List of tasks to analyze (filtered by scope)
            sprint_id: Optional sprint ID for filtering analyzed tasks
            all_tasks: All project tasks for accurate workload calculation
            
        Returns:
            List of RACI overload proposals
        """
        proposals = []
        
        # Calculate CROSS-PROJECT RACI-weighted workload
        # This matches the frontend calculation and includes ALL projects
        from app.utils.workload_calculator import calculate_cross_project_raci_workload
        
        cross_project_workload = calculate_cross_project_raci_workload(
            team_members,
            sprint_id=sprint_id
        )
        
        # Convert to internal format
        member_workloads = {}
        for member in team_members:
            if member.id in cross_project_workload:
                member_workloads[member.id] = {
                    'weighted_sp': cross_project_workload[member.id]['weighted_sp'],
                    'roles': {}
                }
        
        for member_id, workload_info in member_workloads.items():
            member = next((m for m in team_members if m.id == member_id), None)
            if not member:
                continue
            
            weighted_sp = workload_info['weighted_sp']
            max_capacity = member.max_story_points
            overload_ratio = weighted_sp / max_capacity if max_capacity > 0 else 0
            
            # Check for overload
            if overload_ratio >= self.RACI_OVERLOAD_THRESHOLD:
                severity = 'critical'
                score = 95
            elif overload_ratio >= self.RACI_HIGH_LOAD_THRESHOLD:
                severity = 'important'
                score = 80
            else:
                continue  # Not overloaded
            
            # Find tasks where member is Responsible (most impactful role)
            responsible_tasks = [
                t for t in tasks
                if t.raci_responsible and member_id in t.raci_responsible
            ]
            
            if responsible_tasks:
                # Sort by story points (descending) to suggest reassigning largest tasks
                responsible_tasks.sort(key=lambda t: t.story_points or 0, reverse=True)
                task_to_reassign = responsible_tasks[0]
                
                # Find best candidate to take over
                other_members = [m for m in team_members if m.id != member_id]
                if other_members:
                    # Build task requirements for skill matching
                    task_requirements = {
                        'required_skills': task_to_reassign.required_skills or [],
                        'type': task_to_reassign.type,
                        'priority': task_to_reassign.priority
                    }
                    
                    # Calculate workloads and skill match for candidates
                    candidate_scores = []
                    for candidate in other_members:
                        cand_workload = member_workloads.get(candidate.id, {'weighted_sp': 0})
                        cand_ratio = cand_workload['weighted_sp'] / candidate.max_story_points if candidate.max_story_points > 0 else 0
                        
                        # Calculate skill match
                        skill_match = self._calculate_skill_match(candidate, task_requirements)
                        
                        # Only consider if skill match is reasonable (at least 30%)
                        if skill_match < 0.3:
                            continue
                        
                        # Combined score: 40% skill match, 60% workload availability
                        # RACI Overload is primarily a workload problem, so prioritize available capacity
                        # Workload score: lower is better, so invert it
                        workload_score = (1.0 - min(cand_ratio, 1.0))  # 0-1 scale, higher is better
                        combined_score = (skill_match * 0.4) + (workload_score * 0.6)
                        
                        candidate_scores.append({
                            'member': candidate,
                            'ratio': cand_ratio,
                            'weighted_sp': cand_workload['weighted_sp'],
                            'skill_match': skill_match,
                            'score': combined_score
                        })
                    
                    # If no candidates with skills, fallback to any least loaded member
                    if not candidate_scores:
                        candidate_workloads = {}
                        for candidate in other_members:
                            cand_workload = member_workloads.get(candidate.id, {'weighted_sp': 0})
                            cand_ratio = cand_workload['weighted_sp'] / candidate.max_story_points if candidate.max_story_points > 0 else 0
                            candidate_workloads[candidate.id] = {
                                'ratio': cand_ratio,
                                'weighted_sp': cand_workload['weighted_sp']
                            }
                        
                        # Find least loaded candidate (fallback)
                        best_candidate = min(other_members, key=lambda m: candidate_workloads.get(m.id, {'ratio': 999})['ratio'])
                        best_workload = candidate_workloads.get(best_candidate.id, {'ratio': 0, 'weighted_sp': 0})
                        skill_match_pct = 0  # No skill match
                    else:
                        # Sort by combined score (highest first)
                        candidate_scores.sort(key=lambda x: x['score'], reverse=True)
                        best_score_data = candidate_scores[0]
                        best_candidate = best_score_data['member']
                        best_workload = {
                            'ratio': best_score_data['ratio'],
                            'weighted_sp': best_score_data['weighted_sp']
                        }
                        skill_match_pct = round(best_score_data['skill_match'] * 100)
                    
                    task_sp = task_to_reassign.story_points or 0
                    new_workload_ratio = ((best_workload['weighted_sp'] + task_sp) / best_candidate.max_story_points) if best_candidate.max_story_points > 0 else 0
                    after_workload_ratio = ((weighted_sp - task_sp) / max_capacity) if max_capacity > 0 else 0
                    
                    # Build reason with skill match info
                    base_reason = f"{member.name} is overloaded with RACI-weighted workload at {round(overload_ratio * 100, 1)}% capacity ({round(weighted_sp, 1)} weighted SP / {max_capacity} max SP). Reassign '{task_to_reassign.name}' to {best_candidate.name}"
                    
                    if skill_match_pct > 0:
                        reason = f"{base_reason} (skill match: {skill_match_pct}%)."
                    else:
                        # No suitable candidate with skills found - add warning
                        task_required_skills = task_to_reassign.required_skills or []
                        if task_required_skills:
                            required_skills_list = ", ".join(sorted(task_required_skills))
                            skill_warning = f"\n\n*** NO SUITABLE CANDIDATE WARNING ***\nNo team member has the required skills: {required_skills_list.upper()}\nConsider training {best_candidate.name} or hiring external resources."
                        else:
                            skill_warning = "\n\n*** NO SUITABLE CANDIDATE WARNING ***\nTask has no defined skill requirements. Consider adding required_skills to task for better skill matching."
                        reason = f"{base_reason}.{skill_warning}"
                    
                    impact_data = {
                        'fromMember': member.name,
                        'toMember': best_candidate.name,
                        'fromWorkload': round(overload_ratio * 100, 1),
                        'fromWorkloadAfter': round(after_workload_ratio * 100, 1),
                        'toWorkloadBefore': round(best_workload['ratio'] * 100, 1),
                        'toWorkload': round(new_workload_ratio * 100, 1),
                        'taskSP': task_sp,
                        'weightedSP': round(weighted_sp, 1),
                        'raciRoles': workload_info.get('roles', {}),
                        'workloadChange': -(task_sp / max_capacity * 100) if max_capacity > 0 else 0,
                        'balanceChange': 5,
                        'affectedMembers': [member_id, best_candidate.id]
                    }
                    
                    # Add skill match to impact if available
                    if skill_match_pct > 0:
                        impact_data['skillMatch'] = skill_match_pct
                    
                    # Check if recipient will be significantly overloaded
                    recipient_overload_pct = round(new_workload_ratio * 100, 1)
                    
                    # If best candidate will be severely overloaded (>120%), suggest backlog move instead
                    if new_workload_ratio > 1.2:
                        # Suggest moving to backlog since no one has capacity
                        impact_data['suggestedAction'] = 'move_to_backlog'
                        impact_data['reason'] = 'All team members are overloaded'
                        
                        backlog_reason = f"{member.name} is overloaded with RACI-weighted workload at {round(overload_ratio * 100, 1)}% capacity. Best available candidate {best_candidate.name} would be at {recipient_overload_pct}% after reassignment, which is too high. Consider moving '{task_to_reassign.name}' to backlog or adding resources."
                        
                        proposals.append({
                            'id': f"raci-overload-backlog-{member_id}-{task_to_reassign.id}-{uuid.uuid4().hex[:8]}",
                            'type': 'raci_overload',
                            'severity': 'critical',  # Escalate to critical
                            'category': 'workload',
                            'title': f"RACI overload: Move '{task_to_reassign.name}' to backlog",
                            'description': f"{member.name} overloaded, no team member has sufficient capacity",
                            'reason': backlog_reason,
                            'score': score + 10,  # Higher priority
                            'source': 'pert_raci',
                            'taskName': task_to_reassign.name,
                            'taskSp': task_sp,
                            'impact': impact_data,
                            'action': {
                                'type': 'sprint_move',
                                'taskId': task_to_reassign.id,
                                'fromMemberId': member_id,
                                'toSprintId': None  # Move to backlog
                            }
                        })
                    else:
                        # Regular reassignment (possibly with warning if >100%)
                        if new_workload_ratio > 1.0:  # Over 100%
                            impact_data['recipientOverloadWarning'] = True
                            impact_data['recipientOverloadPercent'] = recipient_overload_pct
                        
                        proposals.append({
                            'id': f"raci-overload-{member_id}-{task_to_reassign.id}-{uuid.uuid4().hex[:8]}",
                            'type': 'raci_overload',
                            'severity': severity,
                            'category': 'workload',
                            'title': f"RACI overload: Reassign '{task_to_reassign.name}' from {member.name}",
                            'description': f"{member.name} has {round(overload_ratio * 100, 1)}% RACI-weighted workload",
                            'reason': reason,
                            'score': score,
                            'source': 'pert_raci',
                            'taskName': task_to_reassign.name,
                            'taskSp': task_sp,
                            'impact': impact_data,
                            'action': {
                                'type': 'reassign',
                                'taskId': task_to_reassign.id,
                                'fromMemberId': member_id,
                                'toMemberId': best_candidate.id
                            }
                        })
        
        return proposals
    
    def find_adjusted_duration_risks(
        self,
        tasks: List[Task],
        team_members: List[TeamMember],
        sprint_id: int = None,
        all_tasks: List[Task] = None
    ) -> List[Dict]:
        """
        Find tasks where RACI-adjusted duration significantly exceeds PERT duration
        
        Tries to find reassignment first, then suggests sprint move as fallback
        
        Args:
            tasks: List of tasks to analyze (filtered by scope)
            team_members: List of team members
            sprint_id: Optional sprint ID for filtering analyzed tasks
            all_tasks: All project tasks for accurate workload calculation
            
        Returns:
            List of adjusted duration risk proposals
        """
        proposals = []
        
        # Calculate CROSS-PROJECT RACI-weighted workload
        # This matches the frontend calculation and includes ALL projects
        from app.utils.workload_calculator import calculate_cross_project_raci_workload
        
        cross_project_workload = calculate_cross_project_raci_workload(
            team_members,
            sprint_id=sprint_id
        )
        
        # Convert to internal format
        member_workloads = {}
        for member in team_members:
            if member.id in cross_project_workload:
                member_workloads[member.id] = {
                    'weighted_sp': cross_project_workload[member.id]['weighted_sp'],
                    'roles': {}
                }
        
        for task in tasks:
            if task.status == 'Done':
                continue
            
            # Check if task has PERT estimates
            if not task.pert_expected or task.pert_expected == 0:
                continue
            
            # Calculate adjusted duration based on RACI overload
            adjusted_duration = self._calculate_task_adjusted_duration(
                task, team_members, member_workloads
            )
            
            # Calculate overhead
            overhead = (adjusted_duration - task.pert_expected) / task.pert_expected if task.pert_expected > 0 else 0
            
            # Only flag if overhead is significant
            if overhead < self.DURATION_OVERHEAD_THRESHOLD:
                continue
            
            severity = 'critical' if overhead >= 0.5 else 'important'  # 50% overhead = critical
            
            # Identify overloaded members (those causing the overhead)
            overloaded_members_info = []
            from_member = None
            from_member_id = None
            
            if task.raci_responsible:
                for member_id in task.raci_responsible:
                    member = next((m for m in team_members if m.id == member_id), None)
                    if member and member_id in member_workloads:
                        workload_ratio = member_workloads[member_id]['weighted_sp'] / member.max_story_points if member.max_story_points > 0 else 0
                        if workload_ratio > 1.0:
                            overloaded_members_info.append({
                                'name': member.name,
                                'id': member_id,
                                'ratio': workload_ratio
                            })
            
            # STRATEGY 1: Try to find a less loaded team member for reassignment
            reassignment_found = False
            
            if overloaded_members_info:
                # Sort by overload (most overloaded first)
                overloaded_members_info.sort(key=lambda x: x['ratio'], reverse=True)
                from_member_info = overloaded_members_info[0]
                from_member = from_member_info['name']
                from_member_id = from_member_info['id']
                from_workload_ratio = from_member_info['ratio']
                
                # Find alternative candidates
                candidates = []
                task_requirements = {
                    'required_skills': task.required_skills or [],
                    'type': task.type,
                    'priority': task.priority
                }
                
                for candidate in team_members:
                    if candidate.id == from_member_id:
                        continue  # Skip the overloaded member
                    
                    # Calculate candidate's workload
                    if candidate.id in member_workloads:
                        cand_weighted_sp = member_workloads[candidate.id]['weighted_sp']
                    else:
                        cand_weighted_sp = 0
                    
                    cand_workload_ratio = cand_weighted_sp / candidate.max_story_points if candidate.max_story_points > 0 else 0
                    
                    # Check if candidate has capacity (not more than 95% after adding this task)
                    task_sp = task.story_points or 0
                    new_workload_ratio = (cand_weighted_sp + task_sp) / candidate.max_story_points if candidate.max_story_points > 0 else 0
                    
                    if new_workload_ratio > 0.95:  # Would be overloaded
                        continue
                    
                    # Calculate skill match score
                    skill_match = self._calculate_skill_match(candidate, task_requirements)
                    
                    # Only consider if skill match is reasonable (at least 30%)
                    if skill_match < 0.3:
                        continue
                    
                    # Calculate what would be the new duration overhead with this candidate
                    temp_workloads = member_workloads.copy()
                    temp_workloads[candidate.id] = {'weighted_sp': cand_weighted_sp + task_sp}
                    new_adjusted_duration = self._calculate_task_adjusted_duration_for_member(
                        task, candidate, temp_workloads
                    )
                    new_overhead = (new_adjusted_duration - task.pert_expected) / task.pert_expected if task.pert_expected > 0 else 0
                    
                    # Good candidate if new overhead is less than 10%
                    if new_overhead < 0.10:
                        # Combined score: 60% workload, 40% skills
                        # Duration risk is caused by overload, so prioritize available capacity
                        workload_score = (1.0 - min(new_workload_ratio, 1.0))  # 0-1, higher is better (less loaded)
                        combined_score = (workload_score * 0.6) + (skill_match * 0.4)
                        
                        candidates.append({
                            'member': candidate,
                            'workload_before': round(cand_workload_ratio * 100, 1),
                            'workload_after': round(new_workload_ratio * 100, 1),
                            'skill_match': skill_match,
                            'new_overhead': new_overhead,
                            'new_duration': new_adjusted_duration,
                            'score': combined_score * 100  # Scale to 0-100
                        })
                
                # If we found suitable candidates, create reassignment proposal
                if candidates:
                    # Sort by combined score (best first)
                    candidates.sort(key=lambda x: x['score'], reverse=True)
                    best_candidate = candidates[0]
                    
                    from_member_obj = next((m for m in team_members if m.id == from_member_id), None)
                    task_sp = task.story_points or 0
                    from_weighted_sp = member_workloads.get(from_member_id, {}).get('weighted_sp', 0)
                    from_workload_after = ((from_weighted_sp - task_sp) / from_member_obj.max_story_points * 100) if from_member_obj else 0
                    
                    # Build reason with skill match warning if needed
                    skill_match_pct = round(best_candidate['skill_match'] * 100)
                    base_reason = f"{from_member} is overloaded ({round(from_workload_ratio * 100, 1)}%) causing {round(overhead * 100)}% duration overhead. {best_candidate['member'].name} has capacity and skills (match: {skill_match_pct}%), will complete in {round(best_candidate['new_duration'], 1)}d instead of {round(adjusted_duration, 1)}d."
                    
                    # Add warning if skill match is low (30-50%)
                    if skill_match_pct < 50:
                        task_required_skills = task.required_skills or []
                        if task_required_skills:
                            required_skills_list = ", ".join(sorted(task_required_skills))
                            skill_warning = f"\n\n*** SKILL MISMATCH WARNING ***\n{best_candidate['member'].name} has {skill_match_pct}% skill match! Missing required skills: {required_skills_list.upper()}\nConsider training or finding alternative candidate."
                            base_reason += skill_warning
                    
                    # Check if recipient will be overloaded
                    impact_data = {
                        'pertDuration': round(task.pert_expected, 1),
                        'adjustedDuration': round(adjusted_duration, 1),
                        'newAdjustedDuration': round(best_candidate['new_duration'], 1),
                        'overhead': round(overhead * 100, 1),
                        'newOverhead': round(best_candidate['new_overhead'] * 100, 1),
                        'improvement': round((adjusted_duration - best_candidate['new_duration']), 1),
                        'fromMember': from_member,
                        'toMember': best_candidate['member'].name,
                        'fromWorkload': round(from_workload_ratio * 100, 1),
                        'fromWorkloadAfter': round(from_workload_after, 1),
                        'toWorkloadBefore': best_candidate['workload_before'],
                        'toWorkload': best_candidate['workload_after'],
                        'skillMatch': round(best_candidate['skill_match'] * 100),
                        'taskSP': task_sp,
                        'durationChange': -round(adjusted_duration - best_candidate['new_duration'], 1),
                        'riskChange': -0.5,
                        'affectedMembers': [from_member_id, best_candidate['member'].id]
                    }
                    
                    # Add warning if recipient will be overloaded after reassignment
                    if best_candidate['workload_after'] > 100:
                        impact_data['recipientOverloadWarning'] = True
                        impact_data['recipientOverloadPercent'] = best_candidate['workload_after']
                    
                    proposals.append({
                        'id': f"duration-risk-reassign-{task.id}-{uuid.uuid4().hex[:8]}",
                        'type': 'duration_risk',
                        'severity': severity,
                        'category': 'timeline',
                        'title': f"Duration risk: Reassign '{task.name}' to reduce overhead",
                        'description': f"Reassign from {from_member} to {best_candidate['member'].name} to reduce duration overhead",
                        'reason': base_reason,
                        'score': 85 if severity == 'critical' else 75,
                        'source': 'pert_raci',
                        'taskName': task.name,
                        'taskSp': task_sp,
                        'impact': impact_data,
                        'action': {
                            'type': 'reassign',
                            'taskId': task.id,
                            'fromMemberId': from_member_id,
                            'toMemberId': best_candidate['member'].id
                        }
                    })
                    reassignment_found = True
            
            # STRATEGY 2: Fallback to sprint move if no suitable candidate found
            if not reassignment_found:
                overloaded_names = [info['name'] for info in overloaded_members_info]
                
                proposals.append({
                    'id': f"duration-risk-sprint-{task.id}-{uuid.uuid4().hex[:8]}",
                    'type': 'duration_risk',
                    'severity': severity,
                    'category': 'timeline',
                    'title': f"Duration overhead: '{task.name}' ({round(overhead * 100)}% delay)",
                    'description': f"Move to next sprint to reduce duration overhead",
                    'reason': f"Task '{task.name}' will take {round(adjusted_duration, 1)}d instead of {round(task.pert_expected, 1)}d due to team overload ({round(overhead * 100)}% overhead). No team member available with required skills and capacity. Consider moving to next sprint." + (f" Overloaded: {', '.join(overloaded_names)}" if overloaded_names else ""),
                    'score': 70 if severity == 'critical' else 60,
                    'source': 'pert_raci',
                    'taskName': task.name,
                    'taskSp': task.story_points or 0,
                    'impact': {
                        'pertDuration': round(task.pert_expected, 1),
                        'adjustedDuration': round(adjusted_duration, 1),
                        'overhead': round(overhead * 100, 1),
                        'delayDays': round(adjusted_duration - task.pert_expected, 1),
                        'overloadedMembers': overloaded_names,
                        'taskSP': task.story_points or 0,
                        'reason': 'No suitable team member available',
                        'durationChange': -round(adjusted_duration - task.pert_expected, 1),
                        'riskChange': -0.5,
                        'affectedMembers': (task.raci_responsible or []) + ([task.raci_accountable] if task.raci_accountable else [])
                    },
                    'action': {
                        'type': 'sprint_move',
                        'taskId': task.id,
                        'toSprintId': None,  # Will be determined during application
                        'reason': 'High duration overhead due to team overload, no suitable reassignment candidate'
                    }
                })
        
        return proposals
    
    # Helper methods
    
    def _calculate_raci_workloads(
        self,
        team_members: List[TeamMember],
        tasks: List[Task],
        sprint_id: int = None
    ) -> Dict[int, Dict]:
        """
        Calculate RACI-weighted workload for each team member
        
        Returns:
            Dict mapping member_id to workload info {weighted_sp, roles: {R: sp, A: sp, C: sp, I: sp}}
        """
        workloads = {}
        
        for member in team_members:
            workloads[member.id] = {
                'weighted_sp': 0,
                'roles': {'R': 0, 'A': 0, 'C': 0, 'I': 0}
            }
        
        for task in tasks:
            # Filter by sprint if specified
            if sprint_id is not None and task.sprint_id != sprint_id:
                continue
            
            task_sp = task.story_points or 0
            
            # Responsible (R)
            if task.raci_responsible:
                for member_id in task.raci_responsible:
                    if member_id in workloads:
                        workloads[member_id]['weighted_sp'] += task_sp * self.RACI_WEIGHTS['responsible']
                        workloads[member_id]['roles']['R'] += task_sp
            
            # Accountable (A)
            if task.raci_accountable and task.raci_accountable in workloads:
                workloads[task.raci_accountable]['weighted_sp'] += task_sp * self.RACI_WEIGHTS['accountable']
                workloads[task.raci_accountable]['roles']['A'] += task_sp
            
            # Consulted (C)
            if task.raci_consulted:
                for member_id in task.raci_consulted:
                    if member_id in workloads:
                        workloads[member_id]['weighted_sp'] += task_sp * self.RACI_WEIGHTS['consulted']
                        workloads[member_id]['roles']['C'] += task_sp
            
            # Informed (I)
            if task.raci_informed:
                for member_id in task.raci_informed:
                    if member_id in workloads:
                        workloads[member_id]['weighted_sp'] += task_sp * self.RACI_WEIGHTS['informed']
                        workloads[member_id]['roles']['I'] += task_sp
        
        return workloads
    
    def _calculate_task_adjusted_duration(
        self,
        task: Task,
        team_members: List[TeamMember],
        member_workloads: Dict[int, Dict]
    ) -> float:
        """
        Calculate RACI-adjusted duration for a single task
        Uses the formula from PertRaciOptimizationPage.vue
        """
        if not task.pert_expected or task.pert_expected == 0:
            return 0
        
        pert_duration = task.pert_expected
        
        # Calculate average EXCESS overload for each RACI role
        LR = LA = LC = LI = 0
        
        # Responsible (R)
        if task.raci_responsible:
            excess_sum = 0
            for member_id in task.raci_responsible:
                member = next((m for m in team_members if m.id == member_id), None)
                if member and member_id in member_workloads:
                    weighted_sp = member_workloads[member_id]['weighted_sp']
                    overload = weighted_sp / member.max_story_points if member.max_story_points > 0 else 0
                    excess = max(0, overload - 1.0)  # Only excess over 100%
                    excess_sum += excess
            LR = excess_sum / len(task.raci_responsible) if task.raci_responsible else 0
        
        # Accountable (A)
        if task.raci_accountable:
            member = next((m for m in team_members if m.id == task.raci_accountable), None)
            if member and task.raci_accountable in member_workloads:
                weighted_sp = member_workloads[task.raci_accountable]['weighted_sp']
                overload = weighted_sp / member.max_story_points if member.max_story_points > 0 else 0
                LA = max(0, overload - 1.0)
        
        # Consulted (C)
        if task.raci_consulted:
            excess_sum = 0
            for member_id in task.raci_consulted:
                member = next((m for m in team_members if m.id == member_id), None)
                if member and member_id in member_workloads:
                    weighted_sp = member_workloads[member_id]['weighted_sp']
                    overload = weighted_sp / member.max_story_points if member.max_story_points > 0 else 0
                    excess = max(0, overload - 1.0)
                    excess_sum += excess
            LC = excess_sum / len(task.raci_consulted) if task.raci_consulted else 0
        
        # Informed (I)
        if task.raci_informed:
            excess_sum = 0
            for member_id in task.raci_informed:
                member = next((m for m in team_members if m.id == member_id), None)
                if member and member_id in member_workloads:
                    weighted_sp = member_workloads[member_id]['weighted_sp']
                    overload = weighted_sp / member.max_story_points if member.max_story_points > 0 else 0
                    excess = max(0, overload - 1.0)
                    excess_sum += excess
            LI = excess_sum / len(task.raci_informed) if task.raci_informed else 0
        
        # Apply formula: T_adjusted = T_pert × (1 + (1×LR) + (0.1×LA) + (0.05×LC) + (0.01×LI))
        raci_adjustment = (1.0 * LR) + (0.1 * LA) + (0.05 * LC) + (0.01 * LI)
        adjusted_duration = pert_duration * (1 + raci_adjustment)
        
        return adjusted_duration
    
    def _calculate_skill_match(self, team_member: TeamMember, task_requirements: Dict) -> float:
        """
        Calculate skill match between team member and task requirements
        
        Args:
            team_member: Team member to evaluate
            task_requirements: Dict with 'required_skills', 'type', 'priority'
            
        Returns:
            Skill match score (0.0 to 1.0)
        """
        # Get member skills and task required skills
        member_skills = set(skill.lower() for skill in (team_member.skills or []))
        task_required_skills = set(skill.lower() for skill in task_requirements.get('required_skills', []))
        
        if not task_required_skills:
            # If no specific skills required, return moderate match
            return 0.5
        
        # Calculate skill overlap
        matching_skills = member_skills.intersection(task_required_skills)
        skill_score = len(matching_skills) / len(task_required_skills) if task_required_skills else 0.5
        
        # Bonus for having more skills than required (experienced)
        if matching_skills and len(member_skills) > len(task_required_skills):
            skill_score = min(1.0, skill_score + 0.1)
        
        return skill_score
    
    def _calculate_task_adjusted_duration_for_member(
        self,
        task: Task,
        member: TeamMember,
        member_workloads: Dict[int, Dict]
    ) -> float:
        """
        Calculate adjusted duration if task was assigned to specific member
        Simplified calculation assuming member would be Responsible
        
        Args:
            task: Task to calculate duration for
            member: Target team member
            member_workloads: Current workload dict (modified with task already added)
            
        Returns:
            Adjusted duration in days
        """
        if not task.pert_expected or task.pert_expected == 0:
            return (task.story_points or 0) * 0.5  # Fallback estimate
        
        pert_duration = task.pert_expected
        
        # Calculate member's workload ratio (after adding this task)
        weighted_sp = member_workloads.get(member.id, {}).get('weighted_sp', 0)
        max_sp = member.max_story_points or 20
        overload_ratio = (weighted_sp / max_sp) if max_sp > 0 else 0
        
        # Calculate excess overload (above 100%)
        excess_overload = max(0, overload_ratio - 1.0)
        
        # Apply RACI adjustment (assuming Responsible role, so weight = 1.0)
        raci_adjustment = self.RACI_WEIGHTS['responsible'] * excess_overload
        
        return pert_duration * (1 + raci_adjustment)

