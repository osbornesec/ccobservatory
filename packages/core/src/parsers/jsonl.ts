import type { ClaudeMessage, ClaudeCodeMessage, Message } from '../types/conversation.js';
import { generateId } from '../utils/id.js';
import { parseISODate } from '../utils/date.js';

export class JsonlParseError extends Error {
  constructor(message: string, public lineNumber: number, public line: string) {
    super(`JSONL Parse Error at line ${lineNumber}: ${message}`);
    this.name = 'JsonlParseError';
  }
}

export class JsonlParser {
  /**
   * Parse JSONL content into Claude Code messages
   * @param content JSONL file content
   * @returns Array of parsed Claude Code messages
   */
  static parseClaudeCodeConversation(content: string): ClaudeCodeMessage[] {
    const lines = content.split('\n').filter(line => line.trim());
    const messages: ClaudeCodeMessage[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line?.trim()) continue;

      try {
        const parsed = JSON.parse(line) as ClaudeCodeMessage;
        messages.push(parsed);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        throw new JsonlParseError(
          `Invalid JSON: ${errorMessage}`,
          i + 1,
          line.trim()
        );
      }
    }

    return messages;
  }

  /**
   * Parse JSONL content into Claude messages (legacy format)
   * @param content JSONL file content
   * @returns Array of parsed Claude messages
   */
  static parseConversation(content: string): ClaudeMessage[] {
    const lines = content.split('\n').filter(line => line.trim());
    const messages: ClaudeMessage[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line?.trim()) continue;

      try {
        const parsed = JSON.parse(line) as ClaudeMessage;
        messages.push(parsed);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        throw new JsonlParseError(
          `Invalid JSON: ${errorMessage}`,
          i + 1,
          line.trim()
        );
      }
    }

    return messages;
  }

  /**
   * Convert Claude Code messages to normalized Message format
   * @param claudeCodeMessages Array of Claude Code messages
   * @param conversationId Conversation ID to assign
   * @returns Array of normalized messages
   */
  static claudeCodeToNormalizedMessages(claudeCodeMessages: ClaudeCodeMessage[], conversationId: string): Message[] {
    return claudeCodeMessages
      .filter(msg => msg.type === 'user' || msg.type === 'assistant')
      .filter(msg => msg.message)
      .map(msg => ({
        id: msg.uuid,
        conversationId,
        role: msg.message!.role,
        content: typeof msg.message!.content === 'string' 
          ? msg.message!.content 
          : JSON.stringify(msg.message!.content),
        timestamp: parseISODate(msg.timestamp),
        tokenCount: msg.message!.usage 
          ? msg.message!.usage.input_tokens + msg.message!.usage.output_tokens 
          : undefined,
        model: msg.message!.model,
        toolCalls: msg.message!.content && Array.isArray(msg.message!.content)
          ? msg.message!.content
              .filter((c: any) => c.type === 'tool_use')
              .map((c: any) => ({
                id: c.id,
                name: c.name,
                input: c.input,
                status: 'success' as const
              }))
          : undefined
      }));
  }

  /**
   * Convert Claude messages to normalized Message format (legacy)
   * @param claudeMessages Array of Claude messages
   * @param conversationId Conversation ID to assign
   * @returns Array of normalized messages
   */
  static toNormalizedMessages(claudeMessages: ClaudeMessage[], conversationId: string): Message[] {
    return claudeMessages
      .filter(msg => msg.type === 'user' || msg.type === 'assistant')
      .map(msg => ({
        id: generateId(),
        conversationId,
        role: msg.type as 'user' | 'assistant',
        content: msg.content || '',
        timestamp: parseISODate(msg.timestamp),
        tokenCount: msg.usage ? msg.usage.input_tokens + msg.usage.output_tokens : undefined,
        model: msg.model,
        toolCalls: msg.tool_calls?.map(call => ({
          id: generateId(),
          name: call.name,
          input: call.input,
          output: call.output,
          status: call.output ? 'success' : 'pending' as const
        }))
      }));
  }

  /**
   * Extract conversation metadata from Claude Code messages
   * @param messages Array of Claude Code messages
   * @param filePath Source file path
   * @returns Conversation metadata
   */
  static extractClaudeCodeMetadata(messages: ClaudeCodeMessage[], filePath: string) {
    const timestamps = messages
      .map(msg => parseISODate(msg.timestamp))
      .sort((a, b) => a.getTime() - b.getTime());

    const createdAt = timestamps[0] || new Date();
    const lastUpdated = timestamps[timestamps.length - 1] || new Date();

    const totalTokens = messages.reduce((sum, msg) => {
      return sum + (msg.message?.usage 
        ? msg.message.usage.input_tokens + msg.message.usage.output_tokens 
        : 0);
    }, 0);

    // Extract title from first user message or summary
    const summaryMessage = messages.find(msg => msg.type === 'summary');
    const firstUserMessage = messages.find(msg => msg.type === 'user' && msg.message);
    
    let title = 'Untitled Conversation';
    if (summaryMessage?.summary) {
      title = summaryMessage.summary;
    } else if (firstUserMessage?.message?.content) {
      const content = typeof firstUserMessage.message.content === 'string' 
        ? firstUserMessage.message.content 
        : JSON.stringify(firstUserMessage.message.content);
      title = content.substring(0, 50) + '...';
    } else {
      title = filePath.split('/').pop()?.replace('.jsonl', '') || 'Untitled';
    }

    // Extract session ID and working directory
    const sessionId = messages[0]?.sessionId || '';
    const workingDirectory = messages[0]?.cwd || '';

    return {
      createdAt,
      lastUpdated,
      messageCount: messages.filter(msg => msg.type === 'user' || msg.type === 'assistant').length,
      tokenCount: totalTokens > 0 ? totalTokens : undefined,
      title: title.trim(),
      sessionId,
      workingDirectory
    };
  }

  /**
   * Extract conversation metadata from messages (legacy)
   * @param messages Array of messages
   * @param filePath Source file path
   * @returns Conversation metadata
   */
  static extractMetadata(messages: ClaudeMessage[], filePath: string) {
    const timestamps = messages
      .map(msg => parseISODate(msg.timestamp))
      .sort((a, b) => a.getTime() - b.getTime());

    const createdAt = timestamps[0] || new Date();
    const lastUpdated = timestamps[timestamps.length - 1] || new Date();

    const totalTokens = messages.reduce((sum, msg) => {
      return sum + (msg.usage ? msg.usage.input_tokens + msg.usage.output_tokens : 0);
    }, 0);

    // Extract title from first user message or use filename
    const firstUserMessage = messages.find(msg => msg.type === 'user');
    const title = firstUserMessage?.content?.substring(0, 50) + '...' || 
                  filePath.split('/').pop()?.replace('.jsonl', '') || 'Untitled';

    return {
      createdAt,
      lastUpdated,
      messageCount: messages.filter(msg => msg.type === 'user' || msg.type === 'assistant').length,
      tokenCount: totalTokens > 0 ? totalTokens : undefined,
      title: title.trim()
    };
  }
}