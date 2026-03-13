<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Critical Path Analysis</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Epic dependencies and critical path</p>
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
      <!-- Loading State -->
      <div v-if="loading" class="row justify-center q-py-xl">
        <q-spinner color="primary" size="50px" />
      </div>

      <!-- Empty State -->
      <div v-else-if="epics.length === 0" class="row justify-center q-py-xl">
        <div class="text-center">
          <q-icon name="star_border" size="80px" color="grey-5" />
          <div class="text-h6 text-grey-7 q-mt-md">No epics to display</div>
          <div class="text-body2 text-grey-6 q-mt-sm">
            Create epics first to see critical path analysis
          </div>
        </div>
      </div>

      <!-- Critical Path Content -->
      <div v-else>
        <!-- Critical Path Summary -->
        <div class="row q-gutter-md q-mb-lg">
          <div class="col">
            <q-card class="text-center">
              <q-card-section class="q-pa-md">
                <div class="text-h4 text-primary text-weight-bold">
                  {{ epics.length }}
                </div>
                <div class="text-caption text-grey-7">Total Epics</div>
              </q-card-section>
            </q-card>
          </div>
          <div v-if="criticalPathData" class="col">
            <q-card class="text-center">
              <q-card-section class="q-pa-md">
                <div class="text-h4 text-red text-weight-bold">
                  {{ criticalPathData.criticalPath.length }}
                </div>
                <div class="text-caption text-grey-7">Critical Epics</div>
              </q-card-section>
            </q-card>
          </div>
          <div v-if="criticalPathData" class="col">
            <q-card class="text-center">
              <q-card-section class="q-pa-md">
                <div class="text-h4 text-orange text-weight-bold">
                  {{ criticalPathData.projectDuration.toFixed(1) }}
                </div>
                <div class="text-caption text-grey-7">Critical Path (days)</div>
              </q-card-section>
            </q-card>
          </div>
          <div v-if="criticalPathData && independentEpicsDuration > 0" class="col">
            <q-card class="text-center">
              <q-card-section class="q-pa-md">
                <div class="text-h4 text-purple text-weight-bold">
                  +{{ independentEpicsDuration.toFixed(1) }}
                </div>
                <div class="text-caption text-grey-7">Independent (days)</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- Epic Network Diagram -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="row items-center justify-between q-mb-md">
              <div class="text-h6 text-weight-bold">
                <q-icon name="hub" color="primary" class="q-mr-sm" />
                Epic Dependency Network
              </div>
              <div class="row q-gutter-sm items-center">
                <q-chip color="blue" text-color="white" icon="info">
                  Connected: {{ connectedEpics.length }}
                </q-chip>
                <q-chip color="purple" text-color="white" icon="info">
                  Independent: {{ independentEpics.length }}
                </q-chip>
                <q-separator vertical inset />
                <q-btn
                  color="primary"
                  icon="timeline"
                  label="Calculate Critical Path"
                  @click="calculateCriticalPath"
                  :loading="loadingCriticalPath"
                />
                <q-separator vertical inset />
                <q-btn flat icon="zoom_in" size="sm" @click="zoomIn" />
                <q-btn flat icon="zoom_out" size="sm" @click="zoomOut" />
                <q-btn flat icon="center_focus_strong" size="sm" @click="resetZoom" />
              </div>
            </div>

            <div class="row q-gutter-xs q-mb-sm items-center">
              <q-chip size="sm" color="blue" text-color="white" icon="circle">
                Connected Epics
              </q-chip>
              <q-chip size="sm" color="purple" text-color="white" icon="workspaces">
                Isolated Epics
              </q-chip>
              <q-chip size="sm" color="blue" text-color="white" icon="arrow_forward">
                Dependencies
              </q-chip>
              <q-chip size="sm" color="red" text-color="white" icon="timeline">
                Critical Path
              </q-chip>
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
                  <pattern id="grid-critical" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f0f0f0" stroke-width="1" />
                  </pattern>
                  <marker
                    id="arrowhead-critical"
                    markerWidth="10"
                    markerHeight="10"
                    refX="9"
                    refY="5"
                    orient="auto"
                  >
                    <path d="M 2 2 L 8 5 L 2 8" fill="none" stroke="#f44336" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </marker>
                  <marker
                    id="arrowhead-normal"
                    markerWidth="10"
                    markerHeight="10"
                    refX="9"
                    refY="5"
                    orient="auto"
                  >
                    <path d="M 2 2 L 8 5 L 2 8" fill="none" stroke="#2196f3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </marker>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid-critical)" />

                <!-- Section Label for Independent Epics -->
                <g :transform="transform" v-if="independentEpics.length > 0">
                  <text
                    :x="100"
                    :y="independentSectionY"
                    class="section-label"
                    fill="#9c27b0"
                    font-size="14"
                    font-weight="600"
                  >
                    Independent Epics (No Dependencies)
                  </text>
                </g>

                <!-- Dependency Arrows (with transform) -->
                <g class="connections" :transform="transform">
                  <g v-for="edge in edges" :key="`${edge.from}-${edge.to}`" class="edge-group">
                    <line
                      :x1="edge.x1"
                      :y1="edge.y1"
                      :x2="edge.x2"
                      :y2="edge.y2"
                      :stroke="isEdgeOnCriticalPath(edge.from, edge.to) ? '#f44336' : '#2196f3'"
                      :stroke-width="isEdgeOnCriticalPath(edge.from, edge.to) ? 3 : 2"
                      :marker-end="isEdgeOnCriticalPath(edge.from, edge.to) ? 'url(#arrowhead-critical)' : 'url(#arrowhead-normal)'"
                      class="edge-line"
                    />
                  </g>
                </g>

                <!-- Epic Nodes (with transform) -->
                <g class="nodes" :transform="transform">
                  <!-- All Epics with color based on critical path -->
                  <g
                    v-for="epic in positionedEpics"
                    :key="epic.id"
                    :transform="`translate(${epic.x}, ${epic.y})`"
                    class="epic-node"
                    :class="{ 'independent-epic': independentEpics.some(e => e.id === epic.id) && !isOnCriticalPath(epic.id) }"
                  >
                    <!-- Node Rectangle -->
                    <rect
                      :width="nodeWidth"
                      :height="nodeHeight"
                      :fill="getNodeFill(epic)"
                      :stroke="getNodeStroke(epic)"
                      :stroke-width="isOnCriticalPath(epic.id) ? 3 : 2"
                      rx="8"
                    />

                    <!-- Epic Name -->
                    <text
                      :x="nodeWidth / 2"
                      :y="30"
                      text-anchor="middle"
                      class="node-title"
                      :fill="getNodeTextColor(epic)"
                    >
                      {{ truncateText(epic.name, 18) }}
                    </text>

                    <!-- Duration -->
                    <text
                      :x="nodeWidth / 2"
                      :y="50"
                      text-anchor="middle"
                      class="node-duration"
                      :fill="isOnCriticalPath(epic.id) ? '#d32f2f' : '#333'"
                    >
                      {{ getEpicDuration(epic) }}d
                    </text>

                    <!-- Business Value -->
                    <text :x="nodeWidth / 2" :y="68" text-anchor="middle" class="node-type">
                      BV: {{ epic.businessValue }}
                    </text>

                    <!-- Status Badge -->
                    <rect
                      :x="8"
                      :y="8"
                      width="35"
                      height="14"
                      :fill="getStatusColor(epic.status)"
                      rx="3"
                    />
                    <text x="25.5" y="18" text-anchor="middle" class="status-text">
                      {{ getStatusLabel(epic.status).substring(0, 2) }}
                    </text>
                  </g>
                </g>
              </svg>
            </div>
          </q-card-section>
        </q-card>

        <!-- Critical Path Calculations -->
        <q-card v-if="criticalPathData">
          <q-card-section class="bg-red-1">
            <div class="text-h6 text-weight-bold text-red-9">
              <q-icon name="timeline" class="q-mr-sm" />
              Critical Path Details
            </div>
          </q-card-section>

          <q-card-section>
            <div class="row items-center q-gutter-md q-mb-md">
              <div>
                <div class="text-caption text-grey-7">Critical Path Duration</div>
                <div class="text-h5 text-orange text-weight-bold">
                  {{ criticalPathData.projectDuration.toFixed(1) }} days
                </div>
              </div>
              <div v-if="independentEpicsDuration > 0">
                <div class="text-caption text-grey-7">+ Independent Epics</div>
                <div class="text-h5 text-purple text-weight-bold">
                  +{{ independentEpicsDuration.toFixed(1) }} days
                </div>
              </div>
              <q-separator vertical inset />
              <div>
                <div class="text-caption text-grey-7">Total Estimated Duration</div>
                <div class="text-h5 text-primary text-weight-bold">
                  = {{ (criticalPathData.projectDuration + independentEpicsDuration).toFixed(1) }} days
                </div>
              </div>
            </div>

            <q-banner v-if="independentEpics.length > 0" class="bg-purple-1 text-purple-9 q-mb-md" rounded>
              <template v-slot:avatar>
                <q-icon name="info" color="purple" />
              </template>
              <div class="text-body2">
                <strong>Note:</strong> Independent epics ({{ independentEpics.length }}) can be worked on in parallel with the critical path, 
                potentially reducing total project time if resources are available.
              </div>
            </q-banner>

            <div class="text-subtitle2 q-mb-sm">Critical Path Sequence:</div>
            <div class="row q-gutter-xs q-mb-lg">
              <q-chip
                v-for="epicId in criticalPathData.criticalPath"
                :key="epicId"
                color="red"
                text-color="white"
                icon="star"
              >
                {{ getEpicName(epicId) }}
              </q-chip>
            </div>

            <q-table
              :rows="criticalPathTableData"
              :columns="criticalPathColumns"
              row-key="epicId"
              flat
              bordered
              :rows-per-page-options="[0]"
            >
              <template v-slot:body-cell-epicName="props">
                <q-td :props="props">
                  <div class="row items-center q-gutter-xs">
                    <q-icon
                      v-if="props.row.isCritical"
                      name="warning"
                      color="red"
                      size="sm"
                    />
                    <span :class="{ 'text-weight-bold text-red': props.row.isCritical }">
                      {{ props.row.epicName }}
                    </span>
                  </div>
                </q-td>
              </template>

              <template v-slot:body-cell-slack="props">
                <q-td :props="props">
                  <q-chip
                    :color="props.row.slack === 0 ? 'red' : 'green'"
                    text-color="white"
                    size="sm"
                  >
                    {{ props.row.slack.toFixed(1) }}
                  </q-chip>
                </q-td>
              </template>

              <template v-slot:body-cell-isCritical="props">
                <q-td :props="props">
                  <q-icon
                    :name="props.row.isCritical ? 'check_circle' : 'cancel'"
                    :color="props.row.isCritical ? 'red' : 'grey'"
                    size="md"
                  />
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div v-else class="q-pa-xl text-center text-grey-5">
      <q-icon name="folder_open" size="64px" class="q-mb-md" />
      <div class="text-h6">Select a project to view critical path analysis</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useEpicStore, type Epic, type EpicCriticalPathResponse } from 'src/stores/epic-store';

const $q = useQuasar();
const projectStore = useProjectStore();
const epicStore = useEpicStore();

const selectedProjectId = ref<number | null>(null);
const loading = ref(false);
const loadingCriticalPath = ref(false);
const criticalPathData = ref<EpicCriticalPathResponse | null>(null);

const zoomLevel = ref(1);
const panX = ref(0);
const panY = ref(0);
const isPanning = ref(false);
const panStartX = ref(0);
const panStartY = ref(0);

// Diagram settings
const diagramWidth = 2000;
const diagramHeight = 1500;
const nodeWidth = 180;
const nodeHeight = 80;

// Transform for SVG group (zoom + pan)
const transform = computed(() => {
  return `translate(${panX.value}, ${panY.value}) scale(${zoomLevel.value})`;
});

const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null;
  return projectStore.projects.find((p) => p.id === selectedProjectId.value);
});

const projectOptions = computed(() => {
  return projectStore.projects.map((project) => ({
    label: project.name,
    value: project.id,
  }));
});

const epics = computed(() => epicStore.epics);

// Calculate total duration of independent epics
const independentEpicsDuration = computed(() => {
  return independentEpics.value.reduce((sum, epic) => {
    return sum + (epic.pert.expected || 0);
  }, 0);
});

// Build dependency graph
const dependencyGraph = computed(() => {
  const graph = new Map<number, number[]>();
  epics.value.forEach((epic) => {
    if (!graph.has(epic.id)) {
      graph.set(epic.id, []);
    }
    if (epic.dependencies) {
      epic.dependencies.forEach((depId) => {
        if (!graph.has(depId)) {
          graph.set(depId, []);
        }
        graph.get(depId)!.push(epic.id);
      });
    }
  });
  return graph;
});

// Calculate levels using BFS for cleaner layout (only for connected epics)
const epicLevels = computed(() => {
  const levels = new Map<number, number>();
  const inDegree = new Map<number, number>();

  // Calculate in-degrees only for connected epics
  connectedEpics.value.forEach((epic) => {
    inDegree.set(epic.id, epic.dependencies?.length || 0);
  });

  // BFS to assign levels
  const queue: number[] = [];
  connectedEpics.value.forEach((epic) => {
    if ((inDegree.get(epic.id) || 0) === 0) {
      levels.set(epic.id, 0);
      queue.push(epic.id);
    }
  });

  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentLevel = levels.get(current) || 0;

    const dependents = dependencyGraph.value.get(current) || [];
    dependents.forEach((depId) => {
      // Only process if it's a connected epic
      if (connectedEpics.value.some(e => e.id === depId)) {
        const currentDepLevel = levels.get(depId) || 0;
        levels.set(depId, Math.max(currentDepLevel, currentLevel + 1));

        const degree = (inDegree.get(depId) || 1) - 1;
        inDegree.set(depId, degree);
        if (degree === 0 && !queue.includes(depId)) {
          queue.push(depId);
        }
      }
    });
  }

  return levels;
});

// Group connected epics by level
const epicsByLevel = computed(() => {
  const groups = new Map<number, Epic[]>();
  
  connectedEpics.value.forEach((epic) => {
    const level = epicLevels.value.get(epic.id) ?? 0;
    if (!groups.has(level)) {
      groups.set(level, []);
    }
    groups.get(level)!.push(epic);
  });

  return groups;
});

// Find epics that others depend on
const epicsWithDependents = computed(() => {
  const epicIds = new Set<number>();
  epics.value.forEach((epic) => {
    if (epic.dependencies) {
      epic.dependencies.forEach((depId) => {
        epicIds.add(depId);
      });
    }
  });
  return epicIds;
});

// Truly independent epics: no dependencies AND nobody depends on them
const independentEpics = computed(() => {
  return epics.value.filter(
    (epic) => 
      (!epic.dependencies || epic.dependencies.length === 0) && // No dependencies
      !epicsWithDependents.value.has(epic.id) // Nobody depends on this epic
  );
});

// Connected epics: part of dependency chain
const connectedEpics = computed(() => {
  return epics.value.filter(
    (epic) => 
      (epic.dependencies && epic.dependencies.length > 0) || // Has dependencies
      epicsWithDependents.value.has(epic.id) // Or someone depends on it
  );
});

// Position all epics with optimized layout
const positionedEpics = computed(() => {
  const positioned: Array<Epic & { x: number; y: number }> = [];
  
  const horizontalSpacing = 380;
  const verticalSpacing = 160;
  const startX = 100;
  const startY = 100;

  // Position connected epics level by level
  Array.from(epicsByLevel.value.keys())
    .sort((a, b) => a - b)
    .forEach((level) => {
      const epicsInLevel = epicsByLevel.value.get(level) || [];
      
      epicsInLevel.forEach((epic, index) => {
        positioned.push({
          ...epic,
          x: startX + level * horizontalSpacing,
          y: startY + index * verticalSpacing,
        });
      });
    });

  // Calculate max Y from connected epics
  const maxY = positioned.length > 0 
    ? Math.max(...positioned.map(e => e.y))
    : startY;

  // Position truly independent epics at bottom
  const independentY = maxY + 250;
  const independentSpacing = 280;
  
  independentEpics.value.forEach((epic, index) => {
    positioned.push({
      ...epic,
      x: startX + index * independentSpacing,
      y: independentY,
    });
  });

  return positioned;
});

// Y position for independent section label
const independentSectionY = computed(() => {
  const firstIndependent = positionedEpics.value.find(e => 
    independentEpics.value.some(d => d.id === e.id)
  );
  return firstIndependent ? firstIndependent.y - 40 : 900;
});

// Create edges for dependencies (without zoom/pan - that's handled by transform)
const edges = computed(() => {
  const result: Array<{
    from: number;
    to: number;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  }> = [];

  positionedEpics.value.forEach((epic) => {
    if (epic.dependencies) {
      epic.dependencies.forEach((depId) => {
        const depEpic = positionedEpics.value.find((e) => e.id === depId);
        if (depEpic) {
          result.push({
            from: depId,
            to: epic.id,
            x1: depEpic.x + nodeWidth,
            y1: depEpic.y + nodeHeight / 2,
            x2: epic.x,
            y2: epic.y + nodeHeight / 2,
          });
        }
      });
    }
  });

  return result;
});

// Critical path table data
const criticalPathTableData = computed(() => {
  if (!criticalPathData.value) return [];
  return Object.values(criticalPathData.value.epicSchedule).sort((a, b) => {
    if (a.isCritical && !b.isCritical) return -1;
    if (!a.isCritical && b.isCritical) return 1;
    return a.earlyStart - b.earlyStart;
  });
});

const criticalPathColumns = [
  { name: 'epicName', label: 'Epic Name', field: 'epicName', align: 'left' as const },
  { name: 'duration', label: 'Duration (days)', field: 'duration', align: 'center' as const },
  { name: 'earlyStart', label: 'Early Start', field: 'earlyStart', align: 'center' as const },
  { name: 'earlyFinish', label: 'Early Finish', field: 'earlyFinish', align: 'center' as const },
  { name: 'lateStart', label: 'Late Start', field: 'lateStart', align: 'center' as const },
  { name: 'lateFinish', label: 'Late Finish', field: 'lateFinish', align: 'center' as const },
  { name: 'slack', label: 'Slack', field: 'slack', align: 'center' as const },
  { name: 'isCritical', label: 'Critical', field: 'isCritical', align: 'center' as const },
];

async function loadEpics() {
  if (!selectedProjectId.value) return;
  
  loading.value = true;
  try {
    await epicStore.fetchEpics(selectedProjectId.value, false);
    // Auto-calculate critical path when epics are loaded
    await calculateCriticalPath();
  } catch (error) {
    console.error('Failed to load epics:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load epics',
    });
  } finally {
    loading.value = false;
  }
}

async function calculateCriticalPath() {
  if (!selectedProjectId.value) return;
  
  loadingCriticalPath.value = true;
  try {
    const data = await epicStore.getCriticalPath(selectedProjectId.value);
    criticalPathData.value = data;
    
    $q.notify({
      type: 'positive',
      message: `Critical path calculated: ${data.projectDuration.toFixed(1)} days`,
    });
  } catch (error) {
    console.error('Failed to calculate critical path:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to calculate critical path',
    });
  } finally {
    loadingCriticalPath.value = false;
  }
}

function isOnCriticalPath(epicId: number): boolean {
  if (!criticalPathData.value) return false;
  return criticalPathData.value.criticalPath.includes(epicId);
}

function isEdgeOnCriticalPath(fromId: number, toId: number): boolean {
  if (!criticalPathData.value) return false;
  const path = criticalPathData.value.criticalPath;
  const fromIndex = path.indexOf(fromId);
  const toIndex = path.indexOf(toId);
  return fromIndex !== -1 && toIndex !== -1 && toIndex === fromIndex + 1;
}

function getNodeFill(epic: Epic): string {
  if (isOnCriticalPath(epic.id)) {
    return '#ffebee'; // Red background for critical path
  }
  const isIndependent = independentEpics.value.some(e => e.id === epic.id);
  return isIndependent ? '#f3e5f5' : '#e3f2fd'; // Purple for independent, blue for dependent
}

function getNodeStroke(epic: Epic): string {
  if (isOnCriticalPath(epic.id)) {
    return '#f44336'; // Red stroke for critical path
  }
  const isIndependent = independentEpics.value.some(e => e.id === epic.id);
  return isIndependent ? '#9c27b0' : '#2196f3'; // Purple for independent, blue for dependent
}

function getNodeTextColor(epic: Epic): string {
  if (isOnCriticalPath(epic.id)) {
    return '#d32f2f'; // Red text for critical path
  }
  const isIndependent = independentEpics.value.some(e => e.id === epic.id);
  return isIndependent ? '#6a1b9a' : '#1976d2'; // Purple for independent, blue for dependent
}

function getEpicName(epicId: number): string {
  const epic = epics.value.find((e) => e.id === epicId);
  return epic?.name || `Epic #${epicId}`;
}

function getEpicDuration(epic: Epic): string {
  if (epic.pert.expected !== null && epic.pert.expected !== undefined) {
    return epic.pert.expected.toFixed(1);
  }
  return 'N/A';
}

function getStatusColor(status: string): string {
  if (status === 'to_do' || status === 'not_started') {
    return '#9e9e9e';
  }
  switch (status) {
    case 'in_progress':
      return '#2196f3';
    case 'completed':
      return '#4caf50';
    default:
      return '#9e9e9e';
  }
}

function getStatusLabel(status: string): string {
  if (status === 'to_do' || status === 'not_started') {
    return 'To Do';
  }
  switch (status) {
    case 'in_progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    default:
      return status;
  }
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Zoom controls
function zoomIn() {
  zoomLevel.value = Math.min(2, zoomLevel.value + 0.1);
}

function zoomOut() {
  zoomLevel.value = Math.max(0.3, zoomLevel.value - 0.1);
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

// Pan controls
function startPan(event: MouseEvent) {
  isPanning.value = true;
  panStartX.value = event.clientX - panX.value;
  panStartY.value = event.clientY - panY.value;
}

function handlePan(event: MouseEvent) {
  if (!isPanning.value) return;
  panX.value = event.clientX - panStartX.value;
  panY.value = event.clientY - panStartY.value;
}

function endPan() {
  isPanning.value = false;
}

// Watch for project changes
watch(selectedProjectId, async () => {
  if (selectedProjectId.value) {
    await loadEpics();
  }
});

// Initialize on mount
onMounted(async () => {
  await projectStore.fetchProjects(true);
  
  if (projectStore.projects.length > 0 && !selectedProjectId.value) {
    const firstProject = projectStore.projects[0];
    if (firstProject) {
      selectedProjectId.value = firstProject.id;
    }
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

.epic-node {
  transition: filter 0.2s ease;
}

.node-title {
  font-size: 12px;
  font-weight: 600;
}

.node-duration {
  font-size: 16px;
  font-weight: 700;
}

.node-type {
  font-size: 10px;
  fill: #666;
  text-transform: uppercase;
}

.status-text {
  font-size: 9px;
  font-weight: 600;
  fill: white;
  text-transform: uppercase;
}

.section-label {
  user-select: none;
  pointer-events: none;
}

.independent-epic rect {
  filter: drop-shadow(0 2px 4px rgba(156, 39, 176, 0.3));
}

.edge-line {
  transition:
    stroke 0.3s ease,
    stroke-width 0.3s ease;
}
</style>
