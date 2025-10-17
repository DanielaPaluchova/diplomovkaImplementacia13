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
          <q-btn
            unelevated
            color="white"
            text-color="primary"
            icon="view_kanban"
            label="Kanban Board"
            @click="navigateToKanban"
            class="q-mr-md"
          />
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
          <div class="text-h6 text-weight-bold">{{ project.teamMembers.length }}</div>
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
        <q-tab name="sprints" icon="event_note" label="Sprints" />
        <q-tab name="tasks" icon="task_alt" label="Tasks" />
        <q-tab name="team" icon="group" label="Team" />
        <q-tab name="analytics" icon="analytics" label="Analytics" />
      </q-tabs>

      <!-- Tab Panels -->
      <q-tab-panels v-model="activeTab" animated>
        <!-- Overview Tab -->
        <q-tab-panel name="overview">
          <div class="row q-gutter-lg">
            <!-- Left Column -->
            <div class="col-12 col-lg-8">
              <!-- Recent Tasks -->
              <q-card class="q-mb-lg">
                <q-card-section>
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold">Recent Tasks</div>
                    <q-space />
                    <q-btn flat color="primary" label="View All" @click="activeTab = 'tasks'" />
                  </div>
                </q-card-section>
                <q-separator />
                <q-list>
                  <q-item v-for="task in recentTasks" :key="task.id">
                    <q-item-section avatar>
                      <q-checkbox
                        :model-value="task.completed"
                        @update:model-value="toggleTaskComplete(task)"
                        color="primary"
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label :class="{ 'text-strike text-grey-6': task.completed }">
                        {{ task.name }}
                      </q-item-label>
                      <q-item-label caption>
                        <q-chip
                          :color="getPriorityColor(task.priority)"
                          text-color="white"
                          size="sm"
                          dense
                          class="q-mr-xs"
                        >
                          {{ task.priority }}
                        </q-chip>
                        {{ task.assignee }}
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label caption>{{ formatDate(task.dueDate) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>
            </div>

            <!-- Right Column -->
            <div class="col-12 col-lg-4">
              <!-- Team Members -->
              <q-card class="q-mb-lg">
                <q-card-section>
                  <div class="row items-center">
                    <div class="text-h6 text-weight-bold">Team Members</div>
                    <q-space />
                    <q-btn
                      flat
                      color="primary"
                      icon="add"
                      dense
                      round
                      size="sm"
                      @click="showAddMemberDialog = true"
                    >
                      <q-tooltip>Add Member</q-tooltip>
                    </q-btn>
                  </div>
                </q-card-section>
                <q-separator />
                <q-list>
                  <q-item v-for="member in project.teamMembers" :key="member.id">
                    <q-item-section avatar>
                      <q-avatar size="40px">
                        <img :src="member.avatar" />
                      </q-avatar>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ member.name }}</q-item-label>
                      <q-item-label caption>{{ member.role }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <div class="column items-end" style="min-width: 60px">
                        <div
                          class="text-caption text-weight-bold"
                          :class="{
                            'text-red': member.workload > 80,
                            'text-orange': member.workload > 60 && member.workload <= 80,
                            'text-green': member.workload <= 60,
                          }"
                        >
                          {{ member.workload }}%
                        </div>
                        <q-linear-progress
                          :value="member.workload / 100"
                          :color="
                            member.workload > 80 ? 'red' : member.workload > 60 ? 'orange' : 'green'
                          "
                          size="6px"
                          class="full-width"
                        />
                      </div>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card>

              <!-- Project Info -->
              <q-card>
                <q-card-section>
                  <div class="text-h6 text-weight-bold q-mb-md">Project Information</div>
                  <div class="q-mb-sm">
                    <div class="text-caption text-grey-7">Created</div>
                    <div class="text-weight-medium">{{ formatDate(project.createdAt) }}</div>
                  </div>
                  <div class="q-mb-sm">
                    <div class="text-caption text-grey-7">Template</div>
                    <div class="text-weight-medium">{{ project.template }}</div>
                  </div>
                  <div class="q-mb-sm">
                    <div class="text-caption text-grey-7">Total Story Points</div>
                    <div class="text-weight-medium">{{ project.totalStoryPoints }}</div>
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

        <!-- Sprints Tab -->
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
                    <div class="text-h6 text-green">
                      {{ getSprintCompletedTasks(activeSprint.id) }}
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Remaining Tasks</div>
                    <div class="text-h6 text-orange">
                      {{ getSprintRemainingTasks(activeSprint.id) }}
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Total Tasks</div>
                    <div class="text-h6 text-primary">
                      {{ getSprintTotalTasks(activeSprint.id) }}
                    </div>
                  </div>
                  <div class="col">
                    <div class="text-caption text-grey-7">Progress</div>
                    <div class="text-h6 text-blue">{{ getSprintProgress(activeSprint.id) }}%</div>
                  </div>
                </div>

                <q-linear-progress
                  :value="getSprintProgress(activeSprint.id) / 100"
                  color="green"
                  size="12px"
                  class="q-mt-md rounded-borders"
                />

                <div class="q-mt-md">
                  <q-btn
                    unelevated
                    color="primary"
                    icon="view_kanban"
                    label="Open Kanban Board"
                    @click="navigateToKanban"
                    class="q-mr-sm"
                  />
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
                        {{ getSprintCompletedTasks(sprint.id) }}/{{
                          getSprintTotalTasks(sprint.id)
                        }}
                        tasks
                      </div>
                      <q-linear-progress
                        :value="getSprintProgress(sprint.id) / 100"
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

        <!-- Tasks Tab -->
        <q-tab-panel name="tasks">
          <!-- Task View Selector -->
          <q-tabs
            v-model="taskViewTab"
            dense
            class="bg-grey-2 text-primary q-mb-lg"
            active-color="primary"
            indicator-color="primary"
            align="left"
          >
            <q-tab name="sprint" icon="sprint" label="Sprint Tasks" />
            <q-tab name="backlog" icon="inbox" label="Backlog" />
            <q-tab name="all" icon="list" label="All Tasks" />
          </q-tabs>

          <q-tab-panels v-model="taskViewTab" animated>
            <!-- Sprint Tasks -->
            <q-tab-panel name="sprint">
              <div v-if="activeSprint" class="q-mb-md">
                <q-banner class="bg-green-1 text-green" rounded>
                  <template v-slot:avatar>
                    <q-icon name="play_circle" color="green" />
                  </template>
                  <strong>{{ activeSprint.name }}</strong> - {{ activeSprint.goal }}
                  <template v-slot:action>
                    <q-chip color="green" text-color="white">
                      {{ sprintTasks.length }} tasks
                    </q-chip>
                  </template>
                </q-banner>
              </div>

              <div v-if="!activeSprint" class="text-center q-pa-xl">
                <q-icon name="event_busy" size="64px" class="text-grey-5 q-mb-md" />
                <div class="text-h6 text-grey-7">No Active Sprint</div>
                <div class="text-caption text-grey-6 q-mb-md">Start a sprint to see tasks here</div>
                <q-btn
                  color="primary"
                  icon="play_arrow"
                  label="Start Sprint"
                  @click="activeTab = 'sprints'"
                />
              </div>

              <!-- Tasks by Member -->
              <div v-if="activeSprint" class="row q-gutter-md">
                <div
                  v-for="member in project.teamMembers"
                  :key="member.id"
                  class="col-12 col-md-6 col-lg-4"
                >
                  <q-card flat bordered>
                    <q-card-section class="bg-primary text-white">
                      <div class="row items-center">
                        <q-avatar size="32px" class="q-mr-sm">
                          <img :src="member.avatar" />
                        </q-avatar>
                        <div class="col">
                          <div class="text-weight-bold">{{ member.name }}</div>
                          <div class="text-caption">
                            {{ getMemberSprintTasks(member.id).length }} tasks
                          </div>
                        </div>
                        <q-chip color="white" text-color="primary" size="sm">
                          {{ getMemberSprintStoryPoints(member.id) }} SP
                        </q-chip>
                      </div>
                    </q-card-section>

                    <q-list separator>
                      <q-item
                        v-for="task in getMemberSprintTasks(member.id)"
                        :key="task.id"
                        clickable
                        @click="editTask(task)"
                      >
                        <q-item-section avatar>
                          <q-checkbox
                            :model-value="task.status === 'Done'"
                            @update:model-value="toggleTaskStatus(task)"
                            color="primary"
                          />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label
                            :class="{ 'text-strike text-grey-6': task.status === 'Done' }"
                          >
                            {{ task.name }}
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
                            <q-chip
                              :color="getStatusColorForChip(task.status)"
                              text-color="white"
                              size="sm"
                              dense
                              class="q-ml-xs"
                            >
                              {{ task.status }}
                            </q-chip>
                          </q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <div class="text-caption text-grey-7">{{ task.storyPoints }} SP</div>
                        </q-item-section>
                      </q-item>
                      <q-item v-if="getMemberSprintTasks(member.id).length === 0">
                        <q-item-section class="text-center text-grey-6">
                          <div class="text-caption">No tasks assigned</div>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-card>
                </div>
              </div>
            </q-tab-panel>

            <!-- Backlog -->
            <q-tab-panel name="backlog">
              <div class="row items-center q-mb-md">
                <div class="text-h6 text-weight-bold">Product Backlog</div>
                <q-space />
                <q-btn
                  color="primary"
                  icon="add"
                  label="New Task"
                  @click="showNewTaskDialog = true"
                />
              </div>

              <q-list separator bordered>
                <q-item
                  v-for="task in backlogTasks"
                  :key="task.id"
                  clickable
                  @click="editTask(task)"
                >
                  <q-item-section avatar>
                    <q-icon name="inbox" color="grey-6" size="md" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ task.name }}</q-item-label>
                    <q-item-label caption>{{ task.description }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <div class="column items-end q-gutter-xs">
                      <div class="row items-center q-gutter-xs">
                        <q-chip
                          :color="getPriorityColor(task.priority)"
                          text-color="white"
                          size="sm"
                          dense
                        >
                          {{ task.priority }}
                        </q-chip>
                        <q-chip color="primary" text-color="white" size="sm" dense>
                          {{ task.storyPoints }} SP
                        </q-chip>
                      </div>
                      <div class="row items-center">
                        <q-avatar size="24px" class="q-mr-xs">
                          <img :src="task.assigneeAvatar" />
                        </q-avatar>
                        <span class="text-caption">{{ task.assignee }}</span>
                      </div>
                    </div>
                  </q-item-section>
                </q-item>
                <q-item v-if="backlogTasks.length === 0">
                  <q-item-section class="text-center text-grey-6">
                    <div class="text-caption">No backlog tasks</div>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>

            <!-- All Tasks -->
            <q-tab-panel name="all">
              <q-card>
                <q-card-section>
                  <div class="row items-center q-mb-md">
                    <div class="col">
                      <q-input v-model="taskSearch" placeholder="Search tasks..." outlined dense>
                        <template v-slot:prepend>
                          <q-icon name="search" />
                        </template>
                      </q-input>
                    </div>
                    <div class="col-auto">
                      <q-select
                        v-model="taskStatusFilter"
                        :options="['All', 'To Do', 'In Progress', 'Done']"
                        outlined
                        dense
                        style="min-width: 150px"
                      />
                    </div>
                  </div>
                </q-card-section>

                <q-separator />

                <q-table
                  :rows="filteredTasks"
                  :columns="taskColumns"
                  row-key="id"
                  :pagination="{ rowsPerPage: 10 }"
                  flat
                >
                  <template v-slot:body-cell-name="props">
                    <q-td :props="props">
                      <div class="text-weight-medium">{{ props.row.name }}</div>
                      <div class="text-caption text-grey-7">{{ props.row.description }}</div>
                    </q-td>
                  </template>

                  <template v-slot:body-cell-assignee="props">
                    <q-td :props="props">
                      <q-avatar size="32px">
                        <img :src="props.row.assigneeAvatar" />
                      </q-avatar>
                      <span class="q-ml-sm">{{ props.row.assignee }}</span>
                    </q-td>
                  </template>

                  <template v-slot:body-cell-priority="props">
                    <q-td :props="props">
                      <q-chip
                        :color="getPriorityColor(props.row.priority)"
                        text-color="white"
                        size="sm"
                        dense
                      >
                        {{ props.row.priority }}
                      </q-chip>
                    </q-td>
                  </template>

                  <template v-slot:body-cell-status="props">
                    <q-td :props="props">
                      <q-select
                        :model-value="props.row.status"
                        :options="['To Do', 'In Progress', 'Done']"
                        @update:model-value="updateTaskStatus(props.row, $event)"
                        outlined
                        dense
                        style="min-width: 120px"
                      />
                    </q-td>
                  </template>

                  <template v-slot:body-cell-actions="props">
                    <q-td :props="props">
                      <q-btn flat icon="edit" color="primary" dense @click="editTask(props.row)" />
                      <q-btn flat icon="delete" color="red" dense @click="deleteTask(props.row)" />
                    </q-td>
                  </template>
                </q-table>
              </q-card>
            </q-tab-panel>
          </q-tab-panels>
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
              v-for="member in project.teamMembers"
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
                    :color="getRoleColor(member.projectRole)"
                    text-color="white"
                    icon="badge"
                    class="q-mb-md"
                  >
                    {{ member.projectRole.toUpperCase() }}
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

                    <q-separator class="q-my-md" />

                    <div class="text-caption text-grey-7 q-mb-sm">Assigned Tasks</div>
                    <div class="text-h6 text-primary text-weight-bold">
                      {{ member.assignedTasks }}
                    </div>

                    <div class="text-caption text-grey-7 q-mt-md q-mb-sm">Story Points</div>
                    <div class="text-h6 text-primary text-weight-bold">
                      {{ member.storyPoints }}
                    </div>

                    <q-separator class="q-my-md" />

                    <!-- Permissions -->
                    <div class="text-caption text-grey-7 q-mb-sm">Permissions</div>
                    <div class="row q-gutter-xs">
                      <q-chip
                        v-if="member.permissions.canEdit"
                        size="sm"
                        color="blue-1"
                        text-color="blue-9"
                        icon="edit"
                      >
                        Edit
                      </q-chip>
                      <q-chip
                        v-if="member.permissions.canDelete"
                        size="sm"
                        color="red-1"
                        text-color="red-9"
                        icon="delete"
                      >
                        Delete
                      </q-chip>
                      <q-chip
                        v-if="member.permissions.canManageTeam"
                        size="sm"
                        color="green-1"
                        text-color="green-9"
                        icon="group"
                      >
                        Manage Team
                      </q-chip>
                      <q-chip
                        v-if="member.permissions.canManageSprints"
                        size="sm"
                        color="purple-1"
                        text-color="purple-9"
                        icon="event_note"
                      >
                        Manage Sprints
                      </q-chip>
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

            <div class="col-12">
              <q-card>
                <q-card-section>
                  <div class="text-h6 text-weight-bold q-mb-md">Velocity Trend</div>
                  <div class="text-grey-7">Story points completed over the last 4 sprints</div>
                  <div class="row q-gutter-md q-mt-md">
                    <div v-for="sprint in velocityData" :key="sprint.sprint" class="col">
                      <div class="text-center">
                        <q-linear-progress
                          :value="sprint.points / 50"
                          color="primary"
                          size="20px"
                          class="q-mb-xs"
                          style="
                            transform: rotate(180deg);
                            writing-mode: vertical-lr;
                            height: 150px;
                          "
                        />
                        <div class="text-h6 text-weight-bold q-mt-md">{{ sprint.points }}</div>
                        <div class="text-caption text-grey-7">Sprint {{ sprint.sprint }}</div>
                      </div>
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
          <q-input v-model="newTask.name" label="Task Name" filled class="q-mb-md" />
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
                :options="['High', 'Medium', 'Low']"
                label="Priority"
                filled
              />
            </div>
            <div class="col">
              <q-input v-model="newTask.storyPoints" label="Story Points" type="number" filled />
            </div>
          </div>
          <q-input v-model="newTask.dueDate" label="Due Date" type="date" filled class="q-mb-md" />
          <q-select
            v-model="newTask.assignee"
            :options="project.teamMembers"
            option-value="id"
            option-label="name"
            label="Assignee"
            filled
            emit-value
            map-options
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
          </q-select>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Create" @click="createTask" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Sprint Planning Dialog -->
    <q-dialog v-model="showNewSprintDialog" persistent>
      <q-card style="min-width: 800px; max-width: 1000px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h5 text-weight-bold">
            <q-icon name="event_note" size="sm" class="q-mr-sm" />
            {{ editingSprintId ? 'Edit Sprint' : 'Sprint Planning' }} - {{ project.name }}
          </div>
        </q-card-section>

        <q-card-section>
          <!-- Sprint Basic Info -->
          <div class="row q-gutter-md q-mb-lg">
            <div class="col-12 col-md-5">
              <q-input
                v-model="sprintForm.name"
                label="Sprint Name *"
                filled
                :rules="[(val) => !!val || 'Sprint name is required']"
              />
            </div>
            <div class="col-12 col-md-6">
              <q-input v-model="sprintForm.goal" label="Sprint Goal *" filled />
            </div>
          </div>

          <div class="row q-gutter-md q-mb-lg">
            <div class="col">
              <q-input v-model="sprintForm.startDate" label="Start Date *" type="date" filled />
            </div>
            <div class="col">
              <q-input v-model="sprintForm.endDate" label="End Date *" type="date" filled />
            </div>
          </div>

          <!-- Team Selection -->
          <div class="q-mb-lg">
            <div class="text-h6 text-weight-bold q-mb-md">
              <q-icon name="group" class="q-mr-xs" />
              Select Team Members
            </div>
            <q-select
              v-model="sprintForm.selectedMembers"
              :options="project.teamMembers"
              option-value="id"
              option-label="name"
              multiple
              filled
              use-chips
              label="Team Members for this Sprint"
              hint="Select members who will work on this sprint"
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
          </div>

          <!-- Team Capacity Planning -->
          <div v-if="sprintForm.selectedMembers.length > 0" class="q-mb-lg">
            <div class="text-h6 text-weight-bold q-mb-md">
              <q-icon name="assessment" class="q-mr-xs" />
              Team Capacity Analysis
            </div>

            <q-card flat bordered>
              <q-list separator>
                <q-item v-for="member in sprintForm.selectedMembers" :key="member.id">
                  <q-item-section avatar>
                    <q-avatar size="40px">
                      <img :src="member.avatar" />
                    </q-avatar>
                  </q-item-section>

                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ member.name }}</q-item-label>
                    <q-item-label caption>{{ member.role }}</q-item-label>
                  </q-item-section>

                  <q-item-section>
                    <q-item-label caption>Workload on Other Projects</q-item-label>
                    <div class="row items-center q-gutter-xs">
                      <q-linear-progress
                        :value="getMemberWorkloadOnOtherProjects(member.id) / 100"
                        :color="getWorkloadColor(getMemberWorkloadOnOtherProjects(member.id))"
                        size="8px"
                        style="width: 100px"
                      />
                      <span class="text-caption text-weight-medium">
                        {{ getMemberOtherProjectsStoryPoints(member.id) }} SP
                      </span>
                    </div>
                  </q-item-section>

                  <q-item-section side>
                    <div class="text-center">
                      <div class="text-caption text-grey-7">Available</div>
                      <div
                        class="text-h6 text-weight-bold"
                        :class="{
                          'text-green': getMemberAvailableCapacity(member.id) > 10,
                          'text-orange':
                            getMemberAvailableCapacity(member.id) > 5 &&
                            getMemberAvailableCapacity(member.id) <= 10,
                          'text-red': getMemberAvailableCapacity(member.id) <= 5,
                        }"
                      >
                        {{ getMemberAvailableCapacity(member.id) }} / 20 SP
                      </div>
                    </div>
                  </q-item-section>

                  <q-item-section side>
                    <q-icon
                      v-if="getMemberAvailableCapacity(member.id) <= 5"
                      name="warning"
                      color="red"
                      size="sm"
                    >
                      <q-tooltip>Member is overloaded on other projects!</q-tooltip>
                    </q-icon>
                    <q-icon
                      v-else-if="getMemberAvailableCapacity(member.id) <= 10"
                      name="info"
                      color="orange"
                      size="sm"
                    >
                      <q-tooltip>Member has limited availability</q-tooltip>
                    </q-icon>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card>
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
            emit-value
            map-options
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
          </q-select>

          <q-select
            v-model="newMemberRole"
            :options="['admin', 'member', 'viewer']"
            label="Project Role"
            filled
            class="q-mt-md"
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
            :options="['admin', 'member', 'viewer']"
            label="New Project Role"
            filled
          >
            <template v-slot:prepend>
              <q-icon name="badge" />
            </template>
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.toUpperCase() }}</q-item-label>
                  <q-item-label caption>
                    {{
                      scope.opt === 'admin'
                        ? 'Full access to project'
                        : scope.opt === 'member'
                          ? 'Can edit tasks'
                          : 'View only access'
                    }}
                  </q-item-label>
                </q-item-section>
              </q-item>
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

const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const activeTab = ref('overview');
const taskViewTab = ref('sprint');
const showNewTaskDialog = ref(false);
const showNewSprintDialog = ref(false);
const editingSprintId = ref<number | null>(null);
const showAddMemberDialog = ref(false);
const selectedMemberToAdd = ref<number | null>(null);
const newMemberRole = ref('member');
const showChangeRoleDialog = ref(false);
const memberToChangeRole = ref<TeamMember | null>(null);
const selectedRole = ref('member');
const taskSearch = ref('');
const taskStatusFilter = ref('All');

interface TeamMember {
  id: number;
  name: string;
  role: string;
  avatar: string;
  workload: number;
  assignedTasks: number;
  storyPoints: number;
  projectRole: string;
  permissions: {
    canEdit: boolean;
    canDelete: boolean;
    canManageTeam: boolean;
    canManageSprints: boolean;
  };
}

interface Sprint {
  id: number;
  name: string;
  goal: string;
  startDate: Date;
  endDate: Date;
  status: 'planned' | 'active' | 'completed';
  capacity: number;
  completed: number;
  taskIds: number[];
}

interface Task {
  id: number;
  name: string;
  description: string;
  status: string;
  priority: string;
  storyPoints: number;
  assignee: string;
  assigneeAvatar: string;
  dueDate: Date;
  completed: boolean;
  sprintId?: number | null;
}

interface Project {
  id: number;
  name: string;
  description: string;
  icon: string;
  status: string;
  progress: number;
  tasksCompleted: number;
  totalTasks: number;
  dueDate: Date;
  createdAt: Date;
  template: string;
  totalStoryPoints: number;
  estimatedDuration: number;
  teamMembers: TeamMember[];
}

// Global team members pool (defined before project to avoid circular dependency)
const globalTeamMembers: TeamMember[] = [
  {
    id: 1,
    name: 'John Smith',
    role: 'Frontend Developer',
    avatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    projectRole: 'member',
    permissions: {
      canEdit: true,
      canDelete: false,
      canManageTeam: false,
      canManageSprints: false,
    },
  },
  {
    id: 2,
    name: 'Sarah Johnson',
    role: 'Backend Developer',
    avatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    projectRole: 'member',
    permissions: {
      canEdit: true,
      canDelete: false,
      canManageTeam: false,
      canManageSprints: false,
    },
  },
  {
    id: 3,
    name: 'Mike Wilson',
    role: 'UI/UX Designer',
    avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    projectRole: 'member',
    permissions: {
      canEdit: true,
      canDelete: false,
      canManageTeam: false,
      canManageSprints: false,
    },
  },
  {
    id: 4,
    name: 'Emma Davis',
    role: 'Project Manager',
    avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    projectRole: 'member',
    permissions: {
      canEdit: true,
      canDelete: false,
      canManageTeam: false,
      canManageSprints: false,
    },
  },
  {
    id: 5,
    name: 'David Brown',
    role: 'QA Engineer',
    avatar: 'https://cdn.quasar.dev/img/avatar5.jpg',
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    projectRole: 'member',
    permissions: {
      canEdit: true,
      canDelete: false,
      canManageTeam: false,
      canManageSprints: false,
    },
  },
  {
    id: 6,
    name: 'Lisa Anderson',
    role: 'DevOps Engineer',
    avatar: 'https://cdn.quasar.dev/img/avatar6.jpg',
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    projectRole: 'member',
    permissions: {
      canEdit: true,
      canDelete: false,
      canManageTeam: false,
      canManageSprints: false,
    },
  },
];

// Mock project data (in real app, fetch by route.params.id)
const project = ref<Project>({
  id: Number(route.params.id) || 1,
  name: 'E-commerce Platform Redesign',
  description: 'Complete UI/UX overhaul of the main platform',
  icon: 'shopping_cart',
  status: 'On Track',
  progress: 75,
  tasksCompleted: 18,
  totalTasks: 24,
  dueDate: new Date('2024-03-15'),
  createdAt: new Date('2024-01-05'),
  template: 'Agile Development',
  totalStoryPoints: 180,
  estimatedDuration: 45,
  teamMembers: [
    {
      id: 1,
      name: 'John Smith',
      role: 'Frontend Developer',
      avatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
      workload: 85,
      assignedTasks: 8,
      storyPoints: 42,
      projectRole: 'developer',
      permissions: {
        canEdit: true,
        canDelete: false,
        canManageTeam: false,
        canManageSprints: false,
      },
    },
    {
      id: 3,
      name: 'Mike Wilson',
      role: 'UI/UX Designer',
      avatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
      workload: 70,
      assignedTasks: 6,
      storyPoints: 35,
      projectRole: 'developer',
      permissions: {
        canEdit: true,
        canDelete: false,
        canManageTeam: false,
        canManageSprints: false,
      },
    },
    {
      id: 4,
      name: 'Emma Davis',
      role: 'Project Manager',
      avatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
      workload: 60,
      assignedTasks: 4,
      storyPoints: 20,
      projectRole: 'owner',
      permissions: {
        canEdit: true,
        canDelete: true,
        canManageTeam: true,
        canManageSprints: true,
      },
    },
  ],
});

const sprints = ref<Sprint[]>([
  {
    id: 1,
    name: 'Sprint 1',
    goal: 'Setup authentication and user management',
    startDate: new Date('2024-01-08'),
    endDate: new Date('2024-01-22'),
    status: 'completed',
    capacity: 40,
    completed: 38,
    taskIds: [1, 2, 3],
  },
  {
    id: 2,
    name: 'Sprint 2',
    goal: 'Product catalog and shopping cart',
    startDate: new Date('2024-01-23'),
    endDate: new Date('2024-02-06'),
    status: 'active',
    capacity: 42,
    completed: 28,
    taskIds: [4, 5, 6],
  },
  {
    id: 3,
    name: 'Sprint 3',
    goal: 'Payment integration and checkout',
    startDate: new Date('2024-02-07'),
    endDate: new Date('2024-02-21'),
    status: 'planned',
    capacity: 45,
    completed: 0,
    taskIds: [],
  },
]);

const tasks = ref<Task[]>([
  {
    id: 1,
    name: 'Design landing page',
    description: 'Create modern landing page design',
    status: 'Done',
    priority: 'High',
    storyPoints: 8,
    assignee: 'Mike Wilson',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    dueDate: new Date('2024-02-10'),
    completed: true,
    sprintId: 2,
  },
  {
    id: 2,
    name: 'Implement authentication',
    description: 'Build login and registration flow',
    status: 'In Progress',
    priority: 'High',
    storyPoints: 13,
    assignee: 'John Smith',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    dueDate: new Date('2024-02-15'),
    completed: false,
    sprintId: 2,
  },
  {
    id: 3,
    name: 'Setup CI/CD pipeline',
    description: 'Configure automated deployment',
    status: 'To Do',
    priority: 'Medium',
    storyPoints: 5,
    assignee: 'Emma Davis',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar4.jpg',
    dueDate: new Date('2024-02-20'),
    completed: false,
    sprintId: null,
  },
  {
    id: 4,
    name: 'Product catalog page',
    description: 'Build product listing with filters',
    status: 'In Progress',
    priority: 'High',
    storyPoints: 21,
    assignee: 'John Smith',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar1.jpg',
    dueDate: new Date('2024-02-18'),
    completed: false,
    sprintId: 2,
  },
  {
    id: 5,
    name: 'Shopping cart functionality',
    description: 'Add/remove items, update quantities',
    status: 'To Do',
    priority: 'High',
    storyPoints: 13,
    assignee: 'Mike Wilson',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar3.jpg',
    dueDate: new Date('2024-02-22'),
    completed: false,
    sprintId: 2,
  },
  {
    id: 6,
    name: 'Payment integration',
    description: 'Integrate payment gateway',
    status: 'To Do',
    priority: 'Medium',
    storyPoints: 8,
    assignee: 'Sarah Johnson',
    assigneeAvatar: 'https://cdn.quasar.dev/img/avatar2.jpg',
    dueDate: new Date('2024-02-25'),
    completed: false,
    sprintId: null,
  },
]);

const newTask = ref({
  name: '',
  description: '',
  priority: 'Medium',
  storyPoints: 5,
  dueDate: '',
  assignee: null,
});

const sprintForm = ref({
  name: '',
  goal: '',
  startDate: '',
  endDate: '',
  selectedMembers: [] as TeamMember[],
});

const taskColumns = [
  { name: 'name', label: 'Task', field: 'name', align: 'left' as const, sortable: true },
  { name: 'assignee', label: 'Assignee', field: 'assignee', align: 'left' as const },
  { name: 'priority', label: 'Priority', field: 'priority', align: 'center' as const },
  { name: 'storyPoints', label: 'Story Points', field: 'storyPoints', align: 'center' as const },
  { name: 'status', label: 'Status', field: 'status', align: 'center' as const },
  {
    name: 'dueDate',
    label: 'Due Date',
    field: 'dueDate',
    align: 'center' as const,
    format: (val: Date) => format(val, 'MMM dd'),
  },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' as const },
];

const velocityData = [
  { sprint: 1, points: 32 },
  { sprint: 2, points: 38 },
  { sprint: 3, points: 35 },
  { sprint: 4, points: 42 },
];

// Computed
const recentTasks = computed(() => tasks.value.slice(0, 5));

const filteredTasks = computed(() => {
  let filtered = [...tasks.value];

  if (taskSearch.value) {
    const query = taskSearch.value.toLowerCase();
    filtered = filtered.filter(
      (t) => t.name.toLowerCase().includes(query) || t.description.toLowerCase().includes(query),
    );
  }

  if (taskStatusFilter.value !== 'All') {
    filtered = filtered.filter((t) => t.status === taskStatusFilter.value);
  }

  return filtered;
});

const taskStats = computed(() => ({
  todo: tasks.value.filter((t) => t.status === 'To Do').length,
  inProgress: tasks.value.filter((t) => t.status === 'In Progress').length,
  done: tasks.value.filter((t) => t.status === 'Done').length,
}));

const priorityStats = computed(() => ({
  high: tasks.value.filter((t) => t.priority === 'High').length,
  medium: tasks.value.filter((t) => t.priority === 'Medium').length,
  low: tasks.value.filter((t) => t.priority === 'Low').length,
}));

// Available team members to add (those not already in project)
const availableMembersToAdd = computed(() => {
  const currentMemberIds = project.value.teamMembers.map((m) => m.id);
  return globalTeamMembers.filter((m) => !currentMemberIds.includes(m.id));
});

// Methods
function navigateBack() {
  router.push('/projects');
}

function navigateToKanban() {
  router.push(`/projects/${project.value.id}/kanban`);
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
  switch (priority) {
    case 'High':
      return 'red';
    case 'Medium':
      return 'orange';
    case 'Low':
      return 'blue';
    default:
      return 'grey';
  }
}

function formatDate(date: Date): string {
  return format(date, 'MMM dd, yyyy');
}

function getSprintTotalTasks(sprintId: number): number {
  return tasks.value.filter((t) => t.sprintId === sprintId).length;
}

function getSprintCompletedTasks(sprintId: number): number {
  return tasks.value.filter((t) => t.sprintId === sprintId && t.status === 'Done').length;
}

function getSprintRemainingTasks(sprintId: number): number {
  return tasks.value.filter((t) => t.sprintId === sprintId && t.status !== 'Done').length;
}

function getSprintProgress(sprintId: number): number {
  const totalTasks = getSprintTotalTasks(sprintId);
  if (totalTasks === 0) return 0;
  const completedTasks = getSprintCompletedTasks(sprintId);
  return Math.round((completedTasks / totalTasks) * 100);
}

function toggleTaskComplete(task: Task) {
  task.completed = !task.completed;
  task.status = task.completed ? 'Done' : 'To Do';
}

function updateTaskStatus(task: Task, newStatus: string) {
  task.status = newStatus;
  task.completed = newStatus === 'Done';
  $q.notify({
    message: `Task status updated to ${newStatus}`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
}

function editTask(task: Task) {
  // Implementation for editing task
  console.log('Edit task:', task);
}

function deleteTask(task: Task) {
  const index = tasks.value.findIndex((t) => t.id === task.id);
  if (index > -1) {
    tasks.value.splice(index, 1);
    $q.notify({
      message: 'Task deleted successfully',
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
  }
}

function createTask() {
  // Validate required fields
  if (!newTask.value.name || !newTask.value.assignee) {
    $q.notify({
      message: 'Please fill in task name and assignee',
      color: 'negative',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Find assignee details
  const assigneeMember = project.value.teamMembers.find((m) => m.id === newTask.value.assignee);
  if (!assigneeMember) return;

  // Create new task
  const task: Task = {
    id: Math.max(...tasks.value.map((t) => t.id), 0) + 1,
    name: newTask.value.name,
    description: newTask.value.description,
    status: 'To Do',
    priority: newTask.value.priority,
    storyPoints: newTask.value.storyPoints,
    assignee: assigneeMember.name,
    assigneeAvatar: assigneeMember.avatar,
    dueDate: newTask.value.dueDate ? new Date(newTask.value.dueDate) : new Date(),
    completed: false,
    sprintId: null, // New tasks go to backlog by default
  };

  tasks.value.push(task);

  $q.notify({
    message: `Task "${task.name}" created successfully`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });

  // Reset form and close dialog
  newTask.value = {
    name: '',
    description: '',
    priority: 'Medium',
    storyPoints: 5,
    dueDate: '',
    assignee: null,
  };
  showNewTaskDialog.value = false;
}

// Sprint management functions
const activeSprint = computed(() => sprints.value.find((s) => s.status === 'active'));
const plannedSprints = computed(() => sprints.value.filter((s) => s.status === 'planned'));
const completedSprints = computed(() => sprints.value.filter((s) => s.status === 'completed'));

// Task management
const sprintTasks = computed(() =>
  tasks.value.filter((t) => t.sprintId === activeSprint.value?.id),
);
const backlogTasks = computed(() => tasks.value.filter((t) => !t.sprintId));

function getMemberSprintTasks(memberId: number) {
  const member = project.value.teamMembers.find((m) => m.id === memberId);
  if (!member) return [];
  return sprintTasks.value.filter((t) => t.assignee === member.name);
}

function getMemberSprintStoryPoints(memberId: number) {
  return getMemberSprintTasks(memberId).reduce((sum, t) => sum + t.storyPoints, 0);
}

function toggleTaskStatus(task: Task) {
  task.status = task.status === 'Done' ? 'In Progress' : 'Done';
  $q.notify({
    message: `Task ${task.status === 'Done' ? 'completed' : 'reopened'}`,
    color: 'positive',
    icon: task.status === 'Done' ? 'check_circle' : 'replay',
    position: 'top',
  });
}

function getStatusColorForChip(status: string): string {
  switch (status) {
    case 'Done':
      return 'green';
    case 'In Progress':
      return 'blue';
    case 'To Do':
      return 'grey';
    default:
      return 'grey';
  }
}

function editSprint(sprint: Sprint) {
  // Load sprint data into form
  sprintForm.value = {
    name: sprint.name,
    goal: sprint.goal,
    startDate: format(sprint.startDate, 'yyyy-MM-dd'),
    endDate: format(sprint.endDate, 'yyyy-MM-dd'),
    selectedMembers: [...project.value.teamMembers], // For now, load all team members
  };

  // Store the sprint being edited
  editingSprintId.value = sprint.id;

  // Open dialog
  showNewSprintDialog.value = true;
}

function startSprint(sprint: Sprint) {
  sprint.status = 'active';
  $q.notify({
    message: `Sprint "${sprint.name}" started`,
    color: 'positive',
    icon: 'play_arrow',
    position: 'top',
  });
}

function completeSprint(sprint: Sprint) {
  sprint.status = 'completed';
  $q.notify({
    message: `Sprint "${sprint.name}" completed`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });
}

function deleteSprint(sprint: Sprint) {
  const index = sprints.value.findIndex((s) => s.id === sprint.id);
  if (index > -1) {
    sprints.value.splice(index, 1);
    $q.notify({
      message: 'Sprint deleted',
      color: 'positive',
      icon: 'delete',
      position: 'top',
    });
  }
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
  selectedRole.value = member.projectRole;
  showChangeRoleDialog.value = true;
}

function saveRoleChange() {
  if (!memberToChangeRole.value) return;

  const memberIndex = project.value.teamMembers.findIndex(
    (m) => m.id === memberToChangeRole.value!.id,
  );

  if (memberIndex > -1) {
    const member = project.value.teamMembers[memberIndex]!;
    member.projectRole = selectedRole.value;
    member.permissions = getRolePermissions(selectedRole.value);

    $q.notify({
      message: `${memberToChangeRole.value.name}'s role changed to ${selectedRole.value.toUpperCase()}`,
      color: 'positive',
      icon: 'check_circle',
      position: 'top',
    });
  }

  showChangeRoleDialog.value = false;
  cancelChangeRole();
}

function cancelChangeRole() {
  memberToChangeRole.value = null;
  selectedRole.value = 'member';
}

function removeMember(member: TeamMember) {
  const index = project.value.teamMembers.findIndex((m) => m.id === member.id);
  if (index > -1) {
    project.value.teamMembers.splice(index, 1);
    $q.notify({
      message: `${member.name} removed from project`,
      color: 'positive',
      icon: 'person_remove',
      position: 'top',
    });
  }
}

// Sprint Planning functions
function getMemberOtherProjectsStoryPoints(memberId: number): number {
  // Mock: Calculate story points from other projects' active sprints
  // In real app, this would query all projects where member is assigned
  // based on memberId parameter

  // Mock data - different workload per member
  const memberWorkloads: Record<number, { projectId: number; storyPoints: number }[]> = {
    1: [
      { projectId: 2, storyPoints: 8 },
      { projectId: 3, storyPoints: 5 },
    ],
    2: [{ projectId: 2, storyPoints: 12 }],
    3: [{ projectId: 3, storyPoints: 3 }],
    4: [{ projectId: 2, storyPoints: 5 }],
  };

  const currentProjectId = project.value.id;
  const workload = memberWorkloads[memberId] || [];

  return workload
    .filter((w) => w.projectId !== currentProjectId)
    .reduce((sum, w) => sum + w.storyPoints, 0);
}

function getMemberWorkloadOnOtherProjects(memberId: number): number {
  const storyPoints = getMemberOtherProjectsStoryPoints(memberId);
  return Math.round((storyPoints / 20) * 100);
}

function getMemberAvailableCapacity(memberId: number): number {
  const usedCapacity = getMemberOtherProjectsStoryPoints(memberId);
  return Math.max(0, 20 - usedCapacity);
}

function getWorkloadColor(workload: number): string {
  if (workload > 80) return 'red';
  if (workload > 60) return 'orange';
  return 'green';
}

const totalTeamCapacity = computed(() => {
  return sprintForm.value.selectedMembers.reduce((sum, member) => {
    return sum + getMemberAvailableCapacity(member.id);
  }, 0);
});

const isSprintFormValid = computed(() => {
  return (
    sprintForm.value.name &&
    sprintForm.value.goal &&
    sprintForm.value.startDate &&
    sprintForm.value.endDate &&
    sprintForm.value.selectedMembers.length > 0
  );
});

function addMemberToProject() {
  if (!selectedMemberToAdd.value) return;

  const memberToAdd = globalTeamMembers.find((m) => m.id === selectedMemberToAdd.value);
  if (!memberToAdd) return;

  // Check if member is already in project
  if (project.value.teamMembers.some((m) => m.id === memberToAdd.id)) {
    $q.notify({
      message: 'This member is already in the project',
      color: 'warning',
      icon: 'warning',
      position: 'top',
    });
    return;
  }

  // Add member with selected role
  const newMember: TeamMember = {
    ...memberToAdd,
    projectRole: newMemberRole.value,
    workload: 0,
    assignedTasks: 0,
    storyPoints: 0,
    permissions: getRolePermissions(newMemberRole.value),
  };

  project.value.teamMembers.push(newMember);

  $q.notify({
    message: `${newMember.name} added to project successfully!`,
    color: 'positive',
    icon: 'check_circle',
    position: 'top',
  });

  showAddMemberDialog.value = false;
  cancelAddMember();
}

function cancelAddMember() {
  selectedMemberToAdd.value = null;
  newMemberRole.value = 'member';
}

function getRolePermissions(role: string) {
  switch (role) {
    case 'admin':
      return {
        canEdit: true,
        canDelete: true,
        canManageTeam: true,
        canManageSprints: true,
      };
    case 'member':
      return {
        canEdit: true,
        canDelete: false,
        canManageTeam: false,
        canManageSprints: false,
      };
    case 'viewer':
      return {
        canEdit: false,
        canDelete: false,
        canManageTeam: false,
        canManageSprints: false,
      };
    default:
      return {
        canEdit: true,
        canDelete: false,
        canManageTeam: false,
        canManageSprints: false,
      };
  }
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
    const sprintIndex = sprints.value.findIndex((s) => s.id === editingSprintId.value);
    if (sprintIndex > -1) {
      const existingSprint = sprints.value[sprintIndex]!;
      sprints.value[sprintIndex] = {
        id: existingSprint.id,
        name: sprintForm.value.name,
        goal: sprintForm.value.goal,
        startDate: new Date(sprintForm.value.startDate),
        endDate: new Date(sprintForm.value.endDate),
        status: existingSprint.status,
        capacity: totalTeamCapacity.value,
        completed: existingSprint.completed,
        taskIds: existingSprint.taskIds,
      };

      $q.notify({
        message: `Sprint "${sprintForm.value.name}" updated successfully!`,
        color: 'positive',
        icon: 'check_circle',
        position: 'top',
      });
    }
  } else {
    // Create new sprint
    const newSprint: Sprint = {
      id: Math.max(...sprints.value.map((s) => s.id), 0) + 1,
      name: sprintForm.value.name,
      goal: sprintForm.value.goal,
      startDate: new Date(sprintForm.value.startDate),
      endDate: new Date(sprintForm.value.endDate),
      status: 'planned',
      capacity: totalTeamCapacity.value,
      completed: 0,
      taskIds: [],
    };

    sprints.value.push(newSprint);

    $q.notify({
      message: `Sprint "${newSprint.name}" created successfully!`,
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
    selectedMembers: [],
  };
  editingSprintId.value = null;
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
</style>
