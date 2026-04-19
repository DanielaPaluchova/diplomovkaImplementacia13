<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">PERT Analysis</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Time estimation</p>
        </div>
      </div>

      <!-- Project Selection -->
      <q-select
        v-model="selectedProjectId"
        :options="projectOptions"
        label="Select Project"
        filled
        emit-value
        map-options
        class="q-mt-md"
        style="max-width: 400px"
      >
        <template v-slot:prepend>
          <q-icon name="folder" />
        </template>
      </q-select>
    </div>

    <div v-if="selectedProject" class="q-pa-lg">
        <!-- PERT Summary Cards -->
        <div class="row q-gutter-md q-mb-lg">
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
        </div>

        <!-- PERT Network Diagram -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-bold">
              <q-icon name="account_tree" color="primary" class="q-mr-sm" />
              PERT Network Diagram
            </div>
            <div class="row q-gutter-sm items-center">
              <q-chip color="blue" text-color="white" icon="info">
                Dependent: {{ customNodes.length }} Tasks
              </q-chip>
              <q-chip color="purple" text-color="white" icon="info">
                Independent: {{ independentNodes.length }} Tasks
              </q-chip>
              <q-separator vertical inset />
              <q-btn
                color="primary"
                icon="refresh"
                label="Refresh"
                size="sm"
                @click="refreshDiagram"
              />
              <q-btn flat icon="zoom_in" size="sm" @click="zoomIn" />
              <q-btn flat icon="zoom_out" size="sm" @click="zoomOut" />
              <q-btn flat icon="center_focus_strong" size="sm" @click="resetZoom" />
            </div>
          </div>
          <div class="row q-gutter-xs q-mb-sm items-center">
            <q-chip size="sm" color="blue" text-color="white" icon="circle">Dependent Tasks</q-chip>
            <q-chip size="sm" color="blue" text-color="white" icon="arrow_forward">Dependencies</q-chip>
            <q-chip size="sm" color="purple" text-color="white" icon="workspaces">Independent Tasks</q-chip>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-none">
          <div class="pert-diagram-container" @wheel.prevent="handleWheel">
            <svg
              ref="pertSvg"
              class="pert-diagram"
              :viewBox="`0 0 ${diagramWidth} ${diagramHeight}`"
              @mousedown="startPan"
              @mousemove="handlePan"
              @mouseup="endPan"
              @mouseleave="endPan"
            >
              <!-- Grid Background -->
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" stroke-width="1" />
                </pattern>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="5"
                  orient="auto"
                >
                  <path d="M 2 2 L 8 5 L 2 8" fill="none" stroke="#2196f3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </marker>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              <!-- Connections -->
              <g class="connections" :transform="transform">
                <g
                  v-for="(edge, index) in customEdges"
                  :key="`${edge.from}-${edge.to}-${index}`"
                  class="edge-group"
                >
                  <line
                    :x1="(nodePositions[edge.from]?.x ?? 0) + 60"
                    :y1="(nodePositions[edge.from]?.y ?? 0) + 40"
                    :x2="nodePositions[edge.to]?.x ?? 0"
                    :y2="(nodePositions[edge.to]?.y ?? 0) + 40"
                    stroke="#2196f3"
                    stroke-width="2.5"
                    marker-end="url(#arrowhead)"
                    class="edge-line"
                  />
                </g>
              </g>

              <!-- Dependent Nodes -->
              <g class="nodes" :transform="transform">
                <g
                  v-for="node in customNodes"
                  :key="node.id"
                  :transform="`translate(${nodePositions[node.id]?.x ?? 0}, ${nodePositions[node.id]?.y ?? 0})`"
                  class="pert-node"
                >
                  <rect
                    width="120"
                    height="80"
                    rx="8"
                    fill="#e3f2fd"
                    stroke="#2196f3"
                    stroke-width="2"
                  />
                  <text x="60" y="25" text-anchor="middle" class="node-title">
                    {{ truncateText(node.title, 12) }}
                  </text>
                  <text x="60" y="45" text-anchor="middle" class="node-duration">
                    {{ node.expected }}h
                  </text>
                  <text x="60" y="65" text-anchor="middle" class="node-type">
                    {{ node.type }}
                  </text>
                </g>

                <!-- Independent Nodes -->
                <g
                  v-for="node in independentNodes"
                  :key="node.id"
                  :transform="`translate(${nodePositions[node.id]?.x ?? 0}, ${nodePositions[node.id]?.y ?? 0})`"
                  class="pert-node independent-node"
                >
                  <rect
                    width="120"
                    height="80"
                    rx="8"
                    fill="#f3e5f5"
                    stroke="#9c27b0"
                    stroke-width="2"
                  />
                  <text x="60" y="25" text-anchor="middle" class="node-title">
                    {{ truncateText(node.title, 12) }}
                  </text>
                  <text x="60" y="45" text-anchor="middle" class="node-duration">
                    {{ node.expected }}h
                  </text>
                  <text x="60" y="65" text-anchor="middle" class="node-type">
                    {{ node.type }}
                  </text>
                </g>
              </g>
            </svg>
          </div>
        </q-card-section>
      </q-card>

      <div class="row q-gutter-lg">
        <!-- PERT Tasks Table -->
        <div class="col-12 col-lg-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold">PERT Estimates by Task</div>
            </q-card-section>
            <q-separator />
            <q-card-section class="q-pa-none">
              <q-table
                :rows="taskEstimates"
                :columns="pertColumns"
                row-key="id"
                flat
                :pagination="{ rowsPerPage: 10 }"
              >
                <template v-slot:body-cell-title="props">
                  <q-td :props="props">
                    <div class="text-weight-medium">{{ props.row.title }}</div>
                    <div class="text-caption text-grey-7">{{ props.row.type }}</div>
                  </q-td>
                </template>

                <template v-slot:body-cell-optimistic="props">
                  <q-td :props="props">
                    <q-chip color="green" text-color="white" size="sm">
                      {{ props.row.optimistic }}h
                    </q-chip>
                  </q-td>
                </template>

                <template v-slot:body-cell-mostLikely="props">
                  <q-td :props="props">
                    <q-chip color="primary" text-color="white" size="sm">
                      {{ props.row.mostLikely }}h
                    </q-chip>
                  </q-td>
                </template>

                <template v-slot:body-cell-pessimistic="props">
                  <q-td :props="props">
                    <q-chip color="red" text-color="white" size="sm">
                      {{ props.row.pessimistic }}h
                    </q-chip>
                  </q-td>
                </template>

                <template v-slot:body-cell-expected="props">
                  <q-td :props="props">
                    <div class="text-weight-bold text-primary">{{ props.row.expected }}h</div>
                  </q-td>
                </template>

                <template v-slot:body-cell-stdDev="props">
                  <q-td :props="props">
                    <span v-if="props.row.stdDev != null" class="text-caption">
                      {{ props.row.stdDev }}h
                    </span>
                    <span v-else class="text-grey-5 text-caption">—</span>
                  </q-td>
                </template>

                <template v-slot:body-cell-variance="props">
                  <q-td :props="props">
                    <span v-if="props.row.variance != null" class="text-caption">
                      {{ props.row.variance }}
                    </span>
                    <span v-else class="text-grey-5 text-caption">—</span>
                  </q-td>
                </template>

                <template v-slot:body-cell-cv="props">
                  <q-td :props="props">
                    <q-chip
                      v-if="props.row.cv != null"
                      :color="props.row.cv >= 33 ? 'red' : props.row.cv >= 20 ? 'orange' : 'grey-5'"
                      text-color="white"
                      size="sm"
                    >
                      {{ props.row.cv }}%
                    </q-chip>
                    <span v-else class="text-grey-5 text-caption">—</span>
                  </q-td>
                </template>
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <!-- Task Details & Stats -->
        <div class="col-12 col-lg-4">
          <!-- Status Breakdown -->
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold">Status Breakdown</div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="column q-gutter-sm">
                <div
                  v-for="status in statusBreakdown"
                  :key="status.status"
                  class="row items-center justify-between"
                >
                  <div class="row items-center">
                    <q-chip :color="status.color" text-color="white" size="sm" class="q-mr-sm">
                      {{ status.count }}
                    </q-chip>
                    <span>{{ status.status }}</span>
                  </div>
                  <div class="text-caption text-grey-7">{{ status.hours }}h total</div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <div v-else class="q-pa-xl text-center text-grey-5">
      <q-icon name="folder_open" size="64px" class="q-mb-md" />
      <div class="text-h6">Select a project to view PERT analysis</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useActivityLog } from 'src/composables/useActivityLog';

const $q = useQuasar();
const projectStore = useProjectStore();
const { log } = useActivityLog();

const selectedProjectId = ref<number | null>(null);

// Project options
const projectOptions = computed(() => {
  return projectStore.projects.map((project) => ({
    label: project.name,
    value: project.id,
  }));
});

const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null;
  return projectStore.projects.find((p) => p.id === selectedProjectId.value);
});

// Diagram state
const pertSvg = ref<SVGElement>();
const zoomLevel = ref(1);
const panX = ref(0);
const panY = ref(0);
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });
const diagramWidth = ref(1400);
const diagramHeight = ref(600);

// Node positions
const nodePositions = ref<Record<number, { x: number; y: number }>>({});

// Node and edge types
interface DiagramNode {
  id: number;
  title: string;
  type: string;
  expected: number;
  isIndependent: boolean;
}

interface DiagramEdge {
  from: number;
  to: number;
}

// Nodes and edges (read-only from database)
const customNodes = ref<DiagramNode[]>([]);
const customEdges = ref<DiagramEdge[]>([]);
const independentNodes = ref<DiagramNode[]>([]);

// PERT Columns
const pertColumns = [
  {
    name: 'title',
    label: 'Task',
    field: 'title',
    align: 'left' as const,
    sortable: true,
  },
  {
    name: 'optimistic',
    label: 'Optimistic',
    field: 'optimistic',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'mostLikely',
    label: 'Most Likely',
    field: 'mostLikely',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'pessimistic',
    label: 'Pessimistic',
    field: 'pessimistic',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'expected',
    label: 'Expected',
    field: 'expected',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'stdDev',
    label: 'σ',
    field: 'stdDev',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'variance',
    label: 'Variance',
    field: 'variance',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'cv',
    label: 'CV %',
    field: 'cv',
    align: 'center' as const,
    sortable: true,
  },
];

// PERT statistical formulas (standard PERT: σ = (P-O)/6)
function calcPertStats(
  optimistic: number,
  pessimistic: number,
  expected: number,
): { stdDev: number | null; variance: number | null; cv: number | null } {
  if (optimistic == null || pessimistic == null || expected == null || expected <= 0) {
    return { stdDev: null, variance: null, cv: null };
  }
  const stdDev = (pessimistic - optimistic) / 6;
  const variance = stdDev * stdDev;
  const cv = (stdDev / expected) * 100;
  return { stdDev, variance, cv };
}

// Task estimates from selected project
const taskEstimates = computed(() => {
  if (!selectedProject.value || !selectedProject.value.tasks) return [];

  return selectedProject.value.tasks.map((task) => {
    const optimistic = Number((task.pert.optimistic ?? 0));
    const pessimistic = Number((task.pert.pessimistic ?? 0));
    const expected = Number((task.pert.expected ?? 0).toFixed(2));
    const stats = calcPertStats(optimistic, pessimistic, expected);

    return {
      id: task.id,
      title: task.title,
      type: task.type,
      optimistic: Number(optimistic.toFixed(2)),
      mostLikely: Number((task.pert.mostLikely ?? 0).toFixed(2)),
      pessimistic: Number(pessimistic.toFixed(2)),
      expected,
      stdDev: stats.stdDev != null ? Number(stats.stdDev.toFixed(2)) : null,
      variance: stats.variance != null ? Number(stats.variance.toFixed(3)) : null,
      cv: stats.cv != null ? Number(stats.cv.toFixed(1)) : null,
      status: task.status,
    };
  });
});

// Computed properties
const totalTasks = computed(() => {
  if (!selectedProject.value?.tasks) return 0;
  return selectedProject.value.tasks.length;
});

const statusBreakdown = computed(() => {
  if (!selectedProject.value?.tasks) return [];

  const breakdown: Record<string, { status: string; count: number; hours: number; color: string }> =
    {
      'To Do': { status: 'To Do', count: 0, hours: 0, color: 'grey' },
      'In Progress': { status: 'In Progress', count: 0, hours: 0, color: 'blue' },
      Done: { status: 'Done', count: 0, hours: 0, color: 'green' },
    };

  selectedProject.value.tasks.forEach((task) => {
    const statusData = breakdown[task.status];
    if (statusData) {
      statusData.count++;
      statusData.hours += task.pert.expected || 0;
    }
  });

  return Object.values(breakdown).map((item) => ({
    ...item,
    hours: item.hours.toFixed(2),
  }));
});

const transform = computed(() => {
  return `translate(${panX.value}, ${panY.value}) scale(${zoomLevel.value})`;
});

// Methods
function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Initialize nodes from project tasks
async function initializeCustomNodesFromProject() {
  if (!selectedProject.value || !selectedProject.value.tasks) return;

  const tasks = selectedProject.value.tasks;

  // Build dependency edges from database
  const databaseEdges: DiagramEdge[] = [];
  const allTaskIds = new Set(tasks.map((t) => t.id));

  for (const task of tasks) {
    if (task.dependencies && task.dependencies.length > 0) {
      for (const depId of task.dependencies) {
        // Only add edge if both tasks exist in project
        if (allTaskIds.has(depId)) {
          databaseEdges.push({
            from: depId,
            to: task.id,
          });
        }
      }
    }
  }

  customEdges.value = databaseEdges;

  // Identify independent tasks (no dependencies and no dependents)
  const tasksWithDeps = new Set<number>();
  for (const edge of databaseEdges) {
    tasksWithDeps.add(edge.from);
    tasksWithDeps.add(edge.to);
  }

  // Create nodes
  const allNodes: DiagramNode[] = tasks.map((task) => ({
    id: task.id,
    title: task.title,
    type: task.type,
    expected: Number((task.pert.expected || 0).toFixed(2)),
    isIndependent: !tasksWithDeps.has(task.id),
  }));

  // Separate independent and dependent nodes
  independentNodes.value = allNodes.filter((node) => node.isIndependent);
  customNodes.value = allNodes.filter((node) => !node.isIndependent);

  initializeNodePositions();
}

// Initialize node positions using automatic layout
function initializeNodePositions() {
  if (!selectedProject.value) return;

  const positions: Record<number, { x: number; y: number }> = {};

  // Always use automatic layout
  calculateAutoLayout(positions);

  nodePositions.value = positions;

  updateDiagramSize();
}

// Calculate auto-layout using hierarchical (Sugiyama-style) algorithm
function calculateAutoLayout(existingPositions: Record<number, { x: number; y: number }>) {
  const dependentNodes = customNodes.value;
  const independent = independentNodes.value;

  if (dependentNodes.length === 0 && independent.length === 0) return;

  const horizontalSpacing = 250;
  const verticalSpacing = 180;
  const nodeHeight = 80; // Height of a node
  const sectionBuffer = 150; // Buffer between dependent and independent sections

  let maxDependentY = 0; // Track the maximum Y position of dependent nodes

  // Layout dependent nodes hierarchically
  if (dependentNodes.length > 0) {
    // Build dependency graph
    const inDegree: Record<number, number> = {};
    const outEdges: Record<number, number[]> = {};

    for (const node of dependentNodes) {
      inDegree[node.id] = 0;
      outEdges[node.id] = [];
    }

    for (const edge of customEdges.value) {
      if (inDegree[edge.to] !== undefined) {
        const currentDegree = inDegree[edge.to];
        if (currentDegree !== undefined) {
          inDegree[edge.to] = currentDegree + 1;
        }
      }
      if (outEdges[edge.from]) {
        outEdges[edge.from]?.push(edge.to);
      }
    }

    // Topological sort to assign layers
    const layers: number[][] = [];
    const nodeLayer: Record<number, number> = {};
    const queue: number[] = [];

    // Start with nodes that have no dependencies
    for (const node of dependentNodes) {
      if (inDegree[node.id] === 0) {
        queue.push(node.id);
        nodeLayer[node.id] = 0;
      }
    }

    while (queue.length > 0) {
      const currentId = queue.shift()!;
      const layer = nodeLayer[currentId];

      if (layer !== undefined) {
        if (!layers[layer]) {
          layers[layer] = [];
        }
        layers[layer]?.push(currentId);

        for (const nextId of outEdges[currentId] || []) {
          if (inDegree[nextId] !== undefined) {
            inDegree[nextId]--;
            if (inDegree[nextId] === 0 && layer !== undefined) {
              nodeLayer[nextId] = layer + 1;
              queue.push(nextId);
            }
          }
        }
      }
    }

    // Handle any remaining nodes (cycles or disconnected)
    for (const node of dependentNodes) {
      if (nodeLayer[node.id] === undefined) {
        const lastLayerIndex = layers.length;
        nodeLayer[node.id] = lastLayerIndex;
        if (!layers[lastLayerIndex]) {
          layers[lastLayerIndex] = [];
        }
        layers[lastLayerIndex]?.push(node.id);
      }
    }

    // Position nodes by layer (horizontal layout: left-to-right)
    layers.forEach((layerNodes, layerIndex) => {
      if (!layerNodes) return;
      layerNodes.forEach((nodeId, indexInLayer) => {
        const x = 100 + layerIndex * horizontalSpacing;    // layers go right →
        const y = 100 + indexInLayer * verticalSpacing;    // tasks stacked vertically
        existingPositions[nodeId] = { x, y };

        // Track the maximum Y position (including node height)
        maxDependentY = Math.max(maxDependentY, y + nodeHeight);
      });
    });
  }

  // Calculate Y position for independent section (below all dependent nodes)
  const independentSectionY = maxDependentY > 0 ? maxDependentY + sectionBuffer : 100;

  // Layout independent nodes in a separate swimlane at the bottom
  independent.forEach((node, index) => {
    const x = 100 + (index % 6) * horizontalSpacing;
    const y = independentSectionY + Math.floor(index / 6) * verticalSpacing;
    existingPositions[node.id] = { x, y };
  });
}

// Update diagram size based on node positions
function updateDiagramSize() {
  const positions = Object.values(nodePositions.value);
  if (positions.length === 0) return;

  const maxX = Math.max(...positions.map((p) => p.x)) + 250;
  const maxY = Math.max(...positions.map((p) => p.y)) + 200;
  diagramWidth.value = Math.max(1400, maxX);
  diagramHeight.value = Math.max(800, maxY);
}

// Pan functions
function startPan(event: MouseEvent) {
  if (event.button === 0) {
    isPanning.value = true;
    panStart.value = { x: event.clientX - panX.value, y: event.clientY - panY.value };
  }
}

function handlePan(event: MouseEvent) {
  if (isPanning.value) {
    panX.value = event.clientX - panStart.value.x;
    panY.value = event.clientY - panStart.value.y;
  }
}

function endPan() {
  isPanning.value = false;
}

// Zoom functions
function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value + 0.1, 2);
}

function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value - 0.1, 0.3);
}

function resetZoom() {
  zoomLevel.value = 1;
  panX.value = 0;
  panY.value = 0;
}

function handleWheel(event: WheelEvent) {
  const delta = event.deltaY > 0 ? -0.05 : 0.05;
  zoomLevel.value = Math.max(0.3, Math.min(2, zoomLevel.value + delta));
}

// Refresh diagram - reload from database and reset view
async function refreshDiagram() {
  zoomLevel.value = 1;
  panX.value = 0;
  panY.value = 0;

  // Reload project data from database
  if (selectedProjectId.value) {
    await projectStore.fetchProjects(true);
    await initializeCustomNodesFromProject();

    $q.notify({
      type: 'positive',
      message: 'Diagram refreshed from database'
    });
  }
}

// Initialize on mount
onMounted(async () => {
  // Fetch projects first
  await projectStore.fetchProjects(true);

  // Set default project if available
  if (projectStore.projects.length > 0 && !selectedProjectId.value) {
    const firstProject = projectStore.projects[0];
    if (firstProject) {
      selectedProjectId.value = firstProject.id;
    }
  }

  // Initialize diagram if project is selected
  if (selectedProjectId.value) {
    await initializeCustomNodesFromProject();
  }
});

// Watch for project changes
watch(selectedProjectId, async (newVal) => {
  if (newVal) {
    log('project_select', 'pert_analysis', { projectId: newVal });
    await initializeCustomNodesFromProject();
  }
});
</script>

<style scoped>
.pert-diagram-container {
  width: 100%;
  height: 600px;
  overflow: hidden;
  background: #fafafa;
  cursor: grab;
  user-select: none;
}

.pert-diagram-container:active {
  cursor: grabbing;
}

.pert-diagram {
  width: 100%;
  height: 100%;
}

.pert-node {
  transition: filter 0.2s ease;
}

.node-title {
  font-size: 12px;
  font-weight: 600;
  fill: #1976d2;
}

.node-duration {
  font-size: 14px;
  font-weight: 700;
  fill: #f44336;
}

.node-type {
  font-size: 10px;
  fill: #666;
  text-transform: uppercase;
}

.edge-line {
  transition:
    stroke 0.3s ease,
    stroke-width 0.3s ease;
}


.independent-node rect {
  filter: drop-shadow(0 2px 4px rgba(156, 39, 176, 0.3));
}

.section-label {
  user-select: none;
  pointer-events: none;
}
</style>
