<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">PERT + RACI Integration</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Combined project analysis with time estimates and responsibility matrix
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn color="secondary" icon="calculate" label="Recalculate" @click="recalculateAll" />
          <q-btn color="primary" icon="tune" label="Optimize" @click="optimizeTasks" />
        </div>
      </div>

      <!-- Project Selection -->
      <q-select
        v-model="selectedProjectId"
        :options="projectOptions"
        label="Select Project"
        filled
        emit-value
        map-options
        class="q-mt-md"
        style="max-width: 400px"
      >
        <template v-slot:prepend>
          <q-icon name="folder" />
        </template>
      </q-select>
    </div>

    <div v-if="selectedProject" class="q-pa-lg">
      <div class="row q-gutter-lg">
        <!-- Configuration Panel -->
        <div class="col-12 col-lg-4">
          <!-- RACI Weights Configuration -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">RACI Weights Configuration</div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Responsible (R) Weight</div>
                <q-input
                  v-model.number="raciWeights.responsible"
                  type="number"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.60</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Accountable (A) Weight</div>
                <q-input
                  v-model.number="raciWeights.accountable"
                  type="number"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.45</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Consulted (C) Weight</div>
                <q-input
                  v-model.number="raciWeights.consulted"
                  type="number"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.30</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Informed (I) Weight</div>
                <q-input
                  v-model.number="raciWeights.informed"
                  type="number"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.05</div>
              </div>

              <div class="row q-gutter-sm">
                <q-btn
                  color="primary"
                  icon="check"
                  label="Apply Weights"
                  @click="applyWeights"
                  class="col"
                />
                <q-btn
                  color="secondary"
                  icon="restore"
                  label="Reset"
                  @click="resetWeights"
                  class="col"
                />
              </div>
            </q-card-section>
          </q-card>

          <!-- Formula Display -->
          <q-card>
            <q-expansion-item
              icon="functions"
              label="Combined Formula"
              header-class="text-primary text-h6 text-weight-bold"
            >
              <div class="q-pa-md">
                <div class="formula-section q-mb-md">
                  <div class="text-subtitle2 text-weight-medium q-mb-sm">PERT Duration</div>
                  <div class="formula-box">
                    <div class="formula">T = (O + 4M + P) / 6</div>
                    <div class="formula-description">
                      kde: O = optimistic time, M = most likely time, P = pessimistic time
                    </div>
                  </div>
                </div>

                <div class="formula-section q-mb-md">
                  <div class="text-subtitle2 text-weight-medium q-mb-sm">
                    RACI Adjusted Duration
                  </div>
                  <div class="formula-box">
                    <div class="formula">
                      T<sub>new</sub> = T × (1 + ({{ raciWeights.responsible }}×L<sub>R</sub>) + ({{
                        raciWeights.accountable
                      }}×L<sub>A</sub>) + ({{ raciWeights.consulted }}×L<sub>C</sub>) + ({{
                        raciWeights.informed
                      }}×L<sub>I</sub>))
                    </div>
                    <div class="formula-description">
                      kde: L<sub>R,A,C,I</sub> = preťaženie pre danú RACI rolu
                    </div>
                  </div>
                </div>

                <!-- Expandable Detailed Formula Section -->
                <q-expansion-item
                  icon="help_outline"
                  label="Podrobné vysvetlenie vzorcov"
                  header-class="text-secondary"
                >
                  <div class="q-pa-md">
                    <div class="formula-section">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">
                        Vysvetlivky premenných
                      </div>
                      <div class="variables-list">
                        <div class="variable-item">
                          <strong>T</strong> = PERT duration (vypočítané z optimistic, most likely,
                          pessimistic času)
                        </div>
                        <div class="variable-item">
                          <strong>T<sub>new</sub></strong> = Finálne upravené trvanie úlohy po
                          aplikovaní RACI korekcie
                        </div>
                        <div class="variable-item">
                          <strong>L<sub>R</sub></strong> = Preťaženie z Responsible rolí (story
                          points za sprint pre Responsible rolu / {{ maxStoryPointsPerPerson }})
                        </div>
                        <div class="variable-item">
                          <strong>L<sub>A</sub></strong> = Preťaženie z Accountable rolí (story
                          points za sprint pre Accountable rolu / {{ maxStoryPointsPerPerson }})
                        </div>
                        <div class="variable-item">
                          <strong>L<sub>C</sub></strong> = Preťaženie z Consulted rolí (story points
                          za sprint pre Consulted rolu / {{ maxStoryPointsPerPerson }})
                        </div>
                        <div class="variable-item">
                          <strong>L<sub>I</sub></strong> = Preťaženie z Informed rolí (story points
                          za sprint pre Informed rolu / {{ maxStoryPointsPerPerson }})
                        </div>
                        <div class="variable-item">
                          <strong>{{ maxStoryPointsPerPerson }}</strong> = maximum story points na
                          jedného človeka za sprint
                        </div>
                        <div class="variable-item">
                          <strong
                            >{{ raciWeights.responsible }}, {{ raciWeights.accountable }},
                            {{ raciWeights.consulted }}, {{ raciWeights.informed }}</strong
                          >
                          = Váhy pre jednotlivé RACI roly (konfigurovateľné)
                        </div>
                      </div>
                    </div>
                  </div>
                </q-expansion-item>
              </div>
            </q-expansion-item>
          </q-card>
        </div>

        <!-- Tasks Table -->
        <div class="col-12 col-lg-8">
          <q-card>
            <q-card-section>
              <div class="row items-center justify-between q-mb-md">
                <div class="text-h6 text-weight-bold">Project Tasks</div>
                <div class="row q-gutter-sm">
                  <q-btn flat icon="add" label="Add Task" @click="showAddTaskDialog = true" />
                  <q-btn flat icon="download" label="Export" @click="exportData" />
                </div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-section class="q-pa-none">
              <q-table
                :rows="tasksWithRaciRoles"
                :columns="taskColumns"
                row-key="id"
                :pagination="{ rowsPerPage: 10 }"
                class="tasks-table"
              >
                <!-- Expandable content for each row -->
                <template v-slot:body="props">
                  <q-tr :props="props">
                    <q-td>
                      <q-btn
                        flat
                        round
                        :icon="
                          expandedRows.includes(props.row.id.toString())
                            ? 'expand_less'
                            : 'expand_more'
                        "
                        @click="toggleRowExpansion(props.row.id)"
                        size="sm"
                      />
                    </q-td>
                    <q-td>{{ props.row.name }}</q-td>
                    <q-td>{{ props.row.storyPoints }}</q-td>
                    <q-td>
                      <div class="text-weight-medium">{{ props.row.pertDuration.toFixed(2) }}d</div>
                    </q-td>
                    <q-td>
                      <div class="text-weight-bold" :class="getDurationClass(props.row)">
                        {{ props.row.adjustedDuration.toFixed(2) }}d
                      </div>
                      <div class="text-caption text-grey-7">
                        {{ getDurationChange(props.row) }}
                      </div>
                    </q-td>
                    <q-td>
                      <div class="row q-gutter-xs">
                        <q-chip
                          v-for="role in props.row.raciRoles"
                          :key="role.type"
                          :color="getRaciColor(role.type)"
                          text-color="white"
                          size="sm"
                          :label="`${role.type}(${role.members.length})`"
                        />
                      </div>
                    </q-td>
                    <q-td>
                      <div class="row q-gutter-xs">
                        <q-btn flat icon="edit" size="sm" @click="editTask(props.row)" />
                        <q-btn
                          flat
                          icon="delete"
                          size="sm"
                          color="negative"
                          @click="deleteTask(props.row.id)"
                        />
                      </div>
                    </q-td>
                  </q-tr>

                  <!-- Expanded content -->
                  <q-tr v-if="expandedRows.includes(props.row.id.toString())" :props="props">
                    <q-td colspan="7" class="q-pa-none">
                      <q-card class="q-ma-sm">
                        <q-card-section>
                          <div class="text-h6 text-weight-bold q-mb-md">
                            RACI Team Members Details
                          </div>

                          <div class="row q-gutter-md">
                            <!-- Responsible Members -->
                            <div
                              class="col-12 col-md-6 col-lg-3"
                              v-if="props.row.raciMembers.responsible.length > 0"
                            >
                              <div class="text-subtitle2 text-weight-medium q-mb-sm text-red">
                                Responsible (R)
                              </div>
                              <div
                                v-for="memberId in props.row.raciMembers.responsible"
                                :key="`R-${memberId}`"
                              >
                                <q-card class="member-detail-card">
                                  <q-card-section class="q-pa-sm">
                                    <div class="row items-center">
                                      <q-avatar size="24px" class="q-mr-sm">
                                        <q-icon name="person" />
                                      </q-avatar>
                                      <div class="col">
                                        <div class="text-weight-medium">
                                          {{ getMemberName(memberId) }}
                                        </div>
                                        <div class="text-caption text-grey-7">
                                          ID: {{ memberId }}
                                        </div>
                                        <div class="text-caption text-primary">
                                          Total: {{ getMemberTotalStoryPoints(memberId) }} SP
                                        </div>
                                      </div>
                                      <div class="col-auto">
                                        <q-btn
                                          flat
                                          round
                                          :icon="
                                            getMemberExpanded(memberId)
                                              ? 'expand_less'
                                              : 'expand_more'
                                          "
                                          @click="toggleMemberExpansion(memberId)"
                                          size="sm"
                                        />
                                      </div>
                                    </div>

                                    <!-- Member's tasks -->
                                    <div v-if="getMemberExpanded(memberId)" class="q-mt-sm">
                                      <div class="text-caption text-weight-medium q-mb-xs">
                                        All Tasks:
                                      </div>
                                      <div
                                        v-for="task in getMemberTasks(memberId)"
                                        :key="task.id"
                                        class="q-mb-xs"
                                      >
                                        <q-chip
                                          :color="getTaskRoleColor(task.id, memberId)"
                                          text-color="white"
                                          size="xs"
                                          :label="`${task.name} (${task.storyPoints}SP)`"
                                        />
                                      </div>
                                    </div>
                                  </q-card-section>
                                </q-card>
                              </div>
                            </div>

                            <!-- Accountable Members -->
                            <div
                              class="col-12 col-md-6 col-lg-3"
                              v-if="props.row.raciMembers.accountable !== null"
                            >
                              <div class="text-subtitle2 text-weight-medium q-mb-sm text-blue">
                                Accountable (A)
                              </div>
                              <div
                                v-if="props.row.raciMembers.accountable"
                                :key="`A-${props.row.raciMembers.accountable}`"
                              >
                                <q-card class="member-detail-card">
                                  <q-card-section class="q-pa-sm">
                                    <div class="row items-center">
                                      <q-avatar size="24px" class="q-mr-sm">
                                        <q-icon name="person" />
                                      </q-avatar>
                                      <div class="col">
                                        <div class="text-weight-medium">
                                          {{ getMemberName(props.row.raciMembers.accountable) }}
                                        </div>
                                        <div class="text-caption text-grey-7">
                                          ID: {{ props.row.raciMembers.accountable }}
                                        </div>
                                        <div class="text-caption text-primary">
                                          Total:
                                          {{
                                            getMemberTotalStoryPoints(
                                              props.row.raciMembers.accountable,
                                            )
                                          }}
                                          SP
                                        </div>
                                      </div>
                                      <div class="col-auto">
                                        <q-btn
                                          flat
                                          round
                                          :icon="
                                            getMemberExpanded(props.row.raciMembers.accountable)
                                              ? 'expand_less'
                                              : 'expand_more'
                                          "
                                          @click="
                                            toggleMemberExpansion(props.row.raciMembers.accountable)
                                          "
                                          size="sm"
                                        />
                                      </div>
                                    </div>

                                    <!-- Member's tasks -->
                                    <div
                                      v-if="getMemberExpanded(props.row.raciMembers.accountable)"
                                      class="q-mt-sm"
                                    >
                                      <div class="text-caption text-weight-medium q-mb-xs">
                                        All Tasks:
                                      </div>
                                      <div
                                        v-for="task in getMemberTasks(
                                          props.row.raciMembers.accountable,
                                        )"
                                        :key="task.id"
                                        class="q-mb-xs"
                                      >
                                        <q-chip
                                          :color="
                                            getTaskRoleColor(
                                              task.id,
                                              props.row.raciMembers.accountable,
                                            )
                                          "
                                          text-color="white"
                                          size="xs"
                                          :label="`${task.name} (${task.storyPoints}SP)`"
                                        />
                                      </div>
                                    </div>
                                  </q-card-section>
                                </q-card>
                              </div>
                            </div>

                            <!-- Consulted Members -->
                            <div
                              class="col-12 col-md-6 col-lg-3"
                              v-if="props.row.raciMembers.consulted.length > 0"
                            >
                              <div class="text-subtitle2 text-weight-medium q-mb-sm text-orange">
                                Consulted (C)
                              </div>
                              <div
                                v-for="memberId in props.row.raciMembers.consulted"
                                :key="`C-${memberId}`"
                              >
                                <q-card class="member-detail-card">
                                  <q-card-section class="q-pa-sm">
                                    <div class="row items-center">
                                      <q-avatar size="24px" class="q-mr-sm">
                                        <q-icon name="person" />
                                      </q-avatar>
                                      <div class="col">
                                        <div class="text-weight-medium">
                                          {{ getMemberName(memberId) }}
                                        </div>
                                        <div class="text-caption text-grey-7">
                                          ID: {{ memberId }}
                                        </div>
                                        <div class="text-caption text-primary">
                                          Total: {{ getMemberTotalStoryPoints(memberId) }} SP
                                        </div>
                                      </div>
                                      <div class="col-auto">
                                        <q-btn
                                          flat
                                          round
                                          :icon="
                                            getMemberExpanded(memberId)
                                              ? 'expand_less'
                                              : 'expand_more'
                                          "
                                          @click="toggleMemberExpansion(memberId)"
                                          size="sm"
                                        />
                                      </div>
                                    </div>

                                    <!-- Member's tasks -->
                                    <div v-if="getMemberExpanded(memberId)" class="q-mt-sm">
                                      <div class="text-caption text-weight-medium q-mb-xs">
                                        All Tasks:
                                      </div>
                                      <div
                                        v-for="task in getMemberTasks(memberId)"
                                        :key="task.id"
                                        class="q-mb-xs"
                                      >
                                        <q-chip
                                          :color="getTaskRoleColor(task.id, memberId)"
                                          text-color="white"
                                          size="xs"
                                          :label="`${task.name} (${task.storyPoints}SP)`"
                                        />
                                      </div>
                                    </div>
                                  </q-card-section>
                                </q-card>
                              </div>
                            </div>

                            <!-- Informed Members -->
                            <div
                              class="col-12 col-md-6 col-lg-3"
                              v-if="props.row.raciMembers.informed.length > 0"
                            >
                              <div class="text-subtitle2 text-weight-medium q-mb-sm text-green">
                                Informed (I)
                              </div>
                              <div
                                v-for="memberId in props.row.raciMembers.informed"
                                :key="`I-${memberId}`"
                              >
                                <q-card class="member-detail-card">
                                  <q-card-section class="q-pa-sm">
                                    <div class="row items-center">
                                      <q-avatar size="24px" class="q-mr-sm">
                                        <q-icon name="person" />
                                      </q-avatar>
                                      <div class="col">
                                        <div class="text-weight-medium">
                                          {{ getMemberName(memberId) }}
                                        </div>
                                        <div class="text-caption text-grey-7">
                                          ID: {{ memberId }}
                                        </div>
                                        <div class="text-caption text-primary">
                                          Total: {{ getMemberTotalStoryPoints(memberId) }} SP
                                        </div>
                                      </div>
                                      <div class="col-auto">
                                        <q-btn
                                          flat
                                          round
                                          :icon="
                                            getMemberExpanded(memberId)
                                              ? 'expand_less'
                                              : 'expand_more'
                                          "
                                          @click="toggleMemberExpansion(memberId)"
                                          size="sm"
                                        />
                                      </div>
                                    </div>

                                    <!-- Member's tasks -->
                                    <div v-if="getMemberExpanded(memberId)" class="q-mt-sm">
                                      <div class="text-caption text-weight-medium q-mb-xs">
                                        All Tasks:
                                      </div>
                                      <div
                                        v-for="task in getMemberTasks(memberId)"
                                        :key="task.id"
                                        class="q-mb-xs"
                                      >
                                        <q-chip
                                          :color="getTaskRoleColor(task.id, memberId)"
                                          text-color="white"
                                          size="xs"
                                          :label="`${task.name} (${task.storyPoints}SP)`"
                                        />
                                      </div>
                                    </div>
                                  </q-card-section>
                                </q-card>
                              </div>
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </q-td>
                  </q-tr>
                </template>
              </q-table>
            </q-card-section>
          </q-card>

          <!-- Summary Statistics -->
          <q-card class="q-mt-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Summary Statistics</div>

              <div class="row q-gutter-lg">
                <div class="col-12 col-md-4">
                  <div class="stat-card text-center">
                    <div class="text-h4 text-primary text-weight-bold">
                      {{ totalPertDuration.toFixed(2) }}
                    </div>
                    <div class="text-grey-7">Total PERT Duration (days)</div>
                  </div>
                </div>
                <div class="col-12 col-md-4">
                  <div class="stat-card text-center">
                    <div class="text-h4 text-orange text-weight-bold">
                      {{ totalAdjustedDuration.toFixed(2) }}
                    </div>
                    <div class="text-grey-7">Total Adjusted Duration (days)</div>
                  </div>
                </div>
                <div class="col-12 col-md-4">
                  <div class="stat-card text-center">
                    <div class="text-h4 text-green text-weight-bold">
                      {{ durationIncrease.toFixed(1) }}%
                    </div>
                    <div class="text-grey-7">Duration Increase</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Add/Edit Task Dialog -->
      <q-dialog v-model="showAddTaskDialog" persistent>
        <q-card style="min-width: 600px">
          <q-card-section>
            <div class="text-h6">{{ editingTask ? 'Edit Task' : 'Add New Task' }}</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model="taskForm.name"
                  label="Task Name"
                  filled
                  :rules="[(val) => !!val || 'Task name is required']"
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="taskForm.storyPoints"
                  label="Story Points"
                  type="number"
                  :min="1"
                  :max="20"
                  filled
                />
              </div>
            </div>

            <q-input
              v-model="taskForm.description"
              label="Description"
              type="textarea"
              filled
              rows="3"
              class="q-mt-md"
            />

            <div class="row q-gutter-md q-mt-md">
              <div class="col">
                <q-input
                  v-model.number="taskForm.optimistic"
                  label="Optimistic (days)"
                  type="number"
                  :min="0.5"
                  :step="0.5"
                  filled
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="taskForm.mostLikely"
                  label="Most Likely (days)"
                  type="number"
                  :min="0.5"
                  :step="0.5"
                  filled
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="taskForm.pessimistic"
                  label="Pessimistic (days)"
                  type="number"
                  :min="0.5"
                  :step="0.5"
                  filled
                />
              </div>
            </div>

            <!-- RACI Assignment -->
            <div class="q-mt-md">
              <div class="text-subtitle2 q-mb-sm">RACI Assignment</div>

              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">Responsible (R)</div>
                <q-select
                  v-model="taskForm.raciMembers.responsible"
                  :options="teamMembers"
                  option-label="name"
                  option-value="id"
                  multiple
                  use-chips
                  filled
                  dense
                  placeholder="Select team members"
                />
              </div>

              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">Accountable (A)</div>
                <q-select
                  v-model="taskForm.raciMembers.accountable"
                  :options="teamMembers"
                  option-label="name"
                  option-value="id"
                  multiple
                  use-chips
                  filled
                  dense
                  placeholder="Select team members"
                />
              </div>

              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">Consulted (C)</div>
                <q-select
                  v-model="taskForm.raciMembers.consulted"
                  :options="teamMembers"
                  option-label="name"
                  option-value="id"
                  multiple
                  use-chips
                  filled
                  dense
                  placeholder="Select team members"
                />
              </div>

              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">Informed (I)</div>
                <q-select
                  v-model="taskForm.raciMembers.informed"
                  :options="teamMembers"
                  option-label="name"
                  option-value="id"
                  multiple
                  use-chips
                  filled
                  dense
                  placeholder="Select team members"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" @click="cancelTaskDialog" />
            <q-btn
              color="primary"
              :label="editingTask ? 'Update' : 'Add'"
              @click="saveTask"
              :disable="!taskForm.name"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>

    <div v-else class="q-pa-xl text-center text-grey-5">
      <q-icon name="folder_open" size="64px" class="q-mb-md" />
      <div class="text-h6">Select a project to view PERT + RACI analysis</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';

const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();

// Project Selection
const selectedProjectId = ref<number | null>(null);

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

// Interfaces
interface Task {
  id: number;
  name: string;
  description: string;
  storyPoints: number;
  optimistic: number;
  mostLikely: number;
  pessimistic: number;
  pertDuration: number;
  adjustedDuration: number;
  raciMembers: {
    responsible: number[];
    accountable: number | null; // Single value or null (RACI standard)
    consulted: number[];
    informed: number[];
  };
  overload: number;
}

interface RaciWeights {
  responsible: number;
  accountable: number;
  consulted: number;
  informed: number;
}

interface TaskForm {
  name: string;
  description: string;
  storyPoints: number;
  optimistic: number;
  mostLikely: number;
  pessimistic: number;
  raciMembers: {
    responsible: number[];
    accountable: number | null; // Single value or null (RACI standard)
    consulted: number[];
    informed: number[];
  };
}

// Reactive data
const showAddTaskDialog = ref(false);
const editingTask = ref<Task | null>(null);
const expandedRows = ref<string[]>([]);
const expandedMembers = ref<string[]>([]);

const raciWeights = ref<RaciWeights>({
  responsible: 0.6,
  accountable: 0.45,
  consulted: 0.3,
  informed: 0.05,
});

// Maximum story points per person (fixed at 20)
const maxStoryPointsPerPerson = 20;

// Team members from store
const teamMembers = computed(() => {
  return teamStore.teamMembers.map((member) => ({
    id: member.id,
    name: member.name,
  }));
});

// Computed tasks from selected project
const tasks = computed<Task[]>(() => {
  if (!selectedProject.value) return [];

  return selectedProject.value.tasks.map((task) => {
    const pertDuration = calculatePertDuration(
      task.pert.optimistic || 0,
      task.pert.mostLikely || 0,
      task.pert.pessimistic || 0,
    );

    const raciMembers = {
      responsible: task.raci.responsible || [],
      accountable: task.raci.accountable, // Already single value or null
      consulted: task.raci.consulted || [],
      informed: task.raci.informed || [],
    };

    const taskObj: Task = {
      id: task.id,
      name: task.title || task.name,
      description: task.description || '',
      storyPoints: task.storyPoints,
      optimistic: task.pert.optimistic || 0,
      mostLikely: task.pert.mostLikely || 0,
      pessimistic: task.pert.pessimistic || 0,
      pertDuration,
      adjustedDuration: 0, // Will be calculated
      raciMembers,
      overload: calculateRaciOverload(raciMembers),
    };

    taskObj.adjustedDuration = calculateAdjustedDuration(taskObj);
    return taskObj;
  });
});

const taskForm = reactive<TaskForm>({
  name: '',
  description: '',
  storyPoints: 5,
  optimistic: 1,
  mostLikely: 2,
  pessimistic: 4,
  raciMembers: {
    responsible: [],
    accountable: null, // Single value or null (RACI standard)
    consulted: [],
    informed: [],
  },
});

// Table columns
const taskColumns = [
  {
    name: 'expand',
    label: '',
    field: 'expand',
    align: 'center' as const,
    style: 'width: 50px',
  },
  {
    name: 'name',
    label: 'Task Name',
    field: 'name',
    align: 'left' as const,
    sortable: true,
  },
  {
    name: 'storyPoints',
    label: 'Story Points',
    field: 'storyPoints',
    align: 'center' as const,
  },
  {
    name: 'pertDuration',
    label: 'PERT Duration',
    field: 'pertDuration',
    align: 'center' as const,
  },
  {
    name: 'adjustedDuration',
    label: 'Adjusted Duration',
    field: 'adjustedDuration',
    align: 'center' as const,
  },
  {
    name: 'raciRoles',
    label: 'RACI Roles',
    field: 'raciRoles',
    align: 'center' as const,
  },
  {
    name: 'actions',
    label: 'Actions',
    field: 'actions',
    align: 'center' as const,
  },
];

// Computed properties
const tasksWithRaciRoles = computed(() => {
  return tasks.value.map((task) => ({
    ...task,
    raciRoles: [
      { type: 'R', members: task.raciMembers.responsible },
      {
        type: 'A',
        members: task.raciMembers.accountable !== null ? [task.raciMembers.accountable] : [],
      },
      { type: 'C', members: task.raciMembers.consulted },
      { type: 'I', members: task.raciMembers.informed },
    ].filter((role) => role.members.length > 0),
  }));
});

const totalPertDuration = computed(() => {
  return tasks.value.reduce((sum, task) => sum + task.pertDuration, 0);
});

const totalAdjustedDuration = computed(() => {
  return tasks.value.reduce((sum, task) => sum + task.adjustedDuration, 0);
});

const durationIncrease = computed(() => {
  if (totalPertDuration.value === 0) return 0;
  return ((totalAdjustedDuration.value - totalPertDuration.value) / totalPertDuration.value) * 100;
});

// Methods
function calculatePertDuration(
  optimistic: number,
  mostLikely: number,
  pessimistic: number,
): number {
  return (optimistic + 4 * mostLikely + pessimistic) / 6;
}

function calculateRaciOverload(raciMembers: Task['raciMembers']): number {
  const totalRaciCount =
    raciMembers.responsible.length +
    (raciMembers.accountable !== null ? 1 : 0) + // Single value or null
    raciMembers.consulted.length +
    raciMembers.informed.length;
  return totalRaciCount / maxStoryPointsPerPerson;
}

function calculateAdjustedDuration(task: Task): number {
  const pertDuration = task.pertDuration;

  const raciAdjustment =
    raciWeights.value.responsible *
      (task.raciMembers.responsible.length / maxStoryPointsPerPerson) +
    raciWeights.value.accountable *
      ((task.raciMembers.accountable !== null ? 1 : 0) / maxStoryPointsPerPerson) + // Single value or null
    raciWeights.value.consulted * (task.raciMembers.consulted.length / maxStoryPointsPerPerson) +
    raciWeights.value.informed * (task.raciMembers.informed.length / maxStoryPointsPerPerson);

  return pertDuration * (1 + raciAdjustment);
}

// Tasks are now computed, so recalculation happens automatically when dependencies change

function applyWeights() {
  // Validate weights
  const weights = raciWeights.value;
  if (
    weights.responsible < 0 ||
    weights.responsible > 1 ||
    weights.accountable < 0 ||
    weights.accountable > 1 ||
    weights.consulted < 0 ||
    weights.consulted > 1 ||
    weights.informed < 0 ||
    weights.informed > 1
  ) {
    $q.notify({
      message: 'Váhy musia byť v rozsahu 0 až 1',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Tasks are computed, so they will recalculate automatically with new weights
  $q.notify({
    message: `Váhy aplikované: R=${weights.responsible}, A=${weights.accountable}, C=${weights.consulted}, I=${weights.informed}`,
    color: 'positive',
    icon: 'check',
    position: 'top',
  });
}

function resetWeights() {
  raciWeights.value = {
    responsible: 0.6,
    accountable: 0.45,
    consulted: 0.3,
    informed: 0.05,
  };
  // Tasks are computed, so they will recalculate automatically with new weights

  $q.notify({
    message: 'Váhy resetované na predvolené hodnoty',
    color: 'info',
    icon: 'restore',
    position: 'top',
  });
}

function getRaciColor(role: string): string {
  switch (role) {
    case 'responsible':
      return 'red';
    case 'accountable':
      return 'blue';
    case 'consulted':
      return 'orange';
    case 'informed':
      return 'green';
    default:
      return 'grey';
  }
}

function getDurationClass(task: Task): string {
  const increase = (task.adjustedDuration - task.pertDuration) / task.pertDuration;
  if (increase > 0.2) return 'text-red';
  if (increase > 0.1) return 'text-orange';
  return 'text-green';
}

function getDurationChange(task: Task): string {
  const increase = ((task.adjustedDuration - task.pertDuration) / task.pertDuration) * 100;
  const sign = increase > 0 ? '+' : '';
  return `${sign}${increase.toFixed(1)}%`;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function editTask(_task: Task) {
  $q.notify({
    message:
      'Úprava taskov priamo v PERT+RACI optimalizácii nie je podporovaná. Upravte task v projekte.',
    color: 'info',
    icon: 'info',
    position: 'top',
  });
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function deleteTask(_taskId: number) {
  $q.notify({
    message:
      'Mazanie taskov priamo v PERT+RACI optimalizácii nie je podporované. Upravte tasky v projekte.',
    color: 'info',
    icon: 'info',
    position: 'top',
  });
}

function saveTask() {
  $q.notify({
    message:
      'Pridávanie taskov priamo v PERT+RACI optimalizácii nie je podporované. Pridajte tasky v projekte.',
    color: 'info',
    icon: 'info',
    position: 'top',
  });
  cancelTaskDialog();
}

function cancelTaskDialog() {
  showAddTaskDialog.value = false;
  editingTask.value = null;
  Object.assign(taskForm, {
    name: '',
    description: '',
    storyPoints: 5,
    optimistic: 1,
    mostLikely: 2,
    pessimistic: 4,
    raciMembers: {
      responsible: [],
      accountable: null,
      consulted: [],
      informed: [],
    },
  });
}

function recalculateAll() {
  // Tasks are computed, so they recalculate automatically
  $q.notify({
    message: 'Výpočty sa aktualizujú automaticky pri zmene váh alebo dát projektu',
    color: 'info',
    icon: 'calculate',
    position: 'top',
  });
}

function optimizeTasks() {
  $q.notify({
    message:
      'Optimalizácia RACI priradení bude dostupná v budúcej verzii. Teraz zobrazujeme reálne dáta z projektu.',
    color: 'info',
    icon: 'tune',
    position: 'top',
  });
}

// Team member functions

function getMemberName(memberId: number): string {
  const member = teamMembers.value.find((m: { id: number; name: string }) => m.id === memberId);
  return member ? member.name : `Member ${memberId}`;
}

function toggleRowExpansion(rowId: number) {
  const index = expandedRows.value.indexOf(rowId.toString());
  if (index > -1) {
    expandedRows.value.splice(index, 1);
  } else {
    expandedRows.value.push(rowId.toString());
  }
}

function getMemberTotalStoryPoints(memberId: number): number {
  let total = 0;
  tasks.value.forEach((task) => {
    if (
      task.raciMembers.responsible.includes(memberId) ||
      task.raciMembers.accountable === memberId ||
      task.raciMembers.consulted.includes(memberId) ||
      task.raciMembers.informed.includes(memberId)
    ) {
      total += task.storyPoints;
    }
  });
  return total;
}

function getMemberTasks(memberId: number): Task[] {
  return tasks.value.filter(
    (task) =>
      task.raciMembers.responsible.includes(memberId) ||
      task.raciMembers.accountable === memberId ||
      task.raciMembers.consulted.includes(memberId) ||
      task.raciMembers.informed.includes(memberId),
  );
}

function getTaskRoleColor(taskId: number, memberId: number): string {
  const task = tasks.value.find((t) => t.id === taskId);
  if (!task) return 'grey';

  if (task.raciMembers.responsible.includes(memberId)) return 'red';
  if (task.raciMembers.accountable === memberId) return 'blue';
  if (task.raciMembers.consulted.includes(memberId)) return 'orange';
  if (task.raciMembers.informed.includes(memberId)) return 'green';
  return 'grey';
}

function getMemberExpanded(memberId: number): boolean {
  return expandedMembers.value.includes(memberId.toString());
}

function toggleMemberExpansion(memberId: number) {
  const index = expandedMembers.value.indexOf(memberId.toString());
  if (index > -1) {
    expandedMembers.value.splice(index, 1);
  } else {
    expandedMembers.value.push(memberId.toString());
  }
}

function exportData() {
  const exportData = {
    raciWeights: raciWeights.value,
    maxStoryPointsPerPerson: maxStoryPointsPerPerson,
    tasks: tasks.value,
    summary: {
      totalPertDuration: totalPertDuration.value,
      totalAdjustedDuration: totalAdjustedDuration.value,
      durationIncrease: durationIncrease.value,
    },
  };

  const dataStr = JSON.stringify(exportData, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'pert-raci-optimization.json';
  link.click();
  URL.revokeObjectURL(url);

  $q.notify({
    message: 'Data exported successfully!',
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}

onMounted(async () => {
  await Promise.all([projectStore.fetchProjects(true), teamStore.fetchTeamMembers()]);

  // Set default project if available
  if (projectStore.projects.length > 0 && !selectedProjectId.value) {
    const firstProject = projectStore.projects[0];
    if (firstProject) {
      selectedProjectId.value = firstProject.id;
    }
  }
});
</script>

<style scoped>
.formula-section {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  border-left: 4px solid var(--q-primary);
}

.formula-box {
  background: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.formula {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: bold;
  color: #1976d2;
  margin-bottom: 8px;
}

.formula-description {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.tasks-table {
  border-radius: 8px;
}

.stat-card {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.variables-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.variable-item {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  border-left: 3px solid var(--q-primary);
  font-size: 14px;
}

.member-detail-card {
  border: 1px solid #e0e0e0;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.member-detail-card:hover {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
</style>
