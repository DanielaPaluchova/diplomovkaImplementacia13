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

        <div v-if="proposal.impact?.fromWorkload !== undefined" class="q-mb-sm">
          <div class="row items-center justify-between q-mb-xs">
            <span class="text-caption">{{ proposal.impact.fromMember }} (Before)</span>
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

        <div
          v-if="
            proposal.impact?.toWorkload !== undefined &&
            proposal.impact?.suggestedAction !== 'move_to_backlog'
          "
          class="q-mb-sm"
        >
          <div class="row items-center justify-between q-mb-xs">
            <span class="text-caption">{{ proposal.impact.toMember }} (After)</span>
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

    <!-- Generic Details -->
    <div v-else>
      <div class="text-subtitle2 text-weight-bold q-mb-sm">Details:</div>
      <div v-if="proposal.taskName">
        <strong>Task:</strong> {{ proposal.taskName }}
        <span v-if="proposal.taskSp"> ({{ proposal.taskSp }} SP)</span>
      </div>
    </div>

    <!-- Impact Metrics (always shown) -->
    <q-separator class="q-my-md" />
    <div class="text-subtitle2 text-weight-bold q-mb-sm">
      <q-icon name="insights" size="18px" class="q-mr-xs" />
      Expected Impact:
    </div>

    <!-- Impact Description -->
    <div
      v-if="getImpactDescription(proposal.type)"
      class="q-mb-md q-pa-sm bg-blue-1 rounded-borders"
    >
      <div class="text-body2 text-blue-9">
        {{ getImpactDescription(proposal.type) }}
      </div>
    </div>

    <div class="row q-col-gutter-sm">
      <div class="col-6 col-md-3" v-if="proposal.impact?.durationChange">
        <div class="impact-metric clickable">
          <q-icon
            :name="proposal.impact.durationChange < 0 ? 'trending_down' : 'trending_up'"
            :color="proposal.impact.durationChange < 0 ? 'green' : 'red'"
            size="20px"
          />
          <div class="text-caption text-grey-7">Duration</div>
          <div class="text-body2 text-weight-bold">
            {{ proposal.impact.durationChange > 0 ? '+' : '' }}{{ proposal.impact.durationChange }}d
          </div>
          <q-tooltip class="bg-dark text-body2">
            <div class="text-weight-bold q-mb-xs">Project Duration Impact</div>
            <div>Change in estimated project completion time</div>
            <div class="q-mt-xs text-caption">
              {{ proposal.impact.durationChange < 0 ? 'Faster delivery' : 'Slower delivery' }}
            </div>
          </q-tooltip>
        </div>
      </div>

      <div class="col-6 col-md-3" v-if="proposal.impact?.workloadChange">
        <div class="impact-metric clickable">
          <q-icon
            :name="
              getWorkloadChangeValue(proposal.impact.workloadChange) < 0
                ? 'trending_down'
                : 'trending_up'
            "
            :color="getWorkloadChangeValue(proposal.impact.workloadChange) < 0 ? 'green' : 'red'"
            size="20px"
          />
          <div class="text-caption text-grey-7">Workload</div>
          <div class="text-body2 text-weight-bold">
            {{ getWorkloadChangeValue(proposal.impact.workloadChange) > 0 ? '+' : ''
            }}{{ getWorkloadChangeValue(proposal.impact.workloadChange) }}%
          </div>
          <q-tooltip class="bg-dark text-body2">
            <div class="text-weight-bold q-mb-xs">Team Workload Impact</div>
            <div>Change in average team member workload</div>
            <div class="q-mt-xs text-caption">
              {{
                getWorkloadChangeValue(proposal.impact.workloadChange) < 0
                  ? 'Reduced pressure'
                  : 'Increased pressure'
              }}
            </div>
          </q-tooltip>
        </div>
      </div>

      <div class="col-6 col-md-3" v-if="proposal.impact?.riskChange">
        <div class="impact-metric clickable">
          <q-icon
            :name="proposal.impact.riskChange < 0 ? 'trending_down' : 'trending_up'"
            :color="proposal.impact.riskChange < 0 ? 'green' : 'red'"
            size="20px"
          />
          <div class="text-caption text-grey-7">Risk</div>
          <div class="text-body2 text-weight-bold">
            {{ proposal.impact.riskChange > 0 ? '+' : '' }}{{ proposal.impact.riskChange }}
          </div>
          <q-tooltip class="bg-dark text-body2">
            <div class="text-weight-bold q-mb-xs">Risk Score Impact</div>
            <div>Change in overall project risk level</div>
            <div class="q-mt-xs text-caption">
              Scale: 0-10 ({{
                proposal.impact.riskChange < 0 ? 'Lower is better' : 'Higher is worse'
              }})
            </div>
          </q-tooltip>
        </div>
      </div>

      <div class="col-6 col-md-3" v-if="proposal.impact?.balanceChange">
        <div class="impact-metric clickable">
          <q-icon
            :name="proposal.impact.balanceChange > 0 ? 'trending_up' : 'trending_down'"
            :color="proposal.impact.balanceChange > 0 ? 'green' : 'red'"
            size="20px"
          />
          <div class="text-caption text-grey-7">Balance</div>
          <div class="text-body2 text-weight-bold">
            {{ proposal.impact.balanceChange > 0 ? '+' : '' }}{{ proposal.impact.balanceChange }}%
          </div>
          <q-tooltip class="bg-dark text-body2">
            <div class="text-weight-bold q-mb-xs">Team Balance Impact</div>
            <div>Change in workload distribution evenness</div>
            <div class="q-mt-xs text-caption">
              {{ proposal.impact.balanceChange > 0 ? 'More balanced team' : 'Less balanced team' }}
            </div>
          </q-tooltip>
        </div>
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

function getWorkloadChangeValue(
  workloadChange: { before: number; after: number } | number | undefined,
): number {
  if (!workloadChange) return 0;
  if (typeof workloadChange === 'number') return workloadChange;
  return workloadChange.after - workloadChange.before;
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

function getImpactDescription(type: string): string {
  const descriptions: Record<string, string> = {
    split:
      'Splitting this large task into smaller subtasks will improve estimation accuracy, reduce risk, and enable better parallelization of work. Smaller tasks are easier to manage and complete.',
    merge:
      'Merging these similar small tasks will improve efficiency by reducing management overhead and context switching. Combined tasks are easier to track and complete as a cohesive unit.',
    reassign:
      'Reassigning this task will improve workload distribution across the team, leading to better balance and preventing team member burnout. Work will be allocated more efficiently.',
    bottleneck:
      'Relieving this bottleneck will distribute critical tasks more evenly, reducing single points of failure and project risk. The team will be more resilient and balanced.',
    priority_conflict:
      'Resolving this priority conflict will ensure high-priority work gets appropriate attention and resources, reducing the risk of delays and improving delivery predictability.',
    deadline_risk:
      'Addressing this deadline risk will help ensure on-time delivery by prioritizing urgent work. Early action prevents last-minute rushes and quality compromises.',
    skill_mismatch:
      'Matching skills to task requirements will improve work quality, reduce completion time, and increase team member satisfaction. Better skill alignment leads to better outcomes.',
    cross_sprint_dep:
      'Fixing this cross-sprint dependency will improve sprint planning and reduce scheduling conflicts. Dependencies will be properly sequenced for smoother execution.',
    sprint_move:
      'Rebalancing sprint workload will improve team capacity utilization and prevent sprint overload. More even distribution leads to better predictability and sustainable pace.',
    parallel_opportunity:
      'Enabling parallel work will accelerate project timeline by allowing tasks to run simultaneously. Faster completion without adding resources or risk.',
    idle_resource:
      'Better utilizing available team capacity will improve resource efficiency and project velocity. Underutilized team members can contribute more effectively.',
    add_task:
      'Adding this task with optimal assignment will integrate new work smoothly while maintaining team balance and capacity constraints.',
    increase_sp:
      'Adjusting story points and assignments will ensure the team has appropriate capacity for the increased scope while maintaining healthy workload levels.',
    priority_change:
      'Changing task priority will align work with current business needs and ensure critical items receive appropriate focus and resources.',
  };

  return (
    descriptions[type] ||
    'This optimization will improve project planning, team balance, and delivery predictability through better resource allocation and risk management.'
  );
}
</script>

<style scoped>
.impact-metric {
  text-align: center;
  padding: 8px;
  border-radius: 4px;
  background: white;
  border: 1px solid #e0e0e0;
  transition: all 0.2s ease;
}

.impact-metric.clickable {
  cursor: help;
}

.impact-metric.clickable:hover {
  background: rgba(0, 0, 0, 0.02);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.reassignment-member {
  text-align: center;
  min-width: 80px;
}
</style>
