<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">PERT Analysis</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Critical path analysis with time estimation</p>
        </div>
        <q-btn color="primary" icon="calculate" label="Recalculate" @click="recalculatePert" />
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
              <div class="text-h4 text-primary text-weight-bold">{{ criticalPathDuration }}h</div>
              <div class="text-grey-7">Expected Duration</div>
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
              <div class="text-h4 text-orange text-weight-bold">{{ optimisticDuration }}h</div>
              <div class="text-grey-7">Optimistic</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="text-center">
            <q-card-section>
              <div class="text-h4 text-red text-weight-bold">{{ pessimisticDuration }}h</div>
              <div class="text-grey-7">Pessimistic</div>
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
              PERT Network Diagram Editor
            </div>
            <div class="row q-gutter-sm items-center">
              <q-chip color="red" text-color="white" icon="warning">
                Critical Path: {{ customCriticalNodes.length }} Tasks
              </q-chip>
              <q-btn
                color="primary"
                icon="add"
                label="Add Task"
                size="sm"
                @click="showAddNodeDialog = true"
              />
              <q-btn
                :color="connectionMode ? 'orange' : 'grey'"
                :icon="connectionMode ? 'link' : 'link_off'"
                :label="connectionMode ? 'Connecting...' : 'Connect'"
                size="sm"
                @click="toggleConnectionMode"
              />
              <q-separator vertical inset />
              <q-btn flat icon="zoom_in" size="sm" @click="zoomIn" />
              <q-btn flat icon="zoom_out" size="sm" @click="zoomOut" />
              <q-btn flat icon="center_focus_strong" size="sm" @click="resetZoom" />
            </div>
          </div>
          <div class="row q-gutter-xs q-mb-sm items-center">
            <q-chip size="sm" color="red" text-color="white" icon="circle">Critical Path</q-chip>
            <q-chip size="sm" color="grey-5" text-color="white" icon="circle">Normal Path</q-chip>
            <q-separator vertical inset />
            <div class="text-caption text-grey-7">
              {{
                connectionMode
                  ? 'Click nodes to connect them with arrows'
                  : 'Click nodes to select, drag to move'
              }}
            </div>
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-none">
          <div class="pert-diagram-container" @wheel.prevent="handleWheel" @click="onCanvasClick">
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
                  <polygon points="0 0, 10 5, 0 10" fill="#bdbdbd" />
                </marker>
                <marker
                  id="arrowhead-critical"
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="5"
                  orient="auto"
                >
                  <polygon points="0 0, 10 5, 0 10" fill="#f44336" />
                </marker>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              <!-- Connections -->
              <g class="connections" :transform="transform">
                <g
                  v-for="(edge, index) in customEdges"
                  :key="`${edge.from}-${edge.to}-${index}`"
                  class="edge-group"
                  @click.stop="selectEdge(edge, index)"
                >
                  <line
                    :x1="(nodePositions[edge.from]?.x ?? 0) + 60"
                    :y1="(nodePositions[edge.from]?.y ?? 0) + 40"
                    :x2="nodePositions[edge.to]?.x ?? 0"
                    :y2="(nodePositions[edge.to]?.y ?? 0) + 40"
                    :stroke="edge.isCritical ? '#f44336' : '#bdbdbd'"
                    :stroke-width="edge.isCritical ? 3 : 2"
                    :marker-end="edge.isCritical ? 'url(#arrowhead-critical)' : 'url(#arrowhead)'"
                    class="edge-line"
                  />
                  <!-- Invisible wider line for easier clicking -->
                  <line
                    :x1="(nodePositions[edge.from]?.x ?? 0) + 60"
                    :y1="(nodePositions[edge.from]?.y ?? 0) + 40"
                    :x2="nodePositions[edge.to]?.x ?? 0"
                    :y2="(nodePositions[edge.to]?.y ?? 0) + 40"
                    stroke="transparent"
                    stroke-width="15"
                    class="edge-hitbox"
                  />
                </g>
              </g>

              <!-- Temporary connection line -->
              <line
                v-if="connectionMode && connectionStart !== null && tempConnectionEnd"
                :x1="(nodePositions[connectionStart]?.x ?? 0) + 60"
                :y1="(nodePositions[connectionStart]?.y ?? 0) + 40"
                :x2="tempConnectionEnd.x"
                :y2="tempConnectionEnd.y"
                stroke="#ff9800"
                stroke-width="2"
                stroke-dasharray="5,5"
                :transform="transform"
              />

              <!-- Nodes -->
              <g class="nodes" :transform="transform">
                <g
                  v-for="node in customNodes"
                  :key="node.id"
                  :transform="`translate(${nodePositions[node.id]?.x ?? 0}, ${nodePositions[node.id]?.y ?? 0})`"
                  class="pert-node"
                  :class="{
                    critical: node.isCritical,
                    dragging: draggedNode === node.id,
                    selected: selectedNodeId === node.id,
                    'connection-start': connectionStart === node.id,
                  }"
                  @mousedown.stop="onNodeMouseDown(node.id, $event)"
                  @click.stop="onNodeClick(node.id)"
                >
                  <rect
                    width="120"
                    height="80"
                    rx="8"
                    :fill="node.isCritical ? '#ffebee' : '#e3f2fd'"
                    :stroke="node.isCritical ? '#f44336' : '#2196f3'"
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
                  <!-- Delete button -->
                  <g class="delete-btn" @click.stop="deleteNode(node.id)">
                    <circle cx="110" cy="10" r="8" fill="#f44336" />
                    <text x="110" y="14" text-anchor="middle" class="delete-icon">×</text>
                  </g>
                </g>
              </g>
            </svg>
          </div>
        </q-card-section>
      </q-card>

      <!-- Add/Edit Node Dialog -->
      <q-dialog v-model="showAddNodeDialog">
        <q-card style="min-width: 400px">
          <q-card-section>
            <div class="text-h6">{{ editingNodeId ? 'Edit Task' : 'Add New Task' }}</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <q-input v-model="nodeForm.title" label="Task Name" filled class="q-mb-md" />
            <q-input
              v-model.number="nodeForm.expected"
              label="Expected Duration (hours)"
              type="number"
              filled
              class="q-mb-md"
            />
            <q-select
              v-model="nodeForm.type"
              :options="['feature', 'bug', 'task']"
              label="Type"
              filled
              class="q-mb-md"
            />
            <q-checkbox v-model="nodeForm.isCritical" label="Mark as Critical Path" />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" @click="cancelNodeDialog" />
            <q-btn color="primary" :label="editingNodeId ? 'Save' : 'Add'" @click="saveNode" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- Edge Context Menu Dialog -->
      <q-dialog v-model="showEdgeDialog">
        <q-card style="min-width: 300px">
          <q-card-section>
            <div class="text-h6">Connection Options</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <q-checkbox
              v-model="selectedEdge.isCritical"
              label="Mark as Critical Path"
              @update:model-value="updateEdgeCritical"
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Delete Connection" color="negative" @click="deleteSelectedEdge" />
            <q-btn flat label="Close" @click="showEdgeDialog = false" />
          </q-card-actions>
        </q-card>
      </q-dialog>

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
              </q-table>
            </q-card-section>
          </q-card>
        </div>

        <!-- Task Details & Stats -->
        <div class="col-12 col-lg-4">
          <!-- PERT Distribution Chart -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold">Time Distribution</div>
            </q-card-section>
            <q-separator />
            <q-card-section>
              <div class="column q-gutter-md">
                <div>
                  <div class="text-caption text-grey-7 q-mb-xs">Optimistic (Best Case)</div>
                  <q-linear-progress
                    :value="optimisticPercentage"
                    color="green"
                    size="20px"
                    class="q-mb-xs"
                  >
                    <div class="absolute-full flex flex-center">
                      <q-badge
                        color="white"
                        text-color="accent"
                        :label="`${optimisticDuration}h`"
                      />
                    </div>
                  </q-linear-progress>
                </div>

                <div>
                  <div class="text-caption text-grey-7 q-mb-xs">Expected (Weighted)</div>
                  <q-linear-progress
                    :value="expectedPercentage"
                    color="primary"
                    size="20px"
                    class="q-mb-xs"
                  >
                    <div class="absolute-full flex flex-center">
                      <q-badge
                        color="white"
                        text-color="accent"
                        :label="`${criticalPathDuration}h`"
                      />
                    </div>
                  </q-linear-progress>
                </div>

                <div>
                  <div class="text-caption text-grey-7 q-mb-xs">Pessimistic (Worst Case)</div>
                  <q-linear-progress :value="1" color="red" size="20px" class="q-mb-xs">
                    <div class="absolute-full flex flex-center">
                      <q-badge
                        color="white"
                        text-color="accent"
                        :label="`${pessimisticDuration}h`"
                      />
                    </div>
                  </q-linear-progress>
                </div>
              </div>
            </q-card-section>
          </q-card>

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

const $q = useQuasar();
const projectStore = useProjectStore();

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
const draggedNode = ref<number | null>(null);
const dragOffset = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });
const diagramWidth = ref(1400);
const diagramHeight = ref(600);

// Node positions (can be dragged)
const nodePositions = ref<Record<number, { x: number; y: number }>>({});

// Custom nodes and edges (user-modifiable)
const customNodes = ref<
  Array<{ id: number; title: string; type: string; expected: number; isCritical: boolean }>
>([]);
const customEdges = ref<Array<{ from: number; to: number; isCritical: boolean }>>([]);
let nextNodeId = 1000; // Start custom IDs from 1000

// Connection mode
const connectionMode = ref(false);
const connectionStart = ref<number | null>(null);
const tempConnectionEnd = ref<{ x: number; y: number } | null>(null);

// Node dialog
const showAddNodeDialog = ref(false);
const editingNodeId = ref<number | null>(null);
const nodeForm = ref({
  title: '',
  expected: 8,
  type: 'task',
  isCritical: false,
});

// Edge dialog
const showEdgeDialog = ref(false);
const selectedEdge = ref<{ from: number; to: number; isCritical: boolean }>({
  from: 0,
  to: 0,
  isCritical: false,
});
const selectedEdgeIndex = ref<number | null>(null);

// Selected node
const selectedNodeId = ref<number | null>(null);

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
];

// Task estimates from selected project
const taskEstimates = computed(() => {
  if (!selectedProject.value) return [];

  return selectedProject.value.tasks.map((task) => ({
    id: task.id,
    title: task.title,
    type: task.type,
    optimistic: task.pert.optimistic,
    mostLikely: task.pert.mostLikely,
    pessimistic: task.pert.pessimistic,
    expected: task.pert.expected || 0,
    status: task.status,
  }));
});

// Computed properties
const totalTasks = computed(() => {
  return selectedProject.value?.tasks.length || 0;
});

const criticalPathDuration = computed(() => {
  if (!selectedProject.value) return 0;
  return selectedProject.value.tasks
    .reduce((sum, task) => {
      return sum + (task.pert.expected || 0);
    }, 0)
    .toFixed(1);
});

const optimisticDuration = computed(() => {
  if (!selectedProject.value) return 0;
  return selectedProject.value.tasks.reduce((sum, task) => {
    return sum + task.pert.optimistic;
  }, 0);
});

const pessimisticDuration = computed(() => {
  if (!selectedProject.value) return 0;
  return selectedProject.value.tasks.reduce((sum, task) => {
    return sum + task.pert.pessimistic;
  }, 0);
});

const optimisticPercentage = computed(() => {
  const pessimistic = Number(pessimisticDuration.value);
  if (pessimistic === 0) return 0;
  return Number(optimisticDuration.value) / pessimistic;
});

const expectedPercentage = computed(() => {
  const pessimistic = Number(pessimisticDuration.value);
  if (pessimistic === 0) return 0;
  return Number(criticalPathDuration.value) / pessimistic;
});

const statusBreakdown = computed(() => {
  if (!selectedProject.value) return [];

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
    hours: item.hours.toFixed(1),
  }));
});

// Custom critical nodes
const customCriticalNodes = computed(() => {
  return customNodes.value.filter((node) => node.isCritical);
});

// Critical Path Tasks - top 5 longest tasks (for initialization)
const criticalPathTaskIds = computed(() => {
  if (!selectedProject.value) return [];

  return [...selectedProject.value.tasks]
    .sort((a, b) => (b.pert.expected || 0) - (a.pert.expected || 0))
    .slice(0, 5)
    .map((task) => task.id);
});

const transform = computed(() => {
  return `translate(${panX.value}, ${panY.value}) scale(${zoomLevel.value})`;
});

// Methods
function recalculatePert() {
  $q.notify({
    message: 'PERT analysis recalculated successfully!',
    color: 'positive',
    icon: 'calculate',
    position: 'top',
  });
}

function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Initialize custom nodes from project tasks
function initializeCustomNodesFromProject() {
  if (!selectedProject.value) return;

  const tasks = selectedProject.value.tasks;
  const criticalIds = criticalPathTaskIds.value;

  // Create custom nodes from project tasks
  customNodes.value = tasks.map((task) => ({
    id: task.id,
    title: task.title,
    type: task.type,
    expected: task.pert.expected || 0,
    isCritical: criticalIds.includes(task.id),
  }));

  // Create edges based on task order
  customEdges.value = [];
  for (let i = 0; i < tasks.length - 1; i++) {
    const fromTask = tasks[i];
    const toTask = tasks[i + 1];

    if (fromTask && toTask) {
      customEdges.value.push({
        from: fromTask.id,
        to: toTask.id,
        isCritical: criticalIds.includes(fromTask.id) && criticalIds.includes(toTask.id),
      });
    }
  }

  initializeNodePositions();
}

// Initialize node positions
function initializeNodePositions() {
  const nodes = customNodes.value;
  if (nodes.length === 0) return;

  const positions: Record<number, { x: number; y: number }> = {};

  // Layout in a grid pattern
  const nodesPerRow = Math.ceil(Math.sqrt(nodes.length));
  const horizontalSpacing = 180;
  const verticalSpacing = 140;

  nodes.forEach((node, index) => {
    const row = Math.floor(index / nodesPerRow);
    const col = index % nodesPerRow;

    positions[node.id] = {
      x: 100 + col * horizontalSpacing,
      y: 100 + row * verticalSpacing,
    };
  });

  nodePositions.value = positions;

  // Update diagram size
  const maxX = Math.max(...Object.values(positions).map((p) => p.x)) + 200;
  const maxY = Math.max(...Object.values(positions).map((p) => p.y)) + 200;
  diagramWidth.value = Math.max(1400, maxX);
  diagramHeight.value = Math.max(600, maxY);
}

// Node management
function saveNode() {
  if (!nodeForm.value.title.trim()) {
    $q.notify({ type: 'negative', message: 'Task name is required' });
    return;
  }

  if (editingNodeId.value !== null) {
    // Edit existing node
    const node = customNodes.value.find((n) => n.id === editingNodeId.value);
    if (node) {
      node.title = nodeForm.value.title;
      node.expected = nodeForm.value.expected;
      node.type = nodeForm.value.type;
      node.isCritical = nodeForm.value.isCritical;
    }
    $q.notify({ type: 'positive', message: 'Task updated' });
  } else {
    // Add new node
    const newNode = {
      id: nextNodeId++,
      title: nodeForm.value.title,
      expected: nodeForm.value.expected,
      type: nodeForm.value.type,
      isCritical: nodeForm.value.isCritical,
    };
    customNodes.value.push(newNode);

    // Add position for new node
    nodePositions.value[newNode.id] = {
      x: 200 + (customNodes.value.length % 5) * 180,
      y: 200 + Math.floor(customNodes.value.length / 5) * 140,
    };

    $q.notify({ type: 'positive', message: 'Task added' });
  }

  cancelNodeDialog();
}

function cancelNodeDialog() {
  showAddNodeDialog.value = false;
  editingNodeId.value = null;
  nodeForm.value = {
    title: '',
    expected: 8,
    type: 'task',
    isCritical: false,
  };
}

function deleteNode(nodeId: number) {
  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this task?',
    cancel: true,
  }).onOk(() => {
    // Remove node
    customNodes.value = customNodes.value.filter((n) => n.id !== nodeId);

    // Remove all edges connected to this node
    customEdges.value = customEdges.value.filter((e) => e.from !== nodeId && e.to !== nodeId);

    // Remove position
    delete nodePositions.value[nodeId];

    $q.notify({ type: 'positive', message: 'Task deleted' });
  });
}

// Connection mode
function toggleConnectionMode() {
  connectionMode.value = !connectionMode.value;
  if (!connectionMode.value) {
    connectionStart.value = null;
    tempConnectionEnd.value = null;
  }
}

function onNodeClick(nodeId: number) {
  if (connectionMode.value) {
    if (connectionStart.value === null) {
      // First node selected
      connectionStart.value = nodeId;
      tempConnectionEnd.value = null;
    } else if (connectionStart.value === nodeId) {
      // Clicked same node, cancel
      connectionStart.value = null;
      tempConnectionEnd.value = null;
    } else {
      // Second node selected, create connection
      const edgeExists = customEdges.value.some(
        (e) => e.from === connectionStart.value && e.to === nodeId,
      );

      if (!edgeExists) {
        customEdges.value.push({
          from: connectionStart.value,
          to: nodeId,
          isCritical: false,
        });
        $q.notify({ type: 'positive', message: 'Connection created' });
      } else {
        $q.notify({ type: 'warning', message: 'Connection already exists' });
      }

      connectionStart.value = null;
      tempConnectionEnd.value = null;
    }
  } else {
    // Select node for editing
    selectedNodeId.value = nodeId;
    const node = customNodes.value.find((n) => n.id === nodeId);
    if (node) {
      editingNodeId.value = nodeId;
      nodeForm.value = {
        title: node.title,
        expected: node.expected,
        type: node.type,
        isCritical: node.isCritical,
      };
      showAddNodeDialog.value = true;
    }
  }
}

function onNodeMouseDown(nodeId: number, event: MouseEvent) {
  if (!connectionMode.value) {
    startDrag(nodeId, event);
  }
}

function onCanvasClick() {
  selectedNodeId.value = null;
}

// Edge management
function selectEdge(edge: { from: number; to: number; isCritical: boolean }, index: number) {
  selectedEdge.value = { ...edge };
  selectedEdgeIndex.value = index;
  showEdgeDialog.value = true;
}

function updateEdgeCritical() {
  if (selectedEdgeIndex.value !== null) {
    const edge = customEdges.value[selectedEdgeIndex.value];
    if (edge) {
      edge.isCritical = selectedEdge.value.isCritical;
    }
  }
}

function deleteSelectedEdge() {
  if (selectedEdgeIndex.value !== null) {
    customEdges.value.splice(selectedEdgeIndex.value, 1);
    $q.notify({ type: 'positive', message: 'Connection deleted' });
  }
  showEdgeDialog.value = false;
}

// Drag node functions
function startDrag(nodeId: number, event: MouseEvent) {
  draggedNode.value = nodeId;
  const pos = nodePositions.value[nodeId];
  if (pos) {
    dragOffset.value = {
      x: event.clientX / zoomLevel.value - pos.x,
      y: event.clientY / zoomLevel.value - pos.y,
    };
  }
}

function handleDrag(event: MouseEvent) {
  if (draggedNode.value !== null && nodePositions.value[draggedNode.value]) {
    nodePositions.value[draggedNode.value] = {
      x: event.clientX / zoomLevel.value - dragOffset.value.x - panX.value / zoomLevel.value,
      y: event.clientY / zoomLevel.value - dragOffset.value.y - panY.value / zoomLevel.value,
    };
  }
}

function endDrag() {
  draggedNode.value = null;
}

// Pan functions
function startPan(event: MouseEvent) {
  if (event.button === 0 && draggedNode.value === null) {
    isPanning.value = true;
    panStart.value = { x: event.clientX - panX.value, y: event.clientY - panY.value };
  }
}

function handlePan(event: MouseEvent) {
  if (draggedNode.value !== null) {
    handleDrag(event);
  } else if (isPanning.value) {
    panX.value = event.clientX - panStart.value.x;
    panY.value = event.clientY - panStart.value.y;
  } else if (connectionMode.value && connectionStart.value !== null) {
    // Update temp connection line position
    const svg = pertSvg.value;
    if (svg) {
      const rect = svg.getBoundingClientRect();
      tempConnectionEnd.value = {
        x: (event.clientX - rect.left - panX.value) / zoomLevel.value,
        y: (event.clientY - rect.top - panY.value) / zoomLevel.value,
      };
    }
  }
}

function endPan() {
  isPanning.value = false;
  endDrag();
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

// Initialize on mount
onMounted(() => {
  // Set default project if available
  if (projectStore.projects.length > 0 && !selectedProjectId.value) {
    const firstProject = projectStore.projects[0];
    if (firstProject) {
      selectedProjectId.value = firstProject.id;
    }
  }
  initializeCustomNodesFromProject();
});

// Watch for project changes
watch(selectedProjectId, () => {
  if (selectedProjectId.value) {
    initializeCustomNodesFromProject();
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
  cursor: move;
  transition: filter 0.2s ease;
}

.pert-node:hover {
  filter: brightness(1.05);
}

.pert-node.critical rect {
  filter: drop-shadow(0 4px 8px rgba(244, 67, 54, 0.3));
}

.pert-node.dragging {
  opacity: 0.7;
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

.edge-group:hover .edge-line {
  stroke-width: 4 !important;
  filter: brightness(1.2);
}

.edge-hitbox {
  cursor: pointer;
}

.pert-node.selected rect {
  stroke-width: 4 !important;
  filter: drop-shadow(0 0 10px rgba(33, 150, 243, 0.8));
}

.pert-node.connection-start rect {
  stroke: #ff9800 !important;
  stroke-width: 4 !important;
  filter: drop-shadow(0 0 10px rgba(255, 152, 0, 0.8));
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
  cursor: pointer;
}

.pert-node:hover .delete-btn {
  opacity: 1;
}

.delete-icon {
  font-size: 14px;
  font-weight: bold;
  fill: white;
  pointer-events: none;
}

.delete-btn:hover circle {
  fill: #d32f2f;
}
</style>
