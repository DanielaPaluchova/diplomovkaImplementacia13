<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="flex flex-center bg-gradient">
        <q-card class="login-card" style="width: 450px; max-width: 90vw">
          <q-card-section class="text-center q-pt-xl">
            <q-avatar size="80px" class="q-mb-md">
              <q-icon name="trending_up" size="48px" color="primary" />
            </q-avatar>
            <div class="text-h4 text-weight-bold text-primary q-mb-xs">Darlana</div>
            <div class="text-subtitle2 text-grey-7">Sign in to your account</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="handleLogin" class="q-gutter-md">
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
                :rules="[(val) => !!val || 'Password is required']"
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
              </q-input>

              <div class="row items-center justify-between">
                <q-checkbox v-model="rememberMe" label="Remember me" dense />
                <q-btn flat dense color="primary" label="Forgot password?" size="sm" />
              </div>

              <q-btn
                type="submit"
                color="primary"
                label="Sign In"
                class="full-width"
                size="lg"
                :loading="authStore.isLoading"
                :disable="!email || !password"
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
              Don't have an account?
              <router-link to="/register" class="text-primary text-weight-medium">
                Sign up
              </router-link>
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <q-expansion-item label="Demo Accounts" icon="info" header-class="text-grey-7" dense>
              <q-card flat bordered class="q-mt-sm">
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Admin</q-item-label>
                      <q-item-label class="text-caption">
                        admin@example.com / admin123
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn
                        flat
                        dense
                        size="sm"
                        color="primary"
                        label="Use"
                        @click="useDemoAccount('admin@example.com', 'admin123')"
                      />
                    </q-item-section>
                  </q-item>
                  <q-separator />
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Manager</q-item-label>
                      <q-item-label class="text-caption">
                        manager@example.com / manager123
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn
                        flat
                        dense
                        size="sm"
                        color="primary"
                        label="Use"
                        @click="useDemoAccount('manager@example.com', 'manager123')"
                      />
                    </q-item-section>
                  </q-item>
                  <q-separator />
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Developer</q-item-label>
                      <q-item-label class="text-caption">
                        developer@example.com / dev123
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn
                        flat
                        dense
                        size="sm"
                        color="primary"
                        label="Use"
                        @click="useDemoAccount('developer@example.com', 'dev123')"
                      />
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </q-expansion-item>
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
const email = ref('');
const password = ref('');
const showPassword = ref(false);
const rememberMe = ref(false);

// Validation
function isValidEmail(val: string): boolean | string {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(val) || 'Invalid email format';
}

// Actions
async function handleLogin() {
  const success = await authStore.login({
    email: email.value,
    password: password.value,
    rememberMe: rememberMe.value,
  });

  if (success) {
    $q.notify({
      message: `Welcome back, ${authStore.userName}!`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });

    // Redirect to homepage or intended route
    const redirect = (router.currentRoute.value.query.redirect as string) || '/';
    router.push(redirect);
  }
}

function useDemoAccount(demoEmail: string, demoPassword: string) {
  email.value = demoEmail;
  password.value = demoPassword;
  rememberMe.value = true;
  handleLogin();
}
</script>

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
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
