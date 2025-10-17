<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Team</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Manage your team members and their roles</p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="group_add"
            label="Invite Member"
            @click="showInviteDialog = true"
          />
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
            <q-card-section class="q-pb-none">
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
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_up" class="text-green" size="16px" />
                <span class="text-caption q-ml-xs text-green">+2</span>
                <span class="text-caption text-grey-7 q-ml-xs">this month</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-green-1">
            <q-card-section class="q-pb-none">
              <div class="row items-center no-wrap">
                <div class="col">
                  <div class="text-h4 text-weight-bold text-green">{{ onlineMembers.length }}</div>
                  <div class="text-caption text-grey-7">Online Now</div>
                </div>
                <div class="col-auto">
                  <q-icon name="circle" size="32px" class="text-green" />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-orange-1">
            <q-card-section class="q-pb-none">
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
            <q-card-section class="q-pt-none">
              <div class="row items-center">
                <q-icon name="trending_down" class="text-red" size="16px" />
                <span class="text-caption q-ml-xs text-red">-5%</span>
                <span class="text-caption text-grey-7 q-ml-xs">vs last week</span>
              </div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-12 col-md-3">
          <q-card class="stat-card bg-blue-1">
            <q-card-section class="q-pb-none">
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
              <div class="workload-chart">
                <div class="row q-gutter-sm">
                  <div v-for="member in teamMembers" :key="member.id" class="col">
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
              <div class="text-body2 text-grey-7 q-mb-sm">{{ member.role }}</div>

              <q-chip
                :color="getStatusColor(member.status)"
                text-color="white"
                size="sm"
                :icon="getStatusIcon(member.status)"
                :label="member.status"
                class="q-mb-md"
              />

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
              <q-btn flat color="primary" icon="chat" @click="chatWithMember(member)">
                <q-tooltip>Send message</q-tooltip>
              </q-btn>
              <q-btn flat color="secondary" icon="person" @click="viewMemberProfile(member)">
                <q-tooltip>View profile</q-tooltip>
              </q-btn>
              <q-btn flat color="orange" icon="assignment" @click="assignTaskToMember(member)">
                <q-tooltip>Assign task</q-tooltip>
              </q-btn>
            </q-card-actions>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Add Member Dialog -->
    <q-dialog v-model="showAddMemberDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add Team Member</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newMember.name"
            label="Full Name"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Name is required']"
          />

          <q-input
            v-model="newMember.email"
            label="Email"
            type="email"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Email is required']"
          />

          <q-input v-model="newMember.role" label="Role" filled class="q-mb-md" />

          <q-select
            v-model="newMember.skills"
            :options="availableSkills"
            label="Skills"
            multiple
            use-chips
            filled
            class="q-mb-md"
          />

          <q-slider
            v-model="newMember.workload"
            :min="0"
            :max="100"
            :step="5"
            label
            label-always
            color="primary"
          />
          <div class="text-caption text-grey-7 q-mt-xs">
            Initial workload: {{ newMember.workload }}%
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelAddMember" />
          <q-btn
            color="primary"
            label="Add Member"
            @click="addMember"
            :disable="!newMember.name || !newMember.email"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Invite Member Dialog -->
    <q-dialog v-model="showInviteDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Invite Team Member</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="inviteEmail"
            label="Email Address"
            type="email"
            filled
            class="q-mb-md"
          />

          <q-input
            v-model="inviteMessage"
            label="Personal Message (Optional)"
            type="textarea"
            filled
            rows="3"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Send Invitation"
            @click="sendInvitation"
            :disable="!inviteEmail"
          />
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
        </q-card-section>

        <q-card-section>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <div class="text-caption text-grey-7">Status</div>
              <q-chip
                :color="getStatusColor(selectedMember.status)"
                text-color="white"
                size="sm"
                :icon="getStatusIcon(selectedMember.status)"
                :label="selectedMember.status"
              />
            </div>
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
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useMockDataStore, type TeamMember } from 'stores/mock-data';
import { useQuasar } from 'quasar';

const mockDataStore = useMockDataStore();
const $q = useQuasar();

// Reactive data
const showAddMemberDialog = ref(false);
const showInviteDialog = ref(false);
const showMemberProfile = ref(false);
const selectedMember = ref<TeamMember | null>(null);
const inviteEmail = ref('');
const inviteMessage = ref('');

const newMember = reactive({
  name: '',
  email: '',
  role: '',
  skills: [] as string[],
  workload: 50,
});

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

// Computed
const teamMembers = computed(() => mockDataStore.teamMembers);

const onlineMembers = computed(() => teamMembers.value.filter((m) => m.status === 'online'));

const averageWorkload = computed(() => {
  if (teamMembers.value.length === 0) return 0;
  const total = teamMembers.value.reduce((sum, m) => sum + m.workload, 0);
  return Math.round(total / teamMembers.value.length);
});

const totalActiveProjects = computed(() =>
  teamMembers.value.reduce((sum, m) => sum + m.activeProjects, 0),
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

function getStatusColor(status: string): string {
  switch (status) {
    case 'online':
      return 'green';
    case 'busy':
      return 'orange';
    case 'away':
      return 'yellow';
    case 'offline':
      return 'grey';
    default:
      return 'grey';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'online':
      return 'circle';
    case 'busy':
      return 'do_not_disturb';
    case 'away':
      return 'schedule';
    case 'offline':
      return 'circle';
    default:
      return 'circle';
  }
}

function chatWithMember(member: TeamMember) {
  // Simulate chat functionality
  console.log('Chat with:', member.name);
  $q.notify({
    message: `Opening chat with ${member.name}`,
    color: 'info',
    icon: 'chat',
    position: 'top',
  });
}

function viewMemberProfile(member: TeamMember) {
  selectedMember.value = member;
  showMemberProfile.value = true;
}

function assignTaskToMember(member: TeamMember) {
  // Simulate task assignment
  console.log('Assign task to:', member.name);
  $q.notify({
    message: `Task assignment dialog for ${member.name} - Feature coming soon!`,
    color: 'info',
    icon: 'assignment',
    position: 'top',
  });
}

function addMember() {
  // Simulate add member functionality
  console.log('Adding member:', newMember);

  $q.notify({
    message: `Team member "${newMember.name}" added successfully!`,
    color: 'positive',
    icon: 'person_add',
    position: 'top',
  });

  showAddMemberDialog.value = false;
  cancelAddMember();
}

function cancelAddMember() {
  Object.assign(newMember, {
    name: '',
    email: '',
    role: '',
    skills: [],
    workload: 50,
  });
}

function sendInvitation() {
  // Simulate invitation functionality
  console.log('Sending invitation to:', inviteEmail.value);

  $q.notify({
    message: `Invitation sent to ${inviteEmail.value}!`,
    color: 'positive',
    icon: 'mail',
    position: 'top',
  });

  showInviteDialog.value = false;
  inviteEmail.value = '';
  inviteMessage.value = '';
}

function editMemberProfile() {
  // Simulate edit profile functionality
  console.log('Edit profile for:', selectedMember.value?.name);

  $q.notify({
    message: `Profile editing for ${selectedMember.value?.name} - Feature coming soon!`,
    color: 'info',
    icon: 'edit',
    position: 'top',
  });

  showMemberProfile.value = false;
}

onMounted(() => {
  mockDataStore.initializeData();
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

.workload-chart {
  height: 200px;
  position: relative;
}

.workload-bar-container {
  height: 150px;
  position: relative;
  display: flex;
  align-items: end;
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
