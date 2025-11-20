<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-gradient-to-r from-primary to-secondary text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
          class="q-mr-sm"
        />

        <q-avatar size="32px" class="q-mr-sm">
          <q-icon name="trending_up" size="24px" />
        </q-avatar>

        <q-toolbar-title class="text-h6 text-weight-bold"> Darlana </q-toolbar-title>

        <q-space />

        <!-- User Menu -->
        <q-btn flat round>
          <q-avatar size="32px">
            <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" />
            <div v-else class="bg-white text-primary text-weight-bold">
              {{ authStore.userInitials }}
            </div>
          </q-avatar>
          <q-tooltip>{{ authStore.userName }}</q-tooltip>
          <q-menu>
            <q-list style="min-width: 250px">
              <!-- User Info -->
              <q-item>
                <q-item-section avatar>
                  <q-avatar>
                    <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" />
                    <div v-else class="bg-primary text-white">
                      {{ authStore.userInitials }}
                    </div>
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ authStore.userName }}</q-item-label>
                  <q-item-label caption>{{ authStore.user?.email }}</q-item-label>
                </q-item-section>
              </q-item>

              <q-separator />

              <!-- Profile -->
              <q-item clickable v-close-popup :to="'/profile'">
                <q-item-section avatar>
                  <q-icon name="person" />
                </q-item-section>
                <q-item-section>Profile</q-item-section>
              </q-item>

              <!-- Role Badge -->
              <q-item>
                <q-item-section avatar>
                  <q-icon name="badge" />
                </q-item-section>
                <q-item-section>
                  <q-chip
                    size="sm"
                    :color="
                      authStore.user?.role === 'admin'
                        ? 'red'
                        : authStore.user?.role === 'manager'
                          ? 'blue'
                          : 'green'
                    "
                    text-color="white"
                  >
                    {{ authStore.user?.role?.toUpperCase() }}
                  </q-chip>
                </q-item-section>
              </q-item>

              <q-separator />

              <!-- Logout -->
              <q-item clickable v-close-popup @click="handleLogout">
                <q-item-section avatar>
                  <q-icon name="logout" color="red" />
                </q-item-section>
                <q-item-section class="text-red">Logout</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="bg-grey-1" :width="280">
      <q-scroll-area class="fit">
        <q-list padding>
          <!-- Main Navigation -->
          <q-item-label header class="text-weight-bold text-primary text-uppercase">
            Main Navigation
          </q-item-label>

          <q-item
            v-for="item in mainNavigation"
            :key="item.title"
            clickable
            v-ripple
            :to="item.route"
            class="navigation-item q-mb-xs"
            active-class="bg-primary text-white"
          >
            <q-item-section avatar>
              <q-icon :name="item.icon" size="24px" />
            </q-item-section>

            <q-item-section>
              <q-item-label class="text-weight-medium">{{ item.title }}</q-item-label>
              <q-item-label caption v-if="item.caption">{{ item.caption }}</q-item-label>
            </q-item-section>

            <q-item-section side v-if="item.badge">
              <q-badge
                :color="
                  item.badge === 'New' ? 'green' : item.badge === 'Beta' ? 'orange' : 'primary'
                "
                :label="item.badge"
                rounded
              />
            </q-item-section>
          </q-item>

          <q-separator class="q-my-md" />

          <!-- Project Management (Manager/Admin only) -->
          <template v-if="authStore.isManager">
            <q-item-label header class="text-weight-bold text-primary text-uppercase">
              Project Management
            </q-item-label>

            <q-item
              v-for="item in projectNavigation"
              :key="item.title"
              clickable
              v-ripple
              :to="item.route"
              class="navigation-item q-mb-xs"
              active-class="bg-primary text-white"
            >
              <q-item-section avatar>
                <q-icon :name="item.icon" size="24px" />
              </q-item-section>

              <q-item-section>
                <q-item-label class="text-weight-medium">{{ item.title }}</q-item-label>
                <q-item-label caption v-if="item.caption">{{ item.caption }}</q-item-label>
              </q-item-section>

              <q-item-section side v-if="item.badge">
                <q-badge
                  :color="
                    item.badge === 'New' ? 'green' : item.badge === 'Beta' ? 'orange' : 'primary'
                  "
                  :label="item.badge"
                  rounded
                />
              </q-item-section>
            </q-item>

            <q-separator class="q-my-md" />
          </template>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container>
      <router-view />
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

interface NavigationItemProps {
  title: string;
  caption?: string;
  icon: string;
  route?: string;
  badge?: string | number;
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

const mainNavigation: NavigationItemProps[] = [
  {
    title: 'Dashboard',
    caption: 'Project overview',
    icon: 'dashboard',
    route: '/',
  },
  {
    title: 'Projects',
    caption: 'All projects',
    icon: 'folder',
    route: '/projects',
  },
  {
    title: 'Team',
    caption: 'Team members',
    icon: 'group',
    route: '/team',
  },
  {
    title: 'Workload',
    caption: 'Cross-project workload',
    icon: 'assessment',
    route: '/workload',
  },
];

const projectNavigation: NavigationItemProps[] = [
  {
    title: 'PERT Analysis',
    caption: 'Time estimates',
    icon: 'account_tree',
    route: '/pert-analysis',
  },
  {
    title: 'RACI Matrix',
    caption: 'Responsibility assignment',
    icon: 'assignment_ind',
    route: '/raci-matrix',
  },
  {
    title: 'PERT + RACI Integration',
    caption: 'Combined project analysis',
    icon: 'auto_awesome',
    route: '/pert-raci-optimization',
  },
  {
    title: 'Project Optimization',
    caption: 'Analysis with optimizations',
    icon: 'change_circle',
    route: '/requirement-changes',
  },
  {
    title: 'Smart Sprint Planning',
    caption: 'Sprint planning',
    icon: 'auto_awesome',
    route: '/smart-sprint-planning',
  },
];

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>

<style scoped>
.bg-gradient-to-r {
  background: linear-gradient(90deg, var(--q-primary) 0%, var(--q-secondary) 100%);
}

.navigation-item {
  border-radius: 8px;
  margin: 2px 8px;
}

.navigation-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}
</style>
