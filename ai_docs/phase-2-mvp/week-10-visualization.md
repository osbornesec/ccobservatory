# Week 10: Data Visualization & Dashboard Implementation

## Overview
Implement comprehensive data visualization components and interactive dashboards for the Claude Code Observatory. This week focuses on creating charts, graphs, and visual analytics that transform raw conversation data into meaningful insights for users.

## Team Assignments
- **Frontend Lead**: Chart components, dashboard layout, interactive visualizations
- **UI/UX Developer**: Data visualization design, responsive layouts, accessibility
- **Full-Stack Developer**: Dashboard API integration, real-time chart updates, performance optimization

## Daily Schedule

### Monday: Chart Component Library
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Chart.js integration and base chart components
- **10:30-12:00**: Line chart and area chart implementation

#### Afternoon (4 hours)
- **13:00-15:00**: Bar chart, pie chart, and donut chart components
- **15:00-17:00**: Real-time chart updates and animation

### Tuesday: Advanced Visualization Components
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Time-series charts with zoom and pan functionality
- **10:30-12:00**: Heatmap and calendar view components

#### Afternoon (4 hours)
- **13:00-15:00**: Metrics cards and KPI widgets
- **15:00-17:00**: Progress indicators and gauge components

### Wednesday: Interactive Dashboard Layout
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Dashboard grid system and responsive layout
- **10:30-12:00**: Drag-and-drop dashboard customization

#### Afternoon (4 hours)
- **13:00-15:00**: Dashboard filtering and time range selection
- **15:00-17:00**: Export functionality (PNG, PDF, CSV)

### Thursday: Real-Time Features & Integration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Real-time data streaming integration
- **10:30-12:00**: Live chart updates via WebSocket

#### Afternoon (4 hours)
- **13:00-15:00**: Dashboard data refresh and caching
- **15:00-17:00**: Performance optimization for large datasets

### Friday: Testing & Polish
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Component testing and data validation
- **10:30-12:00**: Cross-browser compatibility testing

#### Afternoon (4 hours)
- **13:00-15:00**: Accessibility improvements and screen reader support
- **15:00-17:00**: Performance testing and optimization

## Technical Implementation Details

### Base Chart Component
```vue
<!-- src/components/charts/BaseChart.vue -->
<template>
  <div class="chart-container relative" :class="containerClasses">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80">
      <LoadingSpinner size="lg" />
    </div>
    
    <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-red-50 dark:bg-red-900/20">
      <div class="text-center text-red-600 dark:text-red-400">
        <ExclamationTriangleIcon class="w-8 h-8 mx-auto mb-2" />
        <p class="text-sm">{{ error }}</p>
        <BaseButton size="sm" variant="secondary" @click="$emit('retry')" class="mt-2">
          Retry
        </BaseButton>
      </div>
    </div>
    
    <canvas
      ref="chartCanvas"
      :width="width"
      :height="height"
      :style="{ maxWidth: '100%', maxHeight: '100%' }"
    />
    
    <div v-if="showLegend && !loading && !error" class="mt-4">
      <ChartLegend :items="legendItems" @toggle="handleLegendToggle" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartConfiguration,
  ChartData,
  ChartOptions
} from 'chart.js'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import ChartLegend from './ChartLegend.vue'
import BaseButton from '@components/base/BaseButton.vue'
import LoadingSpinner from '@components/base/LoadingSpinner.vue'

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface Props {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'area'
  data: ChartData
  options?: Partial<ChartOptions>
  width?: number
  height?: number
  loading?: boolean
  error?: string
  showLegend?: boolean
  responsive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: 400,
  height: 300,
  loading: false,
  error: '',
  showLegend: true,
  responsive: true
})

const emit = defineEmits<{
  retry: []
  legendToggle: [datasetIndex: number, visible: boolean]
  dataPointClick: [element: any, event: any]
}>()

const chartCanvas = ref<HTMLCanvasElement>()
const chartInstance = ref<Chart | null>(null)

const containerClasses = computed(() => [
  'w-full',
  {
    'h-64': !props.height,
    'h-auto': props.responsive
  }
])

const chartConfig = computed((): ChartConfiguration => {
  const baseOptions: ChartOptions = {
    responsive: props.responsive,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false // We use custom legend
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: 'rgba(75, 85, 99, 0.5)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12
      }
    },
    scales: props.type === 'pie' || props.type === 'doughnut' ? undefined : {
      x: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        },
        ticks: {
          color: 'rgba(107, 114, 128, 0.8)'
        }
      },
      y: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        },
        ticks: {
          color: 'rgba(107, 114, 128, 0.8)'
        }
      }
    },
    onClick: (event, elements) => {
      if (elements.length > 0) {
        emit('dataPointClick', elements[0], event)
      }
    }
  }

  return {
    type: props.type === 'area' ? 'line' : props.type,
    data: processChartData(props.data),
    options: {
      ...baseOptions,
      ...props.options
    }
  }
})

const legendItems = computed(() => {
  if (!props.data.datasets) return []
  
  return props.data.datasets.map((dataset, index) => ({
    label: dataset.label || `Dataset ${index + 1}`,
    color: Array.isArray(dataset.backgroundColor) 
      ? dataset.backgroundColor[0] 
      : dataset.backgroundColor || '#3B82F6',
    visible: !dataset.hidden
  }))
})

function processChartData(data: ChartData): ChartData {
  if (props.type === 'area') {
    return {
      ...data,
      datasets: data.datasets?.map(dataset => ({
        ...dataset,
        fill: true,
        backgroundColor: dataset.backgroundColor || 'rgba(59, 130, 246, 0.1)',
        borderColor: dataset.borderColor || '#3B82F6'
      }))
    }
  }
  
  return data
}

function createChart() {
  if (!chartCanvas.value) return
  
  try {
    chartInstance.value = new Chart(chartCanvas.value, chartConfig.value)
  } catch (error) {
    console.error('Failed to create chart:', error)
    emit('retry')
  }
}

function destroyChart() {
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
}

function updateChart() {
  if (!chartInstance.value) return
  
  chartInstance.value.data = processChartData(props.data)
  chartInstance.value.options = { ...chartInstance.value.options, ...props.options }
  chartInstance.value.update('none') // No animation for real-time updates
}

function handleLegendToggle(datasetIndex: number) {
  if (!chartInstance.value) return
  
  const dataset = chartInstance.value.data.datasets[datasetIndex]
  if (dataset) {
    dataset.hidden = !dataset.hidden
    chartInstance.value.update()
    emit('legendToggle', datasetIndex, !dataset.hidden)
  }
}

// Lifecycle
onMounted(async () => {
  await nextTick()
  if (!props.loading && !props.error && props.data) {
    createChart()
  }
})

onUnmounted(() => {
  destroyChart()
})

// Watch for data changes
watch(() => props.data, () => {
  if (chartInstance.value && !props.loading && !props.error) {
    updateChart()
  }
}, { deep: true })

watch(() => [props.loading, props.error], ([loading, error]) => {
  if (!loading && !error && !chartInstance.value && props.data) {
    nextTick(() => createChart())
  } else if ((loading || error) && chartInstance.value) {
    destroyChart()
  }
})
</script>
```

### Time Series Chart Component
```vue
<!-- src/components/charts/TimeSeriesChart.vue -->
<template>
  <div class="time-series-chart">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ title }}
      </h3>
      
      <div class="flex items-center gap-2">
        <!-- Time Range Selector -->
        <select
          v-model="selectedTimeRange"
          class="text-sm border border-gray-300 rounded-md px-3 py-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          @change="handleTimeRangeChange"
        >
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
          <option value="custom">Custom Range</option>
        </select>
        
        <!-- Refresh Button -->
        <BaseButton
          size="sm"
          variant="ghost"
          @click="refreshData"
          :disabled="loading"
        >
          <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        </BaseButton>
      </div>
    </div>
    
    <!-- Custom Date Range Picker -->
    <div v-if="selectedTimeRange === 'custom'" class="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div class="flex items-center gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Start Date
          </label>
          <input
            v-model="customStartDate"
            type="datetime-local"
            class="text-sm border border-gray-300 rounded-md px-3 py-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            End Date
          </label>
          <input
            v-model="customEndDate"
            type="datetime-local"
            class="text-sm border border-gray-300 rounded-md px-3 py-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        <BaseButton
          size="sm"
          @click="applyCustomRange"
          class="mt-6"
        >
          Apply
        </BaseButton>
      </div>
    </div>
    
    <!-- Chart -->
    <BaseChart
      type="line"
      :data="chartData"
      :options="chartOptions"
      :loading="loading"
      :error="error"
      :height="400"
      @retry="refreshData"
    />
    
    <!-- Chart Controls -->
    <div class="mt-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <label class="flex items-center">
          <input
            v-model="showDataPoints"
            type="checkbox"
            class="mr-2"
            @change="updateChartOptions"
          />
          <span class="text-sm text-gray-700 dark:text-gray-300">Show data points</span>
        </label>
        
        <label class="flex items-center">
          <input
            v-model="smoothLines"
            type="checkbox"
            class="mr-2"
            @change="updateChartOptions"
          />
          <span class="text-sm text-gray-700 dark:text-gray-300">Smooth lines</span>
        </label>
      </div>
      
      <div class="text-sm text-gray-500 dark:text-gray-400">
        Last updated: {{ lastUpdated ? formatTime(lastUpdated) : 'Never' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import BaseChart from './BaseChart.vue'
import BaseButton from '@components/base/BaseButton.vue'
import { useAnalyticsStore } from '@stores/analytics'
import { useWebSocketStore } from '@stores/websocket'
import { formatDistanceToNow } from 'date-fns'
import type { ChartData, ChartOptions } from 'chart.js'

interface Props {
  title: string
  metric: string
  realTime?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  realTime: false
})

const analyticsStore = useAnalyticsStore()
const webSocketStore = useWebSocketStore()

const loading = ref(false)
const error = ref('')
const selectedTimeRange = ref('7d')
const customStartDate = ref('')
const customEndDate = ref('')
const showDataPoints = ref(false)
const smoothLines = ref(true)
const lastUpdated = ref<Date | null>(null)

const chartData = computed((): ChartData<'line'> => {
  const timeSeriesData = analyticsStore.getTimeSeriesData(props.metric, getTimeRange())
  
  return {
    labels: timeSeriesData.map(point => point.timestamp),
    datasets: [{
      label: props.title,
      data: timeSeriesData.map(point => point.value),
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      pointRadius: showDataPoints.value ? 4 : 0,
      pointHoverRadius: 6,
      tension: smoothLines.value ? 0.4 : 0,
      fill: true
    }]
  }
})

const chartOptions = computed((): ChartOptions<'line'> => ({
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (context) => {
          return `${props.title}: ${formatValue(context.parsed.y)}`
        }
      }
    }
  },
  scales: {
    x: {
      type: 'time',
      time: {
        displayFormats: {
          hour: 'HH:mm',
          day: 'MMM dd',
          week: 'MMM dd',
          month: 'MMM yyyy'
        }
      },
      title: {
        display: true,
        text: 'Time'
      }
    },
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: getYAxisLabel()
      },
      ticks: {
        callback: (value) => formatValue(value)
      }
    }
  }
}))

function getTimeRange() {
  const now = new Date()
  const ranges = {
    '24h': { start: new Date(now.getTime() - 24 * 60 * 60 * 1000), end: now },
    '7d': { start: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), end: now },
    '30d': { start: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000), end: now },
    '90d': { start: new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000), end: now },
    'custom': { 
      start: customStartDate.value ? new Date(customStartDate.value) : new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
      end: customEndDate.value ? new Date(customEndDate.value) : now
    }
  }
  
  return ranges[selectedTimeRange.value] || ranges['7d']
}

function getYAxisLabel(): string {
  const labels = {
    conversations: 'Conversations',
    messages: 'Messages',
    tokens: 'Tokens',
    users: 'Active Users'
  }
  
  return labels[props.metric] || 'Value'
}

function formatValue(value: any): string {
  const num = Number(value)
  
  if (props.metric === 'tokens') {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  }
  
  return num.toLocaleString()
}

function formatTime(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true })
}

async function refreshData() {
  loading.value = true
  error.value = ''
  
  try {
    const timeRange = getTimeRange()
    await analyticsStore.fetchTimeSeriesData(props.metric, timeRange)
    lastUpdated.value = new Date()
  } catch (err) {
    error.value = 'Failed to load chart data'
    console.error('Chart data fetch error:', err)
  } finally {
    loading.value = false
  }
}

function handleTimeRangeChange() {
  if (selectedTimeRange.value !== 'custom') {
    refreshData()
  }
}

function applyCustomRange() {
  if (customStartDate.value && customEndDate.value) {
    refreshData()
  }
}

function updateChartOptions() {
  // Chart will reactively update based on computed options
}

// Real-time updates
let realTimeInterval: NodeJS.Timeout | null = null

onMounted(async () => {
  await refreshData()
  
  if (props.realTime) {
    // Subscribe to real-time updates
    webSocketStore.on(`analytics_${props.metric}`, (data) => {
      analyticsStore.updateTimeSeriesData(props.metric, data)
      lastUpdated.value = new Date()
    })
    
    // Periodic refresh for real-time data
    realTimeInterval = setInterval(() => {
      if (selectedTimeRange.value === '24h' || selectedTimeRange.value === '7d') {
        refreshData()
      }
    }, 60000) // Refresh every minute
  }
})

onUnmounted(() => {
  if (realTimeInterval) {
    clearInterval(realTimeInterval)
  }
  
  if (props.realTime) {
    webSocketStore.off(`analytics_${props.metric}`)
  }
})
</script>
```

### Dashboard Grid Layout
```vue
<!-- src/components/dashboard/DashboardGrid.vue -->
<template>
  <div class="dashboard-grid" :class="{ 'edit-mode': editMode }">
    <div class="grid gap-6" :style="gridStyle">
      <DashboardWidget
        v-for="widget in widgets"
        :key="widget.id"
        :widget="widget"
        :edit-mode="editMode"
        @move="handleWidgetMove"
        @resize="handleWidgetResize"
        @remove="handleWidgetRemove"
        @configure="handleWidgetConfigure"
      />
      
      <!-- Add Widget Button -->
      <div
        v-if="editMode"
        class="add-widget-placeholder flex items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg min-h-[200px] hover:border-primary-500 transition-colors cursor-pointer"
        @click="showAddWidgetModal = true"
      >
        <div class="text-center text-gray-500 dark:text-gray-400">
          <PlusIcon class="w-8 h-8 mx-auto mb-2" />
          <p class="text-sm">Add Widget</p>
        </div>
      </div>
    </div>
    
    <!-- Dashboard Controls -->
    <div class="fixed bottom-6 right-6 flex flex-col gap-2">
      <BaseButton
        v-if="!editMode"
        @click="toggleEditMode"
        variant="primary"
        class="shadow-lg"
      >
        <PencilIcon class="w-4 h-4 mr-2" />
        Edit Dashboard
      </BaseButton>
      
      <div v-else class="flex flex-col gap-2">
        <BaseButton
          @click="saveDashboard"
          variant="primary"
          class="shadow-lg"
          :loading="saving"
        >
          <CheckIcon class="w-4 h-4 mr-2" />
          Save Changes
        </BaseButton>
        
        <BaseButton
          @click="cancelEdit"
          variant="secondary"
          class="shadow-lg"
        >
          <XMarkIcon class="w-4 h-4 mr-2" />
          Cancel
        </BaseButton>
      </div>
      
      <!-- Export Options -->
      <div class="relative">
        <BaseButton
          @click="showExportMenu = !showExportMenu"
          variant="ghost"
          class="shadow-lg bg-white dark:bg-gray-800"
        >
          <ArrowDownTrayIcon class="w-4 h-4" />
        </BaseButton>
        
        <div
          v-if="showExportMenu"
          class="absolute bottom-full right-0 mb-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 min-w-[150px]"
        >
          <button
            @click="exportDashboard('png')"
            class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Export as PNG
          </button>
          <button
            @click="exportDashboard('pdf')"
            class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Export as PDF
          </button>
          <button
            @click="exportDashboard('csv')"
            class="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Export Data (CSV)
          </button>
        </div>
      </div>
    </div>
    
    <!-- Add Widget Modal -->
    <AddWidgetModal
      v-if="showAddWidgetModal"
      @close="showAddWidgetModal = false"
      @add="handleAddWidget"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  PlusIcon, 
  PencilIcon, 
  CheckIcon, 
  XMarkIcon, 
  ArrowDownTrayIcon 
} from '@heroicons/vue/24/outline'
import DashboardWidget from './DashboardWidget.vue'
import AddWidgetModal from './AddWidgetModal.vue'
import BaseButton from '@components/base/BaseButton.vue'
import { useDashboardStore } from '@stores/dashboard'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

interface DashboardWidget {
  id: string
  type: string
  title: string
  config: Record<string, any>
  position: { x: number; y: number; width: number; height: number }
}

const dashboardStore = useDashboardStore()

const editMode = ref(false)
const saving = ref(false)
const showExportMenu = ref(false)
const showAddWidgetModal = ref(false)
const originalWidgets = ref<DashboardWidget[]>([])

const widgets = computed(() => dashboardStore.widgets)

const gridStyle = computed(() => ({
  gridTemplateColumns: 'repeat(12, 1fr)',
  gridAutoRows: '120px'
}))

function toggleEditMode() {
  editMode.value = true
  originalWidgets.value = JSON.parse(JSON.stringify(widgets.value))
}

async function saveDashboard() {
  saving.value = true
  
  try {
    await dashboardStore.saveDashboard()
    editMode.value = false
    originalWidgets.value = []
  } catch (error) {
    console.error('Failed to save dashboard:', error)
  } finally {
    saving.value = false
  }
}

function cancelEdit() {
  dashboardStore.setWidgets(originalWidgets.value)
  editMode.value = false
  originalWidgets.value = []
}

function handleWidgetMove(widgetId: string, position: { x: number; y: number }) {
  dashboardStore.updateWidgetPosition(widgetId, position)
}

function handleWidgetResize(widgetId: string, size: { width: number; height: number }) {
  dashboardStore.updateWidgetSize(widgetId, size)
}

function handleWidgetRemove(widgetId: string) {
  if (confirm('Are you sure you want to remove this widget?')) {
    dashboardStore.removeWidget(widgetId)
  }
}

function handleWidgetConfigure(widgetId: string) {
  // Open widget configuration modal
  dashboardStore.openWidgetConfig(widgetId)
}

function handleAddWidget(widgetConfig: any) {
  dashboardStore.addWidget(widgetConfig)
  showAddWidgetModal.value = false
}

async function exportDashboard(format: 'png' | 'pdf' | 'csv') {
  showExportMenu.value = false
  
  try {
    switch (format) {
      case 'png':
        await exportAsPNG()
        break
      case 'pdf':
        await exportAsPDF()
        break
      case 'csv':
        await exportAsCSV()
        break
    }
  } catch (error) {
    console.error(`Failed to export dashboard as ${format}:`, error)
  }
}

async function exportAsPNG() {
  const element = document.querySelector('.dashboard-grid') as HTMLElement
  if (!element) return
  
  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    scale: 2
  })
  
  const link = document.createElement('a')
  link.download = `dashboard-${new Date().toISOString().split('T')[0]}.png`
  link.href = canvas.toDataURL()
  link.click()
}

async function exportAsPDF() {
  const element = document.querySelector('.dashboard-grid') as HTMLElement
  if (!element) return
  
  const canvas = await html2canvas(element, {
    backgroundColor: '#ffffff',
    scale: 1
  })
  
  const imgWidth = 210 // A4 width in mm
  const pageHeight = 295 // A4 height in mm
  const imgHeight = (canvas.height * imgWidth) / canvas.width
  let heightLeft = imgHeight
  
  const pdf = new jsPDF('p', 'mm', 'a4')
  let position = 0
  
  pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight)
  heightLeft -= pageHeight
  
  while (heightLeft >= 0) {
    position = heightLeft - imgHeight
    pdf.addPage()
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
  }
  
  pdf.save(`dashboard-${new Date().toISOString().split('T')[0]}.pdf`)
}

async function exportAsCSV() {
  const data = await dashboardStore.getDashboardData()
  const csv = convertToCSV(data)
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const link = document.createElement('a')
  link.download = `dashboard-data-${new Date().toISOString().split('T')[0]}.csv`
  link.href = URL.createObjectURL(blob)
  link.click()
}

function convertToCSV(data: any): string {
  // Implement CSV conversion logic based on dashboard data
  const headers = ['Date', 'Conversations', 'Messages', 'Tokens', 'Users']
  const rows = data.trends.conversationsOverTime.map((point: any, index: number) => [
    point.timestamp,
    point.value,
    data.trends.messagesOverTime[index]?.value || 0,
    data.trends.tokensOverTime[index]?.value || 0,
    data.overview.activeUsers
  ])
  
  return [headers, ...rows].map(row => row.join(',')).join('\n')
}

onMounted(async () => {
  await dashboardStore.loadDashboard()
})

// Close export menu when clicking outside
onMounted(() => {
  document.addEventListener('click', (event) => {
    const target = event.target as Element
    if (!target.closest('.relative')) {
      showExportMenu.value = false
    }
  })
})
</script>

<style scoped>
.dashboard-grid .grid > * {
  grid-column: span var(--widget-width, 4);
  grid-row: span var(--widget-height, 2);
}

.edit-mode .grid > * {
  outline: 2px dashed rgba(59, 130, 246, 0.3);
  outline-offset: 4px;
}
</style>
```

### KPI Metrics Cards
```vue
<!-- src/components/dashboard/MetricsCard.vue -->
<template>
  <div class="metrics-card bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
          {{ title }}
        </h3>
        
        <div class="mt-2 flex items-baseline">
          <p class="text-2xl font-semibold text-gray-900 dark:text-white">
            {{ loading ? '—' : formatValue(value) }}
          </p>
          
          <div v-if="change !== undefined && !loading" class="ml-3 flex items-center">
            <span
              :class="[
                'text-sm font-medium',
                changeType === 'positive' ? 'text-green-600 dark:text-green-400' :
                changeType === 'negative' ? 'text-red-600 dark:text-red-400' :
                'text-gray-500 dark:text-gray-400'
              ]"
            >
              {{ formatChange(change) }}
            </span>
            <component
              :is="changeIcon"
              :class="[
                'w-4 h-4 ml-1',
                changeType === 'positive' ? 'text-green-600 dark:text-green-400' :
                changeType === 'negative' ? 'text-red-600 dark:text-red-400' :
                'text-gray-500 dark:text-gray-400'
              ]"
            />
          </div>
        </div>
        
        <p v-if="description" class="mt-1 text-sm text-gray-600 dark:text-gray-300">
          {{ description }}
        </p>
      </div>
      
      <div class="flex-shrink-0">
        <div
          :class="[
            'w-12 h-12 rounded-full flex items-center justify-center',
            iconBgClass
          ]"
        >
          <component :is="icon" :class="['w-6 h-6', iconClass]" />
        </div>
      </div>
    </div>
    
    <!-- Mini Chart -->
    <div v-if="showChart && chartData.length > 0" class="mt-4">
      <div class="h-16">
        <canvas ref="miniChart" class="w-full h-full"></canvas>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 flex items-center justify-center rounded-lg">
      <LoadingSpinner size="sm" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  MinusIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  UserGroupIcon,
  CpuChipIcon
} from '@heroicons/vue/24/outline'
import { Chart, LineElement, PointElement, LinearScale, CategoryScale } from 'chart.js'
import LoadingSpinner from '@components/base/LoadingSpinner.vue'

Chart.register(LineElement, PointElement, LinearScale, CategoryScale)

interface Props {
  title: string
  value: number
  change?: number
  description?: string
  icon?: any
  loading?: boolean
  showChart?: boolean
  chartData?: number[]
  format?: 'number' | 'currency' | 'percentage' | 'bytes'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showChart: false,
  chartData: () => [],
  format: 'number',
  icon: DocumentTextIcon
})

const miniChart = ref<HTMLCanvasElement>()
const chartInstance = ref<Chart | null>(null)

const changeType = computed(() => {
  if (props.change === undefined || props.change === 0) return 'neutral'
  return props.change > 0 ? 'positive' : 'negative'
})

const changeIcon = computed(() => {
  switch (changeType.value) {
    case 'positive': return ArrowUpIcon
    case 'negative': return ArrowDownIcon
    default: return MinusIcon
  }
})

const iconBgClass = computed(() => {
  const classes = {
    conversations: 'bg-blue-100 dark:bg-blue-900/20',
    messages: 'bg-green-100 dark:bg-green-900/20',
    users: 'bg-purple-100 dark:bg-purple-900/20',
    tokens: 'bg-orange-100 dark:bg-orange-900/20'
  }
  
  return classes[inferType()] || 'bg-gray-100 dark:bg-gray-900/20'
})

const iconClass = computed(() => {
  const classes = {
    conversations: 'text-blue-600 dark:text-blue-400',
    messages: 'text-green-600 dark:text-green-400',
    users: 'text-purple-600 dark:text-purple-400',
    tokens: 'text-orange-600 dark:text-orange-400'
  }
  
  return classes[inferType()] || 'text-gray-600 dark:text-gray-400'
})

function inferType(): string {
  const title = props.title.toLowerCase()
  if (title.includes('conversation')) return 'conversations'
  if (title.includes('message')) return 'messages'
  if (title.includes('user')) return 'users'
  if (title.includes('token')) return 'tokens'
  return 'default'
}

function formatValue(value: number): string {
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    
    case 'percentage':
      return `${value.toFixed(1)}%`
    
    case 'bytes':
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let bytes = value
      let unitIndex = 0
      
      while (bytes >= 1024 && unitIndex < units.length - 1) {
        bytes /= 1024
        unitIndex++
      }
      
      return `${bytes.toFixed(1)} ${units[unitIndex]}`
    
    default:
      if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`
      } else if (value >= 1000) {
        return `${(value / 1000).toFixed(1)}K`
      }
      return value.toLocaleString()
  }
}

function formatChange(change: number): string {
  const abs = Math.abs(change)
  const sign = change >= 0 ? '+' : ''
  
  if (props.format === 'percentage') {
    return `${sign}${change.toFixed(1)}%`
  }
  
  return `${sign}${abs.toFixed(1)}%`
}

function createMiniChart() {
  if (!miniChart.value || props.chartData.length === 0) return
  
  chartInstance.value = new Chart(miniChart.value, {
    type: 'line',
    data: {
      labels: props.chartData.map((_, i) => i),
      datasets: [{
        data: props.chartData,
        borderColor: changeType.value === 'positive' ? '#10B981' : 
                   changeType.value === 'negative' ? '#EF4444' : '#6B7280',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      },
      elements: {
        point: { radius: 0 }
      }
    }
  })
}

function destroyChart() {
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
}

onMounted(async () => {
  if (props.showChart) {
    await nextTick()
    createMiniChart()
  }
})

onUnmounted(() => {
  destroyChart()
})

watch(() => props.chartData, () => {
  if (props.showChart) {
    destroyChart()
    nextTick(() => createMiniChart())
  }
}, { deep: true })
</script>
```

## Performance Requirements
- **Chart Rendering**: Charts render within 500ms with datasets up to 10,000 points
- **Real-time Updates**: Dashboard updates within 2 seconds of data changes
- **Memory Usage**: Visualization components use under 100MB total
- **Export Performance**: Dashboard exports complete within 10 seconds
- **Responsive Design**: Smooth rendering across all device sizes

## Acceptance Criteria
- [ ] Comprehensive chart component library implemented
- [ ] Time-series charts with zoom and pan functionality
- [ ] Interactive dashboard with drag-and-drop customization
- [ ] Real-time data updates via WebSocket integration
- [ ] KPI metrics cards with trending indicators
- [ ] Dashboard export functionality (PNG, PDF, CSV)
- [ ] Responsive design across all device sizes
- [ ] Accessibility compliance (WCAG 2.1 AA)
- [ ] Performance benchmarks meeting requirements
- [ ] Cross-browser compatibility verified

## Testing Procedures
1. **Component Testing**: Test individual chart components with various data sets
2. **Visual Regression Testing**: Screenshot comparison testing for UI consistency
3. **Performance Testing**: Chart rendering performance with large datasets
4. **Export Testing**: Verify export functionality across formats
5. **Accessibility Testing**: Screen reader and keyboard navigation testing

## Integration Points
- **Week 9**: Analytics engine and data processing integration
- **Week 11**: End-to-end MVP integration and testing
- **Backend API**: Real-time analytics data consumption

## Browser Performance Optimization
- Canvas-based rendering for complex visualizations
- Virtual scrolling for large data tables
- Lazy loading for off-screen charts
- WebGL acceleration for high-performance charts
- Progressive data loading for time-series

## Accessibility Features
- High contrast mode support
- Screen reader compatible chart descriptions
- Keyboard navigation for all interactive elements
- Focus management for modal interactions
- Alternative text for visual elements

## Export Capabilities
- PNG export with configurable resolution
- PDF export with multi-page support
- CSV data export with custom formatting
- Scheduled report generation
- Batch export functionality

## Real-Time WebSocket Chart Integration

### WebSocket Chart Service
```typescript
// src/services/websocket-chart.ts
import { ref, reactive, onUnmounted } from 'vue'
import { useWebSocketStore } from '@stores/websocket'
import { throttle, debounce } from 'lodash-es'

export interface ChartDataPoint {
  timestamp: Date
  value: number
  metadata?: Record<string, any>
}

export interface WebSocketChartConfig {
  chartId: string
  dataLimit: number
  updateInterval: number
  throttleMs: number
  aggregationWindow?: number
}

export function useWebSocketChart(config: WebSocketChartConfig) {
  const webSocketStore = useWebSocketStore()
  const chartData = ref<ChartDataPoint[]>([])
  const isConnected = ref(false)
  const lastUpdate = ref<Date | null>(null)
  const stats = reactive({
    totalUpdates: 0,
    droppedUpdates: 0,
    averageLatency: 0
  })

  // Buffer for handling rapid updates
  const updateBuffer: ChartDataPoint[] = []
  let processingBuffer = false

  // Throttled chart update function
  const throttledUpdate = throttle(() => {
    if (updateBuffer.length === 0) return
    
    const newData = [...updateBuffer]
    updateBuffer.length = 0
    
    // Apply aggregation if configured
    const aggregatedData = config.aggregationWindow 
      ? aggregateDataPoints(newData, config.aggregationWindow)
      : newData
    
    // Update chart data with size limit
    chartData.value = [
      ...chartData.value,
      ...aggregatedData
    ].slice(-config.dataLimit)
    
    stats.totalUpdates++
    lastUpdate.value = new Date()
  }, config.throttleMs)

  // Debounced buffer processor
  const debouncedProcess = debounce(() => {
    if (!processingBuffer) {
      processingBuffer = true
      throttledUpdate()
      processingBuffer = false
    }
  }, 16) // ~60fps

  function aggregateDataPoints(points: ChartDataPoint[], windowMs: number): ChartDataPoint[] {
    const windows = new Map<number, ChartDataPoint[]>()
    
    points.forEach(point => {
      const windowStart = Math.floor(point.timestamp.getTime() / windowMs) * windowMs
      if (!windows.has(windowStart)) {
        windows.set(windowStart, [])
      }
      windows.get(windowStart)!.push(point)
    })
    
    return Array.from(windows.entries()).map(([timestamp, windowPoints]) => ({
      timestamp: new Date(timestamp),
      value: windowPoints.reduce((sum, p) => sum + p.value, 0) / windowPoints.length,
      metadata: { count: windowPoints.length }
    }))
  }

  function handleWebSocketMessage(data: any) {
    const startTime = performance.now()
    
    try {
      const dataPoint: ChartDataPoint = {
        timestamp: new Date(data.timestamp),
        value: data.value,
        metadata: data.metadata
      }
      
      // Add to buffer
      updateBuffer.push(dataPoint)
      
      // Process buffer
      debouncedProcess()
      
      // Update latency stats
      const latency = performance.now() - startTime
      stats.averageLatency = (stats.averageLatency * 0.9) + (latency * 0.1)
      
    } catch (error) {
      console.error('Error processing WebSocket chart data:', error)
      stats.droppedUpdates++
    }
  }

  function connect() {
    if (isConnected.value) return
    
    webSocketStore.subscribe(`chart_${config.chartId}`, handleWebSocketMessage)
    isConnected.value = true
  }

  function disconnect() {
    if (!isConnected.value) return
    
    webSocketStore.unsubscribe(`chart_${config.chartId}`, handleWebSocketMessage)
    isConnected.value = false
  }

  function clearData() {
    chartData.value = []
    updateBuffer.length = 0
    stats.totalUpdates = 0
    stats.droppedUpdates = 0
    stats.averageLatency = 0
  }

  function addHistoricalData(historicalData: ChartDataPoint[]) {
    chartData.value = [...historicalData, ...chartData.value]
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .slice(-config.dataLimit)
  }

  // Auto-cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    chartData,
    isConnected,
    lastUpdate,
    stats,
    connect,
    disconnect,
    clearData,
    addHistoricalData
  }
}
```

### Real-Time Chart Component
```vue
<!-- src/components/charts/RealTimeChart.vue -->
<template>
  <div class="real-time-chart">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ title }}
      </h3>
      
      <div class="flex items-center gap-2">
        <!-- Connection Status -->
        <div class="flex items-center gap-1 text-sm">
          <div 
            :class="[
              'w-2 h-2 rounded-full',
              isConnected ? 'bg-green-500' : 'bg-red-500'
            ]"
          />
          <span :class="isConnected ? 'text-green-600' : 'text-red-600'">
            {{ isConnected ? 'Live' : 'Disconnected' }}
          </span>
        </div>
        
        <!-- Stats -->
        <div class="text-xs text-gray-500">
          {{ stats.totalUpdates }} updates
        </div>
        
        <!-- Controls -->
        <BaseButton
          size="sm"
          variant="ghost"
          @click="toggleConnection"
          :disabled="loading"
        >
          {{ isConnected ? 'Pause' : 'Resume' }}
        </BaseButton>
        
        <BaseButton
          size="sm"
          variant="ghost"
          @click="clearChart"
        >
          <TrashIcon class="w-4 h-4" />
        </BaseButton>
      </div>
    </div>
    
    <!-- Performance Indicators -->
    <div class="mb-4 grid grid-cols-3 gap-4 text-sm">
      <div class="bg-gray-50 dark:bg-gray-800 p-2 rounded">
        <div class="text-gray-500 dark:text-gray-400">Latency</div>
        <div class="font-semibold">{{ stats.averageLatency.toFixed(1) }}ms</div>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 p-2 rounded">
        <div class="text-gray-500 dark:text-gray-400">Data Points</div>
        <div class="font-semibold">{{ chartData.length }}</div>
      </div>
      <div class="bg-gray-50 dark:bg-gray-800 p-2 rounded">
        <div class="text-gray-500 dark:text-gray-400">Dropped</div>
        <div class="font-semibold">{{ stats.droppedUpdates }}</div>
      </div>
    </div>
    
    <!-- Chart -->
    <div class="relative">
      <BaseChart
        type="line"
        :data="processedChartData"
        :options="chartOptions"
        :loading="loading"
        :error="error"
        :height="400"
      />
      
      <!-- Streaming Indicator -->
      <div 
        v-if="isStreaming"
        class="absolute top-2 right-2 bg-blue-500 text-white px-2 py-1 rounded text-xs animate-pulse"
      >
        Streaming
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { TrashIcon } from '@heroicons/vue/24/outline'
import BaseChart from './BaseChart.vue'
import BaseButton from '@components/base/BaseButton.vue'
import { useWebSocketChart } from '@services/websocket-chart'
import { format } from 'date-fns'
import type { ChartData, ChartOptions } from 'chart.js'

interface Props {
  title: string
  chartId: string
  dataLimit?: number
  updateInterval?: number
  throttleMs?: number
  aggregationWindow?: number
  autoConnect?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  dataLimit: 100,
  updateInterval: 1000,
  throttleMs: 100,
  autoConnect: true
})

const loading = ref(false)
const error = ref('')
const isStreaming = ref(false)

const {
  chartData,
  isConnected,
  lastUpdate,
  stats,
  connect,
  disconnect,
  clearData,
  addHistoricalData
} = useWebSocketChart({
  chartId: props.chartId,
  dataLimit: props.dataLimit,
  updateInterval: props.updateInterval,
  throttleMs: props.throttleMs,
  aggregationWindow: props.aggregationWindow
})

const processedChartData = computed((): ChartData<'line'> => {
  const data = chartData.value
  
  return {
    labels: data.map(point => format(point.timestamp, 'HH:mm:ss')),
    datasets: [{
      label: props.title,
      data: data.map(point => point.value),
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.4,
      fill: true
    }]
  }
})

const chartOptions = computed((): ChartOptions<'line'> => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false, // Disable animations for real-time
  scales: {
    x: {
      type: 'category',
      ticks: {
        maxTicksLimit: 10
      },
      title: {
        display: true,
        text: 'Time'
      }
    },
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Value'
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      callbacks: {
        label: (context) => {
          const dataPoint = chartData.value[context.dataIndex]
          return `${props.title}: ${context.parsed.y} (${format(dataPoint.timestamp, 'HH:mm:ss')})`
        }
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}))

function toggleConnection() {
  if (isConnected.value) {
    disconnect()
  } else {
    connect()
  }
}

function clearChart() {
  if (confirm('Clear all chart data?')) {
    clearData()
  }
}

// Track streaming state
watch(lastUpdate, () => {
  isStreaming.value = true
  setTimeout(() => {
    isStreaming.value = false
  }, 1000)
})

// Auto-connect on mount
onMounted(() => {
  if (props.autoConnect) {
    connect()
  }
})

// Cleanup on unmount
onUnmounted(() => {
  disconnect()
})
</script>
```

## Performance Optimization Composables

### Chart Performance Optimization
```typescript
// src/composables/useChartPerformance.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { debounce, throttle } from 'lodash-es'

export interface PerformanceMetrics {
  renderTime: number
  memoryUsage: number
  frameRate: number
  dataPointCount: number
}

export function useChartPerformance() {
  const metrics = ref<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    frameRate: 0,
    dataPointCount: 0
  })
  
  const isLowPerformance = ref(false)
  const performanceMode = ref<'high' | 'medium' | 'low'>('high')
  
  // Performance monitoring
  let frameCount = 0
  let lastTime = performance.now()
  let animationFrameId: number | null = null
  
  function measureFrameRate() {
    const now = performance.now()
    frameCount++
    
    if (now - lastTime >= 1000) {
      metrics.value.frameRate = frameCount
      frameCount = 0
      lastTime = now
      
      // Adjust performance mode based on frame rate
      if (metrics.value.frameRate < 30) {
        performanceMode.value = 'low'
        isLowPerformance.value = true
      } else if (metrics.value.frameRate < 45) {
        performanceMode.value = 'medium'
        isLowPerformance.value = false
      } else {
        performanceMode.value = 'high'
        isLowPerformance.value = false
      }
    }
    
    animationFrameId = requestAnimationFrame(measureFrameRate)
  }
  
  function measureMemoryUsage() {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      metrics.value.memoryUsage = memory.usedJSHeapSize / (1024 * 1024) // MB
    }
  }
  
  function measureRenderTime<T>(fn: () => T): T {
    const start = performance.now()
    const result = fn()
    metrics.value.renderTime = performance.now() - start
    return result
  }
  
  // Throttled memory measurement
  const throttledMemoryMeasure = throttle(measureMemoryUsage, 5000)
  
  // Performance optimization strategies
  const optimizationStrategies = computed(() => ({
    // Reduce animation complexity in low performance mode
    animationDuration: performanceMode.value === 'high' ? 750 : 
                      performanceMode.value === 'medium' ? 300 : 0,
    
    // Adjust point radius based on performance
    pointRadius: performanceMode.value === 'high' ? 4 : 
                performanceMode.value === 'medium' ? 2 : 0,
    
    // Reduce data density in low performance mode
    dataDownsampling: performanceMode.value === 'low' ? 0.5 : 1,
    
    // Disable expensive features in low performance mode
    enableShadows: performanceMode.value === 'high',
    enableGradients: performanceMode.value !== 'low',
    enableAntialiasing: performanceMode.value === 'high'
  }))
  
  // Data optimization functions
  function downsampleData<T extends { timestamp: Date; value: number }>(data: T[], ratio: number): T[] {
    if (ratio >= 1) return data
    
    const step = Math.ceil(1 / ratio)
    return data.filter((_, index) => index % step === 0)
  }
  
  function aggregateData<T extends { timestamp: Date; value: number }>(data: T[], windowMs: number): T[] {
    const windows = new Map<number, T[]>()
    
    data.forEach(point => {
      const windowStart = Math.floor(point.timestamp.getTime() / windowMs) * windowMs
      if (!windows.has(windowStart)) {
        windows.set(windowStart, [])
      }
      windows.get(windowStart)!.push(point)
    })
    
    return Array.from(windows.entries()).map(([timestamp, windowPoints]) => ({
      timestamp: new Date(timestamp),
      value: windowPoints.reduce((sum, p) => sum + p.value, 0) / windowPoints.length
    } as T))
  }
  
  // Canvas optimization
  function optimizeCanvas(canvas: HTMLCanvasElement) {
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Enable hardware acceleration
    ctx.imageSmoothingEnabled = optimizationStrategies.value.enableAntialiasing
    
    // Optimize pixel ratio for performance
    const devicePixelRatio = window.devicePixelRatio || 1
    const backingStoreRatio = 1 // Modern browsers
    const ratio = Math.min(devicePixelRatio / backingStoreRatio, 2) // Cap at 2x
    
    if (performanceMode.value === 'low') {
      // Use lower pixel ratio for better performance
      canvas.width = canvas.clientWidth
      canvas.height = canvas.clientHeight
    } else {
      canvas.width = canvas.clientWidth * ratio
      canvas.height = canvas.clientHeight * ratio
      ctx.scale(ratio, ratio)
    }
  }
  
  // Debounced chart update function
  const debouncedChartUpdate = debounce((updateFn: () => void) => {
    measureRenderTime(updateFn)
    throttledMemoryMeasure()
  }, performanceMode.value === 'high' ? 16 : 100)
  
  onMounted(() => {
    measureFrameRate()
    measureMemoryUsage()
  })
  
  onUnmounted(() => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
  })
  
  return {
    metrics,
    isLowPerformance,
    performanceMode,
    optimizationStrategies,
    downsampleData,
    aggregateData,
    optimizeCanvas,
    debouncedChartUpdate,
    measureRenderTime
  }
}
```

### Memory Management for Large Datasets
```typescript
// src/composables/useChartMemory.ts
import { ref, computed, onUnmounted } from 'vue'

export interface MemoryConfig {
  maxDataPoints: number
  memoryThreshold: number // MB
  gcInterval: number // ms
}

export function useChartMemory(config: MemoryConfig) {
  const dataCache = new Map<string, any>()
  const memoryUsage = ref(0)
  const isMemoryPressure = ref(false)
  
  let gcInterval: NodeJS.Timeout
  
  function getCurrentMemoryUsage(): number {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      return memory.usedJSHeapSize / (1024 * 1024) // MB
    }
    return 0
  }
  
  function updateMemoryUsage() {
    memoryUsage.value = getCurrentMemoryUsage()
    isMemoryPressure.value = memoryUsage.value > config.memoryThreshold
  }
  
  // Garbage collection for chart data
  function collectGarbage() {
    updateMemoryUsage()
    
    if (isMemoryPressure.value) {
      // Clear old cache entries
      const now = Date.now()
      const maxAge = 5 * 60 * 1000 // 5 minutes
      
      for (const [key, value] of dataCache.entries()) {
        if (value.timestamp && now - value.timestamp > maxAge) {
          dataCache.delete(key)
        }
      }
      
      // Force garbage collection if available
      if ('gc' in window) {
        (window as any).gc()
      }
    }
  }
  
  // Data management functions
  function cacheData(key: string, data: any) {
    dataCache.set(key, {
      data,
      timestamp: Date.now(),
      size: JSON.stringify(data).length
    })
  }
  
  function getCachedData(key: string) {
    const cached = dataCache.get(key)
    if (cached) {
      // Update access time
      cached.timestamp = Date.now()
      return cached.data
    }
    return null
  }
  
  function clearCache() {
    dataCache.clear()
  }
  
  // Optimize data structure for memory efficiency
  function optimizeDataStructure(data: any[]): any[] {
    if (!isMemoryPressure.value) return data
    
    // Remove unnecessary properties
    return data.map(item => {
      const optimized: any = {
        timestamp: item.timestamp,
        value: item.value
      }
      
      // Only keep essential metadata
      if (item.metadata?.essential) {
        optimized.metadata = { essential: item.metadata.essential }
      }
      
      return optimized
    })
  }
  
  // Pagination for large datasets
  function paginateData<T>(data: T[], pageSize: number, page: number): T[] {
    const start = page * pageSize
    const end = start + pageSize
    return data.slice(start, end)
  }
  
  // Virtual scrolling helper
  function getVisibleDataRange(data: any[], viewportStart: number, viewportEnd: number, itemHeight: number) {
    const startIndex = Math.floor(viewportStart / itemHeight)
    const endIndex = Math.ceil(viewportEnd / itemHeight)
    const visibleData = data.slice(startIndex, endIndex + 1)
    
    return {
      data: visibleData,
      startIndex,
      endIndex,
      totalHeight: data.length * itemHeight
    }
  }
  
  // Start garbage collection interval
  gcInterval = setInterval(collectGarbage, config.gcInterval)
  
  onUnmounted(() => {
    if (gcInterval) {
      clearInterval(gcInterval)
    }
    clearCache()
  })
  
  return {
    memoryUsage,
    isMemoryPressure,
    cacheData,
    getCachedData,
    clearCache,
    optimizeDataStructure,
    paginateData,
    getVisibleDataRange,
    collectGarbage
  }
}
```

## Responsive Chart Container

```vue
<!-- src/components/charts/ResponsiveChartContainer.vue -->
<template>
  <div 
    ref="containerRef"
    :class="[
      'responsive-chart-container',
      `breakpoint-${currentBreakpoint}`,
      { 'mobile-optimized': isMobileOptimized }
    ]"
    :style="containerStyle"
  >
    <slot 
      :width="dimensions.width"
      :height="dimensions.height"
      :breakpoint="currentBreakpoint"
      :is-mobile="isMobile"
      :chart-config="responsiveChartConfig"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useElementSize } from '@vueuse/core'
import { debounce } from 'lodash-es'

interface Props {
  aspectRatio?: number
  minHeight?: number
  maxHeight?: number
  mobileBreakpoint?: number
  tabletBreakpoint?: number
  desktopBreakpoint?: number
  mobileOptimizations?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  aspectRatio: 16 / 9,
  minHeight: 200,
  maxHeight: 600,
  mobileBreakpoint: 768,
  tabletBreakpoint: 1024,
  desktopBreakpoint: 1280,
  mobileOptimizations: true
})

const containerRef = ref<HTMLElement>()
const { width, height } = useElementSize(containerRef)

const windowWidth = ref(window.innerWidth)
const windowHeight = ref(window.innerHeight)

const currentBreakpoint = computed(() => {
  if (windowWidth.value < props.mobileBreakpoint) return 'mobile'
  if (windowWidth.value < props.tabletBreakpoint) return 'tablet'
  if (windowWidth.value < props.desktopBreakpoint) return 'desktop'
  return 'wide'
})

const isMobile = computed(() => currentBreakpoint.value === 'mobile')
const isTablet = computed(() => currentBreakpoint.value === 'tablet')

const isMobileOptimized = computed(() => 
  props.mobileOptimizations && (isMobile.value || isTablet.value)
)

const dimensions = computed(() => {
  const containerWidth = width.value || 0
  let calculatedHeight = containerWidth / props.aspectRatio
  
  // Apply height constraints
  calculatedHeight = Math.max(props.minHeight, calculatedHeight)
  calculatedHeight = Math.min(props.maxHeight, calculatedHeight)
  
  // Mobile-specific adjustments
  if (isMobile.value) {
    calculatedHeight = Math.min(calculatedHeight, windowHeight.value * 0.4)
  }
  
  return {
    width: containerWidth,
    height: calculatedHeight
  }
})

const containerStyle = computed(() => ({
  width: '100%',
  height: `${dimensions.value.height}px`,
  minHeight: `${props.minHeight}px`,
  maxHeight: `${props.maxHeight}px`
}))

// Responsive chart configuration
const responsiveChartConfig = computed(() => {
  const baseConfig = {
    responsive: true,
    maintainAspectRatio: false,
    devicePixelRatio: window.devicePixelRatio || 1
  }
  
  // Mobile optimizations
  if (isMobileOptimized.value) {
    return {
      ...baseConfig,
      plugins: {
        legend: {
          position: 'bottom' as const,
          labels: {
            boxWidth: 12,
            padding: 10,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          mode: 'index' as const,
          intersect: false,
          position: 'nearest' as const,
          caretSize: 8,
          cornerRadius: 4,
          padding: 8,
          titleFont: {
            size: 12
          },
          bodyFont: {
            size: 11
          }
        }
      },
      scales: {
        x: {
          ticks: {
            maxTicksLimit: isMobile.value ? 5 : 8,
            font: {
              size: isMobile.value ? 10 : 12
            }
          },
          grid: {
            display: !isMobile.value
          }
        },
        y: {
          ticks: {
            maxTicksLimit: isMobile.value ? 5 : 8,
            font: {
              size: isMobile.value ? 10 : 12
            }
          },
          grid: {
            display: !isMobile.value
          }
        }
      },
      elements: {
        point: {
          radius: isMobile.value ? 2 : 4,
          hoverRadius: isMobile.value ? 4 : 6
        },
        line: {
          borderWidth: isMobile.value ? 1 : 2
        }
      }
    }
  }
  
  return baseConfig
})

// Debounced window resize handler
const debouncedResize = debounce(() => {
  windowWidth.value = window.innerWidth
  windowHeight.value = window.innerHeight
}, 100)

// Handle window resize
function handleResize() {
  debouncedResize()
}

// Handle orientation change
function handleOrientationChange() {
  // Delay to allow for orientation change to complete
  setTimeout(() => {
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight
  }, 100)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  window.addEventListener('orientationchange', handleOrientationChange)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('orientationchange', handleOrientationChange)
})

// Watch for container size changes
watch([width, height], () => {
  // Trigger chart resize if needed
  const event = new CustomEvent('chartResize', {
    detail: { width: width.value, height: height.value }
  })
  containerRef.value?.dispatchEvent(event)
})
</script>

<style scoped>
.responsive-chart-container {
  position: relative;
  overflow: hidden;
}

.breakpoint-mobile {
  --chart-padding: 8px;
  --chart-font-size: 12px;
}

.breakpoint-tablet {
  --chart-padding: 12px;
  --chart-font-size: 14px;
}

.breakpoint-desktop {
  --chart-padding: 16px;
  --chart-font-size: 16px;
}

.breakpoint-wide {
  --chart-padding: 20px;
  --chart-font-size: 16px;
}

.mobile-optimized {
  touch-action: pan-x pan-y;
}

@media (max-width: 768px) {
  .responsive-chart-container {
    margin: 0 -16px;
    padding: 0 16px;
  }
}
</style>
```

## Accessibility Features

### Screen Reader Support
```vue
<!-- src/components/charts/AccessibleChart.vue -->
<template>
  <div class="accessible-chart" role="img" :aria-label="ariaLabel">
    <!-- Visual Chart -->
    <div class="chart-visual" aria-hidden="true">
      <slot />
    </div>
    
    <!-- Screen Reader Alternative -->
    <div class="sr-only">
      <h3>{{ title }} Chart Data</h3>
      <p>{{ description }}</p>
      
      <!-- Data Table for Screen Readers -->
      <table>
        <caption>{{ title }} data in tabular format</caption>
        <thead>
          <tr>
            <th scope="col">{{ xAxisLabel }}</th>
            <th scope="col">{{ yAxisLabel }}</th>
            <th scope="col">Change</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(point, index) in accessibleData" :key="index">
            <td>{{ formatXValue(point.x) }}</td>
            <td>{{ formatYValue(point.y) }}</td>
            <td>{{ formatChange(point.change) }}</td>
          </tr>
        </tbody>
      </table>
      
      <!-- Summary Statistics -->
      <div class="chart-summary">
        <h4>Summary Statistics</h4>
        <ul>
          <li>Minimum value: {{ formatYValue(stats.min) }}</li>
          <li>Maximum value: {{ formatYValue(stats.max) }}</li>
          <li>Average value: {{ formatYValue(stats.average) }}</li>
          <li>Total data points: {{ stats.count }}</li>
          <li>Trend: {{ stats.trend }}</li>
        </ul>
      </div>
    </div>
    
    <!-- Keyboard Navigation -->
    <div 
      v-if="enableKeyboardNavigation"
      class="chart-keyboard-nav"
      tabindex="0"
      role="application"
      aria-label="Chart navigation. Use arrow keys to navigate data points."
      @keydown="handleKeyNavigation"
    >
      <span class="sr-only">{{ keyboardInstructions }}</span>
      <div 
        v-if="selectedDataPoint"
        class="sr-only"
        aria-live="polite"
        aria-atomic="true"
      >
        {{ announceDataPoint(selectedDataPoint) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { format } from 'date-fns'

interface DataPoint {
  x: any
  y: number
  change?: number
}

interface Props {
  title: string
  description: string
  data: DataPoint[]
  xAxisLabel: string
  yAxisLabel: string
  enableKeyboardNavigation?: boolean
  format?: 'number' | 'currency' | 'percentage'
}

const props = withDefaults(defineProps<Props>(), {
  enableKeyboardNavigation: true,
  format: 'number'
})

const selectedDataPoint = ref<DataPoint | null>(null)
const selectedIndex = ref(0)

const ariaLabel = computed(() => {
  return `${props.title} chart showing ${props.description}. Contains ${props.data.length} data points.`
})

const accessibleData = computed(() => {
  return props.data.map((point, index) => {
    const previousPoint = index > 0 ? props.data[index - 1] : null
    const change = previousPoint ? point.y - previousPoint.y : 0
    
    return {
      ...point,
      change
    }
  })
})

const stats = computed(() => {
  const values = props.data.map(d => d.y)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const average = values.reduce((sum, val) => sum + val, 0) / values.length
  const trend = values.length > 1 ? 
    (values[values.length - 1] > values[0] ? 'increasing' : 'decreasing') : 
    'stable'
  
  return {
    min,
    max,
    average,
    count: values.length,
    trend
  }
})

const keyboardInstructions = computed(() => {
  return 'Use left and right arrow keys to navigate between data points. Press Enter to announce current data point details.'
})

function formatXValue(value: any): string {
  if (value instanceof Date) {
    return format(value, 'MMM dd, yyyy HH:mm')
  }
  return String(value)
}

function formatYValue(value: number): string {
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    
    case 'percentage':
      return `${value.toFixed(1)}%`
    
    default:
      return value.toLocaleString()
  }
}

function formatChange(change: number): string {
  if (change === 0) return 'No change'
  const direction = change > 0 ? 'increase' : 'decrease'
  return `${Math.abs(change).toFixed(2)} ${direction}`
}

function announceDataPoint(point: DataPoint): string {
  return `Data point ${selectedIndex.value + 1} of ${props.data.length}: ${formatXValue(point.x)}, ${formatYValue(point.y)}`
}

function handleKeyNavigation(event: KeyboardEvent) {
  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      if (selectedIndex.value > 0) {
        selectedIndex.value--
        selectedDataPoint.value = props.data[selectedIndex.value]
      }
      break
    
    case 'ArrowRight':
      event.preventDefault()
      if (selectedIndex.value < props.data.length - 1) {
        selectedIndex.value++
        selectedDataPoint.value = props.data[selectedIndex.value]
      }
      break
    
    case 'Home':
      event.preventDefault()
      selectedIndex.value = 0
      selectedDataPoint.value = props.data[0]
      break
    
    case 'End':
      event.preventDefault()
      selectedIndex.value = props.data.length - 1
      selectedDataPoint.value = props.data[selectedIndex.value]
      break
    
    case 'Enter':
    case ' ':
      event.preventDefault()
      if (selectedDataPoint.value) {
        // Announce detailed information
        const announcement = `${announceDataPoint(selectedDataPoint.value)}. ${props.yAxisLabel}: ${formatYValue(selectedDataPoint.value.y)}`
        announceToScreenReader(announcement)
      }
      break
  }
}

function announceToScreenReader(message: string) {
  const announcement = document.createElement('div')
  announcement.setAttribute('aria-live', 'assertive')
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message
  
  document.body.appendChild(announcement)
  
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

// Initialize keyboard navigation
onMounted(() => {
  if (props.enableKeyboardNavigation && props.data.length > 0) {
    selectedDataPoint.value = props.data[0]
    selectedIndex.value = 0
  }
})
</script>

<style scoped>
.accessible-chart {
  position: relative;
}

.chart-keyboard-nav {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  outline: none;
}

.chart-keyboard-nav:focus {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.chart-summary {
  margin-top: 16px;
}

.chart-summary ul {
  list-style: none;
  padding: 0;
}

.chart-summary li {
  margin-bottom: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}
</style>
```

## Advanced Export System

### Multi-Format Export Service
```typescript
// src/services/chart-export.ts
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import * as XLSX from 'xlsx'

export interface ExportOptions {
  format: 'png' | 'pdf' | 'csv' | 'xlsx' | 'json'
  quality?: number
  width?: number
  height?: number
  filename?: string
  includeMetadata?: boolean
}

export interface ChartExportData {
  title: string
  data: any[]
  metadata: {
    generatedAt: Date
    chartType: string
    dataPoints: number
    timeRange?: { start: Date; end: Date }
  }
}

export class ChartExportService {
  async exportChart(element: HTMLElement, data: ChartExportData, options: ExportOptions): Promise<void> {
    const filename = options.filename || `chart-${Date.now()}`
    
    switch (options.format) {
      case 'png':
        await this.exportAsPNG(element, filename, options)
        break
      case 'pdf':
        await this.exportAsPDF(element, filename, options)
        break
      case 'csv':
        await this.exportAsCSV(data, filename, options)
        break
      case 'xlsx':
        await this.exportAsExcel(data, filename, options)
        break
      case 'json':
        await this.exportAsJSON(data, filename, options)
        break
      default:
        throw new Error(`Unsupported export format: ${options.format}`)
    }
  }
  
  private async exportAsPNG(element: HTMLElement, filename: string, options: ExportOptions): Promise<void> {
    const canvas = await html2canvas(element, {
      backgroundColor: '#ffffff',
      scale: options.quality || 2,
      width: options.width,
      height: options.height,
      useCORS: true,
      allowTaint: false
    })
    
    const link = document.createElement('a')
    link.download = `${filename}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }
  
  private async exportAsPDF(element: HTMLElement, filename: string, options: ExportOptions): Promise<void> {
    const canvas = await html2canvas(element, {
      backgroundColor: '#ffffff',
      scale: options.quality || 1,
      width: options.width,
      height: options.height,
      useCORS: true,
      allowTaint: false
    })
    
    const imgWidth = 210 // A4 width in mm
    const pageHeight = 295 // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    
    const pdf = new jsPDF('p', 'mm', 'a4')
    let position = 0
    
    // Add metadata if requested
    if (options.includeMetadata) {
      pdf.setFontSize(16)
      pdf.text('Chart Export', 20, 20)
      pdf.setFontSize(10)
      pdf.text(`Generated: ${new Date().toLocaleString()}`, 20, 30)
      position = 40
    }
    
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
    
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }
    
    pdf.save(`${filename}.pdf`)
  }
  
  private async exportAsCSV(data: ChartExportData, filename: string, options: ExportOptions): Promise<void> {
    const headers = this.extractHeaders(data.data)
    const csvContent = this.convertToCSV(data.data, headers, options.includeMetadata ? data.metadata : undefined)
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.download = `${filename}.csv`
    link.href = URL.createObjectURL(blob)
    link.click()
  }
  
  private async exportAsExcel(data: ChartExportData, filename: string, options: ExportOptions): Promise<void> {
    const workbook = XLSX.utils.book_new()
    
    // Main data sheet
    const worksheet = XLSX.utils.json_to_sheet(data.data)
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Chart Data')
    
    // Metadata sheet if requested
    if (options.includeMetadata) {
      const metadataSheet = XLSX.utils.json_to_sheet([
        { Property: 'Title', Value: data.title },
        { Property: 'Generated At', Value: data.metadata.generatedAt.toISOString() },
        { Property: 'Chart Type', Value: data.metadata.chartType },
        { Property: 'Data Points', Value: data.metadata.dataPoints },
        { Property: 'Time Range Start', Value: data.metadata.timeRange?.start?.toISOString() || 'N/A' },
        { Property: 'Time Range End', Value: data.metadata.timeRange?.end?.toISOString() || 'N/A' }
      ])
      XLSX.utils.book_append_sheet(workbook, metadataSheet, 'Metadata')
    }
    
    XLSX.writeFile(workbook, `${filename}.xlsx`)
  }
  
  private async exportAsJSON(data: ChartExportData, filename: string, options: ExportOptions): Promise<void> {
    const exportData = options.includeMetadata ? data : { data: data.data }
    const jsonContent = JSON.stringify(exportData, null, 2)
    
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
    const link = document.createElement('a')
    link.download = `${filename}.json`
    link.href = URL.createObjectURL(blob)
    link.click()
  }
  
  private extractHeaders(data: any[]): string[] {
    if (data.length === 0) return []
    
    const firstItem = data[0]
    return Object.keys(firstItem)
  }
  
  private convertToCSV(data: any[], headers: string[], metadata?: any): string {
    const csvRows: string[] = []
    
    // Add metadata as comments if provided
    if (metadata) {
      csvRows.push(`# Chart Export: ${metadata.generatedAt}`)
      csvRows.push(`# Chart Type: ${metadata.chartType}`)
      csvRows.push(`# Data Points: ${metadata.dataPoints}`)
      csvRows.push('#')
    }
    
    // Add headers
    csvRows.push(headers.join(','))
    
    // Add data rows
    data.forEach(item => {
      const row = headers.map(header => {
        const value = item[header]
        if (value === null || value === undefined) return ''
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return String(value)
      })
      csvRows.push(row.join(','))
    })
    
    return csvRows.join('\n')
  }
}

// Export service instance
export const chartExportService = new ChartExportService()
```

This comprehensive enhancement adds:

1. **Real-time WebSocket Integration**: Complete WebSocket service with throttling, buffering, and performance monitoring
2. **Performance Optimization**: Memory management, frame rate monitoring, and adaptive performance modes
3. **Responsive Design**: Breakpoint-aware containers with mobile optimizations
4. **Accessibility Features**: Screen reader support, keyboard navigation, and WCAG 2.1 AA compliance
5. **Advanced Export System**: Multi-format export with metadata support
6. **Memory Management**: Garbage collection and data structure optimization for large datasets
7. **Mobile Optimization**: Touch-friendly interfaces with responsive layouts
8. **Professional Error Handling**: Comprehensive error states and recovery mechanisms

The implementation provides a production-ready data visualization system that scales from small dashboards to enterprise-level analytics platforms while maintaining excellent performance and accessibility standards.