<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <div class="row items-center q-gutter-md">
            <q-btn flat round icon="arrow_back" color="primary" @click="navigateBack" />
            <div>
              <h4 class="text-h4 text-weight-bold text-primary q-ma-none">
                Epic PERT Diagram
              </h4>
              <p class="text-grey-7 q-ma-none q-mt-sm">
                Strategic planning visualization for {{ project?.name }}
              </p>
            </div>
          </div>
        </div>
        <div class="row q-gutter-sm">
          <q-btn
            outline
            color="primary"
            label="Show Critical Path"
            icon="timeline"
            @click="showCriticalPath"
            :loading="loadingCriticalPath"
          />
          <q-btn color="primary" icon="refresh" label="Refresh" @click="loadEpics" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
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
            Create epics first to see the PERT diagram
          </div>
        </div>
      </div>

      <!-- PERT Diagram -->
      <q-card v-else>
        <q-card-section>
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-bold">
              <q-icon name="hub" color="primary" class="q-mr-sm" />
              Epic Network Diagram
            </div>
            <div class="row q-gutter-sm items-center">
              <q-chip color="blue" text-color="white" icon="info">
                Total Epics: {{ epics.length }}
              </q-chip>
              <q-chip
                v-if="criticalPathData"
                color="red"
                text-color="white"
                icon="timeline"
              >
                Critical: {{ criticalPathData.criticalPath.length }}
              </q-chip>
              <q-separator vertical inset />
              <q-btn flat icon="zoom_in" size="sm" @click="zoomIn" />
              <q-btn flat icon="zoom_out" size="sm" @click="zoomOut" />
              <q-btn flat icon="center_focus_strong" size="sm" @click="resetZoom" />
            </div>
          </div>

          <div class="row q-gutter-xs q-mb-sm items-center">
            <q-chip size="sm" color="blue" text-color="white" icon="circle">Epics</q-chip>
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
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path
                    d="M 20 0 L 0 0 0 20"
                    fill="none"
                    stroke="#f0f0f0"
                    stroke-width="1"
                  />
                </pattern>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="5"
                  orient="auto"
                >
                  <path
                    d="M 2 2 L 8 5 L 2 8"
                    fill="none"
                    stroke="#2196f3"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </marker>
                <marker
                  id="arrowhead-critical"
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="5"
                  orient="auto"
                >
                  <path
                    d="M 2 2 L 8 5 L 2 8"
                    fill="none"
                    stroke="#f44336"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </marker>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              <!-- Connections -->
              <g class="connections" :transform="transform">
                <g
                  v-for="edge in edges"
                  :key="`${edge.from}-${edge.to}`"
                  class="edge-group"
                >
                  <line
                    :x1="(nodePositions[edge.from]?.x ?? 0) + 75"
                    :y1="(nodePositions[edge.from]?.y ?? 0) + 50"
                    :x2="nodePositions[edge.to]?.x ?? 0"
                    :y2="(nodePositions[edge.to]?.y ?? 0) + 50"
                    :stroke="edge.isCritical ? '#f44336' : '#2196f3'"
                    :stroke-width="edge.isCritical ? '3' : '2.5'"
                    :marker-end="edge.isCritical ? 'url(#arrowhead-critical)' : 'url(#arrowhead)'"
                    class="edge-line"
                  />
                </g>
              </g>

              <!-- Nodes -->
              <g class="nodes" :transform="transform">
                <g
                  v-for="epic in epics"
                  :key="epic.id"
                  :transform="`translate(${nodePositions[epic.id]?.x ?? 0}, ${nodePositions[epic.id]?.y ?? 0})`"
                  class="pert-node"
                  @mousedown.stop="startDrag(epic.id, $event)"
                  style="cursor: move"
                >
                  <rect
                    width="150"
                    height="100"
                    rx="8"
                    :fill="isEpicCritical(epic.id) ? '#ffebee' : '#e3f2fd'"
                    :stroke="isEpicCritical(epic.id) ? '#f44336' : '#2196f3'"
                    :stroke-width="isEpicCritical(epic.id) ? '3' : '2'"
                  />
                  <text x="75" y="25" text-anchor="middle" class="node-title">
                    {{ truncateText(epic.name, 15) }}
                  </text>
                  <text x="75" y="50" text-anchor="middle" class="node-duration">
                    {{ getEpicDuration(epic) }} days
                  </text>
                  <text x="75" y="70" text-anchor="middle" class="node-value">
                    BV: {{ epic.businessValue }}
                  </text>
                  <text x="75" y="90" text-anchor="middle" class="node-status">
                    {{ getStatusLabel(epic.status) }}
                  </text>
                </g>
              </g>
            </svg>
          </div>
        </q-card-section>
      </q-card>

      <!-- Critical Path Info -->
      <q-card v-if="criticalPathData" class="q-mt-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Critical Path Analysis</div>
          <div class="text-body1">
            <strong>Project Duration:</strong>
            {{ criticalPathData.projectDuration.toFixed(1) }} days
          </div>
          <div class="text-body1 q-mt-sm">
            <strong>Critical Path:</strong>
          </div>
          <div class="row q-gutter-xs q-mt-xs">
            <q-chip
              v-for="epicId in criticalPathData.criticalPath"
              :key="epicId"
              color="red"
              text-color="white"
            >
              {{ getEpicName(epicId) }}
            </q-chip>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useEpicStore, type Epic, type EpicCriticalPathResponse } from 'src/stores/epic-store';
import { useProjectStore } from 'src/stores/project-store';

const route = useRoute();
const router = useRouter();
const $q = useQuasar();
const epicStore = useEpicStore();
const projectStore = useProjectStore();

const projectId = computed(() => parseInt(route.params.id as string));
const project = computed(() => projectStore.getProjectById(projectId.value));

const loading = ref(false);
const loadingCriticalPath = ref(false);
const criticalPathData = ref<EpicCriticalPathResponse | null>(null);

const epics = computed(() => epicStore.epics);

// Diagram settings
const diagramWidth = 2000;
const diagramHeight = 1500;
const zoomLevel = ref(1);
const panX = ref(0);
const panY = ref(0);
const isPanning = ref(false);
const panStartX = ref(0);
const panStartY = ref(0);

// Drag settings
const isDragging = ref(false);
const draggedEpicId = ref<number | null>(null);
const dragStartX = ref(0);
const dragStartY = ref(0);

const pertSvg = ref<SVGSVGElement | null>(null);

// Node positions (auto-layout or manual)
const nodePositions = ref<Record<number, { x: number; y: number }>>({});

// Transform for zoom and pan
const transform = computed(
  () => `translate(${panX.value}, ${panY.value}) scale(${zoomLevel.value})`
);

// Edges (dependencies)
const edges = computed(() => {
  const result: Array<{ from: number; to: number; isCritical: boolean }> = [];
  
  for (const epic of epics.value) {
    if (epic.dependencies && epic.dependencies.length > 0) {
      for (const depId of epic.dependencies) {
        const isCritical =
          (criticalPathData.value?.criticalPath.includes(epic.id) &&
          criticalPathData.value?.criticalPath.includes(depId)) ?? false;
        
        result.push({
          from: depId,
          to: epic.id,
          isCritical,
        });
      }
    }
  }
  
  return result;
});

onMounted(async () => {
  await loadEpics();
  calculateLayout();
});

watch(epics, () => {
  calculateLayout();
});

async function loadEpics() {
  loading.value = true;
  try {
    await epicStore.fetchEpics(projectId.value, true);
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Failed to load epics: ${error}`,
    });
  } finally {
    loading.value = false;
  }
}

async function showCriticalPath() {
  loadingCriticalPath.value = true;
  try {
    const data = await epicStore.getCriticalPath(projectId.value);
    criticalPathData.value = data;
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Failed to calculate critical path: ${error}`,
    });
  } finally {
    loadingCriticalPath.value = false;
  }
}

function calculateLayout() {
  // Simple hierarchical layout
  const positions: Record<number, { x: number; y: number }> = {};
  
  // Use saved positions if available
  for (const epic of epics.value) {
    if (epic.diagramPositionX !== null && epic.diagramPositionY !== null) {
      positions[epic.id] = {
        x: epic.diagramPositionX,
        y: epic.diagramPositionY,
      };
    }
  }
  
  // Calculate positions for epics without saved positions
  let currentX = 100;
  let currentY = 100;
  let maxY = 100;
  let epicsInRow = 0;
  const maxEpicsPerRow = 5;
  
  for (const epic of epics.value) {
    if (positions[epic.id] === undefined) {
      positions[epic.id] = { x: currentX, y: currentY };
      
      epicsInRow++;
      currentX += 200;
      
      if (epicsInRow >= maxEpicsPerRow) {
        currentX = 100;
        currentY = maxY + 150;
        maxY = currentY;
        epicsInRow = 0;
      } else {
        maxY = Math.max(maxY, currentY);
      }
    }
  }
  
  nodePositions.value = positions;
}

function isEpicCritical(epicId: number): boolean {
  return criticalPathData.value?.criticalPath.includes(epicId) ?? false;
}

function getEpicDuration(epic: Epic): string {
  if (epic.pert.expected !== null && epic.pert.expected !== undefined) {
    return epic.pert.expected.toFixed(1);
  }
  return 'N/A';
}

function getEpicName(epicId: number): string {
  const epic = epics.value.find((e) => e.id === epicId);
  return epic?.name || `Epic #${epicId}`;
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

// Zoom functions
function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, 3);
}

function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, 0.5);
}

function resetZoom() {
  zoomLevel.value = 1;
  panX.value = 0;
  panY.value = 0;
}

function handleWheel(event: WheelEvent) {
  const delta = event.deltaY > 0 ? 0.9 : 1.1;
  zoomLevel.value = Math.max(0.5, Math.min(3, zoomLevel.value * delta));
}

// Pan functions
function startPan(event: MouseEvent) {
  if (isDragging.value) return;
  isPanning.value = true;
  panStartX.value = event.clientX - panX.value;
  panStartY.value = event.clientY - panY.value;
}

function handlePan(event: MouseEvent) {
  if (isDragging.value) {
    handleDrag(event);
    return;
  }
  
  if (isPanning.value) {
    panX.value = event.clientX - panStartX.value;
    panY.value = event.clientY - panStartY.value;
  }
}

function endPan() {
  isPanning.value = false;
  if (isDragging.value) {
    endDrag();
  }
}

// Drag functions (for moving epic nodes)
function startDrag(epicId: number, event: MouseEvent) {
  isDragging.value = true;
  draggedEpicId.value = epicId;
  
  const pos = nodePositions.value[epicId];
  if (pos) {
    dragStartX.value = event.clientX / zoomLevel.value - pos.x;
    dragStartY.value = event.clientY / zoomLevel.value - pos.y;
  }
}

function handleDrag(event: MouseEvent) {
  if (isDragging.value && draggedEpicId.value !== null) {
    const newX = event.clientX / zoomLevel.value - dragStartX.value;
    const newY = event.clientY / zoomLevel.value - dragStartY.value;
    
    nodePositions.value[draggedEpicId.value] = {
      x: newX,
      y: newY,
    };
  }
}

async function endDrag() {
  if (isDragging.value && draggedEpicId.value !== null) {
    const pos = nodePositions.value[draggedEpicId.value];
    if (pos) {
      try {
        await epicStore.updateEpicPosition(projectId.value, draggedEpicId.value, pos.x, pos.y);
      } catch (error) {
        console.error('Failed to save epic position:', error);
      }
    }
  }
  
  isDragging.value = false;
  draggedEpicId.value = null;
}

function navigateBack() {
  router.push({ name: 'epics', params: { id: projectId.value } });
}
</script>

<style scoped lang="scss">
.pert-diagram-container {
  width: 100%;
  height: 600px;
  overflow: hidden;
  background: #fafafa;
  border: 1px solid #e0e0e0;
}

.pert-diagram {
  width: 100%;
  height: 100%;
  cursor: grab;

  &:active {
    cursor: grabbing;
  }
}

.pert-node {
  cursor: move;

  &:hover rect {
    filter: brightness(0.95);
  }
}

.node-title {
  font-size: 13px;
  font-weight: 600;
  fill: #1976d2;
}

.node-duration {
  font-size: 12px;
  font-weight: bold;
  fill: #424242;
}

.node-value {
  font-size: 11px;
  fill: #666;
}

.node-status {
  font-size: 10px;
  fill: #999;
}

.edge-line {
  transition: stroke-width 0.2s;

  &:hover {
    stroke-width: 4 !important;
  }
}
</style>
