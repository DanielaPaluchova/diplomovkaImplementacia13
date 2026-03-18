import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/services/api';

// Optimization scope types for requirement change analysis (includes planned_sprint support)
export type OptimizationScope = 'current_sprint' | 'planned_sprint' | 'backlog';

export interface ImprovementEstimate {
  estimation_accuracy?: string;
  parallelization_potential?: string;
  risk_reduction?: string;
  average_sp_after_split?: number;
}

export interface SplitProposal {
  should_split: boolean;
  reason: string;
  original_task_id?: number;
  original_sp?: number;
  num_parts?: number;
  subtasks?: Array<{
    name: string;
    title: string;
    description: string;
    story_points: number;
    type: string;
    priority: string;
    labels: string[];
    complexity: number;
    pert?: {
      optimistic: number;
      mostLikely: number;
      pessimistic: number;
    };
    status: string;
  }>;
  split_story_points?: number[];
  estimated_improvement?: ImprovementEstimate;
}

export interface ProposalImpact {
  workloadChange?:
    | {
        before: number;
        after: number;
      }
    | number;
  durationChange?: number;
  riskChange?: number;
  balanceChange?: number;
  affectedMembers?: (number | string)[];
  assignedMember?: string;
  fromMember?: string;
  toMember?: string;
  fromWorkload?: number;
  toWorkload?: number;
  fromWorkloadAfter?: number;
  toWorkloadBefore?: number;
  taskSP?: number;
  originalSP?: number;
  newSP?: number;
  splitInto?: number;
  improvement?: ImprovementEstimate;
  spBefore?: number;
  spAfter?: number;
  increase?: number;
  priorityBefore?: string;
  priorityAfter?: string;
  fromSprintNewUtilization?: number;
  toSprintNewUtilization?: number;
  currentMatch?: string;
  newMatch?: string;
  suggestedAction?: string;
  reason?: string;
  // PERT/RACI specific impact fields
  optimistic?: number;
  mostLikely?: number;
  pessimistic?: number;
  expected?: number;
  uncertainty?: number;
  uncertaintyRatio?: number; // Now represents CV (Coefficient of Variation)
  suggestedBuffer?: number;
  pertDuration?: number;
  adjustedDuration?: number;
  newAdjustedDuration?: number;
  overhead?: number;
  newOverhead?: number;
  delayDays?: number;
  overloadedMembers?: string[];
  weightedSP?: number;
  raciRoles?: Record<string, unknown>;
  reduction?: number;
  roleChange?: string;
  remainingResponsible?: number;
  skillMatch?: number;
  member?: string; // Member name for RACI rebalance
  currentWorkload?: number; // Current workload percentage
  newWorkload?: number; // New workload percentage after change
  // Overload warning
  recipientOverloadWarning?: boolean; // Warning if recipient will be overloaded
  recipientOverloadPercent?: number; // Recipient workload percentage after reassignment
  // Standard PERT statistical metrics
  stdDev?: number; // Standard Deviation (σ)
  variance?: number; // Variance (σ²)
  coefficientOfVariation?: number; // CV (σ / Expected) - as percentage
  // Confidence intervals
  conf68Lower?: number; // 68% confidence interval lower bound (Expected - 1σ)
  conf68Upper?: number; // 68% confidence interval upper bound (Expected + 1σ)
  conf95Lower?: number; // 95% confidence interval lower bound (Expected - 2σ)
  conf95Upper?: number; // 95% confidence interval upper bound (Expected + 2σ)
  // RACI missing assignment
  missingRole?: string; // 'Responsible' | 'Accountable'
  suggestedMemberId?: number;
  suggestedMemberName?: string;
  isProjectOwner?: boolean;
  isFallback?: boolean;
}

export interface ProposalAction {
  type: string;
  taskId?: number;
  taskData?: Record<string, unknown>;
  assignTo?: number;
  fromMemberId?: number;
  toMemberId?: number;
  newSP?: number;
  newPriority?: string;
  subtasks?: Array<Record<string, unknown>>;
  toSprintId?: number;
  newDueDate?: string;
}

export interface Proposal {
  id: string;
  type:
    | 'reassign'
    | 'split'
    | 'merge'
    | 'sprint_move'
    | 'cross_sprint_dep'
    | 'deadline_adjust'
    | 'add_task'
    | 'increase_sp'
    | 'priority_change'
    | 'bottleneck'
    | 'priority_conflict'
    | 'deadline_risk'
    | 'skill_mismatch'
    | 'idle_resource'
    | 'pert_uncertainty'
    | 'raci_overload'
    | 'duration_risk'
    | 'raci_missing_responsible'
    | 'raci_missing_accountable';
  severity: 'critical' | 'important' | 'recommended';
  category: 'workload' | 'quality' | 'timeline' | 'resources' | 'pert_raci';
  title: string;
  description: string;
  reason: string;
  score: number;
  source?: 'standard' | 'pert_raci';
  impact?: ProposalImpact;
  action: ProposalAction;
  selected?: boolean;
  taskId?: number;
  taskName?: string;
  taskSp?: number;
  fromSprintId?: number;
  fromSprintName?: string;
  toSprintId?: number;
  toSprintName?: string;
  proposal?: SplitProposal;
  taskIds?: number[];
  taskNames?: string[];
}

export interface ProjectState {
  totalStoryPoints: number;
  completedStoryPoints: number;
  duration: number;
  workload: number;
  riskScore: number;
  balanceScore: number;
  teamCapacity: number;
  taskCount: number;
  sprintCount: number;
  // PERT/RACI metrics
  totalPertDuration?: number;
  totalAdjustedDuration?: number;
  avgPertUncertainty?: number;
  raciWorkload?: number;
  durationOverhead?: number;
}

export interface AnalysisResult {
  currentState: ProjectState;
  proposals: Proposal[];
  categorized?: {
    critical: Proposal[];
    important: Proposal[];
    recommended: Proposal[];
  };
  projectedState: ProjectState;
  changeType?: string;
  priorityStrategy?: string;
  scope?: string;
  totalProposals?: number;
  message?: string;
}

export const useRequirementChangeStore = defineStore('requirementChange', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const analysisResult = ref<AnalysisResult | null>(null);
  const selectedProposals = ref<string[]>([]);

  async function autoOptimizeProject(
    projectId: number,
    scope: OptimizationScope = 'backlog',
  ): Promise<AnalysisResult | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.post<AnalysisResult>(`/projects/${projectId}/auto-optimize`, {
        scope,
      });

      analysisResult.value = response;
      selectedProposals.value = [];

      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to auto-optimize project';
      console.error('Failed to auto-optimize project:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function analyzeRequirementChange(
    projectId: number,
    changeType: string,
    changeData: Record<string, unknown>,
    priorityStrategy: string = 'balanced',
  ): Promise<AnalysisResult | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.post<AnalysisResult>(
        `/projects/${projectId}/analyze-requirement-change`,
        {
          changeType,
          changeData,
          priorityStrategy,
        },
      );

      analysisResult.value = response;
      selectedProposals.value = [];

      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to analyze requirement change';
      console.error('Failed to analyze requirement change:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function analyzePertRaci(
    projectId: number,
    scope: OptimizationScope = 'backlog',
  ): Promise<AnalysisResult | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.post<AnalysisResult>(`/projects/${projectId}/analyze-pert-raci`, {
        scope,
      });

      analysisResult.value = response;
      selectedProposals.value = [];

      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to analyze PERT+RACI';
      console.error('Failed to analyze PERT+RACI:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function applyChanges(
    projectId: number,
    proposals: Proposal[],
  ): Promise<{ success: boolean; applied: number; skipped: number; failed: number }> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.post<{
        applied?: number;
        failed?: number;
        skipped?: number;
        errors?: string[];
        error?: string;
        message?: string;
      }>(`/projects/${projectId}/apply-requirement-changes`, {
        proposals: proposals.map((p) => ({
          id: p.id,
          type: p.type,
          action: p.action,
        })),
        scope: analysisResult.value?.scope,
        optimizationType: analysisResult.value?.scope ? 'auto' : 'manual',
      });

      const applied = response.applied ?? 0;
      const failed = response.failed ?? 0;
      const skipped = response.skipped ?? 0;

      // If all selected are RACI missing (informational), treat as success even when skipped=0
      // (backend might not return skipped in older versions)
      const allRaciMissing = proposals.every(
        (p) =>
          p.type === 'raci_missing_responsible' ||
          p.type === 'raci_missing_accountable'
      );

      const success =
        applied > 0 ||
        (failed === 0 && skipped > 0) ||
        (failed === 0 && allRaciMissing);

      return {
        success,
        applied,
        skipped,
        failed,
      };
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { message?: string } }; message?: string };
      const errMsg =
        axiosErr?.response?.data?.message ??
        (err instanceof Error ? err.message : 'Failed to apply changes');
      error.value = errMsg;
      console.error('Failed to apply changes:', err);
      return { success: false, applied: 0, skipped: 0, failed: 1 };
    } finally {
      loading.value = false;
    }
  }

  function toggleProposalSelection(proposalId: string) {
    const index = selectedProposals.value.indexOf(proposalId);
    if (index === -1) {
      selectedProposals.value.push(proposalId);
    } else {
      selectedProposals.value.splice(index, 1);
    }
  }

  function selectAllProposals() {
    if (analysisResult.value) {
      selectedProposals.value = analysisResult.value.proposals.map((p) => p.id);
    }
  }

  function deselectAllProposals() {
    selectedProposals.value = [];
  }

  function clearAnalysis() {
    analysisResult.value = null;
    selectedProposals.value = [];
    error.value = null;
  }

  function getSelectedProposals(): Proposal[] {
    if (!analysisResult.value) return [];
    return analysisResult.value.proposals.filter((p) => selectedProposals.value.includes(p.id));
  }

  return {
    loading,
    error,
    analysisResult,
    selectedProposals,
    autoOptimizeProject,
    analyzeRequirementChange,
    analyzePertRaci,
    applyChanges,
    toggleProposalSelection,
    selectAllProposals,
    deselectAllProposals,
    clearAnalysis,
    getSelectedProposals,
  };
});
