<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Team</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Manage your team members and their roles</p>
        </div>
        <div class="row q-gutter-md" v-if="authStore.isManager">
          <q-btn
            color="primary"
            icon="person_add"
            label="Add Member"
            @click="showAddMemberDialog = true"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Team Stats -->
      <div class="row q-gutter-md q-mb-lg">
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-primary-1">
            <q-card-section>
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-primary">{{ teamMembers.length }}</div>
                  <div class="text-caption text-grey-7">Team Members</div>
                </div>
                <div class="col-auto">
                  <q-icon name="group" size="32px" class="text-primary" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-orange-1">
            <q-card-section>
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-orange">{{ averageWorkload }}%</div>
                  <div class="text-caption text-grey-7">Avg. Workload</div>
                </div>
                <div class="col-auto">
                  <q-icon name="speed" size="32px" class="text-orange" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-blue-1">
            <q-card-section>
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-blue">{{ totalActiveProjects }}</div>
                  <div class="text-caption text-grey-7">Active Projects</div>
                </div>
                <div class="col-auto">
                  <q-icon name="folder" size="32px" class="text-blue" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Team Overview Chart -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Team Workload Distribution</div>
              <div class="row q-gutter-sm">
                <div v-for="member in teamMembers" :key="member.id" class="col">
                  <div class="workload-chart-item">
                    <div class="workload-bar-container">
                      <div
                        class="workload-bar"
                        :class="getWorkloadClass(member.workload)"
                        :style="{ height: `${Math.min(member.workload, 100)}%` }"
                      />
                      <div class="workload-overflow" v-if="member.workload > 100" />
                    </div>
                    <div class="text-center q-mt-sm">
                      <q-avatar size="24px" class="q-mb-xs">
                        <img :src="member.avatar" />
                      </q-avatar>
                      <div class="text-caption">{{ member.name.split(' ')[0] }}</div>
                      <div
                        class="text-caption text-weight-bold"
                        :class="getWorkloadTextClass(member.workload)"
                      >
                        {{ member.workload }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Skills Distribution</div>
              <div class="skills-chart">
                <div v-for="skill in topSkills" :key="skill.name" class="skill-item q-mb-sm">
                  <div class="row items-center">
                    <div class="col-4 text-caption">{{ skill.name }}</div>
                    <div class="col">
                      <q-linear-progress
                        :value="skill.count / teamMembers.length"
                        color="primary"
                        style="height: 6px"
                      />
                    </div>
                    <div class="col-auto text-caption text-grey-7">{{ skill.count }}</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Team Members Grid -->
      <div class="row q-gutter-lg">
        <div class="col-12 col-md-6 col-lg-4" v-for="member in teamMembers" :key="member.id">
          <q-card class="team-member-card">
            <q-card-section class="text-center">
              <q-avatar size="64px" class="q-mb-md">
                <img :src="member.avatar" />
              </q-avatar>

              <div class="text-h6 text-weight-bold">{{ member.name }}</div>
              <div class="text-body2 text-grey-7 q-mb-md">{{ member.role }}</div>

              <div class="row q-gutter-sm q-mb-md">
                <div class="col">
                  <div class="text-caption text-grey-7">Projects</div>
                  <div class="text-h6 text-primary">{{ member.activeProjects }}</div>
                </div>
                <div class="col">
                  <div class="text-caption text-grey-7">Workload</div>
                  <div
                    class="text-h6"
                    :class="
                      member.workload > 100
                        ? 'text-red'
                        : member.workload > 80
                          ? 'text-orange'
                          : 'text-green'
                    "
                  >
                    {{ member.workload }}%
                  </div>
                </div>
              </div>

              <q-linear-progress
                :value="member.workload / 100"
                :color="member.workload > 100 ? 'red' : member.workload > 80 ? 'orange' : 'green'"
                class="q-mb-md"
                style="height: 6px"
              />

              <div class="row q-gutter-xs">
                <q-chip
                  v-for="skill in member.skills.slice(0, 3)"
                  :key="skill"
                  size="sm"
                  outline
                  color="primary"
                  :label="skill"
                />
                <q-chip
                  v-if="member.skills.length > 3"
                  size="sm"
                  outline
                  color="grey"
                  :label="`+${member.skills.length - 3}`"
                />
              </div>
            </q-card-section>

            <q-card-actions align="center">
              <q-btn flat color="secondary" icon="person" @click="viewMemberProfile(member)">
                <q-tooltip>View profile</q-tooltip>
              </q-btn>
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Add Member Dialog -->
    <q-dialog v-model="showAddMemberDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add Team Member</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-center q-mb-md">
            <q-avatar size="80px" class="q-mb-sm">
              <img :src="newMember.avatar || 'https://cdn.quasar.dev/img/avatar.png'" />
            </q-avatar>
            <div>
              <q-btn
                size="sm"
                color="primary"
                icon="photo_camera"
                label="Upload Photo"
                @click="triggerNewAvatarUpload"
              />
              <input
                ref="newAvatarInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleNewAvatarUpload"
              />
            </div>
          </div>

          <q-input v-model="newMember.name" label="Full Name" filled class="q-mb-md" />

          <q-input v-model="newMember.email" label="Email" type="email" filled class="q-mb-md" />

          <q-select
            v-model="newMember.role"
            :options="availableRoles"
            label="Role"
            filled
            class="q-mb-md"
          />

          <q-input
            v-if="newMember.role === 'Other'"
            v-model="newMember.customRole"
            label="Specify Role"
            filled
            class="q-mb-md"
          />

          <q-select
            v-model="newMember.skills"
            :options="skillOptions"
            label="Skills"
            multiple
            use-chips
            use-input
            @filter="filterSkills"
            @new-value="createSkill"
            filled
            class="q-mb-md"
            hint="Type and press Enter to add custom skills"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            @click="
              showAddMemberDialog = false;
              cancelAddMember();
            "
          />
          <q-btn color="primary" label="Add Member" @click="addMember" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Member Profile Dialog -->
    <q-dialog v-model="showMemberProfile" v-if="selectedMember">
      <q-card style="min-width: 500px">
        <q-card-section class="text-center">
          <q-avatar size="80px" class="q-mb-md">
            <img :src="selectedMember.avatar" />
          </q-avatar>
          <div class="text-h5 text-weight-bold">{{ selectedMember.name }}</div>
          <div class="text-body1 text-grey-7">{{ selectedMember.role }}</div>
          <!-- System Role Badge -->
          <q-chip
            v-if="selectedMember.systemRole"
            :color="getSystemRoleColor(selectedMember.systemRole)"
            text-color="white"
            size="sm"
            class="q-mt-xs"
          >
            <q-icon
              :name="getSystemRoleIcon(selectedMember.systemRole)"
              size="xs"
              class="q-mr-xs"
            />
            {{ getSystemRoleLabel(selectedMember.systemRole) }}
          </q-chip>
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <div class="text-caption text-grey-7">Workload</div>
              <div class="text-h6" :class="getWorkloadTextClass(selectedMember.workload)">
                {{ selectedMember.workload }}%
              </div>
            </div>
            <div class="col">
              <div class="text-caption text-grey-7">Active Projects</div>
              <div class="text-h6 text-primary">{{ selectedMember.activeProjects }}</div>
            </div>
          </div>

          <div class="q-mb-md">
            <div class="text-caption text-grey-7 q-mb-sm">Skills</div>
            <div class="row q-gutter-xs">
              <q-chip
                v-for="skill in selectedMember.skills"
                :key="skill"
                size="sm"
                color="primary"
                text-color="white"
                :label="skill"
              />
            </div>
          </div>

          <div>
            <div class="text-caption text-grey-7 q-mb-sm">Contact</div>
            <div class="text-body2">{{ selectedMember.email }}</div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" v-close-popup />
          <q-btn color="primary" icon="edit" label="Edit Profile" @click="editMemberProfile" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Member Dialog -->
    <q-dialog v-model="showEditMemberDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Edit Team Member</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-center q-mb-md">
            <q-avatar size="80px" class="q-mb-sm">
              <img :src="editMember.avatar || 'https://cdn.quasar.dev/img/avatar.png'" />
            </q-avatar>
            <div>
              <q-btn
                size="sm"
                color="primary"
                icon="photo_camera"
                label="Upload Photo"
                @click="triggerEditAvatarUpload"
              />
              <input
                ref="editAvatarInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleEditAvatarUpload"
              />
            </div>
          </div>

          <q-input v-model="editMember.name" label="Full Name" filled class="q-mb-md" />

          <q-input v-model="editMember.email" label="Email" type="email" filled class="q-mb-md" />

          <q-select
            v-model="editMember.role"
            :options="availableRoles"
            label="Team Role"
            filled
            class="q-mb-md"
            hint="Team role describes their position (e.g. Frontend Developer)"
          />

          <q-input
            v-if="editMember.role === 'Other'"
            v-model="editMember.customRole"
            label="Specify Role"
            filled
            class="q-mb-md"
          />

          <!-- System Role (Permissions) - Only for Manager/Admin -->
          <q-select
            v-if="authStore.isManager"
            v-model="editMember.systemRole"
            :options="systemRoleOptions"
            label="System Role (Permissions)"
            filled
            class="q-mb-md"
            hint="System role controls access permissions"
          >
            <template v-slot:prepend>
              <q-icon name="security" />
            </template>
          </q-select>

          <q-select
            v-model="editMember.skills"
            :options="skillOptions"
            label="Skills"
            multiple
            use-chips
            use-input
            @filter="filterSkills"
            @new-value="createSkill"
            filled
            class="q-mb-md"
            hint="Type and press Enter to add custom skills"
          />

          <div class="q-mb-sm">
            <div class="text-caption text-grey-7">Workload: {{ editMember.workload }}%</div>
            <q-slider
              v-model="editMember.workload"
              :min="0"
              :max="100"
              :step="5"
              label
              color="primary"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            @click="
              showEditMemberDialog = false;
              cancelEditMember();
            "
          />
          <q-btn color="primary" label="Save Changes" @click="saveEditMember" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useTeamStore, type TeamMember } from 'src/stores/team-store';
import { useAuthStore } from 'src/stores/auth-store';
import { useQuasar } from 'quasar';

const teamStore = useTeamStore();
const authStore = useAuthStore();
const $q = useQuasar();

// Fetch team members from API
onMounted(async () => {
  await teamStore.fetchTeamMembers();
});

// Reactive data
const showAddMemberDialog = ref(false);
const showMemberProfile = ref(false);
const showEditMemberDialog = ref(false);
const selectedMember = ref<TeamMember | null>(null);

const newMember = reactive({
  name: '',
  email: '',
  role: '',
  customRole: '',
  skills: [] as string[],
  workload: 0,
  avatar: '',
});

const editMember = reactive({
  id: 0,
  name: '',
  email: '',
  role: '',
  customRole: '',
  systemRole: 'developer',
  skills: [] as string[],
  workload: 0,
  avatar: '',
});

const newAvatarInput = ref<HTMLInputElement | null>(null);
const editAvatarInput = ref<HTMLInputElement | null>(null);

const availableRoles = [
  'Senior Frontend Developer',
  'Frontend Developer',
  'Junior Frontend Developer',
  'Senior Backend Developer',
  'Backend Developer',
  'Junior Backend Developer',
  'Full Stack Developer',
  'Senior Full Stack Developer',
  'DevOps Engineer',
  'Senior DevOps Engineer',
  'UI/UX Designer',
  'Senior UI/UX Designer',
  'Project Manager',
  'Product Manager',
  'Scrum Master',
  'QA Engineer',
  'Senior QA Engineer',
  'Data Engineer',
  'Machine Learning Engineer',
  'Technical Lead',
  'Software Architect',
  'Other',
];

const systemRoleOptions = [
  {
    label: 'Viewer',
    value: 'viewer',
    description: 'Read-only access to projects',
    icon: 'visibility',
  },
  {
    label: 'Developer',
    value: 'developer',
    description: 'Can work on tasks and projects',
    icon: 'code',
  },
  {
    label: 'Project Manager',
    value: 'manager',
    description: 'Can manage projects and team members',
    icon: 'manage_accounts',
  },
  {
    label: 'Admin',
    value: 'admin',
    description: 'Full system access',
    icon: 'admin_panel_settings',
  },
];

const availableSkills = [
  'Vue.js',
  'React',
  'Angular',
  'TypeScript',
  'JavaScript',
  'Python',
  'Java',
  'C#',
  'PHP',
  'Ruby',
  'Node.js',
  'Django',
  'Spring',
  '.NET',
  'Laravel',
  'PostgreSQL',
  'MySQL',
  'MongoDB',
  'Redis',
  'Elasticsearch',
  'Docker',
  'Kubernetes',
  'AWS',
  'Azure',
  'GCP',
  'Jenkins',
  'GitLab CI',
  'GitHub Actions',
  'Terraform',
  'Figma',
  'Adobe XD',
  'Sketch',
  'Prototyping',
  'User Research',
  'Scrum',
  'Kanban',
  'PERT',
  'Risk Management',
  'Agile',
];

const skillOptions = ref([...availableSkills]);

// Computed
const teamMembers = computed(() => teamStore.teamMembers);

const averageWorkload = computed(() => {
  if (teamMembers.value.length === 0) return 0;
  const total = teamMembers.value.reduce((sum, m) => sum + m.workload, 0);
  return Math.round(total / teamMembers.value.length);
});

const totalActiveProjects = computed(() =>
  teamMembers.value.reduce((sum, m) => sum + (m.activeProjects || 0), 0),
);

const topSkills = computed(() => {
  const skillCounts: Record<string, number> = {};

  teamMembers.value.forEach((member) => {
    member.skills.forEach((skill) => {
      skillCounts[skill] = (skillCounts[skill] || 0) + 1;
    });
  });

  return Object.entries(skillCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
});

// Methods
function getWorkloadClass(workload: number): string {
  if (workload > 100) return 'bg-red';
  if (workload > 80) return 'bg-orange';
  if (workload > 60) return 'bg-yellow';
  return 'bg-green';
}

function getWorkloadTextClass(workload: number): string {
  if (workload > 100) return 'text-red';
  if (workload > 80) return 'text-orange';
  return 'text-green';
}

function viewMemberProfile(member: TeamMember) {
  selectedMember.value = member;
  showMemberProfile.value = true;
}

async function addMember() {
  // Validate required fields
  if (!newMember.name || !newMember.email || !newMember.role) {
    $q.notify({
      message: 'Please fill in all required fields',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Use custom role if "Other" was selected
  const finalRole = newMember.role === 'Other' ? newMember.customRole : newMember.role;

  if (newMember.role === 'Other' && !newMember.customRole) {
    $q.notify({
      message: 'Please specify the role',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Add member to store via API
  try {
    await teamStore.addTeamMember({
      name: newMember.name,
      email: newMember.email,
      role: finalRole,
      avatar: newMember.avatar || 'https://cdn.quasar.dev/img/avatar.png',
      skills: newMember.skills,
      workload: newMember.workload,
    });

    $q.notify({
      message: `Team member "${newMember.name}" added successfully!`,
      color: 'positive',
      icon: 'person_add',
      position: 'top',
    });

    showAddMemberDialog.value = false;
    cancelAddMember();
  } catch (err) {
    console.error('Add team member error:', err);
    $q.notify({
      message: 'Failed to add team member',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function cancelAddMember() {
  Object.assign(newMember, {
    name: '',
    email: '',
    role: '',
    customRole: '',
    skills: [],
    workload: 0,
    avatar: '',
  });
}

function triggerNewAvatarUpload() {
  newAvatarInput.value?.click();
}

function handleNewAvatarUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      newMember.avatar = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

function filterSkills(val: string, update: (fn: () => void) => void) {
  if (val === '') {
    update(() => {
      skillOptions.value = [...availableSkills];
    });
    return;
  }

  update(() => {
    const needle = val.toLowerCase();
    skillOptions.value = availableSkills.filter((v) => v.toLowerCase().indexOf(needle) > -1);
  });
}

function createSkill(
  val: string,
  done: (item?: string, mode?: 'add' | 'add-unique' | 'toggle') => void,
) {
  if (val.length > 0) {
    if (!availableSkills.includes(val)) {
      availableSkills.push(val);
    }
    done(val, 'add-unique');
  }
}

function editMemberProfile() {
  if (!selectedMember.value) return;

  // Copy selected member data to edit form
  Object.assign(editMember, {
    id: selectedMember.value.id,
    name: selectedMember.value.name,
    email: selectedMember.value.email,
    role: selectedMember.value.role,
    customRole: '',
    systemRole: selectedMember.value.systemRole || 'developer',
    skills: [...selectedMember.value.skills],
    workload: selectedMember.value.workload,
    avatar: selectedMember.value.avatar,
  });

  // Check if role is custom (not in availableRoles)
  if (!availableRoles.includes(selectedMember.value.role)) {
    editMember.role = 'Other';
    editMember.customRole = selectedMember.value.role;
  }

  showMemberProfile.value = false;
  showEditMemberDialog.value = true;
}

function cancelEditMember() {
  Object.assign(editMember, {
    id: 0,
    name: '',
    email: '',
    role: '',
    customRole: '',
    skills: [],
    workload: 0,
    avatar: '',
  });
}

function triggerEditAvatarUpload() {
  editAvatarInput.value?.click();
}

function handleEditAvatarUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      editMember.avatar = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

async function saveEditMember() {
  // Validate required fields
  if (!editMember.name || !editMember.email || !editMember.role) {
    $q.notify({
      message: 'Please fill in all required fields',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Use custom role if "Other" was selected
  const finalRole = editMember.role === 'Other' ? editMember.customRole : editMember.role;

  if (editMember.role === 'Other' && !editMember.customRole) {
    $q.notify({
      message: 'Please specify the role',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Update member using teamStore
  try {
    await teamStore.updateTeamMember(editMember.id, {
      name: editMember.name,
      email: editMember.email,
      role: finalRole,
      skills: [...editMember.skills],
      workload: editMember.workload,
      ...(editMember.avatar && { avatar: editMember.avatar }),
    });
  } catch (err) {
    console.error('Update team member error:', err);
    $q.notify({
      message: 'Failed to update team member',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
    return;
  }

  $q.notify({
    message: `Team member "${editMember.name}" updated successfully!`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });

  showEditMemberDialog.value = false;
  cancelEditMember();
}

// Helper functions for system role display
function getSystemRoleColor(role: string): string {
  switch (role) {
    case 'admin':
      return 'red';
    case 'manager':
      return 'blue';
    case 'developer':
      return 'green';
    case 'viewer':
      return 'grey';
    default:
      return 'grey';
  }
}

function getSystemRoleIcon(role: string): string {
  switch (role) {
    case 'admin':
      return 'admin_panel_settings';
    case 'manager':
      return 'manage_accounts';
    case 'developer':
      return 'code';
    case 'viewer':
      return 'visibility';
    default:
      return 'person';
  }
}

function getSystemRoleLabel(role: string): string {
  switch (role) {
    case 'admin':
      return 'Admin';
    case 'manager':
      return 'Project Manager';
    case 'developer':
      return 'Developer';
    case 'viewer':
      return 'Viewer';
    default:
      return role;
  }
}

onMounted(async () => {
  await Promise.all([teamStore.fetchTeamMembers()]);
});
</script>

<style scoped>
.stat-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.team-member-card {
  transition: all 0.2s ease;
  height: 100%;
}

.team-member-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.workload-chart-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 250px;
}

.workload-bar-container {
  height: 150px;
  width: 100%;
  position: relative;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.workload-bar {
  width: 20px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  position: relative;
}

.workload-overflow {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 10px solid #f44336;
}

.skill-item {
  min-height: 24px;
}
</style>
