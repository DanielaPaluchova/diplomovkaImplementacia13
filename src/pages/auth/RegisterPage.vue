<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="flex flex-center bg-gradient">
        <q-card class="register-card" style="width: 500px; max-width: 90vw">
          <q-card-section class="text-center q-pt-xl">
            <q-avatar size="80px" class="q-mb-md">
              <q-icon name="trending_up" size="48px" color="primary" />
            </q-avatar>
            <div class="text-h4 text-weight-bold text-primary q-mb-xs">Create Account</div>
            <div class="text-subtitle2 text-grey-7">Sign up to get started</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="handleRegister" class="q-gutter-md">
              <q-input
                v-model="name"
                label="Full Name"
                outlined
                :rules="[(val) => !!val || 'Name is required']"
                lazy-rules
              >
                <template v-slot:prepend>
                  <q-icon name="person" />
                </template>
              </q-input>

              <q-input
                v-model="email"
                type="email"
                label="Email"
                outlined
                :rules="[(val) => !!val || 'Email is required', isValidEmail]"
                lazy-rules
              >
                <template v-slot:prepend>
                  <q-icon name="email" />
                </template>
              </q-input>

              <q-input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                label="Password"
                outlined
                :rules="[
                  (val) => !!val || 'Password is required',
                  (val) => val.length >= 6 || 'Password must be at least 6 characters',
                ]"
                lazy-rules
              >
                <template v-slot:prepend>
                  <q-icon name="lock" />
                </template>
                <template v-slot:append>
                  <q-icon
                    :name="showPassword ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="showPassword = !showPassword"
                  />
                </template>
                <template v-slot:hint>
                  <div class="row items-center q-gutter-xs">
                    <q-icon
                      name="check_circle"
                      :color="password.length >= 6 ? 'green' : 'grey'"
                      size="xs"
                    />
                    <span :class="password.length >= 6 ? 'text-green' : 'text-grey-7'">
                      At least 6 characters
                    </span>
                  </div>
                </template>
              </q-input>

              <q-input
                v-model="confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                label="Confirm Password"
                outlined
                :rules="[
                  (val) => !!val || 'Please confirm password',
                  (val) => val === password || 'Passwords do not match',
                ]"
                lazy-rules
              >
                <template v-slot:prepend>
                  <q-icon name="lock" />
                </template>
              </q-input>

              <q-separator class="q-my-md" />

              <!-- Role Selection -->
              <div class="q-mb-md">
                <div class="text-subtitle2 q-mb-sm">I am a:</div>
                <q-option-group
                  v-model="selectedRole"
                  :options="roleOptions"
                  color="primary"
                  inline
                />
                <div class="text-caption text-grey-7 q-mt-xs">
                  {{ getRoleDescription(selectedRole) }}
                </div>
              </div>

              <q-separator class="q-my-md" />

              <q-checkbox v-model="agreeTerms" dense>
                <span class="text-body2">
                  I agree to the
                  <a href="#" class="text-primary">Terms of Service</a>
                  and
                  <a href="#" class="text-primary">Privacy Policy</a>
                </span>
              </q-checkbox>

              <q-btn
                type="submit"
                color="primary"
                label="Create Account"
                class="full-width"
                size="lg"
                :loading="authStore.isLoading"
                :disable="!name || !email || !password || !confirmPassword || !agreeTerms"
              />
            </q-form>

            <q-banner v-if="authStore.error" class="bg-red-1 text-red q-mt-md" rounded>
              <template v-slot:avatar>
                <q-icon name="error" color="red" />
              </template>
              {{ authStore.error }}
            </q-banner>
          </q-card-section>

          <q-separator />

          <q-card-section class="text-center">
            <div class="text-body2 text-grey-7">
              Already have an account?
              <router-link to="/login" class="text-primary text-weight-medium">
                Sign in
              </router-link>
            </div>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth-store';

const router = useRouter();
const $q = useQuasar();
const authStore = useAuthStore();

// Form state
const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const agreeTerms = ref(false);
const selectedRole = ref<'developer' | 'manager'>('developer');

// Role options
const roleOptions = [
  {
    label: 'Developer',
    value: 'developer',
    icon: 'code',
  },
  {
    label: 'Project Manager',
    value: 'manager',
    icon: 'manage_accounts',
  },
];

// Helper function
function getRoleDescription(role: string): string {
  switch (role) {
    case 'developer':
      return 'I will be working on development tasks and contributing to projects.';
    case 'manager':
      return 'I will be managing projects, assigning tasks, and coordinating the team.';
    default:
      return '';
  }
}

// Validation
function isValidEmail(val: string): boolean | string {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(val) || 'Invalid email format';
}

// Actions
async function handleRegister() {
  if (password.value !== confirmPassword.value) {
    $q.notify({
      message: 'Passwords do not match',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
    return;
  }

  const success = await authStore.register({
    email: email.value,
    password: password.value,
    name: name.value,
    role: selectedRole.value,
  });

  if (success) {
    $q.notify({
      message: `Account created successfully! Welcome, ${authStore.userName}!`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });

    // Redirect to homepage
    router.push('/');
  }
}
</script>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border-radius: 16px;
}

a {
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
