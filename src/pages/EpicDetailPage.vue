<template>
  <q-page class="q-pa-lg">
    <div v-if="loading" class="row justify-center q-py-xl">
      <q-spinner color="primary" size="50px" />
    </div>

    <div v-else-if="!epic" class="row justify-center q-py-xl">
      <div class="text-center">
        <q-icon name="error" size="80px" color="grey-5" />
        <div class="text-h6 text-grey-7 q-mt-md">Epic not found</div>
        <q-btn
          flat
          label="Go Back"
          color="primary"
          icon="arrow_back"
          @click="router.back()"
          class="q-mt-md"
        />
      </div>
    </div>

    <div v-else>
      <!-- Header -->
      <div class="row items-start q-mb-lg">
        <q-btn
          flat
          round
          icon="arrow_back"
          @click="router.back()"
          class="q-mr-md"
        />
        <div class="col">
          <div class="row items-center q-gutter-sm q-mb-sm">
            <h4 class="text-h4 q-ma-none">{{ epic.name }}</h4>
            <q-chip
              :color="getStatusColor(epic.status)"
              text-color="white"
            >
              {{ getStatusLabel(epic.status) }}
            </q-chip>
            <q-chip
              :color="getPriorityColor(epic.priority)"
              text-color="white"
            >
              <q-icon name="priority_high" size="xs" class="q-mr-xs" />
              {{ getPriorityLabel(epic.priority) }}
            </q-chip>
          </div>
          <p v-if="epic.description" class="text-body1 text-grey-7 q-ma-none">
            {{ epic.description }}
          </p>
        </div>
        <q-btn
          outline
          color="primary"
          label="Edit Epic"
          icon="edit"
          @click="editEpic"
        />
      </div>

      <!-- Info Cards -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey-7">Owner</div>
              <div class="text-h6">
                {{ epic.owner ? epic.owner.name : 'Unassigned' }}
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey-7">Business Value</div>
              <div class="text-h6">{{ epic.businessValue }}</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey-7">Expected Duration</div>
              <div class="text-h6">
                {{ epic.pert.expected ? epic.pert.expected.toFixed(1) + ' days' : 'N/A' }}
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-caption text-grey-7">Progress</div>
              <div class="text-h6">{{ epic.progress || 0 }}%</div>
              <q-linear-progress
                :value="(epic.progress || 0) / 100"
                :color="epic.progress === 100 ? 'positive' : 'primary'"
                size="8px"
                rounded
                class="q-mt-sm"
              />
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Labels & Dates -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-6" v-if="epic.labels && epic.labels.length > 0">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-subtitle2 q-mb-sm">Labels</div>
              <div class="row q-gutter-xs">
                <q-chip
                  v-for="label in epic.labels"
                  :key="label"
                  color="purple-1"
                  text-color="purple-9"
                >
                  {{ label }}
                </q-chip>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Tasks List -->
      <q-card flat bordered>
        <q-card-section class="bg-grey-2">
          <div class="row items-center justify-between">
            <div class="text-h6">
              Tasks
              <q-badge color="primary" :label="tasks.length" class="q-ml-sm" />
            </div>
            <div class="text-caption text-grey-7">
              {{ completedTasks }} / {{ tasks.length }} completed
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section v-if="tasks.length === 0">
          <div class="text-center text-grey-7 q-py-md">
            <q-icon name="info" size="48px" class="q-mb-sm" />
            <div>No tasks in this epic yet</div>
          </div>
        </q-card-section>
        <q-list v-else separator>
          <q-item
            v-for="task in tasks"
            :key="task.id"
            clickable
            @click="viewTask(task)"
          >
            <q-item-section>
              <q-item-label>{{ task.name || task.title }}</q-item-label>
              <q-item-label caption>
                {{ task.description }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <div class="row items-center q-gutter-sm">
                <q-chip
                  size="sm"
                  :color="getTaskStatusColor(task.status)"
                  text-color="white"
                  dense
                >
                  {{ task.status }}
                </q-chip>
                <q-chip
                  v-if="task.storyPoints"
                  size="sm"
                  color="blue-1"
                  text-color="blue-9"
                  dense
                >
                  {{ task.storyPoints }} SP
                </q-chip>
              </div>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>

    <!-- Edit Epic Dialog -->
    <EpicDialog
      v-if="showEpicDialog"
      v-model="showEpicDialog"
      :project-id="projectId"
      :epic="epic"
      :existing-epics="[]"
      @updated="handleEpicUpdated"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEpicStore } from 'src/stores/epic-store';
import type { Task } from 'src/stores/project-store';
import EpicDialog from 'src/components/EpicDialog.vue';

const route = useRoute();
const router = useRouter();
const epicStore = useEpicStore();

const loading = ref(false);
const showEpicDialog = ref(false);

const projectId = computed(() => parseInt(route.params.projectId as string));
const epicId = computed(() => parseInt(route.params.epicId as string));

const epic = computed(() => epicStore.epics.find(e => e.id === epicId.value));
const tasks = computed(() => epic.value?.tasks || []);
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'Done').length);

onMounted(async () => {
  await loadEpic();
});

async function loadEpic() {
  loading.value = true;
  try {
    await epicStore.getEpic(projectId.value, epicId.value, true);
  } catch (error) {
    console.error('Failed to load epic:', error);
  } finally {
    loading.value = false;
  }
}

function editEpic() {
  showEpicDialog.value = true;
}

function handleEpicUpdated() {
  showEpicDialog.value = false;
  loadEpic();
}

function viewTask(task: Task) {
  router.push({
    name: 'project-detail',
    params: { id: projectId.value },
    query: { taskId: task.id }
  });
}

function getStatusLabel(status: string): string {
  if (status === 'to_do' || status === 'not_started') return 'To Do';
  if (status === 'in_progress') return 'In Progress';
  if (status === 'completed') return 'Completed';
  return status;
}

function getStatusColor(status: string): string {
  if (status === 'to_do' || status === 'not_started') return 'grey';
  if (status === 'in_progress') return 'primary';
  if (status === 'completed') return 'positive';
  return 'grey';
}

function getPriorityLabel(priority: string): string {
  if (priority === 'low') return 'Low';
  if (priority === 'medium') return 'Medium';
  if (priority === 'high') return 'High';
  return priority;
}

function getPriorityColor(priority: string): string {
  if (priority === 'low') return 'green';
  if (priority === 'medium') return 'orange';
  if (priority === 'high') return 'red';
  return 'grey';
}

function getTaskStatusColor(status: string): string {
  switch (status) {
    case 'To Do': return 'grey';
    case 'In Progress': return 'primary';
    case 'Done': return 'positive';
    case 'Blocked': return 'negative';
    default: return 'grey';
  }
}
</script>
