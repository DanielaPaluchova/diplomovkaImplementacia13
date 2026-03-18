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
            Analysis with 10+ optimization types
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
            <!-- Workload Card (Current Project) -->
            <div class="col-12 col-sm-6 col-md-3">
              <div class="stat-card clickable">
                <q-icon name="assessment" size="32px" color="orange" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.workload }}%</div>
                <div class="text-caption text-grey-7">Project Workload</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Workload on This Project</div>
                  <div class="text-caption text-grey-6 q-mb-sm">Active sprint only</div>
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

            <!-- Cross-Project Workload Card -->
            <div class="col-12 col-sm-6 col-md-3">
              <div class="stat-card clickable">
                <q-icon name="dashboard" size="32px" color="purple" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ crossProjectWorkload.average }}%</div>
                <div class="text-caption text-grey-7">Cross-Project Workload</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Workload Across All Projects</div>
                  <div class="text-caption text-grey-6 q-mb-sm">All active sprints</div>
                  <div v-if="crossProjectWorkload.details.length > 0">
                    <div v-for="member in crossProjectWorkload.details" :key="member.id" class="q-mb-xs">
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
                    No workload data available
                  </div>
                </q-tooltip>
              </div>
            </div>

            <!-- Risk Score Card -->
            <div class="col-12 col-sm-6 col-md-3">
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
            <div class="col-12 col-sm-6 col-md-3">
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

            <!-- PERT Duration Card -->
            <div class="col-12 col-sm-6 col-md-3" v-if="currentState.totalPertDuration !== undefined">
              <div class="stat-card clickable">
                <q-icon name="schedule" size="32px" color="blue" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.totalPertDuration }}d</div>
                <div class="text-caption text-grey-7">PERT Duration</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">PERT Duration Analysis</div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>PERT Expected:</span>
                      <span class="text-weight-bold">{{ currentState.totalPertDuration }}d</span>
                    </div>
                  </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>RACI Adjusted:</span>
                      <span class="text-weight-bold">{{ currentState.totalAdjustedDuration }}d</span>
                    </div>
                  </div>
                  <div class="q-mb-xs">
                    <div class="row justify-between">
                      <span>Overhead:</span>
                      <span class="text-weight-bold" :class="getDurationOverheadColor(currentState.durationOverhead || 0)">
                        +{{ currentState.durationOverhead }}%
                      </span>
                    </div>
                  </div>
                  <q-separator class="q-my-sm" />
                  <div class="text-caption text-grey-5">
                    PERT duration adjusted for team overload
                  </div>
                </q-tooltip>
              </div>
            </div>

            <!-- PERT Uncertainty Card -->
            <div class="col-12 col-sm-6 col-md-3" v-if="currentState.avgPertUncertainty !== undefined">
              <div class="stat-card clickable">
                <q-icon name="warning_amber" size="32px" color="orange" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.avgPertUncertainty }}%</div>
                <div class="text-caption text-grey-7">PERT Uncertainty</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">Average PERT Uncertainty</div>
                  <div class="q-mb-sm">
                    Measure of task estimation uncertainty (optimistic vs pessimistic).
                  </div>
                  <div class="text-caption text-grey-5">
                    <div v-if="(currentState.avgPertUncertainty || 0) < 30">
                      ✓ Low uncertainty - Good estimates
                    </div>
                    <div v-else-if="(currentState.avgPertUncertainty || 0) < 50" class="text-orange">
                      ⚠ Medium uncertainty - Some risk
                    </div>
                    <div v-else class="text-red">
                      ✗ High uncertainty - Consider breaking down tasks
                    </div>
                  </div>
                </q-tooltip>
              </div>
            </div>

            <!-- RACI Workload Card (Current Project Only) -->
            <div class="col-12 col-sm-6 col-md-3" v-if="currentState.raciProjectWorkload !== undefined">
              <div class="stat-card clickable">
                <q-icon name="people" size="32px" color="teal" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.raciProjectWorkload }}%</div>
                <div class="text-caption text-grey-7">RACI Workload</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">RACI-Weighted Workload</div>
                  <div class="text-caption text-grey-6 q-mb-sm">Active sprint - current project only</div>
                  <div v-if="raciProjectWorkloadDetails.length > 0">
                    <div v-for="member in raciProjectWorkloadDetails" :key="member.id" class="q-mb-xs">
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
                    No active sprint or team members assigned
                  </div>
                  <div class="text-caption text-grey-6 q-mt-sm">
                    Poznámka: Všetky hodnoty sú zaokrúhlené na celé čísla
                  </div>
                </q-tooltip>
              </div>
            </div>

            <!-- RACI Cross-Project Workload Card -->
            <div class="col-12 col-sm-6 col-md-3" v-if="currentState.raciCrossProjectWorkload !== undefined">
              <div class="stat-card clickable">
                <q-icon name="groups" size="32px" color="deep-purple" class="q-mb-sm" />
                <div class="text-h4 text-weight-bold">{{ currentState.raciCrossProjectWorkload }}%</div>
                <div class="text-caption text-grey-7">RACI Cross-Project Workload</div>
                <q-tooltip max-width="350px" class="bg-dark text-body2">
                  <div class="text-weight-bold q-mb-sm">RACI-Weighted Workload Across All Projects</div>
                  <div class="text-caption text-grey-6 q-mb-sm">Active sprint across all projects</div>
                  <div v-if="raciCrossProjectWorkloadDetails.length > 0">
                    <div v-for="member in raciCrossProjectWorkloadDetails" :key="member.id" class="q-mb-xs">
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
                    No active sprint or team members assigned
                  </div>
                  <div class="text-caption text-grey-6 q-mt-sm">
                    Poznámka: Všetky hodnoty sú zaokrúhlené na celé čísla
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
            name="planned_sprint"
            icon="event_available"
            label="Planned Sprint"
            :disable="!hasPlannedSprint"
          >
            <q-tooltip v-if="!hasPlannedSprint">
              No planned sprint available
            </q-tooltip>
          </q-tab>
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
                    Optimize tasks not assigned to any sprint
                          </div>
                        </div>
                <div class="row q-gutter-sm">
                  <q-btn
                    color="secondary"
                    icon="auto_fix_high"
                    label="Analyze & Optimize"
                    @click="analyzeTab('backlog')"
                    :loading="requirementChangeStore.loading"
                    :disable="!selectedProjectId || initialLoading"
                    size="lg"
                    unelevated
                  />
                  <q-btn
                    color="purple"
                    icon="schedule"
                    label="PERT+RACI Analysis"
                    @click="analyzePertRaciTab('backlog')"
                    :loading="requirementChangeStore.loading"
                    :disable="!selectedProjectId || initialLoading"
                    size="lg"
                    unelevated
                  >
                    <q-tooltip>Specialized analysis for PERT duration and RACI workload</q-tooltip>
                  </q-btn>
                </div>
                      </div>

              <!-- Loading State -->
              <div v-if="requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-spinner-dots color="primary" size="48px" class="q-mb-md" />
                <div class="text-h6 text-grey-7">Analyzing Project...</div>
                <div class="text-body2 text-grey-6">
                  Searching for optimization opportunities
                </div>
              </div>

              <OptimizationProposals
                v-else-if="hasProposals"
                :proposals="proposals"
                :selected-proposals="requirementChangeStore.selectedProposals"
                :scope="requirementChangeStore.analysisResult?.scope"
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

          <!-- Planned Sprint Tab -->
          <q-tab-panel name="planned_sprint">
            <div class="q-pa-md">
              <div class="row items-center justify-between q-mb-lg">
                <div>
                  <div class="text-h5 text-weight-bold">Planned Sprint Analysis</div>
                  <div class="text-caption text-grey-7">
                    Preview optimization before starting the sprint
                  </div>
                </div>
                <div class="row q-gutter-sm">
                  <q-btn
                    color="secondary"
                    icon="auto_fix_high"
                    label="Analyze & Optimize"
                    @click="analyzeTab('planned_sprint')"
                    :loading="requirementChangeStore.loading"
                    :disable="!selectedProjectId || initialLoading"
                    size="lg"
                    unelevated
                  />
                  <q-btn
                    color="purple"
                    icon="schedule"
                    label="PERT+RACI Analysis"
                    @click="analyzePertRaciTab('planned_sprint')"
                    :loading="requirementChangeStore.loading"
                    :disable="!selectedProjectId || initialLoading"
                    size="lg"
                    unelevated
                  >
                    <q-tooltip>Specialized analysis for PERT duration and RACI workload</q-tooltip>
                  </q-btn>
                </div>
              </div>

              <!-- Planned Sprint Info Banner -->
              <q-banner class="bg-blue-1 q-mb-lg" rounded>
                <template v-slot:avatar>
                  <q-icon name="event_available" color="blue" size="32px" />
                </template>
                <div class="text-weight-bold text-blue-9">
                  Planned Sprint: "{{ plannedSprint?.name }}"
                </div>
                <div class="text-body2 q-mt-xs">
                  This analysis helps you optimize the sprint before starting it. 
                  Apply recommended changes, then start the sprint when ready.
                </div>
              </q-banner>

              <!-- Loading State -->
              <div v-if="requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-spinner-dots color="primary" size="48px" class="q-mb-md" />
                <div class="text-h6 text-grey-7">Analyzing Planned Sprint...</div>
                <div class="text-body2 text-grey-6">
                  Searching for optimization opportunities
                </div>
              </div>

              <OptimizationProposals
                v-else-if="hasProposals"
                :proposals="proposals"
                :selected-proposals="requirementChangeStore.selectedProposals"
                :scope="requirementChangeStore.analysisResult?.scope"
                @toggle-selection="requirementChangeStore.toggleProposalSelection"
                @select-all="requirementChangeStore.selectAllProposals"
                @deselect-all="requirementChangeStore.deselectAllProposals"
              />

              <div v-else-if="hasAnalysis" class="text-center q-pa-xl">
                <q-icon name="check_circle" size="64px" color="green" class="q-mb-md" />
                <div class="text-h6">Planned Sprint is Optimized!</div>
                <div class="text-body2 text-grey-7">
                  No optimization opportunities found. Ready to start!
                </div>
              </div>

              <div v-else-if="!requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-icon name="analytics" size="64px" color="grey-5" class="q-mb-md" />
                <div class="text-h6 text-grey-6">Ready to Optimize</div>
                <div class="text-body2 text-grey-7">
                  Click "Analyze & Optimize" to find opportunities before starting the sprint
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
                <div class="row q-gutter-sm">
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
                  <q-btn
                    color="purple"
                    icon="schedule"
                    label="PERT+RACI Analysis"
                    @click="analyzePertRaciTab('current_sprint')"
                    :loading="requirementChangeStore.loading"
                    :disable="!selectedProjectId || initialLoading"
                    size="lg"
                    unelevated
                  >
                    <q-tooltip>Specialized analysis for PERT duration and RACI workload</q-tooltip>
                  </q-btn>
                </div>
                      </div>

              <!-- Loading State -->
              <div v-if="requirementChangeStore.loading" class="text-center q-pa-xl">
                <q-spinner-dots color="primary" size="48px" class="q-mb-md" />
                <div class="text-h6 text-grey-7">Analyzing Sprint...</div>
                <div class="text-body2 text-grey-6">
                  Searching for optimization opportunities
                </div>
              </div>

              <OptimizationProposals
                v-else-if="hasProposals"
                :proposals="proposals"
                :selected-proposals="requirementChangeStore.selectedProposals"
                :scope="requirementChangeStore.analysisResult?.scope"
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
import { ref, computed, onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';
import { useRequirementChangeStore, type OptimizationScope } from 'src/stores/requirement-change-store';
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

// Clear analysis when switching tabs
watch(activeTab, () => {
  requirementChangeStore.clearAnalysis();
});

// Computed
const projectOptions = computed(() => {
  return projectStore.projects.map((project) => ({
    label: project.name,
    value: project.id,
  }));
});

const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null;
  const project = projectStore.projects.find((p) => p.id === selectedProjectId.value);
  if (!project) return null;

  // Filter out Split tasks (they should not be displayed in normal views)
  return {
    ...project,
    tasks: projectStore.filterActiveTasks(project.tasks || []),
  };
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

  const sprints = selectedProject.value.sprints || [];

  // Calculate average workload from team members (from active sprints only)
  const members = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  // Get active sprint
  const activeSprint = sprints.find((s) => s.status === 'active');

  let totalWorkload = 0;
  members.forEach((member) => {
    const maxStoryPoints = member.maxStoryPoints || 20;

    // Only count tasks from active sprint (including Done - Sprint Commitment)
    const tasks = (selectedProject.value?.tasks || []).filter((task) => {
      const isInSprint = activeSprint ? task.sprintId === activeSprint.id : false;
      const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
      return isInSprint && isAssigned;
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

  // Calculate PERT/RACI metrics from analysis result if available
  const analysisState = requirementChangeStore.analysisResult?.currentState;

  // Calculate RACI Workload average for current project only
  let raciProjectWorkload = 0;
  if (raciProjectWorkloadDetails.value.length > 0) {
    const totalWorkload = raciProjectWorkloadDetails.value.reduce((sum, m) => sum + m.workload, 0);
    raciProjectWorkload = Math.round(totalWorkload / raciProjectWorkloadDetails.value.length);
  }

  // Calculate RACI Workload average across all projects
  let raciCrossProjectWorkload = 0;
  if (raciCrossProjectWorkloadDetails.value.length > 0) {
    const totalWorkload = raciCrossProjectWorkloadDetails.value.reduce((sum, m) => sum + m.workload, 0);
    raciCrossProjectWorkload = Math.round(totalWorkload / raciCrossProjectWorkloadDetails.value.length);
  }

  return {
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
    // PERT/RACI metrics - both project and cross-project RACI workloads
    totalPertDuration: analysisState?.totalPertDuration,
    totalAdjustedDuration: analysisState?.totalAdjustedDuration,
    avgPertUncertainty: analysisState?.avgPertUncertainty,
    raciProjectWorkload: raciProjectWorkload, // RACI workload for current project only
    raciCrossProjectWorkload: raciCrossProjectWorkload, // RACI workload across all projects
    durationOverhead: analysisState?.durationOverhead,
  };
});

const hasActiveSprint = computed(() => {
  if (!selectedProject.value?.sprints) return false;
  return selectedProject.value.sprints.some((sprint) => sprint.status === 'active');
});

const hasPlannedSprint = computed(() => {
  if (!selectedProject.value?.sprints) return false;
  return selectedProject.value.sprints.some((sprint) => sprint.status === 'planned');
});

const plannedSprint = computed(() => {
  if (!selectedProject.value?.sprints) return null;
  return selectedProject.value.sprints.find((s) => s.status === 'planned') || null;
});

const teamWorkloadDetails = computed(() => {
  if (!selectedProject.value) return [];

  const members = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  // Get active sprint
  const activeSprint = (selectedProject.value.sprints || []).find((s) => s.status === 'active');

  return members.map((member) => {
    const maxStoryPoints = member.maxStoryPoints || 20;

    // Only count tasks from active sprint (including Done - Sprint Commitment)
    const tasks = (selectedProject.value?.tasks || []).filter((task) => {
      const isInSprint = activeSprint ? task.sprintId === activeSprint.id : false;
      const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
      return isInSprint && isAssigned;
    });

    const memberStoryPoints = tasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
    const workload = maxStoryPoints > 0 ? Math.round((memberStoryPoints / maxStoryPoints) * 100) : 0;

    return {
      id: member.id,
      name: member.name,
      workload: workload,
    };
  }).sort((a, b) => b.workload - a.workload);
});

const crossProjectWorkload = computed(() => {
  if (!selectedProject.value) {
    return { average: 0, details: [] };
  }

  // Get members from current project
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  // Calculate workload across all projects for these members
  const memberWorkloads = projectMembers.map((member) => {
    const maxStoryPoints = member.maxStoryPoints || 20;
    let totalStoryPoints = 0;

    // Iterate through all projects
    projectStore.projects.forEach((project) => {
      // Check if member is in this project
      if (project.teamMemberIds && project.teamMemberIds.includes(member.id)) {
        // Get active sprint for this project
        const activeSprint = project.sprints?.find((s) => s.status === 'active');

        if (project.tasks && activeSprint) {
          // Count tasks from active sprint (including Done - Sprint Commitment)
          const sprintTasks = project.tasks.filter((task) => {
            const isInSprint = task.sprintId === activeSprint.id;
            const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
            return isInSprint && isAssigned;
          });
          totalStoryPoints += sprintTasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
        }
      }
    });

    const workload = maxStoryPoints > 0 ? Math.round((totalStoryPoints / maxStoryPoints) * 100) : 0;

    return {
      id: member.id,
      name: member.name,
      workload: workload,
    };
  });

  const average = memberWorkloads.length > 0
    ? Math.round(memberWorkloads.reduce((sum, m) => sum + m.workload, 0) / memberWorkloads.length)
    : 0;

  return {
    average,
    details: memberWorkloads.sort((a, b) => b.workload - a.workload),
  };
});

// RACI Weights (same as backend)
const RACI_WEIGHTS = {
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
};

// RACI Workload for current project only
const raciProjectWorkloadDetails = computed(() => {
  if (!selectedProject.value) return [];

  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  // Get active sprint for current project
  const activeSprint = selectedProject.value.sprints?.find((s) => s.status === 'active');

  return projectMembers.map((member) => {
    const maxStoryPoints = member.maxStoryPoints || 20;
    let weightedSP = 0;

    // Calculate RACI-weighted workload for CURRENT project only (if active sprint exists)
    if (activeSprint) {
      const sprintTasks = (selectedProject.value?.tasks || []).filter(
        (task) => task.sprintId === activeSprint.id
      );

      sprintTasks.forEach((task) => {
        const sp = task.storyPoints || 0;
        if (sp === 0) return;

        // Responsible
        if (task.raci?.responsible && task.raci.responsible.includes(member.id)) {
          weightedSP += sp * RACI_WEIGHTS.responsible;
        }

        // Accountable
        if (task.raci?.accountable === member.id) {
          weightedSP += sp * RACI_WEIGHTS.accountable;
        }

        // Consulted
        if (task.raci?.consulted && task.raci.consulted.includes(member.id)) {
          weightedSP += sp * RACI_WEIGHTS.consulted;
        }

        // Informed
        if (task.raci?.informed && task.raci.informed.includes(member.id)) {
          weightedSP += sp * RACI_WEIGHTS.informed;
        }
      });
    }
    // If no active sprint, weightedSP stays 0 for all members

    const workload = maxStoryPoints > 0 ? Math.round((weightedSP / maxStoryPoints) * 100) : 0;

    return {
      id: member.id,
      name: member.name,
      workload: workload, // Already rounded to whole number
      weightedSP: Math.round(weightedSP), // Round weighted SP to whole number
    };
  })
  // Show all members, even with 0% workload (for consistency with non-RACI workload displays)
  .sort((a, b) => b.workload - a.workload);
});

// RACI Workload across all projects (cross-project)
const raciCrossProjectWorkloadDetails = computed(() => {
  if (!selectedProject.value) return [];

  // Get members from current project only (but calculate cross-project workload for them)
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id)
  );

  return projectMembers.map((member) => {
    const maxStoryPoints = member.maxStoryPoints || 20;
    let weightedSP = 0;

    // Calculate RACI-weighted workload across ALL projects (each with its own active sprint)
    projectStore.projects.forEach((project) => {
      // FIX: Find active sprint for EACH project (not just selected project)
      const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');

      if (project.tasks && projectActiveSprint) {
        const sprintTasks = project.tasks.filter((task) => task.sprintId === projectActiveSprint.id);

        sprintTasks.forEach((task) => {
          const sp = task.storyPoints || 0;
          if (sp === 0) return;

          // Responsible
          if (task.raci?.responsible && task.raci.responsible.includes(member.id)) {
            weightedSP += sp * RACI_WEIGHTS.responsible;
          }

          // Accountable
          if (task.raci?.accountable === member.id) {
            weightedSP += sp * RACI_WEIGHTS.accountable;
          }

          // Consulted
          if (task.raci?.consulted && task.raci.consulted.includes(member.id)) {
            weightedSP += sp * RACI_WEIGHTS.consulted;
          }

          // Informed
          if (task.raci?.informed && task.raci.informed.includes(member.id)) {
            weightedSP += sp * RACI_WEIGHTS.informed;
          }
        });
      }
    });

    const workload = maxStoryPoints > 0 ? Math.round((weightedSP / maxStoryPoints) * 100) : 0;

    return {
      id: member.id,
      name: member.name,
      workload: workload, // Already rounded to whole number
      weightedSP: Math.round(weightedSP), // Round weighted SP to whole number
    };
  })
  // Show all members, even with 0% workload (for consistency with non-RACI workload displays)
  .sort((a, b) => b.workload - a.workload);
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

  return {
    deadlineRisks: tasks.filter((t) => t.dueDate && new Date(t.dueDate) < new Date()).length,
    overloadedMembers: teamWorkloadDetails.value.filter((m) => m.workload > 85).length,
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

async function analyzeTab(scope: OptimizationScope) {
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

async function analyzePertRaciTab(scope: OptimizationScope) {
  if (!selectedProjectId.value) return;

  const result = await requirementChangeStore.analyzePertRaci(
    selectedProjectId.value,
    scope
  );

  if (result) {
    $q.notify({
      message: result.message || `Found ${result.totalProposals || 0} PERT+RACI opportunities`,
      color: 'positive',
      icon: 'schedule',
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
    const result = await requirementChangeStore.applyChanges(
      selectedProjectId.value,
      selectedProposals
    );

    if (result.success) {
      let message: string;
      if (result.applied > 0 && result.skipped > 0) {
        message = `Applied ${result.applied} changes. ${result.skipped} proposals require manual action.`;
      } else if (result.applied > 0) {
        message = `Successfully applied ${result.applied} changes!`;
      } else {
        const count = result.skipped || selectedProposals.length;
        message = `${count} proposals require manual action. Edit tasks to add RACI assignments.`;
      }
      $q.notify({
        message,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
        timeout: 4000,
      });

      showApplyDialog.value = false;
      await projectStore.getProject(selectedProjectId.value);
      requirementChangeStore.clearAnalysis();
    } else {
      const errMsg = requirementChangeStore.error;
      $q.notify({
        message:
          result.failed > 0
            ? errMsg || `${result.failed} changes failed. Check console for details.`
            : 'Failed to apply changes.',
        color: 'negative',
        icon: 'error',
        position: 'top',
        timeout: 5000,
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
    idle_resource: 'person_off',
    pert_uncertainty: 'schedule',
    raci_overload: 'people',
    duration_risk: 'schedule_send',
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

function getDurationOverheadColor(overhead: number): string {
  if (overhead >= 50) return 'text-red';
  if (overhead >= 20) return 'text-orange';
  return 'text-green';
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
