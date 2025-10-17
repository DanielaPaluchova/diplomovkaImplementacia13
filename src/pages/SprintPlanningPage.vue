<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Sprint Planning</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Plan and organize your sprint with AI-powered insights
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="psychology"
            label="AI Suggestions"
            @click="getAISuggestions"
          />
          <q-btn color="primary" icon="rocket_launch" label="Start Sprint" @click="startSprint" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Sprint Info & Controls -->
      <div class="row q-gutter-lg q-mb-lg">
        <!-- Sprint Details -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold">Sprint 12</div>
              <div class="text-grey-7">December 15 - December 29, 2024</div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="row q-gutter-md">
                <div class="col">
                  <div class="text-caption text-grey-7">Capacity</div>
                  <div class="text-h6 text-primary">{{ sprintCapacity }} SP</div>
                </div>
                <div class="col">
                  <div class="text-caption text-grey-7">Planned</div>
                  <div
                    class="text-h6"
                    :class="plannedPoints > sprintCapacity ? 'text-red' : 'text-green'"
                  >
                    {{ plannedPoints }} SP
                  </div>
                </div>
                <div class="col">
                  <div class="text-caption text-grey-7">Team</div>
                  <div class="text-h6 text-orange">{{ teamMembers.length }} devs</div>
                </div>
              </div>

              <q-linear-progress
                :value="plannedPoints / sprintCapacity"
                :color="plannedPoints > sprintCapacity ? 'red' : 'primary'"
                class="q-mt-md"
                style="height: 8px"
              />
              <div class="text-caption text-center q-mt-xs">
                {{ Math.round((plannedPoints / sprintCapacity) * 100) }}% of capacity
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Team Allocation -->
        <div class="col-12 col-md-4">
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

        <!-- AI Insights -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="row items-center">
                <q-icon name="smart_toy" color="primary" size="24px" class="q-mr-sm" />
                <div class="text-h6 text-weight-bold">AI Insights</div>
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="column q-gutter-sm">
                <div class="ai-insight" v-for="insight in currentInsights" :key="insight.id">
                  <q-icon
                    :name="insight.icon"
                    :color="insight.type === 'warning' ? 'orange' : 'primary'"
                    size="16px"
                    class="q-mr-xs"
                  />
                  <span class="text-body2">{{ insight.message }}</span>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Sprint Board -->
      <div class="row q-gutter-lg">
        <!-- Backlog -->
        <div class="col-12 col-lg-4">
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
                     <div class="text-body2 text-grey-7 q-mb-sm" style="font-size: 12px">{{ task.description }}</div>
                     <div class="row items-center justify-between">
                       <q-chip :color="task.priority === 'high' ? 'red' : task.priority === 'medium' ? 'orange' : 'green'" 
                               text-color="white" size="sm" :label="task.priority" />
                       <div class="text-caption">{{ task.storyPoints }} SP</div>
                     </div>
                   </q-card-section>
                 </q-card>
               </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Sprint Backlog -->
        <div class="col-12 col-lg-4">
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
                         <div class="text-subtitle2 text-weight-medium q-mb-xs">{{ task.title }}</div>
                       </div>
                       <div class="col-auto">
                         <q-btn flat round dense icon="close" size="sm" color="grey-6" @click="removeFromSprint(task.id)" />
                       </div>
                     </div>
                     <div class="text-body2 text-grey-7 q-mb-sm" style="font-size: 12px">{{ task.description }}</div>
                     <div class="row items-center justify-between">
                       <q-chip :color="task.priority === 'high' ? 'red' : task.priority === 'medium' ? 'orange' : 'green'" 
                               text-color="white" size="sm" :label="task.priority" />
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

        <!-- Sprint Analysis -->
        <div class="col-12 col-lg-4">
          <q-card class="full-height">
            <q-card-section class="bg-green-1">
              <div class="text-h6 text-weight-bold text-green-8">Sprint Analysis</div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <!-- Velocity Chart -->
              <div class="text-subtitle1 text-weight-medium q-mb-md">Velocity Prediction</div>
              <div class="velocity-chart q-mb-lg">
                <div class="row items-end q-gutter-xs" style="height: 80px">
                  <div
                    v-for="(velocity, index) in velocityHistory"
                    :key="index"
                    class="velocity-bar bg-primary"
                    :style="{
                      height: `${(velocity / Math.max(...velocityHistory)) * 80}px`,
                      width: '20px',
                    }"
                  />
                  <div
                    class="velocity-bar bg-green"
                    :style="{
                      height: `${(predictedVelocity / Math.max(...velocityHistory)) * 80}px`,
                      width: '20px',
                      opacity: 0.7,
                    }"
                  />
                </div>
                <div class="text-caption text-center q-mt-xs">
                  Predicted: {{ predictedVelocity }} SP
                </div>
              </div>

              <!-- Risk Assessment -->
              <div class="text-subtitle1 text-weight-medium q-mb-md">Risk Assessment</div>
              <div class="column q-gutter-sm">
                <div v-for="risk in riskAssessment" :key="risk.type" class="row items-center">
                  <q-icon
                    :name="
                      risk.level === 'high'
                        ? 'error'
                        : risk.level === 'medium'
                          ? 'warning'
                          : 'check_circle'
                    "
                    :color="
                      risk.level === 'high' ? 'red' : risk.level === 'medium' ? 'orange' : 'green'
                    "
                    size="16px"
                    class="q-mr-sm"
                  />
                  <div class="col">
                    <div class="text-body2">{{ risk.type }}</div>
                  </div>
                  <div class="col-auto">
                    <q-chip
                      :color="
                        risk.level === 'high' ? 'red' : risk.level === 'medium' ? 'orange' : 'green'
                      "
                      text-color="white"
                      size="sm"
                      :label="risk.level"
                    />
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Task {
  id: number;
  title: string;
  description: string;
  storyPoints: number;
  priority: 'high' | 'medium' | 'low';
  type: 'feature' | 'bug' | 'task';
  assignee?: string;
  labels: string[];
  complexity: number;
}

interface TeamMember {
  id: number;
  name: string;
  avatar: string;
  capacity: number;
  workload: number;
}

// Reactive data
const isDragOver = ref(false);
const draggedTask = ref<Task | null>(null);

const sprintCapacity = 45;
const predictedVelocity = 38;
const velocityHistory = [32, 35, 40, 38, 42];

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

const backlogTasks = ref<Task[]>([
  {
    id: 1,
    title: 'User Authentication System',
    description: 'Implement JWT-based authentication with refresh tokens',
    storyPoints: 8,
    priority: 'high',
    type: 'feature',
    assignee: 'John Smith',
    labels: ['backend', 'security'],
    complexity: 8,
  },
  {
    id: 2,
    title: 'Dashboard Analytics Widget',
    description: 'Create interactive charts for project metrics',
    storyPoints: 5,
    priority: 'medium',
    type: 'feature',
    labels: ['frontend', 'charts'],
    complexity: 6,
  },
  {
    id: 3,
    title: 'Fix Mobile Responsive Issues',
    description: 'Resolve layout problems on mobile devices',
    storyPoints: 3,
    priority: 'high',
    type: 'bug',
    labels: ['frontend', 'mobile'],
    complexity: 4,
  },
  {
    id: 4,
    title: 'API Rate Limiting',
    description: 'Implement rate limiting for API endpoints',
    storyPoints: 5,
    priority: 'medium',
    type: 'feature',
    labels: ['backend', 'security'],
    complexity: 5,
  },
  {
    id: 5,
    title: 'User Profile Management',
    description: 'Allow users to update their profile information',
    storyPoints: 8,
    priority: 'low',
    type: 'feature',
    labels: ['frontend', 'backend'],
    complexity: 7,
  },
  {
    id: 6,
    title: 'Database Migration Scripts',
    description: 'Create scripts for production database migration',
    storyPoints: 3,
    priority: 'medium',
    type: 'task',
    labels: ['database', 'devops'],
    complexity: 5,
  },
]);

const sprintTasks = ref<Task[]>([
  {
    id: 101,
    title: 'Sprint Planning UI',
    description: 'Create drag and drop interface for sprint planning',
    storyPoints: 13,
    priority: 'high',
    type: 'feature',
    assignee: 'Sarah Johnson',
    labels: ['frontend', 'planning'],
    complexity: 9,
  },
  {
    id: 102,
    title: 'PERT Algorithm Implementation',
    description: 'Implement PERT analysis for project scheduling',
    storyPoints: 21,
    priority: 'high',
    type: 'feature',
    assignee: 'Mike Wilson',
    labels: ['backend', 'algorithm'],
    complexity: 10,
  },
]);

const currentInsights = ref([
  {
    id: 1,
    message: 'Sprint capacity is optimal for current team velocity',
    type: 'info',
    icon: 'check_circle',
  },
  {
    id: 2,
    message: 'Consider breaking down large stories for better estimation',
    type: 'warning',
    icon: 'warning',
  },
  {
    id: 3,
    message: 'Mike Wilson has high workload, consider redistribution',
    type: 'warning',
    icon: 'person',
  },
]);

const riskAssessment = [
  { type: 'Scope Creep', level: 'low' },
  { type: 'Technical Complexity', level: 'medium' },
  { type: 'Team Capacity', level: 'high' },
  { type: 'Dependencies', level: 'low' },
];

// Computed
const plannedPoints = computed(() => {
  return sprintTasks.value.reduce((sum, task) => sum + task.storyPoints, 0);
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

  if (draggedTask.value) {
    // Move task from backlog to sprint
    const taskIndex = backlogTasks.value.findIndex((t) => t.id === draggedTask.value!.id);
    if (taskIndex !== -1) {
      const task = backlogTasks.value.splice(taskIndex, 1)[0];
      if (task) {
        sprintTasks.value.push(task);
      }
    }
    draggedTask.value = null;
  }
}

function removeFromSprint(taskId: number) {
  const taskIndex = sprintTasks.value.findIndex((t) => t.id === taskId);
  if (taskIndex !== -1) {
    const task = sprintTasks.value.splice(taskIndex, 1)[0];
    if (task) {
      backlogTasks.value.push(task);
    }
  }
}

function getAISuggestions() {
  // TODO: Implement AI suggestions
  console.log('Getting AI suggestions...');
}

function startSprint() {
  // TODO: Implement sprint start
  console.log('Starting sprint...');
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

.ai-insight {
  display: flex;
  align-items: flex-start;
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 6px;
}

.velocity-chart {
  display: flex;
  justify-content: center;
}

.velocity-bar {
  border-radius: 2px;
  margin: 0 1px;
  transition: all 0.3s ease;
}

.velocity-bar:hover {
  opacity: 0.8;
}
</style>
