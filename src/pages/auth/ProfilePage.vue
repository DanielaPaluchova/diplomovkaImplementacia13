<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Profile Settings</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Manage your account settings and preferences</p>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <div class="row q-gutter-lg">
        <!-- Profile Card -->
        <div class="col-12 col-md-4">
          <q-card>
            <q-card-section class="text-center">
              <q-avatar size="120px" class="q-mb-md">
                <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="Profile" />
                <div v-else class="bg-primary text-white text-h4">
                  {{ authStore.userInitials }}
                </div>
              </q-avatar>

              <div class="text-h6 text-weight-bold">{{ authStore.user?.name }}</div>
              <div class="text-body2 text-grey-7 q-mb-sm">{{ authStore.user?.email }}</div>

              <q-chip
                :color="getRoleColor(authStore.user?.role)"
                text-color="white"
                :label="authStore.user?.role.toUpperCase()"
              />

              <q-separator class="q-my-md" />

              <div class="text-caption text-grey-7 q-mb-xs">Member since</div>
              <div class="text-body2 text-weight-medium">
                {{ formatDate(authStore.user?.createdAt) }}
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Edit Profile Form -->
        <div class="col-12 col-md-8">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Personal Information</div>

              <q-form @submit.prevent="updateProfile" class="q-gutter-md">
                <q-input
                  v-model="form.name"
                  label="Full Name"
                  outlined
                  :rules="[(val) => !!val || 'Name is required']"
                >
                  <template v-slot:prepend>
                    <q-icon name="person" />
                  </template>
                </q-input>

                <q-input
                  v-model="form.email"
                  type="email"
                  label="Email"
                  outlined
                  :rules="[(val) => !!val || 'Email is required']"
                  hint="Email cannot be changed after registration"
                  readonly
                >
                  <template v-slot:prepend>
                    <q-icon name="email" />
                  </template>
                </q-input>

                <div class="text-subtitle2 q-mb-sm">Role</div>
                <q-chip
                  :color="getRoleColor(form.role)"
                  text-color="white"
                  :label="form.role.toUpperCase()"
                  icon="badge"
                />
                <div class="text-caption text-grey-7 q-mb-md">
                  Role is managed by administrators
                </div>

                <div class="row q-gutter-sm justify-end q-mt-lg">
                  <q-btn flat label="Cancel" @click="resetForm" />
                  <q-btn
                    type="submit"
                    color="primary"
                    label="Save Changes"
                    :loading="authStore.isLoading"
                    :disable="!hasChanges"
                  />
                </div>
              </q-form>
            </q-card-section>
          </q-card>

          <!-- Security Settings -->
          <q-card class="q-mt-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Security</div>

              <q-list>
                <q-item>
                  <q-item-section avatar>
                    <q-icon name="lock" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Password</q-item-label>
                    <q-item-label caption>Last changed 30 days ago</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn flat color="primary" label="Change" @click="showChangePassword = true" />
                  </q-item-section>
                </q-item>

                <q-separator />

                <q-item>
                  <q-item-section avatar>
                    <q-icon name="logout" color="orange" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Sign Out</q-item-label>
                    <q-item-label caption>Sign out from your account</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn flat color="orange" label="Sign Out" @click="handleLogout" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Change Password Dialog -->
    <q-dialog v-model="showChangePassword">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Change Password</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="passwordForm.currentPassword"
            type="password"
            label="Current Password"
            outlined
            class="q-mb-md"
          />
          <q-input
            v-model="passwordForm.newPassword"
            type="password"
            label="New Password"
            outlined
            class="q-mb-md"
            :rules="[(val) => val.length >= 6 || 'At least 6 characters']"
          />
          <q-input
            v-model="passwordForm.confirmPassword"
            type="password"
            label="Confirm New Password"
            outlined
            :rules="[(val) => val === passwordForm.newPassword || 'Passwords do not match']"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="showChangePassword = false" />
          <q-btn color="primary" label="Change Password" @click="changePassword" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth-store';
import { format } from 'date-fns';

const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();

// Form state
const form = reactive({
  name: authStore.user?.name || '',
  email: authStore.user?.email || '',
  role: authStore.user?.role || 'developer',
});

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

const showChangePassword = ref(false);

// Computed
const hasChanges = computed(() => {
  return form.name !== authStore.user?.name;
});

// Methods
function getRoleColor(role?: string): string {
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

function formatDate(date?: Date): string {
  if (!date) return 'N/A';
  return format(new Date(date), 'MMMM dd, yyyy');
}

async function updateProfile() {
  const success = await authStore.updateProfile({
    name: form.name,
  });

  if (success) {
    $q.notify({
      message: 'Profile updated successfully',
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
  } else {
    $q.notify({
      message: authStore.error || 'Failed to update profile',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function resetForm() {
  form.name = authStore.user?.name || '';
  form.email = authStore.user?.email || '';
  form.role = authStore.user?.role || 'developer';
}

async function changePassword() {
  // TODO: Implement password change with backend
  $q.notify({
    message: 'Password changed successfully',
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
  showChangePassword.value = false;

  // Reset form
  passwordForm.currentPassword = '';
  passwordForm.newPassword = '';
  passwordForm.confirmPassword = '';
}

function handleLogout() {
  $q.dialog({
    title: 'Confirm Logout',
    message: 'Are you sure you want to sign out?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    await authStore.logout();
    $q.notify({
      message: 'Signed out successfully',
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
    router.push('/login');
  });
}
</script>

<style scoped>
/* Add any custom styles here */
</style>
