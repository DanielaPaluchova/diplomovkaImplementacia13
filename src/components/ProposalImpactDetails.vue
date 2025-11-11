<template>
  <div class="proposal-impact-details">
    <!-- Task Split Details -->
    <div v-if="proposal.type === 'split' && proposal.proposal">
      <div class="text-subtitle2 text-weight-bold q-mb-sm">Split Plan:</div>
      <div class="q-mb-sm">
        <strong>Original Task:</strong> {{ proposal.taskName || 'Task' }} ({{ proposal.taskSp }} SP)
      </div>
      <div class="row q-gutter-sm">
        <q-card
          v-for="(subtask, index) in proposal.proposal.subtasks"
          :key="index"
          flat
          bordered
          class="col"
        >
          <q-card-section class="q-pa-sm">
            <div class="text-caption text-weight-bold">Subtask {{ index + 1 }}</div>
            <div class="text-body2">{{ subtask.name }}</div>
            <div class="text-caption text-grey-7">{{ subtask.story_points }} SP</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Task Merge Details -->
    <div v-else-if="proposal.type === 'merge' && proposal.taskNames">
      <div class="text-subtitle2 text-weight-bold q-mb-sm">Merge Plan:</div>
      <div class="q-mb-xs">
        <strong>Merging {{ proposal.taskNames.length }} tasks:</strong>
      </div>
      <q-list dense>
        <q-item v-for="(name, index) in proposal.taskNames" :key="index" dense>
          <q-item-section avatar>
            <q-icon name="task" size="xs" />
          </q-item-section>
          <q-item-section>{{ name }}</q-item-section>
        </q-item>
      </q-list>
    </div>

    <!-- Reassignment Details -->
    <div
      v-else-if="
        proposal.type === 'reassign' ||
        proposal.type === 'bottleneck' ||
        proposal.type === 'skill_mismatch' ||
        proposal.type === 'priority_conflict'
      "
    >
      <div class="text-subtitle2 text-weight-bold q-mb-sm">
        {{
          proposal.impact?.suggestedAction === 'move_to_backlog'
            ? 'Backlog Move Plan:'
            : 'Reassignment Plan:'
        }}
      </div>

      <!-- Task Info -->
      <div class="q-mb-md">
        <strong>Task:</strong> {{ proposal.taskName || 'Task' }}
        <span
          v-if="proposal.taskSp || proposal.impact?.taskSP"
          class="text-primary text-weight-bold"
        >
          ({{ proposal.taskSp || proposal.impact?.taskSP }} SP)
        </span>
      </div>

      <!-- Backlog Move Warning -->
      <div v-if="proposal.impact?.suggestedAction === 'move_to_backlog'" class="q-mb-md">
        <q-banner dense class="bg-orange-1 text-orange-9">
          <template v-slot:avatar>
            <q-icon name="warning" color="orange" />
          </template>
          <div class="text-body2">
            <strong>All Team Members Are Overloaded</strong>
            <div class="q-mt-xs text-caption">
              {{
                proposal.impact.reason ||
                'No team member has sufficient capacity to take this task.'
              }}
            </div>
            <div class="q-mt-sm text-caption">
              <strong>Suggested Action:</strong> Move task to backlog or consider adding resources.
            </div>
          </div>
        </q-banner>

        <!-- Current Member Info -->
        <div v-if="proposal.impact?.fromMember" class="q-mt-md">
          <div class="text-caption text-grey-7 q-mb-xs">Current Assignment</div>
          <div class="row items-center q-gutter-sm">
            <div class="reassignment-member">
              <q-avatar color="red" text-color="white" size="32px">
                <q-icon name="person" />
              </q-avatar>
              <div class="text-caption q-mt-xs">{{ proposal.impact.fromMember }}</div>
            </div>
            <q-icon name="arrow_forward" size="24px" color="orange" />
            <div class="reassignment-member">
              <q-avatar color="grey" text-color="white" size="32px">
                <q-icon name="inbox" />
              </q-avatar>
              <div class="text-caption q-mt-xs">Backlog</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Member Reassignment -->
      <div v-else-if="proposal.impact?.fromMember && proposal.impact?.toMember" class="q-mb-md">
        <div class="text-caption text-grey-7 q-mb-xs">Team Member Assignment</div>
        <div class="row items-center q-gutter-sm">
          <div class="reassignment-member">
            <q-avatar color="orange" text-color="white" size="32px">
              <q-icon name="person" />
            </q-avatar>
            <div class="text-caption q-mt-xs">{{ proposal.impact.fromMember }}</div>
          </div>
          <q-icon name="arrow_forward" size="24px" color="primary" />
          <div class="reassignment-member">
            <q-avatar color="green" text-color="white" size="32px">
              <q-icon name="person" />
            </q-avatar>
            <div class="text-caption q-mt-xs">{{ proposal.impact.toMember }}</div>
          </div>
        </div>
      </div>

      <!-- Workload Impact -->
      <div
        v-if="
          proposal.impact?.fromWorkload !== undefined || proposal.impact?.toWorkload !== undefined
        "
        class="q-mb-sm"
      >
        <div class="text-caption text-grey-7 q-mb-xs">Workload Impact</div>

        <!-- From Member - Before and After -->
        <div v-if="proposal.impact?.fromWorkload !== undefined" class="q-mb-md">
          <div class="text-weight-bold text-caption q-mb-xs">{{ proposal.impact.fromMember }}</div>

          <!-- Before -->
          <div class="q-mb-xs">
            <div class="row items-center justify-between q-mb-xs">
              <span class="text-caption">Before</span>
              <span
                class="text-caption text-weight-bold"
                :class="getWorkloadColorClass(proposal.impact.fromWorkload)"
              >
                {{ proposal.impact.fromWorkload }}%
              </span>
            </div>
            <q-linear-progress
              :value="proposal.impact.fromWorkload / 100"
              :color="getWorkloadColor(proposal.impact.fromWorkload)"
              size="8px"
              rounded
            />
          </div>

          <!-- After -->
          <div v-if="proposal.impact?.fromWorkloadAfter !== undefined" class="q-mb-xs">
            <div class="row items-center justify-between q-mb-xs">
              <span class="text-caption">After</span>
              <span
                class="text-caption text-weight-bold"
                :class="getWorkloadColorClass(proposal.impact.fromWorkloadAfter)"
              >
                {{ proposal.impact.fromWorkloadAfter }}%
              </span>
            </div>
            <q-linear-progress
              :value="proposal.impact.fromWorkloadAfter / 100"
              :color="getWorkloadColor(proposal.impact.fromWorkloadAfter)"
              size="8px"
              rounded
            />
          </div>
        </div>

        <!-- To Member - Before and After -->
        <div
          v-if="
            proposal.impact?.toWorkload !== undefined &&
            proposal.impact?.suggestedAction !== 'move_to_backlog'
          "
          class="q-mb-sm"
        >
          <div class="text-weight-bold text-caption q-mb-xs">{{ proposal.impact.toMember }}</div>

          <!-- Before -->
          <div v-if="proposal.impact?.toWorkloadBefore !== undefined" class="q-mb-xs">
            <div class="row items-center justify-between q-mb-xs">
              <span class="text-caption">Before</span>
              <span
                class="text-caption text-weight-bold"
                :class="getWorkloadColorClass(proposal.impact.toWorkloadBefore)"
              >
                {{ proposal.impact.toWorkloadBefore }}%
              </span>
            </div>
            <q-linear-progress
              :value="proposal.impact.toWorkloadBefore / 100"
              :color="getWorkloadColor(proposal.impact.toWorkloadBefore)"
              size="8px"
              rounded
            />
          </div>

          <!-- After -->
          <div class="q-mb-xs">
            <div class="row items-center justify-between q-mb-xs">
              <span class="text-caption">After</span>
              <span
                class="text-caption text-weight-bold"
                :class="getWorkloadColorClass(proposal.impact.toWorkload)"
              >
                {{ proposal.impact.toWorkload }}%
              </span>
            </div>
            <q-linear-progress
              :value="proposal.impact.toWorkload / 100"
              :color="getWorkloadColor(proposal.impact.toWorkload)"
              size="8px"
              rounded
            />
          </div>
        </div>
      </div>

      <!-- Additional Context -->
      <div v-if="proposal.impact?.currentMatch || proposal.impact?.newMatch" class="q-mt-sm">
        <q-banner dense class="bg-blue-1 text-blue-9">
          <template v-slot:avatar>
            <q-icon name="psychology" color="blue" />
          </template>
          <div class="text-caption">
            <strong>Skill Match:</strong>
            {{ proposal.impact.currentMatch }} → {{ proposal.impact.newMatch }}
          </div>
        </q-banner>
      </div>
    </div>

    <!-- Sprint Move Details -->
    <div v-else-if="proposal.type === 'sprint_move' || proposal.type === 'cross_sprint_dep'">
      <div class="text-subtitle2 text-weight-bold q-mb-sm">Sprint Move:</div>
      <div class="q-mb-md">
        <strong>Task:</strong> {{ proposal.taskName || 'Task' }}
        <span v-if="proposal.taskSp" class="text-primary text-weight-bold"
          >({{ proposal.taskSp }} SP)</span
        >
      </div>
      <div class="q-mb-sm">
        <div class="text-caption text-grey-7 q-mb-xs">Sprint Reassignment</div>
        <div class="row items-center q-gutter-sm">
          <q-chip color="grey-5" text-color="white" dense icon="event">
            {{ proposal.fromSprintName || 'Sprint' }}
          </q-chip>
          <q-icon name="arrow_forward" size="24px" color="primary" />
          <q-chip color="primary" text-color="white" dense icon="event">
            {{ proposal.toSprintName || 'Target Sprint' }}
          </q-chip>
        </div>
      </div>

      <!-- Sprint Utilization if available -->
      <div
        v-if="proposal.impact?.fromSprintNewUtilization || proposal.impact?.toSprintNewUtilization"
        class="q-mt-sm"
      >
        <div class="text-caption text-grey-7 q-mb-xs">Sprint Utilization Impact</div>
        <div v-if="proposal.impact?.fromSprintNewUtilization" class="q-mb-xs">
          <div class="row items-center justify-between">
            <span class="text-caption">{{ proposal.fromSprintName }} (After Move)</span>
            <span class="text-caption text-weight-bold"
              >{{ proposal.impact.fromSprintNewUtilization }}%</span
            >
          </div>
        </div>
        <div v-if="proposal.impact?.toSprintNewUtilization" class="q-mb-xs">
          <div class="row items-center justify-between">
            <span class="text-caption">{{ proposal.toSprintName }} (After Move)</span>
            <span class="text-caption text-weight-bold"
              >{{ proposal.impact.toSprintNewUtilization }}%</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- PERT Uncertainty Details -->
    <div v-else-if="proposal.type === 'pert_uncertainty'">
      <div class="text-subtitle2 text-weight-bold q-mb-sm">PERT Uncertainty Analysis:</div>

      <!-- Task Info -->
      <div class="q-mb-md">
        <strong>Task:</strong> {{ proposal.taskName || 'Task' }}
        <span v-if="proposal.taskSp" class="text-primary text-weight-bold">
          ({{ proposal.taskSp }} SP)
        </span>
      </div>

      <!-- PERT Estimates -->
      <div class="q-mb-md">
        <div class="text-caption text-grey-7 q-mb-xs">PERT Estimates (Days)</div>
        <div class="row q-gutter-sm">
          <q-chip dense color="green" text-color="white" icon="trending_down">
            Optimistic: {{ proposal.impact?.optimistic }}d
          </q-chip>
          <q-chip dense color="blue" text-color="white" icon="show_chart">
            Expected: {{ proposal.impact?.expected }}d
          </q-chip>
          <q-chip dense color="orange" text-color="white" icon="trending_up">
            Pessimistic: {{ proposal.impact?.pessimistic }}d
          </q-chip>
        </div>
      </div>

      <!-- Standard PERT Statistics -->
      <div class="q-mb-md bg-blue-1 q-pa-md" style="border-radius: 8px">
        <div class="text-weight-bold q-mb-sm">Statistical Analysis</div>

        <!-- Coefficient of Variation (main metric) -->
        <div class="q-mb-sm">
          <div class="row items-center justify-between">
            <span class="text-body2">
              <q-icon name="analytics" size="sm" class="q-mr-xs" />
              <strong>Coefficient of Variation (CV):</strong>
            </span>
            <span
              class="text-h6 text-weight-bold"
              :class="
                (proposal.impact?.coefficientOfVariation || 0) >= 33 ? 'text-red' : 'text-orange'
              "
            >
              {{ proposal.impact?.coefficientOfVariation }}%
            </span>
          </div>
          <div class="text-caption text-grey-7 q-mt-xs">
            Industry threshold: <strong>CV > 33%</strong> requires breakdown
          </div>
        </div>

        <q-separator class="q-my-sm" />

        <!-- Standard Deviation -->
        <div class="row items-center justify-between q-mb-xs">
          <span class="text-caption">Standard Deviation (σ):</span>
          <span class="text-caption text-weight-bold">{{ proposal.impact?.stdDev }}d</span>
        </div>

        <!-- Variance -->
        <div class="row items-center justify-between q-mb-xs">
          <span class="text-caption">Variance (σ²):</span>
          <span class="text-caption text-weight-bold">{{ proposal.impact?.variance }}</span>
        </div>

        <!-- Suggested Buffer -->
        <div class="row items-center justify-between">
          <span class="text-caption">Suggested Buffer:</span>
          <span class="text-caption text-weight-bold text-primary">
            {{ proposal.impact?.suggestedBuffer }}d
          </span>
        </div>
      </div>

      <!-- Confidence Intervals -->
      <div class="q-mb-md">
        <div class="text-caption text-grey-7 q-mb-sm">Confidence Intervals</div>

        <!-- 68% Confidence -->
        <div class="q-mb-sm">
          <div class="row items-center justify-between q-mb-xs">
            <span class="text-caption">
              <q-icon name="show_chart" size="xs" class="q-mr-xs" />
              68% Confidence (±1σ)
            </span>
            <span class="text-caption text-weight-bold">
              {{ proposal.impact?.conf68Lower }}d - {{ proposal.impact?.conf68Upper }}d
            </span>
          </div>
          <q-linear-progress :value="0.68" color="blue" size="6px" rounded />
        </div>

        <!-- 95% Confidence -->
        <div class="q-mb-sm">
          <div class="row items-center justify-between q-mb-xs">
            <span class="text-caption">
              <q-icon name="trending_flat" size="xs" class="q-mr-xs" />
              95% Confidence (±2σ)
            </span>
            <span class="text-caption text-weight-bold">
              {{ proposal.impact?.conf95Lower }}d - {{ proposal.impact?.conf95Upper }}d
            </span>
          </div>
          <q-linear-progress :value="0.95" color="purple" size="6px" rounded />
        </div>
      </div>

      <!-- Recommendation Banner -->
      <q-banner dense class="bg-orange-1 text-orange-9">
        <template v-slot:avatar>
          <q-icon name="lightbulb" color="orange" />
        </template>
        <div class="text-caption">
          <strong>Recommendation:</strong> Break down this task into smaller subtasks for more
          accurate estimation and reduced uncertainty.
        </div>
      </q-banner>
    </div>

    <!-- Duration Risk Details (PERT+RACI) -->
    <div v-else-if="proposal.type === 'duration_risk'">
      <div class="text-subtitle2 text-weight-bold q-mb-sm">Duration Risk Analysis:</div>

      <!-- Task Info -->
      <div class="q-mb-md">
        <strong>Task:</strong> {{ proposal.taskName || 'Task' }}
        <span v-if="proposal.taskSp" class="text-primary text-weight-bold">
          ({{ proposal.taskSp }} SP)
        </span>
      </div>

      <!-- Duration Comparison -->
      <div class="q-mb-md">
        <div class="text-caption text-grey-7 q-mb-xs">Duration Analysis</div>
        <div class="row q-gutter-sm">
          <q-chip dense color="blue" text-color="white" icon="schedule">
            PERT: {{ proposal.impact?.pertDuration }}d
          </q-chip>
          <q-icon name="arrow_forward" size="sm" />
          <q-chip dense color="red" text-color="white" icon="schedule_send">
            Adjusted: {{ proposal.impact?.adjustedDuration }}d
          </q-chip>
          <q-chip dense color="orange" text-color="white" icon="trending_up">
            +{{ proposal.impact?.overhead }}%
          </q-chip>
        </div>
      </div>

      <!-- If there's a reassignment suggestion with new duration -->
      <div
        v-if="proposal.impact?.newAdjustedDuration"
        class="q-mb-md bg-green-1 q-pa-md"
        style="border-radius: 8px"
      >
        <div class="text-weight-bold q-mb-xs">
          <q-icon name="check_circle" color="green" class="q-mr-xs" />
          Proposed Solution: Reassignment
        </div>
        <div class="row items-center justify-between q-mb-xs">
          <span class="text-caption">New Adjusted Duration:</span>
          <span class="text-caption text-weight-bold text-green">
            {{ proposal.impact.newAdjustedDuration }}d
          </span>
        </div>
        <div class="row items-center justify-between">
          <span class="text-caption">New Overhead:</span>
          <span class="text-caption text-weight-bold text-green">
            {{ proposal.impact.newOverhead }}%
          </span>
        </div>
        <div class="row items-center justify-between q-mt-sm">
          <span class="text-caption text-weight-bold">Improvement:</span>
          <span class="text-caption text-weight-bold text-primary">
            -{{ proposal.impact.improvement }}d
          </span>
        </div>
      </div>

      <!-- Overloaded Members -->
      <div
        v-if="proposal.impact?.overloadedMembers && proposal.impact.overloadedMembers.length > 0"
        class="q-mb-md"
      >
        <div class="text-caption text-grey-7 q-mb-xs">Overloaded Team Members:</div>
        <div class="row q-gutter-xs">
          <q-chip
            v-for="(member, idx) in proposal.impact.overloadedMembers"
            :key="idx"
            dense
            color="red"
            text-color="white"
            icon="person"
          >
            {{ member }}
          </q-chip>
        </div>
      </div>
    </div>

    <!-- RACI Overload Details -->
    <div v-else-if="proposal.type === 'raci_overload'">
      <div class="text-subtitle2 text-weight-bold q-mb-sm">RACI Overload:</div>

      <!-- Task Info -->
      <div class="q-mb-md">
        <strong>Task:</strong> {{ proposal.taskName || 'Task' }}
        <span v-if="proposal.taskSp" class="text-primary text-weight-bold">
          ({{ proposal.taskSp }} SP)
        </span>
      </div>

      <!-- Member Info (if applicable) -->
      <div v-if="proposal.impact?.member" class="q-mb-md">
        <div class="text-caption text-grey-7 q-mb-xs">Affected Member</div>
        <div class="row items-center q-gutter-sm">
          <q-avatar color="red" text-color="white" size="32px">
            <q-icon name="person" />
          </q-avatar>
          <div>
            <div class="text-body2 text-weight-bold">{{ proposal.impact.member }}</div>
            <div class="text-caption text-grey-7">{{ proposal.impact.roleChange }}</div>
          </div>
        </div>
      </div>

      <!-- Workload visualization if available -->
      <div v-if="proposal.impact?.currentWorkload !== undefined">
        <div class="text-caption text-grey-7 q-mb-xs">Workload Impact</div>
        <div class="q-mb-xs">
          <div class="row items-center justify-between q-mb-xs">
            <span class="text-caption">Current</span>
            <span class="text-caption text-weight-bold text-red">
              {{ proposal.impact.currentWorkload }}%
            </span>
          </div>
          <q-linear-progress
            :value="proposal.impact.currentWorkload / 100"
            color="red"
            size="8px"
            rounded
          />
        </div>
        <div v-if="proposal.impact?.newWorkload !== undefined">
          <div class="row items-center justify-between q-mb-xs">
            <span class="text-caption">After</span>
            <span
              class="text-caption text-weight-bold"
              :class="getWorkloadColorClass(proposal.impact.newWorkload)"
            >
              {{ proposal.impact.newWorkload }}%
            </span>
          </div>
          <q-linear-progress
            :value="proposal.impact.newWorkload / 100"
            :color="getWorkloadColor(proposal.impact.newWorkload)"
            size="8px"
            rounded
          />
        </div>
      </div>
    </div>

    <!-- Generic Details -->
    <div v-else>
      <div class="text-subtitle2 text-weight-bold q-mb-sm">Details:</div>
      <div v-if="proposal.taskName">
        <strong>Task:</strong> {{ proposal.taskName }}
        <span v-if="proposal.taskSp"> ({{ proposal.taskSp }} SP)</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Proposal } from 'src/stores/requirement-change-store';

interface Props {
  proposal: Proposal;
}

defineProps<Props>();

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
</script>

<style scoped>
.reassignment-member {
  text-align: center;
  min-width: 80px;
}
</style>
