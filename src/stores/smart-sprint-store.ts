import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
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
  pertHours?: number; // PERT strategies: expected hours
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
  totalHours?: number;
  pertMode?: boolean;
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

  // Editable plan state (synced from planningResult, user can modify before apply)
  const editableTasks = ref<SprintTask[]>([]);
  const editableAssignments = ref<Record<string, TaskAssignment>>({});

  function syncEditableFromPlan() {
    if (!planningResult.value) {
      editableTasks.value = [];
      editableAssignments.value = {};
      return;
    }
    editableTasks.value = [...planningResult.value.suggestedTasks];
    editableAssignments.value = { ...planningResult.value.assignments };
  }

  function updateTaskAssignment(
    taskId: number,
    memberId: number | null,
    memberName?: string
  ) {
    const key = String(taskId);
    if (memberId == null || memberName == null) {
      if (key in editableAssignments.value) {
        const rest = { ...editableAssignments.value };
        delete rest[key];
        editableAssignments.value = rest;
      }
      return;
    }
    const task = editableTasks.value.find((t) => t.id === taskId);
    if (!task) return;
    const existing = editableAssignments.value[key];
    const pertHours = existing?.pertHours;
    editableAssignments.value = {
      ...editableAssignments.value,
      [key]: {
        taskId,
        taskName: task.name || task.title,
        memberId,
        memberName,
        role: 'responsible',
        storyPoints: task.storyPoints || 0,
        ...(pertHours != null ? { pertHours } : {}),
      },
    };
  }

  function removeTaskFromPlan(taskId: number) {
    editableTasks.value = editableTasks.value.filter((t) => t.id !== taskId);
    const key = String(taskId);
    if (key in editableAssignments.value) {
      const rest = { ...editableAssignments.value };
      delete rest[key];
      editableAssignments.value = rest;
    }
  }

  function addTaskToPlan(
    task: SprintTask,
    memberId?: number,
    memberName?: string
  ) {
    if (editableTasks.value.some((t) => t.id === task.id)) return;
    editableTasks.value = [...editableTasks.value, task];
    if (memberId != null && memberName) {
      editableAssignments.value = {
        ...editableAssignments.value,
        [String(task.id)]: {
          taskId: task.id,
          taskName: task.name || task.title,
          memberId,
          memberName,
          role: 'responsible',
          storyPoints: task.storyPoints || 0,
        },
      };
    }
  }

  // Recalculated metrics and team analysis based on editable state
  const editableMetrics = computed<SprintMetrics | null>(() => {
    const plan = planningResult.value;
    if (!plan?.metrics) return null;

    const totalStoryPoints = editableTasks.value.reduce(
      (sum, t) => sum + (t.storyPoints || 0),
      0
    );
    const taskCount = editableTasks.value.length;
    const teamCapacity = plan.metrics.teamCapacity;

    const priorityDistribution = { high: 0, medium: 0, low: 0 };
    for (const t of editableTasks.value) {
      const p = (t.priority || 'medium').toLowerCase();
      if (p in priorityDistribution) {
        priorityDistribution[p as keyof typeof priorityDistribution]++;
      }
    }

    // Member workloads from assignments (SP or hours per member in this sprint)
    const pertMode = plan.metrics.pertMode ?? false;
    const memberWorkloads: Record<number, number> = {};
    for (const a of Object.values(editableAssignments.value)) {
      const workload = pertMode ? (a.pertHours ?? 0) : a.storyPoints;
      memberWorkloads[a.memberId] = (memberWorkloads[a.memberId] || 0) + workload;
    }

    const totalWorkload = pertMode
      ? Object.values(memberWorkloads).reduce((s, w) => s + w, 0)
      : totalStoryPoints;
    const utilization =
      teamCapacity > 0 ? (totalWorkload / teamCapacity) * 100 : 0;

    // Balance score: lower variance in workload % = higher score
    const members = plan.teamAnalysis?.members ?? [];
    let balanceScore = 100;
    if (members.length >= 2 && Object.keys(memberWorkloads).length > 0) {
      const considerCross = plan.teamAnalysis?.considerCrossProject ?? false;
      const workloadPcts: number[] = [];
      for (const m of members) {
        let workload = memberWorkloads[m.memberId] || 0;
        if (considerCross) workload += m.crossProjectWorkload || 0;
        const pct =
          m.maxCapacity > 0 ? (workload / m.maxCapacity) * 100 : 0;
        workloadPcts.push(pct);
      }
      const avg = workloadPcts.reduce((s, x) => s + x, 0) / workloadPcts.length;
      const variance =
        workloadPcts.reduce((s, x) => s + (x - avg) ** 2, 0) /
        workloadPcts.length;
      const stdDev = Math.sqrt(variance);
      balanceScore = Math.max(0, 100 - stdDev * 2);
    }

    return {
      ...plan.metrics,
      totalStoryPoints,
      ...(pertMode ? { totalHours: Math.round(totalWorkload * 10) / 10 } : {}),
      taskCount,
      utilization: Math.round(utilization * 10) / 10,
      balanceScore: Math.round(balanceScore * 10) / 10,
      priorityDistribution,
    };
  });

  const editableTeamAnalysis = computed<TeamAnalysis | null>(() => {
    const plan = planningResult.value;
    const analysis = plan?.teamAnalysis;
    if (!analysis) return null;

    const pertMode = plan.metrics.pertMode ?? false;
    const memberSprintWorkload: Record<number, number> = {};
    for (const a of Object.values(editableAssignments.value)) {
      const w = pertMode ? (a.pertHours ?? 0) : a.storyPoints;
      memberSprintWorkload[a.memberId] = (memberSprintWorkload[a.memberId] || 0) + w;
    }

    const members: TeamMemberAnalysis[] = analysis.members.map((m) => {
      const sprintSp = memberSprintWorkload[m.memberId] || 0;
      const crossSp = m.crossProjectWorkload || 0;
      const totalSp = crossSp + sprintSp;
      const availableSp = Math.max(0, m.maxCapacity - totalSp);
      const utilPct =
        m.maxCapacity > 0 ? (totalSp / m.maxCapacity) * 100 : 0;

      let status: TeamMemberAnalysis['status'] = 'available';
      if (totalSp >= m.maxCapacity) status = 'at_capacity';
      else if (totalSp > m.maxCapacity * 0.9) status = 'nearly_full';
      else if (sprintSp > 0) status = 'assigned';

      let reason: string;
      if (sprintSp === 0) {
        if (pertMode) {
          reason = 'Not assigned - tasks matched better with other team members';
        } else if (analysis.considerCrossProject && crossSp > 0) {
          reason = `Not assigned - has ${crossSp} SP in other projects`;
        } else if (totalSp >= m.maxCapacity) {
          reason = 'Not assigned - at maximum capacity';
        } else {
          reason = 'Not assigned - tasks matched better with other team members';
        }
      } else {
        if (pertMode) {
          reason = `Assigned ${sprintSp.toFixed(1)}h`;
        } else if (analysis.considerCrossProject && crossSp > 0) {
          reason = `Assigned ${sprintSp} SP (considering ${crossSp} SP from other projects)`;
        } else {
          reason = `Assigned ${sprintSp} SP`;
        }
      }

      return {
        ...m,
        assignedInThisSprint: sprintSp,
        totalWorkload: totalSp,
        availableCapacity: availableSp,
        utilizationPercentage: utilPct,
        status,
        reason,
        taskCount: Object.values(editableAssignments.value).filter(
          (a) => a.memberId === m.memberId
        ).length,
      };
    });

    members.sort((a, b) => b.totalWorkload - a.totalWorkload);

    return {
      ...analysis,
      members,
      summary: {
        totalMembers: analysis.summary.totalMembers,
        assignedMembers: members.filter((m) => m.assignedInThisSprint > 0)
          .length,
        atCapacity: members.filter((m) => m.status === 'at_capacity').length,
        available: members.filter((m) => m.status === 'available').length,
      },
    };
  });

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
      syncEditableFromPlan();

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
    syncEditableFromPlan();
  }

  // Set selected strategy
  function setStrategy(strategy: string) {
    selectedStrategy.value = strategy;
  }

  return {
    loading,
    error,
    planningResult,
    editableTasks,
    editableAssignments,
    editableMetrics,
    editableTeamAnalysis,
    selectedStrategy,
    strategies,
    applyingPlan,
    loadStrategies,
    generateSprintPlan,
    applySprintPlan,
    clearPlan,
    setStrategy,
    syncEditableFromPlan,
    updateTaskAssignment,
    removeTaskFromPlan,
    addTaskToPlan,
  };
});

