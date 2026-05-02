<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Smart Sprint Planning</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Sprint planning with multiple optimization strategies
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            v-if="hasGeneratedPlan"
            color="primary"
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
          >
            <q-tooltip max-width="300px">
              Apply the plan and create a new planned sprint. You can adjust it before starting.
            </q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- Project Selection -->
      <div class="row items-center q-gutter-md">
        <div class="col-12 col-md-5">
          <q-select
            v-model="selectedProjectId"
            :options="projectOptions"
            label="Select Project"
            filled
            emit-value
            map-options
            @update:model-value="onProjectChange"
          >
            <template v-slot:prepend>
              <q-icon name="folder" />
            </template>
          </q-select>
        </div>
        <div class="col-12 col-md">
          <div class="row q-gutter-sm items-center">
            <q-chip v-if="selectedProject" icon="task" color="primary" text-color="white">
              {{ eligibleTasksCount }} Available Tasks
            </q-chip>
            <q-chip v-if="selectedProject" icon="group" color="green" text-color="white">
              {{ selectedProject.teamMemberIds?.length || 0 }} Members
            </q-chip>
          </div>
        </div>
      </div>

      <!-- Cross-Project Workload Consideration (not for PERT) -->
      <div
        v-if="selectedProject && !selectedStrategy.startsWith('pert') && !(selectedStrategy === 'hybrid' && hybridWeights.pertMode !== 'none')"
        class="q-mt-md"
      >
        <q-checkbox
          v-model="considerCrossProject"
          color="primary"
          label="Consider workload from other projects"
          @update:model-value="onConsiderCrossProjectToggle"
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
      </div>
    </div>

    <div class="q-pa-lg">

      <!-- No Project Selected -->
      <q-card v-if="!selectedProject" class="q-mb-lg shadow-2 text-center q-pa-xl">
        <q-icon name="folder_open" size="64px" color="grey-5" class="q-mb-md" />
        <div class="text-h6 text-grey-6 q-mb-sm">Select a Project to Begin</div>
        <div class="text-body2 text-grey-7">
          Choose a project from the dropdown above to start intelligent sprint planning
        </div>
      </q-card>

      <!-- Existing Planned Sprint Warning -->
      <q-banner
        v-if="selectedProject && plannedSprint"
        class="bg-orange-1 q-mb-lg"
        rounded
      >
        <template v-slot:avatar>
          <q-icon name="warning" color="orange" size="32px" />
        </template>
        <div class="text-weight-bold text-orange-9 q-mb-sm">
          <q-icon name="schedule" size="20px" class="q-mr-xs" />
          Planned Sprint Already Exists: "{{ plannedSprint.name }}"
        </div>
        <div class="text-body2 q-mb-sm">
          Project can have only <strong>one planned sprint</strong> at a time.
        </div>
        
        <!-- If active sprint is running -->
        <div v-if="activeSprint" class="text-body2 bg-red-1 q-pa-sm rounded-borders q-mb-sm">
          <q-icon name="block" size="16px" color="red" class="q-mr-xs" />
          <strong>Cannot start:</strong> Sprint "{{ activeSprint.name }}" is already active. 
          Complete it before starting "{{ plannedSprint.name }}".
        </div>
        
        <!-- If no active sprint -->
        <div v-else class="text-body2">
          <strong>Options:</strong><br>
          • Start "{{ plannedSprint.name }}" to make it active, then create new planned sprint<br>
          • Delete "{{ plannedSprint.name }}" if no longer needed
        </div>
        
        <template v-slot:action>
          <div class="column q-gutter-sm">
            <q-btn
              v-if="!activeSprint"
              color="green"
              icon="play_arrow"
              label="Start Sprint"
              size="sm"
              @click="startExistingPlannedSprint"
            />
            <q-btn
              flat
              color="negative"
              icon="delete"
              label="Delete Sprint"
              size="sm"
              @click="deleteExistingPlannedSprint"
            />
          </div>
        </template>
      </q-banner>

      <!-- Active Sprint Info (informative only) -->
      <q-banner
        v-if="selectedProject && activeSprint && !plannedSprint"
        class="bg-blue-1 q-mb-lg"
        rounded
      >
        <template v-slot:avatar>
          <q-icon name="info" color="blue" size="32px" />
        </template>
        <div class="text-weight-bold text-blue-9 q-mb-sm">
          <q-icon name="play_circle" size="20px" class="q-mr-xs" />
          Active Sprint Running: "{{ activeSprint.name }}"
        </div>
        <div class="text-body2">
          The AI will create a new <strong>planned sprint</strong>. Your active sprint will continue running.
          You can review and adjust the planned sprint before starting it.
        </div>
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

            <!-- Sprint Duration (read-only, always 2 weeks) -->
            <div class="col-12 col-md-6">
              <q-input
                v-model.number="sprintDuration"
                label="Sprint Duration (days)"
                type="number"
                outlined
                dense
                readonly
                hint="Fixed 2-week sprints per project"
              >
                <template #prepend>
                  <q-icon name="schedule" />
                </template>
              </q-input>
            </div>

            <!-- Start Date (auto from project cadence) -->
            <div class="col-12 col-md-6">
              <q-input
                v-model="startDate"
                label="Start Date *"
                type="date"
                outlined
                dense
                readonly
                :rules="[(val) => !!val || 'Start date is required']"
                hint="Auto-calculated from project sprint cadence"
              >
                <template #prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>

            <!-- End Date (auto from project cadence) -->
            <div class="col-12 col-md-6">
              <q-input
                v-model="endDate"
                label="End Date *"
                type="date"
                outlined
                dense
                readonly
                :rules="[(val) => !!val || 'End date is required']"
                hint="Auto-calculated (2 weeks)"
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
                @click="onStrategySelect(strategy.id)"
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
                <div v-for="key in hybridSliderKeys" :key="key" class="q-mb-md">
                  <div class="text-subtitle2 q-mb-sm">
                    {{ formatWeightLabel(key) }}:
                    {{ (typeof hybridWeights[key] === 'number' ? hybridWeights[key] : 0).toFixed(2) }}
                  </div>
                  <q-slider
                    :model-value="Number(hybridWeights[key]) || 0"
                    @update:model-value="(v) => { hybridWeights[key] = v ?? 0 }"
                    :min="key === 'pertPredictability' ? 0 : 0"
                    :max="key === 'pertPredictability' ? 0.3 : 1"
                    :step="0.05"
                    label
                    label-always
                    color="primary"
                    markers
                  />
                </div>
                <div class="q-mb-md">
                  <div class="text-subtitle2 q-mb-sm">PERT Mode</div>
                  <q-select
                    v-model="hybridWeights.pertMode"
                    :options="[
                      { label: 'None (SP-based)', value: 'none' },
                      { label: 'PERT (raw hours)', value: 'pert' },
                      { label: 'PERT + RACI Integration (adjusted duration)', value: 'pert-raci' },
                    ]"
                    emit-value
                    map-options
                    outlined
                    dense
                  />
                  <div class="text-caption text-grey-7">
                    Choose capacity model. PERT/RACI require tasks with PERT estimates.
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-card-section>

        <q-separator />

        <!-- PERT Strategy Note -->
        <q-banner
          v-if="selectedStrategy.startsWith('pert') || (selectedStrategy === 'hybrid' && hybridWeights.pertMode !== 'none')"
          class="bg-blue-1 q-ma-md"
          rounded
        >
          <template v-slot:avatar>
            <q-icon name="schedule" color="blue" size="24px" />
          </template>
          <div class="text-body2">
            <strong>PERT strategies:</strong> Only tasks with PERT estimates (hours) are included.
            Capacity: 60h per member. Priority variants order tasks by duration and priority.
          </div>
        </q-banner>

        <!-- Warning Banner -->
        <q-banner class="bg-orange-1 q-ma-md" rounded>
          <template v-slot:avatar>
            <q-icon name="info" color="orange" size="24px" />
          </template>
          <div class="text-body2">
            <strong>Note:</strong> All planning strategies will automatically assign tasks to team members based on the selected algorithm.
            Existing RACI "Responsible" assignments will be overwritten to optimize workload distribution.
          </div>
        </q-banner>

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
          >
            <q-tooltip v-if="plannedSprint" max-width="300px">
              Cannot generate: Project already has a planned sprint "{{ plannedSprint.name }}".
              Please start or delete it first.
            </q-tooltip>
          </q-btn>
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
              <!-- Total Story Points / Total Hours (PERT) -->
              <div class="col-6 col-md-3">
                <div class="metric-card">
                  <q-icon name="format_list_numbered" size="32px" color="blue" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ displayMetrics?.pertMode ? displayMetrics?.totalHours : displayMetrics?.totalStoryPoints }}
                  </div>
                  <div class="text-caption text-grey-7">
                    {{ displayMetrics?.pertMode ? 'Total Hours' : 'Total Story Points' }}
                  </div>
                  <div v-if="displayMetrics?.pertMode && displayMetrics?.totalStoryPoints" class="text-caption text-grey-6">
                    ({{ displayMetrics.totalStoryPoints }} SP)
                  </div>
                </div>
              </div>

              <!-- Task Count -->
              <div class="col-6 col-md-3">
                <div class="metric-card">
                  <q-icon name="task" size="32px" color="green" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ displayMetrics?.taskCount }}
                  </div>
                  <div class="text-caption text-grey-7">Tasks Selected</div>
                </div>
              </div>

              <!-- Utilization -->
              <div class="col-6 col-md-3">
                <div class="metric-card cursor-pointer">
                  <q-icon name="speed" size="32px" color="orange" class="q-mb-sm" />
                  <div class="text-h4 text-weight-bold">
                    {{ displayMetrics?.utilization?.toFixed(1) }}%
                  </div>
                  <div class="text-caption text-grey-7">Team Utilization</div>
                  <q-linear-progress
                    :value="(displayMetrics?.utilization ?? 0) / 100"
                    :color="getUtilizationColor(displayMetrics?.utilization ?? 0)"
                    size="8px"
                    class="q-mt-sm"
                  />
                  <q-tooltip max-width="400px" class="bg-dark text-body2">
                    <div class="text-weight-bold q-mb-sm">Team Utilization</div>
                    <div class="q-mb-sm">
                      Percentage of total team capacity being utilized by the selected tasks.
                    </div>
                    <div class="q-mb-xs">
                      <strong>Formula:</strong>
                      {{ displayMetrics?.pertMode ? '(Total Hours / Team Capacity) × 100' : '(Total SP / Team Capacity) × 100' }}
                    </div>
                    <div class="q-mb-xs">
                      <strong>This Sprint:</strong>
                      {{ displayMetrics?.pertMode
                        ? `${displayMetrics?.totalHours ?? 0}h / ${displayMetrics?.teamCapacity ?? 0}h capacity`
                        : `${displayMetrics?.totalStoryPoints ?? 0} SP / ${displayMetrics?.teamCapacity ?? 0} SP capacity`
                      }}
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
                    {{ displayMetrics?.balanceScore?.toFixed(1) }}
                  </div>
                  <div class="text-caption text-grey-7">Balance Score</div>
                  <q-linear-progress
                    :value="(displayMetrics?.balanceScore ?? 0) / 100"
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
                      v-if="displayTeamAnalysis"
                      class="q-mt-sm q-pt-sm"
                      style="border-top: 1px solid rgba(255, 255, 255, 0.3)"
                    >
                      <div class="text-caption text-weight-bold">Current Distribution:</div>
                      <div
                        v-for="member in displayTeamAnalysis.members.slice(0, 3)"
                        :key="member.memberId"
                        class="text-caption"
                      >
                        {{ member.memberName }}: {{ member.utilizationPercentage.toFixed(0) }}%
                      </div>
                      <div v-if="displayTeamAnalysis.members.length > 3" class="text-caption">
                        ... and {{ displayTeamAnalysis.members.length - 3 }} more
                      </div>
                    </div>
                  </q-tooltip>
                </div>
              </div>
            </div>
          </q-card-section>

          <!-- Priority Distribution -->
          <q-card-section v-if="displayMetrics?.priorityDistribution">
            <div class="text-subtitle2 q-mb-sm">Priority Distribution</div>
            <div class="row q-col-gutter-sm">
              <div class="col">
                <q-chip color="red" text-color="white" dense>
                  High: {{ displayMetrics?.priorityDistribution?.high }}
                </q-chip>
              </div>
              <div class="col">
                <q-chip color="orange" text-color="white" dense>
                  Medium: {{ displayMetrics?.priorityDistribution?.medium }}
                </q-chip>
              </div>
              <div class="col">
                <q-chip color="blue" text-color="white" dense>
                  Low: {{ displayMetrics?.priorityDistribution?.low }}
                </q-chip>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Team Analysis - Shows ALL team members -->
        <q-card v-if="displayTeamAnalysis" class="q-mb-lg shadow-3">
          <q-card-section class="bg-indigo-1">
            <div class="text-h6 text-weight-bold">
              <q-icon name="groups" class="q-mr-sm" />
              Team Capacity Analysis
              <q-chip
                v-if="displayTeamAnalysis.considerCrossProject"
                color="primary"
                text-color="white"
                size="sm"
                class="q-ml-sm"
              >
                Cross-Project Enabled
              </q-chip>
            </div>
            <div class="text-caption text-grey-7 q-mt-xs">
              Shows workload for all {{ displayTeamAnalysis.summary.totalMembers }} team
              members
              <span v-if="displayTeamAnalysis.considerCrossProject">
                (including work from other projects)
              </span>
            </div>
          </q-card-section>

          <q-card-section>
            <div
              v-for="member in displayTeamAnalysis.members"
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
                    {{ member.totalWorkload }}{{ displayMetrics?.pertMode ? 'h' : '' }} / {{ member.maxCapacity }}{{ displayMetrics?.pertMode ? 'h' : ' SP' }}
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
                  v-if="!displayMetrics?.pertMode && member.crossProjectWorkload > 0"
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
                      {{ displayMetrics?.pertMode
                        ? `${member.assignedInThisSprint}h (this sprint)`
                        : `+${member.assignedInThisSprint} SP (this sprint) = ${member.totalWorkload} SP total`
                      }}
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
                {{ member.availableCapacity }}{{ displayMetrics?.pertMode ? 'h' : ' SP' }} available
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
                  {{ displayTeamAnalysis.summary.assignedMembers }}
                </div>
                <div class="text-caption text-grey-7">Assigned Tasks</div>
              </div>
              <div class="col">
                <div class="text-h6 text-weight-bold text-negative">
                  {{ displayTeamAnalysis.summary.atCapacity }}
                </div>
                <div class="text-caption text-grey-7">At Capacity</div>
              </div>
              <div class="col">
                <div class="text-h6 text-weight-bold text-positive">
                  {{ displayTeamAnalysis.summary.available }}
                </div>
                <div class="text-caption text-grey-7">Available</div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Selected Tasks Table (editable) -->
        <q-card class="q-mb-lg shadow-3">
          <q-card-section class="bg-primary text-white">
            <div class="row items-center justify-between">
              <div class="text-h6 text-weight-bold">
                <q-icon name="list" class="q-mr-sm" />
                Selected Tasks ({{ smartSprintStore.editableTasks.length }})
              </div>
              <q-btn
                color="white"
                size="sm"
                icon="add"
                label="Add Task"
                @click="showAddTaskDialog = true"
                :disable="availableTasksToAdd.length === 0"
                flat
              >
                <q-tooltip v-if="availableTasksToAdd.length === 0">
                  No tasks available to add (all are in plan or Done)
                </q-tooltip>
              </q-btn>
            </div>
            <div class="text-caption opacity-90 q-mt-xs">
              You can change assignee, remove tasks, or add tasks before applying
            </div>
          </q-card-section>

          <q-card-section class="q-pa-none">
            <q-table
              :rows="smartSprintStore.editableTasks"
              :columns="taskColumns"
              row-key="id"
              flat
              :pagination="{ rowsPerPage: 10 }"
            >
              <template v-slot:body-cell-name="props">
                <q-td :props="props">
                  {{ props.row.title || props.row.name }}
                </q-td>
              </template>
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
                  <q-select
                    :model-value="smartSprintStore.editableAssignments[props.row.id]?.memberId ?? null"
                    :options="memberOptions"
                    emit-value
                    map-options
                    dense
                    outlined
                    options-dense
                    clearable
                    class="assignee-select"
                    style="min-width: 160px"
                    @update:model-value="(val) => onAssigneeChange(props.row.id, val)"
                  >
                    <template v-slot:prepend>
                      <q-icon name="person" size="small" />
                    </template>
                  </q-select>
                </q-td>
              </template>

              <template v-slot:body-cell-reasoning="props">
                <q-td :props="props">
                  <div v-if="props.row.id && planningResult?.reasoning?.[props.row.id]">
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

              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    dense
                    color="negative"
                    icon="remove_circle_outline"
                    size="sm"
                    @click="onRemoveTask(props.row.id)"
                  >
                    <q-tooltip>Remove from sprint</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>

        <!-- Add Task Dialog -->
        <q-dialog v-model="showAddTaskDialog" persistent>
          <q-card style="min-width: 400px">
            <q-card-section>
              <div class="text-h6">Add Task to Sprint</div>
              <div class="text-caption text-grey-7 q-mb-md">
                Select a task to add to the sprint plan
              </div>
              <q-list v-if="availableTasksToAdd.length > 0" bordered separator>
                <q-item
                  v-for="task in availableTasksToAdd"
                  :key="task.id"
                  clickable
                  v-close-popup
                  @click="onAddTask(task)"
                >
                  <q-item-section> {{ task.title || task.name }} </q-item-section>
                  <q-item-section side>
                    <q-chip dense size="sm">{{ task.storyPoints }} SP</q-chip>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-caption text-grey-7 q-pa-md">
                No tasks available to add
              </div>
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat label="Cancel" color="grey" v-close-popup />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useSmartSprintStore } from 'src/stores/smart-sprint-store';
import { useTeamStore } from 'src/stores/team-store';
import type { SprintPlanConfig, SprintTask } from 'src/stores/smart-sprint-store';
import type { Task } from 'src/stores/project-store';
import { useActivityLog } from 'src/composables/useActivityLog';

const $q = useQuasar();
const projectStore = useProjectStore();
const smartSprintStore = useSmartSprintStore();
const teamStore = useTeamStore();
const { log } = useActivityLog();

// State
const selectedProjectId = ref<number | null>(null);
const selectedStrategy = ref('hybrid');
const sprintName = ref('');
const sprintGoal = ref('');
const sprintDuration = ref(14);
const startDate = ref<string>('');
const endDate = ref<string>('');
const targetUtilization = ref(85);
const considerCrossProject = ref(true); // Default: consider workload from other projects
const hybridWeights = ref<Record<string, number | string>>({
  priority: 0.30,
  workload: 0.25,
  skills: 0.30,
  dependency: 0.15,
  pertMode: 'none',
  pertPredictability: 0.1,
});
const showAddTaskDialog = ref(false);

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

const plannedSprint = computed(() => {
  if (!selectedProject.value) return null;
  return selectedProject.value.sprints?.find((s) => s.status === 'planned');
});

const eligibleTasksCount = computed(() => {
  if (!selectedProject.value) return 0;
  const tasks = selectedProject.value.tasks || [];
  // Exclude tasks from active sprint (can't plan already running tasks)
  if (activeSprint.value) {
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
    sprintDuration.value > 0 &&
    !plannedSprint.value  // Cannot generate if planned sprint already exists
  );
});

const hasGeneratedPlan = computed(() => {
  return !!smartSprintStore.planningResult;
});

const hybridSliderKeys = computed(() =>
  Object.keys(hybridWeights.value).filter((k) => k !== 'pertMode')
);

// Note: canApplyPlan check removed - AI now creates PLANNED sprints which don't conflict with active sprints

const planningResult = computed(() => smartSprintStore.planningResult);

// Use recalculated metrics/team analysis (updates when user edits plan)
// Explicitly depend on editableTasks/editableAssignments to trigger recalculation
const displayMetrics = computed(() => {
  void smartSprintStore.editableTasks.length;
  void Object.keys(smartSprintStore.editableAssignments).length;
  return (
    smartSprintStore.editableMetrics ?? smartSprintStore.planningResult?.metrics
  );
});
const displayTeamAnalysis = computed(() => {
  void smartSprintStore.editableTasks.length;
  void Object.keys(smartSprintStore.editableAssignments).length;
  return (
    smartSprintStore.editableTeamAnalysis ??
    smartSprintStore.planningResult?.teamAnalysis
  );
});

const projectTeamMembers = computed(() => {
  if (!selectedProject.value?.teamMemberIds?.length) return [];
  return selectedProject.value.teamMemberIds
    .map((id) => teamStore.teamMembers.find((m) => m.id === id))
    .filter((m): m is NonNullable<typeof m> => !!m);
});

const memberOptions = computed(() =>
  projectTeamMembers.value.map((m) => ({ label: m.name, value: m.id }))
);

const availableTasksToAdd = computed(() => {
  if (!selectedProject.value?.tasks) return [];
  const inPlanIds = new Set(smartSprintStore.editableTasks.map((t) => t.id));
  return selectedProject.value.tasks.filter((t) => {
    if (t.status === 'Done') return false;
    if (activeSprint.value && t.sprintId === activeSprint.value?.id) return false;
    return !inPlanIds.has(t.id);
  });
});

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
  {
    name: 'actions',
    label: '',
    align: 'center' as const,
    field: 'id',
    sortable: false,
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
function onConsiderCrossProjectToggle() {
  log('consider_cross_project_toggle', 'smart_sprint_planning', {
    ...(selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {}),
    details: { enabled: considerCrossProject.value },
  });
}

function onStrategySelect(strategyId: string) {
  selectedStrategy.value = strategyId;
  log('strategy_select', 'smart_sprint_planning', {
    ...(selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {}),
    details: { strategy: strategyId },
  });
}

async function onProjectChange() {
  if (selectedProjectId.value) {
    log('project_select', 'smart_sprint_planning', { projectId: selectedProjectId.value });
  }
  smartSprintStore.clearPlan();

  if (selectedProjectId.value) {
    // Load project details (including tasks) and strategies
    await Promise.all([
      projectStore.getProject(selectedProjectId.value),
      smartSprintStore.loadStrategies(selectedProjectId.value),
    ]);

    // Set default sprint name
    const sprintCount = (selectedProject.value?.sprints?.length || 0) + 1;
    sprintName.value = `Sprint ${sprintCount}`;

    // Fetch next sprint dates from API (2-week cadence, auto-calculated)
    const nextDates = await projectStore.getNextSprintDates(selectedProjectId.value);
    if (nextDates) {
      startDate.value = nextDates.startDate;
      endDate.value = nextDates.endDate;
      sprintDuration.value = nextDates.sprintDurationDays;
    } else {
      const today = new Date();
      startDate.value = today.toISOString().split('T')[0] || '';
      const endDateCalc = new Date(today);
      endDateCalc.setDate(today.getDate() + 14);
      endDate.value = endDateCalc.toISOString().split('T')[0] || '';
      sprintDuration.value = 14;
    }
  }
}

async function onGeneratePlan() {
  if (!selectedProjectId.value) return;
  log('generate_plan', 'smart_sprint_planning', {
    projectId: selectedProjectId.value,
    details: { strategy: selectedStrategy.value },
  });

  const config: SprintPlanConfig = {
    strategy: selectedStrategy.value,
    sprintName: sprintName.value,
    sprintGoal: sprintGoal.value,
    startDate: startDate.value,
    endDate: endDate.value,
    sprintDuration: sprintDuration.value,
    targetUtilization: targetUtilization.value,
    closeActiveSprint: false,
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
  log('regenerate_plan', 'smart_sprint_planning', selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {});
  smartSprintStore.clearPlan();
}

async function startExistingPlannedSprint() {
  if (!plannedSprint.value || !selectedProjectId.value) return;

  // Check if there's already an active sprint
  if (activeSprint.value) {
    $q.notify({
      message: `Cannot start sprint: "${activeSprint.value.name}" is already active. Please complete it first.`,
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  const sprintName = plannedSprint.value.name;

  try {
    await projectStore.updateSprint(selectedProjectId.value, plannedSprint.value.id, {
      status: 'active',
    });

    // Show success immediately after update
    $q.notify({
      message: `Sprint "${sprintName}" started! You can now create a new planned sprint.`,
      color: 'positive',
      icon: 'play_arrow',
      position: 'top',
    });

    // Reload project data (non-critical - if fails, user can manually refresh)
    try {
      await projectStore.getProject(selectedProjectId.value);
    } catch (reloadError) {
      console.warn('Failed to reload project after start:', reloadError);
    }
  } catch {
    $q.notify({
      message: projectStore.error || 'Failed to start sprint',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

async function deleteExistingPlannedSprint() {
  if (!plannedSprint.value || !selectedProjectId.value) return;

  $q.dialog({
    title: 'Delete Planned Sprint',
    message: `Are you sure you want to delete "${plannedSprint.value.name}"? This action cannot be undone.`,
    cancel: true,
    persistent: true,
    ok: {
      label: 'Delete',
      color: 'negative',
      flat: true,
    },
  }).onOk(async () => {
    const sprintName = plannedSprint.value!.name;
    
    try {
      await projectStore.deleteSprint(selectedProjectId.value!, plannedSprint.value!.id);
      
      // Show success immediately after delete
      $q.notify({
        message: `Sprint "${sprintName}" deleted. You can now create a new planned sprint.`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
      
      // Reload project data (non-critical - if fails, user can manually refresh)
      try {
        await projectStore.getProject(selectedProjectId.value!);
      } catch (reloadError) {
        console.warn('Failed to reload project after delete:', reloadError);
      }
    } catch {
      $q.notify({
        message: projectStore.error || 'Failed to delete sprint',
        color: 'negative',
        icon: 'error',
        position: 'top',
      });
    }
  });
}

async function onApplyPlan() {
  if (!selectedProjectId.value || smartSprintStore.editableTasks.length === 0) return;
  log('apply_plan', 'smart_sprint_planning', {
    projectId: selectedProjectId.value,
    details: { taskCount: smartSprintStore.editableTasks.length },
  });

  const taskIds = smartSprintStore.editableTasks.map((t) => t.id);
  const assignments: Record<string, { memberId: number; role: string }> = {};

  Object.entries(smartSprintStore.editableAssignments).forEach(([taskId, assignment]) => {
    assignments[taskId] = {
      memberId: assignment.memberId,
      role: assignment.role,
    };
  });

  // Build confirmation message
  let confirmMessage = `This will create a new planned sprint "${sprintName.value}" with ${taskIds.length} tasks and assign them to team members.`;

  if (activeSprint.value) {
    confirmMessage += `\n\n✓ Your active sprint "${activeSprint.value.name}" will continue running.`;
  }

  confirmMessage += '\n\nYou can review and adjust the planned sprint before starting it.\n\nContinue?';

  $q.dialog({
    title: 'Apply Sprint Plan',
    message: confirmMessage,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    const result = await smartSprintStore.applySprintPlan(selectedProjectId.value!, {
      sprintName: sprintName.value,
      sprintGoal: sprintGoal.value,
      startDate: startDate.value,
      endDate: endDate.value,
      closeActiveSprint: false,
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
    pertPredictability: 'PERT Predictability (CV)',
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

function onAssigneeChange(taskId: number, memberId: number | null) {
  if (memberId == null) {
    smartSprintStore.updateTaskAssignment(taskId, null);
    return;
  }
  const member = projectTeamMembers.value.find((m) => m.id === memberId);
  if (member) {
    smartSprintStore.updateTaskAssignment(taskId, memberId, member.name);
  }
}

function onRemoveTask(taskId: number) {
  smartSprintStore.removeTaskFromPlan(taskId);
}

function taskToSprintTask(task: Task): SprintTask {
  return {
    id: task.id,
    name: task.name,
    title: task.title,
    description: task.description || '',
    status: task.status,
    priority: task.priority,
    type: task.type,
    storyPoints: task.storyPoints || 0,
    labels: task.labels || [],
    complexity: task.complexity || 0,
    dependencies: task.dependencies || [],
    riskLevel: task.riskLevel || 'low',
  };
}

function onAddTask(task: Task) {
  const sprintTask = taskToSprintTask(task);
  smartSprintStore.addTaskToPlan(sprintTask);
  showAddTaskDialog.value = false;
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    projectStore.fetchProjects(true),
    teamStore.fetchTeamMembers(),
  ]);

  // Auto-select first project if available
  if (projectStore.projects.length > 0 && projectStore.projects[0]) {
    selectedProjectId.value = projectStore.projects[0].id;
    await onProjectChange();
  }
});
</script>

<style scoped lang="scss">

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

