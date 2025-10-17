<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center">
        <q-btn flat round icon="arrow_back" @click="navigateBack" class="q-mr-md" />
        <div class="col">
          <div class="text-h5 text-weight-bold text-primary">{{ project.name }} - Kanban Board</div>
          <div class="text-caption text-grey-7">
            <span v-if="activeSprint">{{ activeSprint.name }} - {{ activeSprint.goal }}</span>
            <span v-else>No active sprint</span>
          </div>
        </div>
        <q-btn color="primary" icon="add" label="New Task" @click="showNewTaskDialog = true" />
      </div>
    </div>

    <!-- Kanban Board -->
    <div class="q-pa-lg">
      <div v-if="!activeSprint" class="text-center q-pa-xl">
        <q-icon name="view_kanban" size="64px" class="text-grey-5 q-mb-md" />
        <div class="text-h6 text-grey-7 q-mb-sm">No Active Sprint</div>
        <div class="text-caption text-grey-6 q-mb-md">Start a sprint to use the Kanban board</div>
        <q-btn color="primary" icon="play_arrow" label="Go to Sprints" @click="goToSprints" />
      </div>

      <div v-else class="kanban-board">
        <!-- Sprint Info Banner -->
        <q-banner class="bg-primary text-white q-mb-lg" rounded>
          <template v-slot:avatar>
            <q-icon name="sprint" size="lg" />
          </template>
          <div>
            <div class="text-h6 text-weight-bold">{{ activeSprint.name }}</div>
            <div class="text-body2">{{ activeSprint.goal }}</div>
            <div class="text-caption q-mt-sm">
              <q-icon name="event" size="sm" class="q-mr-xs" />
              {{ formatDate(activeSprint.startDate) }} - {{ formatDate(activeSprint.endDate) }}
            </div>
          </div>
          <template v-slot:action>
            <div class="column items-end">
              <div class="text-h4 text-weight-bold">
                {{ completedStoryPoints }} / {{ totalStoryPoints }} SP
              </div>
              <div class="text-caption">
                {{ Math.round((completedStoryPoints / totalStoryPoints) * 100) }}% Complete
              </div>
              <q-linear-progress
                :value="completedStoryPoints / totalStoryPoints"
                color="white"
                track-color="primary-dark"
                size="8px"
                class="q-mt-sm"
                style="width: 200px"
              />
            </div>
          </template>
        </q-banner>

        <div class="row q-gutter-md">
          <!-- To Do Column -->
          <div class="col">
            <q-card class="kanban-column">
              <q-card-section class="bg-grey-3">
                <div class="row items-center">
                  <div class="text-h6 text-weight-bold">To Do</div>
                  <q-space />
                  <q-chip color="grey-7" text-color="white" size="sm">
                    {{ todoTasks.length }}
                  </q-chip>
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="kanban-tasks-container">
                <draggable
                  v-model="todoTasks"
                  group="tasks"
                  @end="onTaskDrop($event, 'To Do')"
                  item-key="id"
                  class="kanban-tasks-list"
                >
                  <template #item="{ element: task }">
                    <q-card class="kanban-task-card q-mb-md" @click="editTask(task)">
                      <q-card-section>
                        <div class="text-weight-medium q-mb-sm">{{ task.name }}</div>
                        <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                        <div class="row items-center q-gutter-xs q-mb-sm">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <q-chip color="primary" text-color="white" size="sm" dense>
                            {{ task.storyPoints }} SP
                          </q-chip>
                        </div>
                        <div class="row items-center">
                          <q-avatar size="24px">
                            <img :src="task.assigneeAvatar" />
                          </q-avatar>
                          <span class="text-caption q-ml-xs">{{ task.assignee }}</span>
                        </div>
                      </q-card-section>
                    </q-card>
                  </template>
                </draggable>
              </q-card-section>
            </q-card>
          </div>

          <!-- In Progress Column -->
          <div class="col">
            <q-card class="kanban-column">
              <q-card-section class="bg-blue-1">
                <div class="row items-center">
                  <div class="text-h6 text-weight-bold text-blue">In Progress</div>
                  <q-space />
                  <q-chip color="blue" text-color="white" size="sm">
                    {{ inProgressTasks.length }}
                  </q-chip>
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="kanban-tasks-container">
                <draggable
                  v-model="inProgressTasks"
                  group="tasks"
                  @end="onTaskDrop($event, 'In Progress')"
                  item-key="id"
                  class="kanban-tasks-list"
                >
                  <template #item="{ element: task }">
                    <q-card class="kanban-task-card q-mb-md" @click="editTask(task)">
                      <q-card-section>
                        <div class="text-weight-medium q-mb-sm">{{ task.name }}</div>
                        <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                        <div class="row items-center q-gutter-xs q-mb-sm">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <q-chip color="primary" text-color="white" size="sm" dense>
                            {{ task.storyPoints }} SP
                          </q-chip>
                        </div>
                        <div class="row items-center">
                          <q-avatar size="24px">
                            <img :src="task.assigneeAvatar" />
                          </q-avatar>
                          <span class="text-caption q-ml-xs">{{ task.assignee }}</span>
                        </div>
                      </q-card-section>
                    </q-card>
                  </template>
                </draggable>
              </q-card-section>
            </q-card>
          </div>

          <!-- Done Column -->
          <div class="col">
            <q-card class="kanban-column">
              <q-card-section class="bg-green-1">
                <div class="row items-center">
                  <div class="text-h6 text-weight-bold text-green">Done</div>
                  <q-space />
                  <q-chip color="green" text-color="white" size="sm">
                    {{ doneTasks.length }}
                  </q-chip>
                </div>
              </q-card-section>
              <q-separator />
              <q-card-section class="kanban-tasks-container">
                <draggable
                  v-model="doneTasks"
                  group="tasks"
                  @end="onTaskDrop($event, 'Done')"
                  item-key="id"
                  class="kanban-tasks-list"
                >
                  <template #item="{ element: task }">
                    <q-card class="kanban-task-card q-mb-md" @click="editTask(task)">
                      <q-card-section>
                        <div class="text-weight-medium q-mb-sm text-strike">{{ task.name }}</div>
                        <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                        <div class="row items-center q-gutter-xs q-mb-sm">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <q-chip color="primary" text-color="white" size="sm" dense>
                            {{ task.storyPoints }} SP
                          </q-chip>
                        </div>
                        <div class="row items-center">
                          <q-avatar size="24px">
                            <img :src="task.assigneeAvatar" />
                          </q-avatar>
                          <span class="text-caption q-ml-xs">{{ task.assignee }}</span>
                        </div>
                      </q-card-section>
                    </q-card>
                  </template>
                </draggable>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>

    <!-- New Task Dialog -->
    <q-dialog v-model="showNewTaskDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Create New Task</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input v-model="newTask.name" label="Task Name" filled class="q-mb-md" />
          <q-input
            v-model="newTask.description"
            label="Description"
            type="textarea"
            filled
            class="q-mb-md"
          />
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="newTask.priority"
                :options="['High', 'Medium', 'Low']"
                label="Priority"
                filled
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="newTask.storyPoints"
                label="Story Points"
                type="number"
                filled
              />
            </div>
          </div>
          <q-select
            v-model="newTask.assignee"
            :options="project.teamMembers"
            option-label="name"
            label="Assignee"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Create" @click="createTask" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { format } from 'date-fns';
import draggable from 'vuedraggable';

const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const showNewTaskDialog = ref(false);

interface TeamMember {
  id: number;
  name: string;
  role: string;
  avatar: string;
}

interface Task {
  id: number;
  name: string;
  description: string;
  status: 'To Do' | 'In Progress' | 'Done';
  priority: 'High' | 'Medium' | 'Low';
  storyPoints: number;
  assignee: string;
  assigneeAvatar: string;
  sprintId: number | null;
}

interface Sprint {
  id: number;
  name: string;
  goal: string;
  startDate: Date;
  endDate: Date;
  status: 'planned' | 'active' | 'completed';
}

interface Project {
  id: number;
  name: string;
  teamMembers: TeamMember[];
}

// Mock data
const project = ref<Project>({
  id: Number(route.params.id) || 1,
  name: 'E-commerce Platform Redesign',
  teamMembers: [
    {
      id: 1,
      name: 'John Smith',
      role: 'Frontend Developer',
      avatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    },
    {
      id: 3,
      name: 'Mike Wilson',
      role: 'UI/UX Designer',
      avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    },
  ],
});

const activeSprint = ref<Sprint>({
  id: 2,
  name: 'Sprint 2',
  goal: 'Product catalog and shopping cart',
  startDate: new Date('2024-01-23'),
  endDate: new Date('2024-02-06'),
  status: 'active',
});

const allTasks = ref<Task[]>([
  {
    id: 1,
    name: 'Design landing page',
    description: 'Create modern landing page design',
    status: 'Done',
    priority: 'High',
    storyPoints: 8,
    assignee: 'Mike Wilson',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    sprintId: 2,
  },
  {
    id: 2,
    name: 'Implement authentication',
    description: 'Build login and registration flow',
    status: 'In Progress',
    priority: 'High',
    storyPoints: 13,
    assignee: 'John Smith',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    sprintId: 2,
  },
  {
    id: 3,
    name: 'Setup CI/CD pipeline',
    description: 'Configure automated deployment',
    status: 'To Do',
    priority: 'Medium',
    storyPoints: 5,
    assignee: 'John Smith',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    sprintId: 2,
  },
  {
    id: 4,
    name: 'Product catalog page',
    description: 'Build product listing with filters',
    status: 'In Progress',
    priority: 'High',
    storyPoints: 21,
    assignee: 'John Smith',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    sprintId: 2,
  },
  {
    id: 5,
    name: 'Shopping cart functionality',
    description: 'Add/remove items, update quantities',
    status: 'To Do',
    priority: 'High',
    storyPoints: 13,
    assignee: 'Mike Wilson',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    sprintId: 2,
  },
]);

const newTask = ref({
  name: '',
  description: '',
  priority: 'Medium' as 'High' | 'Medium' | 'Low',
  storyPoints: 5,
  assignee: null as TeamMember | null,
});

// Computed - filter tasks by status
const todoTasks = computed({
  get: () =>
    allTasks.value.filter((t) => t.status === 'To Do' && t.sprintId === activeSprint.value?.id),
  set: (value) => {
    // Update allTasks array
    allTasks.value = allTasks.value.filter(
      (t) => t.status !== 'To Do' || t.sprintId !== activeSprint.value?.id,
    );
    allTasks.value.push(...value);
  },
});

const inProgressTasks = computed({
  get: () =>
    allTasks.value.filter(
      (t) => t.status === 'In Progress' && t.sprintId === activeSprint.value?.id,
    ),
  set: (value) => {
    allTasks.value = allTasks.value.filter(
      (t) => t.status !== 'In Progress' || t.sprintId !== activeSprint.value?.id,
    );
    allTasks.value.push(...value);
  },
});

const doneTasks = computed({
  get: () =>
    allTasks.value.filter((t) => t.status === 'Done' && t.sprintId === activeSprint.value?.id),
  set: (value) => {
    allTasks.value = allTasks.value.filter(
      (t) => t.status !== 'Done' || t.sprintId !== activeSprint.value?.id,
    );
    allTasks.value.push(...value);
  },
});

const totalStoryPoints = computed(() => {
  const sprintTasks = allTasks.value.filter((t) => t.sprintId === activeSprint.value?.id);
  return sprintTasks.reduce((sum, t) => sum + t.storyPoints, 0);
});

const completedStoryPoints = computed(() => {
  return doneTasks.value.reduce((sum, t) => sum + t.storyPoints, 0);
});

// Methods
function formatDate(date: Date): string {
  return format(date, 'MMM d, yyyy');
}
function onTaskDrop(_event: unknown, newStatus: 'To Do' | 'In Progress' | 'Done') {
  // Task status is already updated by v-model in draggable component
  // Just show notification
  $q.notify({
    message: `Task moved to ${newStatus}`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'High':
      return 'red';
    case 'Medium':
      return 'orange';
    case 'Low':
      return 'blue';
    default:
      return 'grey';
  }
}

function editTask(task: Task) {
  console.log('Edit task:', task);
}

function createTask() {
  if (!newTask.value.assignee) {
    $q.notify({
      message: 'Please select an assignee',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  const task: Task = {
    id: Math.max(...allTasks.value.map((t) => t.id), 0) + 1,
    name: newTask.value.name,
    description: newTask.value.description,
    status: 'To Do',
    priority: newTask.value.priority,
    storyPoints: newTask.value.storyPoints,
    assignee: newTask.value.assignee.name,
    assigneeAvatar: newTask.value.assignee.avatar,
    sprintId: activeSprint.value?.id || null,
  };

  allTasks.value.push(task);

  $q.notify({
    message: 'Task created successfully',
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });

  showNewTaskDialog.value = false;
  newTask.value = {
    name: '',
    description: '',
    priority: 'Medium',
    storyPoints: 5,
    assignee: null,
  };
}

function navigateBack() {
  router.push(`/projects/${project.value.id}`);
}

function goToSprints() {
  router.push(`/projects/${project.value.id}?tab=sprints`);
}
</script>

<style scoped>
.kanban-board {
  min-height: calc(100vh - 200px);
}

.kanban-column {
  height: calc(100vh - 250px);
  display: flex;
  flex-direction: column;
}

.kanban-tasks-container {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

.kanban-tasks-list {
  min-height: 100px;
}

.kanban-task-card {
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.kanban-task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.text-strike {
  text-decoration: line-through;
}
</style>
