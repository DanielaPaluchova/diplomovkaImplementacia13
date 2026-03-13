<template>
  <q-dialog v-model="isOpen" persistent>
    <q-card style="min-width: 600px; max-width: 800px">
      <q-card-section class="bg-primary text-white">
        <div class="text-h6">{{ isEditMode ? 'Edit Epic' : 'Create New Epic' }}</div>
      </q-card-section>

      <q-card-section class="q-pt-md">
        <q-form @submit="handleSubmit">
          <!-- Epic Name -->
          <q-input
            v-model="formData.name"
            label="Epic Name *"
            filled
            :rules="[(val) => (val && val.length > 0) || 'Epic name is required']"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="star" color="orange" />
            </template>
          </q-input>

          <!-- Description -->
          <q-input
            v-model="formData.description"
            label="Description"
            type="textarea"
            filled
            rows="3"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="description" />
            </template>
          </q-input>

          <!-- Status, Priority & Business Value -->
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-4">
              <q-select
                v-model="formData.status"
                :options="statusOptions"
                label="Status"
                filled
                emit-value
                map-options
              >
                <template v-slot:prepend>
                  <q-icon name="flag" />
                </template>
              </q-select>
            </div>
            <div class="col-4">
              <q-select
                v-model="formData.priority"
                :options="priorityOptions"
                label="Priority"
                filled
                emit-value
                map-options
              >
                <template v-slot:prepend>
                  <q-icon name="priority_high" :color="getPriorityColor(formData.priority)" />
                </template>
              </q-select>
            </div>
            <div class="col-4">
              <q-input
                v-model.number="formData.businessValue"
                label="Business Value"
                type="number"
                filled
                :rules="[(val) => val >= 0 || 'Must be non-negative']"
              >
                <template v-slot:prepend>
                  <q-icon name="trending_up" />
                </template>
              </q-input>
            </div>
          </div>

          <!-- Owner (Assignee) & Labels -->
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-6">
              <q-select
                v-model="formData.ownerId"
                :options="userOptions"
                label="Owner (Assignee)"
                filled
                emit-value
                map-options
                clearable
                option-value="value"
                option-label="label"
              >
                <template v-slot:prepend>
                  <q-icon name="person" />
                </template>
              </q-select>
            </div>
            <div class="col-6">
              <q-select
                v-model="formData.labels"
                label="Labels / Tags"
                filled
                use-input
                use-chips
                multiple
                hide-dropdown-icon
                input-debounce="0"
                new-value-mode="add-unique"
                hint="Press Enter to add new labels"
              >
                <template v-slot:prepend>
                  <q-icon name="label" />
                </template>
              </q-select>
            </div>
          </div>

          <!-- Dates -->
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-6">
              <q-input
                v-model="formData.startDate"
                label="Start Date"
                filled
                type="date"
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>
            <div class="col-6">
              <q-input
                v-model="formData.targetDate"
                label="Target Date"
                filled
                type="date"
              >
                <template v-slot:prepend>
                  <q-icon name="event_available" />
                </template>
              </q-input>
            </div>
          </div>

          <!-- PERT Estimates Section -->
          <q-separator class="q-mb-md" />
          <div class="text-subtitle1 text-weight-medium q-mb-sm">
            <q-icon name="schedule" color="primary" class="q-mr-xs" />
            PERT Estimates (in days)
          </div>
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-4">
              <q-input
                v-model.number="formData.pert.optimistic"
                label="Optimistic"
                type="number"
                filled
                step="0.5"
                hint="Best case"
              >
                <template v-slot:prepend>
                  <q-icon name="sentiment_very_satisfied" color="green" />
                </template>
              </q-input>
            </div>
            <div class="col-4">
              <q-input
                v-model.number="formData.pert.mostLikely"
                label="Most Likely"
                type="number"
                filled
                step="0.5"
                hint="Expected"
              >
                <template v-slot:prepend>
                  <q-icon name="sentiment_satisfied" color="blue" />
                </template>
              </q-input>
            </div>
            <div class="col-4">
              <q-input
                v-model.number="formData.pert.pessimistic"
                label="Pessimistic"
                type="number"
                filled
                step="0.5"
                hint="Worst case"
              >
                <template v-slot:prepend>
                  <q-icon name="sentiment_dissatisfied" color="orange" />
                </template>
              </q-input>
            </div>
          </div>

          <!-- Expected Duration (calculated) -->
          <div v-if="pertExpected !== null" class="q-mb-md">
            <q-banner rounded class="bg-blue-1 text-blue-9">
              <template v-slot:avatar>
                <q-icon name="calculate" color="blue" />
              </template>
              <div class="text-weight-medium">
                Expected Duration: <strong>{{ pertExpected.toFixed(2) }} days</strong>
              </div>
              <div class="text-caption">Calculated using PERT formula: (O + 4M + P) / 6</div>
            </q-banner>
          </div>

          <!-- Dependencies Section -->
          <q-separator class="q-mb-md" />
          <div class="text-subtitle1 text-weight-medium q-mb-sm">
            <q-icon name="link" color="primary" class="q-mr-xs" />
            Dependencies
          </div>
          <q-select
            v-model="formData.dependencies"
            :options="availableEpics"
            option-value="id"
            option-label="name"
            label="Epics that must be completed first"
            filled
            multiple
            use-chips
            emit-value
            map-options
            hint="Select epics that this epic depends on"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="account_tree" />
            </template>
          </q-select>
        </q-form>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn flat label="Cancel" color="grey" @click="handleCancel" />
        <q-btn
          unelevated
          :label="isEditMode ? 'Update Epic' : 'Create Epic'"
          color="primary"
          @click="handleSubmit"
          :loading="loading"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useEpicStore, type Epic } from 'src/stores/epic-store';
import { useQuasar } from 'quasar';
import { api } from 'src/services/api';

interface Props {
  modelValue: boolean;
  projectId: number;
  epic?: Epic | undefined;
  existingEpics?: Epic[];
}

const props = withDefaults(defineProps<Props>(), {
  existingEpics: () => [],
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'created', epic: Epic): void;
  (e: 'updated', epic: Epic): void;
}>();

const $q = useQuasar();
const epicStore = useEpicStore();

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const isEditMode = computed(() => !!props.epic);
const loading = ref(false);

interface UserOption {
  id: number;
  name: string;
  email: string;
  avatar?: string;
}

const users = ref<UserOption[]>([]);

const statusOptions = [
  { label: 'To Do', value: 'to_do' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
];

const priorityOptions = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
];

const userOptions = computed(() => {
  return users.value.map(u => ({
    label: u.name,
    value: u.id
  }));
});

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high': return 'red';
    case 'medium': return 'orange';
    case 'low': return 'green';
    default: return 'grey';
  }
}

const formData = ref({
  name: '',
  description: '',
  status: 'to_do' as 'to_do' | 'in_progress' | 'completed',
  ownerId: null as number | null,
  priority: 'medium' as 'low' | 'medium' | 'high',
  labels: [] as string[],
  startDate: null as string | null,
  targetDate: null as string | null,
  businessValue: 0,
  pert: {
    optimistic: null as number | null,
    mostLikely: null as number | null,
    pessimistic: null as number | null,
  },
  dependencies: [] as number[],
});

// Calculate PERT expected duration
const pertExpected = computed(() => {
  const { optimistic, mostLikely, pessimistic } = formData.value.pert;
  if (
    optimistic !== null &&
    mostLikely !== null &&
    pessimistic !== null &&
    optimistic >= 0 &&
    mostLikely >= 0 &&
    pessimistic >= 0
  ) {
    return (optimistic + 4 * mostLikely + pessimistic) / 6;
  }
  return null;
});

// Filter out current epic from dependencies
const availableEpics = computed(() => {
  if (!props.epic) return props.existingEpics;
  return props.existingEpics.filter((e) => e.id !== props.epic?.id);
});

// Initialize form data when epic prop changes
watch(
  () => props.epic,
  (epic) => {
    if (epic) {
      // Normalize 'not_started' to 'to_do' for form
      const status = epic.status === 'not_started' ? 'to_do' : epic.status;
      
      formData.value = {
        name: epic.name,
        description: epic.description,
        status: status,
        ownerId: epic.ownerId || null,
        priority: epic.priority || 'medium',
        labels: epic.labels || [],
        startDate: epic.startDate || null,
        targetDate: epic.targetDate || null,
        businessValue: epic.businessValue,
        pert: {
          optimistic: epic.pert.optimistic,
          mostLikely: epic.pert.mostLikely,
          pessimistic: epic.pert.pessimistic,
        },
        dependencies: epic.dependencies || [],
      };
    } else {
      formData.value = {
        name: '',
        description: '',
        status: 'to_do',
        ownerId: null,
        priority: 'medium',
        labels: [],
        startDate: null,
        targetDate: null,
        businessValue: 0,
        pert: {
          optimistic: null,
          mostLikely: null,
          pessimistic: null,
        },
        dependencies: [],
      };
    }
  },
  { immediate: true }
);

// Load users on mount
onMounted(async () => {
  try {
    const response = await api.get<UserOption[]>(`/projects/${props.projectId}/team-members`);
    users.value = response;
  } catch (error) {
    console.error('Failed to load project team members:', error);
  }
});

async function handleSubmit() {
  if (!formData.value.name) {
    $q.notify({
      type: 'negative',
      message: 'Epic name is required',
    });
    return;
  }

  loading.value = true;

  try {
    const epicData = {
      name: formData.value.name,
      description: formData.value.description,
      status: formData.value.status,
      ownerId: formData.value.ownerId,
      priority: formData.value.priority,
      labels: formData.value.labels,
      startDate: formData.value.startDate,
      targetDate: formData.value.targetDate,
      businessValue: formData.value.businessValue,
      pert: formData.value.pert,
      dependencies: formData.value.dependencies,
    };

    if (isEditMode.value && props.epic) {
      // Update existing epic
      const updated = await epicStore.updateEpic(props.projectId, props.epic.id, epicData);
      if (updated) {
        $q.notify({
          type: 'positive',
          message: 'Epic updated successfully',
        });
        emit('updated', updated);
        isOpen.value = false;
      }
    } else {
      // Create new epic
      const created = await epicStore.createEpic(props.projectId, epicData);
      if (created) {
        $q.notify({
          type: 'positive',
          message: 'Epic created successfully',
        });
        emit('created', created);
        isOpen.value = false;
      }
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Failed to ${isEditMode.value ? 'update' : 'create'} epic: ${error}`,
    });
  } finally {
    loading.value = false;
  }
}

function handleCancel() {
  isOpen.value = false;
}
</script>
