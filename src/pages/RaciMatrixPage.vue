<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">RACI Matrix</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Responsibility Assignment Matrix for clear role definitions
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn color="secondary" icon="download" label="Export" @click="exportMatrix" />
          <q-btn color="primary" icon="add" label="Add Task" @click="showAddTaskDialog = true" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- RACI Legend -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">RACI Legend</div>
          <div class="row q-gutter-lg">
            <div class="col">
              <div class="row items-center q-mb-sm">
                <q-chip color="red" text-color="white" size="sm" label="R" class="q-mr-sm" />
                <div>
                  <div class="text-weight-medium">Responsible</div>
                  <div class="text-caption text-grey-7">Does the work to complete the task</div>
                </div>
              </div>
            </div>
            <div class="col">
              <div class="row items-center q-mb-sm">
                <q-chip color="blue" text-color="white" size="sm" label="A" class="q-mr-sm" />
                <div>
                  <div class="text-weight-medium">Accountable</div>
                  <div class="text-caption text-grey-7">Ultimately answerable for completion</div>
                </div>
              </div>
            </div>
            <div class="col">
              <div class="row items-center q-mb-sm">
                <q-chip color="orange" text-color="white" size="sm" label="C" class="q-mr-sm" />
                <div>
                  <div class="text-weight-medium">Consulted</div>
                  <div class="text-caption text-grey-7">Provides input and expertise</div>
                </div>
              </div>
            </div>
            <div class="col">
              <div class="row items-center q-mb-sm">
                <q-chip color="green" text-color="white" size="sm" label="I" class="q-mr-sm" />
                <div>
                  <div class="text-weight-medium">Informed</div>
                  <div class="text-caption text-grey-7">Kept up-to-date on progress</div>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- RACI Matrix Table -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Project Tasks & Responsibilities</div>

          <div class="raci-table-container">
            <table class="raci-table">
              <thead>
                <tr>
                  <th class="task-column">Task / Activity</th>
                  <th v-for="member in teamMembers" :key="member.id" class="member-column">
                    <div class="member-header">
                      <q-avatar size="24px" class="q-mb-xs">
                        <img :src="member.avatar" />
                      </q-avatar>
                      <div class="text-caption text-weight-bold">
                        {{ member.name.split(' ')[0] }}
                      </div>
                      <div class="text-caption text-grey-7">{{ member.role }}</div>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in raciTasks" :key="task.id" class="task-row">
                  <td class="task-cell">
                    <div class="text-weight-medium">{{ task.name }}</div>
                    <div class="text-caption text-grey-7">{{ task.description }}</div>
                  </td>
                  <td v-for="member in teamMembers" :key="member.id" class="responsibility-cell">
                    <q-btn-dropdown
                      :color="getRaciColor(getRaciRole(task.id, member.id))"
                      :label="getRaciRole(task.id, member.id) || '-'"
                      size="sm"
                      flat
                      class="raci-btn"
                    >
                      <q-list>
                        <q-item clickable @click="setRaciRole(task.id, member.id, '')">
                          <q-item-section>None</q-item-section>
                        </q-item>
                        <q-item clickable @click="setRaciRole(task.id, member.id, 'R')">
                          <q-item-section>
                            <q-chip color="red" text-color="white" size="xs" label="R" />
                            Responsible
                          </q-item-section>
                        </q-item>
                        <q-item clickable @click="setRaciRole(task.id, member.id, 'A')">
                          <q-item-section>
                            <q-chip color="blue" text-color="white" size="xs" label="A" />
                            Accountable
                          </q-item-section>
                        </q-item>
                        <q-item clickable @click="setRaciRole(task.id, member.id, 'C')">
                          <q-item-section>
                            <q-chip color="orange" text-color="white" size="xs" label="C" />
                            Consulted
                          </q-item-section>
                        </q-item>
                        <q-item clickable @click="setRaciRole(task.id, member.id, 'I')">
                          <q-item-section>
                            <q-chip color="green" text-color="white" size="xs" label="I" />
                            Informed
                          </q-item-section>
                        </q-item>
                      </q-list>
                    </q-btn-dropdown>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </q-card-section>
      </q-card>

      <!-- Analysis -->
      <div class="row q-gutter-lg q-mt-lg">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Matrix Analysis</div>

              <div class="analysis-item q-mb-md">
                <div class="text-subtitle2 text-weight-medium">Issues Found:</div>
                <div v-if="matrixIssues.length === 0" class="text-positive">
                  <q-icon name="check_circle" class="q-mr-xs" />
                  No issues detected
                </div>
                <div v-else>
                  <div v-for="issue in matrixIssues" :key="issue.id" class="issue-item q-mb-sm">
                    <q-icon
                      :name="issue.severity === 'error' ? 'error' : 'warning'"
                      :color="issue.severity === 'error' ? 'red' : 'orange'"
                      class="q-mr-xs"
                    />
                    <span>{{ issue.message }}</span>
                  </div>
                </div>
              </div>

              <div class="analysis-item">
                <div class="text-subtitle2 text-weight-medium q-mb-sm">Workload Distribution:</div>
                <div v-for="member in teamMembers" :key="member.id" class="workload-item q-mb-xs">
                  <div class="row items-center">
                    <div class="col-6">{{ member.name.split(' ')[0] }}</div>
                    <div class="col">
                      <q-linear-progress
                        :value="getWorkloadPercentage(member.id)"
                        :color="getWorkloadColor(member.id)"
                        style="height: 6px"
                      />
                    </div>
                    <div class="col-auto text-caption">{{ getWorkloadCount(member.id) }} tasks</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Recommendations</div>

              <div class="recommendation-list">
                <div
                  v-for="recommendation in recommendations"
                  :key="recommendation.id"
                  class="recommendation-item q-mb-md"
                >
                  <div class="row items-start">
                    <q-icon
                      :name="recommendation.icon"
                      :color="recommendation.color"
                      class="q-mr-sm q-mt-xs"
                    />
                    <div>
                      <div class="text-weight-medium">{{ recommendation.title }}</div>
                      <div class="text-body2 text-grey-7">{{ recommendation.description }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Add Task Dialog -->
    <q-dialog v-model="showAddTaskDialog" persistent>
      <q-card style="min-width: 400px">
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

          <q-input
            v-model="newTask.description"
            label="Description"
            type="textarea"
            filled
            rows="3"
          />
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
import { useQuasar } from 'quasar';

const $q = useQuasar();

interface RaciTask {
  id: number;
  name: string;
  description: string;
}

interface RaciAssignment {
  taskId: number;
  memberId: number;
  role: 'R' | 'A' | 'C' | 'I' | '';
}

interface MatrixIssue {
  id: string;
  severity: 'error' | 'warning';
  message: string;
}

interface Recommendation {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
}

const mockDataStore = useMockDataStore();

// Reactive data
const showAddTaskDialog = ref(false);

const raciTasks = ref<RaciTask[]>([
  { id: 1, name: 'Requirements Analysis', description: 'Gather and analyze project requirements' },
  { id: 2, name: 'System Design', description: 'Create system architecture and design documents' },
  { id: 3, name: 'Frontend Development', description: 'Develop user interface components' },
  { id: 4, name: 'Backend Development', description: 'Implement server-side logic and APIs' },
  { id: 5, name: 'Database Design', description: 'Design and implement database schema' },
  { id: 6, name: 'Testing & QA', description: 'Perform testing and quality assurance' },
  { id: 7, name: 'Deployment', description: 'Deploy application to production' },
  { id: 8, name: 'Documentation', description: 'Create user and technical documentation' },
  { id: 9, name: 'Code Review', description: 'Review code quality and standards' },
  { id: 10, name: 'Project Management', description: 'Manage project timeline and resources' },
]);

const raciAssignments = ref<RaciAssignment[]>([
  // Requirements Analysis
  { taskId: 1, memberId: 6, role: 'A' }, // Lisa (PM) - Accountable
  { taskId: 1, memberId: 1, role: 'R' }, // John - Responsible
  { taskId: 1, memberId: 4, role: 'C' }, // Emma (Designer) - Consulted
  { taskId: 1, memberId: 2, role: 'I' }, // Sarah - Informed

  // System Design
  { taskId: 2, memberId: 1, role: 'A' }, // John - Accountable
  { taskId: 2, memberId: 2, role: 'R' }, // Sarah - Responsible
  { taskId: 2, memberId: 3, role: 'C' }, // Mike (DevOps) - Consulted
  { taskId: 2, memberId: 6, role: 'I' }, // Lisa - Informed

  // Frontend Development
  { taskId: 3, memberId: 1, role: 'A' }, // John - Accountable
  { taskId: 3, memberId: 1, role: 'R' }, // John - Responsible
  { taskId: 3, memberId: 4, role: 'C' }, // Emma - Consulted
  { taskId: 3, memberId: 5, role: 'R' }, // Alex - Responsible

  // Backend Development
  { taskId: 4, memberId: 2, role: 'A' }, // Sarah - Accountable
  { taskId: 4, memberId: 2, role: 'R' }, // Sarah - Responsible
  { taskId: 4, memberId: 5, role: 'R' }, // Alex - Responsible
  { taskId: 4, memberId: 1, role: 'C' }, // John - Consulted

  // Database Design
  { taskId: 5, memberId: 2, role: 'A' }, // Sarah - Accountable
  { taskId: 5, memberId: 2, role: 'R' }, // Sarah - Responsible
  { taskId: 5, memberId: 3, role: 'C' }, // Mike - Consulted

  // Testing & QA
  { taskId: 6, memberId: 6, role: 'A' }, // Lisa - Accountable
  { taskId: 6, memberId: 1, role: 'R' }, // John - Responsible
  { taskId: 6, memberId: 2, role: 'R' }, // Sarah - Responsible
  { taskId: 6, memberId: 5, role: 'R' }, // Alex - Responsible

  // Deployment
  { taskId: 7, memberId: 3, role: 'A' }, // Mike - Accountable
  { taskId: 7, memberId: 3, role: 'R' }, // Mike - Responsible
  { taskId: 7, memberId: 2, role: 'C' }, // Sarah - Consulted

  // Documentation
  { taskId: 8, memberId: 6, role: 'A' }, // Lisa - Accountable
  { taskId: 8, memberId: 4, role: 'R' }, // Emma - Responsible
  { taskId: 8, memberId: 1, role: 'C' }, // John - Consulted
  { taskId: 8, memberId: 2, role: 'I' }, // Sarah - Informed

  // Code Review
  { taskId: 9, memberId: 1, role: 'A' }, // John - Accountable
  { taskId: 9, memberId: 1, role: 'R' }, // John - Responsible
  { taskId: 9, memberId: 2, role: 'R' }, // Sarah - Responsible
  { taskId: 9, memberId: 5, role: 'C' }, // Alex - Consulted

  // Project Management
  { taskId: 10, memberId: 6, role: 'A' }, // Lisa - Accountable
  { taskId: 10, memberId: 6, role: 'R' }, // Lisa - Responsible
]);

const newTask = reactive({
  name: '',
  description: '',
});

// Computed
const teamMembers = computed(() => mockDataStore.teamMembers);

const matrixIssues = computed(() => {
  const issues: MatrixIssue[] = [];

  // Check for tasks without accountable person
  raciTasks.value.forEach((task) => {
    const accountable = raciAssignments.value.filter((a) => a.taskId === task.id && a.role === 'A');
    if (accountable.length === 0) {
      issues.push({
        id: `no-accountable-${task.id}`,
        severity: 'error',
        message: `Task "${task.name}" has no accountable person`,
      });
    } else if (accountable.length > 1) {
      issues.push({
        id: `multiple-accountable-${task.id}`,
        severity: 'error',
        message: `Task "${task.name}" has multiple accountable people`,
      });
    }

    // Check for tasks without responsible person
    const responsible = raciAssignments.value.filter((a) => a.taskId === task.id && a.role === 'R');
    if (responsible.length === 0) {
      issues.push({
        id: `no-responsible-${task.id}`,
        severity: 'warning',
        message: `Task "${task.name}" has no responsible person`,
      });
    }
  });

  return issues;
});

const recommendations = computed(() => {
  const recs: Recommendation[] = [];

  // Check workload balance
  const maxWorkload = Math.max(...teamMembers.value.map((m) => getWorkloadCount(m.id)));
  const minWorkload = Math.min(...teamMembers.value.map((m) => getWorkloadCount(m.id)));

  if (maxWorkload - minWorkload > 3) {
    recs.push({
      id: 'workload-balance',
      title: 'Balance Workload',
      description: 'Consider redistributing responsibilities for better workload balance',
      icon: 'balance',
      color: 'orange',
    });
  }

  // Check for overloaded members
  teamMembers.value.forEach((member) => {
    const accountableCount = raciAssignments.value.filter(
      (a) => a.memberId === member.id && a.role === 'A',
    ).length;
    if (accountableCount > 3) {
      recs.push({
        id: `overloaded-${member.id}`,
        title: `${member.name} is Overloaded`,
        description: `Consider delegating some accountability to other team members`,
        icon: 'warning',
        color: 'red',
      });
    }
  });

  // General recommendations
  if (matrixIssues.value.length === 0) {
    recs.push({
      id: 'well-structured',
      title: 'Well Structured Matrix',
      description: 'Your RACI matrix is well-balanced with clear responsibilities',
      icon: 'thumb_up',
      color: 'green',
    });
  }

  return recs;
});

// Methods
function getRaciRole(taskId: number, memberId: number): string {
  const assignment = raciAssignments.value.find(
    (a) => a.taskId === taskId && a.memberId === memberId,
  );
  return assignment?.role || '';
}

function setRaciRole(taskId: number, memberId: number, role: 'R' | 'A' | 'C' | 'I' | '') {
  const existingIndex = raciAssignments.value.findIndex(
    (a) => a.taskId === taskId && a.memberId === memberId,
  );

  if (role === '') {
    // Remove assignment
    if (existingIndex !== -1) {
      raciAssignments.value.splice(existingIndex, 1);
    }
  } else {
    // Add or update assignment
    if (existingIndex !== -1) {
      const assignment = raciAssignments.value[existingIndex];
      if (assignment) {
        assignment.role = role;
      }
    } else {
      raciAssignments.value.push({ taskId, memberId, role });
    }
  }
}

function getRaciColor(role: string): string {
  switch (role) {
    case 'R':
      return 'red';
    case 'A':
      return 'blue';
    case 'C':
      return 'orange';
    case 'I':
      return 'green';
    default:
      return 'grey-5';
  }
}

function getWorkloadCount(memberId: number): number {
  return raciAssignments.value.filter(
    (a) => a.memberId === memberId && (a.role === 'R' || a.role === 'A'),
  ).length;
}

function getWorkloadPercentage(memberId: number): number {
  const maxPossible = raciTasks.value.length * 2; // Max if responsible and accountable for all
  const actual = getWorkloadCount(memberId);
  return actual / maxPossible;
}

function getWorkloadColor(memberId: number): string {
  const count = getWorkloadCount(memberId);
  if (count > 5) return 'red';
  if (count > 3) return 'orange';
  return 'green';
}

function addTask() {
  if (!newTask.name) return;

  const newId = Math.max(...raciTasks.value.map((t) => t.id)) + 1;
  raciTasks.value.push({
    id: newId,
    name: newTask.name,
    description: newTask.description,
  });

  cancelAddTask();
}

function cancelAddTask() {
  showAddTaskDialog.value = false;
  Object.assign(newTask, {
    name: '',
    description: '',
  });
}

function exportMatrix() {
  // Simulate matrix export functionality
  console.log('Exporting RACI matrix...');
  $q.notify({
    message: 'RACI matrix exported successfully!',
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.raci-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.raci-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.raci-table th,
.raci-table td {
  border: 1px solid #e0e0e0;
  padding: 12px;
  text-align: center;
}

.raci-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.task-column {
  min-width: 200px;
  text-align: left !important;
}

.member-column {
  min-width: 120px;
}

.task-cell {
  text-align: left !important;
  background: #fafafa;
}

.responsibility-cell {
  vertical-align: middle;
}

.member-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.raci-btn {
  min-width: 40px;
  min-height: 32px;
}

.task-row:hover {
  background: rgba(25, 118, 210, 0.05);
}

.analysis-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.issue-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.workload-item {
  padding: 4px 0;
}

.recommendation-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}
</style>
