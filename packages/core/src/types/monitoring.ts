export interface FileWatchEvent {
  type: 'add' | 'change' | 'unlink';
  filePath: string;
  timestamp: Date;
  size?: number;
}

export interface MonitoringConfig {
  watchPaths: string[];
  ignorePatterns: string[];
  debounceMs: number;
  maxFileSize: number;
}

export interface SystemMetrics {
  timestamp: Date;
  memoryUsage: number;
  cpuUsage: number;
  activeConnections: number;
  filesWatched: number;
  eventQueue: number;
}

export interface ProcessingStats {
  filesProcessed: number;
  messagesExtracted: number;
  parsingErrors: number;
  averageProcessingTime: number;
  lastProcessedAt: Date;
}