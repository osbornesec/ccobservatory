import chokidar, { type FSWatcher } from 'chokidar';
import { EventEmitter } from 'events';
import { homedir } from 'os';
import { join, resolve } from 'path';
import { existsSync, statSync, readFileSync } from 'fs';
import {
  DEFAULT_CONFIG,
  FILE_PATTERNS,
  JsonlParser,
  type ClaudeCodeMessage,
  type FileWatchEvent,
  normalizePath,
  isJsonlFile,
  getFileName
} from '@cco/core';

export interface WatcherConfig {
  claudeDir?: string;
  ignorePatterns?: string[];
  debounceMs?: number;
  awaitWriteFinish?: boolean | { stabilityThreshold: number; pollInterval: number };
  usePolling?: boolean;
  followSymlinks?: boolean;
  persistent?: boolean;
}

export interface WatcherEvents {
  fileAdded: (event: FileWatchEvent & { messages?: ClaudeCodeMessage[] }) => void;
  fileChanged: (event: FileWatchEvent & { messages?: ClaudeCodeMessage[]; newLines?: ClaudeCodeMessage[] }) => void;
  fileRemoved: (event: FileWatchEvent) => void;
  error: (error: Error) => void;
  ready: () => void;
  projectDiscovered: (projectPath: string) => void;
}

export class ClaudeCodeWatcher extends EventEmitter {
  private watcher: FSWatcher | null = null;
  private config: Required<WatcherConfig>;
  private fileStates = new Map<string, { size: number; lastModified: number }>();
  private isWatching = false;

  constructor(config: WatcherConfig = {}) {
    super();

    this.config = {
      claudeDir: config.claudeDir || join(homedir(), '.claude'),
      ignorePatterns: config.ignorePatterns || [...FILE_PATTERNS.IGNORE],
      debounceMs: config.debounceMs || DEFAULT_CONFIG.DEBOUNCE_MS,
      awaitWriteFinish: config.awaitWriteFinish !== undefined 
        ? config.awaitWriteFinish 
        : {
            stabilityThreshold: 100,
            pollInterval: 50
          },
      usePolling: config.usePolling || false,
      followSymlinks: config.followSymlinks !== undefined ? config.followSymlinks : true,
      persistent: config.persistent !== undefined ? config.persistent : true
    };
  }

  /**
   * Start watching for Claude Code conversation files
   */
  async startWatching(): Promise<void> {
    if (this.isWatching) {
      throw new Error('Watcher is already running');
    }

    // Validate Claude directory exists
    const projectsDir = join(this.config.claudeDir, 'projects');
    if (!existsSync(projectsDir)) {
      throw new Error(`Claude projects directory not found: ${projectsDir}`);
    }

    const watchPattern = join(projectsDir, '**/*.jsonl');
    
    this.watcher = chokidar.watch(watchPattern, {
      ignored: (path: string, stats?: any) => {
        // Skip files that match ignore patterns
        return this.config.ignorePatterns.some(pattern => 
          path.includes(pattern.replace('**/', '').replace('/**', ''))
        );
      },
      persistent: this.config.persistent,
      awaitWriteFinish: this.config.awaitWriteFinish,
      usePolling: this.config.usePolling,
      followSymlinks: this.config.followSymlinks,
      ignoreInitial: false,
      ignorePermissionErrors: true,
      alwaysStat: true
    });

    // Attach event listeners
    this.watcher
      .on('add', this.handleFileAdd.bind(this))
      .on('change', this.handleFileChange.bind(this))
      .on('unlink', this.handleFileRemove.bind(this))
      .on('error', (err: unknown) => this.handleError(err instanceof Error ? err : new Error(String(err))))
      .on('ready', this.handleReady.bind(this));

    this.isWatching = true;
  }

  /**
   * Stop watching files
   */
  async stopWatching(): Promise<void> {
    if (!this.isWatching || !this.watcher) {
      return;
    }

    await this.watcher.close();
    this.watcher = null;
    this.isWatching = false;
    this.fileStates.clear();
  }

  /**
   * Check if currently watching
   */
  get watching(): boolean {
    return this.isWatching;
  }

  /**
   * Get list of currently watched files
   */
  getWatchedFiles(): string[] {
    if (!this.watcher) return [];
    
    const watched = this.watcher.getWatched();
    const files: string[] = [];
    
    for (const [dir, fileList] of Object.entries(watched)) {
      for (const file of fileList as string[]) {
        const fullPath = join(dir, file);
        if (isJsonlFile(fullPath)) {
          files.push(fullPath);
        }
      }
    }
    
    return files;
  }

  /**
   * Get discovered projects
   */
  getDiscoveredProjects(): string[] {
    const projectsDir = join(this.config.claudeDir, 'projects');
    if (!existsSync(projectsDir)) return [];

    try {
      const { readdirSync } = require('fs');
      return readdirSync(projectsDir, { withFileTypes: true })
        .filter((dirent: any) => dirent.isDirectory())
        .map((dirent: any) => {
          // Convert directory name back to original path
          const dirName: string = dirent.name;
          if (dirName.startsWith('-')) {
            return dirName.substring(1).replace(/-/g, '/');
          }
          return dirName;
        });
    } catch (error) {
      this.emit('error', new Error(`Failed to discover projects: ${error}`));
      return [];
    }
  }

  private handleFileAdd(filePath: string, stats?: any): void {
    try {
      const normalizedPath = normalizePath(filePath);
      
      if (!isJsonlFile(normalizedPath)) return;

      // Store file state
      const fileStats = stats || statSync(normalizedPath);
      this.fileStates.set(normalizedPath, {
        size: fileStats.size,
        lastModified: fileStats.mtime.getTime()
      });

      // Extract project path from file location
      const projectPath = this.extractProjectPath(normalizedPath);
      if (projectPath) {
        this.emit('projectDiscovered', projectPath);
      }

      // Parse conversation if file has content
      let messages: ClaudeCodeMessage[] | undefined;
      if (fileStats.size > 0) {
        try {
          const content = readFileSync(normalizedPath, 'utf-8');
          messages = JsonlParser.parseClaudeCodeConversation(content);
        } catch (parseError) {
          // Don't fail on parse errors, just log them
          this.emit('error', new Error(`Failed to parse ${normalizedPath}: ${parseError}`));
        }
      }

      const event: FileWatchEvent & { messages?: ClaudeCodeMessage[] } = {
        type: 'add',
        filePath: normalizedPath,
        timestamp: new Date(),
        size: fileStats.size,
        messages
      };

      this.emit('fileAdded', event);
    } catch (error) {
      this.emit('error', new Error(`Error handling file add ${filePath}: ${error}`));
    }
  }

  private handleFileChange(filePath: string, stats?: any): void {
    try {
      const normalizedPath = normalizePath(filePath);
      
      if (!isJsonlFile(normalizedPath)) return;

      const fileStats = stats || statSync(normalizedPath);
      const previousState = this.fileStates.get(normalizedPath);
      
      // Update file state
      this.fileStates.set(normalizedPath, {
        size: fileStats.size,
        lastModified: fileStats.mtime.getTime()
      });

      // Parse conversation and detect new lines if possible
      let messages: ClaudeCodeMessage[] | undefined;
      let newLines: ClaudeCodeMessage[] | undefined;

      if (fileStats.size > 0) {
        try {
          const content = readFileSync(normalizedPath, 'utf-8');
          messages = JsonlParser.parseClaudeCodeConversation(content);

          // If we have previous state and file grew, try to get only new lines
          if (previousState && fileStats.size > previousState.size) {
            try {
              const { readFileSync } = require('fs');
              const newContent = readFileSync(normalizedPath, { 
                encoding: 'utf-8',
                start: previousState.size 
              });
              newLines = JsonlParser.parseClaudeCodeConversation(newContent);
            } catch {
              // Fallback to full parse if incremental fails
              newLines = undefined;
            }
          }
        } catch (parseError) {
          this.emit('error', new Error(`Failed to parse ${normalizedPath}: ${parseError}`));
        }
      }

      const event: FileWatchEvent & { messages?: ClaudeCodeMessage[]; newLines?: ClaudeCodeMessage[] } = {
        type: 'change',
        filePath: normalizedPath,
        timestamp: new Date(),
        size: fileStats.size,
        messages,
        newLines
      };

      this.emit('fileChanged', event);
    } catch (error) {
      this.emit('error', new Error(`Error handling file change ${filePath}: ${error}`));
    }
  }

  private handleFileRemove(filePath: string): void {
    try {
      const normalizedPath = normalizePath(filePath);
      
      if (!isJsonlFile(normalizedPath)) return;

      // Remove from file states
      this.fileStates.delete(normalizedPath);

      const event: FileWatchEvent = {
        type: 'unlink',
        filePath: normalizedPath,
        timestamp: new Date()
      };

      this.emit('fileRemoved', event);
    } catch (error) {
      this.emit('error', new Error(`Error handling file removal ${filePath}: ${error}`));
    }
  }

  private handleError(error: Error): void {
    this.emit('error', error);
  }

  private handleReady(): void {
    this.emit('ready');
  }

  /**
   * Extract original project path from Claude directory structure
   */
  private extractProjectPath(filePath: string): string | null {
    try {
      const projectsDir = join(this.config.claudeDir, 'projects');
      const relativePath = filePath.replace(projectsDir, '');
      const parts = relativePath.split('/').filter(Boolean);
      
      if (parts.length < 1) return null;
      
      const projectDirName = parts[0];
      if (!projectDirName) return null;
      
      // Convert back to original path format
      if (projectDirName.startsWith('-')) {
        return projectDirName.substring(1).replace(/-/g, '/');
      }
      
      return projectDirName;
    } catch {
      return null;
    }
  }
}

// Type augmentation for EventEmitter
export declare interface ClaudeCodeWatcher {
  on<K extends keyof WatcherEvents>(event: K, listener: WatcherEvents[K]): this;
  emit<K extends keyof WatcherEvents>(event: K, ...args: Parameters<WatcherEvents[K]>): boolean;
}