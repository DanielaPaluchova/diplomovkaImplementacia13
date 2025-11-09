import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/services/api';

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
    | 'deadline_adjust'
    | 'add_task'
    | 'increase_sp'
    | 'priority_change'
    | 'bottleneck'
    | 'priority_conflict'
    | 'deadline_risk'
    | 'skill_mismatch'
    | 'cross_sprint_dep'
    | 'parallel_opportunity'
    | 'idle_resource';
  severity: 'critical' | 'important' | 'recommended';
  category: 'workload' | 'quality' | 'timeline' | 'resources';
  title: string;
  description: string;
  reason: string;
  score: number;
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
    scope: 'current_sprint' | 'all_sprints' = 'all_sprints',
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

  async function applyChanges(projectId: number, proposals: Proposal[]): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.post<{ applied: number; failed: number; errors?: string[] }>(
        `/projects/${projectId}/apply-requirement-changes`,
        {
          proposals: proposals.map((p) => ({
            id: p.id,
            type: p.type,
            action: p.action,
          })),
        },
      );

      return response.applied > 0;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to apply changes';
      console.error('Failed to apply changes:', err);
      return false;
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
    applyChanges,
    toggleProposalSelection,
    selectAllProposals,
    deselectAllProposals,
    clearAnalysis,
    getSelectedProposals,
  };
});
