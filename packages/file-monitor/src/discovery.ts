import { readdirSync, statSync, readFileSync, existsSync } from 'fs';
import { join, resolve } from 'path';
import { homedir } from 'os';
import {
  JsonlParser,
  type ClaudeCodeMessage,
  type ConversationMetadata,
  type Project,
  generateId,
  generateConversationId,
  normalizePath,
  isJsonlFile,
  getFileName
} from '@cco/core';

export interface DiscoveryResult {
  projects: Project[];
  conversations: ConversationMetadata[];
  totalFiles: number;
  totalMessages: number;
  totalTokens: number;
  processingErrors: string[];
  scanDuration: number;
}

export class ConversationDiscovery {
  private claudeDir: string;

  constructor(claudeDir?: string) {
    this.claudeDir = claudeDir || join(homedir(), '.claude');
  }

  /**
   * Scan for all existing conversations and projects
   */
  async scanForConversations(): Promise<DiscoveryResult> {
    const startTime = Date.now();
    const result: DiscoveryResult = {
      projects: [],
      conversations: [],
      totalFiles: 0,
      totalMessages: 0,
      totalTokens: 0,
      processingErrors: [],
      scanDuration: 0
    };

    const projectsDir = join(this.claudeDir, 'projects');
    
    if (!existsSync(projectsDir)) {
      result.processingErrors.push(`Claude projects directory not found: ${projectsDir}`);
      result.scanDuration = Date.now() - startTime;
      return result;
    }

    try {
      // Discover projects
      const projectDirs = readdirSync(projectsDir, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name);

      for (const projectDirName of projectDirs) {
        try {
          const projectPath = this.convertProjectDirToPath(projectDirName);
          const projectDir = join(projectsDir, projectDirName);
          
          // Create project metadata
          const projectStats = statSync(projectDir);
          const project: Project = {
            id: generateId(),
            name: this.extractProjectName(projectPath),
            path: projectPath,
            createdAt: projectStats.birthtime || projectStats.ctime,
            updatedAt: projectStats.mtime,
            conversationCount: 0
          };

          // Discover conversations in this project
          const conversations = await this.scanProjectConversations(projectDir, project.id);
          project.conversationCount = conversations.length;
          
          result.projects.push(project);
          result.conversations.push(...conversations);
          
          // Update totals
          result.totalFiles += conversations.length;
          result.totalMessages += conversations.reduce((sum, conv) => sum + conv.messageCount, 0);
          result.totalTokens += conversations.reduce((sum, conv) => sum + (conv.tokenCount || 0), 0);

        } catch (error) {
          result.processingErrors.push(`Error processing project ${projectDirName}: ${error}`);
        }
      }

      result.scanDuration = Date.now() - startTime;
      return result;

    } catch (error) {
      result.processingErrors.push(`Error scanning projects directory: ${error}`);
      result.scanDuration = Date.now() - startTime;
      return result;
    }
  }

  /**
   * Scan conversations within a specific project directory
   */
  private async scanProjectConversations(projectDir: string, projectId: string): Promise<ConversationMetadata[]> {
    const conversations: ConversationMetadata[] = [];

    try {
      const files = readdirSync(projectDir)
        .filter(file => isJsonlFile(file))
        .map(file => join(projectDir, file));

      for (const filePath of files) {
        try {
          const conversation = await this.processConversationFile(filePath, projectId);
          if (conversation) {
            conversations.push(conversation);
          }
        } catch (error) {
          // Log individual file errors but continue processing
          console.warn(`Error processing conversation file ${filePath}:`, error);
        }
      }

    } catch (error) {
      throw new Error(`Failed to scan project conversations: ${error}`);
    }

    return conversations;
  }

  /**
   * Process a single conversation file
   */
  private async processConversationFile(filePath: string, projectId: string): Promise<ConversationMetadata | null> {
    try {
      const normalizedPath = normalizePath(filePath);
      const fileStats = statSync(normalizedPath);
      
      if (fileStats.size === 0) {
        return null; // Skip empty files
      }

      // Read and parse conversation
      const content = readFileSync(normalizedPath, 'utf-8');
      const messages = JsonlParser.parseClaudeCodeConversation(content);
      
      if (messages.length === 0) {
        return null; // Skip files with no messages
      }

      // Extract metadata using the parser
      const metadata = JsonlParser.extractClaudeCodeMetadata(messages, normalizedPath);
      
      // Create conversation metadata
      const conversationId = generateConversationId(normalizedPath);
      
      const conversation: ConversationMetadata = {
        id: conversationId,
        projectId,
        filePath: normalizedPath,
        title: metadata.title,
        createdAt: metadata.createdAt,
        lastUpdated: metadata.lastUpdated,
        messageCount: metadata.messageCount,
        tokenCount: metadata.tokenCount
      };

      return conversation;

    } catch (error) {
      throw new Error(`Failed to process conversation file ${filePath}: ${error}`);
    }
  }

  /**
   * Convert Claude project directory name back to original path
   */
  private convertProjectDirToPath(projectDirName: string): string {
    if (projectDirName.startsWith('-')) {
      return projectDirName.substring(1).replace(/-/g, '/');
    }
    return projectDirName;
  }

  /**
   * Extract a readable project name from the path
   */
  private extractProjectName(projectPath: string): string {
    const parts = projectPath.split('/').filter(Boolean);
    if (parts.length === 0) return 'Root';
    
    const lastPart = parts[parts.length - 1];
    return lastPart || parts[parts.length - 2] || 'Unknown Project';
  }

  /**
   * Get summary statistics for all conversations
   */
  async getStatistics(): Promise<{
    totalProjects: number;
    totalConversations: number;
    totalFiles: number;
    totalSize: number;
    oldestConversation: Date | null;
    newestConversation: Date | null;
  }> {
    const result = await this.scanForConversations();
    
    const conversationDates = result.conversations
      .map(conv => conv.createdAt)
      .sort((a, b) => a.getTime() - b.getTime());

    return {
      totalProjects: result.projects.length,
      totalConversations: result.conversations.length,
      totalFiles: result.totalFiles,
      totalSize: 0, // Would need to calculate from file sizes
      oldestConversation: conversationDates[0] || null,
      newestConversation: conversationDates[conversationDates.length - 1] || null
    };
  }

  /**
   * Find conversations by project path
   */
  async findConversationsByProject(projectPath: string): Promise<ConversationMetadata[]> {
    const result = await this.scanForConversations();
    const project = result.projects.find(p => p.path === projectPath);
    
    if (!project) {
      return [];
    }

    return result.conversations.filter(conv => conv.projectId === project.id);
  }

  /**
   * Search conversations by title or content (basic implementation)
   */
  async searchConversations(query: string): Promise<ConversationMetadata[]> {
    const result = await this.scanForConversations();
    const lowerQuery = query.toLowerCase();
    
    return result.conversations.filter(conv => 
      conv.title.toLowerCase().includes(lowerQuery)
    );
  }
}