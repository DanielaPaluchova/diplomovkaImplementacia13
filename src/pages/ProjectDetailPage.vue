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
          <div class="text-h6 text-weight-bold">{{ project.progress }}%</div>
          <q-linear-progress :value="project.progress / 100" color="white" class="q-mt-xs" />
        </div>
        <div class="col">
          <div class="text-caption">Tasks</div>
          <div class="text-h6 text-weight-bold">
            {{ project.tasksCompleted }}/{{ project.totalTasks }}
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
              <div class="row q-col-gutter-md q-mb-lg">
                <div class="col-6 col-md-3">
                  <q-card>
                <q-card-section>
                      <div class="text-caption text-grey-7">Progress</div>
                      <div class="text-h5 text-weight-bold text-primary">
                        {{ project.progress }}%
                      </div>
                      <q-linear-progress
                        :value="project.progress / 100"
                        color="primary"
                        class="q-mt-sm"
                      />
                    </q-card-section>
                  </q-card>
                </div>
                <div class="col-6 col-md-3">
                  <q-card>
                    <q-card-section>
                      <div class="text-caption text-grey-7">Total Tasks</div>
                      <div class="text-h5 text-weight-bold text-blue">
                        {{ project.tasks.length }}
                      </div>
                      <div class="text-caption text-grey-6 q-mt-xs">
                        {{ taskStats.done }} completed
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
                <div class="col-6 col-md-3">
                  <q-card>
                    <q-card-section>
                      <div class="text-caption text-grey-7">Story Points</div>
                      <div class="text-h5 text-weight-bold text-orange">
                        {{ project.totalStoryPoints }}
                      </div>
                      <div class="text-caption text-grey-6 q-mt-xs">Total capacity</div>
                    </q-card-section>
                  </q-card>
                </div>
                <div class="col-6 col-md-3">
                  <q-card>
                    <q-card-section>
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
                      <div class="text-h6 text-primary">{{ activeSprint.totalTasks }}</div>
                    </div>
                    <div class="col-4">
                      <div class="text-caption text-grey-7">Completed</div>
                      <div class="text-h6 text-green">{{ activeSprint.completedTasks }}</div>
                    </div>
                    <div class="col-4">
                      <div class="text-caption text-grey-7">Remaining</div>
                      <div class="text-h6 text-orange">
                        {{ activeSprint.totalTasks - activeSprint.completedTasks }}
                      </div>
                    </div>
                  </div>
                  <q-linear-progress
                    :value="
                      activeSprint.totalTasks > 0
                        ? activeSprint.completedTasks / activeSprint.totalTasks
                        : 0
                    "
                    color="green"
                    size="12px"
                    class="q-mt-md"
                  />
                </q-card-section>
              </q-card>

              <!-- Recent Activity -->
              <q-card>
                <q-card-section>
                  <div class="text-h6 text-weight-bold q-mb-md">Recent Tasks</div>
                  <q-list separator>
                  <q-item v-for="task in recentTasks" :key="task.id">
                    <q-item-section avatar>
                      <q-checkbox
                          :model-value="task.status === 'Done'"
                          @update:model-value="toggleTaskStatus(task)"
                        color="primary"
                      />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label :class="{ 'text-strike': task.status === 'Done' }">
                          {{ task.title }}
                      </q-item-label>
                      <q-item-label caption>
                        <q-chip
                          :color="getPriorityColor(task.priority)"
                          text-color="white"
                          size="sm"
                          dense
                        >
                          {{ task.priority }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                        <q-chip size="sm" dense>{{ task.storyPoints }} SP</q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
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
                        :value="getProjectWorkload(member.id) / 100"
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
                        :value="getOtherProjectsWorkload(member.id) / 100"
                        color="orange"
                        size="6px"
                      />
                    </div>

                    <!-- Total Workload -->
                    <div>
                      <div class="row items-center justify-between q-mb-xs">
                        <span class="text-caption text-weight-bold">Total Workload</span>
                        <span
                          class="text-caption text-weight-bold"
                          :class="{
                            'text-green': member.workload <= 80,
                            'text-orange': member.workload > 80 && member.workload <= 100,
                            'text-red': member.workload > 100,
                          }"
                        >
                          {{ member.workload }}%
                        </span>
                        </div>
                        <q-linear-progress
                          :value="member.workload / 100"
                          :color="
                          member.workload > 100 ? 'red' : member.workload > 80 ? 'orange' : 'green'
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
          <div class="row q-col-gutter-md kanban-container">
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
                        <div class="text-subtitle2 text-weight-medium q-mb-xs">
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
                        <div v-if="task.assignee" class="row items-center q-mt-sm">
                          <q-avatar size="20px" class="q-mr-xs">
                            <img :src="getAssigneeAvatar(task.assigneeId)" />
                          </q-avatar>
                          <span class="text-caption">{{ task.assignee }}</span>
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
                        <div class="text-subtitle2 text-weight-medium q-mb-xs">
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
                        <div v-if="task.assignee" class="row items-center q-mt-sm">
                          <q-avatar size="20px" class="q-mr-xs">
                            <img :src="getAssigneeAvatar(task.assigneeId)" />
                          </q-avatar>
                          <span class="text-caption">{{ task.assignee }}</span>
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
                        <div v-if="task.assignee" class="row items-center q-mt-sm">
                          <q-avatar size="20px" class="q-mr-xs">
                            <img :src="getAssigneeAvatar(task.assigneeId)" />
                          </q-avatar>
                          <span class="text-caption">{{ task.assignee }}</span>
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
          <!-- Sprint Info Bar -->
          <div v-if="activeSprint" class="q-mb-lg">
            <q-card class="bg-green-1">
              <q-card-section>
                <div class="row items-center">
                  <q-icon name="play_circle" size="32px" class="text-green q-mr-md" />
                  <div class="col">
                    <div class="text-h6 text-weight-bold text-green">{{ activeSprint.name }}</div>
                    <div class="text-caption text-grey-7">
                      {{ formatDate(activeSprint.startDate) }} -
                      {{ formatDate(activeSprint.endDate) }}
                    </div>
                  </div>
                  <div class="col-auto">
                    <q-btn
                      flat
                      color="green"
                      icon="check_circle"
                      label="Complete Sprint"
                      @click="completeSprint(activeSprint)"
                    />
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Sprint Planning Board -->
          <div class="row q-col-gutter-lg">
            <!-- Product Backlog -->
            <div class="col-12 col-lg-6">
              <q-card>
                <q-card-section class="bg-grey-3">
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold">Product Backlog</div>
                    <q-space />
                    <q-badge color="grey-7" :label="backlogTasks.length" />
                    <q-btn
                      flat
                      color="primary"
                      icon="add"
                      label="New Task"
                      class="q-ml-sm"
                      @click="showNewTaskDialog = true"
                    />
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-sm" style="min-height: 500px">
                  <div class="column q-gutter-sm">
                    <q-card
                      v-for="task in backlogTasks"
                      :key="task.id"
                      class="task-card cursor-pointer"
                      draggable="true"
                      @dragstart="onDragStart(task)"
                      @dragend="onDragEnd"
                      @click="openEditTaskDialog(task)"
                    >
                      <q-card-section class="q-pa-sm">
                        <div class="row items-start q-mb-xs">
                          <div class="col">
                            <div class="text-subtitle2 text-weight-medium">{{ task.title }}</div>
                          </div>
                          <q-chip
                            :color="getPriorityColor(task.priority)"
                            text-color="white"
                            size="sm"
                            dense
                          >
                            {{ task.priority }}
                          </q-chip>
                        </div>
                        <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                        <div class="row items-center justify-between">
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
                      </q-card-section>
                    </q-card>
                  </div>
                  <div v-if="backlogTasks.length === 0" class="text-center text-grey-5 q-pa-xl">
                    <q-icon name="inbox" size="64px" class="q-mb-md" />
                    <div>No tasks in backlog</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Sprint Backlog -->
            <div class="col-12 col-lg-6">
              <q-card
                class="sprint-drop-zone"
                :class="{ 'drag-over': isDragOver }"
                @dragover.prevent="onDragOver"
                @dragleave="onDragLeave"
                @drop="onDrop"
              >
                <q-card-section class="bg-primary text-white">
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold">
                      {{ activeSprint ? activeSprint.name : 'Sprint Backlog' }}
                    </div>
                    <q-space />
                    <q-badge color="white" text-color="primary" :label="sprintTasks.length" />
                  </div>
                  <div v-if="activeSprint" class="q-mt-sm">
                    <div class="row q-gutter-md text-caption">
                      <div>Total: {{ sprintTasks.length }} tasks</div>
                      <div>Completed: {{ completedSprintTasks }} tasks</div>
                      <div>Remaining: {{ remainingSprintTasks }} tasks</div>
                    </div>
                    <q-linear-progress
                      :value="
                        sprintTasks.length > 0 ? completedSprintTasks / sprintTasks.length : 0
                      "
                      color="white"
                      class="q-mt-sm"
                    />
                  </div>
                </q-card-section>
                <q-separator />
                <q-card-section class="q-pa-sm" style="min-height: 500px">
                  <div v-if="!activeSprint" class="text-center text-grey-5 q-pa-xl">
                    <q-icon name="event_busy" size="64px" class="q-mb-md" />
                    <div class="text-h6 q-mb-sm">No Active Sprint</div>
                    <div class="text-caption q-mb-md">Start a sprint to plan tasks</div>
                    <q-btn
                      color="primary"
                      icon="play_arrow"
                      label="Start Sprint"
                      @click="activeTab = 'sprints'"
                    />
                  </div>

                  <div v-else class="column q-gutter-sm">
                    <q-card
                      v-for="task in sprintTasks"
                      :key="task.id"
                      class="task-card cursor-pointer bg-blue-1"
                      @click="openEditTaskDialog(task)"
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
                          </div>
                        </div>
                        <div class="text-caption text-grey-7 q-mb-sm">{{ task.description }}</div>
                        <div class="row items-center justify-between">
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
                      </q-card-section>
                    </q-card>
                  </div>

                  <div
                    v-if="activeSprint && sprintTasks.length === 0"
                    class="text-center text-grey-5 q-pa-xl"
                  >
                    <q-icon name="timeline" size="64px" class="q-mb-md" />
                    <div>Drag tasks here to add to sprint</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
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
              @click="showNewSprintDialog = true"
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
                    <div class="text-h6 text-green">{{ activeSprint.completedTasks }}</div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Remaining Tasks</div>
                    <div class="text-h6 text-orange">
                      {{ activeSprint.totalTasks - activeSprint.completedTasks }}
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Total Tasks</div>
                    <div class="text-h6 text-primary">{{ activeSprint.totalTasks }}</div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Progress</div>
                    <div class="text-h6 text-blue">
                      {{
                        activeSprint.totalTasks > 0
                          ? Math.round(
                              (activeSprint.completedTasks / activeSprint.totalTasks) * 100,
                            )
                          : 0
                      }}%
                    </div>
                  </div>
                </div>

                <q-linear-progress
                  :value="
                    activeSprint.totalTasks > 0
                      ? activeSprint.completedTasks / activeSprint.totalTasks
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
                </div>
              </q-card-section>
            </q-card>
          </div>

          <!-- Sprint List -->
          <div class="row q-gutter-md">
            <!-- Planned Sprints -->
            <div class="col-12 col-md-6">
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
                          @click="deleteSprint(sprint)"
                        >
                          <q-tooltip>Delete</q-tooltip>
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

            <!-- Completed Sprints -->
            <div class="col-12 col-md-6">
              <q-card>
                <q-card-section class="bg-grey-3">
                  <div class="text-h6 text-weight-bold text-grey-8">
                    <q-icon name="check_circle" class="q-mr-sm" />
                    Completed Sprints
                  </div>
                </q-card-section>
                <q-separator />
                <q-list>
                  <q-item v-for="sprint in completedSprints" :key="sprint.id">
                    <q-item-section>
                      <q-item-label class="text-weight-medium">{{ sprint.name }}</q-item-label>
                      <q-item-label caption>{{ sprint.goal }}</q-item-label>
                      <q-item-label caption class="q-mt-xs">
                        <q-icon name="event" size="xs" class="q-mr-xs" />
                        {{ formatDate(sprint.startDate) }} - {{ formatDate(sprint.endDate) }}
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <div class="text-caption text-weight-medium">
                        {{ sprint.completedTasks }}/{{ sprint.totalTasks }} tasks
                      </div>
                      <q-linear-progress
                        :value="
                          sprint.totalTasks > 0 ? sprint.completedTasks / sprint.totalTasks : 0
                        "
                        color="green"
                        size="4px"
                        class="q-mt-xs"
                        style="width: 80px"
                      />
                    </q-item-section>
                  </q-item>
                  <q-item v-if="completedSprints.length === 0">
                    <q-item-section class="text-center text-grey-6">
                      <div class="text-caption">No completed sprints</div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </div>
          </div>
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

          <div class="row q-gutter-md">
            <div
              v-for="member in projectTeamMembers"
              :key="member.id"
              class="col-12 col-md-6 col-lg-4"
            >
              <q-card>
                <q-card-section class="text-center">
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
                    <div class="text-caption text-grey-7 q-mb-xs">Workload</div>
                    <q-linear-progress
                      :value="member.workload / 100"
                      :color="
                        member.workload > 80 ? 'red' : member.workload > 60 ? 'orange' : 'green'
                      "
                      class="q-mb-xs"
                    />
                    <div class="text-caption text-right">{{ member.workload }}%</div>
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

        <!-- Analytics Tab -->
        <q-tab-panel name="analytics">
          <div class="row q-gutter-lg">
            <!-- Charts and analytics -->
            <div class="col-12 col-md-6">
              <q-card>
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

            <div class="col-12 col-md-6">
              <q-card>
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
            <div class="col">
              <q-input
                v-model.number="newTask.complexity"
                label="Complexity (1-10)"
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

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">PERT Estimates (hours)</div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="newTask.pert.optimistic"
                label="Optimistic"
                type="number"
                filled
                hint="Best case scenario"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="newTask.pert.mostLikely"
                label="Most Likely"
                type="number"
                filled
                hint="Expected time"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="newTask.pert.pessimistic"
                label="Pessimistic"
                type="number"
                filled
                hint="Worst case scenario"
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
            <div class="col">
            <q-select
                v-model="editTask.assigneeId"
                :options="teamMembersOptions"
                label="Assignee"
              filled
                clearable
                emit-value
                map-options
              >
                <template v-slot:prepend v-if="editTask.assigneeId">
                  <q-avatar size="24px">
                    <img :src="getAssigneeAvatar(editTask.assigneeId)" />
                    </q-avatar>
              </template>
            </q-select>
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
            <div class="col">
              <q-input
                v-model.number="editTask.complexity"
                label="Complexity (1-10)"
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

          <q-separator class="q-my-md" />
          <div class="text-subtitle2 text-weight-medium q-mb-sm">PERT Estimates (hours)</div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model.number="editTask.pert.optimistic"
                label="Optimistic"
                type="number"
                filled
                hint="Best case scenario"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="editTask.pert.mostLikely"
                label="Most Likely"
                type="number"
                filled
                hint="Expected time"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="editTask.pert.pessimistic"
                label="Pessimistic"
                type="number"
                filled
                hint="Worst case scenario"
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
import { ref, computed } from 'vue';
import { format } from 'date-fns';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { useProjectStore, type Task, type Project, type Sprint } from 'src/stores/project-store';
import { useMockDataStore, type TeamMember } from 'src/stores/mock-data';

const router = useRouter();
const route = useRoute();
const $q = useQuasar();
const projectStore = useProjectStore();
const mockDataStore = useMockDataStore();

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

// Kanban drag and drop state
const dragOverColumn = ref<string | null>(null);
const kanbanDraggedTask = ref<Task | null>(null);

// Get project from store
const projectId = computed(() => Number(route.params.id));
const project = computed(() => {
  const p = projectStore.getProject(projectId.value);
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
  return p;
});

// Get team members for this project from mock data store
const projectTeamMembers = computed(() => {
  return mockDataStore.teamMembers.filter((member) =>
    project.value.teamMemberIds.includes(member.id),
  );
});

// Get tasks from project
const backlogTasks = computed(() => {
  return project.value.tasks.filter((task) => task.sprintId === null);
});

const sprintTasks = computed(() => {
  if (!activeSprint.value) return [];
  return project.value.tasks.filter((task) => task.sprintId === activeSprint.value!.id);
});

const remainingSprintTasks = computed(() => {
  return sprintTasks.value.length - completedSprintTasks.value;
});

// Sprint management
const activeSprint = computed(() => project.value.sprints.find((s) => s.status === 'active'));
const plannedSprints = computed(() => project.value.sprints.filter((s) => s.status === 'planned'));
const completedSprints = computed(() =>
  project.value.sprints.filter((s) => s.status === 'completed'),
);

// Task stats
const taskStats = computed(() => ({
  todo: project.value.tasks.filter((t) => t.status === 'To Do').length,
  inProgress: project.value.tasks.filter((t) => t.status === 'In Progress').length,
  done: project.value.tasks.filter((t) => t.status === 'Done').length,
}));

const priorityStats = computed(() => ({
  high: project.value.tasks.filter((t) => t.priority.toLowerCase() === 'high').length,
  medium: project.value.tasks.filter((t) => t.priority.toLowerCase() === 'medium').length,
  low: project.value.tasks.filter((t) => t.priority.toLowerCase() === 'low').length,
}));

const completedSprintTasks = computed(() => {
  if (!activeSprint.value) return 0;
  return sprintTasks.value.filter((t) => t.completed).length;
});

const teamMembersOptions = computed(() => {
  return projectTeamMembers.value.map((member) => ({
    label: member.name,
    value: member.id,
  }));
});

// Available team members to add
const availableMembersToAdd = computed(() => {
  const currentMemberIds = project.value.teamMemberIds;
  return mockDataStore.teamMembers.filter((m) => !currentMemberIds.includes(m.id));
});

// Kanban board tasks
const todoTasks = computed(() => {
  return project.value.tasks.filter((t) => t.status === 'To Do');
});

const inProgressTasks = computed(() => {
  return project.value.tasks.filter((t) => t.status === 'In Progress');
});

const doneTasks = computed(() => {
  return project.value.tasks.filter((t) => t.status === 'Done');
});

// Recent tasks for overview
const recentTasks = computed(() => {
  return project.value.tasks.slice(0, 5);
});

// New task form
const newTask = ref({
  title: '',
  description: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  type: 'feature' as 'feature' | 'bug' | 'task',
    storyPoints: 5,
  complexity: 5,
  labels: [] as string[],
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
  status: 'To Do' as 'To Do' | 'In Progress' | 'Done',
  storyPoints: 5,
  complexity: 5,
  labels: [] as string[],
  assigneeId: null as number | null,
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
  const projectRole = project.value.roles.find((r) => r.memberId === memberId);
  return projectRole?.role || 'developer';
}

// Methods
function navigateBack() {
  router.push('/projects');
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'On Track':
      return 'green';
    case 'In Progress':
      return 'blue';
    case 'At Risk':
      return 'orange';
    case 'Delayed':
      return 'red';
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

function formatDate(date: Date): string {
  return format(date, 'MMM dd, yyyy');
}

// Drag and drop functions
function onDragStart(task: Task) {
  draggedTask.value = task;
}

function onDragEnd() {
  draggedTask.value = null;
  isDragOver.value = false;
}

function onDragOver() {
  isDragOver.value = true;
}

function onDragLeave() {
  isDragOver.value = false;
}

function onDrop() {
  isDragOver.value = false;

  if (!draggedTask.value) return;

  if (!activeSprint.value) {
    $q.notify({
      message:
        'Nie je aktívny žiadny sprint. Prosím aktivuj ďalší sprint v sekcii "Sprint Management".',
      color: 'warning',
      icon: 'warning',
      position: 'top',
      timeout: 3000,
      actions: [
        {
          label: 'Prejsť na Sprint Management',
          color: 'white',
          handler: () => {
            activeTab.value = 'sprints';
          },
        },
      ],
    });
    draggedTask.value = null;
    return;
  }

  // Find the task in the project
  const task = project.value.tasks.find((t) => t.id === draggedTask.value!.id);
  if (task && task.sprintId === null) {
    task.sprintId = activeSprint.value.id;

    // Update sprint task counts
    projectStore.updateSprint(projectId.value, activeSprint.value.id, {
      totalTasks: sprintTasks.value.length,
    });

  $q.notify({
      message: `Added "${task.title}" to ${activeSprint.value.name}`,
    color: 'positive',
      icon: 'check',
    position: 'top',
      timeout: 1000,
    });
  }

  draggedTask.value = null;
}

function removeFromSprint(taskId: number) {
  const task = project.value.tasks.find((t) => t.id === taskId);
  if (task) {
    task.sprintId = null;

    // Update sprint task counts
    if (activeSprint.value) {
      projectStore.updateSprint(projectId.value, activeSprint.value.id, {
        totalTasks: sprintTasks.value.length,
        completedTasks: completedSprintTasks.value,
      });
    }

    $q.notify({
      message: `Removed "${task.title}" from sprint`,
      color: 'info',
      icon: 'remove_circle',
      position: 'top',
      timeout: 1000,
    });
  }
}

function toggleTaskStatus(task: Task) {
  if (task.status === 'Done') {
    task.status = 'To Do';
    task.completed = false;
  } else {
    task.status = 'Done';
    task.completed = true;
  }

  // Update sprint completed tasks count
  if (activeSprint.value) {
    projectStore.updateSprint(projectId.value, activeSprint.value.id, {
      completedTasks: completedSprintTasks.value,
    });
  }

  $q.notify({
    message: `Task ${task.status === 'Done' ? 'completed' : 'reopened'}`,
    color: 'positive',
    icon: task.status === 'Done' ? 'check_circle' : 'replay',
    position: 'top',
    timeout: 1000,
  });
}

// Task management
function createTask() {
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

  const task: Task = {
    id: Math.max(...project.value.tasks.map((t) => t.id), 0) + 1,
    name: newTask.value.title,
    title: newTask.value.title,
    description: newTask.value.description,
    status: 'To Do',
    priority: newTask.value.priority,
    type: newTask.value.type,
    storyPoints: newTask.value.storyPoints,
    assigneeId: null,
    sprintId: null,
    dueDate: new Date(),
    completed: false,
    labels: newTask.value.labels,
    complexity: newTask.value.complexity,
    pert: {
      optimistic: newTask.value.pert.optimistic,
      mostLikely: newTask.value.pert.mostLikely,
      pessimistic: newTask.value.pert.pessimistic,
      expected: Number(pertExpected.toFixed(1)),
    },
    raci: {
      responsible: newTask.value.raci.responsible,
      accountable: newTask.value.raci.accountable,
      consulted: newTask.value.raci.consulted,
      informed: newTask.value.raci.informed,
    },
  };

  project.value.tasks.push(task);

  $q.notify({
    message: `Task "${task.title}" created successfully`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });

  cancelNewTask();
  showNewTaskDialog.value = false;
}

function cancelNewTask() {
  newTask.value = {
    title: '',
    description: '',
    priority: 'medium',
    type: 'feature',
    storyPoints: 5,
    complexity: 5,
    labels: [],
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
  editTask.value = {
    id: task.id,
    title: task.title,
    description: task.description,
    priority: task.priority.toLowerCase() as 'high' | 'medium' | 'low',
    type: task.type,
    status: task.status,
    storyPoints: task.storyPoints,
    complexity: task.complexity,
    labels: [...task.labels],
    assigneeId: task.assigneeId,
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

function saveEditTask() {
  if (!editTask.value.title) {
    $q.notify({
      message: 'Please provide a task title',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  const task = project.value.tasks.find((t) => t.id === editTask.value.id);
  if (task) {
    task.title = editTask.value.title;
    task.name = editTask.value.title;
    task.description = editTask.value.description;
    task.priority = editTask.value.priority;
    task.type = editTask.value.type;
    task.status = editTask.value.status;
    task.storyPoints = editTask.value.storyPoints;
    task.complexity = editTask.value.complexity;
    task.labels = editTask.value.labels;
    task.assigneeId = editTask.value.assigneeId;

    // Update PERT estimates
    const pertExpected =
      (editTask.value.pert.optimistic +
        4 * editTask.value.pert.mostLikely +
        editTask.value.pert.pessimistic) /
      6;
    task.pert = {
      optimistic: editTask.value.pert.optimistic,
      mostLikely: editTask.value.pert.mostLikely,
      pessimistic: editTask.value.pert.pessimistic,
      expected: Number(pertExpected.toFixed(1)),
    };

    // Update RACI matrix
    task.raci = {
      responsible: editTask.value.raci.responsible,
      accountable: editTask.value.raci.accountable,
      consulted: editTask.value.raci.consulted,
      informed: editTask.value.raci.informed,
    };

    // Update assignee name
    if (task.assigneeId) {
      const assignee = mockDataStore.teamMembers.find((m) => m.id === task.assigneeId);
      if (assignee) {
        task.assignee = assignee.name;
      }
    } else {
      delete task.assignee;
    }

    // Update completed status
    task.completed = task.status === 'Done';

    // Update sprint completed tasks count if task is in a sprint
    if (task.sprintId && activeSprint.value) {
      projectStore.updateSprint(projectId.value, activeSprint.value.id, {
        completedTasks: completedSprintTasks.value,
      });
    }

  $q.notify({
      message: `Task "${task.title}" updated successfully`,
    color: 'positive',
      icon: 'check_circle',
    position: 'top',
  });
}

  showEditTaskDialog.value = false;
  cancelEditTask();
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
    complexity: 5,
    labels: [],
    assigneeId: null,
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

function startSprint(sprint: Sprint) {
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

  projectStore.updateSprint(projectId.value, sprint.id, {
    status: 'active',
  });

  $q.notify({
    message: `Sprint "${sprint.name}" started`,
    color: 'positive',
    icon: 'play_arrow',
    position: 'top',
  });
}

function completeSprint(sprint: Sprint) {
  projectStore.updateSprint(projectId.value, sprint.id, {
    status: 'completed',
  });

  $q.notify({
    message: `Sprint "${sprint.name}" completed`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
}

function deleteSprint(sprint: Sprint) {
  projectStore.deleteSprint(projectId.value, sprint.id);

    $q.notify({
      message: 'Sprint deleted',
      color: 'positive',
      icon: 'delete',
      position: 'top',
    });
  }

function createSprint() {
  if (!isSprintFormValid.value) {
    $q.notify({
      message: 'Please fill in all required fields',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  if (editingSprintId.value) {
    // Update existing sprint
    const sprint = project.value.sprints.find((s) => s.id === editingSprintId.value);
    if (sprint) {
      projectStore.updateSprint(projectId.value, sprint.id, {
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
    projectStore.addSprint(projectId.value, {
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

function saveRoleChange() {
  if (!memberToChangeRole.value) return;

  projectStore.updateMemberRole(
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
}

function cancelChangeRole() {
  memberToChangeRole.value = null;
  selectedRole.value = 'developer';
}

function removeMember(member: TeamMember) {
  projectStore.removeMemberFromProject(projectId.value, member.id);

    $q.notify({
      message: `${member.name} removed from project`,
      color: 'positive',
      icon: 'person_remove',
      position: 'top',
    });
}

function addMemberToProject() {
  if (!selectedMemberToAdd.value) return;

  projectStore.addMemberToProject(
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

function onKanbanDrop(newStatus: string) {
  dragOverColumn.value = null;

  if (!kanbanDraggedTask.value) return;

  const task = project.value.tasks.find((t) => t.id === kanbanDraggedTask.value!.id);
  if (task && task.status !== newStatus) {
    task.status = newStatus as 'To Do' | 'In Progress' | 'Done';
    task.completed = newStatus === 'Done';

    // Update sprint completed tasks count if task is in a sprint
    if (task.sprintId && activeSprint.value) {
      projectStore.updateSprint(projectId.value, activeSprint.value.id, {
        completedTasks: completedSprintTasks.value,
      });
    }

    $q.notify({
      message: `Task moved to ${newStatus}`,
      color: 'positive',
      icon: 'check',
      position: 'top',
      timeout: 1000,
    });
  }

  kanbanDraggedTask.value = null;
}

// Workload functions for Overview
function getProjectWorkload(memberId: number): number {
  // Calculate workload percentage for this project based on tasks assigned
  const memberTasks = project.value.tasks.filter((t) => t.assigneeId === memberId);
  const totalSP = memberTasks.reduce((sum, t) => sum + t.storyPoints, 0);

  // Assume 20 SP = 100% workload for one project
  return Math.min(100, Math.round((totalSP / 20) * 100));
}

function getOtherProjectsWorkload(memberId: number): number {
  // Get member's total workload and subtract this project's workload
  const member = mockDataStore.teamMembers.find((m) => m.id === memberId);
  if (!member) return 0;

  const thisProjectWorkload = getProjectWorkload(memberId);
  const otherWorkload = member.workload - thisProjectWorkload;

  return Math.max(0, otherWorkload);
}

function getAssigneeAvatar(assigneeId: number | null): string {
  if (!assigneeId) return 'https://cdn.quasar.dev/img/avatar.png';

  const member = mockDataStore.teamMembers.find((m) => m.id === assigneeId);
  return member?.avatar || 'https://cdn.quasar.dev/img/avatar.png';
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
</style>
