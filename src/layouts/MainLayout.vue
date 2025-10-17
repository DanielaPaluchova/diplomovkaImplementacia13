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

        <q-toolbar-title class="text-h6 text-weight-bold"> ProjectFlow AI </q-toolbar-title>

        <q-space />

        <!-- Search -->
        <q-input
          v-model="searchQuery"
          placeholder="Search projects, tasks..."
          dense
          standout="bg-white text-primary"
          class="q-mr-md"
          style="width: 300px"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>

        <!-- Notifications -->
        <q-btn flat round icon="notifications" class="q-mr-sm">
          <q-badge color="red" floating>3</q-badge>
          <q-tooltip>Notifications</q-tooltip>
        </q-btn>

        <!-- User Menu -->
        <q-btn flat round>
          <q-avatar size="32px">
            <img src="https://cdn.quasar.dev/img/avatar.png" />
          </q-avatar>
          <q-tooltip>Profile</q-tooltip>
          <q-menu>
            <q-list style="min-width: 200px">
              <q-item clickable v-close-popup>
                <q-item-section avatar>
                  <q-icon name="person" />
                </q-item-section>
                <q-item-section>Profile</q-item-section>
              </q-item>
              <q-item clickable v-close-popup>
                <q-item-section avatar>
                  <q-icon name="settings" />
                </q-item-section>
                <q-item-section>Settings</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup>
                <q-item-section avatar>
                  <q-icon name="logout" />
                </q-item-section>
                <q-item-section>Logout</q-item-section>
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

          <!-- Project Management -->
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

          <!-- Research & Analytics -->
          <q-item-label header class="text-weight-bold text-primary text-uppercase">
            Research & Analytics
          </q-item-label>

          <q-item
            v-for="item in researchNavigation"
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

interface NavigationItemProps {
  title: string;
  caption?: string;
  icon: string;
  route?: string;
  badge?: string | number;
}

const searchQuery = ref('');

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
    badge: 'New',
  },
];

const projectNavigation: NavigationItemProps[] = [
  {
    title: 'Sprint Planning',
    caption: 'Plan your sprints',
    icon: 'timeline',
    route: '/sprint-planning',
    badge: 'New',
  },
  {
    title: 'PERT Analysis',
    caption: 'Critical path analysis',
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
    caption: 'Combined optimization',
    icon: 'auto_awesome',
    route: '/pert-raci-optimization',
    badge: 'New',
  },
  {
    title: 'Kanban Board',
    caption: 'Visual task management',
    icon: 'view_column',
    route: '/kanban',
  },
  {
    title: 'Gantt Chart',
    caption: 'Timeline visualization',
    icon: 'view_timeline',
    route: '/gantt',
  },
];

const researchNavigation: NavigationItemProps[] = [
  {
    title: 'Experiments',
    caption: 'A/B testing',
    icon: 'science',
    route: '/experiments',
  },
  {
    title: 'Analytics',
    caption: 'Performance metrics',
    icon: 'analytics',
    route: '/analytics',
  },
  {
    title: 'Comparisons',
    caption: 'Method comparisons',
    icon: 'compare',
    route: '/comparisons',
  },
  {
    title: 'Reports',
    caption: 'Research reports',
    icon: 'assessment',
    route: '/reports',
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
