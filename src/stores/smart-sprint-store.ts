import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from 'src/services/api';

// Strategy configuration
export interface StrategyParameter {
  name: string;
  label: string;
  type: 'slider' | 'input' | 'select';
  min?: number;
  max?: number;
  step?: number;
  default: number | string;
  options?: Array<{ label: string; value: string | number }>;
}

export interface SprintStrategy {
  id: string;
  name: string;
  description: string;
  parameters: StrategyParameter[];
  icon: string;
  recommended: string;
}

// Sprint planning request
export interface SprintPlanConfig {
  strategy: string;
  sprintName: string;
  sprintGoal?: string;
  startDate: string;
  endDate: string;
  sprintDuration?: number;
  targetUtilization?: number;
  closeActiveSprint?: boolean;
  considerCrossProjectWorkload?: boolean;
  parameters?: {
    weights?: {
      priority?: number;
      workload?: number;
      skills?: number;
      dependency?: number;
      velocity?: number;
    };
  };
}

// Task assignment
export interface TaskAssignment {
  taskId: number;
  taskName: string;
  memberId: number;
  memberName: string;
  role: 'responsible' | 'accountable';
  storyPoints: number;
}

// Task reasoning
export interface TaskReasoning {
  selected: boolean;
  reason: string;
  assignedTo?: string;
  priority?: string;
  balanceScore?: number;
  skillScore?: number;
  matchScore?: number;
  dependencyScore?: number;
  compositeScore?: number;
  scoreBreakdown?: Record<string, number>;
}

// Sprint plan result
export interface SprintTask {
  id: number;
  name: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  type: string;
  storyPoints: number;
  labels: string[];
  complexity: number;
  dependencies: number[];
  riskLevel: string;
}

export interface MemberWorkload {
  memberId: number;
  memberName: string;
  assignedSP: number;
  maxCapacity: number;
  utilization: number;
  taskCount: number;
}

export interface SprintMetrics {
  totalStoryPoints: number;
  teamCapacity: number;
  utilization: number;
  balanceScore: number;
  riskScore: number;
  taskCount: number;
  priorityDistribution?: {
    high: number;
    medium: number;
    low: number;
  };
  velocityAdjustedCapacity?: number;
  velocityUtilization?: number;
  totalValue?: number;
  averageValue?: number;
  riskBreakdown?: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  weights?: Record<string, number>;
}

export interface SprintSummary {
  totalStoryPoints: number;
  teamCapacity: number;
  utilizationPercentage: number;
  taskCount: number;
  memberBreakdown: MemberWorkload[];
}

export interface TeamMemberAnalysis {
  memberId: number;
  memberName: string;
  maxCapacity: number;
  assignedInThisSprint: number;
  crossProjectWorkload: number;
  totalWorkload: number;
  availableCapacity: number;
  utilizationPercentage: number;
  status: 'available' | 'assigned' | 'nearly_full' | 'at_capacity';
  taskCount: number;
  reason: string;
}

export interface TeamAnalysis {
  members: TeamMemberAnalysis[];
  considerCrossProject: boolean;
  summary: {
    totalMembers: number;
    assignedMembers: number;
    atCapacity: number;
    available: number;
  };
}

export interface SprintPlanResult {
  suggestedTasks: SprintTask[];
  assignments: Record<string, TaskAssignment>;
  metrics: SprintMetrics;
  reasoning: Record<string, TaskReasoning>;
  sprintSummary: SprintSummary;
  teamAnalysis?: TeamAnalysis;
  strategy: string;
  projectId: number;
  sprintConfig?: {
    name: string;
    goal: string;
    startDate: string;
    endDate: string;
    targetCapacity: number;
    teamCapacity: number;
  };
  activeSprint?: {
    id: number;
    name: string;
    status: string;
    willBeClosed: boolean;
  };
  eligibleTasksCount?: number;
  error?: string;
}

// Apply sprint plan request
export interface ApplySprintPlanRequest {
  sprintName: string;
  sprintGoal?: string;
  startDate: string;
  endDate: string;
  closeActiveSprint?: boolean;
  tasks: number[];
  assignments: Record<string, { memberId: number; role: string }>;
}

// Apply sprint plan response
export interface ApplySprintPlanResponse {
  success: boolean;
  sprint: {
    id: number;
    name: string;
    goal: string;
    startDate: string;
    endDate: string;
    status: string;
    capacity: number;
    plannedStoryPoints: number;
  };
  tasksUpdated: number;
  assignmentsApplied: number;
  closedSprint?: {
    id: number;
    name: string;
    status: string;
  };
}

export const useSmartSprintStore = defineStore('smartSprint', () => {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const planningResult = ref<SprintPlanResult | null>(null);
  const selectedStrategy = ref<string>('hybrid');
  const strategies = ref<SprintStrategy[]>([]);
  const applyingPlan = ref(false);

  // Load available strategies
  async function loadStrategies(projectId: number): Promise<SprintStrategy[] | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get<{ strategies: SprintStrategy[]; defaultStrategy: string }>(
        `/projects/${projectId}/sprint-strategies`
      );

      strategies.value = response.strategies;
      selectedStrategy.value = response.defaultStrategy;

      return response.strategies;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load strategies';
      console.error('Failed to load strategies:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Generate sprint plan
  async function generateSprintPlan(
    projectId: number,
    config: SprintPlanConfig
  ): Promise<SprintPlanResult | null> {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.post<SprintPlanResult>(
        `/projects/${projectId}/smart-sprint-planning`,
        config
      );

      planningResult.value = response;

      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to generate sprint plan';
      console.error('Failed to generate sprint plan:', err);
      planningResult.value = null;
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Apply sprint plan
  async function applySprintPlan(
    projectId: number,
    request: ApplySprintPlanRequest
  ): Promise<ApplySprintPlanResponse | null> {
    applyingPlan.value = true;
    error.value = null;

    try {
      const response = await api.post<ApplySprintPlanResponse>(
        `/projects/${projectId}/apply-sprint-plan`,
        request
      );

      // Clear planning result after successful application
      if (response.success) {
        planningResult.value = null;
      }

      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to apply sprint plan';
      console.error('Failed to apply sprint plan:', err);
      return null;
    } finally {
      applyingPlan.value = false;
    }
  }

  // Clear plan
  function clearPlan() {
    planningResult.value = null;
    error.value = null;
  }

  // Set selected strategy
  function setStrategy(strategy: string) {
    selectedStrategy.value = strategy;
  }

  return {
    loading,
    error,
    planningResult,
    selectedStrategy,
    strategies,
    applyingPlan,
    loadStrategies,
    generateSprintPlan,
    applySprintPlan,
    clearPlan,
    setStrategy,
  };
});

