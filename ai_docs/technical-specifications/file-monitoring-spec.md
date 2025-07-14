# 📁 File System Monitoring Technical Specification

## 🎯 **Executive Summary**

This specification defines the technical requirements, architecture, and implementation details for the Claude Code Observatory file system monitoring subsystem. The system monitors `~/.claude/projects/` for JSONL transcript files in real-time, providing sub-100ms detection latency and supporting thousands of concurrent files without performance degradation.

---

## 📋 **Technical Requirements**

### **FR001: Real-Time File Detection**

#### **Performance Requirements**
- **Detection Latency:** <100ms (95th percentile)
- **File Change Detection:** <50ms (95th percentile)
- **Concurrent File Capacity:** 1000+ files without degradation
- **Cross-Platform Support:** Windows, macOS, Linux

#### **Functional Requirements**
```typescript
interface FileMonitoringRequirements {
  detectionLatency: '<100ms';
  fileTypes: ['.jsonl'];
  watchPath: '~/.claude/projects/**/*.jsonl';
  concurrent: 'unlimited';
  errorRecovery: 'automatic';
  crossPlatform: true;
}
```

### **FR002: Incremental File Reading**

#### **Performance Requirements**
- **Maximum File Size:** 100MB per file
- **Chunk Size:** 64KB default
- **Memory Efficiency:** O(1) memory usage per file
- **Encoding Support:** UTF-8 with BOM detection

#### **Functional Requirements**
```typescript
interface IncrementalReading {
  positionTracking: Map<string, FilePosition>;
  chunkSize: '64KB';
  encoding: 'utf-8';
  lineBuffering: true;
  errorHandling: 'skip-malformed';
  resumeAfterRestart: true;
}

interface FilePosition {
  filePath: string;
  byteOffset: number;
  lineNumber: number;
  lastModified: number;
  checksum: string;
}
```

---

## 🏗️ **System Architecture**

### **Component Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    File Monitoring System                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Watcher   │  │   Parser    │  │    Event Router     │  │
│  │   Service   │──│   Service   │──│                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                       │         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Chokidar    │  │ JSONL Line  │  │   WebSocket         │  │
│  │ FileWatcher │  │ Processor   │  │   Broadcaster       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                       │         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Position    │  │ Message     │  │    Database         │  │
│  │ Tracker     │  │ Validator   │  │    Writer           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **Core Components**

#### **1. FileSystemWatcher Service**

```typescript
class FileSystemWatcher extends EventEmitter {
  private watcher: FSWatcher | null = null;
  private fileStates: Map<string, FileState> = new Map();
  private config: WatcherConfig;

  constructor(config: WatcherConfig) {
    super();
    this.config = {
      watchPath: config.watchPath || '~/.claude/projects/**/*.jsonl',
      ignoreInitial: false,
      persistent: true,
      usePolling: false,
      interval: 100,
      binaryInterval: 300,
      awaitWriteFinish: {
        stabilityThreshold: 100,
        pollInterval: 100
      },
      ...config
    };
  }

  async start(): Promise<void> {
    const expandedPath = this.expandPath(this.config.watchPath);
    
    this.watcher = chokidar.watch(expandedPath, {
      ignored: this.config.ignored,
      persistent: this.config.persistent,
      ignoreInitial: this.config.ignoreInitial,
      followSymlinks: true,
      cwd: process.cwd(),
      disableGlobbing: false,
      usePolling: this.config.usePolling,
      interval: this.config.interval,
      binaryInterval: this.config.binaryInterval,
      alwaysStat: false,
      depth: 99,
      awaitWriteFinish: this.config.awaitWriteFinish,
      ignorePermissionErrors: false,
      atomic: true
    });

    this.setupEventHandlers();
    await this.waitForReady();
  }

  private setupEventHandlers(): void {
    this.watcher!
      .on('add', this.handleFileAdded.bind(this))
      .on('change', this.handleFileChanged.bind(this))
      .on('unlink', this.handleFileRemoved.bind(this))
      .on('addDir', this.handleDirectoryAdded.bind(this))
      .on('unlinkDir', this.handleDirectoryRemoved.bind(this))
      .on('error', this.handleError.bind(this))
      .on('ready', () => this.emit('ready'));
  }

  private async handleFileChanged(filePath: string, stats?: fs.Stats): Promise<void> {
    try {
      const fileState = this.fileStates.get(filePath);
      const currentStats = stats || await fs.stat(filePath);
      
      if (!fileState) {
        // First time seeing this file
        await this.handleFileAdded(filePath, currentStats);
        return;
      }

      // Check if file was actually modified
      if (fileState.lastModified >= currentStats.mtime.getTime()) {
        return; // No actual change
      }

      const newLines = await this.readNewLines(filePath, fileState.position);
      
      if (newLines.length > 0) {
        const event: FileChangeEvent = {
          type: 'file_changed',
          filePath,
          projectPath: this.extractProjectPath(filePath),
          sessionId: this.extractSessionId(filePath),
          newLines,
          timestamp: Date.now(),
          fileSize: currentStats.size,
          bytesRead: newLines.reduce((acc, line) => acc + Buffer.byteLength(line, 'utf8'), 0)
        };

        // Update file state
        this.fileStates.set(filePath, {
          position: fileState.position + event.bytesRead,
          lastModified: currentStats.mtime.getTime(),
          size: currentStats.size,
          checksum: this.calculateChecksum(newLines.join('\n'))
        });

        this.emit('file_changed', event);
      }
    } catch (error) {
      this.handleFileError(filePath, error);
    }
  }

  private async readNewLines(filePath: string, fromPosition: number): Promise<string[]> {
    const fd = await fs.open(filePath, 'r');
    const lines: string[] = [];
    const buffer = Buffer.alloc(this.config.chunkSize || 65536);
    let position = fromPosition;
    let remainder = '';

    try {
      while (true) {
        const { bytesRead } = await fd.read(buffer, 0, buffer.length, position);
        
        if (bytesRead === 0) {
          // End of file
          if (remainder.length > 0) {
            lines.push(remainder);
          }
          break;
        }

        const chunk = buffer.subarray(0, bytesRead).toString('utf8');
        const content = remainder + chunk;
        const lineArray = content.split('\n');
        
        // Keep the last incomplete line as remainder
        remainder = lineArray.pop() || '';
        
        lines.push(...lineArray);
        position += bytesRead;

        // Prevent memory exhaustion
        if (lines.length > 10000) {
          throw new Error(`Too many lines in single read operation: ${lines.length}`);
        }
      }
    } finally {
      await fd.close();
    }

    return lines.filter(line => line.trim().length > 0);
  }
}
```

#### **2. JSONL Parser Service**

```typescript
class JSONLParser {
  static parseMessage(rawLine: string): ParsedMessage | null {
    try {
      const rawMessage = JSON.parse(rawLine.trim());
      
      // Validate required fields
      if (!this.isValidMessage(rawMessage)) {
        return null;
      }

      return this.normalizeMessage(rawMessage);
    } catch (error) {
      // Skip malformed JSON lines
      return null;
    }
  }

  private static isValidMessage(message: any): boolean {
    return (
      message &&
      typeof message.uuid === 'string' &&
      typeof message.sessionId === 'string' &&
      typeof message.timestamp === 'string' &&
      ['user', 'assistant', 'system'].includes(message.type) &&
      message.message &&
      typeof message.message.role === 'string' &&
      (typeof message.message.content === 'string' || Array.isArray(message.message.content))
    );
  }

  private static normalizeMessage(rawMessage: any): ParsedMessage {
    const toolUsage = this.extractToolUsage(rawMessage);
    
    return {
      id: rawMessage.uuid,
      conversationId: this.generateConversationId(rawMessage.sessionId),
      sessionId: rawMessage.sessionId,
      timestamp: new Date(rawMessage.timestamp).getTime(),
      type: rawMessage.type,
      content: this.extractContent(rawMessage.message.content),
      toolUsage,
      parentId: rawMessage.parentUuid || null,
      metadata: {
        isSidechain: rawMessage.isSidechain || false,
        userType: rawMessage.userType,
        cwd: rawMessage.cwd,
        version: rawMessage.version,
        requestId: rawMessage.requestId
      }
    };
  }

  private static extractToolUsage(message: any): ToolUsage[] {
    const usage: ToolUsage[] = [];
    
    if (Array.isArray(message.message.content)) {
      for (const block of message.message.content) {
        if (block.type === 'tool_use') {
          usage.push({
            toolId: block.id,
            toolName: block.name,
            input: block.input,
            status: 'pending'
          });
        } else if (block.type === 'tool_result') {
          const existingTool = usage.find(tool => tool.toolId === block.tool_use_id);
          if (existingTool) {
            existingTool.output = block.content;
            existingTool.status = block.is_error ? 'error' : 'success';
          }
        }
      }
    }

    return usage;
  }

  private static extractContent(content: string | any[]): string {
    if (typeof content === 'string') {
      return content;
    }

    if (Array.isArray(content)) {
      return content
        .filter(block => block.type === 'text')
        .map(block => block.text)
        .join('\n');
    }

    return '';
  }
}
```

---

## 🔧 **Implementation Details**

### **Error Handling and Recovery**

```typescript
class ErrorRecoveryManager {
  private retryAttempts: Map<string, number> = new Map();
  private maxRetries = 5;
  private backoffMultiplier = 2;
  private baseDelay = 1000;

  async handleFileError(filePath: string, error: Error): Promise<void> {
    const attempts = this.retryAttempts.get(filePath) || 0;
    
    if (attempts >= this.maxRetries) {
      this.emit('file_error_permanent', { filePath, error, attempts });
      this.retryAttempts.delete(filePath);
      return;
    }

    const delay = this.baseDelay * Math.pow(this.backoffMultiplier, attempts);
    this.retryAttempts.set(filePath, attempts + 1);

    setTimeout(async () => {
      try {
        await this.retryFileOperation(filePath);
        this.retryAttempts.delete(filePath);
      } catch (retryError) {
        await this.handleFileError(filePath, retryError);
      }
    }, delay);
  }

  private async retryFileOperation(filePath: string): Promise<void> {
    // Re-attempt file reading with fresh state
    const stats = await fs.stat(filePath);
    // ... retry logic
  }
}
```

### **Performance Monitoring**

```typescript
interface PerformanceMetrics {
  detectionLatency: number[];
  processingLatency: number[];
  throughputMbps: number;
  errorRate: number;
  memoryUsageMb: number;
  fileCount: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    detectionLatency: [],
    processingLatency: [],
    throughputMbps: 0,
    errorRate: 0,
    memoryUsageMb: 0,
    fileCount: 0
  };

  recordDetectionLatency(latency: number): void {
    this.metrics.detectionLatency.push(latency);
    
    // Keep only last 1000 measurements
    if (this.metrics.detectionLatency.length > 1000) {
      this.metrics.detectionLatency.shift();
    }
  }

  getPercentile(array: number[], percentile: number): number {
    const sorted = [...array].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index] || 0;
  }

  generateReport(): PerformanceReport {
    return {
      detection95thPercentile: this.getPercentile(this.metrics.detectionLatency, 95),
      processing95thPercentile: this.getPercentile(this.metrics.processingLatency, 95),
      avgThroughput: this.metrics.throughputMbps,
      errorRate: this.metrics.errorRate,
      memoryUsage: this.metrics.memoryUsageMb,
      activeFiles: this.metrics.fileCount,
      timestamp: Date.now()
    };
  }
}
```

---

## 🔒 **Security Considerations**

### **File System Security**

```typescript
class SecurityValidator {
  private allowedPaths: Set<string> = new Set();
  private maxFileSize = 100 * 1024 * 1024; // 100MB
  private maxFilesPerDirectory = 10000;

  validateFilePath(filePath: string): boolean {
    const resolved = path.resolve(filePath);
    const claudeDir = path.resolve(os.homedir(), '.claude', 'projects');
    
    // Ensure file is within allowed directory
    if (!resolved.startsWith(claudeDir)) {
      return false;
    }

    // Check file extension
    if (!resolved.endsWith('.jsonl')) {
      return false;
    }

    // Prevent directory traversal
    if (resolved.includes('..')) {
      return false;
    }

    return true;
  }

  async validateFileSize(filePath: string): Promise<boolean> {
    try {
      const stats = await fs.stat(filePath);
      return stats.size <= this.maxFileSize;
    } catch {
      return false;
    }
  }

  sanitizeContent(content: string): string {
    // Remove potential script injection
    return content
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '');
  }
}
```

### **Data Validation**

```typescript
interface DataValidationRules {
  maxMessageSize: number;
  maxSessionDuration: number;
  allowedMessageTypes: string[];
  requiredFields: string[];
}

class DataValidator {
  private rules: DataValidationRules = {
    maxMessageSize: 1024 * 1024, // 1MB
    maxSessionDuration: 24 * 60 * 60 * 1000, // 24 hours
    allowedMessageTypes: ['user', 'assistant', 'system'],
    requiredFields: ['uuid', 'sessionId', 'timestamp', 'type', 'message']
  };

  validateMessage(message: any): ValidationResult {
    const errors: string[] = [];

    // Check required fields
    for (const field of this.rules.requiredFields) {
      if (!(field in message)) {
        errors.push(`Missing required field: ${field}`);
      }
    }

    // Validate message type
    if (!this.rules.allowedMessageTypes.includes(message.type)) {
      errors.push(`Invalid message type: ${message.type}`);
    }

    // Check message size
    const messageSize = JSON.stringify(message).length;
    if (messageSize > this.rules.maxMessageSize) {
      errors.push(`Message too large: ${messageSize} bytes`);
    }

    // Validate timestamp
    const timestamp = new Date(message.timestamp);
    if (isNaN(timestamp.getTime())) {
      errors.push(`Invalid timestamp: ${message.timestamp}`);
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}
```

---

## 📊 **Performance Benchmarks**

### **Load Testing Scenarios**

```typescript
interface LoadTestScenario {
  name: string;
  fileCount: number;
  updateFrequency: number; // updates per second
  fileSize: number; // bytes
  duration: number; // seconds
  expectedLatency: number; // milliseconds
}

const loadTestScenarios: LoadTestScenario[] = [
  {
    name: 'Light Load',
    fileCount: 10,
    updateFrequency: 1,
    fileSize: 1024,
    duration: 300,
    expectedLatency: 50
  },
  {
    name: 'Medium Load',
    fileCount: 100,
    updateFrequency: 10,
    fileSize: 10240,
    duration: 600,
    expectedLatency: 75
  },
  {
    name: 'Heavy Load',
    fileCount: 1000,
    updateFrequency: 100,
    fileSize: 102400,
    duration: 900,
    expectedLatency: 100
  },
  {
    name: 'Stress Test',
    fileCount: 5000,
    updateFrequency: 500,
    fileSize: 1048576,
    duration: 1800,
    expectedLatency: 200
  }
];
```

### **Performance Targets**

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Detection Latency | <100ms (95th percentile) | File system event to emit time |
| Processing Latency | <10ms per message | JSON parse to normalized message |
| Memory Usage | <1GB total | Process memory monitoring |
| CPU Usage | <20% average | System resource monitoring |
| Throughput | 10,000+ messages/sec | Messages processed per second |
| Error Rate | <0.1% | Failed operations / total operations |

---

## 🧪 **Testing Strategy**

### **Unit Tests**

```typescript
describe('FileSystemWatcher', () => {
  describe('File Detection', () => {
    it('should detect new files within 100ms', async () => {
      const watcher = new FileSystemWatcher(testConfig);
      const startTime = Date.now();
      
      await watcher.start();
      await createTestFile('test.jsonl');
      
      const event = await waitForEvent(watcher, 'file_added');
      const latency = Date.now() - startTime;
      
      expect(latency).toBeLessThan(100);
      expect(event.filePath).toContain('test.jsonl');
    });

    it('should handle concurrent file changes', async () => {
      const watcher = new FileSystemWatcher(testConfig);
      const events: FileChangeEvent[] = [];
      
      watcher.on('file_changed', (event) => events.push(event));
      await watcher.start();
      
      // Create 100 files simultaneously
      const promises = Array.from({ length: 100 }, (_, i) => 
        createTestFile(`test-${i}.jsonl`)
      );
      
      await Promise.all(promises);
      await waitForEvents(100);
      
      expect(events).toHaveLength(100);
      expect(events.every(e => e.type === 'file_changed')).toBe(true);
    });
  });

  describe('Incremental Reading', () => {
    it('should only read new lines', async () => {
      const filePath = await createTestFile('incremental.jsonl');
      const watcher = new FileSystemWatcher(testConfig);
      
      await watcher.start();
      await appendToFile(filePath, 'line 1\n');
      
      const event1 = await waitForEvent(watcher, 'file_changed');
      expect(event1.newLines).toEqual(['line 1']);
      
      await appendToFile(filePath, 'line 2\n');
      
      const event2 = await waitForEvent(watcher, 'file_changed');
      expect(event2.newLines).toEqual(['line 2']);
    });
  });
});
```

### **Integration Tests**

```typescript
describe('File Monitoring Integration', () => {
  it('should handle complete workflow', async () => {
    const watcher = new FileSystemWatcher(testConfig);
    const parser = new JSONLParser();
    const events: ParsedMessage[] = [];
    
    watcher.on('file_changed', (event) => {
      event.newLines.forEach(line => {
        const message = parser.parseMessage(line);
        if (message) events.push(message);
      });
    });
    
    await watcher.start();
    
    // Simulate Claude Code writing a conversation
    const conversation = [
      { uuid: '1', sessionId: 'session1', timestamp: new Date().toISOString(), type: 'user', message: { role: 'user', content: 'Hello' } },
      { uuid: '2', sessionId: 'session1', timestamp: new Date().toISOString(), type: 'assistant', message: { role: 'assistant', content: 'Hi there!' } }
    ];
    
    const filePath = await createTestFile('conversation.jsonl');
    for (const message of conversation) {
      await appendToFile(filePath, JSON.stringify(message) + '\n');
      await sleep(100);
    }
    
    await waitForEvents(2);
    
    expect(events).toHaveLength(2);
    expect(events[0].type).toBe('user');
    expect(events[1].type).toBe('assistant');
    expect(events[0].content).toBe('Hello');
    expect(events[1].content).toBe('Hi there!');
  });
});
```

### **Performance Tests**

```typescript
describe('Performance Benchmarks', () => {
  it('should meet latency requirements under load', async () => {
    const watcher = new FileSystemWatcher(testConfig);
    const monitor = new PerformanceMonitor();
    const latencies: number[] = [];
    
    watcher.on('file_changed', (event) => {
      const latency = Date.now() - event.timestamp;
      latencies.push(latency);
      monitor.recordDetectionLatency(latency);
    });
    
    await watcher.start();
    
    // Create 1000 files with updates
    for (let i = 0; i < 1000; i++) {
      const startTime = Date.now();
      await createTestFileWithContent(`test-${i}.jsonl`, generateTestMessage());
      // Don't wait - let them pile up
    }
    
    await waitForEvents(1000);
    
    const p95 = monitor.getPercentile(latencies, 95);
    expect(p95).toBeLessThan(100);
  });
});
```

---

## 🚀 **Deployment Configuration**

### **Production Configuration**

```typescript
const productionConfig: WatcherConfig = {
  watchPath: '~/.claude/projects/**/*.jsonl',
  chunkSize: 65536, // 64KB
  maxFileSize: 100 * 1024 * 1024, // 100MB
  maxFilesPerDirectory: 10000,
  awaitWriteFinish: {
    stabilityThreshold: 100,
    pollInterval: 100
  },
  usePolling: false, // Use native events
  interval: 100,
  binaryInterval: 300,
  ignored: [
    '**/.git/**',
    '**/node_modules/**',
    '**/.DS_Store',
    '**/Thumbs.db'
  ],
  performance: {
    maxRetries: 5,
    retryDelay: 1000,
    maxMemoryUsage: 1024 * 1024 * 1024, // 1GB
    monitoringInterval: 30000 // 30 seconds
  },
  logging: {
    level: 'info',
    destination: 'file',
    rotateSize: 100 * 1024 * 1024, // 100MB
    maxFiles: 10
  }
};
```

### **Development Configuration**

```typescript
const developmentConfig: WatcherConfig = {
  ...productionConfig,
  chunkSize: 4096, // Smaller chunks for testing
  awaitWriteFinish: {
    stabilityThreshold: 50,
    pollInterval: 50
  },
  logging: {
    level: 'debug',
    destination: 'console',
    includeStack: true
  },
  performance: {
    ...productionConfig.performance,
    monitoringInterval: 5000 // 5 seconds
  }
};
```

---

## 📈 **Monitoring and Observability**

### **Health Checks**

```typescript
class HealthChecker {
  async checkFileSystemHealth(): Promise<HealthStatus> {
    const checks = await Promise.allSettled([
      this.checkDirectoryAccess(),
      this.checkDiskSpace(),
      this.checkMemoryUsage(),
      this.checkWatcherStatus()
    ]);

    const results = checks.map((check, index) => ({
      name: ['directory_access', 'disk_space', 'memory_usage', 'watcher_status'][index],
      status: check.status === 'fulfilled' ? 'healthy' : 'unhealthy',
      details: check.status === 'fulfilled' ? check.value : check.reason
    }));

    const overallHealth = results.every(r => r.status === 'healthy') ? 'healthy' : 'unhealthy';

    return {
      status: overallHealth,
      checks: results,
      timestamp: Date.now()
    };
  }

  private async checkDirectoryAccess(): Promise<string> {
    const claudeDir = path.join(os.homedir(), '.claude', 'projects');
    await fs.access(claudeDir, fs.constants.R_OK | fs.constants.W_OK);
    return 'Directory accessible';
  }

  private async checkDiskSpace(): Promise<string> {
    const stats = await fs.statvfs(path.join(os.homedir(), '.claude'));
    const freeBytes = stats.bavail * stats.frsize;
    const freeGB = freeBytes / (1024 * 1024 * 1024);
    
    if (freeGB < 1) {
      throw new Error(`Low disk space: ${freeGB.toFixed(2)}GB remaining`);
    }
    
    return `${freeGB.toFixed(2)}GB free space available`;
  }
}
```

### **Metrics Collection**

```typescript
interface MetricsCollector {
  recordFileDetection(latency: number): void;
  recordProcessingTime(duration: number): void;
  recordError(error: Error, context: string): void;
  recordThroughput(messagesPerSecond: number): void;
  getMetrics(): SystemMetrics;
}

interface SystemMetrics {
  detectionLatency: LatencyMetrics;
  processingLatency: LatencyMetrics;
  throughput: ThroughputMetrics;
  errors: ErrorMetrics;
  system: SystemResourceMetrics;
}
```

---

This specification provides comprehensive technical guidance for implementing a production-ready file monitoring system that meets the performance, reliability, and security requirements of the Claude Code Observatory project.