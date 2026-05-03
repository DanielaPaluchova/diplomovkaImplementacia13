<template>
  <q-page class="bg-grey-1">
    <!-- Header Section -->
    <div class="bg-primary text-white q-pa-lg shadow-1">
      <div class="row items-center q-gutter-md">
        <q-btn flat round icon="arrow_back" color="white" @click="navigateBack" />
        <div class="col">
          <div class="row items-center q-gutter-md">
            <q-avatar :icon="project.icon" size="64px" class="bg-white text-primary" />
            <div>
              <h4 class="text-h4 text-weight-bold q-ma-none">{{ project.name }}</h4>
              <p class="q-ma-none q-mt-sm">{{ project.description }}</p>
            </div>
          </div>
        </div>
        <div class="col-auto">
          <q-chip :color="getStatusColor(project.status)" text-color="white" size="lg">
            {{ project.status }}
          </q-chip>
        </div>
      </div>

      <!-- Project Stats -->
      <div class="row q-gutter-md q-mt-lg">
        <div class="col">
          <div class="text-caption">Progress</div>
          <div class="text-h6 text-weight-bold">{{ projectProgress }}%</div>
          <q-linear-progress :value="projectProgress / 100" color="white" class="q-mt-xs" />
        </div>
        <div class="col">
          <div class="text-caption">Tasks</div>
          <div class="text-h6 text-weight-bold">
            {{ projectTasksCompleted }}/{{ projectTotalTasks }}
          </div>
        </div>
        <div class="col">
          <div class="text-caption">Team Members</div>
          <div class="text-h6 text-weight-bold">{{ projectTeamMembers.length }}</div>
        </div>
        <div class="col">
          <div class="text-caption">Due Date</div>
          <div class="text-h6 text-weight-bold">{{ formatDate(project.dueDate) }}</div>
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Tabs -->
      <q-tabs
        v-model="activeTab"
        dense
        class="bg-white text-primary shadow-1 q-mb-lg"
        active-color="primary"
        indicator-color="primary"
        align="left"
      >
        <q-tab name="overview" icon="dashboard" label="Overview" />
        <q-tab name="kanban" icon="view_kanban" label="Kanban Board" />
        <q-tab name="backlog" icon="inbox" label="Backlog & Sprints" />
        <q-tab name="sprints" icon="event_note" label="Sprint Management" />
        <q-tab name="completed" icon="check_circle" label="Completed Tasks" />
        <q-tab name="epics" icon="star" label="Epic Planning" />
        <q-tab name="team" icon="group" label="Team" />
        <q-tab name="analytics" icon="analytics" label="Analytics" />
      </q-tabs>

      <!-- Tab Panels -->
      <q-tab-panels v-model="activeTab" animated>
        <!-- Overview Tab -->
        <q-tab-panel name="overview">
          <div class="row q-col-gutter-lg">
            <!-- Left Column - Project Info -->
            <div class="col-12 col-lg-8">
              <!-- Project Summary Cards -->
              <div class="overview-summary-grid q-mb-lg">
                <div>
                  <q-card class="overview-stat-card">
                    <q-card-section class="overview-stat-section">
                      <div class="text-caption text-grey-7">Progress</div>
                      <div class="text-h5 text-weight-bold text-primary">
                        {{ projectProgress }}%
                      </div>
                      <q-linear-progress
                        :value="projectProgress / 100"
                        color="primary"
                        class="q-mt-sm"
                      />
                    </q-card-section>
                  </q-card>
                </div>
                <div>
                  <q-card class="overview-stat-card">
                    <q-card-section class="overview-stat-section">
                      <div class="text-caption text-grey-7">Total Tasks</div>
                      <div class="text-h5 text-weight-bold text-blue">
                        {{ project.tasks?.length || 0 }}
                      </div>
                      <div class="text-caption text-grey-6 q-mt-xs">
                        {{ taskStats.done }} completed
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                <div>
                  <q-card class="overview-stat-card">
                    <q-card-section class="overview-stat-section">
                      <div class="text-caption text-grey-7">Story Points</div>
                      <div class="text-h5 text-weight-bold text-orange">
                        {{ project.totalStoryPoints }}
                      </div>
                      <div class="text-caption text-grey-6 q-mt-xs">Total capacity</div>
                    </q-card-section>
                  </q-card>
                </div>
                <div>
                  <q-card class="overview-stat-card">
                    <q-card-section class="overview-stat-section">
                      <div class="text-caption text-grey-7">Team Size</div>
                      <div class="text-h5 text-weight-bold text-green">
                        {{ projectTeamMembers.length }}
                      </div>
                      <div class="text-caption text-grey-6 q-mt-xs">Active members</div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>

              <!-- Active Sprint Info -->
              <q-card v-if="activeSprint" class="q-mb-lg">
                <q-card-section class="bg-green-1">
                  <div class="row items-center">
                    <q-icon name="play_circle" size="32px" class="text-green q-mr-md" />
                    <div class="col">
                      <div class="text-h6 text-weight-bold text-green">
                        Active Sprint: {{ activeSprint.name }}
                      </div>
                      <div class="text-caption text-grey-7">
                        {{ formatDate(activeSprint.startDate) }} -
                        {{ formatDate(activeSprint.endDate) }}
                      </div>
                    </div>
                  </div>
                </q-card-section>
                <q-card-section>
                  <div class="row q-col-gutter-md">
                    <div class="col-4">
                      <div class="text-caption text-grey-7">Total Tasks</div>
                      <div class="text-h6 text-primary">{{ activeSprintTotalTasks }}</div>
                    </div>
                    <div class="col-4">
                      <div class="text-caption text-grey-7">Completed</div>
                      <div class="text-h6 text-green">{{ activeSprintCompletedTasks }}</div>
                    </div>
                    <div class="col-4">
                      <div class="text-caption text-grey-7">Remaining</div>
                      <div class="text-h6 text-orange">
                        {{ activeSprintTotalTasks - activeSprintCompletedTasks }}
                      </div>
                    </div>
                  </div>
                  <q-linear-progress
                    :value="
                      activeSprintTotalTasks > 0
                        ? activeSprintCompletedTasks / activeSprintTotalTasks
                        : 0
                    "
                    color="green"
                    size="12px"
                    class="q-mt-md"
                  />
                </q-card-section>
              </q-card>

            </div>

            <!-- Right Column - Team Workload -->
            <div class="col-12 col-lg-4">
              <!-- Team Workload Analysis -->
              <q-card class="q-mb-lg">
                <q-card-section>
                  <div class="text-h6 text-weight-bold q-mb-md">Team Workload</div>
                  <div class="text-caption text-grey-7 q-mb-md">
                    Workload distribution across this and other projects
                  </div>

                  <div v-for="member in projectTeamMembers" :key="member.id" class="q-mb-lg">
                    <div class="row items-center q-mb-sm">
                      <q-avatar size="32px" class="q-mr-sm">
                        <img :src="member.avatar" />
                      </q-avatar>
                      <div class="col">
                        <div class="text-weight-medium">{{ member.name }}</div>
                        <div class="text-caption text-grey-7">{{ member.role }}</div>
                      </div>
                    </div>

                    <!-- This Project Workload -->
                    <div class="q-mb-xs">
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-grey-7">This Project</span>
                        <span class="text-caption text-weight-medium">
                          {{ getProjectWorkload(member.id) }}%
                        </span>
                      </div>
                      <q-linear-progress
                        :value="Math.min(1, getProjectWorkload(member.id) / 100)"
                        color="primary"
                        size="6px"
                      />
                    </div>

                    <!-- Other Projects Workload -->
                    <div class="q-mb-xs">
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-grey-7">Other Projects</span>
                        <span class="text-caption text-weight-medium">
                          {{ getOtherProjectsWorkload(member.id) }}%
                        </span>
                      </div>
                      <q-linear-progress
                        :value="Math.min(1, getOtherProjectsWorkload(member.id) / 100)"
                        color="orange"
                        size="6px"
                      />
                    </div>

                    <!-- Total Workload -->
                    <div>
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-weight-bold">Total Workload (All Projects)</span>
                        <span
                          class="text-caption text-weight-bold"
                          :class="{
                            'text-green': getTotalWorkload(member.id) <= 80,
                            'text-orange': getTotalWorkload(member.id) > 80 && getTotalWorkload(member.id) <= 100,
                            'text-red': getTotalWorkload(member.id) > 100,
                          }"
                        >
                          {{ getTotalWorkload(member.id) }}%
                        </span>
                      </div>
                      <q-linear-progress
                        :value="Math.min(1, getTotalWorkload(member.id) / 100)"
                        :color="
                          getTotalWorkload(member.id) > 100 ? 'red' : getTotalWorkload(member.id) > 80 ? 'orange' : 'green'
                        "
                        size="8px"
                      />
                    </div>

                    <q-separator
                      class="q-mt-md"
                      v-if="
                        projectTeamMembers.length > 0 &&
                        member.id !== projectTeamMembers[projectTeamMembers.length - 1]?.id
                      "
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- Project Info -->
              <q-card>
                <q-card-section>
                  <div class="text-h6 text-weight-bold q-mb-md">Project Details</div>
                  <div class="q-mb-sm">
                    <div class="text-caption text-grey-7">Created</div>
                    <div class="text-weight-medium">{{ formatDate(project.createdAt) }}</div>
                  </div>
                  <div class="q-mb-sm">
                    <div class="text-caption text-grey-7">Due Date</div>
                    <div class="text-weight-medium">{{ formatDate(project.dueDate) }}</div>
                  </div>
                  <div class="q-mb-sm">
                    <div class="text-caption text-grey-7">Template</div>
                    <div class="text-weight-medium">{{ project.template }}</div>
                  </div>
                  <div>
                    <div class="text-caption text-grey-7">Estimated Duration</div>
                    <div class="text-weight-medium">{{ project.estimatedDuration }} days</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-tab-panel>

        <!-- Kanban Board Tab -->
        <q-tab-panel name="kanban">
          <!-- Active Sprint Info -->
          <div v-if="activeSprint" class="q-mb-md">
            <q-banner class="bg-blue-1 text-blue-9">
              <template v-slot:avatar>
                <q-icon name="view_kanban" color="blue" />
              </template>
              <div class="text-weight-medium">Kanban Board: {{ activeSprint.name }}</div>
              <div class="text-caption">
                {{ formatDate(activeSprint.startDate) }} - {{ formatDate(activeSprint.endDate) }}
              </div>
            </q-banner>
          </div>

          <!-- No Active Sprint Message -->
          <div v-if="!activeSprint" class="text-center q-pa-xl">
            <q-icon name="event_busy" size="64px" class="text-grey-5 q-mb-md" />
            <div class="text-h6 text-grey-7 q-mb-sm">No Active Sprint</div>
            <div class="text-caption text-grey-6 q-mb-md">
              Start a sprint to use the Kanban board
            </div>
            <q-btn
              color="primary"
              icon="play_arrow"
              label="Go to Sprint Management"
              @click="activeTab = 'sprints'"
            />
          </div>

          <div v-if="activeSprint" class="row q-col-gutter-md kanban-container">
            <!-- To Do Column -->
            <div class="col-12 col-md-4">
              <q-card
                class="kanban-column"
                :class="{ 'drag-over': dragOverColumn === 'To Do' }"
                @dragover.prevent="onKanbanDragOver('To Do')"
                @dragleave="onKanbanDragLeave"
                @drop="onKanbanDrop('To Do')"
              >
                <q-card-section class="bg-grey-3">
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold">To Do</div>
                    <q-space />
                    <q-badge color="grey-7" :label="todoTasks.length" />
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-sm kanban-cards-area">
                  <div class="column q-gutter-sm">
                    <q-card
                      v-for="task in todoTasks"
                      :key="task.id"
                      class="kanban-card cursor-pointer"
                      draggable="true"
                      @dragstart="onKanbanDragStart(task)"
                      @dragend="onKanbanDragEnd"
                      @click="openEditTaskDialog(task)"
                    >
                      <q-card-section class="q-pa-sm">
                        <div class="row items-start justify-between q-mb-xs">
                          <div class="text-subtitle2 text-weight-medium">
                            {{ task.title }}
                          </div>
                          <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            size="xs"
                            color="negative"
                            @click.stop="confirmDeleteTask(task)"
                          >
                            <q-tooltip>Delete task</q-tooltip>
                          </q-btn>
                        </div>
                        <div class="text-caption text-grey-7 q-mb-sm">
                          {{ task.description }}
                        </div>
                        <div class="row items-center justify-between">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <div class="text-caption">{{ task.storyPoints }} SP</div>
                        </div>
                        <div
                          v-if="task.raci?.responsible && task.raci.responsible.length > 0"
                          class="row items-center q-mt-sm"
                        >
                          <q-avatar
                            v-for="memberId in task.raci.responsible.slice(0, 3)"
                            :key="memberId"
                            size="20px"
                            class="q-mr-xs"
                          >
                            <img :src="getResponsibleAvatar(memberId)" />
                            <q-tooltip>{{
                              teamStore.teamMembers.find((m) => m.id === memberId)?.name
                            }}</q-tooltip>
                          </q-avatar>
                          <span v-if="task.raci.responsible.length > 3" class="text-caption"
                            >+{{ task.raci.responsible.length - 3 }} more</span
                          >
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                  <div v-if="todoTasks.length === 0" class="text-center text-grey-5 q-pa-lg">
                    <div>No tasks</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- In Progress Column -->
            <div class="col-12 col-md-4">
              <q-card
                class="kanban-column"
                :class="{ 'drag-over': dragOverColumn === 'In Progress' }"
                @dragover.prevent="onKanbanDragOver('In Progress')"
                @dragleave="onKanbanDragLeave"
                @drop="onKanbanDrop('In Progress')"
              >
                <q-card-section class="bg-blue-1">
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold text-blue">In Progress</div>
                    <q-space />
                    <q-badge color="blue" text-color="white" :label="inProgressTasks.length" />
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-sm kanban-cards-area">
                  <div class="column q-gutter-sm">
                    <q-card
                      v-for="task in inProgressTasks"
                      :key="task.id"
                      class="kanban-card cursor-pointer"
                      draggable="true"
                      @dragstart="onKanbanDragStart(task)"
                      @dragend="onKanbanDragEnd"
                      @click="openEditTaskDialog(task)"
                    >
                      <q-card-section class="q-pa-sm">
                        <div class="row items-start justify-between q-mb-xs">
                          <div class="text-subtitle2 text-weight-medium">
                            {{ task.title }}
                          </div>
                          <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            size="xs"
                            color="negative"
                            @click.stop="confirmDeleteTask(task)"
                          >
                            <q-tooltip>Delete task</q-tooltip>
                          </q-btn>
                        </div>
                        <div class="text-caption text-grey-7 q-mb-sm">
                          {{ task.description }}
                        </div>
                        <div class="row items-center justify-between">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <div class="text-caption">{{ task.storyPoints }} SP</div>
                        </div>
                        <div
                          v-if="task.raci?.responsible && task.raci.responsible.length > 0"
                          class="row items-center q-mt-sm"
                        >
                          <q-avatar
                            v-for="memberId in task.raci.responsible.slice(0, 3)"
                            :key="memberId"
                            size="20px"
                            class="q-mr-xs"
                          >
                            <img :src="getResponsibleAvatar(memberId)" />
                            <q-tooltip>{{
                              teamStore.teamMembers.find((m) => m.id === memberId)?.name
                            }}</q-tooltip>
                          </q-avatar>
                          <span v-if="task.raci.responsible.length > 3" class="text-caption"
                            >+{{ task.raci.responsible.length - 3 }} more</span
                          >
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                  <div v-if="inProgressTasks.length === 0" class="text-center text-grey-5 q-pa-lg">
                    <div>No tasks</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Done Column -->
            <div class="col-12 col-md-4">
              <q-card
                class="kanban-column"
                :class="{ 'drag-over': dragOverColumn === 'Done' }"
                @dragover.prevent="onKanbanDragOver('Done')"
                @dragleave="onKanbanDragLeave"
                @drop="onKanbanDrop('Done')"
              >
                <q-card-section class="bg-green-1">
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold text-green">Done</div>
                    <q-space />
                    <q-badge color="green" text-color="white" :label="doneTasks.length" />
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-sm kanban-cards-area">
                  <div class="column q-gutter-sm">
                    <q-card
                      v-for="task in doneTasks"
                      :key="task.id"
                      class="kanban-card cursor-pointer"
                      draggable="true"
                      @dragstart="onKanbanDragStart(task)"
                      @dragend="onKanbanDragEnd"
                      @click="openEditTaskDialog(task)"
                    >
                      <q-card-section class="q-pa-sm">
                        <div class="text-subtitle2 text-weight-medium q-mb-xs text-strike">
                          {{ task.title }}
                        </div>
                        <div class="text-caption text-grey-7 q-mb-sm">
                          {{ task.description }}
                        </div>
                        <div class="row items-center justify-between">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <div class="text-caption">{{ task.storyPoints }} SP</div>
                        </div>
                        <div
                          v-if="task.raci?.responsible && task.raci.responsible.length > 0"
                          class="row items-center q-mt-sm"
                        >
                          <q-avatar
                            v-for="memberId in task.raci.responsible.slice(0, 3)"
                            :key="memberId"
                            size="20px"
                            class="q-mr-xs"
                          >
                            <img :src="getResponsibleAvatar(memberId)" />
                            <q-tooltip>{{
                              teamStore.teamMembers.find((m) => m.id === memberId)?.name
                            }}</q-tooltip>
                          </q-avatar>
                          <span v-if="task.raci.responsible.length > 3" class="text-caption"
                            >+{{ task.raci.responsible.length - 3 }} more</span
                          >
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                  <div v-if="doneTasks.length === 0" class="text-center text-grey-5 q-pa-lg">
                    <div>No tasks</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-tab-panel>

        <!-- Backlog & Sprint Planning Tab -->
        <q-tab-panel name="backlog">
          <!-- Header with Create Sprint Button -->
          <div class="row items-center q-mb-lg">
            <div class="text-h5 text-weight-bold">Sprint Backlog</div>
            <q-space />
            <q-btn
              color="primary"
              icon="add"
              label="Create Sprint"
              @click="openCreateSprintDialog"
            />
          </div>

          <!-- Product Backlog -->
          <q-card class="q-mb-lg">
            <q-card-section class="bg-grey-3 cursor-pointer" @click="backlogExpanded = !backlogExpanded">
              <div class="row items-center">
                <q-icon
                  :name="backlogExpanded ? 'expand_more' : 'chevron_right'"
                  size="sm"
                  class="q-mr-sm"
                />
                <div class="text-h6 text-weight-bold">Product Backlog</div>
                <q-space />
                <q-badge color="grey-7" :label="backlogTasks.length" />
                <q-btn
                  flat
                  color="primary"
                  icon="add"
                  label="New Task"
                  class="q-ml-sm"
                  @click.stop="showNewTaskDialog = true"
                />
              </div>
            </q-card-section>
            <q-separator v-if="backlogExpanded" />
            <q-slide-transition>
              <q-card-section
                v-if="backlogExpanded"
                class="q-pa-sm"
                style="max-height: 500px; overflow-y: auto"
              >
                <div class="column q-gutter-sm">
                  <q-card
                    v-for="task in backlogTasks"
                    :key="task.id"
                    class="task-card cursor-pointer"
                    draggable="true"
                    @dragstart="onDragStart(task)"
                    @dragend="onDragEnd"
                    @click="openEditTaskDialog(task)"
                    @contextmenu.prevent="showTaskContextMenu($event, task, 'backlog')"
                  >
                    <q-card-section class="q-pa-sm">
                      <div class="row items-start q-mb-xs">
                        <div class="col">
                          <div class="text-subtitle2 text-weight-medium">{{ task.title }}</div>
                        </div>
                        <div class="row q-gutter-xs">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            size="sm"
                            color="negative"
                            @click.stop="confirmDeleteTask(task)"
                          >
                            <q-tooltip>Delete task</q-tooltip>
                          </q-btn>
                        </div>
                      </div>
                      <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                      <div class="row items-center justify-between q-mb-xs">
                        <div class="row items-center q-gutter-xs">
                          <q-chip
                            v-for="label in task.labels"
                            :key="label"
                            size="sm"
                            dense
                            color="blue-1"
                            text-color="blue-9"
                          >
                            {{ label }}
                          </q-chip>
                        </div>
                        <div class="text-caption text-weight-medium">
                          {{ task.storyPoints }} SP
                        </div>
                      </div>
                      <div class="row items-center q-gutter-xs">
                        <q-icon name="person" size="16px" color="grey-6" />
                        <span class="text-caption text-grey-7">
                          {{ getResponsibleNames(task.raci?.responsible || []) }}
                        </span>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                <div v-if="backlogTasks.length === 0" class="text-center text-grey-5 q-pa-xl">
                  <q-icon name="inbox" size="64px" class="q-mb-md" />
                  <div>No tasks in backlog</div>
                </div>
              </q-card-section>
            </q-slide-transition>
          </q-card>

          <!-- Active Sprint -->
          <q-card
            v-if="activeSprint"
            class="q-mb-lg sprint-drop-zone"
            :class="{ 'drag-over': isDragOver && dragTarget === 'active' }"
            @dragover.prevent="onDragOver('active')"
            @dragleave="onDragLeave"
            @drop="onDrop(activeSprint.id)"
          >
            <q-card-section class="bg-green-1 cursor-pointer" @click="activeSprintExpanded = !activeSprintExpanded">
              <div class="row items-center">
                <q-icon
                  :name="activeSprintExpanded ? 'expand_more' : 'chevron_right'"
                  size="sm"
                  class="q-mr-sm"
                />
                <q-icon name="play_circle" size="24px" class="text-green q-mr-sm" />
                <div class="col">
                  <div class="text-h6 text-weight-bold text-green">{{ activeSprint.name }}</div>
                  <div class="text-caption text-grey-7">
                    {{ formatDate(activeSprint.startDate) }} - {{ formatDate(activeSprint.endDate) }}
                  </div>
                </div>
                <q-badge color="green" text-color="white" :label="sprintTasks.length" />
                <q-btn
                  flat
                  color="green"
                  icon="check_circle"
                  label="Complete"
                  class="q-ml-sm"
                  @click.stop="completeSprint(activeSprint)"
                />
              </div>
              <div v-if="activeSprintExpanded" class="q-mt-sm">
                <div class="row q-gutter-md text-caption">
                  <div>Total: {{ sprintTasks.length }} tasks</div>
                  <div>Completed: {{ completedSprintTasks }} tasks</div>
                  <div>Remaining: {{ remainingSprintTasks }} tasks</div>
                </div>
                <q-linear-progress
                  :value="sprintTasks.length > 0 ? completedSprintTasks / sprintTasks.length : 0"
                  color="green"
                  class="q-mt-sm"
                />
              </div>
            </q-card-section>
            <q-separator v-if="activeSprintExpanded" />
            <q-slide-transition>
              <q-card-section
                v-if="activeSprintExpanded"
                class="q-pa-sm"
                style="max-height: 500px; overflow-y: auto"
              >
                <div class="column q-gutter-sm">
                  <q-card
                    v-for="task in sprintTasks"
                    :key="task.id"
                    class="task-card cursor-pointer bg-blue-1"
                    @click="openEditTaskDialog(task)"
                    @contextmenu.prevent="showTaskContextMenu($event, task, 'sprint')"
                  >
                    <q-card-section class="q-pa-sm">
                      <div class="row items-start q-mb-xs">
                        <div class="col">
                          <div class="text-subtitle2 text-weight-medium">{{ task.title }}</div>
                        </div>
                        <div class="row q-gutter-xs">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <q-btn
                            flat
                            round
                            dense
                            icon="close"
                            size="sm"
                            color="grey-6"
                            @click.stop="removeFromSprint(task.id)"
                          >
                            <q-tooltip>Remove from sprint</q-tooltip>
                          </q-btn>
                          <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            size="sm"
                            color="negative"
                            @click.stop="confirmDeleteTask(task)"
                          >
                            <q-tooltip>Delete task</q-tooltip>
                          </q-btn>
                        </div>
                      </div>
                      <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                      <div class="row items-center justify-between q-mb-xs">
                        <div class="row items-center q-gutter-xs">
                          <q-chip
                            v-for="label in task.labels"
                            :key="label"
                            size="sm"
                            dense
                            color="blue-2"
                            text-color="blue-10"
                          >
                            {{ label }}
                          </q-chip>
                        </div>
                        <div class="row items-center q-gutter-sm">
                          <q-checkbox
                            :model-value="task.status === 'Done'"
                            @update:model-value="toggleTaskStatus(task)"
                            color="primary"
                            size="sm"
                          >
                            <q-tooltip>Mark as done</q-tooltip>
                          </q-checkbox>
                          <div class="text-caption text-weight-medium">
                            {{ task.storyPoints }} SP
                          </div>
                        </div>
                      </div>
                      <div class="row items-center q-gutter-xs">
                        <q-icon name="person" size="16px" color="grey-6" />
                        <span class="text-caption text-grey-7">
                          {{ getResponsibleNames(task.raci?.responsible || []) }}
                        </span>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                <div v-if="sprintTasks.length === 0" class="text-center text-grey-5 q-pa-md">
                  <q-icon name="timeline" size="48px" class="q-mb-sm" />
                  <div>Drag tasks here to add to sprint</div>
                </div>
              </q-card-section>
            </q-slide-transition>
          </q-card>

          <!-- Planned Sprints -->
          <q-card
            v-for="sprint in plannedSprints"
            :key="sprint.id"
            class="q-mb-lg sprint-drop-zone"
            :class="{ 'drag-over': isDragOver && dragTarget === sprint.id }"
            @dragover.prevent="onDragOver(sprint.id)"
            @dragleave="onDragLeave"
            @drop="onDrop(sprint.id)"
          >
            <q-card-section class="bg-blue-1 cursor-pointer" @click="togglePlannedSprint(sprint.id)">
              <div class="row items-center">
                <q-icon
                  :name="isPlannedSprintExpanded(sprint.id) ? 'expand_more' : 'chevron_right'"
                  size="sm"
                  class="q-mr-sm"
                />
                <q-icon name="schedule" size="24px" class="text-blue q-mr-sm" />
                <div class="col">
                  <div class="text-h6 text-weight-bold text-blue">{{ sprint.name }}</div>
                  <div class="text-caption text-grey-7">
                    {{ formatDate(sprint.startDate) }} - {{ formatDate(sprint.endDate) }}
                  </div>
                </div>
                <q-badge color="blue" text-color="white" :label="getSprintTasks(sprint.id).length" />
                <q-btn
                  flat
                  color="blue"
                  icon="play_arrow"
                  label="Start"
                  class="q-ml-sm"
                  @click.stop="startSprint(sprint)"
                />
                <q-btn
                  flat
                  color="grey-7"
                  icon="edit"
                  size="sm"
                  dense
                  class="q-ml-xs"
                  @click.stop="editSprint(sprint)"
                >
                  <q-tooltip>Edit Sprint</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  color="negative"
                  icon="delete"
                  size="sm"
                  dense
                  class="q-ml-xs"
                  @click.stop="confirmDeleteSprint(sprint)"
                >
                  <q-tooltip>Delete Sprint</q-tooltip>
                </q-btn>
              </div>
            </q-card-section>
            <q-separator v-if="isPlannedSprintExpanded(sprint.id)" />
            <q-slide-transition>
              <q-card-section
                v-if="isPlannedSprintExpanded(sprint.id)"
                class="q-pa-sm"
                style="max-height: 500px; overflow-y: auto"
              >
                <div class="column q-gutter-sm">
                  <q-card
                    v-for="task in getSprintTasks(sprint.id)"
                    :key="task.id"
                    class="task-card cursor-pointer bg-grey-2"
                    @click="openEditTaskDialog(task)"
                    @contextmenu.prevent="showTaskContextMenu($event, task, 'sprint')"
                  >
                    <q-card-section class="q-pa-sm">
                      <div class="row items-start q-mb-xs">
                        <div class="col">
                          <div class="text-subtitle2 text-weight-medium">{{ task.title }}</div>
                        </div>
                        <div class="row q-gutter-xs">
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                          <q-btn
                            flat
                            round
                            dense
                            icon="close"
                            size="sm"
                            color="grey-6"
                            @click.stop="removeFromSprint(task.id)"
                          >
                            <q-tooltip>Remove from sprint</q-tooltip>
                          </q-btn>
                          <q-btn
                            flat
                            round
                            dense
                            icon="delete"
                            size="sm"
                            color="negative"
                            @click.stop="confirmDeleteTask(task)"
                          >
                            <q-tooltip>Delete task</q-tooltip>
                          </q-btn>
                        </div>
                      </div>
                      <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                      <div class="row items-center justify-between q-mb-xs">
                        <div class="row items-center q-gutter-xs">
                          <q-chip
                            v-for="label in task.labels"
                            :key="label"
                            size="sm"
                            dense
                            color="blue-1"
                            text-color="blue-9"
                          >
                            {{ label }}
                          </q-chip>
                        </div>
                        <div class="text-caption text-weight-medium">
                          {{ task.storyPoints }} SP
                        </div>
                      </div>
                      <div class="row items-center q-gutter-xs">
                        <q-icon name="person" size="16px" color="grey-6" />
                        <span class="text-caption text-grey-7">
                          {{ getResponsibleNames(task.raci?.responsible || []) }}
                        </span>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                <div v-if="getSprintTasks(sprint.id).length === 0" class="text-center text-grey-5 q-pa-md">
                  <q-icon name="timeline" size="48px" class="q-mb-sm" />
                  <div>Drag tasks here to add to sprint</div>
                </div>
              </q-card-section>
            </q-slide-transition>
          </q-card>

          <!-- Empty State: No Sprints -->
          <q-card v-if="!activeSprint && plannedSprints.length === 0" class="text-center q-pa-xl">
            <q-icon name="event_note" size="64px" color="grey-5" class="q-mb-md" />
            <div class="text-h6 text-grey-7 q-mb-sm">No Sprints Yet</div>
            <div class="text-caption text-grey-6 q-mb-md">Create your first sprint to start planning</div>
            <q-btn
              color="primary"
              icon="add"
              label="Create Sprint"
              @click="openCreateSprintDialog"
            />
          </q-card>

          <!-- Context Menu -->
          <q-menu
            v-model="showContextMenu"
            touch-position
            context-menu
            :target="false"
            :offset="[contextMenuX, contextMenuY]"
          >
            <q-list dense style="min-width: 200px">
              <q-item
                v-if="contextMenuSource === 'backlog' && (activeSprint || plannedSprints.length > 0)"
                clickable
                v-close-popup
                @click="moveTaskToSprint"
              >
                <q-item-section avatar>
                  <q-icon name="arrow_forward" color="primary" />
                </q-item-section>
                <q-item-section>Move to Sprint</q-item-section>
              </q-item>
              <q-item
                v-if="contextMenuSource === 'sprint'"
                clickable
                v-close-popup
                @click="moveTaskToBacklog"
              >
                <q-item-section avatar>
                  <q-icon name="arrow_back" color="primary" />
                </q-item-section>
                <q-item-section>Move to Backlog</q-item-section>
              </q-item>
              <q-separator v-if="contextMenuTask" />
              <q-item
                v-if="contextMenuTask"
                clickable
                v-close-popup
                @click="openEditTaskDialog(contextMenuTask)"
              >
                <q-item-section avatar>
                  <q-icon name="edit" color="grey-7" />
                </q-item-section>
                <q-item-section>Edit Task</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-tab-panel>

        <!-- Sprint Management Tab -->
        <q-tab-panel name="sprints">
          <div class="row items-center q-mb-lg">
            <div class="text-h6 text-weight-bold">Sprint Management</div>
            <q-space />
            <q-btn
              color="primary"
              icon="add"
              label="New Sprint"
              @click="openCreateSprintDialog"
            />
          </div>

          <!-- Active Sprint -->
          <div v-if="activeSprint" class="q-mb-lg">
            <q-card class="active-sprint-card">
              <q-card-section class="bg-green-1">
                <div class="row items-center">
                  <q-icon name="play_circle" size="32px" class="text-green q-mr-md" />
                  <div class="col">
                    <div class="text-h6 text-weight-bold text-green">Active Sprint</div>
                    <div class="text-caption text-grey-7">Currently in progress</div>
                  </div>
                  <q-chip color="green" text-color="white" icon="event">
                    {{ formatDate(activeSprint.startDate) }} -
                    {{ formatDate(activeSprint.endDate) }}
                  </q-chip>
                </div>
              </q-card-section>
              <q-card-section>
                <div class="text-h6 text-weight-bold q-mb-sm">{{ activeSprint.name }}</div>
                <div class="text-body2 text-grey-7 q-mb-md">{{ activeSprint.goal }}</div>

                <div class="row q-gutter-md">
                  <div class="col">
                    <div class="text-caption text-grey-7">Completed Tasks</div>
                    <div class="text-h6 text-green">{{ activeSprintCompletedTasks }}</div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Remaining Tasks</div>
                    <div class="text-h6 text-orange">
                      {{ activeSprintTotalTasks - activeSprintCompletedTasks }}
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Total Tasks</div>
                    <div class="text-h6 text-primary">{{ activeSprintTotalTasks }}</div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Progress</div>
                    <div class="text-h6 text-blue">
                      {{
                        activeSprintTotalTasks > 0
                          ? Math.round((activeSprintCompletedTasks / activeSprintTotalTasks) * 100)
                          : 0
                      }}%
                    </div>
                  </div>
                </div>

                <q-linear-progress
                  :value="
                    activeSprintTotalTasks > 0
                      ? activeSprintCompletedTasks / activeSprintTotalTasks
                      : 0
                  "
                  color="green"
                  size="12px"
                  class="q-mt-md rounded-borders"
                />

                <div class="q-mt-md">
                  <q-btn
                    flat
                    color="primary"
                    icon="edit"
                    label="Edit"
                    @click="editSprint(activeSprint)"
                  />
                  <q-btn
                    flat
                    color="red"
                    icon="stop_circle"
                    label="Complete"
                    @click="completeSprint(activeSprint)"
                  />
                  <q-btn
                    flat
                    color="negative"
                    icon="delete"
                    label="Delete"
                    @click="confirmDeleteSprint(activeSprint)"
                  />
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Sprint List -->
          <div class="sprint-management-sections">
            <!-- Planned Sprints -->
            <div>
              <q-card>
                <q-card-section class="bg-blue-1">
                  <div class="text-h6 text-weight-bold text-blue">
                    <q-icon name="schedule" class="q-mr-sm" />
                    Planned Sprints
                  </div>
                </q-card-section>
                <q-separator />
                <q-list>
                  <q-item v-for="sprint in plannedSprints" :key="sprint.id">
                    <q-item-section>
                      <q-item-label class="text-weight-medium">{{ sprint.name }}</q-item-label>
                      <q-item-label caption>{{ sprint.goal }}</q-item-label>
                      <q-item-label caption class="q-mt-xs">
                        <q-icon name="event" size="xs" class="q-mr-xs" />
                        {{ formatDate(sprint.startDate) }} - {{ formatDate(sprint.endDate) }}
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <div class="row q-gutter-xs">
                        <q-btn flat icon="edit" size="sm" dense @click="editSprint(sprint)">
                          <q-tooltip>Edit</q-tooltip>
                        </q-btn>
                        <q-btn
                          flat
                          icon="play_arrow"
                          size="sm"
                          dense
                          color="green"
                          @click="startSprint(sprint)"
                        >
                          <q-tooltip>Start Sprint</q-tooltip>
                        </q-btn>
                        <q-btn
                          flat
                          icon="delete"
                          size="sm"
                          dense
                          color="red"
                          @click="confirmDeleteSprint(sprint)"
                        >
                          <q-tooltip>Delete Sprint</q-tooltip>
                        </q-btn>
                      </div>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="plannedSprints.length === 0">
                    <q-item-section class="text-center text-grey-6">
                      <div class="text-caption">No planned sprints</div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </div>

            <!-- Completed Sprints Report -->
            <div>
              <q-card>
                <q-card-section class="bg-grey-3">
                  <div class="row items-center">
                    <div class="col">
                      <div class="text-h6 text-weight-bold text-grey-8">
                        <q-icon name="assessment" class="q-mr-sm" />
                        Sprint Report – dokončené šprinty
                      </div>
                      <div class="text-caption text-grey-7 q-mt-xs">
                        Kliknúť na šprint pre rozbalenie detailov a taskov
                      </div>
                    </div>
                    <div v-if="completedSprints.length > 0" class="col-auto">
                      <div class="row q-gutter-md">
                        <q-card flat bordered class="bg-white">
                          <q-card-section class="q-pa-sm">
                            <div class="text-caption text-grey-7">Dokončených šprintov</div>
                            <div class="text-h6 text-weight-bold text-primary">
                              {{ completedSprints.length }}
                            </div>
                          </q-card-section>
                        </q-card>
                        <q-card flat bordered class="bg-white">
                          <q-card-section class="q-pa-sm">
                            <div class="text-caption text-grey-7">Celkom dokončených taskov</div>
                            <div class="text-h6 text-weight-bold text-green">
                              {{ completedSprintsReportTotalCompleted }}
                            </div>
                          </q-card-section>
                        </q-card>
                        <q-card flat bordered class="bg-white">
                          <q-card-section class="q-pa-sm">
                            <div class="text-caption text-grey-7">Celkom nedokončených</div>
                            <div class="text-h6 text-weight-bold text-orange">
                              {{ completedSprintsReportTotalIncomplete }}
                            </div>
                          </q-card-section>
                        </q-card>
                        <q-card flat bordered class="bg-white">
                          <q-card-section class="q-pa-sm">
                            <div class="text-caption text-grey-7">Priemerná úspešnosť</div>
                            <div class="text-h6 text-weight-bold text-blue">
                              {{ completedSprintsReportAvgRate }}%
                            </div>
                          </q-card-section>
                        </q-card>
                      </div>
                    </div>
                  </div>
                </q-card-section>
                <q-separator />
                <q-list v-if="completedSprints.length > 0">
                  <q-expansion-item
                    v-for="sprint in completedSprints"
                    :key="sprint.id"
                    expand-separator
                    header-class="text-weight-medium"
                    class="sprint-report-item"
                  >
                    <template v-slot:header>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">{{ sprint.name }}</q-item-label>
                        <q-item-label caption>{{ sprint.goal }}</q-item-label>
                        <q-item-label caption class="q-mt-xs">
                          <q-icon name="event" size="xs" class="q-mr-xs" />
                          {{ formatDate(sprint.startDate) }} – {{ formatDate(sprint.endDate) }}
                        </q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <div class="text-center">
                          <div class="text-caption text-weight-medium">
                            {{ sprint.completedTasks }}/{{ sprint.totalTasks }} dokončených
                          </div>
                          <q-linear-progress
                            :value="
                              sprint.totalTasks > 0 ? sprint.completedTasks / sprint.totalTasks : 0
                            "
                            :color="sprint.completedTasks === sprint.totalTasks ? 'green' : 'orange'"
                            size="6px"
                            class="q-mt-xs"
                            style="width: 100px"
                          />
                          <q-btn
                            flat
                            icon="delete"
                            size="sm"
                            dense
                            color="red"
                            class="q-mt-xs"
                            @click.stop="confirmDeleteSprint(sprint)"
                          >
                            <q-tooltip>Delete Sprint</q-tooltip>
                          </q-btn>
                        </div>
                      </q-item-section>
                    </template>
                    <q-card flat bordered class="q-ml-md q-mr-md q-mb-md bg-grey-1">
                      <q-card-section>
                        <div class="text-subtitle2 text-weight-medium q-mb-md">
                          Tasky v šprinte ({{ getTasksForSprint(sprint.id).length }} v šprinte)
                        </div>
                        <div class="text-caption text-grey-7 q-mb-md">
                          Dokončené tasky ostali v šprinte, nedokončené boli presunuté do backlogu
                        </div>
                        <q-list separator>
                          <q-expansion-item
                            v-for="task in getTasksForSprint(sprint.id)"
                            :key="task.id"
                            expand-separator
                            dense
                            class="rounded-borders bg-white q-mb-xs"
                          >
                            <template v-slot:header>
                              <q-item-section avatar>
                                <q-icon
                                  :name="task.status === 'Done' ? 'check_circle' : 'radio_button_unchecked'"
                                  :color="task.status === 'Done' ? 'positive' : 'grey'"
                                  size="24px"
                                />
                              </q-item-section>
                              <q-item-section>
                                <q-item-label>{{ task.title }}</q-item-label>
                                <q-item-label caption>
                                  <q-chip
                                    size="xs"
                                    dense
                                    :color="task.status === 'Done' ? 'positive' : 'grey'"
                                    text-color="white"
                                  >
                                    {{ task.status }}
                                  </q-chip>
                                  <q-chip size="xs" dense>{{ task.storyPoints }} SP</q-chip>
                                  <q-chip
                                    size="xs"
                                    dense
                                    :color="getPriorityColor(task.priority)"
                                    text-color="white"
                                  >
                                    {{ task.priority }}
                                  </q-chip>
                                </q-item-label>
                              </q-item-section>
                              <q-item-section side>
                                <q-btn
                                  flat
                                  icon="edit"
                                  size="sm"
                                  dense
                                  @click.stop="openEditTaskDialog(task)"
                                >
                                  <q-tooltip>Edit task</q-tooltip>
                                </q-btn>
                              </q-item-section>
                            </template>
                            <q-card flat bordered class="q-ml-md q-mr-md q-mb-md bg-white">
                              <q-card-section>
                                <div v-if="task.description" class="text-body2 q-mb-sm">
                                  {{ task.description }}
                                </div>
                                <div class="row q-gutter-sm">
                                  <q-chip size="sm" dense icon="functions">
                                    {{ task.storyPoints }} SP
                                  </q-chip>
                                  <q-chip
                                    size="sm"
                                    dense
                                    :color="getPriorityColor(task.priority)"
                                    text-color="white"
                                  >
                                    {{ task.priority }}
                                  </q-chip>
                                  <q-chip size="sm" dense>{{ task.type }}</q-chip>
                                  <div
                                    v-if="task.raci?.responsible && task.raci.responsible.length > 0"
                                    class="q-ml-sm"
                                  >
                                    <q-chip size="sm" dense icon="people">
                                      {{ getResponsibleNames(task.raci.responsible) }}
                                    </q-chip>
                                  </div>
                                </div>
                              </q-card-section>
                            </q-card>
                          </q-expansion-item>
                        </q-list>
                        <div
                          v-if="getTasksForSprint(sprint.id).length === 0"
                          class="text-center text-grey-6 q-pa-md"
                        >
                          Žiadne tasky v šprinte (všetky boli presunuté do backlogu pri dokončení)
                        </div>
                      </q-card-section>
                    </q-card>
                  </q-expansion-item>
                </q-list>
                <q-card-section v-else class="text-center text-grey-6">
                  <q-icon name="check_circle" size="48px" class="q-mb-sm" />
                  <div class="text-body1">Žiadne dokončené šprinty</div>
                  <div class="text-caption q-mt-xs">
                    Po dokončení aktívneho šprintu sa tu zobrazí report
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-tab-panel>

        <!-- Completed Tasks Tab -->
        <q-tab-panel name="completed">
          <div class="text-h6 text-weight-bold q-mb-lg">Completed Tasks</div>

          <q-card>
            <q-card-section>
              <div v-if="completedTasks.length === 0" class="text-center text-grey-7 q-pa-lg">
                <q-icon name="check_circle" size="64px" class="q-mb-md" />
                <div class="text-h6">No completed tasks yet</div>
                <div class="text-body2 q-mt-sm">
                  Completed tasks will appear here with their sprint information
                </div>
              </div>

              <q-list v-else separator>
                <q-item
                  v-for="task in completedTasks"
                  :key="task.id"
                  class="q-pa-md"
                  clickable
                  @click="openEditTaskDialog(task)"
                >
                  <q-item-section avatar>
                    <q-icon name="check_circle" color="positive" size="32px" />
                  </q-item-section>

                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ task.title }}</q-item-label>
                    <q-item-label caption class="q-mt-xs">
                      {{ task.description }}
                    </q-item-label>
                    <div class="row q-gutter-sm q-mt-sm">
                      <q-chip
                        size="sm"
                        dense
                        color="positive"
                        text-color="white"
                        icon="check_circle"
                      >
                        Done
                      </q-chip>
                      <q-chip
                        v-if="getSprintName(task.sprintId)"
                        size="sm"
                        dense
                        color="blue"
                        text-color="white"
                        icon="event_note"
                      >
                        {{ getSprintName(task.sprintId) }}
                      </q-chip>
                      <q-chip v-else size="sm" dense color="grey" text-color="white" icon="inbox">
                        Backlog
                      </q-chip>
                      <q-chip
                        :color="getPriorityColor(task.priority)"
                        text-color="white"
                        size="sm"
                        dense
                      >
                        {{ task.priority }}
                      </q-chip>
                      <q-chip size="sm" dense icon="functions"> {{ task.storyPoints }} SP </q-chip>
                      <q-chip
                        v-if="task.raci?.responsible && task.raci.responsible.length > 0"
                        size="sm"
                        dense
                        icon="people"
                      >
                        {{ getResponsibleNames(task.raci.responsible) }}
                      </q-chip>
                    </div>
                  </q-item-section>

                  <q-item-section side>
                    <div class="text-caption text-grey-7">Task ID: #{{ task.id }}</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card-section>
          </q-card>
        </q-tab-panel>

        <!-- Team Tab -->
        <q-tab-panel name="team">
          <div class="row items-center q-mb-lg">
            <div class="text-h6 text-weight-bold">Team Members & Roles</div>
            <q-space />
            <q-btn
              color="primary"
              icon="person_add"
              label="Add Member"
              @click="showAddMemberDialog = true"
            />
          </div>

          <div class="project-team-grid">
            <div
              v-for="member in projectTeamMembers"
              :key="member.id"
            >
              <q-card class="project-team-card">
                <q-card-section class="text-center project-team-card-content">
                  <q-avatar size="80px" class="q-mb-md">
                    <img :src="member.avatar" />
                  </q-avatar>
                  <div class="text-h6 text-weight-bold">{{ member.name }}</div>
                  <div class="text-caption text-grey-7 q-mb-sm">{{ member.role }}</div>

                  <!-- Project Role -->
                  <q-chip
                    :color="getRoleColor(getMemberProjectRole(member.id))"
                    text-color="white"
                    icon="badge"
                    class="q-mb-md"
                  >
                    {{ getMemberProjectRole(member.id).toUpperCase() }}
                  </q-chip>

                  <div class="text-left">
                    <div class="text-caption text-grey-7 q-mb-xs">
                      Total Workload (All Active Sprints)
                    </div>
                    <q-linear-progress
                      :value="Math.min(1, member.workload / 100)"
                      :color="
                        member.workload > 80 ? 'red' : member.workload > 60 ? 'orange' : 'green'
                      "
                      class="q-mb-xs"
                    />
                    <div class="text-caption text-right q-mb-sm">
                      {{ member.workload }}%
                      <span class="text-grey-6">
                        ({{ member.totalStoryPoints || 0 }}/{{ member.maxStoryPoints || 20 }} SP)
                      </span>
                    </div>
                    
                    <!-- Breakdown -->
                    <div class="q-mt-sm q-pt-sm" style="border-top: 1px solid #e0e0e0">
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-grey-7">This Project:</span>
                        <span class="text-caption text-weight-medium text-primary">
                          {{ member.thisProjectStoryPoints || 0 }} SP
                        </span>
                      </div>
                      <div class="row items-center justify-between">
                        <span class="text-caption text-grey-7">Other Projects:</span>
                        <span class="text-caption text-weight-medium text-orange">
                          {{ (member.totalStoryPoints || 0) - (member.thisProjectStoryPoints || 0) }} SP
                        </span>
                      </div>
                    </div>
                  </div>
                </q-card-section>

                <q-separator />

                <q-card-actions>
                  <q-btn
                    flat
                    color="primary"
                    icon="edit"
                    label="Change Role"
                    @click="changeMemberRole(member)"
                  />
                  <q-space />
                  <q-btn flat icon="remove_circle" color="red" dense @click="removeMember(member)">
                    <q-tooltip>Remove from Project</q-tooltip>
                  </q-btn>
                </q-card-actions>
              </q-card>
            </div>
          </div>
        </q-tab-panel>

        <!-- Epic Planning Tab -->
        <q-tab-panel name="epics">
          <EpicManagementTab :project-id="projectId" />
        </q-tab-panel>

        <!-- Analytics Tab -->
        <q-tab-panel name="analytics">
          <div class="analytics-sections">
            <!-- Velocity Chart -->
            <q-card>
              <q-card-section>
                <div class="text-h6 text-weight-bold q-mb-md">
                  <q-icon name="trending_up" class="q-mr-sm" />
                  Velocity Chart
                </div>
                <p class="text-caption text-grey-7 q-mb-md">
                  Story points completed per sprint. Use this to predict team capacity for future sprints.
                </p>
                <div v-if="velocityChartData.labels.length > 0" style="height: 280px">
                  <Bar :data="velocityChartData" :options="velocityChartOptions" />
                </div>
                <div v-else class="text-center text-grey-6 q-pa-xl">
                  <q-icon name="bar_chart" size="48px" class="q-mb-sm" />
                  <div class="text-body2">No completed sprints yet</div>
                  <div class="text-caption">Complete sprints to see velocity data</div>
                </div>
              </q-card-section>
            </q-card>

            <!-- Charts and analytics -->
            <div class="analytics-cards-grid">
              <div>
                <q-card class="analytics-stat-card">
                  <q-card-section>
                    <div class="text-h6 text-weight-bold q-mb-md">Task Distribution</div>
                    <div class="row q-gutter-md">
                      <div class="col">
                        <div class="text-h4 text-primary text-weight-bold">{{ taskStats.todo }}</div>
                        <div class="text-caption text-grey-7">To Do</div>
                      </div>
                      <div class="col">
                        <div class="text-h4 text-orange text-weight-bold">
                          {{ taskStats.inProgress }}
                        </div>
                        <div class="text-caption text-grey-7">In Progress</div>
                      </div>
                      <div class="col">
                        <div class="text-h4 text-green text-weight-bold">{{ taskStats.done }}</div>
                        <div class="text-caption text-grey-7">Done</div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <div>
                <q-card class="analytics-stat-card">
                  <q-card-section>
                    <div class="text-h6 text-weight-bold q-mb-md">Priority Breakdown</div>
                    <div class="row q-gutter-md">
                      <div class="col">
                        <div class="text-h4 text-red text-weight-bold">{{ priorityStats.high }}</div>
                        <div class="text-caption text-grey-7">High</div>
                      </div>
                      <div class="col">
                        <div class="text-h4 text-orange text-weight-bold">
                          {{ priorityStats.medium }}
                        </div>
                        <div class="text-caption text-grey-7">Medium</div>
                      </div>
                      <div class="col">
                        <div class="text-h4 text-blue text-weight-bold">{{ priorityStats.low }}</div>
                        <div class="text-caption text-grey-7">Low</div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- New Task Dialog -->
    <q-dialog v-model="showNewTaskDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Create New Task</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input v-model="newTask.title" label="Task Title" filled class="q-mb-md" />
          <q-input
            v-model="newTask.description"
            label="Description"
            type="textarea"
            filled
            class="q-mb-md"
          />
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="newTask.priority"
                :options="['high', 'medium', 'low']"
                label="Priority"
                filled
              />
            </div>
            <div class="col">
              <q-select
                v-model="newTask.type"
                :options="['feature', 'bug', 'task']"
                label="Type"
                filled
              />
            </div>
          </div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="newTask.storyPoints"
                label="Story Points"
                type="number"
                filled
              />
            </div>
          </div>
          <q-select
            v-model="newTask.labels"
            :options="['frontend', 'backend', 'api', 'ui', 'database', 'mobile', 'security']"
            label="Labels"
            filled
            multiple
            use-chips
            class="q-mb-md"
          />

          <q-select
            v-model="newTask.epicId"
            :options="epicOptions"
            label="Epic (Optional)"
            filled
            clearable
            emit-value
            map-options
            class="q-mb-md"
            hint="Assign this task to an epic"
          >
            <template v-slot:prepend>
              <q-icon name="flag" />
            </template>
          </q-select>

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="newTask.requiredSkills"
                :options="availableSkillsForTasks"
                label="Required Skills"
                filled
                multiple
                use-chips
                use-input
                hint="Skills from your team members"
              />
            </div>
          </div>

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">Time Tracking</div>
          <q-input
            v-model.number="newTask.actualHours"
            label="Actual Hours"
            type="number"
            filled
            min="0"
            hint="How long the task actually took (hours)"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="schedule" />
            </template>
          </q-input>

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model="newTask.dueDate"
                label="Due Date"
                type="date"
                filled
                hint="Task deadline (optional)"
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>
          </div>

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">PERT Estimates (hours)</div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="newTask.pert.optimistic"
                label="Optimistic"
                type="number"
                filled
                hint="Best case scenario (hours)"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="newTask.pert.mostLikely"
                label="Most Likely"
                type="number"
                filled
                hint="Expected time (hours)"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="newTask.pert.pessimistic"
                label="Pessimistic"
                type="number"
                filled
                hint="Worst case scenario (hours)"
              />
            </div>
          </div>

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">RACI Matrix</div>
          <q-select
            v-model="newTask.raci.responsible"
            :options="teamMembersOptions"
            label="Responsible (who does the work)"
            filled
            multiple
            use-chips
            emit-value
            map-options
            class="q-mb-md"
          />
          <q-select
            v-model="newTask.raci.accountable"
            :options="teamMembersOptions"
            label="Accountable (who approves)"
            filled
            clearable
            emit-value
            map-options
            class="q-mb-md"
          />
          <q-select
            v-model="newTask.raci.consulted"
            :options="teamMembersOptions"
            label="Consulted (who provides input)"
            filled
            multiple
            use-chips
            emit-value
            map-options
            class="q-mb-md"
          />
          <q-select
            v-model="newTask.raci.informed"
            :options="teamMembersOptions"
            label="Informed (who is kept updated)"
            filled
            multiple
            use-chips
            emit-value
            map-options
            class="q-mb-md"
          />

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">Task Dependencies</div>
          <q-select
            v-model="newTask.dependencies"
            :options="availableTasksForDependencies"
            label="Tasks that must be completed first"
            filled
            multiple
            use-chips
            emit-value
            map-options
            hint="Select tasks that need to be finished before this task can start"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption
                    >{{ scope.opt.status }} - {{ scope.opt.storyPoints }} SP</q-item-label
                  >
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup @click="cancelNewTask" />
          <q-btn color="primary" label="Create" @click="createTask" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Edit Task Dialog -->
    <q-dialog v-model="showEditTaskDialog">
      <q-card style="min-width: 500px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Edit Task</div>
        </q-card-section>

        <q-card-section class="q-pt-md">
          <q-input v-model="editTask.title" label="Task Title" filled class="q-mb-md" />
          <q-input
            v-model="editTask.description"
            label="Description"
            type="textarea"
            filled
            class="q-mb-md"
          />
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="editTask.priority"
                :options="['high', 'medium', 'low']"
                label="Priority"
                filled
              />
            </div>
            <div class="col">
              <q-select
                v-model="editTask.type"
                :options="['feature', 'bug', 'task']"
                label="Type"
                filled
              />
            </div>
          </div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="editTask.status"
                :options="['To Do', 'In Progress', 'Done']"
                label="Status"
                filled
              />
            </div>
          </div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="editTask.storyPoints"
                label="Story Points"
                type="number"
                filled
              />
            </div>
          </div>
          <q-select
            v-model="editTask.labels"
            :options="['frontend', 'backend', 'api', 'ui', 'database', 'mobile', 'security']"
            label="Labels"
            filled
            multiple
            use-chips
            class="q-mb-md"
          />

          <q-select
            v-model="editTask.epicId"
            :options="epicOptions"
            label="Epic (Optional)"
            filled
            clearable
            emit-value
            map-options
            class="q-mb-md"
            hint="Assign this task to an epic"
          >
            <template v-slot:prepend>
              <q-icon name="flag" />
            </template>
          </q-select>

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="editTask.requiredSkills"
                :options="availableSkillsForTasks"
                label="Required Skills"
                filled
                multiple
                use-chips
                use-input
                hint="Skills from your team members"
              />
            </div>
          </div>

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">Time Tracking</div>
          <q-input
            v-model.number="editTask.actualHours"
            label="Actual Hours"
            type="number"
            filled
            min="0"
            hint="How long the task actually took (hours)"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="schedule" />
            </template>
          </q-input>

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model="editTask.dueDate"
                label="Due Date"
                type="date"
                filled
                hint="Task deadline (optional)"
              >
                <template v-slot:prepend>
                  <q-icon name="event" />
                </template>
              </q-input>
            </div>
          </div>

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">PERT Estimates (hours)</div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="editTask.pert.optimistic"
                label="Optimistic"
                type="number"
                filled
                hint="Best case scenario (hours)"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="editTask.pert.mostLikely"
                label="Most Likely"
                type="number"
                filled
                hint="Expected time (hours)"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="editTask.pert.pessimistic"
                label="Pessimistic"
                type="number"
                filled
                hint="Worst case scenario (hours)"
              />
            </div>
          </div>

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">RACI Matrix</div>
          <q-select
            v-model="editTask.raci.responsible"
            :options="teamMembersOptions"
            label="Responsible (who does the work)"
            filled
            multiple
            use-chips
            emit-value
            map-options
            class="q-mb-md"
          />
          <q-select
            v-model="editTask.raci.accountable"
            :options="teamMembersOptions"
            label="Accountable (who approves)"
            filled
            clearable
            emit-value
            map-options
            class="q-mb-md"
          />
          <q-select
            v-model="editTask.raci.consulted"
            :options="teamMembersOptions"
            label="Consulted (who provides input)"
            filled
            multiple
            use-chips
            emit-value
            map-options
            class="q-mb-md"
          />
          <q-select
            v-model="editTask.raci.informed"
            :options="teamMembersOptions"
            label="Informed (who is kept updated)"
            filled
            multiple
            use-chips
            emit-value
            map-options
            class="q-mb-md"
          />

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">Task Dependencies</div>
          <q-select
            v-model="editTask.dependencies"
            :options="availableTasksForEditDependencies"
            label="Tasks that must be completed first"
            filled
            multiple
            use-chips
            emit-value
            map-options
            hint="Select tasks that need to be finished before this task can start"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption
                    >{{ scope.opt.status }} - {{ scope.opt.storyPoints }} SP</q-item-label
                  >
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup @click="cancelEditTask" />
          <q-btn color="primary" label="Save" @click="saveEditTask" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Sprint Planning Dialog -->
    <q-dialog v-model="showNewSprintDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h5 text-weight-bold">
            <q-icon name="event_note" size="sm" class="q-mr-sm" />
            {{ editingSprintId ? 'Edit Sprint' : 'Create New Sprint' }}
          </div>
        </q-card-section>

        <q-card-section>
          <q-input v-model="sprintForm.name" label="Sprint Name *" filled class="q-mb-md" />
          <q-input v-model="sprintForm.goal" label="Sprint Goal" filled class="q-mb-md" />

          <div class="row q-gutter-md">
            <div class="col">
              <q-input v-model="sprintForm.startDate" label="Start Date *" type="date" filled />
            </div>
            <div class="col">
              <q-input v-model="sprintForm.endDate" label="End Date *" type="date" filled />
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" v-close-popup @click="cancelSprintDialog" />
          <q-btn
            color="primary"
            :icon="editingSprintId ? 'save' : 'add'"
            :label="editingSprintId ? 'Save Changes' : 'Create Sprint'"
            @click="createSprint"
            :disable="!isSprintFormValid"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add Member Dialog -->
    <q-dialog v-model="showAddMemberDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Add Team Member to Project</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-select
            v-model="selectedMemberToAdd"
            :options="availableMembersToAdd"
            option-value="id"
            option-label="name"
            label="Select Team Member"
            filled
            class="q-mb-md"
          >
            <template #option="scope">
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
          </q-select>

          <q-select
            v-model="newMemberRole"
            :options="['owner', 'admin', 'developer', 'viewer']"
            label="Project Role"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup @click="cancelAddMember" />
          <q-btn
            color="primary"
            label="Add Member"
            @click="addMemberToProject"
            :disable="!selectedMemberToAdd"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Change Role Dialog -->
    <q-dialog v-model="showChangeRoleDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Change Project Role</div>
        </q-card-section>

        <q-card-section class="q-pt-none" v-if="memberToChangeRole">
          <div class="row items-center q-mb-md">
            <q-avatar size="48px" class="q-mr-md">
              <img :src="memberToChangeRole.avatar" />
            </q-avatar>
            <div>
              <div class="text-subtitle1 text-weight-bold">{{ memberToChangeRole.name }}</div>
              <div class="text-caption text-grey-7">{{ memberToChangeRole.role }}</div>
            </div>
          </div>

          <q-select
            v-model="selectedRole"
            :options="['owner', 'admin', 'developer', 'viewer']"
            label="New Project Role"
            filled
          >
            <template #prepend>
              <q-icon name="badge" />
            </template>
          </q-select>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup @click="cancelChangeRole" />
          <q-btn color="primary" label="Save Changes" @click="saveRoleChange" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { format } from 'date-fns';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useProjectStore, type Task, type Project, type Sprint } from 'src/stores/project-store';
import { useTeamStore, type TeamMember } from 'src/stores/team-store';
import { useEpicStore } from 'src/stores/epic-store';
import EpicManagementTab from 'src/components/EpicManagementTab.vue';
import type { AxiosError } from 'axios';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const router = useRouter();
const route = useRoute();
const $q = useQuasar();
const projectStore = useProjectStore();
const teamStore = useTeamStore();
const epicStore = useEpicStore();

// Helper function to extract error messages from server responses
function getErrorMessage(error: unknown, defaultMessage: string): string {
  // Type guard to check if error is an AxiosError
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const axiosError = error as AxiosError<{ error?: string; message?: string }>;
    if (axiosError.response?.data?.error) {
      return axiosError.response.data.error;
    } else if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
  }
  
  // Check if error has a message property
  if (error instanceof Error) {
    return error.message;
  }
  
  return defaultMessage;
}

// Fetch data from API
onMounted(async () => {
  // Fetch all projects with full details (tasks, sprints, etc.) for workload calculation
  await Promise.all([projectStore.fetchProjects(true), teamStore.fetchTeamMembers()]);
  // Load specific project if ID is in route
  if (route.params.id) {
    const id = parseInt(route.params.id as string);
    await Promise.all([projectStore.getProject(id), epicStore.fetchEpics(id, false)]);
  }
});

// Watch for route changes to reload project data
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      const id = parseInt(newId as string);
      await projectStore.getProject(id);
    }
  },
);

const activeTab = ref('overview');
const showNewTaskDialog = ref(false);
const showEditTaskDialog = ref(false);
const showNewSprintDialog = ref(false);
const editingSprintId = ref<number | null>(null);
const showAddMemberDialog = ref(false);
const selectedMemberToAdd = ref<TeamMember | null>(null);
const newMemberRole = ref('developer');
const showChangeRoleDialog = ref(false);
const memberToChangeRole = ref<TeamMember | null>(null);
const selectedRole = ref('developer');

// Drag and drop state
const isDragOver = ref(false);
const draggedTask = ref<Task | null>(null);
const dragTarget = ref<number | string | null>(null); // 'active' or sprint ID

// Expand/collapse state for sprints
const backlogExpanded = ref(true);
const activeSprintExpanded = ref(true);
const expandedPlannedSprints = ref<Set<number>>(new Set());

// Context menu state
const showContextMenu = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuTask = ref<Task | null>(null);
const contextMenuSource = ref<'backlog' | 'sprint'>('backlog');

// Kanban drag and drop state
const dragOverColumn = ref<string | null>(null);
const kanbanDraggedTask = ref<Task | null>(null);

// Get project from store
const projectId = computed(() => Number(route.params.id));
const project = computed(() => {
  const p = projectStore.getProjectById(projectId.value);
  if (!p) {
    // Return default project if not found
    return {
      id: projectId.value,
      name: 'Project Not Found',
      description: '',
      icon: 'folder',
      status: 'In Progress',
      progress: 0,
      tasksCompleted: 0,
      totalTasks: 0,
      dueDate: new Date(),
      createdAt: new Date(),
      template: '',
      totalStoryPoints: 0,
      estimatedDuration: 0,
      teamMemberIds: [],
      roles: [],
      sprints: [],
      tasks: [],
    } as Project;
  }
  
  // Filter out Split tasks (they should not be displayed in normal views)
  return {
    ...p,
    tasks: projectStore.filterActiveTasks(p.tasks || []),
  };
});

// Get team members for this project from team store with calculated workload
const projectTeamMembers = computed(() => {
  return teamStore.teamMembers
    .filter((member) => project.value.teamMemberIds?.includes(member.id))
    .map((member) => {
      const maxStoryPoints = member.maxStoryPoints || 20;
      
      // Calculate TOTAL workload across ALL projects (all active sprints)
      // This matches WorkloadDashboardPage logic
      let totalStoryPoints = 0;
      let thisProjectStoryPoints = 0;

      // Iterate through all projects where member is assigned
      projectStore.projects.forEach((proj) => {
        if (proj.teamMemberIds && proj.teamMemberIds.includes(member.id)) {
          // Get active sprint for this project
          const activeSprint = projectStore.getActiveSprint(proj.id);
          
          // Calculate story points for CURRENT SPRINT only
          let sprintStoryPoints = 0;
          if (proj.tasks && activeSprint) {
            const sprintTasks = proj.tasks.filter((task) => {
              const isInSprint = task.sprintId === activeSprint.id;
              const isAssigned = task.raci?.responsible && task.raci.responsible.includes(member.id);
              return isInSprint && isAssigned;
            });
            sprintStoryPoints = sprintTasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
          }

          totalStoryPoints += sprintStoryPoints;

          // Track story points from THIS project
          if (proj.id === project.value.id) {
            thisProjectStoryPoints = sprintStoryPoints;
          }
        }
      });

      const workload = maxStoryPoints > 0 ? Math.round((totalStoryPoints / maxStoryPoints) * 100) : 0;

      return {
        ...member,
        workload, // Total workload across all projects
        totalStoryPoints, // Total SP across all active sprints
        thisProjectStoryPoints, // SP from this project only
      };
    });
});

// Get tasks from project
const backlogTasks = computed(() => {
  if (!project.value || !project.value.tasks) return [];
  return project.value.tasks.filter(
    (task) => task.projectId === project.value.id && task.sprintId === null,
  );
});

const sprintTasks = computed(() => {
  if (!activeSprint.value || !project.value || !project.value.tasks) return [];
  return project.value.tasks.filter(
    (task) => task.projectId === project.value.id && task.sprintId === activeSprint.value!.id,
  );
});

const remainingSprintTasks = computed(() => {
  return sprintTasks.value.length - completedSprintTasks.value;
});

// Sprint management
const activeSprint = computed(() => project.value.sprints?.find((s) => s.status === 'active'));
const plannedSprints = computed(
  () => project.value.sprints?.filter((s) => s.status === 'planned') || [],
);
const completedSprints = computed(
  () => project.value.sprints?.filter((s) => s.status === 'completed') || [],
);

// Sprint report – tasks in a sprint (for completed sprints: only completed tasks remain)
function getTasksForSprint(sprintId: number) {
  if (!project.value?.tasks) return [];
  return project.value.tasks.filter(
    (t) => t.projectId === project.value.id && t.sprintId === sprintId,
  );
}

// Sprint report summary
const completedSprintsReportTotalCompleted = computed(() =>
  completedSprints.value.reduce((sum, s) => sum + s.completedTasks, 0),
);
const completedSprintsReportTotalIncomplete = computed(() =>
  completedSprints.value.reduce((sum, s) => sum + (s.totalTasks - s.completedTasks), 0),
);
const completedSprintsReportAvgRate = computed(() => {
  const total = completedSprints.value.reduce((sum, s) => sum + s.totalTasks, 0);
  const completed = completedSprintsReportTotalCompleted.value;
  return total > 0 ? Math.round((completed / total) * 100) : 0;
});

// Task stats - filter by current project ID
const taskStats = computed(() => {
  if (!project.value || !project.value.tasks) return { todo: 0, inProgress: 0, done: 0 };
  const projectTasks = project.value.tasks.filter((t) => t.projectId === project.value.id);
  return {
    todo: projectTasks.filter((t) => t.status === 'To Do').length,
    inProgress: projectTasks.filter((t) => t.status === 'In Progress').length,
    done: projectTasks.filter((t) => t.status === 'Done').length,
  };
});

const priorityStats = computed(() => {
  if (!project.value || !project.value.tasks) return { high: 0, medium: 0, low: 0 };
  const projectTasks = project.value.tasks.filter((t) => t.projectId === project.value.id);
  return {
    high: projectTasks.filter((t) => t.priority.toLowerCase() === 'high').length,
    medium: projectTasks.filter((t) => t.priority.toLowerCase() === 'medium').length,
    low: projectTasks.filter((t) => t.priority.toLowerCase() === 'low').length,
  };
});

// Velocity chart data: completed story points per sprint (completed sprints only)
const velocityChartData = computed(() => {
  const sprints = completedSprints.value;
  if (!sprints.length || !project.value?.tasks) {
    return {
      labels: [] as string[],
      datasets: [
        {
          label: 'Completed Story Points',
          data: [] as number[],
          backgroundColor: 'rgba(25, 118, 210, 0.7)',
          borderColor: 'rgb(25, 118, 210)',
          borderWidth: 1,
        },
      ],
    };
  }
  const sorted = [...sprints].sort((a, b) => {
    const dateA = new Date(a.endDate).getTime();
    const dateB = new Date(b.endDate).getTime();
    return dateA - dateB;
  });
  const labels = sorted.map((s) => s.name);
  const completedSP = sorted.map((sprint) => {
    const sprintTasks = getTasksForSprint(sprint.id);
    return sprintTasks
      .filter((t) => t.status === 'Done' || t.completed)
      .reduce((sum, t) => sum + (t.storyPoints || 0), 0);
  });
  return {
    labels,
    datasets: [
      {
        label: 'Completed Story Points',
        data: completedSP,
        backgroundColor: 'rgba(25, 118, 210, 0.7)',
        borderColor: 'rgb(25, 118, 210)',
        borderWidth: 1,
      },
    ],
  };
});

const velocityChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
      title: { display: true, text: 'Story Points' },
    },
    x: {
      title: { display: true, text: 'Sprint' },
    },
  },
};

const completedSprintTasks = computed(() => {
  if (!activeSprint.value) return 0;
  return sprintTasks.value.filter((t) => t.completed).length;
});

// Dynamic project-level calculations
const projectProgress = computed(() => {
  const tasks = project.value.tasks || [];
  const totalTasks = tasks.length;
  if (totalTasks === 0) return 0;
  const completedTasks = tasks.filter((t) => t.status === 'Done').length;
  return Math.round((completedTasks / totalTasks) * 100);
});

const projectTotalTasks = computed(() => {
  return (project.value.tasks || []).length;
});

const projectTasksCompleted = computed(() => {
  return (project.value.tasks || []).filter((t) => t.status === 'Done').length;
});

// Dynamic sprint task calculations
const activeSprintTotalTasks = computed(() => {
  if (!activeSprint.value) return 0;
  return (project.value.tasks || []).filter((t) => t.sprintId === activeSprint.value?.id).length;
});

const activeSprintCompletedTasks = computed(() => {
  if (!activeSprint.value) return 0;
  return (project.value.tasks || []).filter(
    (t) => t.sprintId === activeSprint.value?.id && t.status === 'Done',
  ).length;
});

const teamMembersOptions = computed(() => {
  return projectTeamMembers.value.map((member) => ({
    label: member.name,
    value: member.id,
  }));
});

// Epic options for task epic selector
const epicOptions = computed(() => {
  return epicStore.epics.map((epic) => ({
    label: epic.name,
    value: epic.id,
  }));
});

// Skills from team members (option A - single source of truth)
// Also includes skills from existing tasks so we don't lose them when editing
const FALLBACK_SKILLS = [
  'JavaScript',
  'Python',
  'TypeScript',
  'Vue.js',
];
const availableSkillsForTasks = computed(() => {
  const skills = new Set<string>();
  teamStore.teamMembers.forEach((member) => {
    (member.skills || []).forEach((s: string) => skills.add(s));
  });
  (project.value.tasks || []).forEach((task) => {
    (task.requiredSkills || []).forEach((s: string) => skills.add(s));
  });
  const list = [...skills].sort((a, b) => a.localeCompare(b));
  return list.length > 0 ? list : FALLBACK_SKILLS;
});

// Available tasks for dependencies (existing tasks in the project)
const availableTasksForDependencies = computed(() => {
  return project.value.tasks.map((task) => ({
    label: task.title || task.name,
    value: task.id,
    status: task.status,
    storyPoints: task.storyPoints,
  }));
});

// Available tasks for dependencies in edit mode (exclude current task)
const availableTasksForEditDependencies = computed(() => {
  return project.value.tasks
    .filter((task) => task.id !== editTask.value.id)
    .map((task) => ({
      label: task.title || task.name,
      value: task.id,
      status: task.status,
      storyPoints: task.storyPoints,
    }));
});

// Available team members to add
const availableMembersToAdd = computed(() => {
  const currentMemberIds = project.value.teamMemberIds || [];
  return teamStore.teamMembers.filter((m) => !currentMemberIds.includes(m.id));
});

// Kanban board tasks - show only tasks from active sprint
const todoTasks = computed(() => {
  if (!activeSprint.value || !project.value || !project.value.tasks) return [];
  return project.value.tasks.filter(
    (t) =>
      t.projectId === project.value.id &&
      t.sprintId === activeSprint.value!.id &&
      t.status === 'To Do',
  );
});

const inProgressTasks = computed(() => {
  if (!activeSprint.value || !project.value || !project.value.tasks) return [];
  return project.value.tasks.filter(
    (t) =>
      t.projectId === project.value.id &&
      t.sprintId === activeSprint.value!.id &&
      t.status === 'In Progress',
  );
});

const doneTasks = computed(() => {
  if (!activeSprint.value || !project.value || !project.value.tasks) return [];
  return project.value.tasks.filter(
    (t) =>
      t.projectId === project.value.id &&
      t.sprintId === activeSprint.value!.id &&
      t.status === 'Done',
  );
});

// Completed tasks - all tasks with status Done, sorted by most recent (by ID)
const completedTasks = computed(() => {
  if (!project.value || !project.value.tasks) return [];
  return project.value.tasks
    .filter((t) => t.projectId === project.value.id) // Explicit filter by project ID
    .filter((t) => t.status === 'Done' || t.completed)
    .sort((a, b) => b.id - a.id); // Most recent first (higher ID = newer)
});

// New task form
const newTask = ref({
  title: '',
  description: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  type: 'feature' as 'feature' | 'bug' | 'task',
  storyPoints: 5,
  labels: [] as string[],
  dependencies: [] as number[],
  epicId: null as number | null,
  requiredSkills: [] as string[],
  actualHours: 0,
  dueDate: '',
  pert: {
    optimistic: 8,
    mostLikely: 16,
    pessimistic: 24,
  },
  raci: {
    responsible: [] as number[],
    accountable: null as number | null,
    consulted: [] as number[],
    informed: [] as number[],
  },
});

// Edit task form
const editTask = ref({
  id: 0,
  title: '',
  description: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  type: 'feature' as 'feature' | 'bug' | 'task',
  status: 'To Do' as 'To Do' | 'In Progress' | 'Done' | 'Split' | 'Blocked',
  storyPoints: 5,
  labels: [] as string[],
  dependencies: [] as number[],
  epicId: null as number | null,
  requiredSkills: [] as string[],
  actualHours: 0,
  dueDate: '',
  pert: {
    optimistic: 8,
    mostLikely: 16,
    pessimistic: 24,
  },
  raci: {
    responsible: [] as number[],
    accountable: null as number | null,
    consulted: [] as number[],
    informed: [] as number[],
  },
});

// Sprint form
const sprintForm = ref({
  name: '',
  goal: '',
  startDate: '',
  endDate: '',
});

const isSprintFormValid = computed(() => {
  return sprintForm.value.name && sprintForm.value.startDate && sprintForm.value.endDate;
});

// Helper to get member's project role
function getMemberProjectRole(memberId: number): string {
  const projectRole = project.value.roles?.find((r) => r.memberId === memberId);
  return projectRole?.role || 'developer';
}

// Methods
function navigateBack() {
  router.push('/projects');
}

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

function getPriorityColor(priority: string): string {
  const p = priority.toLowerCase();
  switch (p) {
    case 'high':
      return 'red';
    case 'medium':
      return 'orange';
    case 'low':
      return 'blue';
    default:
      return 'grey';
  }
}

function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return format(d, 'MMM dd, yyyy');
}

function getSprintName(sprintId: number | null): string | null {
  if (!sprintId) return null;
  const sprint = project.value.sprints?.find((s) => s.id === sprintId);
  return sprint ? sprint.name : null;
}

// Drag and drop functions
function onDragStart(task: Task) {
  draggedTask.value = task;
}

function onDragEnd() {
  draggedTask.value = null;
  isDragOver.value = false;
  dragTarget.value = null;
}

function onDragOver(target: number | string) {
  isDragOver.value = true;
  dragTarget.value = target;
}

function onDragLeave() {
  isDragOver.value = false;
  dragTarget.value = null;
}

async function onDrop(sprintId: number) {
  isDragOver.value = false;
  dragTarget.value = null;

  if (!draggedTask.value) return;

  // Find the task in the project
  const task = project.value.tasks?.find((t) => t.id === draggedTask.value!.id);
  if (task) {
    const oldSprintId = task.sprintId;
    
    // Don't move if already in the target sprint
    if (task.sprintId === sprintId) {
      draggedTask.value = null;
      return;
    }
    
    task.sprintId = sprintId;

    // Save to backend
    try {
      await projectStore.updateTask(task.id, {
        sprintId: sprintId,
      });

      // Reload project to get updated sprint stats
      await projectStore.getProject(projectId.value);

      const sprint = project.value.sprints?.find(s => s.id === sprintId);
      const sprintName = sprint ? sprint.name : 'Sprint';

      $q.notify({
        message: `Added "${task.title}" to ${sprintName}`,
        color: 'positive',
        icon: 'check',
        position: 'top',
        timeout: 1000,
      });
    } catch (error) {
      // Revert on error
      task.sprintId = oldSprintId;
      $q.notify({
        message: getErrorMessage(error, 'Failed to add task to sprint'),
        color: 'negative',
        icon: 'error',
        position: 'top',
      });
    }
  }

  draggedTask.value = null;
}

// Helper functions for planned sprints
function togglePlannedSprint(sprintId: number) {
  if (expandedPlannedSprints.value.has(sprintId)) {
    expandedPlannedSprints.value.delete(sprintId);
  } else {
    expandedPlannedSprints.value.add(sprintId);
  }
}

function isPlannedSprintExpanded(sprintId: number): boolean {
  return expandedPlannedSprints.value.has(sprintId);
}

function getSprintTasks(sprintId: number): Task[] {
  if (!project.value || !project.value.tasks) return [];
  return project.value.tasks.filter(
    (task) => task.projectId === project.value.id && task.sprintId === sprintId
  );
}

// Context menu functions
function showTaskContextMenu(event: MouseEvent, task: Task, source: 'backlog' | 'sprint') {
  contextMenuTask.value = task;
  contextMenuSource.value = source;
  contextMenuX.value = event.clientX;
  contextMenuY.value = event.clientY;
  showContextMenu.value = true;
}

async function moveTaskToSprint() {
  if (!contextMenuTask.value || !activeSprint.value) {
    $q.notify({
      message: 'No active sprint available',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    showContextMenu.value = false;
    return;
  }

  const task = contextMenuTask.value;
  try {
    await projectStore.updateTask(task.id, {
      sprintId: activeSprint.value.id,
    });

    $q.notify({
      message: `Moved "${task.title}" to sprint`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
  } catch (error) {
    console.error('Failed to move task to sprint:', error);
    $q.notify({
      message: getErrorMessage(error, 'Failed to move task to sprint'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
  showContextMenu.value = false;
}

async function moveTaskToBacklog() {
  if (!contextMenuTask.value) {
    showContextMenu.value = false;
    return;
  }

  const task = contextMenuTask.value;
  try {
    await projectStore.updateTask(task.id, {
      sprintId: null,
    });

    $q.notify({
      message: `Moved "${task.title}" to backlog`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
  } catch (error) {
    console.error('Failed to move task to backlog:', error);
    $q.notify({
      message: getErrorMessage(error, 'Failed to move task to backlog'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
  showContextMenu.value = false;
}

async function removeFromSprint(taskId: number) {
  const task = project.value.tasks?.find((t) => t.id === taskId);
  if (task) {
    const oldSprintId = task.sprintId;
    task.sprintId = null;

    try {
      await projectStore.updateTask(task.id, {
        sprintId: null,
      });

      // Reload project to get updated sprint stats
      await projectStore.getProject(projectId.value);

      $q.notify({
        message: `Removed "${task.title}" from sprint`,
        color: 'info',
        icon: 'remove_circle',
        position: 'top',
        timeout: 1000,
      });
    } catch (error) {
      // Revert on error
      task.sprintId = oldSprintId;
      $q.notify({
        message: getErrorMessage(error, 'Failed to remove task from sprint'),
        color: 'negative',
        icon: 'error',
        position: 'top',
      });
    }
  }
}

function confirmDeleteTask(task: Task) {
  $q.dialog({
    title: 'Delete Task',
    message: `Are you sure you want to delete "${task.title}"? This action cannot be undone.`,
    persistent: true,
    ok: {
      label: 'Delete',
      color: 'negative',
      flat: true,
    },
    cancel: {
      label: 'Cancel',
      color: 'grey',
      flat: true,
    },
  }).onOk(async () => {
    await deleteTask(task.id);
  });
}

async function deleteTask(taskId: number) {
  const task = project.value.tasks?.find((t) => t.id === taskId);
  if (!task) return;

  try {
    await projectStore.deleteTask(taskId);

    // Reload project to get updated stats
    await projectStore.getProject(projectId.value);

    $q.notify({
      message: `Task "${task.title}" deleted successfully`,
      color: 'positive',
      icon: 'delete',
      position: 'top',
    });
  } catch (error) {
    $q.notify({
      message: getErrorMessage(error, 'Failed to delete task'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

async function toggleTaskStatus(task: Task) {
  const oldStatus = task.status;
  const oldCompleted = task.completed;

  if (task.status === 'Done') {
    task.status = 'To Do';
    task.completed = false;
  } else {
    task.status = 'Done';
    task.completed = true;
  }

  try {
    await projectStore.updateTask(task.id, {
      status: task.status,
      completed: task.completed,
    });

    // Reload project to get updated stats
    await projectStore.getProject(projectId.value);

    $q.notify({
      message: `Task ${task.status === 'Done' ? 'completed' : 'reopened'}`,
      color: 'positive',
      icon: task.status === 'Done' ? 'check_circle' : 'replay',
      position: 'top',
      timeout: 1000,
    });
  } catch (error) {
    // Revert on error
    task.status = oldStatus;
    task.completed = oldCompleted;
    $q.notify({
      message: getErrorMessage(error, 'Failed to update task status'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

// Task management
async function createTask() {
  if (!newTask.value.title) {
    $q.notify({
      message: 'Please provide a task title',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Calculate PERT expected time
  const pertExpected =
    (newTask.value.pert.optimistic +
      4 * newTask.value.pert.mostLikely +
      newTask.value.pert.pessimistic) /
    6;

  const taskData: Partial<Task> = {
    projectId: project.value.id,
    name: newTask.value.title,
    title: newTask.value.title,
    description: newTask.value.description,
    status: 'To Do' as 'To Do' | 'In Progress' | 'Done',
    priority: newTask.value.priority,
    type: newTask.value.type,
    storyPoints: newTask.value.storyPoints,
    sprintId: null,
    epicId: newTask.value.epicId,
    dueDate: newTask.value.dueDate ? new Date(newTask.value.dueDate).toISOString() : '',
    completed: false,
    labels: newTask.value.labels,
    dependencies: newTask.value.dependencies,
    requiredSkills: newTask.value.requiredSkills,
    actualHours: newTask.value.actualHours,
    pert: {
      optimistic: newTask.value.pert.optimistic,
      mostLikely: newTask.value.pert.mostLikely,
      pessimistic: newTask.value.pert.pessimistic,
      expected: Number(pertExpected.toFixed(2)),
    },
    raci: {
      responsible: newTask.value.raci.responsible,
      accountable: newTask.value.raci.accountable,
      consulted: newTask.value.raci.consulted,
      informed: newTask.value.raci.informed,
    },
  };

  try {
    await projectStore.createTask(project.value.id, taskData);

    // Reload project to get updated data
    await projectStore.getProject(projectId.value);

    $q.notify({
      message: `Task "${newTask.value.title}" created successfully`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });

    cancelNewTask();
    showNewTaskDialog.value = false;
  } catch (error) {
    $q.notify({
      message: getErrorMessage(error, 'Failed to create task'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function cancelNewTask() {
  newTask.value = {
    title: '',
    description: '',
    priority: 'medium',
    type: 'feature',
    storyPoints: 5,
    labels: [],
    dependencies: [],
    epicId: null,
    requiredSkills: [],
    actualHours: 0,
    dueDate: '',
    pert: {
      optimistic: 8,
      mostLikely: 16,
      pessimistic: 24,
    },
    raci: {
      responsible: [],
      accountable: null,
      consulted: [],
      informed: [],
    },
  };
}

// Edit task functions
function openEditTaskDialog(task: Task) {
  // Format due date for input[type="date"] (YYYY-MM-DD)
  let dueDateFormatted = '';
  if (task.dueDate) {
    try {
      const date = new Date(task.dueDate);
      if (!isNaN(date.getTime())) {
        const isoString = date.toISOString().split('T')[0];
        if (isoString) {
          dueDateFormatted = isoString;
        }
      }
    } catch {
      console.warn('Invalid due date format:', task.dueDate);
    }
  }

  editTask.value = {
    id: task.id,
    title: task.title,
    description: task.description,
    priority: task.priority.toLowerCase() as 'high' | 'medium' | 'low',
    type: task.type,
    status: task.status,
    storyPoints: task.storyPoints,
    labels: [...task.labels],
    dependencies: task.dependencies ? [...task.dependencies] : [],
    epicId: task.epicId || null,
    requiredSkills: task.requiredSkills ? [...task.requiredSkills] : [],
    actualHours: task.actualHours || 0,
    dueDate: dueDateFormatted,
    pert: {
      optimistic: task.pert?.optimistic || 8,
      mostLikely: task.pert?.mostLikely || 16,
      pessimistic: task.pert?.pessimistic || 24,
    },
    raci: {
      responsible: task.raci?.responsible ? [...task.raci.responsible] : [],
      accountable: task.raci?.accountable || null,
      consulted: task.raci?.consulted ? [...task.raci.consulted] : [],
      informed: task.raci?.informed ? [...task.raci.informed] : [],
    },
  };
  showEditTaskDialog.value = true;
}

async function saveEditTask() {
  if (!editTask.value.title) {
    $q.notify({
      message: 'Please provide a task title',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  const task = project.value.tasks?.find((t) => t.id === editTask.value.id);
  if (task) {
    // Calculate PERT expected
    const pertExpected =
      (editTask.value.pert.optimistic +
        4 * editTask.value.pert.mostLikely +
        editTask.value.pert.pessimistic) /
      6;

    try {
      // Save to backend
      await projectStore.updateTask(task.id, {
        title: editTask.value.title,
        name: editTask.value.title,
        description: editTask.value.description,
        priority: editTask.value.priority,
        type: editTask.value.type,
        status: editTask.value.status,
        storyPoints: editTask.value.storyPoints,
        labels: editTask.value.labels,
        dependencies: editTask.value.dependencies,
        epicId: editTask.value.epicId,
        completed: editTask.value.status === 'Done',
        requiredSkills: editTask.value.requiredSkills,
        actualHours: editTask.value.actualHours,
        dueDate: editTask.value.dueDate ? new Date(editTask.value.dueDate).toISOString() : '',
        pert: {
          optimistic: editTask.value.pert.optimistic,
          mostLikely: editTask.value.pert.mostLikely,
          pessimistic: editTask.value.pert.pessimistic,
          expected: Number(pertExpected.toFixed(2)),
        },
        raci: {
          responsible: editTask.value.raci.responsible,
          accountable: editTask.value.raci.accountable,
          consulted: editTask.value.raci.consulted,
          informed: editTask.value.raci.informed,
        },
      });

      // Reload project to get updated data
      await projectStore.getProject(projectId.value);

      $q.notify({
        message: `Task "${editTask.value.title}" updated successfully`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });

      showEditTaskDialog.value = false;
      cancelEditTask();
    } catch (error) {
      $q.notify({
        message: getErrorMessage(error, 'Failed to update task'),
        color: 'negative',
        icon: 'error',
        position: 'top',
      });
    }
  }
}

function cancelEditTask() {
  editTask.value = {
    id: 0,
    title: '',
    description: '',
    priority: 'medium',
    type: 'feature',
    status: 'To Do',
    storyPoints: 5,
    labels: [],
    dependencies: [],
    epicId: null,
    requiredSkills: [],
    actualHours: 0,
    dueDate: '',
    pert: {
      optimistic: 8,
      mostLikely: 16,
      pessimistic: 24,
    },
    raci: {
      responsible: [],
      accountable: null,
      consulted: [],
      informed: [],
    },
  };
}

// Sprint management functions
function editSprint(sprint: Sprint) {
  sprintForm.value = {
    name: sprint.name,
    goal: sprint.goal,
    startDate: format(sprint.startDate, 'yyyy-MM-dd'),
    endDate: format(sprint.endDate, 'yyyy-MM-dd'),
  };
  editingSprintId.value = sprint.id;
  showNewSprintDialog.value = true;
}

async function startSprint(sprint: Sprint) {
  // Check if there's already an active sprint
  if (activeSprint.value) {
    $q.notify({
      message: 'Please complete the current active sprint first',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  try {
    await projectStore.updateSprint(projectId.value, sprint.id, {
      status: 'active',
    });

    // Reload project to get updated data
    await projectStore.getProject(projectId.value);

    $q.notify({
      message: `Sprint "${sprint.name}" started`,
      color: 'positive',
      icon: 'play_arrow',
      position: 'top',
    });
  } catch (error) {
    $q.notify({
      message: getErrorMessage(error, 'Failed to start sprint'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

async function completeSprint(sprint: Sprint) {
  // Find tasks in this sprint before completing
  const sprintTasks =
    project.value.tasks?.filter((t) => t.sprintId === sprint.id) || [];
  const incompleteTasks = sprintTasks.filter((t) => t.status !== 'Done');
  const completedCount = sprintTasks.filter((t) => t.status === 'Done').length;
  const totalPlanned = sprintTasks.length;

  try {
    // Automatically move incomplete tasks to backlog
    if (incompleteTasks.length > 0) {
      for (const task of incompleteTasks) {
        await projectStore.updateTask(task.id, {
          sprintId: null, // Move to backlog
        });
      }
    }

    // Complete the sprint - pass counts for report (incomplete tasks moved to backlog)
    await projectStore.updateSprint(projectId.value, sprint.id, {
      status: 'completed',
      totalTasks: totalPlanned,
      completedTasks: completedCount,
    });

    // Reload project
    await projectStore.getProject(projectId.value);

    const message =
      incompleteTasks.length > 0
        ? `Sprint completed. ${incompleteTasks.length} incomplete tasks moved to backlog`
        : `Sprint "${sprint.name}" completed`;

    $q.notify({
      message: message,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
  } catch (error) {
    $q.notify({
      message: getErrorMessage(error, 'Failed to complete sprint'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function confirmDeleteSprint(sprint: Sprint) {
  const isActive = sprint.status === 'active';
  const hasActiveTasks = sprint.totalTasks > 0 && sprint.completedTasks < sprint.totalTasks;

  let warningMessage = `Are you sure you want to delete "${sprint.name}"?`;

  if (isActive) {
    warningMessage += ` This is the active sprint.`;
  }

  if (hasActiveTasks) {
    warningMessage += ` All tasks in this sprint will be moved to backlog.`;
  }

  warningMessage += ' This action cannot be undone.';

  $q.dialog({
    title: 'Delete Sprint',
    message: warningMessage,
    persistent: true,
    ok: {
      label: 'Delete',
      color: 'negative',
      flat: true,
    },
    cancel: {
      label: 'Cancel',
      color: 'grey',
      flat: true,
    },
  }).onOk(async () => {
    await deleteSprint(sprint);
  });
}

async function deleteSprint(sprint: Sprint) {
  try {
    await projectStore.deleteSprint(projectId.value, sprint.id);

    // Reload project to get updated data
    await projectStore.getProject(projectId.value);

    $q.notify({
      message: `Sprint "${sprint.name}" deleted successfully`,
      color: 'positive',
      icon: 'delete',
      position: 'top',
    });
  } catch (error) {
    $q.notify({
      message: getErrorMessage(error, 'Failed to delete sprint'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

async function createSprint() {
  if (!isSprintFormValid.value) {
    $q.notify({
      message: 'Please fill in all required fields',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  try {
    if (editingSprintId.value) {
      // Update existing sprint
      const sprint = project.value.sprints?.find((s) => s.id === editingSprintId.value);
      if (sprint) {
        await projectStore.updateSprint(projectId.value, sprint.id, {
          name: sprintForm.value.name,
          goal: sprintForm.value.goal,
          startDate: new Date(sprintForm.value.startDate),
          endDate: new Date(sprintForm.value.endDate),
        });

        $q.notify({
          message: `Sprint "${sprintForm.value.name}" updated successfully!`,
          color: 'positive',
          icon: 'check_circle',
          position: 'top',
        });
      }
    } else {
      // Create new sprint
      await projectStore.addSprint(projectId.value, {
        name: sprintForm.value.name,
        goal: sprintForm.value.goal,
        startDate: new Date(sprintForm.value.startDate),
        endDate: new Date(sprintForm.value.endDate),
        status: 'planned',
        totalTasks: 0,
        completedTasks: 0,
        taskIds: [],
      });

      $q.notify({
        message: `Sprint "${sprintForm.value.name}" created successfully!`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
    }

    showNewSprintDialog.value = false;
    cancelSprintDialog();
  } catch (error) {
    $q.notify({
      message: getErrorMessage(error, 'Failed to create sprint'),
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

async function openCreateSprintDialog() {
  editingSprintId.value = null;
  const sprintCount = (project.value.sprints?.length || 0) + 1;
  sprintForm.value = {
    name: `Sprint ${sprintCount}`,
    goal: '',
    startDate: '',
    endDate: '',
  };
  // Fetch next sprint dates from API (2-week cadence)
  const nextDates = await projectStore.getNextSprintDates(projectId.value);
  if (nextDates) {
    sprintForm.value.startDate = nextDates.startDate;
    sprintForm.value.endDate = nextDates.endDate;
  }
  showNewSprintDialog.value = true;
}

function cancelSprintDialog() {
  sprintForm.value = {
    name: '',
    goal: '',
    startDate: '',
    endDate: '',
  };
  editingSprintId.value = null;
}

// Team management functions
function getRoleColor(role: string): string {
  switch (role) {
    case 'owner':
      return 'purple';
    case 'admin':
      return 'blue';
    case 'developer':
      return 'green';
    case 'viewer':
      return 'grey';
    default:
      return 'grey';
  }
}

function changeMemberRole(member: TeamMember) {
  memberToChangeRole.value = member;
  selectedRole.value = getMemberProjectRole(member.id);
  showChangeRoleDialog.value = true;
}

async function saveRoleChange() {
  if (!memberToChangeRole.value) return;

  try {
    await projectStore.updateMemberRole(
      projectId.value,
      memberToChangeRole.value.id,
      selectedRole.value as 'owner' | 'admin' | 'developer' | 'viewer',
    );

    $q.notify({
      message: `${memberToChangeRole.value.name}'s role changed to ${selectedRole.value.toUpperCase()}`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });

    showChangeRoleDialog.value = false;
    cancelChangeRole();
  } catch (err) {
    console.error('Failed to update member role:', err);
    $q.notify({
      message: 'Failed to update member role',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function cancelChangeRole() {
  memberToChangeRole.value = null;
  selectedRole.value = 'developer';
}

async function removeMember(member: TeamMember) {
  try {
    await projectStore.removeMemberFromProject(projectId.value, member.id);

    $q.notify({
      message: `${member.name} removed from project`,
      color: 'positive',
      icon: 'person_remove',
      position: 'top',
    });
  } catch {
    $q.notify({
      message: projectStore.error || 'Failed to remove member from project',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

async function addMemberToProject() {
  if (!selectedMemberToAdd.value) return;

  try {
    await projectStore.addMemberToProject(
      projectId.value,
      selectedMemberToAdd.value.id,
      newMemberRole.value as 'owner' | 'admin' | 'developer' | 'viewer',
    );

    $q.notify({
      message: `${selectedMemberToAdd.value.name} added to project successfully!`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });

    showAddMemberDialog.value = false;
    cancelAddMember();
  } catch {
    $q.notify({
      message: projectStore.error || 'Failed to add member to project',
      color: 'negative',
      icon: 'error',
      position: 'top',
    });
  }
}

function cancelAddMember() {
  selectedMemberToAdd.value = null;
  newMemberRole.value = 'developer';
}

// Kanban drag and drop functions
function onKanbanDragStart(task: Task) {
  kanbanDraggedTask.value = task;
}

function onKanbanDragEnd() {
  kanbanDraggedTask.value = null;
  dragOverColumn.value = null;
}

function onKanbanDragOver(column: string) {
  dragOverColumn.value = column;
}

function onKanbanDragLeave() {
  dragOverColumn.value = null;
}

async function onKanbanDrop(newStatus: string) {
  dragOverColumn.value = null;

  if (!kanbanDraggedTask.value) return;

  const task = project.value.tasks?.find((t) => t.id === kanbanDraggedTask.value!.id);
  if (task && task.status !== newStatus) {
    const oldStatus = task.status;
    const oldCompleted = task.completed;

    task.status = newStatus as 'To Do' | 'In Progress' | 'Done';
    task.completed = newStatus === 'Done';

    try {
      await projectStore.updateTask(task.id, {
        status: task.status,
        completed: task.completed,
      });

      // Reload project to get updated stats
      await projectStore.getProject(projectId.value);

      $q.notify({
        message: `Task moved to ${newStatus}`,
        color: 'positive',
        icon: 'check',
        position: 'top',
        timeout: 1000,
      });
    } catch (error) {
      // Revert on error
      task.status = oldStatus;
      task.completed = oldCompleted;
      $q.notify({
        message: getErrorMessage(error, 'Failed to move task'),
        color: 'negative',
        icon: 'error',
        position: 'top',
      });
    }
  }

  kanbanDraggedTask.value = null;
}

// Workload functions for Overview
function getProjectWorkload(memberId: number): number {
  // Calculate workload percentage for this project based on tasks in ACTIVE SPRINT only
  // This matches the backend API calculation

  const member = teamStore.teamMembers.find((m) => m.id === memberId);
  if (!member) return 0;

  const maxStoryPoints = member.maxStoryPoints || 20;

  // Get active sprint for this project
  const activeSprintForProject = project.value.sprints?.find((s) => s.status === 'active');

  if (!activeSprintForProject) {
    return 0; // No active sprint = no workload from this project
  }

  // Filter tasks: in active sprint, assigned to member (via RACI) - Sprint Commitment
  const memberTasks =
    project.value.tasks?.filter(
      (t) =>
        t.sprintId === activeSprintForProject.id &&
        t.raci?.responsible?.includes(memberId),
    ) || [];

  const totalSP = memberTasks.reduce((sum, t) => sum + t.storyPoints, 0);

  // Calculate as percentage of member's total capacity
  return maxStoryPoints > 0 ? Math.round((totalSP / maxStoryPoints) * 100) : 0;
}

function getTotalWorkload(memberId: number): number {
  // Calculate total workload across ALL projects (all active sprints)
  const member = teamStore.teamMembers.find((m) => m.id === memberId);
  if (!member) return 0;

  const maxStoryPoints = member.maxStoryPoints || 20;
  let totalStoryPoints = 0;

  // Iterate through all projects
  projectStore.projects.forEach((proj) => {
    // Find active sprint for this project
    const activeSprintForProject = proj.sprints?.find((s) => s.status === 'active');
    
    if (activeSprintForProject && proj.tasks) {
      // Get tasks assigned to this member in active sprint
      const memberTasks = proj.tasks.filter((task) => {
        const isInActiveSprint = task.sprintId === activeSprintForProject.id;
        const isResponsible = task.raci?.responsible && task.raci.responsible.includes(memberId);
        return isInActiveSprint && isResponsible;
      });

      totalStoryPoints += memberTasks.reduce((sum, task) => sum + (task.storyPoints || 0), 0);
    }
  });

  return maxStoryPoints > 0 ? Math.round((totalStoryPoints / maxStoryPoints) * 100) : 0;
}

function getOtherProjectsWorkload(memberId: number): number {
  // Get total workload and subtract this project's workload
  const totalWorkload = getTotalWorkload(memberId);
  const thisProjectWorkload = getProjectWorkload(memberId);
  
  return Math.max(0, totalWorkload - thisProjectWorkload);
}

function getResponsibleAvatar(memberId: number | null): string {
  if (!memberId) return 'https://cdn.quasar.dev/img/avatar.png';

  const member = teamStore.teamMembers.find((m) => m.id === memberId);
  return member?.avatar || 'https://cdn.quasar.dev/img/avatar.png';
}

function getResponsibleNames(responsibleIds: number[]): string {
  if (!responsibleIds || responsibleIds.length === 0) return 'Unassigned';

  const names = responsibleIds
    .map((id) => teamStore.teamMembers.find((m) => m.id === id)?.name)
    .filter((name) => name)
    .join(', ');

  return names || 'Unassigned';
}
</script>

<style scoped>
.text-strike {
  text-decoration: line-through;
}

.rounded-borders {
  border-radius: 8px;
}

.active-sprint-card {
  border-left: 4px solid #21ba45;
}

.task-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.cursor-grab {
  cursor: grab;
}

.cursor-grab:active {
  cursor: grabbing;
}

.sprint-drop-zone {
  transition: all 0.3s ease;
}

.sprint-drop-zone.drag-over {
  background-color: #e3f2fd;
  border: 2px dashed #1976d2;
}

.kanban-container {
  min-height: 600px;
}

.kanban-column {
  height: 100%;
}

.kanban-column.drag-over {
  background-color: #f5f5f5;
  border: 2px dashed #1976d2;
}

.kanban-cards-area {
  min-height: 500px;
  max-height: 70vh;
  overflow-y: auto;
}

.kanban-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.kanban-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sprint-management-sections {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
}

.project-team-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
}

.project-team-grid > div {
  display: flex;
}

.project-team-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-team-card-content {
  flex: 1;
}

.overview-summary-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.overview-summary-grid > div {
  display: flex;
}

.overview-stat-card {
  width: 100%;
  height: 100%;
}

.overview-stat-section {
  min-height: 128px;
}

.analytics-sections {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr;
}

.analytics-cards-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.analytics-cards-grid > div {
  display: flex;
}

.analytics-stat-card {
  width: 100%;
  height: 100%;
}

@media (max-width: 1240px) {
  .overview-summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .project-team-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1023px) {
  .overview-summary-grid {
    grid-template-columns: 1fr;
  }

  .project-team-grid {
    grid-template-columns: 1fr;
  }

  .analytics-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
