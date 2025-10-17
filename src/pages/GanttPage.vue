<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Gantt Chart</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Visual timeline and project scheduling</p>
        </div>
        <div class="row q-gutter-md">
          <q-btn-toggle
            v-model="viewMode"
            :options="[
              { label: 'Days', value: 'days' },
              { label: 'Weeks', value: 'weeks' },
              { label: 'Months', value: 'months' },
            ]"
            color="primary"
            toggle-color="primary"
          />
          <q-btn color="secondary" icon="zoom_in" label="Zoom In" @click="zoomIn" />
          <q-btn color="secondary" icon="zoom_out" label="Zoom Out" @click="zoomOut" />
          <q-btn color="primary" icon="add" label="Add Task" @click="showAddTaskDialog = true" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Project Info -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-primary-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-primary">{{ ganttTasks.length }}</div>
                  <div class="text-caption text-grey-7">Total Tasks</div>
                </div>
                <div class="col-auto">
                  <q-icon name="task" size="32px" class="text-primary" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-green-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-green">{{ completedTasks.length }}</div>
                  <div class="text-caption text-grey-7">Completed</div>
                </div>
                <div class="col-auto">
                  <q-icon name="check_circle" size="32px" class="text-green" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-orange-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-orange">{{ criticalPath.length }}</div>
                  <div class="text-caption text-grey-7">Critical Path</div>
                </div>
                <div class="col-auto">
                  <q-icon name="timeline" size="32px" class="text-orange" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-blue-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-blue">{{ projectDuration }} days</div>
                  <div class="text-caption text-grey-7">Duration</div>
                </div>
                <div class="col-auto">
                  <q-icon name="schedule" size="32px" class="text-blue" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Gantt Chart -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Project Timeline</div>

          <div class="gantt-container">
            <!-- Timeline Header -->
            <div class="gantt-header">
              <div class="task-names-header">Tasks</div>
              <div class="timeline-header">
                <div
                  v-for="date in timelineHeaders"
                  :key="date.key"
                  class="timeline-header-cell"
                  :style="{ width: `${cellWidth}px` }"
                >
                  <div class="text-caption text-weight-bold">{{ date.label }}</div>
                  <div class="text-caption text-grey-7">{{ date.sublabel }}</div>
                </div>
              </div>
            </div>

            <!-- Gantt Rows -->
            <div class="gantt-body">
              <div
                v-for="task in ganttTasks"
                :key="task.id"
                class="gantt-row"
                :class="{ 'critical-path': isCriticalPath(task.id) }"
              >
                <!-- Task Info -->
                <div class="task-info">
                  <div class="task-name">
                    <q-icon :name="getTaskIcon(task.type)" class="q-mr-xs" />
                    {{ task.name }}
                  </div>
                  <div class="task-details">
                    <span class="text-caption text-grey-7">{{ task.duration }}d</span>
                    <span class="text-caption text-grey-7 q-ml-sm">{{ task.assignee }}</span>
                  </div>
                </div>

                <!-- Timeline -->
                <div class="task-timeline">
                  <div
                    class="task-bar"
                    :class="{
                      'task-bar-completed': task.progress === 100,
                      'task-bar-critical': isCriticalPath(task.id),
                      'task-bar-milestone': task.type === 'milestone',
                    }"
                    :style="getTaskBarStyle(task)"
                    @click="selectTask(task)"
                  >
                    <div class="task-bar-progress" :style="{ width: `${task.progress}%` }"></div>
                    <div class="task-bar-label">{{ task.name }}</div>
                  </div>

                  <!-- Dependencies -->
                  <div
                    v-for="dep in task.dependencies"
                    :key="dep"
                    class="dependency-line"
                    :style="getDependencyStyle(task.id, dep)"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Task Details -->
      <div class="row q-gutter-lg q-mt-lg" v-if="selectedTask">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Task Details</div>

              <div class="row q-gutter-md">
                <div class="col">
                  <q-input v-model="selectedTask.name" label="Task Name" filled />
                </div>
                <div class="col">
                  <q-input
                    v-model.number="selectedTask.duration"
                    label="Duration (days)"
                    type="number"
                    filled
                  />
                </div>
              </div>

              <div class="row q-gutter-md q-mt-md">
                <div class="col">
                  <q-input
                    v-model="selectedTask.startDate"
                    label="Start Date"
                    filled
                    mask="date"
                    :rules="['date']"
                  >
                    <template v-slot:append>
                      <q-icon name="event" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                          <q-date v-model="selectedTask.startDate">
                            <div class="row items-center justify-end">
                              <q-btn v-close-popup label="Close" color="primary" flat />
                            </div>
                          </q-date>
                        </q-popup-proxy>
                      </q-icon>
                    </template>
                  </q-input>
                </div>
                <div class="col">
                  <q-select
                    v-model="selectedTask.assignee"
                    :options="teamMemberOptions"
                    label="Assignee"
                    filled
                  />
                </div>
              </div>

              <q-slider
                v-model="selectedTask.progress"
                :min="0"
                :max="100"
                :step="10"
                label
                label-always
                color="primary"
                class="q-mt-md"
              />
              <div class="text-caption text-grey-7 q-mt-xs">
                Progress: {{ selectedTask.progress }}%
              </div>
            </q-card-section>

            <q-card-actions align="right">
              <q-btn flat label="Cancel" @click="selectedTask = null" />
              <q-btn color="primary" label="Save Changes" @click="saveTaskChanges" />
            </q-card-actions>
          </q-card>
        </div>

        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Dependencies</div>

              <div class="dependency-list">
                <div
                  v-if="selectedTask.dependencies.length === 0"
                  class="text-grey-7 text-center q-pa-md"
                >
                  No dependencies
                </div>
                <div v-else>
                  <div
                    v-for="depId in selectedTask.dependencies"
                    :key="depId"
                    class="dependency-item q-mb-sm"
                  >
                    <div class="row items-center">
                      <q-icon name="arrow_right" class="q-mr-sm" />
                      <div class="col">{{ getTaskName(depId) }}</div>
                      <q-btn
                        flat
                        round
                        dense
                        icon="close"
                        size="sm"
                        @click="removeDependency(selectedTask.id, depId)"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <q-select
                v-model="newDependency"
                :options="availableDependencies"
                label="Add Dependency"
                filled
                class="q-mt-md"
                @update:model-value="addDependency"
              />
            </q-card-section>
          </q-card>
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
            v-model="newTask.name"
            label="Task Name"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Task name is required']"
          />

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="newTask.duration"
                label="Duration (days)"
                type="number"
                filled
              />
            </div>
            <div class="col">
              <q-select v-model="newTask.type" :options="taskTypeOptions" label="Type" filled />
            </div>
          </div>

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model="newTask.startDate"
                label="Start Date"
                filled
                mask="date"
                :rules="['date']"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="newTask.startDate">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
            <div class="col">
              <q-select
                v-model="newTask.assignee"
                :options="teamMemberOptions"
                label="Assignee"
                filled
              />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelAddTask" />
          <q-btn color="primary" label="Add Task" @click="addTask" :disable="!newTask.name" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';
import { format, addDays, differenceInDays } from 'date-fns';

interface GanttTask {
  id: number;
  name: string;
  duration: number;
  startDate: string;
  endDate: string;
  progress: number;
  assignee: string;
  type: 'task' | 'milestone' | 'summary';
  dependencies: number[];
}

const mockDataStore = useMockDataStore();

// Reactive data
const showAddTaskDialog = ref(false);
const viewMode = ref('weeks');
const zoomLevel = ref(1);
const selectedTask = ref<GanttTask | null>(null);
const newDependency = ref<number | null>(null);

const ganttTasks = ref<GanttTask[]>([
  {
    id: 1,
    name: 'Project Planning',
    duration: 5,
    startDate: '2024/01/01',
    endDate: '2024/01/05',
    progress: 100,
    assignee: 'Lisa Rodriguez',
    type: 'task',
    dependencies: [],
  },
  {
    id: 2,
    name: 'Requirements Analysis',
    duration: 8,
    startDate: '2024/01/06',
    endDate: '2024/01/13',
    progress: 100,
    assignee: 'John Smith',
    type: 'task',
    dependencies: [1],
  },
  {
    id: 3,
    name: 'System Design',
    duration: 10,
    startDate: '2024/01/14',
    endDate: '2024/01/23',
    progress: 85,
    assignee: 'Sarah Johnson',
    type: 'task',
    dependencies: [2],
  },
  {
    id: 4,
    name: 'Database Design',
    duration: 6,
    startDate: '2024/01/16',
    endDate: '2024/01/21',
    progress: 90,
    assignee: 'Sarah Johnson',
    type: 'task',
    dependencies: [2],
  },
  {
    id: 5,
    name: 'Frontend Development',
    duration: 15,
    startDate: '2024/01/24',
    endDate: '2024/02/07',
    progress: 60,
    assignee: 'John Smith',
    type: 'task',
    dependencies: [3],
  },
  {
    id: 6,
    name: 'Backend Development',
    duration: 18,
    startDate: '2024/01/22',
    endDate: '2024/02/08',
    progress: 45,
    assignee: 'Alex Chen',
    type: 'task',
    dependencies: [4],
  },
  {
    id: 7,
    name: 'Integration Testing',
    duration: 7,
    startDate: '2024/02/09',
    endDate: '2024/02/15',
    progress: 0,
    assignee: 'Mike Wilson',
    type: 'task',
    dependencies: [5, 6],
  },
  {
    id: 8,
    name: 'Deployment',
    duration: 3,
    startDate: '2024/02/16',
    endDate: '2024/02/18',
    progress: 0,
    assignee: 'Mike Wilson',
    type: 'task',
    dependencies: [7],
  },
  {
    id: 9,
    name: 'Project Completion',
    duration: 1,
    startDate: '2024/02/19',
    endDate: '2024/02/19',
    progress: 0,
    assignee: 'Lisa Rodriguez',
    type: 'milestone',
    dependencies: [8],
  },
]);

const newTask = reactive({
  name: '',
  duration: 5,
  startDate: format(new Date(), 'yyyy/MM/dd'),
  assignee: '',
  type: 'task',
});

const taskTypeOptions = ['task', 'milestone', 'summary'];

// Computed
const teamMembers = computed(() => mockDataStore.teamMembers);
const teamMemberOptions = computed(() => teamMembers.value.map((m) => m.name));

const completedTasks = computed(() => ganttTasks.value.filter((t) => t.progress === 100));

const criticalPath = computed(() => {
  // Simplified critical path calculation
  return [2, 3, 5, 7, 8, 9]; // Task IDs on critical path
});

const projectDuration = computed(() => {
  if (ganttTasks.value.length === 0) return 0;
  const startDates = ganttTasks.value.map((t) => new Date(t.startDate));
  const endDates = ganttTasks.value.map((t) => new Date(t.endDate));
  const projectStart = new Date(Math.min(...startDates.map((d) => d.getTime())));
  const projectEnd = new Date(Math.max(...endDates.map((d) => d.getTime())));
  return differenceInDays(projectEnd, projectStart) + 1;
});

const cellWidth = computed(() => {
  const baseWidth = viewMode.value === 'days' ? 30 : viewMode.value === 'weeks' ? 50 : 80;
  return baseWidth * zoomLevel.value;
});

const timelineHeaders = computed(() => {
  const headers = [];
  const startDate = new Date('2024/01/01');
  const endDate = new Date('2024/03/01');

  let current = new Date(startDate);
  let index = 0;

  while (current <= endDate && index < 20) {
    if (viewMode.value === 'days') {
      headers.push({
        key: format(current, 'yyyy-MM-dd'),
        label: format(current, 'dd'),
        sublabel: format(current, 'MMM'),
      });
      current = addDays(current, 1);
    } else if (viewMode.value === 'weeks') {
      headers.push({
        key: format(current, 'yyyy-ww'),
        label: `W${format(current, 'w')}`,
        sublabel: format(current, 'MMM'),
      });
      current = addDays(current, 7);
    } else {
      headers.push({
        key: format(current, 'yyyy-MM'),
        label: format(current, 'MMM'),
        sublabel: format(current, 'yyyy'),
      });
      current.setMonth(current.getMonth() + 1);
    }
    index++;
  }

  return headers;
});

const availableDependencies = computed(() => {
  if (!selectedTask.value) return [];
  return ganttTasks.value
    .filter(
      (t) => t.id !== selectedTask.value!.id && !selectedTask.value!.dependencies.includes(t.id),
    )
    .map((t) => ({ label: t.name, value: t.id }));
});

// Methods
function getTaskIcon(type: string): string {
  switch (type) {
    case 'milestone':
      return 'flag';
    case 'summary':
      return 'folder';
    default:
      return 'task';
  }
}

function isCriticalPath(taskId: number): boolean {
  return criticalPath.value.includes(taskId);
}

function getTaskBarStyle(task: GanttTask) {
  const startDate = new Date(task.startDate);
  const projectStart = new Date('2024/01/01');
  const daysFromStart = differenceInDays(startDate, projectStart);

  return {
    left: `${daysFromStart * (cellWidth.value / (viewMode.value === 'days' ? 1 : viewMode.value === 'weeks' ? 7 : 30))}px`,
    width: `${task.duration * (cellWidth.value / (viewMode.value === 'days' ? 1 : viewMode.value === 'weeks' ? 7 : 30))}px`,
  };
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getDependencyStyle(_taskId: number, _depId: number) {
  // Simplified dependency line styling
  // Parameters prefixed with _ to indicate they're unused but reserved for future implementation
  return {
    display: 'none', // Hide for now - complex SVG implementation needed
  };
}

function selectTask(task: GanttTask) {
  selectedTask.value = { ...task };
}

function saveTaskChanges() {
  if (!selectedTask.value) return;

  const index = ganttTasks.value.findIndex((t) => t.id === selectedTask.value!.id);
  if (index !== -1) {
    ganttTasks.value[index] = { ...selectedTask.value };
  }
  selectedTask.value = null;
}

function getTaskName(taskId: number): string {
  const task = ganttTasks.value.find((t) => t.id === taskId);
  return task?.name || 'Unknown Task';
}

function addDependency() {
  if (selectedTask.value && newDependency.value) {
    selectedTask.value.dependencies.push(newDependency.value);
    newDependency.value = null;
  }
}

function removeDependency(taskId: number, depId: number) {
  if (selectedTask.value) {
    selectedTask.value.dependencies = selectedTask.value.dependencies.filter((id) => id !== depId);
  }
}

function addTask() {
  const newId = Math.max(...ganttTasks.value.map((t) => t.id)) + 1;
  const startDate = new Date(newTask.startDate);
  const endDate = addDays(startDate, newTask.duration - 1);

  ganttTasks.value.push({
    id: newId,
    name: newTask.name,
    duration: newTask.duration,
    startDate: newTask.startDate,
    endDate: format(endDate, 'yyyy/MM/dd'),
    progress: 0,
    assignee: newTask.assignee,
    type: newTask.type as 'task' | 'milestone' | 'summary',
    dependencies: [],
  });

  cancelAddTask();
}

function cancelAddTask() {
  showAddTaskDialog.value = false;
  Object.assign(newTask, {
    name: '',
    duration: 5,
    startDate: format(new Date(), 'yyyy/MM/dd'),
    assignee: '',
    type: 'task',
  });
}

function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, 3);
}

function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, 0.5);
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.stat-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.gantt-container {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.gantt-header {
  display: flex;
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
}

.task-names-header {
  width: 250px;
  min-width: 250px;
  padding: 12px;
  font-weight: 600;
  border-right: 1px solid #e0e0e0;
}

.timeline-header {
  display: flex;
  overflow-x: auto;
}

.timeline-header-cell {
  min-width: 50px;
  padding: 8px;
  text-align: center;
  border-right: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.gantt-body {
  max-height: 500px;
  overflow-y: auto;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  min-height: 60px;
  align-items: center;
}

.gantt-row:hover {
  background: rgba(25, 118, 210, 0.05);
}

.gantt-row.critical-path {
  background: rgba(255, 152, 0, 0.1);
}

.task-info {
  width: 250px;
  min-width: 250px;
  padding: 12px;
  border-right: 1px solid #e0e0e0;
}

.task-name {
  font-weight: 500;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.task-details {
  display: flex;
  gap: 8px;
}

.task-timeline {
  flex: 1;
  position: relative;
  height: 60px;
  overflow-x: auto;
}

.task-bar {
  position: absolute;
  height: 24px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--q-primary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 20px;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.task-bar:hover {
  height: 28px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.task-bar-completed {
  background: #4caf50;
}

.task-bar-critical {
  background: #ff9800;
}

.task-bar-milestone {
  background: #f44336;
  border-radius: 50%;
  width: 24px !important;
  min-width: 24px !important;
}

.task-bar-progress {
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  transition: width 0.3s ease;
}

.task-bar-label {
  position: absolute;
  left: 8px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  pointer-events: none;
}

.dependency-line {
  position: absolute;
  border: 1px solid #666;
  z-index: 1;
}

.dependency-item {
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}
</style>
