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
      <div class="pert-raci-sections">
        <!-- Configuration Panel -->
        <div>
          <div class="raci-weights-grid q-mb-lg">
            <!-- RACI Weights Configuration (for Adjusted Duration Formula) -->
            <q-card>
              <q-card-section>
                <div class="text-h6 text-weight-bold q-mb-md">
                  RACI Weights - Overload Impact on Task Duration
                </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Responsible (R) Weight</div>
                <q-input
                  v-model.number="raciWeights.responsible"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 1.0</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Accountable (A) Weight</div>
                <q-input
                  v-model.number="raciWeights.accountable"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.1</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Consulted (C) Weight</div>
                <q-input
                  v-model.number="raciWeights.consulted"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.05</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Informed (I) Weight</div>
                <q-input
                  v-model.number="raciWeights.informed"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.01</div>
              </div>

                <div class="row q-gutter-sm">
                  <q-btn
                    color="primary"
                    icon="check"
                    label="Apply"
                    @click="applyDurationWeights"
                    class="col"
                  />
                  <q-btn
                    color="secondary"
                    icon="restore"
                    label="Reset"
                    @click="resetDurationWeights"
                    class="col"
                  />
                </div>
              </q-card-section>
            </q-card>

            <!-- RACI Weights Configuration (for Workload Calculation) -->
            <q-card>
              <q-card-section>
                <div class="text-h6 text-weight-bold q-mb-md">
                  RACI Weights - Work Share by Role
                </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Responsible (R) Weight</div>
                <q-input
                  v-model.number="raciWorkloadWeights.responsible"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 1.0</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Accountable (A) Weight</div>
                <q-input
                  v-model.number="raciWorkloadWeights.accountable"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.1</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Consulted (C) Weight</div>
                <q-input
                  v-model.number="raciWorkloadWeights.consulted"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.05</div>
              </div>

              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">Informed (I) Weight</div>
                <q-input
                  v-model.number="raciWorkloadWeights.informed"
                  type="number"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  filled
                  dense
                />
                <div class="text-caption text-grey-7">Default: 0.01</div>
              </div>

                <div class="row q-gutter-sm">
                  <q-btn
                    color="primary"
                    icon="check"
                    label="Apply"
                    @click="applyWorkloadWeights"
                    class="col"
                  />
                  <q-btn
                    color="secondary"
                    icon="restore"
                    label="Reset"
                    @click="resetWorkloadWeights"
                    class="col"
                  />
                </div>
              </q-card-section>
            </q-card>
          </div>

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
                    <div class="formula">
                      E<sub>t</sub> = (O<sub>t</sub> + 4M<sub>t</sub> + P<sub>t</sub>) / 6
                    </div>
                    <div class="formula-description">
                      where O<sub>t</sub> = optimistic, M<sub>t</sub> = most likely, P<sub>t</sub> =
                      pessimistic estimate for task t
                    </div>
                  </div>
                </div>

                <div class="formula-section q-mb-md">
                  <div class="text-subtitle2 text-weight-medium q-mb-sm">
                    Task Duration Extension from Role Overload
                  </div>
                  <div class="formula-box">
                    <div class="formula">
                      T<sub>adjusted,t</sub> = E<sub>t</sub> × (1 +
                      {{ raciWeights.responsible }}·L<sub>R,t</sub> +
                      {{ raciWeights.accountable }}·L<sub>A,t</sub> +
                      {{ raciWeights.consulted }}·L<sub>C,t</sub> +
                      {{ raciWeights.informed }}·L<sub>I,t</sub>)
                    </div>
                    <div class="formula-description">
                      where L<sub>X,t</sub> denotes role overload contribution for task t
                    </div>
                  </div>
                </div>

                <!-- Expandable Detailed Formula Section -->
                <q-expansion-item
                  icon="help_outline"
                  label="Detailed Formula Explanation"
                  header-class="text-secondary"
                >
                  <div class="q-pa-md">
                    <div class="formula-section q-mb-md">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">
                        Variable Definitions
                      </div>
                      <div class="variables-list">
                        <div class="variable-item">
                          <strong>E<sub>t</sub></strong> = expected PERT duration for task t
                        </div>
                        <div class="variable-item">
                          <strong>Workload<sub>m</sub></strong> = workload of member m calculated
                          from task story points according to assigned RACI roles:
                          Σ<sub>t∈T</sub>(w<sub>role(m,t)</sub> · SP<sub>t</sub>)<br />
                          <span class="text-caption text-grey-7">
                            where w<sub>R</sub>={{ raciWorkloadWeights.responsible }},
                            w<sub>A</sub>={{ raciWorkloadWeights.accountable }},
                            w<sub>C</sub>={{ raciWorkloadWeights.consulted }},
                            w<sub>I</sub>={{ raciWorkloadWeights.informed }}
                          </span>
                        </div>
                        <div class="variable-item">
                          <strong>Capacity<sub>m</sub> = {{ maxStoryPointsPerPerson }}</strong> =
                          maximum weighted story points per person per sprint
                        </div>
                        <div class="variable-item">
                          <strong>Utilization<sub>m</sub></strong> = capacity utilization of member m:
                          (Workload<sub>m</sub> / Capacity<sub>m</sub>) × 100%
                        </div>
                        <div class="variable-item">
                          <strong>L<sub>X,t</sub></strong> = overload factor for role
                          X ∈ {R, A, C, I} for task t<br />
                          <span class="text-caption text-grey-7">
                            For a role with one member:
                            max(0, Utilization<sub>x</sub> - 1.0)<br />
                            For a role with multiple members:
                            (1 / |X<sub>t</sub>|) Σ<sub>x∈X<sub>t</sub></sub> max(0,
                            Utilization<sub>x</sub> - 1.0)
                          </span>
                        </div>
                        <div class="variable-item">
                          <strong>T<sub>adjusted,t</sub></strong> = final adjusted duration for task
                          t after applying RACI overload correction
                        </div>
                      </div>
                    </div>

                    <div class="formula-section">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm text-orange-8">
                        ⚠️ Important Rules
                      </div>
                      <div class="variables-list">
                        <div class="variable-item">
                          <strong>1.</strong> Duration increases ONLY when a RACI role is overloaded
                          (weighted
                          SP > {{ maxStoryPointsPerPerson }})
                        </div>
                        <div class="variable-item">
                          <strong>2.</strong> The formula uses only EXCESS overload (above 100%
                          capacity)
                        </div>
                        <div class="variable-item">
                          <strong>3.</strong> If weighted SP = 21.4, overload = 21.4/20 = 1.07,
                          excess = 1.07 - 1.0 = 0.07 (7% duration increase)
                        </div>
                        <div class="variable-item">
                          <strong>4.</strong> If weighted SP = 15, overload = 15/20 = 0.75, excess =
                          0 (no impact on duration)
                        </div>
                      </div>
                    </div>
                  </div>
                </q-expansion-item>
              </div>
            </q-expansion-item>
          </q-card>
        </div>

        <!-- Tasks Table with Tab Navigation -->
        <div>
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Project Tasks</div>

              <!-- Tab Navigation -->
              <q-tabs v-model="activeTab" class="text-primary q-mt-md" dense align="left">
                <q-tab name="active" icon="play_arrow" label="Aktívny Šprit" />
                <q-tab name="planned" icon="event_available" label="Plánovaný Šprit" />
                <q-tab name="past" icon="history" label="Minulé Šprinty" />
                <q-tab name="future" icon="schedule" label="Budúce Tasky" />
              </q-tabs>
            </q-card-section>

            <q-separator />

            <!-- Tab Panels -->
            <q-tab-panels v-model="activeTab" animated>
              <!-- ACTIVE SPRINT TAB -->
              <q-tab-panel name="active" class="q-pa-none">
                <!-- RACI Weighted Workload for Active Sprint -->
                <q-card flat bordered class="q-mb-lg">
                  <q-card-section>
                    <div class="text-h6 text-weight-bold q-mb-md">
                      RACI Weighted Workload (Aktívny Šprit naprieč projektami)
                    </div>
                    <div class="text-caption text-grey-7 q-mb-md">
                      Work-share weights: R={{ raciWorkloadWeights.responsible }}, A={{
                        raciWorkloadWeights.accountable
                      }}, C={{ raciWorkloadWeights.consulted }}, I={{
                        raciWorkloadWeights.informed
                      }}
                    </div>

                    <div v-if="raciWeightedWorkload.length > 0" class="q-gutter-md">
                      <q-expansion-item
                        v-for="member in raciWeightedWorkload"
                        :key="member.memberId"
                        expand-separator
                        :label="member.memberName"
                        :caption="`${member.weightedSP} SP (${member.workload}%)`"
                        header-class="bg-grey-2"
                      >
                        <template v-slot:header>
                          <div class="row items-center full-width">
                            <div class="col-2 text-weight-medium">
                              {{ member.memberName }}
                            </div>
                            <div class="col-8">
                              <q-linear-progress
                                :value="member.workload / 100"
                                :color="
                                  member.workload > 100
                                    ? 'negative'
                                    : member.workload > 80
                                      ? 'warning'
                                      : 'positive'
                                "
                                size="25px"
                                rounded
                              >
                                <div class="absolute-full flex flex-center">
                                  <q-badge
                                    :color="
                                      member.workload > 100
                                        ? 'negative'
                                        : member.workload > 80
                                          ? 'warning'
                                          : 'positive'
                                    "
                                    text-color="white"
                                    :label="`${member.weightedSP} SP`"
                                  />
                                </div>
                              </q-linear-progress>
                            </div>
                            <div class="col-2 text-right text-weight-bold">
                              {{ member.workload }}%
                            </div>
                          </div>
                        </template>

                        <!-- Task Details -->
                        <q-card flat bordered class="q-ma-sm">
                          <q-card-section>
                            <div class="text-subtitle2 text-weight-bold q-mb-md">
                              Tasky v aktívnych šprintoch naprieč projektami:
                            </div>
                            <q-list separator>
                              <q-item
                                v-for="task in getMemberActiveSprintTasks(member.memberId)"
                                :key="`${task.projectName}-${task.taskId}`"
                                dense
                              >
                                <q-item-section>
                                  <q-item-label>
                                    <strong>{{ task.taskName }}</strong>
                                  </q-item-label>
                                  <q-item-label caption>
                                    {{ task.projectName }} - {{ task.sprintName }}
                                  </q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                  <q-badge color="primary" :label="`${task.storyPoints} SP`" />
                                </q-item-section>
                                <q-item-section side>
                                  <div class="row q-gutter-xs">
                                    <q-badge
                                      v-if="task.roles.includes('R')"
                                      color="negative"
                                      label="R"
                                    />
                                    <q-badge
                                      v-if="task.roles.includes('A')"
                                      color="warning"
                                      label="A"
                                    />
                                    <q-badge
                                      v-if="task.roles.includes('C')"
                                      color="info"
                                      label="C"
                                    />
                                    <q-badge
                                      v-if="task.roles.includes('I')"
                                      color="grey"
                                      label="I"
                                    />
                                  </div>
                                </q-item-section>
                              </q-item>
                            </q-list>
                            <div
                              v-if="getMemberActiveSprintTasks(member.memberId).length === 0"
                              class="text-center text-grey-6 q-pa-md"
                            >
                              Žiadne tasky v aktívnych šprintoch
                            </div>
                          </q-card-section>
                        </q-card>
                      </q-expansion-item>
                    </div>

                    <div v-else class="text-center text-grey-7 q-pa-md">
                      Žiadni členovia v projekte
                    </div>

                    <div
                      v-if="raciWeightedWorkload.length > 0"
                      class="text-caption text-grey-6 q-mt-md"
                    >
                      Kapacita: {{ maxStoryPointsPerPerson }} SP na člena
                      <br />
                      <span class="text-grey-5"
                        >Poznámka: Všetky hodnoty sú zaokrúhlené na celé čísla</span
                      >
                    </div>
                  </q-card-section>

                  <q-separator v-if="activeSprintTasks.length > 0" />
                </q-card>

                <!-- Summary for Active Sprint -->
                <q-card-section v-if="activeSprintTasks.length > 0">
                  <div class="row q-gutter-md">
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div class="text-h6 text-weight-bold text-primary">
                            {{ activeSprintSummary.taskCount }}
                          </div>
                          <div class="text-caption text-grey-7">Tasks</div>
                        </q-card-section>
                      </q-card>
                    </div>
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div
                            class="text-h6 text-weight-bold"
                            :class="
                              activeSprintSummary.durationIncrease > 20
                                ? 'text-negative'
                                : activeSprintSummary.durationIncrease > 10
                                  ? 'text-warning'
                                  : 'text-positive'
                            "
                          >
                            {{ activeSprintSummary.durationIncrease > 0 ? '+' : ''
                            }}{{ activeSprintSummary.durationIncrease.toFixed(1) }}%
                          </div>
                          <div class="text-caption text-grey-7">Average Task Increase</div>
                          <q-tooltip max-width="300px">
                            Priemerný percentuálny nárast duration taskov v sprinte kvôli RACI
                            overhead. Počíta sa ako (Σ Adjusted - Σ PERT) / Σ PERT × 100%
                          </q-tooltip>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>
                </q-card-section>

                <q-card-section v-else class="text-center text-grey-7">
                  <q-icon name="info" size="48px" class="q-mb-md" />
                  <div>Žiadny aktívny šprit alebo tasky v aktívnom šprinte</div>
                </q-card-section>

                <!-- Table for Active Sprint -->
                <q-table
                  v-if="activeSprintTasks.length > 0"
                  :rows="
                    activeSprintTasks.map((task) => ({
                      ...task,
                      raciRoles: [
                        { type: 'R', members: task.raciMembers.responsible },
                        {
                          type: 'A',
                          members:
                            task.raciMembers.accountable !== null
                              ? [task.raciMembers.accountable]
                              : [],
                        },
                        { type: 'C', members: task.raciMembers.consulted },
                        { type: 'I', members: task.raciMembers.informed },
                      ].filter((role) => role.members.length > 0),
                    }))
                  "
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
                      <q-td>{{ props.row.optimistic || 0 }}</q-td>
                      <q-td>{{ props.row.mostLikely || 0 }}</q-td>
                      <q-td>{{ props.row.pessimistic || 0 }}</q-td>
                      <q-td>
                        <div class="text-weight-medium">
                          {{ props.row.pertDuration.toFixed(2) }}d
                        </div>
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
                    </q-tr>

                    <!-- Expanded content -->
                    <q-tr v-if="expandedRows.includes(props.row.id.toString())" :props="props">
                      <q-td colspan="9" class="q-pa-none">
                        <q-card class="q-ma-sm">
                          <q-card-section>
                            <div class="text-h6 text-weight-bold q-mb-md">
                              RACI Team Members Details
                            </div>

                            <div class="column q-gutter-md">
                              <!-- Responsible Members -->
                              <div v-if="props.row.raciMembers.responsible.length > 0">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-red">
                                  Responsible (R)
                                </div>
                                <div
                                  v-for="memberId in props.row.raciMembers.responsible"
                                  :key="`R-${memberId}`"
                                  class="q-mb-sm"
                                >
                                  <q-card class="member-detail-card" bordered flat>
                                    <q-card-section class="q-pa-md">
                                      <div class="row items-center">
                                        <q-avatar
                                          size="32px"
                                          class="q-mr-md"
                                          color="red"
                                          text-color="white"
                                        >
                                          <q-icon name="person" />
                                        </q-avatar>
                                        <div class="col">
                                          <div class="text-h6 text-weight-bold">
                                            {{ getMemberName(memberId) }}
                                          </div>
                                          <div class="text-caption text-grey-6">
                                            ID: {{ memberId }}
                                          </div>
                                        </div>
                                      </div>

                                      <div class="col-12">
                                        <div class="text-caption text-grey-7">
                                          Aktívne projekty:
                                        </div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveProjects(memberId).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>
                                      <div class="col-12 q-mt-sm">
                                        <div class="text-caption text-grey-7">Aktívne šprinty:</div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveSprints(memberId).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>

                                      <!-- Expand/Collapse Tasks Button -->
                                      <q-separator class="q-my-sm" />
                                      <q-btn
                                        flat
                                        dense
                                        no-caps
                                        :label="
                                          getMemberExpanded(memberId)
                                            ? 'Skryť tasky'
                                            : 'Zobraziť tasky v tomto projekte'
                                        "
                                        :icon="
                                          getMemberExpanded(memberId)
                                            ? 'expand_less'
                                            : 'expand_more'
                                        "
                                        @click="toggleMemberExpansion(memberId)"
                                        class="full-width"
                                        color="primary"
                                      />

                                      <!-- Member's tasks -->
                                      <div v-if="getMemberExpanded(memberId)" class="q-mt-sm">
                                        <div class="row q-gutter-xs">
                                          <q-chip
                                            v-for="task in getMemberTasks(memberId)"
                                            :key="task.id"
                                            :color="getTaskRoleColor(task.id, memberId)"
                                            text-color="white"
                                            size="sm"
                                            :label="`${task.name} (${task.storyPoints}SP)`"
                                          />
                                        </div>
                                        <div
                                          v-if="getMemberTasks(memberId).length === 0"
                                          class="text-caption text-grey-6 text-center q-pa-sm"
                                        >
                                          Žiadne tasky v aktívnom šprinte
                                        </div>
                                      </div>
                                    </q-card-section>
                                  </q-card>
                                </div>
                              </div>

                              <!-- Accountable Members -->
                              <div v-if="props.row.raciMembers.accountable !== null">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-blue">
                                  Accountable (A)
                                </div>
                                <q-card class="member-detail-card" bordered flat>
                                  <q-card-section class="q-pa-md">
                                    <div class="row items-center">
                                      <q-avatar
                                        size="32px"
                                        class="q-mr-md"
                                        color="blue"
                                        text-color="white"
                                      >
                                        <q-icon name="person" />
                                      </q-avatar>
                                      <div class="col">
                                        <div class="text-h6 text-weight-bold">
                                          {{ getMemberName(props.row.raciMembers.accountable) }}
                                        </div>
                                        <div class="text-caption text-grey-6">
                                          ID: {{ props.row.raciMembers.accountable }}
                                        </div>
                                      </div>
                                    </div>

                                    <div class="col-12">
                                      <div class="text-caption text-grey-7">Aktívne projekty:</div>
                                      <div class="text-body2" style="word-break: break-word">
                                        {{
                                          getMemberActiveProjects(
                                            props.row.raciMembers.accountable,
                                          ).join(', ') || 'Žiadne'
                                        }}
                                      </div>
                                    </div>
                                    <div class="col-12 q-mt-sm">
                                      <div class="text-caption text-grey-7">Aktívne šprinty:</div>
                                      <div class="text-body2" style="word-break: break-word">
                                        {{
                                          getMemberActiveSprints(
                                            props.row.raciMembers.accountable,
                                          ).join(', ') || 'Žiadne'
                                        }}
                                      </div>
                                    </div>

                                    <!-- Expand/Collapse Tasks Button -->
                                    <q-separator class="q-my-sm" />
                                    <q-btn
                                      flat
                                      dense
                                      no-caps
                                      :label="
                                        getMemberExpanded(props.row.raciMembers.accountable)
                                          ? 'Skryť tasky'
                                          : 'Zobraziť tasky v tomto projekte'
                                      "
                                      :icon="
                                        getMemberExpanded(props.row.raciMembers.accountable)
                                          ? 'expand_less'
                                          : 'expand_more'
                                      "
                                      @click="
                                        toggleMemberExpansion(props.row.raciMembers.accountable)
                                      "
                                      class="full-width"
                                      color="primary"
                                    />

                                    <!-- Member's tasks -->
                                    <div
                                      v-if="getMemberExpanded(props.row.raciMembers.accountable)"
                                      class="q-mt-sm"
                                    >
                                      <div class="row q-gutter-xs">
                                        <q-chip
                                          v-for="task in getMemberTasks(
                                            props.row.raciMembers.accountable,
                                          )"
                                          :key="task.id"
                                          :color="
                                            getTaskRoleColor(
                                              task.id,
                                              props.row.raciMembers.accountable,
                                            )
                                          "
                                          text-color="white"
                                          size="sm"
                                          :label="`${task.name} (${task.storyPoints}SP)`"
                                        />
                                      </div>
                                      <div
                                        v-if="
                                          getMemberTasks(props.row.raciMembers.accountable)
                                            .length === 0
                                        "
                                        class="text-caption text-grey-6 text-center q-pa-sm"
                                      >
                                        Žiadne tasky v aktívnom šprinte
                                      </div>
                                    </div>
                                  </q-card-section>
                                </q-card>
                              </div>

                              <!-- Consulted Members -->
                              <div v-if="props.row.raciMembers.consulted.length > 0">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-orange">
                                  Consulted (C)
                                </div>
                                <div
                                  v-for="memberId in props.row.raciMembers.consulted"
                                  :key="`C-${memberId}`"
                                  class="q-mb-sm"
                                >
                                  <q-card class="member-detail-card" bordered flat>
                                    <q-card-section class="q-pa-md">
                                      <div class="row items-center">
                                        <q-avatar
                                          size="32px"
                                          class="q-mr-md"
                                          color="orange"
                                          text-color="white"
                                        >
                                          <q-icon name="person" />
                                        </q-avatar>
                                        <div class="col">
                                          <div class="text-h6 text-weight-bold">
                                            {{ getMemberName(memberId) }}
                                          </div>
                                          <div class="text-caption text-grey-6">
                                            ID: {{ memberId }}
                                          </div>
                                        </div>
                                      </div>

                                      <div class="col-12">
                                        <div class="text-caption text-grey-7">
                                          Aktívne projekty:
                                        </div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveProjects(memberId).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>
                                      <div class="col-12 q-mt-sm">
                                        <div class="text-caption text-grey-7">Aktívne šprinty:</div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveSprints(memberId).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>

                                      <!-- Expand/Collapse Tasks Button -->
                                      <q-separator class="q-my-sm" />
                                      <q-btn
                                        flat
                                        dense
                                        no-caps
                                        :label="
                                          getMemberExpanded(memberId)
                                            ? 'Skryť tasky'
                                            : 'Zobraziť tasky v tomto projekte'
                                        "
                                        :icon="
                                          getMemberExpanded(memberId)
                                            ? 'expand_less'
                                            : 'expand_more'
                                        "
                                        @click="toggleMemberExpansion(memberId)"
                                        class="full-width"
                                        color="primary"
                                      />

                                      <!-- Member's tasks -->
                                      <div v-if="getMemberExpanded(memberId)" class="q-mt-sm">
                                        <div class="row q-gutter-xs">
                                          <q-chip
                                            v-for="task in getMemberTasks(memberId)"
                                            :key="task.id"
                                            :color="getTaskRoleColor(task.id, memberId)"
                                            text-color="white"
                                            size="sm"
                                            :label="`${task.name} (${task.storyPoints}SP)`"
                                          />
                                        </div>
                                        <div
                                          v-if="getMemberTasks(memberId).length === 0"
                                          class="text-caption text-grey-6 text-center q-pa-sm"
                                        >
                                          Žiadne tasky v aktívnom šprinte
                                        </div>
                                      </div>
                                    </q-card-section>
                                  </q-card>
                                </div>
                              </div>

                              <!-- Informed Members -->
                              <div v-if="props.row.raciMembers.informed.length > 0">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-green">
                                  Informed (I)
                                </div>
                                <div
                                  v-for="memberId in props.row.raciMembers.informed"
                                  :key="`I-${memberId}`"
                                  class="q-mb-sm"
                                >
                                  <q-card class="member-detail-card" bordered flat>
                                    <q-card-section class="q-pa-md">
                                      <div class="row items-center">
                                        <q-avatar
                                          size="32px"
                                          class="q-mr-md"
                                          color="green"
                                          text-color="white"
                                        >
                                          <q-icon name="person" />
                                        </q-avatar>
                                        <div class="col">
                                          <div class="text-h6 text-weight-bold">
                                            {{ getMemberName(memberId) }}
                                          </div>
                                          <div class="text-caption text-grey-6">
                                            ID: {{ memberId }}
                                          </div>
                                        </div>
                                      </div>

                                      <div class="col-12">
                                        <div class="text-caption text-grey-7">
                                          Aktívne projekty:
                                        </div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveProjects(memberId).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>
                                      <div class="col-12 q-mt-sm">
                                        <div class="text-caption text-grey-7">Aktívne šprinty:</div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveSprints(memberId).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>

                                      <!-- Expand/Collapse Tasks Button -->
                                      <q-separator class="q-my-sm" />
                                      <q-btn
                                        flat
                                        dense
                                        no-caps
                                        :label="
                                          getMemberExpanded(memberId)
                                            ? 'Skryť tasky'
                                            : 'Zobraziť tasky v tomto projekte'
                                        "
                                        :icon="
                                          getMemberExpanded(memberId)
                                            ? 'expand_less'
                                            : 'expand_more'
                                        "
                                        @click="toggleMemberExpansion(memberId)"
                                        class="full-width"
                                        color="primary"
                                      />

                                      <!-- Member's tasks -->
                                      <div v-if="getMemberExpanded(memberId)" class="q-mt-sm">
                                        <div class="row q-gutter-xs">
                                          <q-chip
                                            v-for="task in getMemberTasks(memberId)"
                                            :key="task.id"
                                            :color="getTaskRoleColor(task.id, memberId)"
                                            text-color="white"
                                            size="sm"
                                            :label="`${task.name} (${task.storyPoints}SP)`"
                                          />
                                        </div>
                                        <div
                                          v-if="getMemberTasks(memberId).length === 0"
                                          class="text-caption text-grey-6 text-center q-pa-sm"
                                        >
                                          Žiadne tasky v aktívnom šprinte
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
              </q-tab-panel>

              <!-- PLANNED SPRINT TAB -->
              <q-tab-panel name="planned" class="q-pa-none">
                <!-- No Planned Sprint Message -->
                <div
                  v-if="!plannedSprint"
                  class="q-pa-xl text-center"
                >
                  <q-icon name="event_available" size="64px" color="grey-5" class="q-mb-md" />
                  <div class="text-h6 text-grey-6 q-mb-sm">No Planned Sprint</div>
                  <div class="text-body2 text-grey-7 q-mb-md">
                    Create a planned sprint in Smart Sprint Planning to preview PERT/RACI analysis
                  </div>
                  <q-btn
                    color="primary"
                    icon="auto_awesome"
                    label="Go to Smart Planning"
                    @click="$router.push('/smart-sprint-planning')"
                    unelevated
                  />
                </div>

                <!-- Planned Sprint Analysis -->
                <div v-else>
                  <!-- Planned Sprint Info Banner -->
                  <q-banner class="bg-blue-1 q-mb-lg">
                    <template v-slot:avatar>
                      <q-icon name="event_available" color="blue" size="32px" />
                    </template>
                    <div class="text-weight-bold text-blue-9">
                      Planned Sprint Preview: "{{ plannedSprint.name }}"
                    </div>
                    <div class="text-body2 q-mt-xs">
                      This is a preview of PERT/RACI analysis. Start the sprint to begin tracking progress.
                    </div>
                  </q-banner>

                  <!-- RACI Weighted Workload for Planned Sprint -->
                  <q-card flat bordered class="q-mb-lg">
                    <q-card-section>
                      <div class="text-h6 text-weight-bold q-mb-md">
                        RACI Weighted Workload (Plánovaný Šprit naprieč projektami)
                      </div>
                      <div class="text-caption text-grey-7 q-mb-md">
                        Work-share weights: R={{ raciWorkloadWeights.responsible }}, A={{
                          raciWorkloadWeights.accountable
                        }}, C={{ raciWorkloadWeights.consulted }}, I={{
                          raciWorkloadWeights.informed
                        }}
                      </div>

                      <div v-if="plannedSprintRaciWorkload.length > 0" class="q-gutter-md">
                        <q-expansion-item
                          v-for="member in plannedSprintRaciWorkload"
                          :key="member.memberId"
                          expand-separator
                          :label="member.memberName"
                          :caption="`${member.weightedSP} SP (${member.workload}%)`"
                          header-class="bg-grey-2"
                        >
                          <template v-slot:header>
                            <div class="row items-center full-width">
                              <div class="col-2 text-weight-medium">
                                {{ member.memberName }}
                              </div>
                              <div class="col-8">
                                <q-linear-progress
                                  :value="member.workload / 100"
                                  :color="
                                    member.workload > 100
                                      ? 'negative'
                                      : member.workload > 80
                                        ? 'warning'
                                        : 'positive'
                                  "
                                  size="25px"
                                  rounded
                                >
                                  <div class="absolute-full flex flex-center">
                                    <q-badge
                                      :color="
                                        member.workload > 100
                                          ? 'negative'
                                          : member.workload > 80
                                            ? 'warning'
                                            : 'positive'
                                      "
                                      text-color="white"
                                      :label="`${member.weightedSP} SP`"
                                    />
                                  </div>
                                </q-linear-progress>
                              </div>
                              <div class="col-2 text-right text-weight-bold">
                                {{ member.workload }}%
                              </div>
                            </div>
                          </template>

                          <q-card>
                            <q-card-section>
                              <div class="text-body2">
                                <div class="text-weight-bold q-mb-sm">Member Details:</div>
                                <div class="q-mb-xs">
                                  <span class="text-grey-7">Weighted Story Points:</span>
                                  <span class="text-weight-medium q-ml-sm"
                                    >{{ member.weightedSP }} SP</span
                                  >
                                </div>
                                <div class="q-mb-xs">
                                  <span class="text-grey-7">Workload:</span>
                                  <span class="text-weight-medium q-ml-sm">{{ member.workload }}%</span>
                                </div>
                                <div class="q-mb-xs">
                                  <span class="text-grey-7">Aktívne projekty:</span>
                                  <span class="q-ml-sm">{{
                                    getMemberActiveProjects(member.memberId).join(', ') || 'Žiadne'
                                  }}</span>
                                </div>
                                <div>
                                  <span class="text-grey-7">Aktívne šprinty:</span>
                                  <span class="q-ml-sm">{{
                                    getMemberActiveSprints(member.memberId).join(', ') || 'Žiadne'
                                  }}</span>
                                </div>
                              </div>
                            </q-card-section>
                          </q-card>
                        </q-expansion-item>
                      </div>

                      <div v-else class="text-center text-grey-7 q-pa-md">
                        <q-icon name="info" size="48px" class="q-mb-md" />
                        <div>Žiadny RACI workload v plánovanom šprinte</div>
                      </div>
                    </q-card-section>
                  </q-card>

                  <!-- Summary Cards for Planned Sprint -->
                  <div v-if="plannedSprintTasks.length > 0" class="row q-gutter-md q-mb-lg">
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div class="text-h6 text-weight-bold text-primary">
                            {{ plannedSprintSummary.taskCount }}
                          </div>
                          <div class="text-caption text-grey-7">Tasks</div>
                        </q-card-section>
                      </q-card>
                    </div>
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div
                            class="text-h6 text-weight-bold"
                            :class="
                              plannedSprintSummary.durationIncrease > 20
                                ? 'text-negative'
                                : plannedSprintSummary.durationIncrease > 10
                                  ? 'text-warning'
                                  : 'text-positive'
                            "
                          >
                            {{ plannedSprintSummary.durationIncrease > 0 ? '+' : ''
                            }}{{ plannedSprintSummary.durationIncrease.toFixed(1) }}%
                          </div>
                          <div class="text-caption text-grey-7">Average Task Increase</div>
                          <q-tooltip max-width="300px">
                            Priemerný percentuálny nárast duration taskov v sprinte kvôli RACI
                            overhead. Počíta sa ako (Σ Adjusted - Σ PERT) / Σ PERT × 100%
                          </q-tooltip>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>

                  <div v-else class="text-center text-grey-7 q-pa-xl">
                    <q-icon name="info" size="48px" class="q-mb-md" />
                    <div>Žiadne tasky v plánovanom šprinte</div>
                  </div>

                  <!-- Table for Planned Sprint -->
                  <q-table
                    v-if="plannedSprintTasks.length > 0"
                    :rows="
                      plannedSprintTasks.map((task) => ({
                        ...task,
                        raciRoles: [
                          { type: 'R', members: task.raciMembers.responsible },
                          {
                            type: 'A',
                            members:
                              task.raciMembers.accountable !== null
                                ? [task.raciMembers.accountable]
                                : [],
                          },
                          { type: 'C', members: task.raciMembers.consulted },
                          { type: 'I', members: task.raciMembers.informed },
                        ].filter((r) => r.members.length > 0),
                      }))
                    "
                    :columns="taskColumns"
                    row-key="id"
                    flat
                    bordered
                    :rows-per-page-options="[10, 20, 50, 0]"
                    class="shadow-2"
                  >
                    <template v-slot:header="props">
                      <q-tr :props="props">
                        <q-th v-for="col in props.cols" :key="col.name" :props="props">
                          {{ col.label }}
                        </q-th>
                      </q-tr>
                    </template>

                    <template v-slot:body="props">
                      <q-tr :props="props">
                        <q-td key="name" :props="props">
                          <div class="text-weight-medium">{{ props.row.name }}</div>
                          <div class="text-caption text-grey-7">{{ props.row.type }}</div>
                        </q-td>

                        <q-td key="pertOptimistic" :props="props">
                          {{ props.row.pertOptimistic }}d
                        </q-td>

                        <q-td key="pertMostLikely" :props="props">
                          {{ props.row.pertMostLikely }}d
                        </q-td>

                        <q-td key="pertPessimistic" :props="props">
                          {{ props.row.pertPessimistic }}d
                        </q-td>

                        <q-td key="pertDuration" :props="props">
                          <q-badge color="primary">{{ props.row.pertDuration.toFixed(1) }}d</q-badge>
                        </q-td>

                        <q-td key="adjustedDuration" :props="props">
                          <q-badge
                            :color="
                              props.row.increase > 50
                                ? 'negative'
                                : props.row.increase > 25
                                  ? 'warning'
                                  : 'positive'
                            "
                          >
                            {{ props.row.adjustedDuration.toFixed(1) }}d
                          </q-badge>
                        </q-td>

                        <q-td key="increase" :props="props">
                          <q-badge
                            :color="
                              props.row.increase > 50
                                ? 'negative'
                                : props.row.increase > 25
                                  ? 'warning'
                                  : 'info'
                            "
                          >
                            {{ props.row.increase > 0 ? '+' : '' }}{{ props.row.increase.toFixed(0) }}%
                          </q-badge>
                        </q-td>

                        <q-td key="cv" :props="props">
                          <q-badge
                            :color="
                              props.row.cv > 0.3 ? 'negative' : props.row.cv > 0.2 ? 'warning' : 'info'
                            "
                          >
                            {{ props.row.cv.toFixed(2) }}
                          </q-badge>
                        </q-td>

                        <q-td key="uncertainty" :props="props">
                          <q-badge
                            :color="
                              props.row.cv > 0.3
                                ? 'negative'
                                : props.row.cv > 0.2
                                  ? 'warning'
                                  : 'positive'
                            "
                          >
                            {{
                              props.row.cv > 0.3 ? 'High' : props.row.cv > 0.2 ? 'Medium' : 'Low'
                            }}
                          </q-badge>
                        </q-td>

                        <q-td key="raci" :props="props">
                          <q-card flat bordered class="q-pa-sm">
                            <div class="row q-gutter-xs items-center">
                              <template v-for="role in props.row.raciRoles" :key="role.type">
                                <q-badge
                                  :color="
                                    role.type === 'R'
                                      ? 'negative'
                                      : role.type === 'A'
                                        ? 'warning'
                                        : role.type === 'C'
                                          ? 'info'
                                          : 'grey'
                                  "
                                  :label="role.type"
                                />
                                <span class="text-caption">{{ role.members.length }}</span>
                              </template>
                            </div>
                          </q-card>
                        </q-td>
                      </q-tr>
                    </template>
                  </q-table>
                </div>
              </q-tab-panel>

              <!-- PAST SPRINTS TAB -->
              <q-tab-panel name="past" class="q-pa-none">
                <div v-if="pastSprintsTasks.length === 0" class="q-pa-lg text-center text-grey-7">
                  <q-icon name="info" size="48px" class="q-mb-md" />
                  <div>Žiadne dokončené šprinty</div>
                </div>

                <div v-else>
                  <!-- Average RACI Weighted Workload from all completed sprints -->
                  <q-card flat bordered class="q-mb-lg">
                    <q-card-section>
                      <div class="text-h6 text-weight-bold q-mb-md">
                        Priemerné RACI Weighted Workload
                      </div>
                      <div class="text-caption text-grey-7 q-mb-md">
                        Work-share weights: R={{ raciWorkloadWeights.responsible }}, A={{
                          raciWorkloadWeights.accountable
                        }}, C={{ raciWorkloadWeights.consulted }}, I={{
                          raciWorkloadWeights.informed
                        }}
                      </div>

                      <q-banner
                        v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0"
                        class="bg-info text-white q-mb-lg"
                      >
                        <template v-slot:avatar>
                          <q-icon name="info" color="white" />
                        </template>
                        Priemer vypočítaný z ukončených šprintov tohto projektu a zahŕňa celé RACI
                        zaťaženie (R+A+C+I) naprieč projektami. Celkovo
                        {{ completedSprintsInCurrentProject }}
                        {{
                          completedSprintsInCurrentProject === 1
                            ? 'ukončený šprit'
                            : completedSprintsInCurrentProject < 5
                              ? 'ukončené šprinty'
                              : 'ukončených šprintov'
                        }}
                        v tomto projekte.
                      </q-banner>

                      <div
                        v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0"
                        class="q-gutter-md"
                      >
                        <div
                          v-for="member in averageRaciWeightedWorkloadInCurrentProject"
                          :key="member.memberId"
                          class="row items-center"
                        >
                          <div class="col-2 text-weight-medium cursor-pointer">
                            {{ member.memberName }}
                            <q-tooltip
                              anchor="center right"
                              self="center left"
                              :offset="[10, 10]"
                              max-width="400px"
                            >
                              <div class="text-body2">
                                <div class="text-weight-bold q-mb-sm">
                                  Priemer z {{ member.sprintCount }} šprintov:
                                </div>
                                <div
                                  v-for="(sprint, idx) in member.sprintDetails"
                                  :key="idx"
                                  class="q-mb-xs"
                                >
                                  <div class="text-weight-medium">{{ sprint.projectName }}</div>
                                  <div class="text-caption">
                                    {{ sprint.sprintName }}: {{ Math.round(sprint.workload) }} SP
                                  </div>
                                </div>
                                <div
                                  class="q-mt-sm q-pt-sm"
                                  style="border-top: 1px solid rgba(255, 255, 255, 0.3)"
                                >
                                  <strong>Celkom:</strong>
                                  {{
                                    Math.round(
                                      member.sprintDetails.reduce((sum, s) => sum + s.workload, 0),
                                    )
                                  }}
                                  SP
                                  <br />
                                  <strong>Priemer:</strong> {{ member.weightedSP }} SP ({{
                                    member.workload
                                  }}%)
                                </div>
                              </div>
                            </q-tooltip>
                          </div>
                          <div class="col-8">
                            <q-linear-progress
                              :value="member.workload / 100"
                              :color="
                                member.workload > 100
                                  ? 'negative'
                                  : member.workload > 80
                                    ? 'warning'
                                    : 'positive'
                              "
                              size="25px"
                              rounded
                            >
                              <div class="absolute-full flex flex-center">
                                <q-badge
                                  :color="
                                    member.workload > 100
                                      ? 'negative'
                                      : member.workload > 80
                                        ? 'warning'
                                        : 'positive'
                                  "
                                  text-color="white"
                                  :label="`${member.weightedSP} SP`"
                                />
                              </div>
                            </q-linear-progress>
                          </div>
                          <div class="col-2 text-right text-weight-bold">
                            {{ member.workload }}%
                          </div>
                        </div>
                      </div>
                      <div
                        v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0"
                        class="text-caption text-grey-6 q-mt-md"
                      >
                        Kapacita: {{ maxStoryPointsPerPerson }} SP na člena
                        <br />
                        <span class="text-grey-5"
                          >Poznámka: Všetky hodnoty sú zaokrúhlené na celé čísla</span
                        >
                      </div>

                      <div v-else class="text-center text-grey-7 q-pa-md">
                        Žiadne dáta o workload v ukončených šprintoch
                      </div>
                    </q-card-section>

                    <q-separator v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0" />
                  </q-card>
                  <!-- Loop through each past sprint -->
                  <div
                    v-for="(sprintGroup, index) in pastSprintsTasks"
                    :key="sprintGroup.sprint.id"
                    class="q-mb-md"
                  >
                    <q-card-section>
                      <div class="text-h6 text-weight-bold q-mb-sm">
                        {{ sprintGroup.sprint.name }}
                        <q-chip size="sm" color="grey" text-color="white" class="q-ml-sm">
                          Completed
                        </q-chip>
                      </div>

                      <!-- Summary for this sprint -->
                      <div class="row q-gutter-md q-mb-md" v-if="pastSprintsSummary[index]">
                        <div class="col">
                          <q-card flat bordered>
                            <q-card-section class="text-center">
                              <div class="text-h6 text-weight-bold text-primary">
                                {{ pastSprintsSummary[index]?.taskCount || 0 }}
                              </div>
                              <div class="text-caption text-grey-7">Tasks</div>
                            </q-card-section>
                          </q-card>
                        </div>
                        <div class="col">
                          <q-card flat bordered>
                            <q-card-section class="text-center">
                              <div
                                class="text-h6 text-weight-bold"
                                :class="
                                  (pastSprintsSummary[index]?.durationIncrease || 0) > 20
                                    ? 'text-negative'
                                    : (pastSprintsSummary[index]?.durationIncrease || 0) > 10
                                      ? 'text-warning'
                                      : 'text-positive'
                                "
                              >
                                {{
                                  (pastSprintsSummary[index]?.durationIncrease || 0) > 0 ? '+' : ''
                                }}{{
                                  (pastSprintsSummary[index]?.durationIncrease || 0).toFixed(1)
                                }}%
                              </div>
                              <div class="text-caption text-grey-7">Average Task Increase</div>
                              <q-tooltip max-width="300px">
                                Priemerný percentuálny nárast duration taskov v sprinte kvôli RACI
                                overhead. Počíta sa ako (Σ Adjusted - Σ PERT) / Σ PERT × 100%
                              </q-tooltip>
                            </q-card-section>
                          </q-card>
                        </div>
                      </div>

                      <!-- RACI Weighted Workload for this specific sprint -->
                      <q-card-section>
                        <div class="text-subtitle1 text-weight-bold q-mb-md">
                          RACI Weighted Workload (Tento Šprit naprieč projektami)
                        </div>
                        <div class="text-caption text-grey-7 q-mb-md">
                          Work-share weights: R={{ raciWorkloadWeights.responsible }}, A={{
                            raciWorkloadWeights.accountable
                          }}, C={{ raciWorkloadWeights.consulted }}, I={{
                            raciWorkloadWeights.informed
                          }}
                        </div>

                        <div
                          v-if="getSprintRaciWeightedWorkload(sprintGroup.sprint.id).length > 0"
                          class="q-gutter-md"
                        >
                          <div
                            v-for="member in getSprintRaciWeightedWorkload(sprintGroup.sprint.id)"
                            :key="member.memberId"
                            class="row items-center"
                          >
                            <div class="col-2 text-weight-medium">
                              {{ member.memberName }}
                            </div>
                            <div class="col-8">
                              <q-linear-progress
                                :value="member.workload / 100"
                                :color="
                                  member.workload > 100
                                    ? 'negative'
                                    : member.workload > 80
                                      ? 'warning'
                                      : 'positive'
                                "
                                size="25px"
                                rounded
                              >
                                <div class="absolute-full flex flex-center">
                                  <q-badge
                                    :color="
                                      member.workload > 100
                                        ? 'negative'
                                        : member.workload > 80
                                          ? 'warning'
                                          : 'positive'
                                    "
                                    text-color="white"
                                    :label="`${member.weightedSP} SP`"
                                  />
                                </div>
                              </q-linear-progress>
                            </div>
                            <div class="col-2 text-right text-weight-bold">
                              {{ member.workload }}%
                            </div>
                          </div>
                        </div>
                        <div
                          v-if="getSprintRaciWeightedWorkload(sprintGroup.sprint.id).length > 0"
                          class="text-caption text-grey-6 q-mt-md"
                        >
                          Kapacita: {{ maxStoryPointsPerPerson }} SP na člena
                          <br />
                          <span class="text-grey-5"
                            >Poznámka: Všetky hodnoty sú zaokrúhlené na celé čísla</span
                          >
                        </div>

                        <div v-else class="text-center text-grey-7 q-pa-md">
                          Žiadne dáta o workload v tomto šprinte
                        </div>
                      </q-card-section>

                      <q-separator
                        v-if="getSprintRaciWeightedWorkload(sprintGroup.sprint.id).length > 0"
                      />
                    </q-card-section>

                    <!-- Table for this sprint's tasks -->
                    <q-table
                      :rows="
                        sprintGroup.tasks.map((task) => ({
                          ...task,
                          sprintId: sprintGroup.sprint.id,
                          raciRoles: [
                            { type: 'R', members: task.raciMembers.responsible },
                            {
                              type: 'A',
                              members:
                                task.raciMembers.accountable !== null
                                  ? [task.raciMembers.accountable]
                                  : [],
                            },
                            { type: 'C', members: task.raciMembers.consulted },
                            { type: 'I', members: task.raciMembers.informed },
                          ].filter((role) => role.members.length > 0),
                        }))
                      "
                      :columns="taskColumns"
                      row-key="id"
                      :pagination="{ rowsPerPage: 5 }"
                      class="tasks-table"
                      flat
                      bordered
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
                            <div class="text-weight-medium">
                              {{ props.row.pertDuration.toFixed(2) }}d
                            </div>
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
                        </q-tr>

                        <!-- Expanded content -->
                        <q-tr v-if="expandedRows.includes(props.row.id.toString())" :props="props">
                          <q-td colspan="9" class="q-pa-none">
                            <q-card class="q-ma-sm">
                              <q-card-section>
                                <div class="text-h6 text-weight-bold q-mb-md">
                                  RACI Team Members Details
                                </div>

                                <div class="column q-gutter-md">
                                  <!-- Responsible Members -->
                                  <div v-if="props.row.raciMembers.responsible.length > 0">
                                    <div class="text-subtitle2 text-weight-medium q-mb-sm text-red">
                                      Responsible (R)
                                    </div>
                                    <div
                                      v-for="memberId in props.row.raciMembers.responsible"
                                      :key="`R-${memberId}`"
                                      class="q-mb-sm"
                                    >
                                      <q-card class="member-detail-card" bordered flat>
                                        <q-card-section class="q-pa-md">
                                          <div class="row items-center">
                                            <q-avatar
                                              size="32px"
                                              class="q-mr-md"
                                              color="red"
                                              text-color="white"
                                            >
                                              <q-icon name="person" />
                                            </q-avatar>
                                            <div class="col">
                                              <div class="text-h6 text-weight-bold">
                                                {{ getMemberName(memberId) }}
                                              </div>
                                              <div class="text-caption text-grey-6">
                                                ID: {{ memberId }}
                                              </div>
                                            </div>
                                          </div>

                                          <div class="col-12">
                                            <div class="text-caption text-grey-7">
                                              Aktívne projekty:
                                            </div>
                                            <div class="text-body2" style="word-break: break-word">
                                              {{
                                                getMemberActiveProjects(memberId).join(', ') ||
                                                'Žiadne'
                                              }}
                                            </div>
                                          </div>
                                          <div class="col-12 q-mt-sm">
                                            <div class="text-caption text-grey-7">
                                              Aktívne šprinty:
                                            </div>
                                            <div class="text-body2" style="word-break: break-word">
                                              {{
                                                getMemberActiveSprints(memberId).join(', ') ||
                                                'Žiadne'
                                              }}
                                            </div>
                                          </div>
                                        </q-card-section>
                                      </q-card>
                                    </div>
                                  </div>

                                  <!-- Accountable Members -->
                                  <div v-if="props.row.raciMembers.accountable !== null">
                                    <div
                                      class="text-subtitle2 text-weight-medium q-mb-sm text-blue"
                                    >
                                      Accountable (A)
                                    </div>
                                    <q-card class="member-detail-card" bordered flat>
                                      <q-card-section class="q-pa-md">
                                        <div class="row items-center">
                                          <q-avatar
                                            size="32px"
                                            class="q-mr-md"
                                            color="blue"
                                            text-color="white"
                                          >
                                            <q-icon name="person" />
                                          </q-avatar>
                                          <div class="col">
                                            <div class="text-h6 text-weight-bold">
                                              {{ getMemberName(props.row.raciMembers.accountable) }}
                                            </div>
                                            <div class="text-caption text-grey-6">
                                              ID: {{ props.row.raciMembers.accountable }}
                                            </div>
                                          </div>
                                        </div>

                                        <div class="col-12">
                                          <div class="text-caption text-grey-7">
                                            Aktívne projekty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveProjects(
                                                props.row.raciMembers.accountable,
                                              ).join(', ') || 'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                        <div class="col-12 q-mt-sm">
                                          <div class="text-caption text-grey-7">
                                            Aktívne šprinty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveSprints(
                                                props.row.raciMembers.accountable,
                                              ).join(', ') || 'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                      </q-card-section>
                                    </q-card>
                                  </div>

                                  <!-- Consulted Members -->
                                  <div v-if="props.row.raciMembers.consulted.length > 0">
                                    <div
                                      class="text-subtitle2 text-weight-medium q-mb-sm text-orange"
                                    >
                                      Consulted (C)
                                    </div>
                                    <div
                                      v-for="memberId in props.row.raciMembers.consulted"
                                      :key="`C-${memberId}`"
                                      class="q-mb-sm"
                                    >
                                      <q-card class="member-detail-card" bordered flat>
                                        <q-card-section class="q-pa-md">
                                          <div class="row items-center">
                                            <q-avatar
                                              size="32px"
                                              class="q-mr-md"
                                              color="orange"
                                              text-color="white"
                                            >
                                              <q-icon name="person" />
                                            </q-avatar>
                                            <div class="col">
                                              <div class="text-h6 text-weight-bold">
                                                {{ getMemberName(memberId) }}
                                              </div>
                                              <div class="text-caption text-grey-6">
                                                ID: {{ memberId }}
                                              </div>
                                            </div>
                                          </div>

                                          <div class="col-12">
                                            <div class="text-caption text-grey-7">
                                              Aktívne projekty:
                                            </div>
                                            <div class="text-body2" style="word-break: break-word">
                                              {{
                                                getMemberActiveProjects(memberId).join(', ') ||
                                                'Žiadne'
                                              }}
                                            </div>
                                          </div>
                                          <div class="col-12 q-mt-sm">
                                            <div class="text-caption text-grey-7">
                                              Aktívne šprinty:
                                            </div>
                                            <div class="text-body2" style="word-break: break-word">
                                              {{
                                                getMemberActiveSprints(memberId).join(', ') ||
                                                'Žiadne'
                                              }}
                                            </div>
                                          </div>
                                        </q-card-section>
                                      </q-card>
                                    </div>
                                  </div>

                                  <!-- Informed Members -->
                                  <div v-if="props.row.raciMembers.informed.length > 0">
                                    <div
                                      class="text-subtitle2 text-weight-medium q-mb-sm text-green"
                                    >
                                      Informed (I)
                                    </div>
                                    <div
                                      v-for="memberId in props.row.raciMembers.informed"
                                      :key="`I-${memberId}`"
                                      class="q-mb-sm"
                                    >
                                      <q-card class="member-detail-card" bordered flat>
                                        <q-card-section class="q-pa-md">
                                          <div class="row items-center">
                                            <q-avatar
                                              size="32px"
                                              class="q-mr-md"
                                              color="green"
                                              text-color="white"
                                            >
                                              <q-icon name="person" />
                                            </q-avatar>
                                            <div class="col">
                                              <div class="text-h6 text-weight-bold">
                                                {{ getMemberName(memberId) }}
                                              </div>
                                              <div class="text-caption text-grey-6">
                                                ID: {{ memberId }}
                                              </div>
                                            </div>
                                          </div>

                                          <div class="col-12">
                                            <div class="text-caption text-grey-7">
                                              Aktívne projekty:
                                            </div>
                                            <div class="text-body2" style="word-break: break-word">
                                              {{
                                                getMemberActiveProjects(memberId).join(', ') ||
                                                'Žiadne'
                                              }}
                                            </div>
                                          </div>
                                          <div class="col-12 q-mt-sm">
                                            <div class="text-caption text-grey-7">
                                              Aktívne šprinty:
                                            </div>
                                            <div class="text-body2" style="word-break: break-word">
                                              {{
                                                getMemberActiveSprints(memberId).join(', ') ||
                                                'Žiadne'
                                              }}
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

                    <q-separator v-if="index < pastSprintsTasks.length - 1" class="q-my-md" />
                  </div>
                </div>
              </q-tab-panel>

              <!-- FUTURE/BACKLOG TAB -->
              <q-tab-panel name="future" class="q-pa-none">
                <!-- RACI Weighted Workload for Future/Backlog tasks -->
                <q-card flat bordered class="q-mb-lg">
                  <q-card-section>
                    <div class="text-h6 text-weight-bold q-mb-md">
                      Priemerné RACI Weighted Workload (Minulé Šprinty v tomto projekte)
                    </div>
                    <div class="text-caption text-grey-7 q-mb-md">
                      Work-share weights: R={{ raciWorkloadWeights.responsible }}, A={{
                        raciWorkloadWeights.accountable
                      }}, C={{ raciWorkloadWeights.consulted }}, I={{
                        raciWorkloadWeights.informed
                      }}
                    </div>

                    <q-banner
                      v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0"
                      class="bg-info text-white q-mb-lg"
                    >
                      <template v-slot:avatar>
                        <q-icon name="info" color="white" />
                      </template>
                      Priemer vypočítaný z ukončených šprintov tohto projektu a zahŕňa celé RACI
                      zaťaženie (R+A+C+I) naprieč projektami. Celkovo
                      {{ completedSprintsInCurrentProject }}
                      {{
                        completedSprintsInCurrentProject === 1
                          ? 'ukončený šprit'
                          : completedSprintsInCurrentProject < 5
                            ? 'ukončené šprinty'
                            : 'ukončených šprintov'
                      }}
                      v tomto projekte.
                    </q-banner>

                    <div
                      v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0"
                      class="q-gutter-md"
                    >
                      <div
                        v-for="member in averageRaciWeightedWorkloadInCurrentProject"
                        :key="member.memberId"
                        class="row items-center"
                      >
                        <div class="col-2 text-weight-medium cursor-pointer">
                          {{ member.memberName }}
                          <q-tooltip v-if="member.sprintCount > 0" max-width="400px">
                            <div class="text-weight-bold q-mb-sm">
                              Detaily z {{ member.sprintCount }}
                              {{
                                member.sprintCount === 1
                                  ? 'šprintu'
                                  : member.sprintCount < 5
                                    ? 'šprintov'
                                    : 'šprintov'
                              }}:
                            </div>
                            <div
                              v-for="(detail, index) in member.sprintDetails"
                              :key="index"
                              class="q-mb-xs"
                            >
                              <span class="text-grey-4">{{ detail.projectName }}</span> -
                              {{ detail.sprintName }}: {{ detail.workload }} SP
                            </div>
                          </q-tooltip>
                        </div>
                        <div class="col-8">
                          <q-linear-progress
                            :value="member.workload / 100"
                            :color="
                              member.workload > 100
                                ? 'negative'
                                : member.workload > 80
                                  ? 'warning'
                                  : 'positive'
                            "
                            size="25px"
                            rounded
                          >
                            <div class="absolute-full flex flex-center">
                              <q-badge
                                :color="
                                  member.workload > 100
                                    ? 'negative'
                                    : member.workload > 80
                                      ? 'warning'
                                      : 'positive'
                                "
                                text-color="white"
                                :label="`${member.weightedSP} SP`"
                              />
                            </div>
                          </q-linear-progress>
                        </div>
                        <div class="col-2 text-right text-weight-bold">{{ member.workload }}%</div>
                      </div>
                    </div>
                    <div
                      v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0"
                      class="text-caption text-grey-6 q-mt-md"
                    >
                      Kapacita: {{ maxStoryPointsPerPerson }} SP na člena
                      <br />
                      <span class="text-grey-5"
                        >Poznámka: Všetky hodnoty sú zaokrúhlené na celé čísla</span
                      >
                    </div>

                    <div v-else class="text-center text-grey-7 q-pa-md">
                      Žiadne dáta o workload v ukončených šprintoch
                    </div>
                  </q-card-section>

                  <q-separator v-if="averageRaciWeightedWorkloadInCurrentProject.length > 0" />
                </q-card>

                <!-- Summary for Future Tasks -->
                <q-card-section v-if="futureBacklogTasks.length > 0">
                  <div class="row q-gutter-md">
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div class="text-h6 text-weight-bold text-primary">
                            {{ futureBacklogSummary.taskCount }}
                          </div>
                          <div class="text-caption text-grey-7">Tasks</div>
                        </q-card-section>
                      </q-card>
                    </div>
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div class="text-h6 text-weight-bold">
                            {{ futureBacklogSummary.totalPertDuration.toFixed(2) }}d
                          </div>
                          <div class="text-caption text-grey-7">PERT Duration</div>
                        </q-card-section>
                      </q-card>
                    </div>
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div class="text-h6 text-weight-bold text-orange">
                            {{ futureBacklogSummary.totalAdjustedDuration.toFixed(2) }}d
                          </div>
                          <div class="text-caption text-grey-7">Adjusted Duration (Estimated)</div>
                        </q-card-section>
                      </q-card>
                    </div>
                    <div class="col">
                      <q-card flat bordered>
                        <q-card-section class="text-center">
                          <div
                            class="text-h6 text-weight-bold"
                            :class="
                              futureBacklogSummary.durationIncrease > 20
                                ? 'text-negative'
                                : futureBacklogSummary.durationIncrease > 10
                                  ? 'text-warning'
                                  : 'text-positive'
                            "
                          >
                            {{ futureBacklogSummary.durationIncrease > 0 ? '+' : ''
                            }}{{ futureBacklogSummary.durationIncrease.toFixed(1) }}%
                          </div>
                          <div class="text-caption text-grey-7">Increase (Estimated)</div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>
                </q-card-section>

                <q-card-section v-else class="text-center text-grey-7">
                  <q-icon name="info" size="48px" class="q-mb-md" />
                  <div>Žiadne budúce alebo backlog tasky</div>
                </q-card-section>

                <!-- Table for Future Tasks -->
                <q-table
                  v-if="futureBacklogTasks.length > 0"
                  :rows="
                    futureBacklogTasks.map((task) => ({
                      ...task,
                      raciRoles: [
                        { type: 'R', members: task.raciMembers.responsible },
                        {
                          type: 'A',
                          members:
                            task.raciMembers.accountable !== null
                              ? [task.raciMembers.accountable]
                              : [],
                        },
                        { type: 'C', members: task.raciMembers.consulted },
                        { type: 'I', members: task.raciMembers.informed },
                      ].filter((role) => role.members.length > 0),
                    }))
                  "
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
                      <q-td>{{ props.row.optimistic || 0 }}</q-td>
                      <q-td>{{ props.row.mostLikely || 0 }}</q-td>
                      <q-td>{{ props.row.pessimistic || 0 }}</q-td>
                      <q-td>
                        <div class="text-weight-medium">
                          {{ props.row.pertDuration.toFixed(2) }}d
                        </div>
                      </q-td>
                      <q-td>
                        <div class="text-weight-bold" :class="getDurationClass(props.row)">
                          {{ props.row.adjustedDuration.toFixed(2) }}d
                        </div>
                        <div class="text-caption text-grey-7">
                          {{ getDurationChange(props.row) }} (Estimated)
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
                    </q-tr>

                    <!-- Expanded content -->
                    <q-tr v-if="expandedRows.includes(props.row.id.toString())" :props="props">
                      <q-td colspan="6" class="q-pa-none">
                        <q-card class="q-ma-sm">
                          <q-card-section>
                            <div class="text-h6 text-weight-bold q-mb-md">
                              RACI Team Members Details (Priemer z minulých šprintov)
                            </div>

                            <q-banner class="bg-info text-white q-mb-md">
                              <template v-slot:avatar>
                                <q-icon name="info" color="white" />
                              </template>
                              Zobrazené hodnoty sú priemery weighted SP z ukončených šprintov, keďže
                              tento task ešte nie je priradený do šprintu.
                            </q-banner>

                            <div class="column q-gutter-md">
                              <!-- Responsible Members -->
                              <div v-if="props.row.raciMembers.responsible.length > 0">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-red">
                                  Responsible (R)
                                </div>
                                <div
                                  v-for="memberId in props.row.raciMembers.responsible"
                                  :key="`R-${memberId}`"
                                  class="q-mb-sm"
                                >
                                  <q-card class="member-detail-card" bordered flat>
                                    <q-card-section class="q-pa-md">
                                      <div class="row items-center">
                                        <q-avatar
                                          size="32px"
                                          class="q-mr-md"
                                          color="red"
                                          text-color="white"
                                        >
                                          <q-icon name="person" />
                                        </q-avatar>
                                        <div class="col">
                                          <div class="text-h6 text-weight-bold">
                                            {{ getMemberName(memberId) }}
                                          </div>
                                          <div class="text-caption text-grey-6">
                                            ID: {{ memberId }}
                                          </div>
                                        </div>
                                      </div>

                                      <q-separator class="q-my-sm" />

                                      <div class="row q-col-gutter-sm">
                                        <div class="col-12">
                                          <div class="text-caption text-grey-7">
                                            Aktívne projekty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveProjects(memberId).join(', ') ||
                                              'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                        <div class="col-12 q-mt-sm">
                                          <div class="text-caption text-grey-7">
                                            Aktívne šprinty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveSprints(memberId).join(', ') ||
                                              'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                      </div>
                                    </q-card-section>
                                  </q-card>
                                </div>
                              </div>

                              <!-- Accountable Members -->
                              <div v-if="props.row.raciMembers.accountable !== null">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-blue">
                                  Accountable (A)
                                </div>
                                <q-card class="member-detail-card" bordered flat>
                                  <q-card-section class="q-pa-md">
                                    <div class="row items-center">
                                      <q-avatar
                                        size="32px"
                                        class="q-mr-md"
                                        color="blue"
                                        text-color="white"
                                      >
                                        <q-icon name="person" />
                                      </q-avatar>
                                      <div class="col">
                                        <div class="text-h6 text-weight-bold">
                                          {{ getMemberName(props.row.raciMembers.accountable) }}
                                        </div>
                                        <div class="text-caption text-grey-6">
                                          ID: {{ props.row.raciMembers.accountable }}
                                        </div>
                                      </div>
                                    </div>

                                    <q-separator class="q-my-sm" />

                                    <div class="row q-col-gutter-sm">
                                      <div class="col-12">
                                        <div class="text-caption text-grey-7">
                                          Aktívne projekty:
                                        </div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveProjects(
                                              props.row.raciMembers.accountable,
                                            ).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>
                                      <div class="col-12 q-mt-sm">
                                        <div class="text-caption text-grey-7">Aktívne šprinty:</div>
                                        <div class="text-body2" style="word-break: break-word">
                                          {{
                                            getMemberActiveSprints(
                                              props.row.raciMembers.accountable,
                                            ).join(', ') || 'Žiadne'
                                          }}
                                        </div>
                                      </div>
                                    </div>
                                  </q-card-section>
                                </q-card>
                              </div>

                              <!-- Consulted Members -->
                              <div v-if="props.row.raciMembers.consulted.length > 0">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-orange">
                                  Consulted (C)
                                </div>
                                <div
                                  v-for="memberId in props.row.raciMembers.consulted"
                                  :key="`C-${memberId}`"
                                  class="q-mb-sm"
                                >
                                  <q-card class="member-detail-card" bordered flat>
                                    <q-card-section class="q-pa-md">
                                      <div class="row items-center">
                                        <q-avatar
                                          size="32px"
                                          class="q-mr-md"
                                          color="orange"
                                          text-color="white"
                                        >
                                          <q-icon name="person" />
                                        </q-avatar>
                                        <div class="col">
                                          <div class="text-h6 text-weight-bold">
                                            {{ getMemberName(memberId) }}
                                          </div>
                                          <div class="text-caption text-grey-6">
                                            ID: {{ memberId }}
                                          </div>
                                        </div>
                                      </div>

                                      <q-separator class="q-my-sm" />

                                      <div class="row q-col-gutter-sm">
                                        <div class="col-12">
                                          <div class="text-caption text-grey-7">
                                            Aktívne projekty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveProjects(memberId).join(', ') ||
                                              'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                        <div class="col-12 q-mt-sm">
                                          <div class="text-caption text-grey-7">
                                            Aktívne šprinty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveSprints(memberId).join(', ') ||
                                              'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                      </div>
                                    </q-card-section>
                                  </q-card>
                                </div>
                              </div>

                              <!-- Informed Members -->
                              <div v-if="props.row.raciMembers.informed.length > 0">
                                <div class="text-subtitle2 text-weight-medium q-mb-sm text-green">
                                  Informed (I)
                                </div>
                                <div
                                  v-for="memberId in props.row.raciMembers.informed"
                                  :key="`I-${memberId}`"
                                  class="q-mb-sm"
                                >
                                  <q-card class="member-detail-card" bordered flat>
                                    <q-card-section class="q-pa-md">
                                      <div class="row items-center">
                                        <q-avatar
                                          size="32px"
                                          class="q-mr-md"
                                          color="green"
                                          text-color="white"
                                        >
                                          <q-icon name="person" />
                                        </q-avatar>
                                        <div class="col">
                                          <div class="text-h6 text-weight-bold">
                                            {{ getMemberName(memberId) }}
                                          </div>
                                          <div class="text-caption text-grey-6">
                                            ID: {{ memberId }}
                                          </div>
                                        </div>
                                      </div>

                                      <q-separator class="q-my-sm" />

                                      <div class="row q-col-gutter-sm">
                                        <div class="col-12">
                                          <div class="text-caption text-grey-7">
                                            Aktívne projekty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveProjects(memberId).join(', ') ||
                                              'Žiadne'
                                            }}
                                          </div>
                                        </div>
                                        <div class="col-12 q-mt-sm">
                                          <div class="text-caption text-grey-7">
                                            Aktívne šprinty:
                                          </div>
                                          <div class="text-body2" style="word-break: break-word">
                                            {{
                                              getMemberActiveSprints(memberId).join(', ') ||
                                              'Žiadne'
                                            }}
                                          </div>
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
              </q-tab-panel>
            </q-tab-panels>
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
import { ref, computed, reactive, onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';
import { raciWeightsApi } from 'src/services/api';
import { useActivityLog } from 'src/composables/useActivityLog';

const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();
const { log } = useActivityLog();

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
  const project = projectStore.projects.find((p) => p.id === selectedProjectId.value);
  if (!project) return null;

  // Filter out Split tasks (they should not be displayed in normal views)
  return {
    ...project,
    tasks: projectStore.filterActiveTasks(project.tasks || []),
  };
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

interface RaciWorkloadWeights {
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
const activeTab = ref('active'); // Tab navigation: 'active', 'past', 'future'

// RACI weights - loaded from database (both duration and workload)
const raciWeights = ref<RaciWeights>({
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
});

const raciWorkloadWeights = ref<RaciWorkloadWeights>({
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
});

// Load RACI weights from database
const loadRaciWeightsFromApi = async () => {
  try {
    const config = await raciWeightsApi.getRaciWeights();

    // Update duration weights (for adjusted duration formula)
    raciWeights.value = {
      responsible: config.duration.responsible,
      accountable: config.duration.accountable,
      consulted: config.duration.consulted,
      informed: config.duration.informed,
    };

    // Update workload weights
    raciWorkloadWeights.value = {
      responsible: config.workload.responsible,
      accountable: config.workload.accountable,
      consulted: config.workload.consulted,
      informed: config.workload.informed,
    };

    console.log('✅ RACI weights loaded from database', config);
  } catch (error) {
    console.error('❌ Failed to load RACI weights from database:', error);
    $q.notify({
      type: 'warning',
      message: 'Nepodarilo sa načítať RACI váhy z databázy, používam predvolené hodnoty',
      position: 'top',
    });
  }
};

// Save RACI weights to database
const saveRaciWeightsToApi = async () => {
  try {
    const updatedConfig = await raciWeightsApi.updateRaciWeights({
      duration: {
        responsible: raciWeights.value.responsible,
        accountable: raciWeights.value.accountable,
        consulted: raciWeights.value.consulted,
        informed: raciWeights.value.informed,
      },
      workload: {
        responsible: raciWorkloadWeights.value.responsible,
        accountable: raciWorkloadWeights.value.accountable,
        consulted: raciWorkloadWeights.value.consulted,
        informed: raciWorkloadWeights.value.informed,
      },
    });

    console.log('✅ RACI weights saved to database', updatedConfig);
    $q.notify({
      type: 'positive',
      message: 'RACI váhy boli úspešne uložené',
      position: 'top',
    });
  } catch (error) {
    console.error('❌ Failed to save RACI weights to database:', error);
    $q.notify({
      type: 'negative',
      message: 'Nepodarilo sa uložiť RACI váhy do databázy',
      position: 'top',
    });
  }
};

// Maximum story points per person (global setting)
const maxStoryPointsPerPerson = ref(
  parseInt(localStorage.getItem('max_story_points_per_person') || '20'),
);

// Team members from store - filtered by selected project
const teamMembers = computed(() => {
  if (!selectedProject.value) return [];
  return teamStore.teamMembers
    .filter((member) => selectedProject.value!.teamMemberIds?.includes(member.id))
    .map((member) => ({
      id: member.id,
      name: member.name,
    }));
});

// Helper function to convert project task to local Task type
function convertToTask(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  task: any,
  sprintId: number | null,
  useAverage: boolean = false,
): Task {
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

  taskObj.adjustedDuration = calculateAdjustedDuration(taskObj, sprintId, useAverage);
  return taskObj;
}

// Get active sprint
const activeSprint = computed(() => {
  if (!selectedProject.value || !selectedProject.value.sprints) return null;
  return selectedProject.value.sprints.find((s) => s.status === 'active') || null;
});

// Get planned sprint
const plannedSprint = computed(() => {
  if (!selectedProject.value || !selectedProject.value.sprints) return null;
  return selectedProject.value.sprints.find((s) => s.status === 'planned') || null;
});

// Computed: Tasks from ACTIVE sprint
const activeSprintTasks = computed<Task[]>(() => {
  if (!selectedProject.value || !selectedProject.value.tasks || !activeSprint.value) return [];

  return selectedProject.value.tasks
    .filter((task) => task.sprintId === activeSprint.value!.id)
    .map((task) => convertToTask(task, activeSprint.value!.id, false));
});

// Computed: Tasks from PLANNED sprint
const plannedSprintTasks = computed<Task[]>(() => {
  if (!selectedProject.value || !selectedProject.value.tasks || !plannedSprint.value) return [];

  return selectedProject.value.tasks
    .filter((task) => task.sprintId === plannedSprint.value!.id)
    .map((task) => convertToTask(task, plannedSprint.value!.id, false));
});

// Computed: Tasks from PAST sprints (grouped by sprint)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const pastSprintsTasks = computed<{ sprint: any; tasks: Task[] }[]>(() => {
  if (!selectedProject.value || !selectedProject.value.tasks || !selectedProject.value.sprints) {
    return [];
  }

  const completedSprints = selectedProject.value.sprints.filter((s) => s.status === 'completed');

  return completedSprints
    .map((sprint) => {
      const sprintTasks = selectedProject
        .value!.tasks.filter((task) => task.sprintId === sprint.id)
        .map((task) => convertToTask(task, sprint.id, false));

      return {
        sprint,
        tasks: sprintTasks,
      };
    })
    .filter((group) => group.tasks.length > 0); // Only show sprints with tasks
});

// Computed: FUTURE/BACKLOG tasks (not in any sprint or in planned sprints)
const futureBacklogTasks = computed<Task[]>(() => {
  if (!selectedProject.value || !selectedProject.value.tasks) return [];

  return selectedProject.value.tasks
    .filter((task) => {
      if (task.sprintId === null) return true; // Backlog tasks

      // Check if task is in a planned sprint
      const sprint = selectedProject.value!.sprints?.find((s) => s.id === task.sprintId);
      return sprint && sprint.status === 'planned';
    })
    .map((task) => convertToTask(task, null, true)); // Use average for future tasks
});

// Computed tasks from selected project (keep for backward compatibility)
const tasks = computed<Task[]>(() => {
  // Return active sprint tasks by default, or all if no active sprint
  return activeSprintTasks.value.length > 0 ? activeSprintTasks.value : futureBacklogTasks.value;
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
    name: 'optimistic',
    label: 'Optimistic',
    field: 'optimistic',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'mostLikely',
    label: 'Most Likely',
    field: 'mostLikely',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'pessimistic',
    label: 'Pessimistic',
    field: 'pessimistic',
    align: 'center' as const,
    sortable: true,
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
];

// Computed properties (tasksWithRaciRoles removed - now using inline mapping in templates)

// Summary statistics for ACTIVE sprint
const activeSprintSummary = computed(() => {
  const totalPert = activeSprintTasks.value.reduce((sum, task) => sum + task.pertDuration, 0);
  const totalAdjusted = activeSprintTasks.value.reduce(
    (sum, task) => sum + task.adjustedDuration,
    0,
  );
  const increase = totalPert === 0 ? 0 : ((totalAdjusted - totalPert) / totalPert) * 100;

  return {
    totalPertDuration: totalPert,
    totalAdjustedDuration: totalAdjusted,
    durationIncrease: increase,
    taskCount: activeSprintTasks.value.length,
  };
});

// Summary statistics for PLANNED sprint
const plannedSprintSummary = computed(() => {
  const totalPert = plannedSprintTasks.value.reduce((sum, task) => sum + task.pertDuration, 0);
  const totalAdjusted = plannedSprintTasks.value.reduce(
    (sum, task) => sum + task.adjustedDuration,
    0,
  );
  const increase = totalPert === 0 ? 0 : ((totalAdjusted - totalPert) / totalPert) * 100;

  return {
    totalPertDuration: totalPert,
    totalAdjustedDuration: totalAdjusted,
    durationIncrease: increase,
    taskCount: plannedSprintTasks.value.length,
  };
});

// Summary statistics for PAST sprints
const pastSprintsSummary = computed(() => {
  return pastSprintsTasks.value.map((sprintGroup) => {
    const totalPert = sprintGroup.tasks.reduce((sum, task) => sum + task.pertDuration, 0);
    const totalAdjusted = sprintGroup.tasks.reduce((sum, task) => sum + task.adjustedDuration, 0);
    const increase = totalPert === 0 ? 0 : ((totalAdjusted - totalPert) / totalPert) * 100;

    return {
      sprint: sprintGroup.sprint,
      totalPertDuration: totalPert,
      totalAdjustedDuration: totalAdjusted,
      durationIncrease: increase,
      taskCount: sprintGroup.tasks.length,
    };
  });
});

// Summary statistics for FUTURE/BACKLOG tasks
const futureBacklogSummary = computed(() => {
  const totalPert = futureBacklogTasks.value.reduce((sum, task) => sum + task.pertDuration, 0);
  const totalAdjusted = futureBacklogTasks.value.reduce(
    (sum, task) => sum + task.adjustedDuration,
    0,
  );
  const increase = totalPert === 0 ? 0 : ((totalAdjusted - totalPert) / totalPert) * 100;

  return {
    totalPertDuration: totalPert,
    totalAdjustedDuration: totalAdjusted,
    durationIncrease: increase,
    taskCount: futureBacklogTasks.value.length,
  };
});

// Count of completed sprints in CURRENT project only
const completedSprintsInCurrentProject = computed(() => {
  return pastSprintsTasks.value.length;
});

// RACI Weighted Workload for Active Sprint across ALL projects
const raciWeightedWorkload = computed(() => {
  if (!selectedProject.value) return [];

  // Get members from current project only (but calculate cross-project workload for them)
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id),
  );

  const workloadMap = new Map<number, { memberId: number; memberName: string; workload: number }>();

  // Initialize map with project members only
  projectMembers.forEach((member) => {
    workloadMap.set(member.id, {
      memberId: member.id,
      memberName: member.name,
      workload: 0,
    });
  });

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    // FIX: Find active sprint for EACH project (not just selected project)
    const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');

    if (project.tasks && projectActiveSprint) {
      project.tasks.forEach((task) => {
        // Only count tasks in THIS project's active sprint
        if (task.sprintId === projectActiveSprint.id) {
          const sp = task.storyPoints || 0;

          // Add weighted SP for Responsible (using workload weight)
          if (task.raci?.responsible) {
            task.raci.responsible.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.responsible * sp;
              }
            });
          }

          // Add weighted SP for Accountable (using workload weight)
          if (task.raci?.accountable) {
            const memberId = task.raci.accountable;
            const current = workloadMap.get(memberId);
            if (current) {
              current.workload += raciWorkloadWeights.value.accountable * sp;
            }
          }

          // Add weighted SP for Consulted (using workload weight)
          if (task.raci?.consulted) {
            task.raci.consulted.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.consulted * sp;
              }
            });
          }

          // Add weighted SP for Informed (using workload weight)
          if (task.raci?.informed) {
            task.raci.informed.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.informed * sp;
              }
            });
          }
        }
      });
    }
  });

  // Convert map to array and calculate percentage workload
  const workloadArray = Array.from(workloadMap.values())
    .map((item) => {
      // Get member's max story points
      const member = projectMembers.find((m) => m.id === item.memberId);
      const maxSP = member?.maxStoryPoints || 20;

      return {
        ...item,
        weightedSP: Math.round(item.workload), // Round weighted SP to whole number
        workload: Math.round((item.workload / maxSP) * 100), // Convert to percentage and round
      };
    })
    // Show all project members, even with 0% workload (for consistency)
    .sort((a, b) => b.workload - a.workload); // Sort by workload descending

  return workloadArray;
});

// RACI Weighted Workload for Planned Sprint (cross-project calculation)
const plannedSprintRaciWorkload = computed(() => {
  if (!selectedProject.value) return [];

  // Get members from current project only (but calculate cross-project workload for them)
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id),
  );

  const workloadMap = new Map<number, { memberId: number; memberName: string; workload: number }>();

  // Initialize map with project members only
  projectMembers.forEach((member) => {
    workloadMap.set(member.id, {
      memberId: member.id,
      memberName: member.name,
      workload: 0,
    });
  });

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    // Find planned sprint for EACH project
    const projectPlannedSprint = project.sprints?.find((s) => s.status === 'planned');

    if (project.tasks && projectPlannedSprint) {
      project.tasks.forEach((task) => {
        // Only count tasks in THIS project's planned sprint
        if (task.sprintId === projectPlannedSprint.id) {
          const sp = task.storyPoints || 0;

          // Add weighted SP for Responsible (using workload weight)
          if (task.raci?.responsible) {
            task.raci.responsible.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.responsible * sp;
              }
            });
          }

          // Add weighted SP for Accountable (using workload weight)
          if (task.raci?.accountable) {
            const memberId = task.raci.accountable;
            const current = workloadMap.get(memberId);
            if (current) {
              current.workload += raciWorkloadWeights.value.accountable * sp;
            }
          }

          // Add weighted SP for Consulted (using workload weight)
          if (task.raci?.consulted) {
            task.raci.consulted.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.consulted * sp;
              }
            });
          }

          // Add weighted SP for Informed (using workload weight)
          if (task.raci?.informed) {
            task.raci.informed.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.informed * sp;
              }
            });
          }
        }
      });
    }
  });

  // Convert map to array and calculate percentage workload
  const workloadArray = Array.from(workloadMap.values())
    .map((item) => {
      // Get member's max story points
      const member = projectMembers.find((m) => m.id === item.memberId);
      const maxSP = member?.maxStoryPoints || 20;

      return {
        ...item,
        weightedSP: Math.round(item.workload), // Round weighted SP to whole number
        workload: Math.round((item.workload / maxSP) * 100), // Convert to percentage and round
      };
    })
    // Show all project members, even with 0% workload (for consistency)
    .sort((a, b) => b.workload - a.workload); // Sort by workload descending

  return workloadArray;
});

// Total count of completed sprints across ALL projects (for average calculation)
// Reserved for future use (e.g., for comparing cross-project vs. current-project averages)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const totalCompletedSprintsCountAllProjects = computed(() => {
  const processedSprints = new Set<number>();

  projectStore.projects.forEach((project) => {
    if (project.sprints) {
      project.sprints.forEach((sprint) => {
        if (sprint.status === 'completed') {
          processedSprints.add(sprint.id);
        }
      });
    }
  });

  return processedSprints.size;
});

// Average RACI Weighted Workload from completed sprints across ALL projects
// Includes ALL RACI workload (R+A+C+I) for more accurate capacity planning
// Reserved for future use (e.g., for comparing cross-project vs. current-project averages)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const averageRaciWeightedWorkload = computed(() => {
  if (!selectedProject.value) return [];

  // Get members from current project only (but calculate cross-project workload for them)
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id),
  );

  const workloadMap = new Map<
    number,
    {
      memberId: number;
      memberName: string;
      totalWorkload: number;
      sprintCount: number;
      sprintDetails: Array<{ projectName: string; sprintName: string; workload: number }>;
    }
  >();

  // Initialize map with project members only
  projectMembers.forEach((member) => {
    workloadMap.set(member.id, {
      memberId: member.id,
      memberName: member.name,
      totalWorkload: 0,
      sprintCount: 0,
      sprintDetails: [],
    });
  });

  // Track which sprints we've processed (to avoid counting same sprint twice)
  const processedSprints = new Set<number>();

  // Iterate through ALL projects to find completed sprints
  projectStore.projects.forEach((project) => {
    if (project.sprints) {
      project.sprints.forEach((sprint) => {
        if (sprint.status === 'completed' && !processedSprints.has(sprint.id)) {
          processedSprints.add(sprint.id);

          // Store project name for sprint details
          const projectName = project.name;
          const sprintName = sprint.name;

          // Calculate workload for each member in this sprint
          const sprintWorkload = new Map<number, number>();

          // Initialize sprint workload for project members only
          projectMembers.forEach((member) => {
            sprintWorkload.set(member.id, 0);
          });

          // Calculate workload from all projects for this sprint
          projectStore.projects.forEach((proj) => {
            if (proj.tasks) {
              proj.tasks.forEach((task) => {
                if (task.sprintId === sprint.id) {
                  const sp = task.storyPoints || 0;

                  // Add weighted SP for each RACI role
                  if (task.raci?.responsible) {
                    task.raci.responsible.forEach((memberId: number) => {
                      const current = sprintWorkload.get(memberId) || 0;
                      sprintWorkload.set(
                        memberId,
                        current + raciWorkloadWeights.value.responsible * sp,
                      );
                    });
                  }

                  if (task.raci?.accountable) {
                    const memberId = task.raci.accountable;
                    const current = sprintWorkload.get(memberId) || 0;
                    sprintWorkload.set(
                      memberId,
                      current + raciWorkloadWeights.value.accountable * sp,
                    );
                  }

                  if (task.raci?.consulted) {
                    task.raci.consulted.forEach((memberId: number) => {
                      const current = sprintWorkload.get(memberId) || 0;
                      sprintWorkload.set(
                        memberId,
                        current + raciWorkloadWeights.value.consulted * sp,
                      );
                    });
                  }

                  if (task.raci?.informed) {
                    task.raci.informed.forEach((memberId: number) => {
                      const current = sprintWorkload.get(memberId) || 0;
                      sprintWorkload.set(
                        memberId,
                        current + raciWorkloadWeights.value.informed * sp,
                      );
                    });
                  }
                }
              });
            }
          });

          // Add this sprint's workload to the total (includes all RACI roles: R+A+C+I)
          // Only count sprints where member has at least 1 weighted SP
          sprintWorkload.forEach((workload, memberId) => {
            if (workload >= 1) {
              const memberData = workloadMap.get(memberId);
              if (memberData) {
                memberData.totalWorkload += workload;
                memberData.sprintCount += 1;
                // Add sprint details for tooltip
                memberData.sprintDetails.push({
                  projectName: projectName,
                  sprintName: sprintName,
                  workload: Math.round(workload * 100) / 100, // Round to 2 decimals
                });
              }
            }
          });
        }
      });
    }
  });

  // Calculate average and convert to array
  const workloadArray = Array.from(workloadMap.values())
    .map((item) => {
      // Calculate average weighted SP
      const avgWeightedSP = item.sprintCount > 0 ? item.totalWorkload / item.sprintCount : 0;

      // Get member's max story points to calculate percentage
      const member = projectMembers.find((m) => m.id === item.memberId);
      const maxSP = member?.maxStoryPoints || 20;

      return {
        memberId: item.memberId,
        memberName: item.memberName,
        weightedSP: Math.round(avgWeightedSP), // Round weighted SP to whole number
        workload: Math.round((avgWeightedSP / maxSP) * 100), // Convert to percentage and round
        sprintCount: item.sprintCount,
        sprintDetails: item.sprintDetails,
      };
    })
    // Show all project members, even with 0% workload (for consistency)
    .sort((a, b) => b.workload - a.workload); // Sort by workload descending

  return workloadArray;
});

// Average RACI Weighted Workload from completed sprints in CURRENT project only
// This calculates the average from sprints belonging to the selected project
const averageRaciWeightedWorkloadInCurrentProject = computed(() => {
  if (!selectedProject.value) return [];

  // Get members from current project only
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id),
  );

  const workloadMap = new Map<
    number,
    {
      memberId: number;
      memberName: string;
      totalWorkload: number;
      sprintCount: number;
      sprintDetails: Array<{ projectName: string; sprintName: string; workload: number }>;
    }
  >();

  // Initialize map with project members only
  projectMembers.forEach((member) => {
    workloadMap.set(member.id, {
      memberId: member.id,
      memberName: member.name,
      totalWorkload: 0,
      sprintCount: 0,
      sprintDetails: [],
    });
  });

  // Iterate through completed sprints of CURRENT project only
  const currentProject = selectedProject.value;
  if (currentProject.sprints) {
    currentProject.sprints.forEach((sprint) => {
      if (sprint.status === 'completed') {
        // Store project name for sprint details
        const projectName = currentProject.name;
        const sprintName = sprint.name;

        // Calculate workload for each member in this sprint
        const sprintWorkload = new Map<number, number>();

        // Initialize sprint workload for project members only
        projectMembers.forEach((member) => {
          sprintWorkload.set(member.id, 0);
        });

        // Calculate workload from all projects for this sprint (cross-project)
        projectStore.projects.forEach((proj) => {
          if (proj.tasks) {
            proj.tasks.forEach((task) => {
              if (task.sprintId === sprint.id) {
                const sp = task.storyPoints || 0;

                // Add weighted SP for each RACI role
                if (task.raci?.responsible) {
                  task.raci.responsible.forEach((memberId: number) => {
                    const current = sprintWorkload.get(memberId) || 0;
                    sprintWorkload.set(
                      memberId,
                      current + raciWorkloadWeights.value.responsible * sp,
                    );
                  });
                }

                if (task.raci?.accountable) {
                  const memberId = task.raci.accountable;
                  const current = sprintWorkload.get(memberId) || 0;
                  sprintWorkload.set(
                    memberId,
                    current + raciWorkloadWeights.value.accountable * sp,
                  );
                }

                if (task.raci?.consulted) {
                  task.raci.consulted.forEach((memberId: number) => {
                    const current = sprintWorkload.get(memberId) || 0;
                    sprintWorkload.set(
                      memberId,
                      current + raciWorkloadWeights.value.consulted * sp,
                    );
                  });
                }

                if (task.raci?.informed) {
                  task.raci.informed.forEach((memberId: number) => {
                    const current = sprintWorkload.get(memberId) || 0;
                    sprintWorkload.set(memberId, current + raciWorkloadWeights.value.informed * sp);
                  });
                }
              }
            });
          }
        });

        // Add this sprint's workload to the total (includes all RACI roles: R+A+C+I)
        // Only count sprints where member has at least 1 weighted SP
        sprintWorkload.forEach((workload, memberId) => {
          if (workload >= 1) {
            const memberData = workloadMap.get(memberId);
            if (memberData) {
              memberData.totalWorkload += workload;
              memberData.sprintCount += 1;
              // Add sprint details for tooltip
              memberData.sprintDetails.push({
                projectName: projectName,
                sprintName: sprintName,
                workload: Math.round(workload * 100) / 100, // Round to 2 decimals
              });
            }
          }
        });
      }
    });
  }

  // Calculate average and convert to array
  const workloadArray = Array.from(workloadMap.values())
    .map((item) => {
      // Calculate average weighted SP
      const avgWeightedSP = item.sprintCount > 0 ? item.totalWorkload / item.sprintCount : 0;

      // Get member's max story points to calculate percentage
      const member = projectMembers.find((m) => m.id === item.memberId);
      const maxSP = member?.maxStoryPoints || 20;

      return {
        memberId: item.memberId,
        memberName: item.memberName,
        weightedSP: Math.round(avgWeightedSP), // Round weighted SP to whole number
        workload: Math.round((avgWeightedSP / maxSP) * 100), // Convert to percentage and round
        sprintCount: item.sprintCount,
        sprintDetails: item.sprintDetails,
      };
    })
    // Show all project members, even with 0% workload (for consistency)
    .sort((a, b) => b.workload - a.workload); // Sort by workload descending

  return workloadArray;
});

// Get RACI Weighted Workload for a specific sprint across ALL projects
function getSprintRaciWeightedWorkload(sprintId: number) {
  if (!selectedProject.value) return [];

  // Get members from current project only
  const projectMembers = teamStore.teamMembers.filter((member) =>
    selectedProject.value?.teamMemberIds?.includes(member.id),
  );

  const workloadMap = new Map<number, { memberId: number; memberName: string; workload: number }>();

  // Initialize map with project members only
  projectMembers.forEach((member) => {
    workloadMap.set(member.id, {
      memberId: member.id,
      memberName: member.name,
      workload: 0,
    });
  });

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    if (project.tasks) {
      project.tasks.forEach((task) => {
        // Only count tasks in this specific sprint
        if (task.sprintId === sprintId) {
          const sp = task.storyPoints || 0;

          // Add weighted SP for Responsible
          if (task.raci?.responsible) {
            task.raci.responsible.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.responsible * sp;
              }
            });
          }

          // Add weighted SP for Accountable
          if (task.raci?.accountable) {
            const memberId = task.raci.accountable;
            const current = workloadMap.get(memberId);
            if (current) {
              current.workload += raciWorkloadWeights.value.accountable * sp;
            }
          }

          // Add weighted SP for Consulted
          if (task.raci?.consulted) {
            task.raci.consulted.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.consulted * sp;
              }
            });
          }

          // Add weighted SP for Informed
          if (task.raci?.informed) {
            task.raci.informed.forEach((memberId: number) => {
              const current = workloadMap.get(memberId);
              if (current) {
                current.workload += raciWorkloadWeights.value.informed * sp;
              }
            });
          }
        }
      });
    }
  });

  // Convert map to array and calculate percentage workload
  const workloadArray = Array.from(workloadMap.values())
    .map((item) => {
      // Get member's max story points
      const member = projectMembers.find((m) => m.id === item.memberId);
      const maxSP = member?.maxStoryPoints || 20;

      return {
        ...item,
        weightedSP: Math.round(item.workload), // Round weighted SP to whole number
        workload: Math.round((item.workload / maxSP) * 100), // Convert to percentage and round
      };
    })
    // Show all project members, even with 0% workload (for consistency)
    .sort((a, b) => b.workload - a.workload); // Sort by workload descending

  return workloadArray;
}

// Keep these for backward compatibility with old UI
// Removed: totalPertDuration, totalAdjustedDuration, durationIncrease computed properties
// (Summary Statistics section was removed as redundant with tab-specific summaries)

// Methods
function calculatePertDuration(
  optimistic: number,
  mostLikely: number,
  pessimistic: number,
): number {
  return (optimistic + 4 * mostLikely + pessimistic) / 6;
}

// Helper function to get member's story points in a specific sprint across ALL projects
function getMemberStoryPointsInSprint(memberId: number, sprintId: number | null): number {
  if (sprintId === null) return 0;

  let total = 0;

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    if (project.tasks) {
      project.tasks.forEach((task) => {
        // Only count tasks in the specified sprint
        if (task.sprintId === sprintId) {
          // Check if member is in any RACI role
          if (
            task.raci?.responsible?.includes(memberId) ||
            task.raci?.accountable === memberId ||
            task.raci?.consulted?.includes(memberId) ||
            task.raci?.informed?.includes(memberId)
          ) {
            total += task.storyPoints || 0;
          }
        }
      });
    }
  });

  return total;
}

// Helper function to get member's WEIGHTED story points in a specific sprint across ALL projects
// Uses RACI workload weights (configurable)
// Reserved for potential future use (currently using getMemberWeightedStoryPointsInAllActiveSprints)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getMemberWeightedStoryPointsInSprint(memberId: number, sprintId: number | null): number {
  if (sprintId === null) return 0;

  let total = 0;

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    if (project.tasks) {
      project.tasks.forEach((task) => {
        // Only count tasks in the specified sprint
        if (task.sprintId === sprintId) {
          const sp = task.storyPoints || 0;

          // Add weighted SP based on RACI role using workload weights
          if (task.raci?.responsible?.includes(memberId)) {
            total += raciWorkloadWeights.value.responsible * sp;
          }
          if (task.raci?.accountable === memberId) {
            total += raciWorkloadWeights.value.accountable * sp;
          }
          if (task.raci?.consulted?.includes(memberId)) {
            total += raciWorkloadWeights.value.consulted * sp;
          }
          if (task.raci?.informed?.includes(memberId)) {
            total += raciWorkloadWeights.value.informed * sp;
          }
        }
      });
    }
  });

  return total;
}

// Helper function to get member's story points in active sprint across ALL projects
// Reserved for future use (e.g., for detailed member analysis)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getMemberStoryPointsInActiveSprint(memberId: number): number {
  if (!selectedProject.value) return 0;

  // Get active sprint from the selected project
  const activeSprint = selectedProject.value.sprints?.find((s) => s.status === 'active');
  if (!activeSprint) return 0;

  return getMemberStoryPointsInSprint(memberId, activeSprint.id);
}

// Helper function to get member's WEIGHTED story points in ALL active sprints across ALL projects
// Uses RACI workload weights (configurable)
// This is used for calculateAdjustedDuration to reflect true cross-project workload
function getMemberWeightedStoryPointsInAllActiveSprints(memberId: number): number {
  let total = 0;

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    // Find active sprint for EACH project (not just selected project)
    const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');

    if (project.tasks && projectActiveSprint) {
      project.tasks.forEach((task) => {
        // Only count tasks in THIS project's active sprint
        if (task.sprintId === projectActiveSprint.id) {
          const sp = task.storyPoints || 0;

          // Add weighted SP based on RACI role using workload weights
          if (task.raci?.responsible?.includes(memberId)) {
            total += raciWorkloadWeights.value.responsible * sp;
          }
          if (task.raci?.accountable === memberId) {
            total += raciWorkloadWeights.value.accountable * sp;
          }
          if (task.raci?.consulted?.includes(memberId)) {
            total += raciWorkloadWeights.value.consulted * sp;
          }
          if (task.raci?.informed?.includes(memberId)) {
            total += raciWorkloadWeights.value.informed * sp;
          }
        }
      });
    }
  });

  return total;
}

// Helper function to get average member's story points from past sprints across ALL projects
// Reserved for backward compatibility (now using weighted version)
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getAverageMemberStoryPoints(memberId: number): number {
  const sprintTotals: number[] = [];
  const processedSprints = new Set<number>();

  // Iterate through all projects to find completed sprints
  projectStore.projects.forEach((project) => {
    if (project.sprints) {
      project.sprints.forEach((sprint) => {
        if (sprint.status === 'completed' && !processedSprints.has(sprint.id)) {
          processedSprints.add(sprint.id);
          const sprintTotal = getMemberStoryPointsInSprint(memberId, sprint.id);
          if (sprintTotal > 0) {
            sprintTotals.push(sprintTotal);
          }
        }
      });
    }
  });

  if (sprintTotals.length === 0) return 0;

  const sum = sprintTotals.reduce((acc, val) => acc + val, 0);
  return sum / sprintTotals.length;
}

function calculateRaciOverload(raciMembers: Task['raciMembers']): number {
  const totalRaciCount =
    raciMembers.responsible.length +
    (raciMembers.accountable !== null ? 1 : 0) + // Single value or null
    raciMembers.consulted.length +
    raciMembers.informed.length;
  return totalRaciCount / maxStoryPointsPerPerson.value;
}

// Updated calculateAdjustedDuration with RACI Weighted Workload
// Uses weighted story points (R=1.0, A=0.1, C=0.05, I=0.01) for overload calculation
// Duration increases ONLY when team members are overloaded (weighted SP > maxStoryPointsPerPerson)
function calculateAdjustedDuration(
  task: Task,
  sprintId: number | null,
  useAverage: boolean = false,
): number {
  const pertDuration = task.pertDuration;

  // Calculate LR: average EXCESS overload for Responsible role
  let LR = 0;
  if (task.raciMembers.responsible.length > 0) {
    const sumExcessOverload = task.raciMembers.responsible.reduce((sum, memberId) => {
      const memberWeightedSP = useAverage
        ? getMemberAverageWeightedSpInProject(memberId)
        : getMemberWeightedStoryPointsInAllActiveSprints(memberId);
      const overload = memberWeightedSP / maxStoryPointsPerPerson.value;
      const excess = Math.max(0, overload - 1); // Excess over 100% capacity
      return sum + excess;
    }, 0);
    LR = sumExcessOverload / task.raciMembers.responsible.length;
  }

  // Calculate LA: average overload for Accountable role
  let LA = 0;
  if (task.raciMembers.accountable !== null) {
    const memberWeightedSP = useAverage
      ? getMemberAverageWeightedSpInProject(task.raciMembers.accountable)
      : getMemberWeightedStoryPointsInAllActiveSprints(task.raciMembers.accountable);
    LA = Math.max(0, memberWeightedSP / maxStoryPointsPerPerson.value - 1);
  }

  // Calculate LC: average EXCESS overload for Consulted role
  let LC = 0;
  if (task.raciMembers.consulted.length > 0) {
    const sumExcessOverload = task.raciMembers.consulted.reduce((sum, memberId) => {
      const memberWeightedSP = useAverage
        ? getMemberAverageWeightedSpInProject(memberId)
        : getMemberWeightedStoryPointsInAllActiveSprints(memberId);
      const overload = memberWeightedSP / maxStoryPointsPerPerson.value;
      const excess = Math.max(0, overload - 1); // Excess over 100% capacity
      return sum + excess;
    }, 0);
    LC = sumExcessOverload / task.raciMembers.consulted.length;
  }

  // Calculate LI: average EXCESS overload for Informed role
  let LI = 0;
  if (task.raciMembers.informed.length > 0) {
    const sumExcessOverload = task.raciMembers.informed.reduce((sum, memberId) => {
      const memberWeightedSP = useAverage
        ? getMemberAverageWeightedSpInProject(memberId)
        : getMemberWeightedStoryPointsInAllActiveSprints(memberId);
      const overload = memberWeightedSP / maxStoryPointsPerPerson.value;
      const excess = Math.max(0, overload - 1); // Excess over 100% capacity
      return sum + excess;
    }, 0);
    LI = sumExcessOverload / task.raciMembers.informed.length;
  }

  // Apply the formula: Tnew = T × (1 + (R_weight×LR) + (A_weight×LA) + (C_weight×LC) + (I_weight×LI))
  // Note: LR, LA, LC, LI represent EXCESS over 1.0 (only overload above 100% capacity increases duration)
  // Use dynamic weights from raciWeights (duration weights)
  const raciAdjustment =
    raciWeights.value.responsible * LR +
    raciWeights.value.accountable * LA +
    raciWeights.value.consulted * LC +
    raciWeights.value.informed * LI;

  return pertDuration * (1 + raciAdjustment);
}

// Tasks are now computed, so recalculation happens automatically when dependencies change

function validateWeights(weights: RaciWeights | RaciWorkloadWeights): boolean {
  if (
    weights.responsible < 0 ||
    weights.responsible > 10 ||
    weights.accountable < 0 ||
    weights.accountable > 10 ||
    weights.consulted < 0 ||
    weights.consulted > 10 ||
    weights.informed < 0 ||
    weights.informed > 10
  ) {
    $q.notify({
      message: 'Váhy musia byť v rozsahu 0 až 10',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return false;
  }
  return true;
}

async function applyDurationWeights() {
  log('weights_apply_duration', 'pert_raci_optimization', selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {});
  if (!validateWeights(raciWeights.value)) return;

  // Save configuration to localStorage (for backwards compatibility)
  localStorage.setItem('max_story_points_per_person', maxStoryPointsPerPerson.value.toString());

  // Save to database via API
  await saveRaciWeightsToApi();

  // Tasks are computed, so they will recalculate automatically with new weights
}

async function resetDurationWeights() {
  log('weights_reset_duration', 'pert_raci_optimization', selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {});
  raciWeights.value = {
    responsible: 1.0,
    accountable: 0.1,
    consulted: 0.05,
    informed: 0.01,
  };

  // Save to database via API
  await saveRaciWeightsToApi();

  // Tasks are computed, so they will recalculate automatically with new weights
}

async function applyWorkloadWeights() {
  log('weights_apply_workload', 'pert_raci_optimization', selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {});
  if (!validateWeights(raciWorkloadWeights.value)) return;
  await saveRaciWeightsToApi();
}

async function resetWorkloadWeights() {
  log('weights_reset_workload', 'pert_raci_optimization', selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {});
  raciWorkloadWeights.value = {
    responsible: 1.0,
    accountable: 0.1,
    consulted: 0.05,
    informed: 0.01,
  };
  await saveRaciWeightsToApi();
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
  return `${sign}${increase.toFixed(2)}%`;
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

// Team member functions

function getMemberName(memberId: number): string {
  // Search in all team members, not just project members
  // This handles cases where a member is assigned to a task but not in project.teamMemberIds
  const member = teamStore.teamMembers.find((m) => m.id === memberId);
  return member ? member.name : `Member ${memberId}`;
}

// Get member's AVERAGE WEIGHTED SP from past sprints in current project (for future/backlog tasks)
// Uses cross-project workload (same logic as averageRaciWeightedWorkloadInCurrentProject)
function getMemberAverageWeightedSpInProject(memberId: number): number {
  if (!selectedProject.value) return 0;

  const sprintTotals: number[] = [];
  const processedSprints = new Set<number>();

  // Find completed sprints in the selected project
  const currentProject = selectedProject.value;
  if (currentProject.sprints) {
    currentProject.sprints.forEach((sprint) => {
      if (sprint.status === 'completed' && !processedSprints.has(sprint.id)) {
        processedSprints.add(sprint.id);

        let sprintTotal = 0;

        // Calculate weighted SP for this member in this sprint across ALL projects (cross-project)
        // This matches the logic in averageRaciWeightedWorkloadInCurrentProject
        projectStore.projects.forEach((proj) => {
          if (proj.tasks) {
            proj.tasks.forEach((task) => {
              if (task.sprintId === sprint.id) {
                const sp = task.storyPoints || 0;

                if (task.raci?.responsible?.includes(memberId)) {
                  sprintTotal += raciWorkloadWeights.value.responsible * sp;
                }
                if (task.raci?.accountable === memberId) {
                  sprintTotal += raciWorkloadWeights.value.accountable * sp;
                }
                if (task.raci?.consulted?.includes(memberId)) {
                  sprintTotal += raciWorkloadWeights.value.consulted * sp;
                }
                if (task.raci?.informed?.includes(memberId)) {
                  sprintTotal += raciWorkloadWeights.value.informed * sp;
                }
              }
            });
          }
        });

        // Only add to totals if member has workload >= 1 SP
        // This ensures we only count sprints where member actively worked (not just marginally consulted/informed)
        if (sprintTotal >= 1) {
          sprintTotals.push(sprintTotal);
        }
      }
    });
  }

  if (sprintTotals.length === 0) return 0;

  const sum = sprintTotals.reduce((acc, val) => acc + val, 0);
  const average = sum / sprintTotals.length;
  return average; // Don't round here - let calculateAdjustedDuration handle precision
}

// Get all tasks for a member from active sprints across all projects (for debugging/display)
function getMemberActiveSprintTasks(memberId: number): Array<{
  taskId: number;
  taskName: string;
  projectName: string;
  sprintName: string;
  storyPoints: number;
  roles: string[];
}> {
  const tasks: Array<{
    taskId: number;
    taskName: string;
    projectName: string;
    sprintName: string;
    storyPoints: number;
    roles: string[];
  }> = [];

  projectStore.projects.forEach((project) => {
    const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');

    if (project.tasks && projectActiveSprint) {
      project.tasks.forEach((task) => {
        if (task.sprintId === projectActiveSprint.id) {
          const roles: string[] = [];

          // Check which RACI roles the member has for this task
          if (task.raci?.responsible?.includes(memberId)) {
            roles.push('R');
          }
          if (task.raci?.accountable === memberId) {
            roles.push('A');
          }
          if (task.raci?.consulted?.includes(memberId)) {
            roles.push('C');
          }
          if (task.raci?.informed?.includes(memberId)) {
            roles.push('I');
          }

          // Only add task if member has at least one role
          if (roles.length > 0) {
            tasks.push({
              taskId: task.id,
              taskName: task.title || task.name || `Task ${task.id}`,
              projectName: project.name,
              sprintName: projectActiveSprint.name,
              storyPoints: task.storyPoints || 0,
              roles: roles,
            });
          }
        }
      });
    }
  });

  return tasks;
}

// Get member's active projects (projects with active sprints where member has tasks)
function getMemberActiveProjects(memberId: number): string[] {
  const activeProjects = new Set<string>();

  projectStore.projects.forEach((project) => {
    const activeSprint = project.sprints?.find((s) => s.status === 'active');
    if (activeSprint && project.tasks) {
      const hasTasks = project.tasks.some(
        (task) =>
          task.sprintId === activeSprint.id &&
          (task.raci?.responsible?.includes(memberId) ||
            task.raci?.accountable === memberId ||
            task.raci?.consulted?.includes(memberId) ||
            task.raci?.informed?.includes(memberId)),
      );

      if (hasTasks) {
        activeProjects.add(project.name);
      }
    }
  });

  return Array.from(activeProjects);
}

// Get member's active sprints (sprints where member has tasks)
function getMemberActiveSprints(memberId: number): string[] {
  const activeSprints = new Set<string>();

  projectStore.projects.forEach((project) => {
    if (project.sprints) {
      project.sprints.forEach((sprint) => {
        if (sprint.status === 'active' && project.tasks) {
          const hasTasks = project.tasks.some(
            (task) =>
              task.sprintId === sprint.id &&
              (task.raci?.responsible?.includes(memberId) ||
                task.raci?.accountable === memberId ||
                task.raci?.consulted?.includes(memberId) ||
                task.raci?.informed?.includes(memberId)),
          );

          if (hasTasks) {
            activeSprints.add(`${project.name}: ${sprint.name}`);
          }
        }
      });
    }
  });

  return Array.from(activeSprints);
}

function toggleRowExpansion(rowId: number) {
  const index = expandedRows.value.indexOf(rowId.toString());
  if (index > -1) {
    expandedRows.value.splice(index, 1);
  } else {
    expandedRows.value.push(rowId.toString());
  }
}

// Legacy function - kept for backward compatibility if needed elsewhere
// eslint-disable-next-line @typescript-eslint/no-unused-vars
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

// Legacy function - kept for backward compatibility if needed elsewhere
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getMemberSprintStoryPoints(memberId: number): number {
  if (!selectedProject.value) return 0;

  // Get active sprint
  const activeSprint = selectedProject.value.sprints?.find((s) => s.status === 'active');
  if (!activeSprint) return 0;

  // Get tasks from project store that are in active sprint
  const projectTasks = selectedProject.value.tasks || [];
  let total = 0;

  projectTasks.forEach((task) => {
    if (task.sprintId === activeSprint.id) {
      if (
        task.raci.responsible.includes(memberId) ||
        task.raci.accountable === memberId ||
        task.raci.consulted.includes(memberId) ||
        task.raci.informed.includes(memberId)
      ) {
        total += task.storyPoints;
      }
    }
  });

  return total;
}

// Legacy function - kept for backward compatibility if needed elsewhere
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getMemberProjects(memberId: number): string[] {
  const projects = new Set<string>();

  // Check all projects in store
  projectStore.projects.forEach((project) => {
    if (project.teamMemberIds?.includes(memberId) && project.tasks) {
      // Check if member has any tasks in this project
      const hasTasks = project.tasks.some(
        (task) =>
          task.raci.responsible.includes(memberId) ||
          task.raci.accountable === memberId ||
          task.raci.consulted.includes(memberId) ||
          task.raci.informed.includes(memberId),
      );

      if (hasTasks) {
        projects.add(project.name);
      }
    }
  });

  return Array.from(projects);
}

function getMemberTasks(memberId: number): Task[] {
  if (!selectedProject.value) return [];

  // Get active sprint
  const activeSprint = selectedProject.value.sprints?.find((s) => s.status === 'active');
  if (!activeSprint) return [];

  // Get tasks from project store that are in active sprint
  const projectTasks = selectedProject.value.tasks || [];

  return projectTasks
    .filter((task) => task.sprintId === activeSprint.id)
    .filter(
      (task) =>
        task.raci.responsible.includes(memberId) ||
        task.raci.accountable === memberId ||
        task.raci.consulted.includes(memberId) ||
        task.raci.informed.includes(memberId),
    )
    .map((task) => {
      // Map to local Task interface
      const pertDuration = calculatePertDuration(
        task.pert.optimistic || 0,
        task.pert.mostLikely || 0,
        task.pert.pessimistic || 0,
      );

      return {
        id: task.id,
        name: task.title || task.name,
        description: task.description,
        storyPoints: task.storyPoints,
        optimistic: task.pert.optimistic || 0,
        mostLikely: task.pert.mostLikely || 0,
        pessimistic: task.pert.pessimistic || 0,
        pertDuration,
        adjustedDuration: pertDuration,
        raciMembers: {
          responsible: task.raci.responsible || [],
          accountable: task.raci.accountable,
          consulted: task.raci.consulted || [],
          informed: task.raci.informed || [],
        },
        overload: 0,
      };
    });
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

onMounted(async () => {
  await Promise.all([
    projectStore.fetchProjects(true),
    teamStore.fetchTeamMembers(),
    loadRaciWeightsFromApi(), // Load RACI weights from database
  ]);

  // Set default project if available
  if (projectStore.projects.length > 0 && !selectedProjectId.value) {
    const firstProject = projectStore.projects[0];
    if (firstProject) {
      selectedProjectId.value = firstProject.id;
    }
  }
});

const TAB_ACTION_MAP: Record<string, string> = {
  active: 'view_aktívny_šprint',
  planned: 'view_plánovaný_šprint',
  past: 'view_minulé_šprinty',
  future: 'view_budúce_tasky',
};

watch(selectedProjectId, (newVal) => {
  if (newVal) log('project_select', 'pert_raci_optimization', { projectId: newVal });
});

watch(activeTab, (newVal) => {
  const action = TAB_ACTION_MAP[newVal];
  if (action) log(action, 'pert_raci_optimization', selectedProjectId.value != null ? { projectId: selectedProjectId.value } : {});
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

.pert-raci-sections {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr;
}

.raci-weights-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (max-width: 1240px) {
  .raci-weights-grid {
    grid-template-columns: 1fr;
  }
}
</style>
