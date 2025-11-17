<template>
  <div class="optimization-proposals">
    <!-- Header with actions -->
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h6 text-weight-bold">
        Optimization Opportunities ({{ proposals.length }})
      </div>
      <div class="row q-gutter-sm">
        <q-btn
          flat
          color="primary"
          label="Select All"
          size="sm"
          @click="$emit('select-all')"
          icon="check_box"
        />
        <q-btn
          flat
          color="grey"
          label="Deselect All"
          size="sm"
          @click="$emit('deselect-all')"
          icon="check_box_outline_blank"
        />
      </div>
    </div>

    <!-- Critical Proposals -->
    <div v-if="criticalProposals.length > 0" class="q-mb-lg">
      <div class="category-header bg-red-1 q-pa-md">
        <q-icon name="error" color="red" size="24px" class="q-mr-sm" />
        <span class="text-h6 text-weight-bold text-red">Critical ({{ criticalProposals.length }})</span>
        <span class="text-caption text-grey-7 q-ml-sm">- Requires immediate attention</span>
      </div>
      <div class="proposals-list">
        <proposal-card
          v-for="proposal in criticalProposals"
          :key="proposal.id"
          :proposal="proposal"
          :selected="isSelected(proposal.id)"
          :scope="props.scope"
          @toggle="$emit('toggle-selection', proposal.id)"
        />
      </div>
    </div>

    <!-- Important Proposals -->
    <div v-if="importantProposals.length > 0" class="q-mb-lg">
      <div class="category-header bg-orange-1 q-pa-md">
        <q-icon name="warning" color="orange" size="24px" class="q-mr-sm" />
        <span class="text-h6 text-weight-bold text-orange">Important ({{ importantProposals.length }})</span>
        <span class="text-caption text-grey-7 q-ml-sm">- Should be addressed</span>
      </div>
      <div class="proposals-list">
        <proposal-card
          v-for="proposal in importantProposals"
          :key="proposal.id"
          :proposal="proposal"
          :selected="isSelected(proposal.id)"
          :scope="props.scope"
          @toggle="$emit('toggle-selection', proposal.id)"
        />
      </div>
    </div>

    <!-- Recommended Proposals -->
    <div v-if="recommendedProposals.length > 0" class="q-mb-lg">
      <div class="category-header bg-blue-1 q-pa-md">
        <q-icon name="lightbulb" color="blue" size="24px" class="q-mr-sm" />
        <span class="text-h6 text-weight-bold text-blue">Recommended ({{ recommendedProposals.length }})</span>
        <span class="text-caption text-grey-7 q-ml-sm">- Nice to have</span>
      </div>
      <div class="proposals-list">
        <proposal-card
          v-for="proposal in recommendedProposals"
          :key="proposal.id"
          :proposal="proposal"
          :selected="isSelected(proposal.id)"
          :scope="props.scope"
          @toggle="$emit('toggle-selection', proposal.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineOptions } from 'vue';
import type { Proposal } from 'src/stores/requirement-change-store';
import ProposalCard from './ProposalCard.vue';

defineOptions({
  name: 'OptimizationProposals'
});

interface Props {
  proposals: Proposal[];
  selectedProposals: string[];
  scope?: string | undefined; // 'backlog' | 'current_sprint'
}

const props = defineProps<Props>();

defineEmits<{
  (e: 'toggle-selection', id: string): void;
  (e: 'select-all'): void;
  (e: 'deselect-all'): void;
}>();

const criticalProposals = computed(() =>
  props.proposals.filter((p) => p.severity === 'critical')
);

const importantProposals = computed(() =>
  props.proposals.filter((p) => p.severity === 'important')
);

const recommendedProposals = computed(() =>
  props.proposals.filter((p) => p.severity === 'recommended')
);

function isSelected(id: string): boolean {
  return props.selectedProposals.includes(id);
}
</script>

<style scoped>
.category-header {
  border-radius: 8px 8px 0 0;
  border-left: 4px solid currentColor;
}

.proposals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 0 0 8px 8px;
  border: 1px solid #e0e0e0;
  border-top: none;
}
</style>

