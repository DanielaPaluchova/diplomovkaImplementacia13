<template>
  <q-card
    flat
    bordered
    :class="['proposal-card', { 'proposal-selected': selected }]"
    @click="$emit('toggle')"
  >
    <q-card-section class="row items-start q-pa-md">
      <!-- Checkbox -->
      <div class="col-auto q-pr-md">
        <q-checkbox :model-value="selected" color="primary" size="md" />
      </div>

      <!-- Icon -->
      <div class="col-auto q-pr-md">
        <q-avatar :color="getIconColor(proposal.type)" text-color="white" size="48px">
          <q-icon :name="getProposalIcon(proposal.type)" size="28px" />
        </q-avatar>
      </div>

      <!-- Content -->
      <div class="col">
        <!-- Title with score -->
        <div class="row items-center q-mb-xs">
          <div class="text-subtitle1 text-weight-bold">{{ proposal.title }}</div>
          <q-space />
          <q-chip
            :color="getScoreColor(proposal.score)"
            text-color="white"
            size="sm"
            dense
          >
            {{ proposal.score }}
          </q-chip>
        </div>

        <!-- Description -->
        <div class="text-body2 text-grey-8 q-mb-sm">
          {{ proposal.description }}
        </div>

        <!-- Reason -->
        <div class="text-caption text-grey-7 q-mb-md">
          <q-icon name="info" size="14px" class="q-mr-xs" />
          {{ proposal.reason }}
        </div>

        <!-- Category & Severity badges -->
        <div class="row q-gutter-xs q-mb-sm">
          <q-badge :color="getSeverityColor(proposal.severity)" :label="getSeverityLabel(proposal.severity)" />
          <q-badge color="grey-6" :label="getCategoryLabel(proposal.category)" />
          <q-badge color="blue-grey-5" :label="getTypeLabel(proposal.type)" />
        </div>

        <!-- Impact Preview -->
        <q-expansion-item
          dense
          label="View Impact Details"
          class="impact-expansion"
          header-class="text-caption text-primary"
        >
          <q-card flat class="bg-grey-1 q-pa-md q-mt-sm">
            <proposal-impact-details :proposal="proposal" />
          </q-card>
        </q-expansion-item>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import type { Proposal } from 'src/stores/requirement-change-store';
import ProposalImpactDetails from './ProposalImpactDetails.vue';

interface Props {
  proposal: Proposal;
  selected: boolean;
}

defineProps<Props>();

defineEmits<{
  (e: 'toggle'): void;
}>();

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

function getIconColor(type: string): string {
  const colors: Record<string, string> = {
    split: 'orange',
    merge: 'blue',
    reassign: 'green',
    sprint_move: 'purple',
    bottleneck: 'red',
    priority_conflict: 'red',
    deadline_risk: 'red',
    skill_mismatch: 'orange',
    cross_sprint_dep: 'orange',
    parallel_opportunity: 'blue',
    idle_resource: 'yellow-8',
  };
  return colors[type] || 'grey';
}

function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    critical: 'red',
    important: 'orange',
    recommended: 'blue',
  };
  return colors[severity] || 'grey';
}

function getSeverityLabel(severity: string): string {
  const labels: Record<string, string> = {
    critical: 'Critical',
    important: 'Important',
    recommended: 'Recommended',
  };
  return labels[severity] || severity;
}

function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    workload: 'Workload',
    quality: 'Quality',
    timeline: 'Timeline',
    resources: 'Resources',
  };
  return labels[category] || category;
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'green';
  if (score >= 60) return 'light-green';
  if (score >= 40) return 'orange';
  return 'red';
}

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    split: 'Task Split',
    merge: 'Task Merge',
    reassign: 'Reassignment',
    sprint_move: 'Sprint Move',
    bottleneck: 'Bottleneck',
    priority_conflict: 'Priority',
    deadline_risk: 'Deadline',
    skill_mismatch: 'Skills',
    cross_sprint_dep: 'Dependencies',
    parallel_opportunity: 'Parallel',
    idle_resource: 'Resources',
  };
  return labels[type] || type;
}
</script>

<style scoped>
.proposal-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.proposal-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.proposal-selected {
  border-color: var(--q-primary);
  background-color: rgba(25, 118, 210, 0.05);
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
}

.impact-expansion {
  background: transparent;
}
</style>

