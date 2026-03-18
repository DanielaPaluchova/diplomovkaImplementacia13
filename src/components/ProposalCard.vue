<template>
  <q-card
    flat
    bordered
    :class="['proposal-card', { 'proposal-selected': selected }]"
    @click="$emit('toggle')"
  >
    <q-card-section class="row items-start q-pa-md">
      <!-- Icon -->
      <div class="col-auto q-pr-md">
        <q-avatar :color="getIconColor(proposal.type)" text-color="white" size="48px">
          <q-icon :name="getProposalIcon(proposal.type)" size="28px" />
        </q-avatar>
      </div>

      <!-- Content -->
      <div class="col">
        <!-- Title with PERT+RACI badge -->
        <div class="row items-center q-mb-xs">
          <div class="text-subtitle1 text-weight-bold">{{ proposal.title }}</div>
          <q-space />
          <q-badge
            v-if="proposal.source === 'pert_raci'"
            color="purple"
            label="PERT+RACI"
            class="q-mr-sm"
          >
            <q-tooltip>Analyzed using PERT duration and RACI workload metrics</q-tooltip>
          </q-badge>
        </div>

        <!-- Description -->
        <div class="text-body2 text-grey-8 q-mb-sm">
          {{ proposal.description }}
        </div>

        <!-- Reason -->
        <div class="text-caption text-grey-7 q-mb-md">
          <q-icon name="info" size="14px" class="q-mr-xs" />
          {{ getReasonWithoutWarning(proposal.reason) }}
        </div>

        <!-- Skill Mismatch Warning (if present) -->
        <q-banner
          v-if="hasSkillWarning(proposal.reason)"
          class="bg-red-1 text-red-9 q-mb-md"
          dense
          rounded
        >
          <template v-slot:avatar>
            <q-icon name="warning" color="red" size="32px" />
          </template>
          <div class="text-weight-bold text-body2">
            {{ getWarningTitle(proposal.reason) }}
          </div>
          <div class="text-caption q-mt-xs">
            {{ getWarningText(proposal.reason) }}
          </div>
        </q-banner>

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
            <proposal-impact-details :proposal="proposal" :scope="props.scope" />
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
  scope?: string | undefined; // 'backlog' | 'current_sprint'
}

const props = defineProps<Props>();

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
    pert_uncertainty: 'schedule',
    raci_overload: 'people',
    duration_risk: 'schedule_send',
    raci_missing_responsible: 'person_add',
    raci_missing_accountable: 'verified_user',
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
    pert_uncertainty: 'orange',
    raci_overload: 'red',
    duration_risk: 'orange',
    raci_missing_responsible: 'teal',
    raci_missing_accountable: 'indigo',
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
    pert_raci: 'PERT+RACI',
  };
  return labels[category] || category;
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
    pert_uncertainty: 'PERT Uncertainty',
    raci_overload: 'RACI Overload',
    duration_risk: 'Duration Risk',
    raci_missing_responsible: 'Task without Responsible',
    raci_missing_accountable: 'Task without Accountable',
  };
  return labels[type] || type;
}

// Skill warning detection and extraction
function hasSkillWarning(reason: string): boolean {
  return reason.includes('*** SKILL MISMATCH WARNING ***') || reason.includes('*** NO SUITABLE CANDIDATE WARNING ***');
}

function getWarningTitle(reason: string): string {
  if (reason.includes('*** NO SUITABLE CANDIDATE WARNING ***')) {
    return '⚠️ NO SUITABLE CANDIDATE WARNING';
  }
  return '⚠️ SKILL MISMATCH WARNING';
}

function getWarningText(reason: string): string {
  if (!hasSkillWarning(reason)) return '';
  
  // Check for both warning types
  if (reason.includes('*** NO SUITABLE CANDIDATE WARNING ***')) {
    const parts = reason.split('*** NO SUITABLE CANDIDATE WARNING ***');
    if (parts.length < 2 || !parts[1]) return '';
    return parts[1].trim();
  }
  
  // Extract warning text (everything after the warning marker)
  const parts = reason.split('*** SKILL MISMATCH WARNING ***');
  if (parts.length < 2 || !parts[1]) return '';
  
  return parts[1].trim();
}

function getReasonWithoutWarning(reason: string): string {
  if (!hasSkillWarning(reason)) return reason;
  
  // Check for both warning types
  if (reason.includes('*** NO SUITABLE CANDIDATE WARNING ***')) {
    const parts = reason.split('\n\n*** NO SUITABLE CANDIDATE WARNING ***');
    return parts[0]?.trim() ?? reason;
  }
  
  // Return only the part before the warning
  const parts = reason.split('\n\n*** SKILL MISMATCH WARNING ***');
  return parts[0]?.trim() ?? reason;
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

/* Make skill warning banner more prominent */
.q-banner.bg-red-1 {
  border: 2px solid #ef5350;
  box-shadow: 0 2px 8px rgba(239, 83, 80, 0.3);
}
</style>

