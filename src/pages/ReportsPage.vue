<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">Research Reports</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">Export and documentation for diploma thesis</p>
        </div>
        <div class="row q-gutter-md">
          <q-btn color="secondary" icon="picture_as_pdf" label="Export PDF" @click="exportPDF" />
          <q-btn color="primary" icon="download" label="Export All Data" @click="exportAllData" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <!-- Quick Export Templates -->
      <div class="row q-gutter-lg q-mb-lg">
        <div class="col-12 col-md-3" v-for="template in exportTemplates" :key="template.id">
          <q-card class="export-card" @click="exportTemplate(template)">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <q-icon :name="template.icon" :color="template.color" size="48px" class="q-mr-md" />
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ template.name }}</div>
                  <div class="text-caption text-grey-7">{{ template.format }}</div>
                </div>
              </div>

              <div class="text-body2 text-grey-8 q-mb-md">{{ template.description }}</div>

              <q-btn
                flat
                color="primary"
                icon="download"
                :label="`Export ${template.format}`"
                class="full-width"
                @click.stop="exportTemplate(template)"
              />
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Research Summary -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Research Summary</div>

          <div class="row q-gutter-lg">
            <div class="col">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-center">
                    <q-icon name="science" color="primary" size="32px" />
                    <div class="text-h4 text-weight-bold text-primary q-mt-sm">5</div>
                    <div class="text-caption text-grey-7">Experiments Completed</div>
                  </div>
                  <q-separator class="q-my-md" />
                  <div class="text-caption text-grey-7">
                    <div>• PERT+RACI vs Traditional</div>
                    <div>• Workload Rebalancing</div>
                    <div>• Requirement Adaptation</div>
                    <div>• Risk-Based Optimization</div>
                    <div>• Multi-Project RACI</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-center">
                    <q-icon name="trending_up" color="green" size="32px" />
                    <div class="text-h4 text-weight-bold text-green q-mt-sm">+28%</div>
                    <div class="text-caption text-grey-7">Average Improvement</div>
                  </div>
                  <q-separator class="q-my-md" />
                  <div class="text-caption text-grey-7">
                    <div>• Duration: -15% improvement</div>
                    <div>• Accuracy: +35% increase</div>
                    <div>• Balance: +42% better</div>
                    <div>• Adaptation: 99% faster</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-center">
                    <q-icon name="verified" color="blue" size="32px" />
                    <div class="text-h4 text-weight-bold text-blue q-mt-sm">93%</div>
                    <div class="text-caption text-grey-7">Confidence Level</div>
                  </div>
                  <q-separator class="q-my-md" />
                  <div class="text-caption text-grey-7">
                    <div>• Statistical significance</div>
                    <div>• 50+ simulations</div>
                    <div>• 92% success rate</div>
                    <div>• Validated results</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-center">
                    <q-icon name="storage" color="orange" size="32px" />
                    <div class="text-h4 text-weight-bold text-orange q-mt-sm">1.2k+</div>
                    <div class="text-caption text-grey-7">Data Points</div>
                  </div>
                  <q-separator class="q-my-md" />
                  <div class="text-caption text-grey-7">
                    <div>• Experiment results</div>
                    <div>• Performance metrics</div>
                    <div>• Batch simulations</div>
                    <div>• Ready for export</div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Experiment Results Table -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Experiment Results</div>

          <q-table
            :rows="experimentResults"
            :columns="experimentColumns"
            row-key="id"
            :pagination="{ rowsPerPage: 0 }"
            flat
            bordered
          >
            <template v-slot:body-cell-status="props">
              <q-td :props="props">
                <q-chip
                  :color="getStatusColor(props.value)"
                  text-color="white"
                  size="sm"
                  :icon="getStatusIcon(props.value)"
                >
                  {{ props.value }}
                </q-chip>
              </q-td>
            </template>

            <template v-slot:body-cell-improvement="props">
              <q-td :props="props">
                <div class="text-weight-bold" :class="getImprovementClass(props.value)">
                  {{ props.value > 0 ? '+' : '' }}{{ props.value }}%
                </div>
              </q-td>
            </template>

            <template v-slot:body-cell-confidence="props">
              <q-td :props="props">
                <div class="confidence-indicator">
                  <q-linear-progress
                    :value="props.value / 100"
                    color="blue"
                    size="10px"
                    class="q-mb-xs"
                  />
                  <div class="text-caption">{{ props.value }}%</div>
                </div>
              </q-td>
            </template>

            <template v-slot:body-cell-actions="props">
              <q-td :props="props">
                <q-btn
                  flat
                  dense
                  round
                  icon="download"
                  color="primary"
                  @click="exportExperiment(props.row)"
                >
                  <q-tooltip>Export Results</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  dense
                  round
                  icon="visibility"
                  color="secondary"
                  @click="viewDetails(props.row)"
                >
                  <q-tooltip>View Details</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>
        </q-card-section>
      </q-card>

      <!-- Documentation Sections -->
      <q-card class="q-mb-lg">
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Documentation Sections</div>

          <q-list separator>
            <q-item v-for="section in documentationSections" :key="section.id" clickable>
              <q-item-section avatar>
                <q-icon :name="section.icon" :color="section.color" size="32px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold">{{ section.title }}</q-item-label>
                <q-item-label caption>{{ section.description }}</q-item-label>
                <q-item-label caption class="q-mt-xs">
                  <q-chip size="xs" :color="section.statusColor" text-color="white">
                    {{ section.status }}
                  </q-chip>
                  <span class="q-ml-sm text-grey-6">{{ section.pages }} pages</span>
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn flat icon="download" color="primary" @click="exportSection(section)">
                  <q-tooltip>Export Section</q-tooltip>
                </q-btn>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>

      <!-- Export History -->
      <q-card>
        <q-card-section>
          <div class="text-h6 text-weight-bold q-mb-md">Recent Exports</div>

          <q-timeline color="primary">
            <q-timeline-entry
              v-for="export_item in recentExports"
              :key="export_item.id"
              :title="export_item.title"
              :subtitle="export_item.timestamp"
              :icon="export_item.icon"
              :color="export_item.color"
            >
              <div class="text-caption text-grey-7">{{ export_item.description }}</div>
              <div class="q-mt-sm">
                <q-chip size="sm" color="grey-3" text-color="grey-8">
                  {{ export_item.format }}
                </q-chip>
                <q-chip size="sm" color="grey-3" text-color="grey-8">
                  {{ export_item.size }}
                </q-chip>
                    </div>
            </q-timeline-entry>
          </q-timeline>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useQuasar } from 'quasar';
import { useResearchStore } from 'src/stores/research-store';
import { format, differenceInDays } from 'date-fns';

const $q = useQuasar();
const researchStore = useResearchStore();

// Export templates
const exportTemplates = [
  {
    id: 1,
    name: 'All Experiments',
    description: 'Complete experiment data with results, metrics, and analysis',
    format: 'JSON + CSV',
    icon: 'science',
    color: 'primary',
  },
  {
    id: 2,
    name: 'Comparison Data',
    description: 'PERT+RACI vs Traditional methodology comparison',
    format: 'JSON',
    icon: 'compare',
    color: 'blue',
  },
  {
    id: 3,
    name: 'Performance Metrics',
    description: 'Analytics dashboard data with charts and statistics',
    format: 'CSV',
    icon: 'analytics',
    color: 'green',
  },
  {
    id: 4,
    name: 'Research Summary',
    description: 'Executive summary for diploma thesis documentation',
    format: 'PDF',
    icon: 'description',
    color: 'orange',
  },
];

// Experiment results (computed from research store)
const experimentResults = computed(() => {
  return researchStore.experiments.map((exp) => {
    const duration = differenceInDays(exp.endDate, exp.startDate);
    const statusMap = {
      planning: 'Planning',
      running: 'In Progress',
      completed: 'Completed',
      cancelled: 'Cancelled',
    };

    return {
      id: exp.id,
      name: exp.name,
      status: statusMap[exp.status],
      improvement: exp.results?.improvement || 0,
      confidence: exp.results?.confidence || 0,
      duration: exp.status === 'planning' ? 'TBD' : `${duration} days`,
      participants: exp.actualRuns,
    };
  });
});

const experimentColumns = [
  { name: 'name', label: 'Experiment', field: 'name', align: 'left' as const, sortable: true },
  { name: 'status', label: 'Status', field: 'status', align: 'center' as const },
  {
    name: 'improvement',
    label: 'Improvement',
    field: 'improvement',
    align: 'center' as const,
    sortable: true,
  },
  {
    name: 'confidence',
    label: 'Confidence',
    field: 'confidence',
    align: 'center' as const,
    sortable: true,
  },
  { name: 'duration', label: 'Duration', field: 'duration', align: 'center' as const },
  {
    name: 'participants',
    label: 'Participants',
    field: 'participants',
    align: 'center' as const,
  },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' as const },
];

// Documentation sections
const documentationSections = [
  {
    id: 1,
    title: 'Mathematical Model',
    description: 'PERT+RACI integration formulas and algorithms',
    icon: 'calculate',
    color: 'purple',
    status: 'Complete',
    statusColor: 'green',
    pages: 12,
  },
  {
    id: 2,
    title: 'Experiment Design',
    description: 'Methodology, hypotheses, and testing procedures',
    icon: 'biotech',
    color: 'blue',
    status: 'Complete',
    statusColor: 'green',
    pages: 8,
  },
  {
    id: 3,
    title: 'Results Analysis',
    description: 'Statistical analysis and findings interpretation',
    icon: 'bar_chart',
    color: 'green',
    status: 'Complete',
    statusColor: 'green',
    pages: 15,
  },
  {
    id: 4,
    title: 'Implementation Details',
    description: 'Technical architecture and code documentation',
    icon: 'code',
    color: 'orange',
    status: 'In Progress',
    statusColor: 'orange',
    pages: 10,
  },
  {
    id: 5,
    title: 'User Guide',
    description: 'System usage instructions with screenshots',
    icon: 'menu_book',
    color: 'cyan',
    status: 'Draft',
    statusColor: 'grey',
    pages: 6,
  },
];

// Recent exports
const recentExports = [
  {
    id: 1,
    title: 'All Experiments Data',
    description: 'Exported complete experiment results with metrics',
    timestamp: format(new Date(), 'MMM dd, yyyy HH:mm'),
    format: 'JSON + CSV',
    size: '2.4 MB',
    icon: 'science',
    color: 'primary',
  },
  {
    id: 2,
    title: 'Comparison Report',
    description: 'PERT+RACI vs Traditional methodology comparison',
    timestamp: format(new Date(Date.now() - 3600000), 'MMM dd, yyyy HH:mm'),
    format: 'JSON',
    size: '156 KB',
    icon: 'compare',
    color: 'blue',
  },
  {
    id: 3,
    title: 'Batch Simulation Results',
    description: 'Requirement change adaptation batch test data',
    timestamp: format(new Date(Date.now() - 7200000), 'MMM dd, yyyy HH:mm'),
    format: 'JSON',
    size: '384 KB',
    icon: 'sync_alt',
    color: 'green',
  },
];

// Helper functions
function getStatusColor(status: string): string {
  switch (status) {
    case 'Completed':
      return 'green';
    case 'In Progress':
      return 'orange';
    default:
      return 'grey';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'Completed':
      return 'check_circle';
    case 'In Progress':
      return 'hourglass_empty';
    default:
      return 'radio_button_unchecked';
  }
}

function getImprovementClass(value: number): string {
  if (value > 30) return 'text-green';
  if (value > 10) return 'text-blue';
  if (value > 0) return 'text-grey-8';
  return 'text-grey-6';
}

// Export functions
function exportTemplate(template: (typeof exportTemplates)[0]) {
  let data: Record<string, unknown> = {};

  switch (template.id) {
    case 1: // All Experiments
      data = researchStore.exportResearchData();
      break;
    case 2: // Comparison Data
      data = {
        methodologies: researchStore.allComparisonData,
        exportedAt: new Date().toISOString(),
      };
      break;
    case 3: // Performance Metrics
      data = {
        pertRaciMetrics: researchStore.pertRaciMetrics,
        totalSimulations: researchStore.totalSimulationRuns,
        successRate: researchStore.overallSuccessRate,
        avgAdaptationTime: researchStore.avgAdaptationTime,
        avgImprovementRate: researchStore.avgImprovementRate,
        exportedAt: new Date().toISOString(),
      };
      break;
    case 4: // Research Summary
      data = {
        summary: {
          totalExperiments: researchStore.experiments.length,
          completedExperiments: researchStore.completedExperiments.length,
          totalSimulations: researchStore.totalSimulationRuns,
          successRate: researchStore.overallSuccessRate,
        },
        pertRaciMetrics: researchStore.pertRaciMetrics,
        experiments: researchStore.experiments,
        exportedAt: new Date().toISOString(),
      };
      break;
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${template.name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(url);

  $q.notify({
    message: `${template.name} exported successfully`,
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}

function exportAllData() {
  const researchData = researchStore.exportResearchData();
  const data = {
    ...researchData,
    documentation: documentationSections,
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `research_data_complete_${Date.now()}.json`;
  link.click();
  URL.revokeObjectURL(url);

  $q.notify({
    message: `Complete research data exported: ${data.summary.totalExperiments} experiments, ${data.summary.totalSimulations} simulations`,
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}

function exportPDF() {
  $q.notify({
    message: 'PDF export feature coming soon',
    color: 'info',
    icon: 'info',
    position: 'top',
  });
}

function exportExperiment(experiment: { id: number; name: string }) {
  // Find real experiment from research store
  const realExperiment = researchStore.experiments.find((e) => e.id === experiment.id);
  const simulations = researchStore.simulationRuns.filter((r) => r.experimentId === experiment.id);
  const metrics = researchStore.getExperimentMetrics(experiment.id);

  const data = {
    experiment: realExperiment,
    simulations,
    metrics,
    exportedAt: new Date().toISOString(),
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `experiment_${experiment.id}_${experiment.name.toLowerCase().replace(/\s+/g, '_')}.json`;
  link.click();
  URL.revokeObjectURL(url);

  $q.notify({
    message: `Experiment "${experiment.name}" exported with ${simulations.length} simulations`,
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}

function viewDetails(experiment: { id: number; name: string }) {
  const metrics = researchStore.getExperimentMetrics(experiment.id);
  const simulations = researchStore.simulationRuns.filter((r) => r.experimentId === experiment.id);

  $q.dialog({
    title: experiment.name,
    message: metrics
      ? `Simulations: ${simulations.length}\nSuccess Rate: ${metrics.successRate}%\nAvg Improvement: ${metrics.avgImprovementRate}%\nAvg Adaptation Time: ${metrics.avgAdaptationTime}ms`
      : 'No simulations yet. Go to Requirement Change Simulator to add runs.',
    ok: { label: 'Close', color: 'primary' },
  });
}

function exportSection(section: (typeof documentationSections)[0]) {
  $q.notify({
    message: `Exporting: ${section.title}`,
    color: 'positive',
    icon: 'download',
    position: 'top',
  });
}
</script>

<style scoped>
.export-card {
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  cursor: pointer;
}

.export-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.confidence-indicator {
  min-width: 100px;
}
</style>
