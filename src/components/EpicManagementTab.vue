<template>
  <div>
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

    <!-- Epics Content -->
    <div v-else>
      <!-- Action Bar -->
      <div class="row items-center justify-between q-mb-lg">
        <div class="text-h6 text-weight-bold">Strategic Epics</div>
        <div class="row q-gutter-sm">
          <q-btn-toggle
            v-model="viewMode"
            :options="[
              { label: 'Grid', value: 'grid', icon: 'grid_view' },
              { label: 'Board', value: 'board', icon: 'view_column' }
            ]"
            toggle-color="primary"
            unelevated
          />
          <q-btn
            outline
            icon="filter_list"
            label="Filters"
            @click="showFilters = !showFilters"
          />
          <q-btn
            unelevated
            color="primary"
            label="Create Epic"
            icon="add"
            @click="openCreateDialog"
          />
        </div>
      </div>

      <!-- Filters Panel -->
      <q-slide-transition>
        <div v-show="showFilters" class="q-mb-lg">
          <q-card flat bordered>
            <q-card-section>
              <div class="row q-col-gutter-md">
                <!-- Status Filter -->
                <div class="col-12 col-md-3">
                  <q-select
                    v-model="filters.status"
                    :options="statusFilterOptions"
                    label="Status"
                    filled
                    dense
                    multiple
                    use-chips
                    emit-value
                    map-options
                  >
                    <template v-slot:append>
                      <q-icon 
                        v-if="filters.status.length > 0"
                        name="close" 
                        @click.stop="filters.status = []" 
                        class="cursor-pointer" 
                      />
                    </template>
                  </q-select>
                </div>
                <!-- Priority Filter -->
                <div class="col-12 col-md-3">
                  <q-select
                    v-model="filters.priority"
                    :options="priorityFilterOptions"
                    label="Priority"
                    filled
                    dense
                    multiple
                    use-chips
                    emit-value
                    map-options
                  >
                    <template v-slot:append>
                      <q-icon 
                        v-if="filters.priority.length > 0"
                        name="close" 
                        @click.stop="filters.priority = []" 
                        class="cursor-pointer" 
                      />
                    </template>
                  </q-select>
                </div>
                <!-- Owner Filter -->
                <div class="col-12 col-md-3">
                  <q-select
                    v-model="filters.ownerId"
                    :options="ownerFilterOptions"
                    label="Owner"
                    filled
                    dense
                    emit-value
                    map-options
                  >
                    <template v-slot:append>
                      <q-icon 
                        v-if="filters.ownerId"
                        name="close" 
                        @click.stop="filters.ownerId = null" 
                        class="cursor-pointer" 
                      />
                    </template>
                  </q-select>
                </div>
                <!-- Sort By -->
                <div class="col-12 col-md-3">
                  <q-select
                    v-model="sortBy"
                    :options="sortOptions"
                    label="Sort By"
                    filled
                    dense
                    emit-value
                    map-options
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-slide-transition>

      <!-- Board View -->
      <EpicBoard
        v-if="viewMode === 'board'"
        :epics="sortedEpics"
        @edit="viewEpicDetails"
        @edit-epic="openEditDialog"
        @status-change="handleStatusChange"
      />

      <!-- Grid View -->
      <div v-else class="row q-col-gutter-md">
        <div v-for="epic in sortedEpics" :key="epic.id" class="col-12 col-md-6 col-lg-4">
          <q-card 
            class="epic-card cursor-pointer" 
            @click="viewEpicDetails(epic)"
          >
            <q-card-section class="q-pa-sm">
              <!-- Header: Title + Status + Priority + Actions -->
              <div class="row items-start q-mb-xs">
                <div class="col">
                  <div class="text-subtitle2 text-weight-medium">{{ epic.name }}</div>
                </div>
                <div class="row q-gutter-xs">
                  <q-chip
                    :color="getPriorityColor(epic.priority)"
                    text-color="white"
                    size="sm"
                    dense
                  >
                    <q-icon name="priority_high" size="xs" class="q-mr-xs" />
                    {{ getPriorityLabel(epic.priority) }}
                  </q-chip>
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
                    icon="edit"
                    size="sm"
                    color="primary"
                    @click.stop="openEditDialog(epic)"
                  >
                    <q-tooltip>Edit epic</q-tooltip>
                  </q-btn>
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

              <!-- Owner -->
              <div v-if="epic.owner" class="row items-center q-mb-xs q-gutter-xs">
                <q-icon name="person" size="xs" color="grey-7" />
                <span class="text-caption text-grey-7">{{ epic.owner.name }}</span>
              </div>

              <!-- Labels/Tags -->
              <div v-if="epic.labels && epic.labels.length > 0" class="row items-center q-gutter-xs q-mb-xs">
                <q-chip
                  v-for="label in epic.labels.slice(0, 3)"
                  :key="label"
                  size="xs"
                  dense
                  color="purple-1"
                  text-color="purple-9"
                >
                  {{ label }}
                </q-chip>
                <q-chip
                  v-if="epic.labels.length > 3"
                  size="xs"
                  dense
                  color="purple-1"
                  text-color="purple-9"
                >
                  +{{ epic.labels.length - 3 }}
                </q-chip>
              </div>

              <!-- Progress Bar & Task Count -->
              <div v-if="epic.progress !== undefined || epic.tasks" class="q-mb-sm">
                <div class="row items-center justify-between q-mb-xs">
                  <span class="text-caption text-grey-7">
                    <q-icon name="task" size="xs" class="q-mr-xs" />
                    {{ getCompletedTasksCount(epic) }}/{{ getTotalTasksCount(epic) }} tasks
                  </span>
                  <span class="text-caption text-weight-medium">{{ epic.progress || 0 }}%</span>
                </div>
                <q-linear-progress
                  :value="(epic.progress || 0) / 100"
                  :color="epic.progress === 100 ? 'positive' : 'primary'"
                  size="8px"
                  rounded
                />
              </div>

              <!-- Footer: Dependencies + Business Value + Duration -->
              <div class="row items-center justify-between">
                <div class="row items-center q-gutter-xs">
                  <q-chip
                    v-if="epic.dependencies && epic.dependencies.length > 0"
                    size="sm"
                    dense
                    color="blue-1"
                    text-color="blue-9"
                  >
                    <q-icon name="link" size="xs" class="q-mr-xs" />
                    {{ epic.dependencies.length }}
                  </q-chip>
                  <div class="text-caption text-grey-7">
                    <q-icon name="trending_up" size="xs" />
                    BV: {{ epic.businessValue }}
                  </div>
                  <div v-if="epic.pert.expected" class="text-caption text-grey-7">
                    <q-icon name="schedule" size="xs" />
                    {{ epic.pert.expected.toFixed(1) }}d
                  </div>
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

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useEpicStore, type Epic } from 'src/stores/epic-store';
import EpicDialog from 'src/components/EpicDialog.vue';
import EpicBoard from 'src/components/EpicBoard.vue';

interface Props {
  projectId: number;
}

const props = defineProps<Props>();

const router = useRouter();
const $q = useQuasar();
const epicStore = useEpicStore();

const loading = ref(false);
const showEpicDialog = ref(false);
const selectedEpic = ref<Epic | undefined>(undefined);
const viewMode = ref<'grid' | 'board'>('grid');
const showFilters = ref(false);

const filters = ref({
  status: [] as string[],
  priority: [] as string[],
  ownerId: null as number | null,
});

const sortBy = ref<string>('status');

const epics = computed(() => epicStore.epics);

// Filter options
const statusFilterOptions = [
  { label: 'To Do', value: 'to_do' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
];

const priorityFilterOptions = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
];

const ownerFilterOptions = computed(() => {
  const owners = epics.value
    .filter(e => e.owner)
    .map(e => e.owner!)
    .filter((owner, index, self) => 
      self.findIndex(o => o.id === owner.id) === index
    );
  return owners.map(o => ({ label: o.name, value: o.id }));
});

const sortOptions = [
  { label: 'Status', value: 'status' },
  { label: 'Priority', value: 'priority' },
  { label: 'Business Value', value: 'businessValue' },
  { label: 'Name', value: 'name' },
  { label: 'Progress', value: 'progress' },
];

// Filtered and sorted epics
const sortedEpics = computed(() => {
  let filtered = [...epics.value];

  // Apply filters
  if (filters.value.status.length > 0) {
    filtered = filtered.filter(e => filters.value.status.includes(e.status));
  }
  if (filters.value.priority.length > 0) {
    filtered = filtered.filter(e => filters.value.priority.includes(e.priority));
  }
  if (filters.value.ownerId) {
    filtered = filtered.filter(e => e.ownerId === filters.value.ownerId);
  }

  // Apply sorting
  return filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'status': {
        const getStatusOrder = (status: string) => {
          if (status === 'in_progress') return 1;
          if (status === 'to_do' || status === 'not_started') return 2;
          if (status === 'completed') return 3;
          return 4;
        };
        return getStatusOrder(a.status) - getStatusOrder(b.status);
      }
      case 'priority': {
        const getPriorityOrder = (priority: string) => {
          if (priority === 'high') return 1;
          if (priority === 'medium') return 2;
          if (priority === 'low') return 3;
          return 4;
        };
        return getPriorityOrder(a.priority) - getPriorityOrder(b.priority);
      }
      case 'businessValue':
        return b.businessValue - a.businessValue;
      case 'name':
        return a.name.localeCompare(b.name);
      case 'progress':
        return (b.progress || 0) - (a.progress || 0);
      default:
        return 0;
    }
  });
});

onMounted(async () => {
  await loadEpics();
});

async function loadEpics() {
  loading.value = true;
  try {
    await epicStore.fetchEpics(props.projectId, true);
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

function viewEpicDetails(epic: Epic) {
  router.push({
    name: 'epic-detail',
    params: {
      projectId: props.projectId,
      epicId: epic.id
    }
  });
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
      await epicStore.deleteEpic(props.projectId, epic.id);
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

async function handleStatusChange(epicId: number, newStatus: string) {
  try {
    // Type assertion for status - we know it's valid from the board columns
    const statusValue = newStatus as Epic['status'];
    const updated = await epicStore.updateEpic(props.projectId, epicId, {
      status: statusValue
    });
    if (updated) {
      $q.notify({
        type: 'positive',
        message: 'Epic status updated',
        position: 'top',
      });
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Failed to update epic status: ${error}`,
    });
    await loadEpics();
  }
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

function getPriorityLabel(priority: string): string {
  switch (priority) {
    case 'low': return 'Low';
    case 'medium': return 'Medium';
    case 'high': return 'High';
    default: return priority;
  }
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'low': return 'green';
    case 'medium': return 'orange';
    case 'high': return 'red';
    default: return 'grey';
  }
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function getTotalTasksCount(epic: Epic): number {
  return epic.tasks?.length || 0;
}

function getCompletedTasksCount(epic: Epic): number {
  if (!epic.tasks) return 0;
  return epic.tasks.filter(t => t.status === 'Done').length;
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
