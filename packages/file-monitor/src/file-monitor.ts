import { EventEmitter } from 'events';
import { join } from 'path';
import { ClaudeCodeWatcher, type WatcherConfig, type WatcherEvents } from './claude-watcher.js';
import { ConversationDiscovery, type DiscoveryResult } from './discovery.js';
import {
  type FileWatchEvent,
  type ClaudeCodeMessage,
  type SystemMetrics,
  type ProcessingStats
} from '@cco/core';

export interface FileMonitorConfig {
  enableDiscovery?: boolean;
  performInitialScan?: boolean;
  collectMetrics?: boolean;
  maxConcurrentFiles?: number;
  // Inherit watcher config fields
  claudeDir?: string;
  ignorePatterns?: string[];
  debounceMs?: number;
  awaitWriteFinish?: boolean | { stabilityThreshold: number; pollInterval: number };
  usePolling?: boolean;
  followSymlinks?: boolean;
  persistent?: boolean;
}

export interface FileMonitorEvents extends WatcherEvents {
  discoveryComplete: (result: DiscoveryResult) => void;
  metricsUpdate: (metrics: SystemMetrics) => void;
  processingStatsUpdate: (stats: ProcessingStats) => void;
}

export class FileMonitor extends EventEmitter {
  private watcher: ClaudeCodeWatcher;
  private discovery: ConversationDiscovery;
  private config: FileMonitorConfig & {
    enableDiscovery: boolean;
    performInitialScan: boolean;
    collectMetrics: boolean;
    maxConcurrentFiles: number;
    claudeDir: string;
    ignorePatterns: string[];
    debounceMs: number;
    awaitWriteFinish: boolean | { stabilityThreshold: number; pollInterval: number };
    usePolling: boolean;
    followSymlinks: boolean;
    persistent: boolean;
  };
  private metricsInterval: NodeJS.Timeout | null = null;
  private processingStats: ProcessingStats;

  constructor(config: FileMonitorConfig = {}) {
    super();

    this.config = {
      enableDiscovery: config.enableDiscovery !== undefined ? config.enableDiscovery : true,
      performInitialScan: config.performInitialScan !== undefined ? config.performInitialScan : true,
      collectMetrics: config.collectMetrics !== undefined ? config.collectMetrics : true,
      maxConcurrentFiles: config.maxConcurrentFiles || 1000,
      // Inherit watcher config with defaults
      claudeDir: config.claudeDir || join(require('os').homedir(), '.claude'),
      ignorePatterns: config.ignorePatterns || [],
      debounceMs: config.debounceMs || 100,
      awaitWriteFinish: config.awaitWriteFinish !== undefined ? config.awaitWriteFinish : true,
      usePolling: config.usePolling || false,
      followSymlinks: config.followSymlinks !== undefined ? config.followSymlinks : true,
      persistent: config.persistent !== undefined ? config.persistent : true
    };

    // Initialize components
    this.watcher = new ClaudeCodeWatcher(this.config);
    this.discovery = new ConversationDiscovery(this.config.claudeDir);

    // Initialize processing stats
    this.processingStats = {
      filesProcessed: 0,
      messagesExtracted: 0,
      parsingErrors: 0,
      averageProcessingTime: 0,
      lastProcessedAt: new Date()
    };

    // Set up event forwarding and processing
    this.setupEventHandlers();
  }

  /**
   * Start the file monitoring system
   */
  async start(): Promise<void> {
    try {
      // Perform initial discovery if enabled
      if (this.config.enableDiscovery && this.config.performInitialScan) {
        console.log('Performing initial conversation discovery...');
        const discoveryResult = await this.discovery.scanForConversations();
        this.emit('discoveryComplete', discoveryResult);
        console.log(`Discovered ${discoveryResult.conversations.length} conversations across ${discoveryResult.projects.length} projects`);
      }

      // Start file watching
      console.log('Starting file watcher...');
      await this.watcher.startWatching();

      // Start metrics collection if enabled
      if (this.config.collectMetrics) {
        this.startMetricsCollection();
      }

      console.log('File monitoring system started successfully');
    } catch (error) {
      throw new Error(`Failed to start file monitor: ${error}`);
    }
  }

  /**
   * Stop the file monitoring system
   */
  async stop(): Promise<void> {
    try {
      // Stop metrics collection
      if (this.metricsInterval) {
        clearInterval(this.metricsInterval);
        this.metricsInterval = null;
      }

      // Stop file watching
      await this.watcher.stopWatching();

      console.log('File monitoring system stopped');
    } catch (error) {
      throw new Error(`Failed to stop file monitor: ${error}`);
    }
  }

  /**
   * Get current monitoring status
   */
  getStatus() {
    return {
      watching: this.watcher.watching,
      watchedFiles: this.watcher.getWatchedFiles().length,
      discoveredProjects: this.watcher.getDiscoveredProjects().length,
      processingStats: this.processingStats
    };
  }

  /**
   * Trigger manual discovery scan
   */
  async performDiscovery(): Promise<DiscoveryResult> {
    const result = await this.discovery.scanForConversations();
    this.emit('discoveryComplete', result);
    return result;
  }

  /**
   * Get list of discovered projects
   */
  getDiscoveredProjects(): string[] {
    return this.watcher.getDiscoveredProjects();
  }

  /**
   * Get list of currently watched files
   */
  getWatchedFiles(): string[] {
    return this.watcher.getWatchedFiles();
  }

  private setupEventHandlers(): void {
    // Forward watcher events with processing stats updates
    this.watcher.on('fileAdded', (event) => {
      this.updateProcessingStats(event.messages?.length || 0, false);
      this.emit('fileAdded', event);
    });

    this.watcher.on('fileChanged', (event) => {
      this.updateProcessingStats(event.newLines?.length || 0, false);
      this.emit('fileChanged', event);
    });

    this.watcher.on('fileRemoved', (event) => {
      this.emit('fileRemoved', event);
    });

    this.watcher.on('error', (error) => {
      this.updateProcessingStats(0, true);
      this.emit('error', error);
    });

    this.watcher.on('ready', () => {
      this.emit('ready');
    });

    this.watcher.on('projectDiscovered', (projectPath) => {
      this.emit('projectDiscovered', projectPath);
    });
  }

  private updateProcessingStats(messageCount: number, isError: boolean): void {
    const now = new Date();
    const timeSinceLastProcessed = now.getTime() - this.processingStats.lastProcessedAt.getTime();

    // Update stats
    this.processingStats.filesProcessed += 1;
    this.processingStats.messagesExtracted += messageCount;
    this.processingStats.lastProcessedAt = now;

    if (isError) {
      this.processingStats.parsingErrors += 1;
    }

    // Update average processing time (simple moving average)
    if (this.processingStats.filesProcessed > 1) {
      this.processingStats.averageProcessingTime = 
        (this.processingStats.averageProcessingTime * (this.processingStats.filesProcessed - 1) + timeSinceLastProcessed) 
        / this.processingStats.filesProcessed;
    } else {
      this.processingStats.averageProcessingTime = timeSinceLastProcessed;
    }

    // Emit stats update
    this.emit('processingStatsUpdate', { ...this.processingStats });
  }

  private startMetricsCollection(): void {
    // Collect system metrics every 30 seconds
    this.metricsInterval = setInterval(() => {
      try {
        const metrics: SystemMetrics = {
          timestamp: new Date(),
          memoryUsage: process.memoryUsage().heapUsed,
          cpuUsage: process.cpuUsage().user / 1000000, // Convert to seconds
          activeConnections: 0, // Will be set by server component
          filesWatched: this.watcher.getWatchedFiles().length,
          eventQueue: 0 // Will be calculated based on pending events
        };

        this.emit('metricsUpdate', metrics);
      } catch (error) {
        this.emit('error', new Error(`Failed to collect metrics: ${error}`));
      }
    }, 30000);
  }
}

// Type augmentation for EventEmitter
export declare interface FileMonitor {
  on<K extends keyof FileMonitorEvents>(event: K, listener: FileMonitorEvents[K]): this;
  emit<K extends keyof FileMonitorEvents>(event: K, ...args: Parameters<FileMonitorEvents[K]>): boolean;
}