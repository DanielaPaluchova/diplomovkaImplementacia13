<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Kanban Board</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Visual task management with drag & drop interface
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-select
            v-model="selectedProject"
            :options="projectOptions"
            label="Project"
            filled
            dense
            style="min-width: 200px"
          />
          <q-btn
            color="secondary"
            icon="view_week"
            label="Add Column"
            @click="showAddColumnDialog = true"
          />
          <q-btn
            color="primary"
            icon="add_task"
            label="Add Task"
            @click="showAddTaskDialog = true"
          />
        </div>
      </div>
    </div>

    <div class="kanban-container q-pa-lg">
      <div class="kanban-board">
        <div
          v-for="column in kanbanColumns"
          :key="column.id"
          class="kanban-column"
          @dragover.prevent="onDragOver"
          @drop="onDrop($event, column.id)"
        >
          <!-- Column Header -->
          <div class="column-header" :class="`bg-${column.color}-1`">
            <div class="row items-center">
              <q-icon
                :name="column.icon"
                :class="`text-${column.color}`"
                size="20px"
                class="q-mr-sm"
              />
              <div class="col">
                <div class="text-subtitle1 text-weight-bold">{{ column.title }}</div>
                <div class="text-caption text-grey-7">
                  {{ getTasksInColumn(column.id).length }} tasks
                </div>
              </div>
              <q-btn flat round dense icon="more_vert" size="sm" @click="showColumnMenu(column)">
                <q-menu>
                  <q-list>
                    <q-item clickable @click="editColumn(column)">
                      <q-item-section avatar>
                        <q-icon name="edit" />
                      </q-item-section>
                      <q-item-section>Edit Column</q-item-section>
                    </q-item>
                    <q-item clickable @click="deleteColumn(column)">
                      <q-item-section avatar>
                        <q-icon name="delete" />
                      </q-item-section>
                      <q-item-section>Delete Column</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-btn>
            </div>
          </div>

          <!-- Tasks -->
          <div class="column-content">
            <div
              v-for="task in getTasksInColumn(column.id)"
              :key="task.id"
              class="kanban-task"
              draggable="true"
              @dragstart="onDragStart($event, task)"
              @dragend="onDragEnd"
            >
              <div class="task-header q-mb-sm">
                <div class="row items-center">
                  <q-chip
                    :color="getPriorityColor(task.priority)"
                    text-color="white"
                    size="xs"
                    :label="task.priority"
                  />
                  <q-space />
                  <q-chip
                    :color="getTypeColor(task.type)"
                    text-color="white"
                    size="xs"
                    :icon="getTypeIcon(task.type)"
                    :label="task.type"
                  />
                </div>
              </div>

              <div class="text-subtitle2 text-weight-medium q-mb-xs">{{ task.title }}</div>
              <div class="text-body2 text-grey-7 q-mb-sm" style="font-size: 12px">
                {{ task.description }}
              </div>

              <!-- Labels -->
              <div class="row q-gutter-xs q-mb-sm" v-if="task.labels.length">
                <q-chip
                  v-for="label in task.labels.slice(0, 2)"
                  :key="label"
                  size="xs"
                  outline
                  color="grey-6"
                  :label="label"
                />
                <q-chip
                  v-if="task.labels.length > 2"
                  size="xs"
                  outline
                  color="grey-6"
                  :label="`+${task.labels.length - 2}`"
                />
              </div>

              <!-- Task Footer -->
              <div class="row items-center justify-between">
                <div class="row items-center q-gutter-xs">
                  <q-icon name="functions" size="12px" />
                  <span class="text-caption text-weight-bold">{{ task.storyPoints }} SP</span>
                </div>
                <q-avatar v-if="task.assignee" size="20px">
                  <img :src="getAssigneeAvatar(task.assignee)" />
                  <q-tooltip>{{ task.assignee }}</q-tooltip>
                </q-avatar>
              </div>

              <!-- Task Actions -->
              <div class="task-actions">
                <q-btn flat round dense icon="more_horiz" size="sm" @click="showTaskMenu(task)">
                  <q-menu>
                    <q-list>
                      <q-item clickable @click="editTask(task)">
                        <q-item-section avatar>
                          <q-icon name="edit" />
                        </q-item-section>
                        <q-item-section>Edit Task</q-item-section>
                      </q-item>
                      <q-item clickable @click="assignTask(task)">
                        <q-item-section avatar>
                          <q-icon name="person_add" />
                        </q-item-section>
                        <q-item-section>Assign</q-item-section>
                      </q-item>
                      <q-item clickable @click="deleteTask(task)">
                        <q-item-section avatar>
                          <q-icon name="delete" />
                        </q-item-section>
                        <q-item-section>Delete</q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </div>
            </div>

            <!-- Add Task Button -->
            <q-btn
              flat
              color="primary"
              icon="add"
              label="Add Task"
              class="full-width q-mt-sm"
              @click="
                showAddTaskDialog = true;
                newTask.status = column.id;
              "
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Add Task Dialog -->
    <q-dialog v-model="showAddTaskDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Add New Task</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newTask.title"
            label="Task Title"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Title is required']"
          />

          <q-input
            v-model="newTask.description"
            label="Description"
            type="textarea"
            filled
            rows="3"
            class="q-mb-md"
          />

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select v-model="newTask.type" :options="taskTypes" label="Type" filled />
            </div>
            <div class="col">
              <q-select
                v-model="newTask.priority"
                :options="priorityOptions"
                label="Priority"
                filled
              />
            </div>
          </div>

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="newTask.storyPoints"
                label="Story Points"
                type="number"
                filled
              />
            </div>
            <div class="col">
              <q-select
                v-model="newTask.assignee"
                :options="teamMemberOptions"
                label="Assignee"
                filled
                clearable
              />
            </div>
          </div>

          <q-select
            v-model="newTask.labels"
            :options="availableLabels"
            label="Labels"
            multiple
            use-chips
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelAddTask" />
          <q-btn color="primary" label="Add Task" @click="addTask" :disable="!newTask.title" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add Column Dialog -->
    <q-dialog v-model="showAddColumnDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add New Column</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input v-model="newColumn.title" label="Column Title" filled class="q-mb-md" />

          <div class="row q-gutter-md">
            <div class="col">
              <q-select v-model="newColumn.color" :options="colorOptions" label="Color" filled />
            </div>
            <div class="col">
              <q-select v-model="newColumn.icon" :options="iconOptions" label="Icon" filled />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelAddColumn" />
          <q-btn
            color="primary"
            label="Add Column"
            @click="addColumn"
            :disable="!newColumn.title"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();

interface KanbanColumn {
  id: string;
  title: string;
  color: string;
  icon: string;
  order: number;
}

interface KanbanTask {
  id: number;
  title: string;
  description: string;
  storyPoints: number;
  priority: 'high' | 'medium' | 'low';
  type: 'feature' | 'bug' | 'task';
  assignee?: string;
  labels: string[];
  status: string;
  projectId: number;
}

// Reactive data
const showAddTaskDialog = ref(false);
const showAddColumnDialog = ref(false);
const selectedProject = ref('All Projects');
const draggedTask = ref<KanbanTask | null>(null);

const kanbanColumns = ref<KanbanColumn[]>([
  { id: 'todo', title: 'To Do', color: 'grey', icon: 'radio_button_unchecked', order: 1 },
  { id: 'in_progress', title: 'In Progress', color: 'blue', icon: 'play_circle', order: 2 },
  { id: 'review', title: 'Review', color: 'orange', icon: 'rate_review', order: 3 },
  { id: 'done', title: 'Done', color: 'green', icon: 'check_circle', order: 4 },
]);

// Initialize with empty tasks - users can add tasks via the UI
const kanbanTasks = ref<KanbanTask[]>([]);

const newTask = reactive({
  title: '',
  description: '',
  type: 'feature',
  priority: 'medium',
  storyPoints: 1,
  assignee: '',
  labels: [] as string[],
  status: 'todo',
});

const newColumn = reactive({
  title: '',
  color: 'blue',
  icon: 'circle',
});

// Options
const projectOptions = computed(() => {
  const projects = projectStore.projects.map((p) => p.name);
  return ['All Projects', ...projects];
});
const taskTypes = ['feature', 'bug', 'task'];
const priorityOptions = ['high', 'medium', 'low'];
const colorOptions = ['blue', 'green', 'orange', 'red', 'purple', 'teal'];
const iconOptions = ['circle', 'play_circle', 'check_circle', 'star', 'flag'];
const availableLabels = [
  'frontend',
  'backend',
  'mobile',
  'security',
  'performance',
  'database',
  'ui/ux',
];

const teamMemberOptions = computed(() => teamStore.teamMembers.map((member) => member.name));

// Methods
function getTasksInColumn(columnId: string) {
  return kanbanTasks.value.filter((task) => task.status === columnId);
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high':
      return 'red';
    case 'medium':
      return 'orange';
    case 'low':
      return 'green';
    default:
      return 'grey';
  }
}

function getTypeColor(type: string): string {
  switch (type) {
    case 'feature':
      return 'blue';
    case 'bug':
      return 'red';
    case 'task':
      return 'green';
    default:
      return 'grey';
  }
}

function getTypeIcon(type: string): string {
  switch (type) {
    case 'feature':
      return 'new_releases';
    case 'bug':
      return 'bug_report';
    case 'task':
      return 'task';
    default:
      return 'circle';
  }
}

function getAssigneeAvatar(assignee: string): string {
  const avatars: Record<string, string> = {
    'John Smith': 'https://cdn.quasar.dev/img/avatar2.jpg',
    'Sarah Johnson': 'https://cdn.quasar.dev/img/avatar3.jpg',
    'Mike Wilson': 'https://cdn.quasar.dev/img/avatar4.jpg',
    'Emma Davis': 'https://cdn.quasar.dev/img/avatar5.jpg',
  };
  return avatars[assignee] || 'https://cdn.quasar.dev/img/avatar.png';
}

function onDragStart(event: DragEvent, task: KanbanTask) {
  draggedTask.value = task;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
  }
}

function onDragEnd() {
  draggedTask.value = null;
}

function onDragOver(event: DragEvent) {
  event.preventDefault();
}

function onDrop(event: DragEvent, columnId: string) {
  event.preventDefault();
  if (draggedTask.value && draggedTask.value.status !== columnId) {
    draggedTask.value.status = columnId;
  }
}

function addTask() {
  const newId = Math.max(...kanbanTasks.value.map((t) => t.id)) + 1;
  kanbanTasks.value.push({
    ...newTask,
    id: newId,
    projectId: 1,
  } as KanbanTask);

  showAddTaskDialog.value = false;
  cancelAddTask();
}

function cancelAddTask() {
  Object.assign(newTask, {
    title: '',
    description: '',
    type: 'feature',
    priority: 'medium',
    storyPoints: 1,
    assignee: '',
    labels: [],
    status: 'todo',
  });
}

function addColumn() {
  const newId = `custom_${Date.now()}`;
  const maxOrder = Math.max(...kanbanColumns.value.map((c) => c.order));

  kanbanColumns.value.push({
    ...newColumn,
    id: newId,
    order: maxOrder + 1,
  });

  showAddColumnDialog.value = false;
  cancelAddColumn();
}

function cancelAddColumn() {
  Object.assign(newColumn, {
    title: '',
    color: 'blue',
    icon: 'circle',
  });
}

function showColumnMenu(column: KanbanColumn) {
  console.log('Column menu:', column);
}

function editColumn(column: KanbanColumn) {
  console.log('Edit column:', column);
  $q.notify({
    message: `Editing column "${column.title}" - Feature coming soon!`,
    color: 'info',
    icon: 'edit',
    position: 'top',
  });
}

function deleteColumn(column: KanbanColumn) {
  console.log('Delete column:', column);
}

function showTaskMenu(task: KanbanTask) {
  console.log('Task menu:', task);
}

function editTask(task: KanbanTask) {
  console.log('Edit task:', task);
  $q.notify({
    message: `Editing task "${task.title}" - Feature coming soon!`,
    color: 'info',
    icon: 'edit',
    position: 'top',
  });
}

function assignTask(task: KanbanTask) {
  console.log('Assign task:', task);
  $q.notify({
    message: `Task assignment for "${task.title}" - Feature coming soon!`,
    color: 'info',
    icon: 'person_add',
    position: 'top',
  });
}

function deleteTask(task: KanbanTask) {
  const index = kanbanTasks.value.findIndex((t) => t.id === task.id);
  if (index !== -1) {
    kanbanTasks.value.splice(index, 1);
  }
}

onMounted(async () => {
  await Promise.all([projectStore.fetchProjects(), teamStore.fetchTeamMembers()]);
});
</script>

<style scoped>
.kanban-container {
  overflow-x: auto;
}

.kanban-board {
  display: flex;
  gap: 20px;
  min-width: 1200px;
  padding-bottom: 20px;
}

.kanban-column {
  flex: 0 0 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.column-header {
  padding: 16px;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #e0e0e0;
}

.column-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kanban-task {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  cursor: grab;
  transition: all 0.2s ease;
  position: relative;
}

.kanban-task:hover {
  border-color: var(--q-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.kanban-task:hover .task-actions {
  opacity: 1;
}

.kanban-task:active {
  cursor: grabbing;
}

.task-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}
</style>
