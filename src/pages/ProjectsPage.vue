<template>
  <q-page class="bg-grey-1">
    <!-- Header Section -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <div class="col">
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Projects</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Manage and track all your projects in one place
          </p>
        </div>
        <div class="col-auto">
          <q-btn
            color="primary"
            icon="add"
            label="New Project"
            unelevated
            class="q-px-lg"
            @click="openNewProjectDialog"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Filter and Search -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="projects-filters-grid">
            <div>
              <q-input v-model="searchQuery" placeholder="Search projects..." outlined dense>
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>
            <div>
              <q-select
                v-model="statusFilter"
                :options="statusOptions"
                label="Filter by Status"
                outlined
                dense
                clearable
              />
            </div>
            <div>
              <q-select v-model="sortBy" :options="sortOptions" label="Sort by" outlined dense />
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Projects Grid -->
      <div class="projects-grid">
        <div v-for="project in filteredProjects" :key="project.id">
          <q-card class="project-card" @click="navigateToProject(project.id)">
            <q-card-section class="bg-primary text-white">
              <div class="row items-center">
                <q-avatar :icon="project.icon" size="48px" class="bg-white text-primary" />
                <div class="col q-ml-md">
                  <div class="text-h6 text-weight-bold">{{ project.name }}</div>
                  <div class="text-caption">Created {{ formatDate(project.createdAt) }}</div>
                </div>
              </div>
            </q-card-section>

            <q-card-section class="project-card-content">
              <div class="text-grey-8 q-mb-md" style="min-height: 40px">
                {{ project.description }}
              </div>

              <div class="q-mb-sm">
                <div class="row items-center q-mb-xs">
                  <span class="text-caption text-grey-7">Progress</span>
                  <q-space />
                  <span class="text-caption text-weight-bold">{{ project.progress }}%</span>
                </div>
                <q-linear-progress
                  :value="project.progress / 100"
                  :color="getProgressColor(project.progress)"
                  class="q-mt-xs"
                />
              </div>

              <div class="row items-center q-mb-sm">
                <q-icon name="task_alt" size="xs" class="q-mr-xs text-grey-6" />
                <span class="text-caption text-grey-7">
                  {{ project.tasksCompleted }}/{{ project.totalTasks }} tasks
                </span>
              </div>

              <div class="row items-center q-mb-md">
                <q-icon name="group" size="xs" class="q-mr-xs text-grey-6" />
                <span class="text-caption text-grey-7">
                  {{ project.teamMembers.length }} team members
                </span>
              </div>

              <div class="row items-center justify-between">
                <q-chip :color="getStatusColor(project.status)" text-color="white" size="sm" dense>
                  {{ project.status }}
                </q-chip>
                <div class="text-caption text-grey-7">Due: {{ formatDate(project.dueDate) }}</div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions>
              <q-btn
                flat
                color="primary"
                icon="visibility"
                label="View Details"
                @click.stop="navigateToProject(project.id)"
              />
              <q-space />
              <q-btn flat icon="edit" color="grey-7" dense @click.stop="editProject(project)">
                <q-tooltip>Edit Project</q-tooltip>
              </q-btn>
              <q-btn
                flat
                icon="delete"
                color="red"
                dense
                @click.stop="confirmDeleteProject(project)"
              >
                <q-tooltip>Delete Project</q-tooltip>
              </q-btn>
            </q-card-actions>
          </q-card>
        </div>

        <!-- Empty State -->
        <div v-if="filteredProjects.length === 0" class="projects-grid-empty">
          <q-card class="text-center q-pa-xl">
            <q-icon name="folder_off" size="64px" class="text-grey-5 q-mb-md" />
            <div class="text-h6 text-grey-7 q-mb-sm">No projects found</div>
            <div class="text-caption text-grey-6 q-mb-md">
              {{
                searchQuery
                  ? 'Try adjusting your search or filters'
                  : 'Get started by creating your first project'
              }}
            </div>
            <q-btn
              v-if="!searchQuery"
              color="primary"
              icon="add"
              label="Create Project"
              unelevated
              @click="openNewProjectDialog"
            />
          </q-card>
        </div>
      </div>
    </div>

    <!-- New/Edit Project Dialog -->
    <q-dialog v-model="showNewProjectDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">{{ editingProject ? 'Edit Project' : 'Create New Project' }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="projectForm.name"
            label="Project Name *"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Project name is required']"
          />

          <q-input
            v-model="projectForm.description"
            label="Description *"
            type="textarea"
            filled
            rows="3"
            class="q-mb-md"
            :rules="[(val) => !!val || 'Description is required']"
          />

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select v-model="projectForm.icon" :options="iconOptions" label="Icon" filled>
                <template v-slot:prepend>
                  <q-icon :name="projectForm.icon" />
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps">
                    <q-item-section avatar>
                      <q-icon :name="scope.opt" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ scope.opt }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </div>
          </div>

          <q-input
            v-model="projectForm.dueDate"
            label="Due Date *"
            type="date"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Due date is required']"
          />

          <q-input
            v-model="projectForm.sprintStartDate"
            label="Sprint Start Date (first day of first sprint)"
            type="date"
            filled
            class="q-mb-md"
            hint="All sprints will be 2 weeks. Dates are calculated automatically from this start."
          />

          <q-select
            v-model="projectForm.teamMembers"
            :options="availableTeamMembers"
            option-value="id"
            option-label="name"
            label="Assign Team Members"
            filled
            multiple
            use-chips
            class="q-mb-md"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section avatar>
                  <q-avatar size="32px">
                    <img :src="scope.opt.avatar" />
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ scope.opt.name }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.role }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
            <template v-slot:selected-item="scope">
              <q-chip
                removable
                @remove="scope.removeAtIndex(scope.index)"
                :tabindex="scope.tabindex"
                color="primary"
                text-color="white"
                class="q-ma-xs"
              >
                <q-avatar>
                  <img :src="scope.opt.avatar" />
                </q-avatar>
                {{ scope.opt.name }}
              </q-chip>
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup @click="cancelProjectDialog" />
          <q-btn
            color="primary"
            :label="editingProject ? 'Save Changes' : 'Create Project'"
            @click="saveProject"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Confirm Delete</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete the project "<strong>{{ projectToDelete?.name }}</strong
          >"? This action cannot be undone.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="red" label="Delete" @click="deleteProject" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { format } from 'date-fns';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useProjectStore } from 'src/stores/project-store';
import { useTeamStore } from 'src/stores/team-store';
import { useActivityLog } from 'src/composables/useActivityLog';

const router = useRouter();
const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();
const { log } = useActivityLog();

// Reactive data
const showNewProjectDialog = ref(false);
const showDeleteDialog = ref(false);
const editingProject = ref<Project | null>(null);
const projectToDelete = ref<Project | null>(null);
const searchQuery = ref('');
const statusFilter = ref<string | null>(null);
const sortBy = ref('Recent');

// Fetch data from API
onMounted(async () => {
  await Promise.all([projectStore.fetchProjects(), teamStore.fetchTeamMembers()]);
});

interface Project {
  id: number;
  name: string;
  description: string;
  template: string;
  icon: string;
  progress: number;
  tasksCompleted: number;
  totalTasks: number;
  status: string;
  dueDate: Date;
  createdAt: Date;
  teamMembers: TeamMember[];
}

interface TeamMember {
  id: number;
  name: string;
  role: string;
  avatar: string;
}

interface ProjectForm {
  name: string;
  description: string;
  template: string;
  icon: string;
  dueDate: string;
  sprintStartDate: string;
  teamMembers: TeamMember[];
}

const projectForm = ref<ProjectForm>({
  name: '',
  description: '',
  template: 'Agile Development',
  icon: 'folder',
  dueDate: '',
  sprintStartDate: '',
  teamMembers: [],
});

// Get data from stores
const availableTeamMembers = computed(() => teamStore.teamMembers);

const iconOptions = [
  'folder',
  'shopping_cart',
  'phone_android',
  'cloud_upload',
  'dashboard',
  'rocket_launch',
  'analytics',
  'lightbulb',
  'code',
  'design_services',
];

const statusOptions = ['Not started', 'In progress', 'Completed'];

const sortOptions = ['Recent', 'Name', 'Due Date', 'Progress'];

// Computed
const filteredProjects = computed(() => {
  let filtered = [
    ...projectStore.projects.map((p) => {
      // Use backend-calculated values for totalTasks, tasksCompleted, and progress
      // Backend now dynamically calculates these from the database
      return {
        ...p,
        dueDate: typeof p.dueDate === 'string' ? new Date(p.dueDate) : p.dueDate,
        createdAt: typeof p.createdAt === 'string' ? new Date(p.createdAt) : p.createdAt,
        teamMembers: p.teamMemberIds
          .map((id) => teamStore.teamMembers.find((m) => m.id === id))
          .filter(Boolean) as TeamMember[],
      };
    }),
  ];

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      (p) => p.name.toLowerCase().includes(query) || p.description.toLowerCase().includes(query),
    );
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter((p) => p.status === statusFilter.value);
  }

  // Sort
  switch (sortBy.value) {
    case 'Name':
      filtered.sort((a, b) => a.name.localeCompare(b.name));
      break;
    case 'Due Date':
      filtered.sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime());
      break;
    case 'Progress':
      filtered.sort((a, b) => b.progress - a.progress);
      break;
    case 'Recent':
    default:
      filtered.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
      break;
  }

  return filtered;
});

// Methods
function getStatusColor(status: string): string {
  switch (status) {
    case 'Not started':
      return 'grey';
    case 'In progress':
      return 'blue';
    case 'Completed':
      return 'green';
    default:
      return 'grey';
  }
}

function getProgressColor(progress: number): string {
  if (progress >= 75) return 'green';
  if (progress >= 50) return 'blue';
  if (progress >= 25) return 'orange';
  return 'red';
}

function formatDate(date: Date): string {
  return format(date, 'MMM dd, yyyy');
}

function openNewProjectDialog() {
  log('project_create', 'projects');
  showNewProjectDialog.value = true;
}

function navigateToProject(projectId: number) {
  log('project_select', 'projects', { projectId });
  router.push(`/projects/${projectId}`);
}

function editProject(project: Project) {
  log('project_edit', 'projects', { projectId: project.id });
  editingProject.value = project;
  const p = project as Project & { sprintStartDate?: string };
  projectForm.value = {
    name: project.name,
    description: project.description,
    template: project.template,
    icon: project.icon,
    dueDate: format(project.dueDate, 'yyyy-MM-dd'),
    sprintStartDate: p.sprintStartDate || '',
    teamMembers: [...project.teamMembers],
  };
  showNewProjectDialog.value = true;
}

function confirmDeleteProject(project: Project) {
  log('project_delete', 'projects', { projectId: project.id });
  projectToDelete.value = project;
  showDeleteDialog.value = true;
}

async function deleteProject() {
  if (projectToDelete.value) {
    try {
      await projectStore.deleteProject(projectToDelete.value.id);
      $q.notify({
        message: `Project "${projectToDelete.value.name}" deleted successfully`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
    } catch (err) {
      console.error('Delete project error:', err);
      $q.notify({
        message: 'Failed to delete project',
        color: 'negative',
        icon: 'error',
        position: 'top',
      });
    }
  }
  showDeleteDialog.value = false;
  projectToDelete.value = null;
}

async function saveProject() {
  // Validate
  if (!projectForm.value.name || !projectForm.value.description || !projectForm.value.dueDate) {
    $q.notify({
      message: 'Please fill in all required fields',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  try {
    if (editingProject.value) {
      // Update existing project
      await projectStore.updateProject(editingProject.value.id, {
        name: projectForm.value.name,
        description: projectForm.value.description,
        template: projectForm.value.template,
        icon: projectForm.value.icon,
        dueDate: new Date(projectForm.value.dueDate),
        teamMemberIds: projectForm.value.teamMembers.map((m) => m.id),
        sprintStartDate: projectForm.value.sprintStartDate || null,
      });
      $q.notify({
        message: `Project "${projectForm.value.name}" updated successfully`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
    } else {
      // Create new project
      await projectStore.addProject({
        name: projectForm.value.name,
        description: projectForm.value.description,
        template: projectForm.value.template,
        icon: projectForm.value.icon,
        progress: 0,
        tasksCompleted: 0,
        totalTasks: 0,
        status: 'Not started',
        dueDate: new Date(projectForm.value.dueDate),
        createdAt: new Date(),
        teamMemberIds: projectForm.value.teamMembers.map((m) => m.id),
        roles: [],
        sprints: [],
        tasks: [],
        totalStoryPoints: 0,
        estimatedDuration: 0,
        sprintDurationDays: 14,
        sprintStartDate: projectForm.value.sprintStartDate || null,
      });
      $q.notify({
        message: `Project "${projectForm.value.name}" created successfully`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
    }

    showNewProjectDialog.value = false;
    cancelProjectDialog();
  } catch (err) {
    console.error('Save project error:', err);
    $q.notify({
      message: 'Failed to save project',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function cancelProjectDialog() {
  editingProject.value = null;
  projectForm.value = {
    name: '',
    description: '',
    template: 'Agile Development',
    icon: 'folder',
    dueDate: '',
    sprintStartDate: '',
    teamMembers: [],
  };
}
</script>

<style scoped>
.project-card {
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.projects-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
}

.projects-filters-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.projects-grid > div {
  display: flex;
}

.project-card-content {
  flex: 1;
}

.projects-grid-empty {
  grid-column: 1 / -1;
}

@media (max-width: 1240px) {
  .projects-filters-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .projects-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1023px) {
  .projects-filters-grid {
    grid-template-columns: 1fr;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }
}
</style>
