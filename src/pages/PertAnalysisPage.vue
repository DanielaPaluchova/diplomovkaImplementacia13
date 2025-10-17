<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">PERT Analysis</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Critical path analysis with AI-enhanced time estimation
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn color="secondary" icon="psychology" label="AI Optimize" @click="aiOptimize" />
          <q-btn color="primary" icon="calculate" label="Recalculate" @click="recalculatePert" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- PERT Summary Cards -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="text-center">
            <q-card-section>
              <div class="text-h4 text-primary text-weight-bold">
                {{ criticalPathDuration }}
              </div>
              <div class="text-grey-7">Critical Path Duration (days)</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="text-center">
            <q-card-section>
              <div class="text-h4 text-green text-weight-bold">
                {{ totalTasks }}
              </div>
              <div class="text-grey-7">Total Tasks</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="text-center">
            <q-card-section>
              <div class="text-h4 text-orange text-weight-bold">
                {{ criticalTasks }}
              </div>
              <div class="text-grey-7">Critical Tasks</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="text-center">
            <q-card-section>
              <div class="text-h4 text-red text-weight-bold">{{ riskLevel }}%</div>
              <div class="text-grey-7">Project Risk Level</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <div class="row q-gutter-lg">
        <!-- PERT Network Diagram -->
        <div class="col-12 col-lg-8">
          <q-card class="full-height">
            <q-card-section>
              <div class="row items-center justify-between q-mb-md">
                <div class="text-h6 text-weight-bold">PERT Network Diagram</div>
                <div class="row q-gutter-sm">
                  <q-btn flat icon="zoom_in" @click="zoomIn" size="sm" />
                  <q-btn flat icon="zoom_out" @click="zoomOut" size="sm" />
                  <q-btn flat icon="center_focus_strong" @click="resetZoom" size="sm" />
                </div>
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-none">
              <div
                ref="pertDiagramContainer"
                class="pert-diagram-container"
                :style="{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }"
              >
                <svg width="100%" height="500" class="pert-diagram">
                  <!-- Grid Background -->
                  <defs>
                    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" stroke-width="1" />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />

                  <!-- Connections -->
                  <g class="connections">
                    <line
                      v-for="connection in connections"
                      :key="`${connection.from}-${connection.to}`"
                      :x1="getNodePosition(connection.from).x + 60"
                      :y1="getNodePosition(connection.from).y + 30"
                      :x2="getNodePosition(connection.to).x"
                      :y2="getNodePosition(connection.to).y + 30"
                      :stroke="connection.isCritical ? '#f44336' : '#2196f3'"
                      :stroke-width="connection.isCritical ? 3 : 2"
                      marker-end="url(#arrowhead)"
                    />
                  </g>

                  <!-- Arrow marker definition -->
                  <defs>
                    <marker
                      id="arrowhead"
                      markerWidth="10"
                      markerHeight="7"
                      refX="9"
                      refY="3.5"
                      orient="auto"
                    >
                      <polygon points="0 0, 10 3.5, 0 7" fill="#2196f3" />
                    </marker>
                  </defs>

                  <!-- Nodes -->
                  <g class="nodes">
                    <g
                      v-for="node in pertNodes"
                      :key="node.id"
                      :transform="`translate(${getNodePosition(node.id).x}, ${getNodePosition(node.id).y})`"
                      class="pert-node"
                      :class="{ critical: node.isCritical }"
                      @click="selectNode(node)"
                    >
                      <rect
                        width="120"
                        height="60"
                        rx="8"
                        :fill="node.isCritical ? '#ffebee' : '#e3f2fd'"
                        :stroke="node.isCritical ? '#f44336' : '#2196f3'"
                        stroke-width="2"
                      />
                      <text x="60" y="25" text-anchor="middle" class="node-title">
                        {{ node.name }}
                      </text>
                      <text x="60" y="45" text-anchor="middle" class="node-duration">
                        {{ node.duration }}d
                      </text>
                    </g>
                  </g>
                </svg>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Task Details & Controls -->
        <div class="col-12 col-lg-4">
          <!-- Task Details -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold">Task Details</div>
            </q-card-section>
            <q-separator />
            <q-card-section v-if="selectedNode">
              <div class="column q-gutter-md">
                <div>
                  <div class="text-weight-medium">{{ selectedNode.name }}</div>
                  <div class="text-caption text-grey-7">{{ selectedNode.description }}</div>
                </div>

                <div class="row q-gutter-md">
                  <div class="col">
                    <div class="text-caption text-grey-7">Duration</div>
                    <div class="text-h6 text-primary">{{ selectedNode.duration }}d</div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Float</div>
                    <div
                      class="text-h6"
                      :class="selectedNode.float === 0 ? 'text-red' : 'text-green'"
                    >
                      {{ selectedNode.float }}d
                    </div>
                  </div>
                </div>

                <div>
                  <div class="text-caption text-grey-7 q-mb-sm">Time Estimates</div>
                  <div class="column q-gutter-xs">
                    <div class="row justify-between">
                      <span>Optimistic:</span>
                      <span class="text-weight-medium">{{ selectedNode.optimistic }}d</span>
                    </div>
                    <div class="row justify-between">
                      <span>Most Likely:</span>
                      <span class="text-weight-medium">{{ selectedNode.mostLikely }}d</span>
                    </div>
                    <div class="row justify-between">
                      <span>Pessimistic:</span>
                      <span class="text-weight-medium">{{ selectedNode.pessimistic }}d</span>
                    </div>
                  </div>
                </div>

                <q-chip
                  :color="selectedNode.isCritical ? 'red' : 'green'"
                  text-color="white"
                  :icon="selectedNode.isCritical ? 'warning' : 'check_circle'"
                  :label="selectedNode.isCritical ? 'Critical Path' : 'Non-Critical'"
                />
              </div>
            </q-card-section>
            <q-card-section v-else class="text-center text-grey-5">
              <q-icon name="touch_app" size="48px" class="q-mb-md" />
              <div>Click on a task to view details</div>
            </q-card-section>
          </q-card>

          <!-- AI Insights -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="row items-center">
                <q-icon name="smart_toy" color="primary" size="24px" class="q-mr-sm" />
                <div class="text-h6 text-weight-bold">AI Insights</div>
              </div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="column q-gutter-sm">
                <div v-for="insight in aiInsights" :key="insight.id" class="ai-insight-card">
                  <q-icon
                    :name="insight.icon"
                    :color="
                      insight.type === 'warning'
                        ? 'orange'
                        : insight.type === 'error'
                          ? 'red'
                          : 'primary'
                    "
                    size="16px"
                    class="q-mr-sm"
                  />
                  <div class="text-body2">{{ insight.message }}</div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Critical Path Tasks -->
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold text-red">Critical Path Tasks</div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-none">
              <q-list>
                <q-item v-for="task in criticalPathTasks" :key="task.id" class="q-pa-md">
                  <q-item-section avatar>
                    <q-icon name="warning" color="red" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ task.name }}</q-item-label>
                    <q-item-label caption>Duration: {{ task.duration }} days</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-chip color="red" text-color="white" size="sm" label="Critical" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

interface PertNode {
  id: string;
  name: string;
  description: string;
  duration: number;
  optimistic: number;
  mostLikely: number;
  pessimistic: number;
  isCritical: boolean;
  float: number;
}

interface Connection {
  from: string;
  to: string;
  isCritical: boolean;
}

// Reactive data
const selectedNode = ref<PertNode | null>(null);
const zoomLevel = ref(1);
const pertDiagramContainer = ref<HTMLElement>();

// Mock PERT data
const pertNodes: PertNode[] = [
  {
    id: 'A',
    name: 'Project Start',
    description: 'Initialize project and setup environment',
    duration: 0,
    optimistic: 0,
    mostLikely: 0,
    pessimistic: 0,
    isCritical: true,
    float: 0,
  },
  {
    id: 'B',
    name: 'Requirements',
    description: 'Gather and analyze requirements',
    duration: 5,
    optimistic: 3,
    mostLikely: 5,
    pessimistic: 8,
    isCritical: true,
    float: 0,
  },
  {
    id: 'C',
    name: 'Design UI',
    description: 'Create user interface designs',
    duration: 8,
    optimistic: 6,
    mostLikely: 8,
    pessimistic: 12,
    isCritical: false,
    float: 2,
  },
  {
    id: 'D',
    name: 'Database Design',
    description: 'Design database schema',
    duration: 6,
    optimistic: 4,
    mostLikely: 6,
    pessimistic: 10,
    isCritical: true,
    float: 0,
  },
  {
    id: 'E',
    name: 'Backend API',
    description: 'Develop REST API endpoints',
    duration: 12,
    optimistic: 10,
    mostLikely: 12,
    pessimistic: 16,
    isCritical: true,
    float: 0,
  },
  {
    id: 'F',
    name: 'Frontend Dev',
    description: 'Develop user interface',
    duration: 10,
    optimistic: 8,
    mostLikely: 10,
    pessimistic: 14,
    isCritical: false,
    float: 2,
  },
  {
    id: 'G',
    name: 'Integration',
    description: 'Integrate frontend and backend',
    duration: 4,
    optimistic: 3,
    mostLikely: 4,
    pessimistic: 6,
    isCritical: true,
    float: 0,
  },
  {
    id: 'H',
    name: 'Testing',
    description: 'Comprehensive testing phase',
    duration: 6,
    optimistic: 4,
    mostLikely: 6,
    pessimistic: 9,
    isCritical: true,
    float: 0,
  },
  {
    id: 'I',
    name: 'Deployment',
    description: 'Deploy to production',
    duration: 2,
    optimistic: 1,
    mostLikely: 2,
    pessimistic: 4,
    isCritical: true,
    float: 0,
  },
];

const connections: Connection[] = [
  { from: 'A', to: 'B', isCritical: true },
  { from: 'B', to: 'C', isCritical: false },
  { from: 'B', to: 'D', isCritical: true },
  { from: 'D', to: 'E', isCritical: true },
  { from: 'C', to: 'F', isCritical: false },
  { from: 'E', to: 'G', isCritical: true },
  { from: 'F', to: 'G', isCritical: false },
  { from: 'G', to: 'H', isCritical: true },
  { from: 'H', to: 'I', isCritical: true },
];

const aiInsights = [
  {
    id: 1,
    message: 'Backend API development is on the critical path - consider additional resources',
    type: 'warning',
    icon: 'warning',
  },
  {
    id: 2,
    message: 'UI Design has 2 days float - can be delayed if needed',
    type: 'info',
    icon: 'info',
  },
  {
    id: 3,
    message: 'Integration phase may need extra time based on complexity',
    type: 'warning',
    icon: 'psychology',
  },
];

// Computed properties
const criticalPathDuration = computed(() => {
  return pertNodes.filter((node) => node.isCritical).reduce((sum, node) => sum + node.duration, 0);
});

const totalTasks = computed(() => pertNodes.length);

const criticalTasks = computed(() => {
  return pertNodes.filter((node) => node.isCritical).length;
});

const riskLevel = computed(() => 75); // Mock risk calculation

const criticalPathTasks = computed(() => {
  return pertNodes.filter((node) => node.isCritical && node.duration > 0);
});

// Methods
function getNodePosition(nodeId: string) {
  // Simple layout algorithm - in real app would use proper graph layout
  const positions: Record<string, { x: number; y: number }> = {
    A: { x: 50, y: 200 },
    B: { x: 200, y: 200 },
    C: { x: 350, y: 100 },
    D: { x: 350, y: 200 },
    E: { x: 500, y: 200 },
    F: { x: 500, y: 100 },
    G: { x: 650, y: 150 },
    H: { x: 800, y: 150 },
    I: { x: 950, y: 150 },
  };
  return positions[nodeId] || { x: 0, y: 0 };
}

function selectNode(node: PertNode) {
  selectedNode.value = node;
}

function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value + 0.1, 2);
}

function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value - 0.1, 0.5);
}

function resetZoom() {
  zoomLevel.value = 1;
}

function aiOptimize() {
  // Simulate AI optimization
  console.log('AI optimizing PERT...');
  // Add a notification to show it's working
  $q.notify({
    message: 'AI optimization completed! Critical path updated.',
    color: 'positive',
    icon: 'psychology',
    position: 'top',
  });
}

function recalculatePert() {
  // Simulate PERT recalculation
  console.log('Recalculating PERT...');
  // Add a notification to show it's working
  $q.notify({
    message: 'PERT diagram recalculated successfully!',
    color: 'positive',
    icon: 'calculate',
    position: 'top',
  });
}
</script>

<style scoped>
.pert-diagram-container {
  overflow: auto;
  transition: transform 0.3s ease;
}

.pert-diagram {
  min-width: 1200px;
  background: white;
}

.pert-node {
  cursor: pointer;
  transition: all 0.2s ease;
}

.pert-node:hover rect {
  filter: brightness(1.1);
}

.pert-node.critical rect {
  filter: drop-shadow(0 2px 4px rgba(244, 67, 54, 0.3));
}

.node-title {
  font-size: 12px;
  font-weight: 600;
  fill: #1976d2;
}

.node-duration {
  font-size: 10px;
  fill: #666;
}

.ai-insight-card {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  border-left: 3px solid var(--q-primary);
}
</style>
