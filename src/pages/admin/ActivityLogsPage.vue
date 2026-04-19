<template>
  <q-page class="bg-grey-1">
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">
            <q-icon name="history" size="36px" class="q-mr-sm" />
            Activity Logs
          </h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Monitor user activity across the application
          </p>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Filters -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Filters</div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-3">
              <q-select
                v-model="filters.userId"
                :options="userOptions"
                label="User"
                outlined
                dense
                clearable
                emit-value
                map-options
                @update:model-value="fetchLogs"
              />
            </div>
            <div class="col-12 col-md-3">
              <q-select
                v-model="filters.projectId"
                :options="projectOptions"
                label="Project"
                outlined
                dense
                clearable
                emit-value
                map-options
                @update:model-value="fetchLogs"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-select
                v-model="filters.action"
                :options="actionOptions"
                label="Action"
                outlined
                dense
                clearable
                @update:model-value="fetchLogs"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-select
                v-model="filters.entityType"
                :options="entityTypeOptions"
                label="Page"
                outlined
                dense
                clearable
                @update:model-value="fetchLogs"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model="filters.search"
                label="Search"
                outlined
                dense
                clearable
                @keyup.enter="fetchLogs"
              >
                <template v-slot:append>
                  <q-icon name="search" class="cursor-pointer" @click="fetchLogs" />
                </template>
              </q-input>
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model="filters.dateFrom"
                label="From"
                type="date"
                outlined
                dense
                clearable
                @update:model-value="fetchLogs"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-input
                v-model="filters.dateTo"
                label="To"
                type="date"
                outlined
                dense
                clearable
                @update:model-value="fetchLogs"
              />
            </div>
            <div class="col-12 col-md-2">
              <q-btn color="primary" icon="search" label="Apply" @click="fetchLogs" />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Logs Table -->
      <q-card>
        <q-card-section>
          <div class="row items-center justify-between q-mb-md">
            <div class="text-h6 text-weight-bold">
              Logs ({{ total }} total)
            </div>
          </div>

          <div v-if="loading" class="row justify-center q-py-xl">
            <q-spinner color="primary" size="50px" />
          </div>

          <q-table
            v-else
            :rows="logs"
            :columns="columns"
            row-key="id"
            flat
            bordered
            :pagination="pagination"
            @request="onRequest"
            class="activity-logs-table"
          >
            <template v-slot:body-cell-user="props">
              <q-td :props="props">
                <div class="text-weight-medium">{{ props.row.userName || 'Unknown' }}</div>
                <div class="text-caption text-grey-7">{{ props.row.userEmail }}</div>
              </q-td>
            </template>

            <template v-slot:body-cell-action="props">
              <q-td :props="props">
                <q-chip size="sm" color="primary" text-color="white" dense>
                  {{ props.row.action }}
                </q-chip>
              </q-td>
            </template>

            <template v-slot:body-cell-entityType="props">
              <q-td :props="props">
                <q-chip size="sm" color="grey-6" text-color="white" dense>
                  {{ props.row.entityType }}
                </q-chip>
              </q-td>
            </template>

            <template v-slot:body-cell-details="props">
              <q-td :props="props">
                <div v-if="Object.keys(props.row.details || {}).length > 0" class="text-caption">
                  <q-btn
                    flat
                    dense
                    size="sm"
                    icon="info"
                    @click="showDetails(props.row)"
                  >
                    <q-tooltip>View details</q-tooltip>
                  </q-btn>
                </div>
                <span v-else class="text-grey-5">-</span>
              </q-td>
            </template>

            <template v-slot:body-cell-createdAt="props">
              <q-td :props="props">
                {{ formatDate(props.row.createdAt) }}
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </div>

    <!-- Details Dialog -->
    <q-dialog v-model="showDetailsDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Log Details</div>
        </q-card-section>
        <q-card-section>
          <pre class="details-json">{{ JSON.stringify(selectedLogDetails, null, 2) }}</pre>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { activityLogsApi, type ActivityLog, type ActivityLogsFilters } from 'src/services/activity-logs-api';
import { useProjectStore } from 'src/stores/project-store';
import { api } from 'src/services/api';

const $q = useQuasar();
const projectStore = useProjectStore();

const logs = ref<ActivityLog[]>([]);
const total = ref(0);
const loading = ref(false);
const actionOptions = ref<string[]>([]);
const entityTypeOptions = ref<string[]>([]);
const users = ref<Array<{ id: number; name: string; email: string }>>([]);
const showDetailsDialog = ref(false);
const selectedLogDetails = ref<Record<string, unknown>>({});

const filters = ref<Partial<ActivityLogsFilters> & { page: number; limit: number }>({
  page: 1,
  limit: 25,
});

const columns = [
  { name: 'user', label: 'User', field: 'userName', align: 'left' as const, sortable: false },
  { name: 'action', label: 'Action', field: 'action', align: 'left' as const, sortable: true },
  { name: 'entityType', label: 'Page', field: 'entityType', align: 'left' as const, sortable: true },
  { name: 'projectName', label: 'Project', field: 'projectName', align: 'left' as const, sortable: false },
  { name: 'route', label: 'Route', field: 'route', align: 'left' as const, sortable: false },
  { name: 'details', label: 'Details', field: 'details', align: 'center' as const, sortable: false },
  { name: 'createdAt', label: 'Time', field: 'createdAt', align: 'left' as const, sortable: true },
];

const pagination = computed(() => ({
  sortBy: 'createdAt',
  descending: true,
  page: filters.value.page || 1,
  rowsPerPage: filters.value.limit || 25,
  rowsNumber: total.value,
}));

const userOptions = computed(() =>
  users.value.map((u) => ({ label: `${u.name} (${u.email})`, value: u.id })),
);

const projectOptions = computed(() =>
  projectStore.projects.map((p) => ({ label: p.name, value: p.id })),
);

function formatDate(dateStr: string): string {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleString('sk-SK');
}

async function fetchLogs() {
  loading.value = true;
  try {
    const { dateFrom, dateTo, ...rest } = filters.value;
    const res = await activityLogsApi.getLogs({
      ...rest,
      dateFrom: dateFrom ? `${dateFrom}T00:00:00Z` : undefined,
      dateTo: dateTo ? `${dateTo}T23:59:59Z` : undefined,
    });
    logs.value = res.logs;
    total.value = res.total;
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to load activity logs',
    });
  } finally {
    loading.value = false;
  }
}

function onRequest(props: { pagination: { page: number; rowsPerPage: number } }) {
  filters.value.page = props.pagination.page;
  filters.value.limit = props.pagination.rowsPerPage;
  fetchLogs();
}

function showDetails(row: ActivityLog) {
  selectedLogDetails.value = {
    ...row.details,
    projectId: row.projectId,
    entityId: row.entityId,
    route: row.route,
  };
  showDetailsDialog.value = true;
}

onMounted(async () => {
  await projectStore.fetchProjects();
  try {
    const [actions, types, usersRes] = await Promise.all([
      activityLogsApi.getActions(),
      activityLogsApi.getEntityTypes(),
      api.get<Array<{ id: number; name: string; email: string }>>('/users'),
    ]);
    actionOptions.value = actions;
    entityTypeOptions.value = types;
    users.value = usersRes;
  } catch {
    // Use empty if endpoints fail
  }
  await fetchLogs();
});
</script>

<style scoped>
.details-json {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
}
</style>
