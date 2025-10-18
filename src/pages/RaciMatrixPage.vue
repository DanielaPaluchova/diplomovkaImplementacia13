<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between q-mb-md">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">RACI Matrix</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Responsibility Assignment Matrix for clear role definitions
          </p>
        </div>
        <q-btn color="secondary" icon="download" label="Export" @click="exportMatrix" />
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
                  <th v-for="member in projectMembers" :key="member.id" class="member-column">
                    <div class="member-header">
                      <q-avatar size="24px" class="q-mb-xs">
                        <img :src="member.avatar" />
                      </q-avatar>
                      <div class="text-caption text-weight-bold">
                        {{ member.name.split(' ')[0] }}
                      </div>
                      <div class="text-caption text-grey-7">{{ getMemberRole(member.id) }}</div>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in selectedProject.tasks" :key="task.id" class="task-row">
                  <td class="task-cell">
                    <div class="text-weight-medium">{{ task.title }}</div>
                    <div class="text-caption text-grey-7">{{ task.type }}</div>
                  </td>
                  <td v-for="member in projectMembers" :key="member.id" class="responsibility-cell">
                    <div class="row q-gutter-xs justify-center">
                      <q-chip
                        v-if="task.raci.responsible.includes(member.id)"
                        color="red"
                        text-color="white"
                        size="sm"
                        label="R"
                      />
                      <q-chip
                        v-if="task.raci.accountable === member.id"
                        color="blue"
                        text-color="white"
                        size="sm"
                        label="A"
                      />
                      <q-chip
                        v-if="task.raci.consulted.includes(member.id)"
                        color="orange"
                        text-color="white"
                        size="sm"
                        label="C"
                      />
                      <q-chip
                        v-if="task.raci.informed.includes(member.id)"
                        color="green"
                        text-color="white"
                        size="sm"
                        label="I"
                      />
                      <span v-if="!hasRaciRole(task, member.id)" class="text-grey-5">-</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </q-card-section>
      </q-card>

      <!-- RACI Statistics -->
      <div class="row q-gutter-lg q-mt-lg">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Team Member Workload</div>
              <q-list>
                <q-item v-for="member in projectMembers" :key="member.id">
                  <q-item-section avatar>
                    <q-avatar>
                      <img :src="member.avatar" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>{{ member.name }}</q-item-label>
                    <q-item-label caption>{{ getMemberRole(member.id) }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="column items-end">
                      <div class="row q-gutter-xs q-mb-xs">
                        <q-chip
                          color="red"
                          text-color="white"
                          size="sm"
                          :label="`R: ${getMemberResponsibleCount(member.id)}`"
                        />
                        <q-chip
                          color="blue"
                          text-color="white"
                          size="sm"
                          :label="`A: ${getMemberAccountableCount(member.id)}`"
                        />
                      </div>
                      <div class="text-caption text-grey-7">
                        {{ getMemberTotalTasks(member.id) }} total assignments
                      </div>
                    </div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card class="q-mb-md">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">RACI Distribution</div>
              <div class="column q-gutter-md">
                <div>
                  <div class="row items-center justify-between q-mb-xs">
                    <span>Responsible (R)</span>
                    <q-chip
                      color="red"
                      text-color="white"
                      size="sm"
                      :label="raciStats.responsible"
                    />
                  </div>
                  <q-linear-progress
                    :value="raciStats.responsible / raciStats.total"
                    color="red"
                    size="8px"
                  />
                </div>
                <div>
                  <div class="row items-center justify-between q-mb-xs">
                    <span>Accountable (A)</span>
                    <q-chip
                      color="blue"
                      text-color="white"
                      size="sm"
                      :label="raciStats.accountable"
                    />
                  </div>
                  <q-linear-progress
                    :value="raciStats.accountable / raciStats.total"
                    color="blue"
                    size="8px"
                  />
                </div>
                <div>
                  <div class="row items-center justify-between q-mb-xs">
                    <span>Consulted (C)</span>
                    <q-chip
                      color="orange"
                      text-color="white"
                      size="sm"
                      :label="raciStats.consulted"
                    />
                  </div>
                  <q-linear-progress
                    :value="raciStats.consulted / raciStats.total"
                    color="orange"
                    size="8px"
                  />
                </div>
                <div>
                  <div class="row items-center justify-between q-mb-xs">
                    <span>Informed (I)</span>
                    <q-chip
                      color="green"
                      text-color="white"
                      size="sm"
                      :label="raciStats.informed"
                    />
                  </div>
                  <q-linear-progress
                    :value="raciStats.informed / raciStats.total"
                    color="green"
                    size="8px"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <div v-else class="q-pa-xl text-center text-grey-5">
      <q-icon name="folder_open" size="64px" class="q-mb-md" />
      <div class="text-h6">Select a project to view RACI matrix</div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useProjectStore, type Task } from 'src/stores/project-store';
import { useMockDataStore } from 'src/stores/mock-data';

const $q = useQuasar();
const projectStore = useProjectStore();
const mockDataStore = useMockDataStore();

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

// Project members
const projectMembers = computed(() => {
  if (!selectedProject.value) return [];
  return selectedProject.value.teamMemberIds
    .map((id) => mockDataStore.teamMembers.find((m) => m.id === id))
    .filter((m) => m !== undefined);
});

// Helper functions
function getMemberRole(memberId: number) {
  if (!selectedProject.value) return '';
  const role = selectedProject.value.roles.find((r) => r.memberId === memberId);
  return role?.role || 'member';
}

function hasRaciRole(task: Task, memberId: number) {
  return (
    task.raci.responsible.includes(memberId) ||
    task.raci.accountable === memberId ||
    task.raci.consulted.includes(memberId) ||
    task.raci.informed.includes(memberId)
  );
}

function getMemberResponsibleCount(memberId: number) {
  if (!selectedProject.value) return 0;
  return selectedProject.value.tasks.filter((t) => t.raci.responsible.includes(memberId)).length;
}

function getMemberAccountableCount(memberId: number) {
  if (!selectedProject.value) return 0;
  return selectedProject.value.tasks.filter((t) => t.raci.accountable === memberId).length;
}

function getMemberTotalTasks(memberId: number) {
  if (!selectedProject.value) return 0;
  return selectedProject.value.tasks.filter((t) => hasRaciRole(t, memberId)).length;
}

// RACI Statistics
const raciStats = computed(() => {
  if (!selectedProject.value) {
    return { responsible: 0, accountable: 0, consulted: 0, informed: 0, total: 0 };
  }

  const stats = {
    responsible: 0,
    accountable: 0,
    consulted: 0,
    informed: 0,
    total: 0,
  };

  selectedProject.value.tasks.forEach((task) => {
    stats.responsible += task.raci.responsible.length;
    stats.accountable += task.raci.accountable ? 1 : 0;
    stats.consulted += task.raci.consulted.length;
    stats.informed += task.raci.informed.length;
  });

  stats.total = stats.responsible + stats.accountable + stats.consulted + stats.informed;

  return stats;
});

// Methods
function exportMatrix() {
  $q.notify({
    message: 'RACI Matrix exported successfully!',
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}
</script>

<style scoped>
.raci-table-container {
  overflow-x: auto;
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

.task-column {
  min-width: 250px;
  text-align: left !important;
  background: #f5f5f5;
  position: sticky;
  left: 0;
  z-index: 2;
}

.member-column {
  min-width: 120px;
  background: #f5f5f5;
}

.member-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.task-cell {
  text-align: left !important;
  background: white;
  position: sticky;
  left: 0;
  z-index: 1;
}

.task-row:hover {
  background-color: #fafafa;
}

.responsibility-cell {
  vertical-align: middle;
  background: white;
}
</style>
