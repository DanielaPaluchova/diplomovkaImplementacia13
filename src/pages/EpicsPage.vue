<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-primary text-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <q-btn flat round icon="arrow_back" color="white" @click="navigateBack" />
        <div class="col">
          <h4 class="text-h4 text-weight-bold q-ma-none">Epic Planning</h4>
          <p class="q-ma-none q-mt-sm">
            Strategic planning with epics for {{ project?.name }}
          </p>
        </div>
        <q-btn unelevated color="white" text-color="primary" label="Create Epic" icon="add" @click="openCreateDialog" />
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Loading State -->
      <div v-if="loading" class="row justify-center q-py-xl">
        <q-spinner color="primary" size="50px" />
      </div>

      <!-- Empty State -->
      <div v-else-if="epics.length === 0" class="row justify-center q-py-xl">
        <div class="text-center">
          <q-icon name="star_border" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">No epics yet</div>
          <div class="text-body2 text-grey-6 q-mt-sm">
            Create your first epic to start strategic planning
          </div>
          <q-btn
            unelevated
            color="primary"
            label="Create Epic"
            icon="add"
            class="q-mt-md"
            @click="openCreateDialog"
          />
        </div>
      </div>

      <!-- Epics Grid -->
      <div v-else class="row q-col-gutter-md">
        <div v-for="epic in sortedEpics" :key="epic.id" class="col-12 col-md-6 col-lg-4">
          <q-card 
            class="epic-card cursor-pointer" 
            @click="openEditDialog(epic)"
          >
            <q-card-section class="q-pa-sm">
              <!-- Header: Title + Status Badge + Delete -->
              <div class="row items-start q-mb-xs">
                <div class="col">
                  <div class="text-subtitle2 text-weight-medium">{{ epic.name }}</div>
                </div>
                <div class="row q-gutter-xs">
                  <q-chip
                    :color="getStatusColor(epic.status)"
                    text-color="white"
                    size="sm"
                    dense
                  >
                    {{ getStatusLabel(epic.status) }}
                  </q-chip>
                  <q-btn
                    flat
                    round
                    dense
                    icon="delete"
                    size="sm"
                    color="negative"
                    @click.stop="confirmDelete(epic)"
                  >
                    <q-tooltip>Delete epic</q-tooltip>
                  </q-btn>
                </div>
              </div>

              <!-- Description -->
              <div class="text-caption text-grey-7 q-mb-sm" v-if="epic.description">
                {{ truncateText(epic.description, 100) }}
              </div>

              <!-- Labels row: Dependencies + Business Value -->
              <div class="row items-center justify-between q-mb-xs">
                <div class="row items-center q-gutter-xs">
                  <q-chip
                    v-for="depId in (epic.dependencies || []).slice(0, 2)"
                    :key="depId"
                    size="sm"
                    dense
                    color="blue-1"
                    text-color="blue-9"
                  >
                    {{ getEpicName(depId) }}
                  </q-chip>
                  <q-chip
                    v-if="epic.dependencies && epic.dependencies.length > 2"
                    size="sm"
                    dense
                    color="blue-1"
                    text-color="blue-9"
                  >
                    +{{ epic.dependencies.length - 2 }}
                  </q-chip>
                </div>
                <div class="text-caption text-weight-medium">
                  BV: {{ epic.businessValue }}
                </div>
              </div>

              <!-- Footer: Expected duration -->
              <div class="row items-center justify-between">
                <div v-if="epic.pert.expected" class="text-caption text-grey-7">
                  <q-icon name="schedule" size="xs" class="q-mr-xs" />
                  {{ epic.pert.expected.toFixed(1) }} days
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

    </div>

    <!-- Epic Dialog -->
    <EpicDialog
      v-if="showEpicDialog"
      v-model="showEpicDialog"
      :project-id="projectId"
      :epic="selectedEpic"
      :existing-epics="epics"
      @created="handleEpicCreated"
      @updated="handleEpicUpdated"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useEpicStore, type Epic } from 'src/stores/epic-store';
import { useProjectStore } from 'src/stores/project-store';
import EpicDialog from 'src/components/EpicDialog.vue';
// Epic Planning Page

const route = useRoute();
const router = useRouter();
const $q = useQuasar();
const epicStore = useEpicStore();
const projectStore = useProjectStore();

const projectId = computed(() => parseInt(route.params.id as string));
const project = computed(() => projectStore.getProjectById(projectId.value));

const loading = ref(false);
const showEpicDialog = ref(false);
const selectedEpic = ref<Epic | undefined>(undefined);

const epics = computed(() => epicStore.epics);

// Sort epics by business value (descending) and then by status
const sortedEpics = computed(() => {
  return [...epics.value].sort((a, b) => {
    // First by status (in_progress > to_do/not_started > completed)
    const getStatusOrder = (status: string) => {
      if (status === 'in_progress') return 1;
      if (status === 'to_do' || status === 'not_started') return 2;
      if (status === 'completed') return 3;
      return 4;
    };
    const statusDiff = getStatusOrder(a.status) - getStatusOrder(b.status);
    if (statusDiff !== 0) return statusDiff;

    // Then by business value (descending)
    return b.businessValue - a.businessValue;
  });
});

onMounted(async () => {
  await loadEpics();
});

async function loadEpics() {
  loading.value = true;
  try {
    await epicStore.fetchEpics(projectId.value, true);
  } catch (error) {
    console.error('Failed to load epics:', error);
  } finally {
    loading.value = false;
  }
}

function openCreateDialog() {
  selectedEpic.value = undefined;
  showEpicDialog.value = true;
}

function openEditDialog(epic: Epic) {
  selectedEpic.value = epic;
  showEpicDialog.value = true;
}

function handleEpicCreated() {
  loadEpics();
}

function handleEpicUpdated() {
  loadEpics();
}

function confirmDelete(epic: Epic) {
  $q.dialog({
    title: 'Delete Epic',
    message: `Are you sure you want to delete "${epic.name}"? Tasks in this epic will remain but will no longer be associated with it.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await epicStore.deleteEpic(projectId.value, epic.id);
      $q.notify({
        type: 'positive',
        message: 'Epic deleted successfully',
      });
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: `Failed to delete epic: ${error}`,
      });
    }
  });
}

function navigateBack() {
  router.push({ name: 'project-detail', params: { id: projectId.value } });
}

function getEpicName(epicId: number): string {
  const epic = epics.value.find((e) => e.id === epicId);
  return epic?.name || `Epic #${epicId}`;
}

function getStatusColor(status: string): string {
  if (status === 'to_do' || status === 'not_started') {
    return 'grey';
  }
  switch (status) {
    case 'in_progress':
      return 'blue';
    case 'completed':
      return 'green';
    default:
      return 'grey';
  }
}

function getStatusLabel(status: string): string {
  if (status === 'to_do' || status === 'not_started') {
    return 'To Do';
  }
  switch (status) {
    case 'in_progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    default:
      return status;
  }
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}
</script>

<style scoped lang="scss">
.epic-card {
  transition: all 0.2s ease;
  border-left: 3px solid transparent;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
}
</style>
