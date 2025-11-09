<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-gradient-primary q-pa-lg shadow-2">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-white q-ma-none">
            <q-icon name="auto_fix_high" size="36px" class="q-mr-sm" />
            Project Optimization
          </h4>
          <p class="text-white q-ma-none q-mt-sm opacity-90">
            Intelligent analysis with 12 optimization types
          </p>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Loading Skeleton -->
      <div v-if="initialLoading">
        <q-card class="q-mb-lg shadow-3">
          <q-card-section>
            <div class="row items-center q-gutter-md">
              <div class="col-auto">
                <q-skeleton type="QAvatar" size="48px" />
              </div>
              <div class="col">
                <q-skeleton type="text" width="100px" class="q-mb-xs" />
                <q-skeleton type="rect" height="40px" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Project Selection & Actions -->
      <q-card v-else class="q-mb-lg shadow-3">
            <q-card-section>
          <div class="row items-center q-gutter-md">
            <div class="col-auto">
              <q-icon name="folder_open" size="48px" color="primary" />
            </div>
            <div class="col">
              <div class="text-overline text-grey-7">SELECT PROJECT</div>
                <q-select
                  v-model="selectedProjectId"
                  :options="projectOptions"
                  emit-value
                  map-options
                outlined
                  dense
                @update:model-value="onProjectChange"
                style="min-width: 350px; max-width: 500px"
                class="text-h6"
                  :loading="initialLoading"
                  :disable="initialLoading"
                >
                  <template v-slot:prepend>
                  <q-icon name="folder" color="primary" />
                  </template>
                </q-select>
              </div>

            <div class="col-auto" v-if="selectedProject && !initialLoading">
              <div class="row q-gutter-sm">
                <q-chip icon="task" color="primary" text-color="white" size="md">
                  {{ selectedProject.tasks?.length || 0 }} Tasks
                </q-chip>
                <q-chip icon="group" color="green" text-color="white" size="md">
                  {{ selectedProject.teamMemberIds?.length || 0 }} Members
                </q-chip>
                <q-chip icon="event" color="orange" text-color="white" size="md">
                  {{ selectedProject.sprints?.length || 0 }} Sprints
                </q-chip>
              </div>
              </div>
              </div>
        </q-card-section>
        
        <q-separator />
        
        <q-card-actions class="q-pa-md">
          <q-btn
            color="orange"
            icon="refresh"
            label="Clear"
            @click="clearAnalysis"
            :disable="!hasAnalysis || initialLoading"
            flat
          />
        </q-card-actions>
          </q-card>

      <!-- Empty State - No Project Selected -->
      <q-card v-if="!selectedProject && !initialLoading" class="q-mb-lg shadow-2 text-center q-pa-xl">
        <q-icon name="folder_open" size="64px" color="grey-5" class="q-mb-md" />
        <div class="text-h6 text-grey-6 q-mb-sm">Select a Project to Begin</div>
        <div class="text-body2 text-grey-7">
          Choose a project from the dropdown above to analyze and optimize its planning
        </div>
      </q-card>

      <!-- Current State Display -->
      <q-card v-if="selectedProject && currentState && !initialLoading" class="q-mb-lg shadow-2">
        <q-card-section class="bg-blue-1">
          <div class="text-h6 text-weight-bold">Current Project State</div>
        </q-card-section>
            <q-card-section>
          <div class="row q-col-gutter-md">
            <!-- Duration Card -->
            <div class="col-6 col-md-3">
              <div class="stat-card clickable">
                <q-icon name="schedule" size="32px" color="blue" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.duration }}d</div>
                <div class="text-caption text-grey-7">Duration</div>
                <q-tooltip max-width="300px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Project Duration Breakdown</div>
                  <div>Total Sprints: {{ currentState.sprintCount || 0 }}</div>
                  <div>Estimated Duration: {{ currentState.duration }}d</div>
                  <div class="q-mt-sm text-caption">
                    Based on sprint capacity and task estimates
                  </div>
                </q-tooltip>
                      </div>
                    </div>

            <!-- Workload Card -->
            <div class="col-6 col-md-3">
              <div class="stat-card clickable">
                <q-icon name="assessment" size="32px" color="orange" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.workload }}%</div>
                <div class="text-caption text-grey-7">Avg Workload</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Team Workload Distribution</div>
                  <div v-if="teamWorkloadDetails.length > 0">
                    <div v-for="member in teamWorkloadDetails" :key="member.id" class="q-mb-xs">
                      <div class="row items-center justify-between">
                        <span>{{ member.name }}:</span>
                        <span class="text-weight-bold" :class="getWorkloadColorClass(member.workload)">
                          {{ member.workload }}%
                        </span>
                      </div>
                      <q-linear-progress 
                        :value="Math.min(1, member.workload / 100)" 
                        :color="getWorkloadColor(member.workload)"
                        size="4px"
                        class="q-mt-xs"
                      />
                    </div>
                      </div>
                  <div v-else class="text-caption text-grey-5">
                    No team members assigned
                    </div>
                </q-tooltip>
                  </div>
                </div>

            <!-- Risk Score Card -->
            <div class="col-6 col-md-3">
              <div class="stat-card clickable">
                <q-icon name="warning" size="32px" color="red" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.riskScore }}/10</div>
                <div class="text-caption text-grey-7">Risk Score</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Risk Score Breakdown</div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Deadline Risks:</span>
                      <span class="text-weight-bold">{{ riskBreakdown.deadlineRisks }}</span>
                </div>
                    </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Overloaded Members:</span>
                      <span class="text-weight-bold">{{ riskBreakdown.overloadedMembers }}</span>
                  </div>
                        </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Blocked Tasks:</span>
                      <span class="text-weight-bold">{{ riskBreakdown.blockedTasks }}</span>
                      </div>
                    </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Large Tasks (21+ SP):</span>
                      <span class="text-weight-bold">{{ riskBreakdown.largeTasks }}</span>
                        </div>
                      </div>
                  <q-separator class="q-my-sm" />
                  <div class="text-caption text-grey-5">
                    Higher score = Higher risk. Scale: 0-10
                    </div>
                </q-tooltip>
                        </div>
                      </div>

            <!-- Balance Card -->
            <div class="col-6 col-md-3">
              <div class="stat-card clickable">
                <q-icon name="balance" size="32px" color="green" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.balanceScore }}%</div>
                <div class="text-caption text-grey-7">Balance</div>
                <q-tooltip max-width="300px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Team Balance Score</div>
                  <div class="q-mb-sm">
                    Measures how evenly work is distributed across the team.
                    </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Min Workload:</span>
                      <span class="text-weight-bold">{{ balanceDetails.minWorkload }}%</span>
                        </div>
                      </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Max Workload:</span>
                      <span class="text-weight-bold">{{ balanceDetails.maxWorkload }}%</span>
                    </div>
                  </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Difference:</span>
                      <span class="text-weight-bold">{{ balanceDetails.difference }}%</span>
                </div>
              </div>
                  <q-separator class="q-my-sm" />
                  <div class="text-caption text-grey-5">
                    100% = Perfect balance, 0% = Highly imbalanced
                  </div>
                </q-tooltip>
                  </div>
                    </div>
                  </div>
        </q-card-section>
              </q-card>

      <!-- Tabs for Backlog vs Current Sprint -->
      <q-card v-if="selectedProject && !initialLoading" class="shadow-3">
        <q-tabs
          v-model="activeTab"
          dense
          class="text-grey"
          active-color="primary"
          indicator-color="primary"
          align="justify"
        >
          <q-tab name="backlog" icon="inventory_2" label="Backlog" />
          <q-tab 
            name="current_sprint" 
            icon="today" 
            label="Current Sprint"
            :disable="!hasActiveSprint"
          >
            <q-tooltip v-if="!hasActiveSprint">
              No active sprint available
            </q-tooltip>
          </q-tab>
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="activeTab" animated>
          <!-- Backlog Tab -->
          <q-tab-panel name="backlog">
            <div class="q-pa-md">
              <div class="row items-center justify-between q-mb-lg">
                <div>
                  <div class="text-h5 text-weight-bold">Backlog Analysis</div>
                  <div class="text-caption text-grey-7">
                    Complete project optimization across all sprints
                          </div>
                        </div>
                <q-btn
                  color="secondary"
                  icon="auto_fix_high"
                  label="Analyze & Optimize"
                  @click="analyzeTab('all_sprints')"
                  :loading="requirementChangeStore.loading"
                  :disable="!selectedProjectId || initialLoading"
                  size="lg"
                  unelevated
                />
                      </div>

              <!-- Loading State -->
              <div v-if="requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-spinner-dots color="primary" size="48px" class="q-mb-md" />
                <div class="text-h6 text-grey-7">Analyzing Project...</div>
                <div class="text-body2 text-grey-6">
                  Searching for optimization opportunities
                </div>
              </div>

              <optimization-proposals
                v-else-if="hasProposals"
                :proposals="proposals"
                :selected-proposals="requirementChangeStore.selectedProposals"
                @toggle-selection="requirementChangeStore.toggleProposalSelection"
                @select-all="requirementChangeStore.selectAllProposals"
                @deselect-all="requirementChangeStore.deselectAllProposals"
              />

              <div v-else-if="hasAnalysis" class="text-center q-pa-xl">
                <q-icon name="check_circle" size="64px" color="green" class="q-mb-md" />
                <div class="text-h6">All Good!</div>
                <div class="text-body2 text-grey-7">
                  No optimization opportunities found. Your project is well-balanced.
                    </div>
                  </div>

              <div v-else-if="!requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-icon name="analytics" size="64px" color="grey-5" class="q-mb-md" />
                <div class="text-h6 text-grey-6">Ready to Optimize</div>
                <div class="text-body2 text-grey-7">
                  Click "Analyze & Optimize" to find all opportunities
                          </div>
                        </div>
                      </div>
          </q-tab-panel>

          <!-- Current Sprint Tab -->
          <q-tab-panel name="current_sprint">
            <div class="q-pa-md">
              <div class="row items-center justify-between q-mb-lg">
                <div>
                  <div class="text-h5 text-weight-bold">Current Sprint Analysis</div>
                  <div class="text-caption text-grey-7">
                    Focus on active sprint optimization
                          </div>
                        </div>
                <q-btn
                  color="secondary"
                  icon="auto_fix_high"
                  label="Analyze & Optimize"
                  @click="analyzeTab('current_sprint')"
                  :loading="requirementChangeStore.loading"
                  :disable="!selectedProjectId || initialLoading"
                  size="lg"
                  unelevated
                />
                      </div>

              <!-- Loading State -->
              <div v-if="requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-spinner-dots color="primary" size="48px" class="q-mb-md" />
                <div class="text-h6 text-grey-7">Analyzing Sprint...</div>
                <div class="text-body2 text-grey-6">
                  Searching for optimization opportunities
                </div>
              </div>

              <optimization-proposals
                v-else-if="hasProposals"
                :proposals="proposals"
                :selected-proposals="requirementChangeStore.selectedProposals"
                @toggle-selection="requirementChangeStore.toggleProposalSelection"
                @select-all="requirementChangeStore.selectAllProposals"
                @deselect-all="requirementChangeStore.deselectAllProposals"
              />

              <div v-else-if="hasAnalysis" class="text-center q-pa-xl">
                <q-icon name="check_circle" size="64px" color="green" class="q-mb-md" />
                <div class="text-h6">Sprint is Optimized!</div>
                <div class="text-body2 text-grey-7">
                  No optimization opportunities found in current sprint.
                    </div>
                  </div>

              <div v-else-if="!requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-icon name="analytics" size="64px" color="grey-5" class="q-mb-md" />
                <div class="text-h6 text-grey-6">Ready to Optimize</div>
                <div class="text-body2 text-grey-7">
                  Click "Analyze & Optimize" to find sprint opportunities
                          </div>
                        </div>
                      </div>
          </q-tab-panel>
        </q-tab-panels>
              </q-card>

      <!-- Apply Changes Sticky Footer -->
      <q-page-sticky v-if="hasSelectedProposals" position="bottom" :offset="[0, 18]">
        <q-card class="apply-footer shadow-up-8">
          <q-card-section class="bg-primary text-white q-pa-md">
            <div class="row items-center">
              <div class="col">
                <div class="text-h6 text-weight-bold">
                  <q-icon name="check_circle" size="24px" class="q-mr-sm" />
                  {{ selectedProposalCount }} Changes Ready
        </div>
                <div class="text-body2">Review and apply selected optimizations</div>
      </div>
              <div class="col-auto">
            <q-btn
                  color="white"
                  text-color="primary"
                  label="Apply Changes"
                  icon-right="arrow_forward"
                  size="lg"
                  @click="showApplyDialog = true"
                  :loading="applyingChanges"
                  unelevated
            />
          </div>
                </div>
          </q-card-section>
              </q-card>
      </q-page-sticky>
          </div>

    <!-- Apply Confirmation Dialog -->
    <q-dialog v-model="showApplyDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Confirm Changes</div>
        </q-card-section>

        <q-card-section>
          <div class="text-body1 q-mb-md">
            You are about to apply {{ selectedProposalCount }} optimization changes. This will:
          </div>

          <q-list dense bordered separator class="rounded-borders">
            <q-item
              v-for="proposal in requirementChangeStore.getSelectedProposals()"
              :key="proposal.id"
              class="q-pa-md"
            >
              <q-item-section avatar>
                <q-icon
                  :name="getProposalIcon(proposal.type)"
                  :color="getSeverityColor(proposal.severity)"
                  size="24px"
                />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-medium">{{ proposal.title }}</q-item-label>
                <q-item-label caption>{{ proposal.description }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-badge :color="getSeverityColor(proposal.severity)" :label="proposal.severity" />
              </q-item-section>
            </q-item>
          </q-list>

          <div class="text-caption text-grey-7 q-mt-md">
            <q-icon name="info" size="16px" />
            These changes will be immediately applied to your project.
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" color="grey" @click="showApplyDialog = false" />
            <q-btn
            label="Apply All Changes"
              color="primary"
            @click="applyChanges"
            :loading="applyingChanges"
            unelevated
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';
import { useRequirementChangeStore } from 'src/stores/requirement-change-store';
import OptimizationProposals from 'src/components/OptimizationProposals.vue';

const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();
const requirementChangeStore = useRequirementChangeStore();

// Load data on mount
const initialLoading = ref(true);

onMounted(async () => {
  try {
    await Promise.all([
      projectStore.fetchProjects(true),
      teamStore.fetchTeamMembers()
    ]);
  } finally {
    initialLoading.value = false;
  }
});

// State
const selectedProjectId = ref<number | null>(null);
const activeTab = ref('backlog'); // Default to backlog
const showApplyDialog = ref(false);
const applyingChanges = ref(false);

// Computed
const projectOptions = computed(() => {
  return projectStore.projects.map((project) => ({
    label: project.name,
    value: project.id,
  }));
});

const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null;
  return projectStore.projects.find((p) => p.id === selectedProjectId.value);
});

const hasAnalysis = computed(() => !!requirementChangeStore.analysisResult);
const hasProposals = computed(
  () => (requirementChangeStore.analysisResult?.proposals?.length ?? 0) > 0
);
const hasSelectedProposals = computed(
  () => requirementChangeStore.selectedProposals.length > 0
);
const selectedProposalCount = computed(() => requirementChangeStore.selectedProposals.length);

const proposals = computed(() => requirementChangeStore.analysisResult?.proposals || []);

// Dynamic current state calculations (always show real-time data)
const currentState = computed(() => {
  if (!selectedProject.value) return null;

  // Calculate duration from sprints
  const sprints = selectedProject.value.sprints || [];
  const duration = sprints.reduce((total, sprint) => {
    if (sprint.startDate && sprint.endDate) {
      const start = typeof sprint.startDate === 'string' ? new Date(sprint.startDate) : sprint.startDate;
      const end = typeof sprint.endDate === 'string' ? new Date(sprint.endDate) : sprint.endDate;
      const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      return total + days;
    }
    return total;
  }, 0);

  // Calculate average workload from team members (similar to WorkloadDashboardPage)
  const members = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );
  
  let totalWorkload = 0;
  members.forEach((member) => {
    const maxStoryPoints = member.maxStoryPoints || 20;
    const tasks = (selectedProject.value?.tasks || []).filter((task) => {
      const isAssigned =
        (task.raci?.responsible && task.raci.responsible.includes(member.id)) ||
        task.raci?.accountable === member.id;
      const isIncomplete = task.status !== 'Done';
      return isAssigned && isIncomplete;
    });
    const memberStoryPoints = tasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
    const memberWorkload = maxStoryPoints > 0 ? (memberStoryPoints / maxStoryPoints) * 100 : 0;
    totalWorkload += memberWorkload;
  });
  const workload = members.length > 0 ? Math.round(totalWorkload / members.length) : 0;

  // Calculate risk score (0-10 scale based on multiple factors)
  const risks = riskBreakdown.value;
  const riskScore = Math.min(10, Math.round(
    (risks.deadlineRisks * 0.3) +
    (risks.overloadedMembers * 0.4) +
    (risks.blockedTasks * 0.2) +
    (risks.largeTasks * 0.1)
  ));

  // Calculate balance score (0-100%, higher is better)
  const workloads = teamWorkloadDetails.value.map((m) => m.workload);
  let balanceScore = 100;
  if (workloads.length > 1) {
    const min = Math.min(...workloads);
    const max = Math.max(...workloads);
    const variance = max - min;
    // If variance is high, balance is low
    balanceScore = Math.max(0, Math.round(100 - variance));
  }

  return {
    duration: duration || 0,
    workload,
    riskScore,
    balanceScore,
    totalStoryPoints: (selectedProject.value.tasks || []).reduce((sum, t) => sum + (t.storyPoints || 0), 0),
    completedStoryPoints: (selectedProject.value.tasks || [])
      .filter((t) => t.status === 'Done')
      .reduce((sum, t) => sum + (t.storyPoints || 0), 0),
    teamCapacity: members.reduce((sum, m) => sum + (m.maxStoryPoints || 20), 0),
    taskCount: (selectedProject.value.tasks || []).length,
    sprintCount: sprints.length,
  };
});

const hasActiveSprint = computed(() => {
  if (!selectedProject.value?.sprints) return false;
  return selectedProject.value.sprints.some((sprint) => sprint.status === 'active');
});

const teamWorkloadDetails = computed(() => {
  if (!selectedProject.value) return [];
  
  const members = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  return members.map((member) => ({
    id: member.id,
    name: member.name,
    workload: Math.round((member.workload || 0) * 100) / 100,
  })).sort((a, b) => b.workload - a.workload);
});

const riskBreakdown = computed(() => {
  if (!selectedProject.value) {
    return {
      deadlineRisks: 0,
      overloadedMembers: 0,
      blockedTasks: 0,
      largeTasks: 0,
    };
  }

  const tasks = selectedProject.value.tasks || [];
  const members = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  return {
    deadlineRisks: tasks.filter((t) => t.dueDate && new Date(t.dueDate) < new Date()).length,
    overloadedMembers: members.filter((m) => (m.workload || 0) > 85).length,
    blockedTasks: tasks.filter((t) => t.dependencies && t.dependencies.length > 0).length,
    largeTasks: tasks.filter((t) => (t.storyPoints || 0) >= 21).length,
  };
});

const balanceDetails = computed(() => {
  const workloads = teamWorkloadDetails.value.map((m) => m.workload);
  
  if (workloads.length === 0) {
    return { minWorkload: 0, maxWorkload: 0, difference: 0 };
  }

  const min = Math.min(...workloads);
  const max = Math.max(...workloads);
  
  return {
    minWorkload: Math.round(min * 100) / 100,
    maxWorkload: Math.round(max * 100) / 100,
    difference: Math.round((max - min) * 100) / 100,
  };
});

// Methods
function onProjectChange() {
  requirementChangeStore.clearAnalysis();
  activeTab.value = 'backlog';
}

function getWorkloadColor(workload: number): string {
  if (workload >= 90) return 'red';
  if (workload >= 75) return 'orange';
  if (workload >= 50) return 'yellow';
  return 'green';
}

function getWorkloadColorClass(workload: number): string {
  if (workload >= 90) return 'text-red';
  if (workload >= 75) return 'text-orange';
  if (workload >= 50) return 'text-yellow-8';
  return 'text-green';
}

async function analyzeTab(scope: 'current_sprint' | 'all_sprints') {
  if (!selectedProjectId.value) return;

  const result = await requirementChangeStore.autoOptimizeProject(
    selectedProjectId.value,
    scope
  );

  if (result) {
  $q.notify({
      message: result.message || `Found ${result.totalProposals || 0} opportunities`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
      timeout: 3000,
  });
  }
}

function clearAnalysis() {
  requirementChangeStore.clearAnalysis();
    $q.notify({
    message: 'Analysis cleared',
    color: 'info',
    icon: 'refresh',
      position: 'top',
    });
}

async function applyChanges() {
  if (!selectedProjectId.value) return;

  applyingChanges.value = true;

  try {
    const selectedProposals = requirementChangeStore.getSelectedProposals();
    const success = await requirementChangeStore.applyChanges(
      selectedProjectId.value,
      selectedProposals
    );

    if (success) {
  $q.notify({
        message: `Successfully applied ${selectedProposalCount.value} changes!`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
        timeout: 4000,
      });

      showApplyDialog.value = false;
      await projectStore.getProject(selectedProjectId.value);
      requirementChangeStore.clearAnalysis();
    } else {
  $q.notify({
        message: 'Some changes failed. Check console for details.',
        color: 'negative',
        icon: 'error',
    position: 'top',
  });
}
  } finally {
    applyingChanges.value = false;
  }
}

function getProposalIcon(type: string): string {
  const icons: Record<string, string> = {
    split: 'call_split',
    merge: 'merge',
    reassign: 'swap_horiz',
    sprint_move: 'event_note',
    bottleneck: 'warning',
    priority_conflict: 'priority_high',
    deadline_risk: 'alarm',
    skill_mismatch: 'psychology',
    cross_sprint_dep: 'link_off',
    parallel_opportunity: 'device_hub',
    idle_resource: 'person_off',
  };
  return icons[type] || 'change_circle';
}

function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    critical: 'red',
    important: 'orange',
    recommended: 'blue',
  };
  return colors[severity] || 'grey';
}

</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.stat-card.clickable {
  cursor: help;
}

.stat-card.clickable:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.apply-footer {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.shadow-up-8 {
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.15);
}

.opacity-90 {
  opacity: 0.9;
}
</style>
