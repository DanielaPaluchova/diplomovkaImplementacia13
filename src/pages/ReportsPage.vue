<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Reports</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Generate and manage project reports</p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="schedule"
            label="Schedule Report"
            @click="showScheduleDialog = true"
          />
          <q-btn
            color="primary"
            icon="add"
            label="Generate Report"
            @click="showGenerateDialog = true"
          />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Report Templates -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-4" v-for="template in reportTemplates" :key="template.id">
          <q-card class="report-template-card" @click="generateFromTemplate(template)">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon :name="template.icon" :color="template.color" size="32px" class="q-mr-sm" />
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ template.name }}</div>
                  <div class="text-caption text-grey-7">{{ template.category }}</div>
                </div>
              </div>

              <div class="text-body2 text-grey-7 q-mb-md">{{ template.description }}</div>

              <div class="row items-center">
                <q-chip size="sm" color="grey-3" text-color="grey-8" :label="template.format" />
                <q-space />
                <div class="text-caption text-grey-6">{{ template.estimatedTime }}</div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Recent Reports -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Recent Reports</div>

          <q-table
            :rows="recentReports"
            :columns="reportsColumns"
            row-key="id"
            :pagination="{ rowsPerPage: 10 }"
          >
            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-chip
                  :color="getStatusColor(props.value)"
                  text-color="white"
                  size="sm"
                  :icon="getStatusIcon(props.value)"
                  :label="props.value"
                />
              </q-td>
            </template>

            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn
                  flat
                  round
                  dense
                  icon="download"
                  color="primary"
                  @click="downloadReport(props.row)"
                  :disable="props.row.status !== 'Completed'"
                >
                  <q-tooltip>Download Report</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  dense
                  icon="visibility"
                  color="secondary"
                  @click="previewReport(props.row)"
                  :disable="props.row.status !== 'Completed'"
                >
                  <q-tooltip>Preview Report</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  dense
                  icon="share"
                  color="orange"
                  @click="shareReport(props.row)"
                  :disable="props.row.status !== 'Completed'"
                >
                  <q-tooltip>Share Report</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- Report Statistics -->
      <div class="row q-gutter-lg">
        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Report Statistics</div>

              <div class="stats-grid">
                <div class="stat-item">
                  <div class="text-h4 text-weight-bold text-primary">
                    {{ reportStats.totalGenerated }}
                  </div>
                  <div class="text-caption text-grey-7">Total Generated</div>
                </div>
                <div class="stat-item">
                  <div class="text-h4 text-weight-bold text-green">{{ reportStats.thisMonth }}</div>
                  <div class="text-caption text-grey-7">This Month</div>
                </div>
                <div class="stat-item">
                  <div class="text-h4 text-weight-bold text-orange">
                    {{ reportStats.scheduled }}
                  </div>
                  <div class="text-caption text-grey-7">Scheduled</div>
                </div>
                <div class="stat-item">
                  <div class="text-h4 text-weight-bold text-blue">{{ reportStats.avgTime }}</div>
                  <div class="text-caption text-grey-7">Avg. Generation Time</div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <div class="col-12 col-md-6">
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Popular Report Types</div>

              <div class="popular-reports">
                <div
                  v-for="report in popularReports"
                  :key="report.type"
                  class="popular-item q-mb-md"
                >
                  <div class="row items-center">
                    <q-icon :name="report.icon" :color="report.color" class="q-mr-sm" />
                    <div class="col">
                      <div class="text-weight-medium">{{ report.name }}</div>
                      <div class="text-caption text-grey-7">{{ report.count }} generated</div>
                    </div>
                    <div class="col-auto">
                      <q-linear-progress
                        :value="report.count / reportStats.totalGenerated"
                        :color="report.color"
                        style="width: 60px; height: 6px"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Generate Report Dialog -->
    <q-dialog v-model="showGenerateDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Generate Custom Report</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newReport.title"
            label="Report Title"
            filled
            class="q-mb-md"
            :rules="[(val) => !!val || 'Title is required']"
          />

          <q-select
            v-model="newReport.type"
            :options="reportTypeOptions"
            label="Report Type"
            filled
            class="q-mb-md"
          />

          <q-select
            v-model="newReport.projects"
            :options="projectOptions"
            label="Projects"
            multiple
            use-chips
            filled
            class="q-mb-md"
          />

          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-input
                v-model="newReport.startDate"
                label="Start Date"
                filled
                mask="date"
                :rules="['date']"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="newReport.startDate">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
            <div class="col">
              <q-input
                v-model="newReport.endDate"
                label="End Date"
                filled
                mask="date"
                :rules="['date']"
              >
                <template v-slot:append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date v-model="newReport.endDate">
                        <div class="row items-center justify-end">
                          <q-btn v-close-popup label="Close" color="primary" flat />
                        </div>
                      </q-date>
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>
          </div>

          <q-select
            v-model="newReport.format"
            :options="formatOptions"
            label="Export Format"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelGenerateReport" />
          <q-btn
            color="primary"
            label="Generate"
            @click="generateReport"
            :disable="!newReport.title"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Schedule Report Dialog -->
    <q-dialog v-model="showScheduleDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Schedule Recurring Report</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-select
            v-model="scheduledReport.template"
            :options="templateOptions"
            label="Report Template"
            filled
            class="q-mb-md"
          />

          <q-select
            v-model="scheduledReport.frequency"
            :options="frequencyOptions"
            label="Frequency"
            filled
            class="q-mb-md"
          />

          <q-input
            v-model="scheduledReport.recipients"
            label="Email Recipients (comma separated)"
            filled
            class="q-mb-md"
          />

          <q-input
            v-model="scheduledReport.nextRun"
            label="Next Run Date"
            filled
            mask="date"
            :rules="['date']"
          >
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                  <q-date v-model="scheduledReport.nextRun">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" @click="cancelScheduleReport" />
          <q-btn
            color="primary"
            label="Schedule"
            @click="scheduleReport"
            :disable="!scheduledReport.template"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';
import { format } from 'date-fns';

const mockDataStore = useMockDataStore();

// Reactive data
const showGenerateDialog = ref(false);
const showScheduleDialog = ref(false);

const reportTemplates = ref([
  {
    id: 1,
    name: 'Project Status Report',
    category: 'Management',
    description: 'Comprehensive overview of all project statuses, progress, and key metrics',
    icon: 'assessment',
    color: 'primary',
    format: 'PDF',
    estimatedTime: '2-3 minutes',
  },
  {
    id: 2,
    name: 'Team Performance Report',
    category: 'HR',
    description: 'Detailed analysis of team member performance and productivity metrics',
    icon: 'group',
    color: 'green',
    format: 'Excel',
    estimatedTime: '3-4 minutes',
  },
  {
    id: 3,
    name: 'Budget Analysis Report',
    category: 'Finance',
    description: 'Financial breakdown of project costs, budget utilization, and forecasts',
    icon: 'euro',
    color: 'orange',
    format: 'PDF',
    estimatedTime: '1-2 minutes',
  },
  {
    id: 4,
    name: 'Risk Assessment Report',
    category: 'Risk Management',
    description: 'Comprehensive risk analysis with mitigation strategies and recommendations',
    icon: 'warning',
    color: 'red',
    format: 'PDF',
    estimatedTime: '4-5 minutes',
  },
  {
    id: 5,
    name: 'Sprint Summary Report',
    category: 'Agile',
    description: 'Sprint performance, velocity tracking, and burndown analysis',
    icon: 'timeline',
    color: 'blue',
    format: 'PDF',
    estimatedTime: '1-2 minutes',
  },
  {
    id: 6,
    name: 'Quality Metrics Report',
    category: 'QA',
    description: 'Code quality, testing coverage, and defect analysis report',
    icon: 'verified',
    color: 'purple',
    format: 'Excel',
    estimatedTime: '2-3 minutes',
  },
]);

const recentReports = ref([
  {
    id: 1,
    title: 'Monthly Project Status - December 2024',
    type: 'Project Status',
    createdBy: 'Lisa Rodriguez',
    createdAt: '2024-12-15',
    status: 'Completed',
    format: 'PDF',
    size: '2.4 MB',
  },
  {
    id: 2,
    title: 'Q4 Team Performance Analysis',
    type: 'Team Performance',
    createdBy: 'John Smith',
    createdAt: '2024-12-14',
    status: 'Completed',
    format: 'Excel',
    size: '1.8 MB',
  },
  {
    id: 3,
    title: 'Sprint 12 Summary Report',
    type: 'Sprint Summary',
    createdBy: 'Sarah Johnson',
    createdAt: '2024-12-13',
    status: 'Processing',
    format: 'PDF',
    size: '-',
  },
  {
    id: 4,
    title: 'Risk Assessment - E-commerce Project',
    type: 'Risk Assessment',
    createdBy: 'Mike Wilson',
    createdAt: '2024-12-12',
    status: 'Completed',
    format: 'PDF',
    size: '3.1 MB',
  },
]);

const newReport = reactive({
  title: '',
  type: '',
  projects: [],
  startDate: format(new Date(), 'yyyy/MM/dd'),
  endDate: format(new Date(), 'yyyy/MM/dd'),
  format: 'PDF',
});

const scheduledReport = reactive({
  template: '',
  frequency: '',
  recipients: '',
  nextRun: format(new Date(), 'yyyy/MM/dd'),
});

const reportStats = ref({
  totalGenerated: 156,
  thisMonth: 23,
  scheduled: 8,
  avgTime: '2.5 min',
});

const popularReports = ref([
  {
    type: 'project-status',
    name: 'Project Status',
    count: 45,
    icon: 'assessment',
    color: 'primary',
  },
  { type: 'team-performance', name: 'Team Performance', count: 32, icon: 'group', color: 'green' },
  { type: 'budget-analysis', name: 'Budget Analysis', count: 28, icon: 'euro', color: 'orange' },
  { type: 'risk-assessment', name: 'Risk Assessment', count: 21, icon: 'warning', color: 'red' },
  { type: 'sprint-summary', name: 'Sprint Summary', count: 18, icon: 'timeline', color: 'blue' },
]);

const reportsColumns = [
  { name: 'title', label: 'Report Title', field: 'title', align: 'left' as const, sortable: true },
  { name: 'type', label: 'Type', field: 'type', align: 'left' as const },
  { name: 'createdBy', label: 'Created By', field: 'createdBy', align: 'left' as const },
  {
    name: 'createdAt',
    label: 'Created',
    field: 'createdAt',
    align: 'left' as const,
    sortable: true,
  },
  { name: 'status', label: 'Status', field: 'status', align: 'center' as const },
  { name: 'format', label: 'Format', field: 'format', align: 'center' as const },
  { name: 'size', label: 'Size', field: 'size', align: 'center' as const },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' as const },
];

const reportTypeOptions = [
  'Project Status',
  'Team Performance',
  'Budget Analysis',
  'Risk Assessment',
  'Sprint Summary',
  'Quality Metrics',
];
const projectOptions = [
  'E-commerce Platform',
  'Mobile App',
  'Data Migration',
  'AI Chatbot',
  'Security Audit',
];
const formatOptions = ['PDF', 'Excel', 'CSV', 'PowerPoint'];
const templateOptions = reportTemplates.value.map((t) => ({ label: t.name, value: t.id }));
const frequencyOptions = ['Daily', 'Weekly', 'Monthly', 'Quarterly'];

// Methods
function generateFromTemplate(template: { name: string }) {
  console.log('Generating report from template:', template.name);
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'Completed':
      return 'green';
    case 'Processing':
      return 'orange';
    case 'Failed':
      return 'red';
    default:
      return 'grey';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'Completed':
      return 'check_circle';
    case 'Processing':
      return 'schedule';
    case 'Failed':
      return 'error';
    default:
      return 'help';
  }
}

function downloadReport(report: { title: string }) {
  console.log('Downloading report:', report.title);
}

function previewReport(report: { title: string }) {
  console.log('Previewing report:', report.title);
}

function shareReport(report: { title: string }) {
  console.log('Sharing report:', report.title);
}

function generateReport() {
  console.log('Generating custom report:', newReport);
  cancelGenerateReport();
}

function cancelGenerateReport() {
  showGenerateDialog.value = false;
  Object.assign(newReport, {
    title: '',
    type: '',
    projects: [],
    startDate: format(new Date(), 'yyyy/MM/dd'),
    endDate: format(new Date(), 'yyyy/MM/dd'),
    format: 'PDF',
  });
}

function scheduleReport() {
  console.log('Scheduling report:', scheduledReport);
  cancelScheduleReport();
}

function cancelScheduleReport() {
  showScheduleDialog.value = false;
  Object.assign(scheduledReport, {
    template: '',
    frequency: '',
    recipients: '',
    nextRun: format(new Date(), 'yyyy/MM/dd'),
  });
}

onMounted(() => {
  mockDataStore.initializeData();
});
</script>

<style scoped>
.report-template-card {
  transition: all 0.2s ease;
  cursor: pointer;
  height: 100%;
}

.report-template-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.popular-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}
</style>
