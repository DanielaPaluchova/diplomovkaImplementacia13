<template>
  <q-page class="bg-grey-1">
    <!-- Header -->
    <div class="bg-white q-pa-lg shadow-1">
      <div class="row items-center justify-between">
        <div>
          <h4 class="text-h4 text-weight-bold text-primary q-ma-none">AI Assistant</h4>
          <p class="text-grey-7 q-ma-none q-mt-sm">
            Intelligent project management assistant powered by AI
          </p>
        </div>
        <div class="row q-gutter-md">
          <q-btn
            color="secondary"
            icon="history"
            label="Chat History"
            @click="showHistoryDialog = true"
          />
          <q-btn color="primary" icon="add_comment" label="New Chat" @click="startNewChat" />
        </div>
      </div>
    </div>

    <div class="q-pa-lg">
      <div class="row q-gutter-lg">
        <!-- Chat Interface -->
        <div class="col-12 col-lg-8">
          <q-card class="chat-card">
            <q-card-section class="chat-header bg-primary text-white">
              <div class="row items-center">
                <q-avatar size="32px" class="q-mr-sm">
                  <q-icon name="smart_toy" />
                </q-avatar>
                <div class="col">
                  <div class="text-weight-bold">ProjectFlow AI Assistant</div>
                  <div class="text-caption">{{ aiStatus }}</div>
                </div>
                <q-btn flat round icon="more_vert" @click="showChatMenu = !showChatMenu">
                  <q-menu v-model="showChatMenu">
                    <q-list>
                      <q-item clickable @click="clearChat">
                        <q-item-section avatar>
                          <q-icon name="clear_all" />
                        </q-item-section>
                        <q-item-section>Clear Chat</q-item-section>
                      </q-item>
                      <q-item clickable @click="exportChat">
                        <q-item-section avatar>
                          <q-icon name="download" />
                        </q-item-section>
                        <q-item-section>Export Chat</q-item-section>
                      </q-item>
                    </q-list>
                  </q-menu>
                </q-btn>
              </div>
            </q-card-section>

            <q-card-section class="chat-messages">
              <div class="messages-container" ref="messagesContainer">
                <div v-for="message in messages" :key="message.id" class="message-wrapper">
                  <div
                    class="message"
                    :class="{
                      'message-user': message.sender === 'user',
                      'message-ai': message.sender === 'ai',
                    }"
                  >
                    <div class="message-avatar">
                      <q-avatar size="24px">
                        <q-icon :name="message.sender === 'user' ? 'person' : 'smart_toy'" />
                      </q-avatar>
                    </div>
                    <div class="message-content">
                      <div class="message-text" v-html="formatMessage(message.text)"></div>
                      <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                    </div>
                  </div>
                </div>

                <!-- Typing indicator -->
                <div v-if="isTyping" class="message message-ai">
                  <div class="message-avatar">
                    <q-avatar size="24px">
                      <q-icon name="smart_toy" />
                    </q-avatar>
                  </div>
                  <div class="message-content">
                    <div class="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>

            <q-card-section class="chat-input">
              <div class="row q-gutter-sm">
                <div class="col">
                  <q-input
                    v-model="currentMessage"
                    placeholder="Ask me anything about your projects..."
                    filled
                    @keyup.enter="sendMessage"
                    :loading="isTyping"
                  >
                    <template v-slot:prepend>
                      <q-btn
                        flat
                        round
                        icon="attachment"
                        @click="showAttachmentMenu = !showAttachmentMenu"
                      >
                        <q-menu v-model="showAttachmentMenu">
                          <q-list>
                            <q-item clickable @click="attachFile">
                              <q-item-section avatar>
                                <q-icon name="attach_file" />
                              </q-item-section>
                              <q-item-section>Attach File</q-item-section>
                            </q-item>
                            <q-item clickable @click="attachProject">
                              <q-item-section avatar>
                                <q-icon name="folder" />
                              </q-item-section>
                              <q-item-section>Attach Project</q-item-section>
                            </q-item>
                          </q-list>
                        </q-menu>
                      </q-btn>
                    </template>
                  </q-input>
                </div>
                <div class="col-auto">
                  <q-btn
                    color="primary"
                    icon="send"
                    @click="sendMessage"
                    :disable="!currentMessage.trim() || isTyping"
                  />
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- AI Features Sidebar -->
        <div class="col-12 col-lg-4">
          <!-- Quick Actions -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Quick Actions</div>
              <div class="column q-gutter-sm">
                <q-btn
                  v-for="action in quickActions"
                  :key="action.id"
                  :color="action.color"
                  :icon="action.icon"
                  :label="action.label"
                  align="left"
                  @click="executeQuickAction(action)"
                />
              </div>
            </q-card-section>
          </q-card>

          <!-- AI Capabilities -->
          <q-card class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">AI Capabilities</div>
              <div class="capabilities-list">
                <div
                  v-for="capability in aiCapabilities"
                  :key="capability.id"
                  class="capability-item q-mb-sm"
                >
                  <div class="row items-center">
                    <q-icon :name="capability.icon" :color="capability.color" class="q-mr-sm" />
                    <div class="col">
                      <div class="text-weight-medium">{{ capability.name }}</div>
                      <div class="text-caption text-grey-7">{{ capability.description }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Recent Insights -->
          <q-card>
            <q-card-section>
              <div class="text-h6 text-weight-bold q-mb-md">Recent AI Insights</div>
              <div class="insights-list">
                <div
                  v-for="insight in recentInsights"
                  :key="insight.id"
                  class="insight-item q-mb-md"
                >
                  <div class="row items-start">
                    <q-icon
                      :name="insight.icon"
                      :color="insight.type === 'warning' ? 'orange' : 'primary'"
                      class="q-mr-sm q-mt-xs"
                    />
                    <div class="col">
                      <div class="text-body2">{{ insight.message }}</div>
                      <div class="text-caption text-grey-7">
                        {{ formatTime(insight.timestamp) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>

    <!-- Chat History Dialog -->
    <q-dialog v-model="showHistoryDialog" maximized>
      <q-card>
        <q-bar class="bg-primary text-white">
          <q-space />
          <div class="text-weight-bold">Chat History</div>
          <q-space />
          <q-btn dense flat icon="close" @click="showHistoryDialog = false" />
        </q-bar>

        <q-card-section class="q-pa-lg">
          <div class="text-center q-pa-xl">
            <q-icon name="history" size="96px" color="grey-5" class="q-mb-md" />
            <div class="text-h5 text-grey-7 q-mb-md">Chat History</div>
            <div class="text-body1 text-grey-6">
              Previous conversations with AI assistant would be displayed here
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';
import { useMockDataStore } from 'stores/mock-data';
import { format } from 'date-fns';

const mockDataStore = useMockDataStore();

interface Message {
  id: number;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

interface QuickAction {
  id: string;
  label: string;
  icon: string;
  color: string;
  prompt: string;
}

interface AICapability {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

interface AIInsight {
  id: string;
  message: string;
  type: 'info' | 'warning' | 'success';
  icon: string;
  timestamp: Date;
}

// Reactive data
const showHistoryDialog = ref(false);
const showChatMenu = ref(false);
const showAttachmentMenu = ref(false);
const currentMessage = ref('');
const isTyping = ref(false);
const aiStatus = ref('Online and ready to help');
const messagesContainer = ref<HTMLElement | null>(null);

const messages = ref<Message[]>([
  {
    id: 1,
    sender: 'ai',
    text: "Hello! I'm your AI project management assistant. I can help you with:<br/>• Project analysis and insights<br/>• Risk assessment<br/>• Team optimization<br/>• Schedule planning<br/>• Budget forecasting<br/><br/>What would you like to know about your projects?",
    timestamp: new Date(),
  },
]);

const quickActions: QuickAction[] = [
  {
    id: 'project-status',
    label: 'Analyze Project Status',
    icon: 'analytics',
    color: 'primary',
    prompt: 'Please analyze the current status of all my projects',
  },
  {
    id: 'risk-assessment',
    label: 'Risk Assessment',
    icon: 'warning',
    color: 'orange',
    prompt: 'Identify potential risks in my current projects',
  },
  {
    id: 'team-optimization',
    label: 'Optimize Team Allocation',
    icon: 'group',
    color: 'green',
    prompt: 'Suggest team allocation optimizations based on current workload',
  },
  {
    id: 'budget-forecast',
    label: 'Budget Forecast',
    icon: 'euro',
    color: 'blue',
    prompt: 'Provide budget forecast for upcoming projects',
  },
  {
    id: 'schedule-optimization',
    label: 'Schedule Optimization',
    icon: 'schedule',
    color: 'purple',
    prompt: 'Optimize project schedules to improve delivery times',
  },
];

const aiCapabilities: AICapability[] = [
  {
    id: 'analysis',
    name: 'Project Analysis',
    description: 'Deep insights into project performance and metrics',
    icon: 'analytics',
    color: 'primary',
  },
  {
    id: 'prediction',
    name: 'Predictive Analytics',
    description: 'Forecast project outcomes and identify potential issues',
    icon: 'trending_up',
    color: 'green',
  },
  {
    id: 'optimization',
    name: 'Resource Optimization',
    description: 'Optimize team allocation and resource distribution',
    icon: 'tune',
    color: 'orange',
  },
  {
    id: 'automation',
    name: 'Task Automation',
    description: 'Automate routine project management tasks',
    icon: 'auto_fix_high',
    color: 'blue',
  },
  {
    id: 'reporting',
    name: 'Smart Reporting',
    description: 'Generate intelligent reports and summaries',
    icon: 'description',
    color: 'purple',
  },
];

const recentInsights = ref<AIInsight[]>([
  {
    id: '1',
    message: 'Project "E-commerce Platform" is 15% ahead of schedule',
    type: 'success',
    icon: 'check_circle',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
  },
  {
    id: '2',
    message: "Mike Wilson's workload is 90% - consider redistribution",
    type: 'warning',
    icon: 'person',
    timestamp: new Date(Date.now() - 1000 * 60 * 60),
  },
  {
    id: '3',
    message: 'Budget utilization is optimal at 94% efficiency',
    type: 'info',
    icon: 'euro',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
  },
  {
    id: '4',
    message: 'Sprint velocity increased by 12% this iteration',
    type: 'success',
    icon: 'speed',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4),
  },
]);

// Mock AI responses
const aiResponses = [
  'Based on your current projects, I can see that you have 6 active projects with a total budget of €1.03M. The overall performance is strong with 87% on-time delivery rate.',
  "I've analyzed your team's workload distribution. Mike Wilson appears to be overloaded at 90% capacity. I recommend redistributing some of his tasks to Emma Davis who is at 60% capacity.",
  'Your project risk assessment shows 3 high-priority risks that need attention: 1) Data Migration project is behind schedule, 2) Budget overrun risk in Mobile App project, 3) Technical dependency bottleneck in AI Chatbot project.',
  'The PERT analysis suggests optimizing the critical path by parallelizing tasks in the System Design phase. This could reduce overall project duration by 2-3 weeks.',
  "Budget forecast indicates you're on track to finish 8% under budget if current trends continue. However, the Data Migration project may require additional resources.",
  'I recommend implementing daily standups for the Mobile App team and weekly retrospectives to improve velocity by an estimated 15-20%.',
];

// Methods
async function sendMessage() {
  if (!currentMessage.value.trim()) return;

  // Add user message
  const userMessage: Message = {
    id: Date.now(),
    sender: 'user',
    text: currentMessage.value,
    timestamp: new Date(),
  };

  messages.value.push(userMessage);
  currentMessage.value = '';

  // Show typing indicator
  isTyping.value = true;
  await scrollToBottom();

  // Simulate AI response delay
  setTimeout(
    () => {
      const aiMessage: Message = {
        id: Date.now() + 1,
        sender: 'ai',
        text: getRandomAIResponse(),
        timestamp: new Date(),
      };

      messages.value.push(aiMessage);
      isTyping.value = false;
      void scrollToBottom();
    },
    1500 + Math.random() * 2000,
  );
}

function getRandomAIResponse(): string {
  const randomIndex = Math.floor(Math.random() * aiResponses.length);
  return (
    aiResponses[randomIndex] || 'I apologize, but I encountered an error generating a response.'
  );
}

async function executeQuickAction(action: QuickAction) {
  currentMessage.value = action.prompt;
  await sendMessage();
}

function formatMessage(text: string): string {
  return text.replace(/\n/g, '<br/>');
}

function formatTime(timestamp: Date): string {
  return format(timestamp, 'HH:mm');
}

async function scrollToBottom() {
  await nextTick();
  const container = messagesContainer.value;
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function startNewChat() {
  messages.value = [
    {
      id: 1,
      sender: 'ai',
      text: "Hello! I'm ready to help you with your project management needs. What would you like to discuss?",
      timestamp: new Date(),
    },
  ];
}

function clearChat() {
  messages.value = [];
  showChatMenu.value = false;
}

function exportChat() {
  console.log('Exporting chat history...');
  showChatMenu.value = false;
}

function attachFile() {
  console.log('Attaching file...');
  showAttachmentMenu.value = false;
}

function attachProject() {
  console.log('Attaching project...');
  showAttachmentMenu.value = false;
}

onMounted(() => {
  mockDataStore.initializeData();
  void scrollToBottom();
});
</script>

<style scoped>
.chat-card {
  height: 70vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  flex-shrink: 0;
}

.chat-messages {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.chat-input {
  flex-shrink: 0;
  border-top: 1px solid #e0e0e0;
}

.message-wrapper {
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 8px;
}

.message-user {
  flex-direction: row-reverse;
}

.message-user .message-content {
  background: var(--q-primary);
  color: white;
  border-radius: 18px 18px 4px 18px;
}

.message-ai .message-content {
  background: #f5f5f5;
  color: #333;
  border-radius: 18px 18px 18px 4px;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  position: relative;
}

.message-text {
  margin-bottom: 4px;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
}

.message-user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.capability-item {
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.insight-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}
</style>
