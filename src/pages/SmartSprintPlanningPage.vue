<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-gradient-primary q-pa-lg shadow-2">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-white q-ma-none">
            <q-icon name="auto_awesome" size="36px" class="q-mr-sm" />
            Smart Sprint Planning
          </h4>
          <p class="text-white q-ma-none q-mt-sm opacity-90">
            AI-powered sprint planning with multiple optimization strategies
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            v-if="hasGeneratedPlan"
            color="white"
            text-color="primary"
            icon="refresh"
            label="Regenerate"
            @click="onRegenerate"
            :loading="smartSprintStore.loading"
            unelevated
          />
          <q-btn
            v-if="hasGeneratedPlan"
            color="green"
            icon="check_circle"
            label="Apply Plan"
            @click="onApplyPlan"
            :loading="smartSprintStore.applyingPlan"
            unelevated
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Project Selection -->
      <q-card class="q-mb-lg shadow-3">
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
              >
                <template v-slot:prepend>
                  <q-icon name="folder" color="primary" />
                </template>
              </q-select>
            </div>
            <div class="col-auto" v-if="selectedProject">
              <div class="row q-gutter-sm">
                <q-chip icon="task" color="primary" text-color="white" size="md">
                  {{ eligibleTasksCount }} Available Tasks
                </q-chip>
                <q-chip icon="group" color="green" text-color="white" size="md">
                  {{ selectedProject.teamMemberIds?.length || 0 }} Members
                </q-chip>
              </div>
            </div>
          </div>
        </q-card-section>

        <!-- Cross-Project Workload Consideration -->
        <q-card-section v-if="selectedProject" class="q-pt-none">
          <q-checkbox
            v-model="considerCrossProject"
            color="primary"
            label="Consider workload from other projects"
          >
            <q-tooltip max-width="400px">
              When enabled, the planner will take into account team members' existing workload from
              active sprints in other projects. This helps prevent overloading team members who work
              on multiple projects simultaneously.
            </q-tooltip>
          </q-checkbox>
          <div class="text-caption text-grey-7 q-ml-lg">
            <q-icon name="info" size="14px" />
            Recommended: Keep enabled to ensure realistic workload distribution across all projects
          </div>
        </q-card-section>
      </q-card>

      <!-- No Project Selected -->
      <q-card v-if="!selectedProject" class="q-mb-lg shadow-2 text-center q-pa-xl">
        <q-icon name="folder_open" size="64px" color="grey-5" class="q-mb-md" />
        <div class="text-h6 text-grey-6 q-mb-sm">Select a Project to Begin</div>
        <div class="text-body2 text-grey-7">
          Choose a project from the dropdown above to start intelligent sprint planning
        </div>
      </q-card>

      <!-- Active Sprint Warning -->
      <q-banner
        v-if="selectedProject && activeSprint"
        class="bg-orange-1 q-mb-lg"
        rounded
      >
        <template v-slot:avatar>
          <q-icon name="warning" color="orange" size="32px" />
        </template>
        <div class="text-weight-bold">Active Sprint Detected</div>
        <div class="text-body2">
          Sprint "{{ activeSprint.name }}" is currently active. You can either plan a new sprint
          with remaining tasks or close the active sprint and replan all tasks.
        </div>
        <template v-slot:action>
          <q-checkbox
            v-model="closeActiveSprint"
            label="Close active sprint when applying"
            color="orange"
          />
        </template>
      </q-banner>

      <!-- Configuration Section -->
      <q-card v-if="selectedProject && !hasGeneratedPlan" class="q-mb-lg shadow-3">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6 text-weight-bold">
            <q-icon name="settings" class="q-mr-sm" />
            Sprint Configuration
          </div>
        </q-card-section>

        <q-card-section>
          <div class="row q-col-gutter-md">
            <!-- Sprint Name -->
            <div class="col-12 col-md-6">
              <q-input
                v-model="sprintName"
                label="Sprint Name *"
                outlined
                dense
                :rules="[(val) => !!val || 'Sprint name is required']"
              >
                <template #prepend>
                  <q-icon name="label" />
                </template>
              </q-input>
            </div>

            <!-- Sprint Duration -->
            <div class="col-12 col-md-6">
              <q-input
                v-model.number="sprintDuration"
                label="Sprint Duration (days) *"
                type="number"
                outlined
                dense
                :rules="[(val) => val > 0 || 'Duration must be positive']"
              >
                <template #prepend>
                  <q-icon name="schedule" />
                </template>
              </q-input>
            </div>

            <!-- Start Date -->
            <div class="col-12 col-md-6">
              <q-input
                v-model="startDate"
                label="Start Date *"
                type="date"
                outlined
                dense
                :rules="[(val) => !!val || 'Start date is required']"
              >
                <template #prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>

            <!-- End Date -->
            <div class="col-12 col-md-6">
              <q-input
                v-model="endDate"
                label="End Date *"
                type="date"
                outlined
                dense
                :rules="[(val) => !!val || 'End date is required']"
                :disable="true"
              >
                <template #prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>

            <!-- Sprint Goal -->
            <div class="col-12">
              <q-input
                v-model="sprintGoal"
                label="Sprint Goal (optional)"
                type="textarea"
                outlined
                rows="2"
                dense
              >
                <template #prepend>
                  <q-icon name="flag" />
                </template>
              </q-input>
            </div>

            <!-- Target Utilization -->
            <div class="col-12">
              <div class="text-subtitle2 q-mb-sm">
                Target Team Utilization: {{ targetUtilization }}%
              </div>
              <q-slider
                v-model="targetUtilization"
                :min="50"
                :max="100"
                :step="5"
                label
                label-always
                color="primary"
                markers
              />
              <div class="text-caption text-grey-7">
                Recommended: 80-85% for sustainable pace, higher for urgent sprints
              </div>
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <!-- Strategy Selection -->
        <q-card-section class="bg-blue-1">
          <div class="text-h6 text-weight-bold">
            <q-icon name="psychology" class="q-mr-sm" />
            Planning Strategy
          </div>
        </q-card-section>

        <q-card-section>
          <div class="row q-col-gutter-md">
            <div
              v-for="strategy in smartSprintStore.strategies"
              :key="strategy.id"
              class="col-12 col-md-6 col-lg-4"
            >
              <q-card
                flat
                bordered
                class="strategy-card cursor-pointer"
                :class="{ 'strategy-card-selected': selectedStrategy === strategy.id }"
                @click="selectedStrategy = strategy.id"
              >
                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <q-icon :name="strategy.icon" size="32px" color="primary" class="q-mr-sm" />
                    <div class="text-subtitle1 text-weight-bold">{{ strategy.name }}</div>
                    <q-space />
                    <q-radio
                      v-model="selectedStrategy"
                      :val="strategy.id"
                      color="primary"
                      dense
                    />
                  </div>
                  <div class="text-body2 text-grey-7 q-mb-sm">
                    {{ strategy.description }}
                  </div>
                  <div class="text-caption text-primary">
                    <q-icon name="info" size="14px" />
                    {{ strategy.recommended }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>

        <!-- Advanced Parameters for Hybrid Strategy -->
        <q-card-section v-if="selectedStrategy === 'hybrid' && hybridWeights">
          <q-expansion-item
            label="Advanced: Hybrid Strategy Weights"
            icon="tune"
            header-class="bg-grey-2"
          >
            <q-card flat bordered class="q-mt-sm">
              <q-card-section>
                <div class="text-body2 text-grey-7 q-mb-md">
                  Customize how different factors influence task selection in the hybrid strategy
                </div>
                <div v-for="(value, key) in hybridWeights" :key="key" class="q-mb-md">
                  <div class="text-subtitle2 q-mb-sm">
                    {{ formatWeightLabel(key) }}: {{ value.toFixed(2) }}
                  </div>
                  <q-slider
                    v-model="hybridWeights[key]"
                    :min="0"
                    :max="1"
                    :step="0.05"
                    label
                    label-always
                    color="primary"
                    markers
                  />
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-card-section>

        <q-separator />

        <!-- Generate Button -->
        <q-card-actions class="q-pa-md">
          <q-space />
          <q-btn
            color="primary"
            icon="auto_awesome"
            label="Generate Sprint Plan"
            size="lg"
            @click="onGeneratePlan"
            :loading="smartSprintStore.loading"
            :disable="!canGeneratePlan"
            unelevated
          />
        </q-card-actions>
      </q-card>

      <!-- Planning Results -->
      <div v-if="hasGeneratedPlan && planningResult">
        <!-- Error Display -->
        <q-banner v-if="planningResult.error" class="bg-red-1 q-mb-lg" rounded>
          <template v-slot:avatar>
            <q-icon name="error" color="red" size="32px" />
          </template>
          <div class="text-weight-bold">Planning Error</div>
          <div class="text-body2">{{ planningResult.error }}</div>
        </q-banner>

        <!-- Metrics Overview -->
        <q-card class="q-mb-lg shadow-3">
          <q-card-section class="bg-green-1">
            <div class="text-h6 text-weight-bold">
              <q-icon name="insights" class="q-mr-sm" />
              Sprint Plan Metrics
            </div>
          </q-card-section>

          <q-card-section>
            <div class="row q-col-gutter-md">
              <!-- Total Story Points -->
              <div class="col-6 col-md-3">
                <div class="metric-card">
                  <q-icon name="format_list_numbered" size="32px" color="blue" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ planningResult.metrics.totalStoryPoints }}
                  </div>
                  <div class="text-caption text-grey-7">Total Story Points</div>
                </div>
              </div>

              <!-- Task Count -->
              <div class="col-6 col-md-3">
                <div class="metric-card">
                  <q-icon name="task" size="32px" color="green" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ planningResult.metrics.taskCount }}
                  </div>
                  <div class="text-caption text-grey-7">Tasks Selected</div>
                </div>
              </div>

              <!-- Utilization -->
              <div class="col-6 col-md-3">
                <div class="metric-card cursor-pointer">
                  <q-icon name="speed" size="32px" color="orange" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ planningResult.metrics.utilization.toFixed(1) }}%
                  </div>
                  <div class="text-caption text-grey-7">Team Utilization</div>
                  <q-linear-progress
                    :value="planningResult.metrics.utilization / 100"
                    :color="getUtilizationColor(planningResult.metrics.utilization)"
                    size="8px"
                    class="q-mt-sm"
                  />
                  <q-tooltip max-width="400px" class="bg-dark text-body2">
                    <div class="text-weight-bold q-mb-sm">Team Utilization</div>
                    <div class="q-mb-sm">
                      Percentage of total team capacity being utilized by the selected tasks.
                    </div>
                    <div class="q-mb-xs">
                      <strong>Formula:</strong> (Total SP / Team Capacity) × 100
                    </div>
                    <div class="q-mb-xs">
                      <strong>This Sprint:</strong> {{ planningResult.metrics.totalStoryPoints }} SP
                      / {{ planningResult.metrics.teamCapacity }} SP capacity
                    </div>
                    <div class="q-mt-sm text-caption">
                      <div>
                        <q-icon name="info" size="14px" />
                        <strong>Target Range:</strong>
                      </div>
                      <div>• 70-85%: Ideal sustainable pace</div>
                      <div>• 85-95%: Good utilization</div>
                      <div>• 95-100%: At capacity</div>
                      <div>• >100%: Overloaded (risky)</div>
                    </div>
                  </q-tooltip>
                </div>
              </div>

              <!-- Balance Score -->
              <div class="col-6 col-md-3">
                <div class="metric-card cursor-pointer">
                  <q-icon name="balance" size="32px" color="purple" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ planningResult.metrics.balanceScore.toFixed(1) }}
                  </div>
                  <div class="text-caption text-grey-7">Balance Score</div>
                  <q-linear-progress
                    :value="planningResult.metrics.balanceScore / 100"
                    color="purple"
                    size="8px"
                    class="q-mt-sm"
                  />
                  <q-tooltip max-width="400px" class="bg-dark text-body2">
                    <div class="text-weight-bold q-mb-sm">Workload Balance Score</div>
                    <div class="q-mb-sm">
                      Measures how evenly work is distributed across team members. Higher is better.
                    </div>
                    <div class="q-mb-xs">
                      <strong>How it works:</strong>
                    </div>
                    <div class="q-mb-xs text-caption">
                      • Calculates workload percentage for each member
                    </div>
                    <div class="q-mb-xs text-caption">
                      • Measures variance/spread in workload
                    </div>
                    <div class="q-mb-xs text-caption">
                      • Lower variance = higher score
                    </div>
                    <div class="q-mt-sm">
                      <strong>Score Meaning:</strong>
                    </div>
                    <div class="text-caption">
                      <div>• 90-100: Excellent balance</div>
                      <div>• 70-89: Good balance</div>
                      <div>• 50-69: Moderate imbalance</div>
                      <div>• &lt;50: Significant imbalance</div>
                    </div>
                    <div
                      v-if="planningResult.teamAnalysis"
                      class="q-mt-sm q-pt-sm"
                      style="border-top: 1px solid rgba(255, 255, 255, 0.3)"
                    >
                      <div class="text-caption text-weight-bold">Current Distribution:</div>
                      <div
                        v-for="member in planningResult.teamAnalysis.members.slice(0, 3)"
                        :key="member.memberId"
                        class="text-caption"
                      >
                        {{ member.memberName }}: {{ member.utilizationPercentage.toFixed(0) }}%
                      </div>
                      <div v-if="planningResult.teamAnalysis.members.length > 3" class="text-caption">
                        ... and {{ planningResult.teamAnalysis.members.length - 3 }} more
                      </div>
                    </div>
                  </q-tooltip>
                </div>
              </div>
            </div>
          </q-card-section>

          <!-- Priority Distribution -->
          <q-card-section v-if="planningResult.metrics.priorityDistribution">
            <div class="text-subtitle2 q-mb-sm">Priority Distribution</div>
            <div class="row q-col-gutter-sm">
              <div class="col">
                <q-chip color="red" text-color="white" dense>
                  High: {{ planningResult.metrics.priorityDistribution.high }}
                </q-chip>
              </div>
              <div class="col">
                <q-chip color="orange" text-color="white" dense>
                  Medium: {{ planningResult.metrics.priorityDistribution.medium }}
                </q-chip>
              </div>
              <div class="col">
                <q-chip color="blue" text-color="white" dense>
                  Low: {{ planningResult.metrics.priorityDistribution.low }}
                </q-chip>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Team Analysis - Shows ALL team members -->
        <q-card v-if="planningResult.teamAnalysis" class="q-mb-lg shadow-3">
          <q-card-section class="bg-indigo-1">
            <div class="text-h6 text-weight-bold">
              <q-icon name="groups" class="q-mr-sm" />
              Team Capacity Analysis
              <q-chip
                v-if="planningResult.teamAnalysis.considerCrossProject"
                color="primary"
                text-color="white"
                size="sm"
                class="q-ml-sm"
              >
                Cross-Project Enabled
              </q-chip>
            </div>
            <div class="text-caption text-grey-7 q-mt-xs">
              Shows workload for all {{ planningResult.teamAnalysis.summary.totalMembers }} team
              members
              <span v-if="planningResult.teamAnalysis.considerCrossProject">
                (including work from other projects)
              </span>
            </div>
          </q-card-section>

          <q-card-section>
            <div
              v-for="member in planningResult.teamAnalysis.members"
              :key="member.memberId"
              class="q-mb-lg"
            >
              <div class="row items-center justify-between q-mb-xs">
                <div>
                  <div class="text-subtitle1 text-weight-bold">
                    {{ member.memberName }}
                    <q-badge
                      :color="getMemberStatusColor(member.status)"
                      :label="getMemberStatusLabel(member.status)"
                      class="q-ml-sm"
                    />
                  </div>
                  <div class="text-caption text-grey-7">{{ member.reason }}</div>
                </div>
                <div class="text-right">
                  <div class="text-subtitle2">
                    {{ member.totalWorkload }} / {{ member.maxCapacity }} SP
                  </div>
                  <div class="text-caption text-grey-7">
                    {{ member.utilizationPercentage.toFixed(0) }}% utilized
                  </div>
                </div>
              </div>

              <!-- Workload breakdown bar -->
              <div class="relative-position" style="height: 24px">
                <!-- Cross-project workload (background) -->
                <q-linear-progress
                  v-if="member.crossProjectWorkload > 0"
                  :value="Math.min(1, member.crossProjectWorkload / member.maxCapacity)"
                  color="orange"
                  size="24px"
                  class="absolute-full"
                >
                  <div class="absolute-full flex flex-center">
                    <div class="text-caption text-white">
                      {{ member.crossProjectWorkload }} SP (other projects)
                    </div>
                  </div>
                </q-linear-progress>

                <!-- This sprint workload (stacked on top) -->
                <q-linear-progress
                  v-if="member.assignedInThisSprint > 0"
                  :value="
                    Math.min(
                      1,
                      (member.crossProjectWorkload + member.assignedInThisSprint) /
                        member.maxCapacity
                    )
                  "
                  :color="getUtilizationColor(member.utilizationPercentage)"
                  size="24px"
                  class="absolute-full"
                  style="background: transparent"
                >
                  <div class="absolute-full flex flex-center">
                    <div class="text-caption text-white text-weight-bold">
                      +{{ member.assignedInThisSprint }} SP (this sprint) =
                      {{ member.totalWorkload }} SP total
                    </div>
                  </div>
                </q-linear-progress>

                <!-- Empty state -->
                <div
                  v-if="member.totalWorkload === 0"
                  class="absolute-full flex flex-center bg-grey-3 rounded-borders"
                >
                  <div class="text-caption text-grey-7">No workload</div>
                </div>
              </div>

              <!-- Available capacity indicator -->
              <div v-if="member.availableCapacity > 0" class="text-caption text-positive q-mt-xs">
                <q-icon name="check_circle" size="14px" />
                {{ member.availableCapacity }} SP available
              </div>
              <div v-else class="text-caption text-negative q-mt-xs">
                <q-icon name="warning" size="14px" />
                At capacity
              </div>
            </div>
          </q-card-section>

          <!-- Summary Stats -->
          <q-separator />
          <q-card-section class="bg-grey-2">
            <div class="row q-col-gutter-md text-center">
              <div class="col">
                <div class="text-h6 text-weight-bold">
                  {{ planningResult.teamAnalysis.summary.assignedMembers }}
                </div>
                <div class="text-caption text-grey-7">Assigned Tasks</div>
              </div>
              <div class="col">
                <div class="text-h6 text-weight-bold text-negative">
                  {{ planningResult.teamAnalysis.summary.atCapacity }}
                </div>
                <div class="text-caption text-grey-7">At Capacity</div>
              </div>
              <div class="col">
                <div class="text-h6 text-weight-bold text-positive">
                  {{ planningResult.teamAnalysis.summary.available }}
                </div>
                <div class="text-caption text-grey-7">Available</div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Selected Tasks Table -->
        <q-card class="q-mb-lg shadow-3">
          <q-card-section class="bg-primary text-white">
            <div class="text-h6 text-weight-bold">
              <q-icon name="list" class="q-mr-sm" />
              Selected Tasks ({{ planningResult.suggestedTasks.length }})
            </div>
          </q-card-section>

          <q-card-section class="q-pa-none">
            <q-table
              :rows="planningResult.suggestedTasks"
              :columns="taskColumns"
              row-key="id"
              flat
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:body-cell-priority="props">
                <q-td :props="props">
                  <q-chip
                    :color="getPriorityColor(props.value)"
                    text-color="white"
                    dense
                    size="sm"
                  >
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>

              <template v-slot:body-cell-type="props">
                <q-td :props="props">
                  <q-chip dense size="sm" :icon="getTypeIcon(props.value)">
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>

              <template v-slot:body-cell-assignedTo="props">
                <q-td :props="props">
                  <div v-if="props.row.id && planningResult.assignments[props.row.id]">
                    <q-chip color="primary" text-color="white" dense size="sm">
                      <q-avatar>
                        <q-icon name="person" />
                      </q-avatar>
                      {{ planningResult.assignments[props.row.id]?.memberName || '—' }}
                    </q-chip>
                  </div>
                  <div v-else class="text-grey-7">—</div>
                </q-td>
              </template>

              <template v-slot:body-cell-reasoning="props">
                <q-td :props="props">
                  <div v-if="props.row.id && planningResult.reasoning[props.row.id]">
                    <div class="text-caption">
                      {{ planningResult.reasoning[props.row.id]?.reason || '' }}
                    </div>
                    <q-tooltip max-width="400px">
                      <div class="text-weight-bold q-mb-sm">Selection Reasoning</div>
                      <div>{{ planningResult.reasoning[props.row.id]?.reason || '' }}</div>
                      <div
                        v-if="planningResult.reasoning[props.row.id]?.scoreBreakdown"
                        class="q-mt-sm"
                      >
                        <div class="text-caption text-weight-bold">Score Breakdown:</div>
                        <div
                          v-for="(score, key) in planningResult.reasoning[props.row.id]
                            ?.scoreBreakdown"
                          :key="key"
                          class="text-caption"
                        >
                          {{ formatWeightLabel(key) }}: {{ score.toFixed(1) }}
                        </div>
                      </div>
                    </q-tooltip>
                  </div>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useSmartSprintStore } from 'src/stores/smart-sprint-store';
import type { SprintPlanConfig } from 'src/stores/smart-sprint-store';

const $q = useQuasar();
const projectStore = useProjectStore();
const smartSprintStore = useSmartSprintStore();

// State
const selectedProjectId = ref<number | null>(null);
const selectedStrategy = ref('hybrid');
const sprintName = ref('');
const sprintGoal = ref('');
const sprintDuration = ref(14);
const startDate = ref<string>('');
const endDate = ref<string>('');
const targetUtilization = ref(85);
const closeActiveSprint = ref(false);
const considerCrossProject = ref(true); // Default: consider workload from other projects
const hybridWeights = ref({
  priority: 0.25,
  workload: 0.2,
  skills: 0.25,
  dependency: 0.15,
  velocity: 0.15,
});

// Computed
const projectOptions = computed(() =>
  projectStore.projects.map((p) => ({
    label: p.name,
    value: p.id,
  }))
);

const selectedProject = computed(() =>
  projectStore.projects.find((p) => p.id === selectedProjectId.value)
);

const activeSprint = computed(() => {
  if (!selectedProject.value) return null;
  return selectedProject.value.sprints?.find((s) => s.status === 'active');
});

const eligibleTasksCount = computed(() => {
  if (!selectedProject.value) return 0;
  const tasks = selectedProject.value.tasks || [];
  if (activeSprint.value && !closeActiveSprint.value) {
    return tasks.filter(
      (t) => t.status !== 'Done' && t.sprintId !== activeSprint.value?.id
    ).length;
  }
  return tasks.filter((t) => t.status !== 'Done').length;
});

const canGeneratePlan = computed(() => {
  return (
    selectedProjectId.value &&
    sprintName.value &&
    startDate.value &&
    endDate.value &&
    sprintDuration.value > 0
  );
});

const hasGeneratedPlan = computed(() => {
  return !!smartSprintStore.planningResult;
});

const planningResult = computed(() => smartSprintStore.planningResult);

// Table columns
const taskColumns = [
  {
    name: 'name',
    label: 'Task',
    align: 'left' as const,
    field: 'name',
    sortable: true,
  },
  {
    name: 'priority',
    label: 'Priority',
    align: 'center' as const,
    field: 'priority',
    sortable: true,
  },
  {
    name: 'type',
    label: 'Type',
    align: 'center' as const,
    field: 'type',
    sortable: true,
  },
  {
    name: 'storyPoints',
    label: 'SP',
    align: 'center' as const,
    field: 'storyPoints',
    sortable: true,
  },
  {
    name: 'assignedTo',
    label: 'Assigned To',
    align: 'left' as const,
    field: 'id',
  },
  {
    name: 'reasoning',
    label: 'Reasoning',
    align: 'left' as const,
    field: 'id',
  },
];

// Watchers
watch(sprintDuration, (newDuration) => {
  if (startDate.value && newDuration > 0) {
    const start = new Date(startDate.value);
    const end = new Date(start);
    end.setDate(start.getDate() + newDuration);
    endDate.value = end.toISOString().split('T')[0] || '';
  }
});

watch(startDate, (newStartDate) => {
  if (newStartDate && sprintDuration.value > 0) {
    const start = new Date(newStartDate);
    const end = new Date(start);
    end.setDate(start.getDate() + sprintDuration.value);
    endDate.value = end.toISOString().split('T')[0] || '';
  }
});

// Methods
async function onProjectChange() {
  smartSprintStore.clearPlan();
  closeActiveSprint.value = false;

  if (selectedProjectId.value) {
    // Load strategies
    await smartSprintStore.loadStrategies(selectedProjectId.value);

    // Set default sprint name
    const sprintCount = (selectedProject.value?.sprints?.length || 0) + 1;
    sprintName.value = `Sprint ${sprintCount}`;

    // Set default dates
    const today = new Date();
    startDate.value = today.toISOString().split('T')[0] || '';
    const endDateCalc = new Date(today);
    endDateCalc.setDate(today.getDate() + sprintDuration.value);
    endDate.value = endDateCalc.toISOString().split('T')[0] || '';
  }
}

async function onGeneratePlan() {
  if (!selectedProjectId.value) return;

  const config: SprintPlanConfig = {
    strategy: selectedStrategy.value,
    sprintName: sprintName.value,
    sprintGoal: sprintGoal.value,
    startDate: startDate.value,
    endDate: endDate.value,
    sprintDuration: sprintDuration.value,
    targetUtilization: targetUtilization.value,
    closeActiveSprint: closeActiveSprint.value,
    considerCrossProjectWorkload: considerCrossProject.value,
  };

  // Add hybrid weights if hybrid strategy is selected
  if (selectedStrategy.value === 'hybrid') {
    config.parameters = {
      weights: { ...hybridWeights.value },
    };
  }

  const result = await smartSprintStore.generateSprintPlan(selectedProjectId.value, config);

  if (result) {
    $q.notify({
      type: 'positive',
      message: `Sprint plan generated with ${result.suggestedTasks.length} tasks`,
      position: 'top',
    });
  } else if (smartSprintStore.error) {
    $q.notify({
      type: 'negative',
      message: smartSprintStore.error,
      position: 'top',
    });
  }
}

function onRegenerate() {
  smartSprintStore.clearPlan();
}

async function onApplyPlan() {
  if (!planningResult.value || !selectedProjectId.value) return;

  const taskIds = planningResult.value.suggestedTasks.map((t) => t.id);
  const assignments: Record<string, { memberId: number; role: string }> = {};

  Object.entries(planningResult.value.assignments).forEach(([taskId, assignment]) => {
    assignments[taskId] = {
      memberId: assignment.memberId,
      role: assignment.role,
    };
  });

  $q.dialog({
    title: 'Apply Sprint Plan',
    message: `This will create "${sprintName.value}" with ${taskIds.length} tasks and assign them to team members. ${closeActiveSprint.value && activeSprint.value ? `The active sprint "${activeSprint.value.name}" will be closed.` : ''} Continue?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    const result = await smartSprintStore.applySprintPlan(selectedProjectId.value!, {
      sprintName: sprintName.value,
      sprintGoal: sprintGoal.value,
      startDate: startDate.value,
      endDate: endDate.value,
      closeActiveSprint: closeActiveSprint.value,
      tasks: taskIds,
      assignments,
    });

    if (result?.success) {
      $q.notify({
        type: 'positive',
        message: `Sprint "${sprintName.value}" created successfully with ${result.tasksUpdated} tasks`,
        position: 'top',
      });

      // Reload project data
      await projectStore.fetchProjects(true);

      // Clear plan and reset form
      smartSprintStore.clearPlan();
      onProjectChange();
    } else if (smartSprintStore.error) {
      $q.notify({
        type: 'negative',
        message: smartSprintStore.error,
        position: 'top',
      });
    }
  });
}

function getPriorityColor(priority: string): string {
  const priorityLower = (priority || 'medium').toLowerCase();
  if (priorityLower === 'high') return 'red';
  if (priorityLower === 'medium') return 'orange';
  return 'blue';
}

function getTypeIcon(type: string): string {
  if (type === 'feature') return 'star';
  if (type === 'bug') return 'bug_report';
  return 'task';
}

function getUtilizationColor(utilization: number): string {
  if (utilization > 95) return 'red';
  if (utilization > 85) return 'orange';
  if (utilization > 70) return 'green';
  return 'blue';
}

function formatWeightLabel(key: string): string {
  const labels: Record<string, string> = {
    priority: 'Priority',
    workload: 'Workload Balance',
    skills: 'Skills Match',
    dependency: 'Dependency',
    velocity: 'Velocity',
    risk: 'Risk',
  };
  return labels[key] || key;
}

function getMemberStatusColor(status: string): string {
  const colors: Record<string, string> = {
    available: 'positive',
    assigned: 'primary',
    nearly_full: 'warning',
    at_capacity: 'negative',
  };
  return colors[status] || 'grey';
}

function getMemberStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    available: 'Available',
    assigned: 'Assigned',
    nearly_full: 'Nearly Full',
    at_capacity: 'At Capacity',
  };
  return labels[status] || status;
}

// Lifecycle
onMounted(async () => {
  await projectStore.fetchProjects();

  // Auto-select first project if available
  if (projectStore.projects.length > 0 && projectStore.projects[0]) {
    selectedProjectId.value = projectStore.projects[0].id;
    await onProjectChange();
  }
});
</script>

<style scoped lang="scss">
.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.strategy-card {
  transition: all 0.3s ease;
  border: 2px solid transparent;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  }
}

.strategy-card-selected {
  border-color: #667eea !important;
  background-color: #f0f4ff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.metric-card {
  text-align: center;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &.cursor-pointer:hover {
    background: #ececec;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.cursor-pointer {
  cursor: pointer;
}
</style>

