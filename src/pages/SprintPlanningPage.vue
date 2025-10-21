<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Sprint Planning</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Plan and organize your sprint</p>
        </div>
        <div class="row q-gutter-md">
          <q-btn color="primary" icon="rocket_launch" label="Start Sprint" @click="startSprint" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Project Selection & Sprint Configuration -->
      <div class="row q-col-gutter-lg q-mb-lg">
        <div class="col-12">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Sprint Configuration</div>
              <div class="row q-col-gutter-md">
                <div class="col-12 col-md-6">
                  <q-select
                    v-model="selectedProjectId"
                    :options="projectOptions"
                    label="Select Project"
                    outlined
                    dense
                    emit-value
                    map-options
                    :rules="[(val) => !!val || 'Please select a project']"
                  >
                    <template #prepend>
                      <q-icon name="folder" />
                    </template>
                  </q-select>
                </div>
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="sprintName"
                    label="Sprint Name"
                    outlined
                    dense
                    :rules="[(val) => !!val || 'Sprint name is required']"
                  >
                    <template #prepend>
                      <q-icon name="label" />
                    </template>
                  </q-input>
                </div>
                <div class="col-12">
                  <q-input
                    v-model="sprintGoal"
                    label="Sprint Goal (optional)"
                    outlined
                    dense
                    type="textarea"
                    rows="2"
                  >
                    <template #prepend>
                      <q-icon name="flag" />
                    </template>
                  </q-input>
                </div>
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="startDate"
                    label="Start Date"
                    outlined
                    dense
                    type="date"
                    :rules="[(val) => !!val || 'Start date is required']"
                  >
                    <template #prepend>
                      <q-icon name="event" />
                    </template>
                  </q-input>
                </div>
                <div class="col-12 col-md-6">
                  <q-input
                    v-model="endDate"
                    label="End Date"
                    outlined
                    dense
                    type="date"
                    :rules="[(val) => !!val || 'End date is required']"
                  >
                    <template #prepend>
                      <q-icon name="event" />
                    </template>
                  </q-input>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Sprint Info & Controls -->
      <div class="row q-gutter-lg q-mb-lg">
        <!-- Sprint Details -->
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold">{{ sprintName || 'Sprint' }}</div>
              <div class="text-grey-7">
                {{
                  startDate && endDate
                    ? `${formatDateForDisplay(startDate)} - ${formatDateForDisplay(endDate)}`
                    : 'Set dates above'
                }}
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="row q-gutter-md">
                <div class="col">
                  <div class="text-caption text-grey-7">Total Tasks</div>
                  <div class="text-h6 text-primary">{{ totalTasks }}</div>
                </div>
                <div class="col">
                  <div class="text-caption text-grey-7">Completed Tasks</div>
                  <div class="text-h6 text-green">{{ completedTasks }}</div>
                </div>
                <div class="col">
                  <div class="text-caption text-grey-7">Remaining Tasks</div>
                  <div class="text-h6 text-orange">{{ remainingTasks }}</div>
                </div>
              </div>

              <q-linear-progress
                :value="completedTasks / totalTasks"
                color="green"
                class="q-mt-md"
                style="height: 8px"
              />
              <div class="text-caption text-center q-mt-xs">
                {{ totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0 }}%
                completed
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Team Allocation -->
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold">Team Allocation</div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="column q-gutter-sm">
                <div v-for="member in teamMembers" :key="member.id" class="row items-center">
                  <q-avatar size="24px" class="q-mr-sm">
                    <img :src="member.avatar" />
                  </q-avatar>
                  <div class="col">
                    <div class="text-weight-medium">{{ member.name }}</div>
                  </div>
                  <div class="col-auto">
                    <q-chip
                      size="sm"
                      :color="
                        member.workload > 100 ? 'red' : member.workload > 80 ? 'orange' : 'green'
                      "
                      text-color="white"
                      :label="`${member.workload}%`"
                    />
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Sprint Board -->
      <div class="row q-gutter-lg">
        <!-- Backlog -->
        <div class="col-12 col-lg-6">
          <q-card class="full-height">
            <q-card-section class="bg-grey-3">
              <div class="row items-center">
                <div class="text-h6 text-weight-bold">Product Backlog</div>
                <q-space />
                <q-badge color="grey-7" :label="backlogTasks.length" />
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-sm">
              <div class="column q-gutter-sm">
                <q-card
                  v-for="task in backlogTasks"
                  :key="task.id"
                  class="task-card cursor-pointer"
                  draggable
                  @dragstart="onDragStart(task)"
                  @dragend="onDragEnd"
                >
                  <q-card-section class="q-pa-sm">
                    <div class="text-subtitle2 text-weight-medium q-mb-xs">{{ task.title }}</div>
                    <div class="text-body2 text-grey-7 q-mb-sm" style="font-size: 12px">
                      {{ task.description }}
                    </div>
                    <div class="row items-center justify-between">
                      <q-chip
                        :color="
                          task.priority.toLowerCase() === 'high'
                            ? 'red'
                            : task.priority.toLowerCase() === 'medium'
                              ? 'orange'
                              : 'green'
                        "
                        text-color="white"
                        size="sm"
                        :label="task.priority"
                      />
                      <div class="text-caption">{{ task.storyPoints }} SP</div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Sprint Backlog -->
        <div class="col-12 col-lg-6">
          <q-card
            class="full-height sprint-backlog"
            :class="{ 'drag-over': isDragOver }"
            @dragover.prevent="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
          >
            <q-card-section class="bg-primary text-white">
              <div class="row items-center">
                <div class="text-h6 text-weight-bold">Sprint Backlog</div>
                <q-space />
                <q-badge color="white" text-color="primary" :label="sprintTasks.length" />
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-sm">
              <div class="column q-gutter-sm">
                <q-card
                  v-for="task in sprintTasks"
                  :key="task.id"
                  class="task-card cursor-pointer bg-primary-1"
                >
                  <q-card-section class="q-pa-sm">
                    <div class="row items-start q-mb-sm">
                      <div class="col">
                        <div class="text-subtitle2 text-weight-medium q-mb-xs">
                          {{ task.title }}
                        </div>
                      </div>
                      <div class="col-auto">
                        <q-btn
                          flat
                          round
                          dense
                          icon="close"
                          size="sm"
                          color="grey-6"
                          @click="removeFromSprint(task.id)"
                        />
                      </div>
                    </div>
                    <div class="text-body2 text-grey-7 q-mb-sm" style="font-size: 12px">
                      {{ task.description }}
                    </div>
                    <div class="row items-center justify-between">
                      <q-chip
                        :color="
                          task.priority.toLowerCase() === 'high'
                            ? 'red'
                            : task.priority.toLowerCase() === 'medium'
                              ? 'orange'
                              : 'green'
                        "
                        text-color="white"
                        size="sm"
                        :label="task.priority"
                      />
                      <div class="text-caption">{{ task.storyPoints }} SP</div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div v-if="sprintTasks.length === 0" class="text-center text-grey-5 q-pa-lg">
                <q-icon name="timeline" size="48px" class="q-mb-md" />
                <div>Drag tasks here to add to sprint</div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore, type Task, type Sprint } from 'src/stores/project-store';

interface TeamMember {
  id: number;
  name: string;
  avatar: string;
  capacity: number;
  workload: number;
}

const $q = useQuasar();
const projectStore = useProjectStore();

// Reactive data
const isDragOver = ref(false);
const draggedTask = ref<Task | null>(null);

// Sprint configuration
const selectedProjectId = ref<number | null>(projectStore.projects[0]?.id || null);
const sprintName = ref('Sprint 1');
const sprintGoal = ref('');
const startDate = ref('');
const endDate = ref('');

// Computed project options
const projectOptions = computed(() => {
  return projectStore.projects.map((p) => ({
    label: p.name,
    value: p.id,
  }));
});

// Watch for project changes and update sprint info
watch(
  selectedProjectId,
  (newProjectId) => {
    if (newProjectId) {
      const project = projectStore.getProjectById(newProjectId);
      if (project) {
        const activeSprint = project.sprints.find((s: Sprint) => s.status === 'active');
        if (activeSprint) {
          sprintName.value = activeSprint.name;
          sprintGoal.value = activeSprint.goal;
          startDate.value = formatDateForInput(activeSprint.startDate);
          endDate.value = formatDateForInput(activeSprint.endDate);
        } else {
          // Set defaults for new sprint
          const nextSprintNumber = project.sprints.length + 1;
          sprintName.value = `Sprint ${nextSprintNumber}`;
          sprintGoal.value = '';
          startDate.value = formatDateForInput(new Date());
          const defaultEndDate = new Date();
          defaultEndDate.setDate(defaultEndDate.getDate() + 14);
          endDate.value = formatDateForInput(defaultEndDate);
        }
      }
    }
  },
  { immediate: true },
);

// Helper to format date for input
function formatDateForInput(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Helper to format date for display
function formatDateForDisplay(dateString: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  };
  return date.toLocaleDateString('en-US', options);
}

// Mock data
const teamMembers: TeamMember[] = [
  {
    id: 1,
    name: 'John Smith',
    avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
    capacity: 40,
    workload: 85,
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    capacity: 40,
    workload: 75,
  },
  {
    id: 3,
    name: 'Mike Wilson',
    avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
    capacity: 35,
    workload: 90,
  },
  {
    id: 4,
    name: 'Emma Davis',
    avatar: 'https://cdn.quasar.dev/img/avatar5.jpg',
    capacity: 30,
    workload: 60,
  },
];

// Get tasks from the selected project
const backlogTasks = computed(() => {
  if (!selectedProjectId.value) return [];
  const project = projectStore.getProjectById(selectedProjectId.value);
  if (!project) return [];

  // Get tasks that are not in any sprint (backlog)
  return project.tasks.filter((task: Task) => task.sprintId === null);
});

const sprintTasks = computed(() => {
  if (!selectedProjectId.value) return [];
  const project = projectStore.getProjectById(selectedProjectId.value);
  if (!project) return [];

  // Get the active sprint
  const activeSprint = project.sprints.find((s: Sprint) => s.status === 'active');
  if (!activeSprint) return [];

  // Get tasks that are in the active sprint
  return project.tasks.filter((task: Task) => task.sprintId === activeSprint.id);
});

// Computed
const totalTasks = computed(() => {
  return sprintTasks.value.length;
});

const completedTasks = computed(() => {
  // For now, we'll simulate some completed tasks
  // In a real app, tasks would have a status property
  return Math.floor(sprintTasks.value.length * 0.6);
});

const remainingTasks = computed(() => {
  return totalTasks.value - completedTasks.value;
});

// Methods
function onDragStart(task: Task) {
  draggedTask.value = task;
}

function onDragEnd() {
  draggedTask.value = null;
  isDragOver.value = false;
}

function onDragOver(event: DragEvent) {
  event.preventDefault();
  isDragOver.value = true;
}

function onDragLeave() {
  isDragOver.value = false;
}

function onDrop(event: DragEvent) {
  event.preventDefault();
  isDragOver.value = false;

  if (draggedTask.value && selectedProjectId.value) {
    const project = projectStore.getProjectById(selectedProjectId.value);
    if (!project) return;

    const activeSprint = project.sprints.find((s: Sprint) => s.status === 'active');
    if (!activeSprint) {
      $q.notify({
        message: 'No active sprint. Please start a sprint first.',
        color: 'warning',
        icon: 'warning',
        position: 'top',
      });
      return;
    }

    // Find the task in the project and update its sprintId
    const task = project.tasks.find((t: Task) => t.id === draggedTask.value!.id);
    if (task && task.sprintId === null) {
      task.sprintId = activeSprint.id;

      $q.notify({
        message: `Added "${task.title}" to sprint`,
        color: 'positive',
        icon: 'check',
        position: 'top',
        timeout: 1000,
      });
    }

    draggedTask.value = null;
  }
}

function removeFromSprint(taskId: number) {
  if (!selectedProjectId.value) return;

  const project = projectStore.getProjectById(selectedProjectId.value);
  if (!project) return;

  // Find the task and remove it from sprint
  const task = project.tasks.find((t: Task) => t.id === taskId);
  if (task) {
    task.sprintId = null;

    $q.notify({
      message: `Removed "${task.title}" from sprint`,
      color: 'info',
      icon: 'remove_circle',
      position: 'top',
      timeout: 1000,
    });
  }
}

function startSprint() {
  if (!selectedProjectId.value) {
    $q.notify({
      message: 'Please select a project first',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  if (sprintTasks.value.length === 0) {
    $q.notify({
      message: 'Please add tasks to the sprint before starting',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  if (!startDate.value || !endDate.value) {
    $q.notify({
      message: 'Please set start and end dates for the sprint',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  if (!sprintName.value.trim()) {
    $q.notify({
      message: 'Please provide a sprint name',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Check if there's an active sprint to update or create new one
  const project = projectStore.getProjectById(selectedProjectId.value);
  if (project) {
    const activeSprint = project.sprints.find((s: Sprint) => s.status === 'active');

    if (activeSprint) {
      // Update existing sprint
      projectStore.updateSprint(selectedProjectId.value, activeSprint.id, {
        name: sprintName.value,
        goal: sprintGoal.value,
        startDate: new Date(startDate.value),
        endDate: new Date(endDate.value),
        totalTasks: sprintTasks.value.length,
        taskIds: sprintTasks.value.map((t: Task) => t.id),
      });

      $q.notify({
        message: `Sprint "${sprintName.value}" updated with ${sprintTasks.value.length} tasks!`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
    } else {
      // Create new sprint
      projectStore.addSprint(selectedProjectId.value, {
        name: sprintName.value,
        goal: sprintGoal.value,
        startDate: new Date(startDate.value),
        endDate: new Date(endDate.value),
        status: 'active',
        totalTasks: sprintTasks.value.length,
        completedTasks: 0,
        taskIds: sprintTasks.value.map((t: Task) => t.id),
      });

      $q.notify({
        message: `Sprint "${sprintName.value}" started with ${sprintTasks.value.length} tasks!`,
        color: 'positive',
        icon: 'rocket_launch',
        position: 'top',
      });
    }
  }

  console.log('Sprint details:', {
    project: selectedProjectId.value,
    name: sprintName.value,
    goal: sprintGoal.value,
    dates: { start: startDate.value, end: endDate.value },
    tasks: sprintTasks.value,
  });
}
</script>

<style scoped>
.sprint-backlog {
  transition: all 0.3s ease;
}

.sprint-backlog.drag-over {
  border: 2px dashed var(--q-primary);
  background-color: rgba(25, 118, 210, 0.05);
}

.task-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: white;
}

.task-card:hover {
  border-color: var(--q-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}
</style>
