<template>
  <div class="epic-board">
    <div class="row q-col-gutter-md">
      <!-- TO DO Column -->
      <div class="col-12 col-md-4">
        <q-card flat bordered class="column-card">
          <q-card-section class="bg-grey-2">
            <div class="row items-center justify-between">
              <div class="text-subtitle1 text-weight-bold">
                <q-icon name="flag" class="q-mr-xs" />
                To Do
              </div>
              <q-badge color="grey" :label="todoEpics.length" />
            </div>
          </q-card-section>
          <q-separator />
          <q-card-section 
            class="column-content"
            @dragover.prevent
            @drop="handleDrop($event, 'to_do')"
          >
            <div class="q-gutter-sm">
              <q-card
                v-for="epic in todoEpics"
                :key="epic.id"
                class="epic-card cursor-pointer"
                draggable="true"
                @dragstart="handleDragStart($event, epic)"
                @dragend="handleDragEnd"
                @click="$emit('edit', epic)"
              >
                <q-card-section class="q-pa-sm">
                    <div class="row items-start justify-between q-mb-xs">
                      <div class="text-subtitle2 text-weight-medium">{{ epic.name }}</div>
                      <q-chip
                        :color="getPriorityColor(epic.priority)"
                        text-color="white"
                        size="xs"
                        dense
                      >
                        {{ getPriorityLabel(epic.priority) }}
                      </q-chip>
                    </div>
                    
                    <div v-if="epic.description" class="text-caption text-grey-7 q-mb-sm">
                      {{ truncate(epic.description, 80) }}
                    </div>

                    <div v-if="epic.owner" class="text-caption text-grey-7 q-mb-xs">
                      <q-icon name="person" size="xs" />
                      {{ epic.owner.name }}
                    </div>

                    <div v-if="epic.labels && epic.labels.length > 0" class="q-mb-xs">
                      <q-chip
                        v-for="label in epic.labels.slice(0, 2)"
                        :key="label"
                        size="xs"
                        dense
                        color="purple-1"
                        text-color="purple-9"
                      >
                        {{ label }}
                      </q-chip>
                    </div>

                    <div v-if="epic.progress !== undefined || epic.tasks" class="q-mb-xs">
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-grey-7">
                          <q-icon name="task" size="xs" />
                          {{ getCompletedTasksCount(epic) }}/{{ getTotalTasksCount(epic) }}
                        </span>
                        <span class="text-caption text-weight-medium">{{ epic.progress || 0 }}%</span>
                      </div>
                      <q-linear-progress
                        :value="(epic.progress || 0) / 100"
                        color="primary"
                        size="6px"
                        rounded
                      />
                    </div>

                    <div class="row items-center justify-between">
                      <span class="text-caption text-grey-7">
                        <q-icon name="trending_up" size="xs" />
                        BV: {{ epic.businessValue }}
                      </span>
                      <span v-if="epic.pert.expected" class="text-caption text-grey-7">
                        <q-icon name="schedule" size="xs" />
                        {{ epic.pert.expected.toFixed(1) }}d
                      </span>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- IN PROGRESS Column -->
      <div class="col-12 col-md-4">
        <q-card flat bordered class="column-card">
          <q-card-section class="bg-blue-1">
            <div class="row items-center justify-between">
              <div class="text-subtitle1 text-weight-bold text-primary">
                <q-icon name="play_circle" class="q-mr-xs" />
                In Progress
              </div>
              <q-badge color="primary" :label="inProgressEpics.length" />
            </div>
          </q-card-section>
          <q-separator />
          <q-card-section 
            class="column-content"
            @dragover.prevent
            @drop="handleDrop($event, 'in_progress')"
          >
            <div class="q-gutter-sm">
              <q-card
                v-for="epic in inProgressEpics"
                :key="epic.id"
                class="epic-card cursor-pointer"
                draggable="true"
                @dragstart="handleDragStart($event, epic)"
                @dragend="handleDragEnd"
                @click="$emit('edit', epic)"
              >
                <q-card-section class="q-pa-sm">
                    <div class="row items-start justify-between q-mb-xs">
                      <div class="text-subtitle2 text-weight-medium">{{ epic.name }}</div>
                      <div class="row q-gutter-xs">
                        <q-chip
                          :color="getPriorityColor(epic.priority)"
                          text-color="white"
                          size="xs"
                          dense
                        >
                          {{ getPriorityLabel(epic.priority) }}
                        </q-chip>
                        <q-btn
                          flat
                          round
                          dense
                          icon="edit"
                          size="xs"
                          color="primary"
                          @click.stop="$emit('editEpic', epic)"
                        >
                          <q-tooltip>Edit epic</q-tooltip>
                        </q-btn>
                      </div>
                    </div>
                    
                    <div v-if="epic.description" class="text-caption text-grey-7 q-mb-sm">
                      {{ truncate(epic.description, 80) }}
                    </div>

                    <div v-if="epic.owner" class="text-caption text-grey-7 q-mb-xs">
                      <q-icon name="person" size="xs" />
                      {{ epic.owner.name }}
                    </div>

                    <div v-if="epic.labels && epic.labels.length > 0" class="q-mb-xs">
                      <q-chip
                        v-for="label in epic.labels.slice(0, 2)"
                        :key="label"
                        size="xs"
                        dense
                        color="purple-1"
                        text-color="purple-9"
                      >
                        {{ label }}
                      </q-chip>
                    </div>

                    <div v-if="epic.progress !== undefined || epic.tasks" class="q-mb-xs">
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-grey-7">
                          <q-icon name="task" size="xs" />
                          {{ getCompletedTasksCount(epic) }}/{{ getTotalTasksCount(epic) }}
                        </span>
                        <span class="text-caption text-weight-medium">{{ epic.progress || 0 }}%</span>
                      </div>
                      <q-linear-progress
                        :value="(epic.progress || 0) / 100"
                        color="primary"
                        size="6px"
                        rounded
                      />
                    </div>

                    <div class="row items-center justify-between">
                      <span class="text-caption text-grey-7">
                        <q-icon name="trending_up" size="xs" />
                        BV: {{ epic.businessValue }}
                      </span>
                      <span v-if="epic.pert.expected" class="text-caption text-grey-7">
                        <q-icon name="schedule" size="xs" />
                        {{ epic.pert.expected.toFixed(1) }}d
                      </span>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- COMPLETED Column -->
      <div class="col-12 col-md-4">
        <q-card flat bordered class="column-card">
          <q-card-section class="bg-green-1">
            <div class="row items-center justify-between">
              <div class="text-subtitle1 text-weight-bold text-positive">
                <q-icon name="check_circle" class="q-mr-xs" />
                Completed
              </div>
              <q-badge color="positive" :label="completedEpics.length" />
            </div>
          </q-card-section>
          <q-separator />
          <q-card-section
            class="column-content"
            @dragover.prevent
            @drop="handleDrop($event, 'completed')"
          >
            <div class="q-gutter-sm">
              <q-card
                v-for="epic in completedEpics"
                :key="epic.id"
                class="epic-card cursor-pointer"
                draggable="true"
                @dragstart="handleDragStart($event, epic)"
                @dragend="handleDragEnd"
                @click="$emit('edit', epic)"
              >
                <q-card-section class="q-pa-sm">
                    <div class="row items-start justify-between q-mb-xs">
                      <div class="text-subtitle2 text-weight-medium">{{ epic.name }}</div>
                      <div class="row q-gutter-xs">
                        <q-chip
                          :color="getPriorityColor(epic.priority)"
                          text-color="white"
                          size="xs"
                          dense
                        >
                          {{ getPriorityLabel(epic.priority) }}
                        </q-chip>
                        <q-btn
                          flat
                          round
                          dense
                          icon="edit"
                          size="xs"
                          color="primary"
                          @click.stop="$emit('editEpic', epic)"
                        >
                          <q-tooltip>Edit epic</q-tooltip>
                        </q-btn>
                      </div>
                    </div>
                    
                    <div v-if="epic.description" class="text-caption text-grey-7 q-mb-sm">
                      {{ truncate(epic.description, 80) }}
                    </div>

                    <div v-if="epic.owner" class="text-caption text-grey-7 q-mb-xs">
                      <q-icon name="person" size="xs" />
                      {{ epic.owner.name }}
                    </div>

                    <div v-if="epic.labels && epic.labels.length > 0" class="q-mb-xs">
                      <q-chip
                        v-for="label in epic.labels.slice(0, 2)"
                        :key="label"
                        size="xs"
                        dense
                        color="purple-1"
                        text-color="purple-9"
                      >
                        {{ label }}
                      </q-chip>
                    </div>

                    <div v-if="epic.progress !== undefined || epic.tasks" class="q-mb-xs">
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-grey-7">
                          <q-icon name="task" size="xs" />
                          {{ getCompletedTasksCount(epic) }}/{{ getTotalTasksCount(epic) }}
                        </span>
                        <span class="text-caption text-weight-medium">{{ epic.progress || 0 }}%</span>
                      </div>
                      <q-linear-progress
                        :value="(epic.progress || 0) / 100"
                        color="positive"
                        size="6px"
                        rounded
                      />
                    </div>

                    <div class="row items-center justify-between">
                      <span class="text-caption text-grey-7">
                        <q-icon name="trending_up" size="xs" />
                        BV: {{ epic.businessValue }}
                      </span>
                      <span v-if="epic.pert.expected" class="text-caption text-grey-7">
                        <q-icon name="schedule" size="xs" />
                        {{ epic.pert.expected.toFixed(1) }}d
                      </span>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Epic } from 'src/stores/epic-store';

interface Props {
  epics: Epic[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'edit', epic: Epic): void;
  (e: 'editEpic', epic: Epic): void;
  (e: 'statusChange', epicId: number, newStatus: string): void;
}>();

const draggedEpic = ref<Epic | null>(null);

const todoEpics = computed(() => 
  props.epics.filter(e => e.status === 'to_do' || e.status === 'not_started')
);

const inProgressEpics = computed(() => 
  props.epics.filter(e => e.status === 'in_progress')
);

const completedEpics = computed(() => 
  props.epics.filter(e => e.status === 'completed')
);

function getPriorityLabel(priority: string): string {
  switch (priority) {
    case 'low': return 'Low';
    case 'medium': return 'Med';
    case 'high': return 'High';
    default: return priority;
  }
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'low': return 'green';
    case 'medium': return 'orange';
    case 'high': return 'red';
    default: return 'grey';
  }
}

function truncate(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function handleDragStart(event: DragEvent, epic: Epic) {
  draggedEpic.value = epic;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', epic.id.toString());
  }
  // Add visual feedback
  const target = event.target as HTMLElement;
  setTimeout(() => {
    target.style.opacity = '0.5';
  }, 0);
}

function handleDragEnd(event: DragEvent) {
  const target = event.target as HTMLElement;
  target.style.opacity = '1';
}

function handleDrop(event: DragEvent, newStatus: string) {
  event.preventDefault();
  if (draggedEpic.value && draggedEpic.value.status !== newStatus) {
    emit('statusChange', draggedEpic.value.id, newStatus);
  }
  draggedEpic.value = null;
}

function getTotalTasksCount(epic: Epic): number {
  return epic.tasks?.length || 0;
}

function getCompletedTasksCount(epic: Epic): number {
  if (!epic.tasks) return 0;
  return epic.tasks.filter(t => t.status === 'Done').length;
}
</script>

<style scoped lang="scss">
.epic-board {
  min-height: 600px;
}

.column-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.column-content {
  flex: 1;
  padding: 12px;
  min-height: 500px;
  max-height: 600px;
  overflow-y: auto;
}

.epic-card {
  transition: all 0.2s ease;
  margin-bottom: 8px;
  cursor: move;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
  
  &:active {
    cursor: grabbing;
  }
}

.column-content {
  &:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
}
</style>
