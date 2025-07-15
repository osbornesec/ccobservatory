# Week 9: Analytics Foundation & Data Processing

## Overview
Establish the core analytics engine for the Claude Code Observatory, focusing on conversation metrics, usage patterns, token analysis, and performance monitoring. This week implements the data processing pipeline that transforms raw conversation data into actionable insights.

## Team Assignments
- **Backend Lead**: Analytics data pipeline, metrics calculation, performance optimization
- **Full-Stack Developer**: Real-time analytics API, data aggregation, storage optimization
- **Frontend Developer**: Analytics store integration, data visualization preparation

## Daily Schedule

### Monday: Analytics Architecture & Data Pipeline
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Analytics system architecture and data modeling
- **10:30-12:00**: Data pipeline implementation for conversation metrics

#### Afternoon (4 hours)
- **13:00-15:00**: Real-time data processing and aggregation
- **15:00-17:00**: Message analysis and token usage tracking

### Tuesday: Metrics Calculation & Storage
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Conversation analytics metrics implementation
- **10:30-12:00**: User behavior and usage pattern analysis

#### Afternoon (4 hours)
- **13:00-15:00**: Performance metrics and system monitoring
- **15:00-17:00**: Data aggregation and time-series storage

### Wednesday: API Integration & Real-Time Updates
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Analytics API endpoints development
- **10:30-12:00**: Real-time analytics data streaming

#### Afternoon (4 hours)
- **13:00-15:00**: WebSocket integration for live analytics updates
- **15:00-17:00**: Caching layer and query optimization

### Thursday: Data Export & Reporting Foundation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Data export functionality (CSV, JSON, PDF)
- **10:30-12:00**: Report generation and scheduling system

#### Afternoon (4 hours)
- **13:00-15:00**: Historical data analysis and trends
- **15:00-17:00**: Data retention and archival policies

### Friday: Testing & Performance Optimization
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Analytics pipeline testing and validation
- **10:30-12:00**: Performance benchmarking and optimization

#### Afternoon (4 hours)
- **13:00-15:00**: Load testing with large datasets
- **15:00-17:00**: Integration testing with existing components

## Technical Implementation Details

### Analytics Engine Architecture
```typescript
// analytics/engine.ts
import { EventEmitter } from 'events';
import { DatabaseManager } from '../database/connection';
import { MetricsCalculator } from './metrics-calculator';
import { DataAggregator } from './data-aggregator';

export interface AnalyticsEvent {
  type: string;
  timestamp: Date;
  conversationId?: string;
  userId?: string;
  data: Record<string, any>;
}

export class AnalyticsEngine extends EventEmitter {
  private db: DatabaseManager;
  private metricsCalculator: MetricsCalculator;
  private dataAggregator: DataAggregator;
  private processingQueue: AnalyticsEvent[] = [];
  private isProcessing = false;

  constructor(db: DatabaseManager) {
    super();
    this.db = db;
    this.metricsCalculator = new MetricsCalculator(db);
    this.dataAggregator = new DataAggregator(db);
    this.startProcessing();
  }

  // Event ingestion
  trackEvent(event: AnalyticsEvent): void {
    this.processingQueue.push({
      ...event,
      timestamp: event.timestamp || new Date()
    });

    this.emit('event_tracked', event);
  }

  trackConversationCreated(conversationId: string, userId: string, metadata: any): void {
    this.trackEvent({
      type: 'conversation_created',
      conversationId,
      userId,
      data: metadata
    });
  }

  trackMessageSent(conversationId: string, messageId: string, role: string, tokenCount: number): void {
    this.trackEvent({
      type: 'message_sent',
      conversationId,
      data: {
        messageId,
        role,
        tokenCount,
        messageLength: 0 // Will be calculated
      }
    });
  }

  trackTokenUsage(conversationId: string, tokens: number, type: 'input' | 'output'): void {
    this.trackEvent({
      type: 'token_usage',
      conversationId,
      data: { tokens, type }
    });
  }

  trackUserActivity(userId: string, activity: string, metadata?: any): void {
    this.trackEvent({
      type: 'user_activity',
      userId,
      data: { activity, ...metadata }
    });
  }

  // Data processing
  private async startProcessing(): Promise<void> {
    if (this.isProcessing) return;
    
    this.isProcessing = true;
    
    while (true) {
      if (this.processingQueue.length > 0) {
        const events = this.processingQueue.splice(0, 100); // Process in batches
        await this.processEvents(events);
      } else {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
      }
    }
  }

  private async processEvents(events: AnalyticsEvent[]): Promise<void> {
    try {
      // Store raw events
      await this.storeRawEvents(events);
      
      // Calculate metrics
      await this.metricsCalculator.processEvents(events);
      
      // Update aggregations
      await this.dataAggregator.updateAggregations(events);
      
      this.emit('events_processed', events.length);
    } catch (error) {
      console.error('Failed to process analytics events:', error);
      this.emit('processing_error', error);
    }
  }

  private async storeRawEvents(events: AnalyticsEvent[]): Promise<void> {
    const stmt = this.db.prepare(`
      INSERT INTO analytics_events (id, type, timestamp, conversation_id, user_id, data)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    for (const event of events) {
      stmt.run(
        this.generateEventId(),
        event.type,
        event.timestamp.toISOString(),
        event.conversationId || null,
        event.userId || null,
        JSON.stringify(event.data)
      );
    }
  }

  // Analytics queries
  async getConversationMetrics(conversationId: string): Promise<ConversationMetrics> {
    return this.metricsCalculator.getConversationMetrics(conversationId);
  }

  async getUserMetrics(userId: string, timeRange?: TimeRange): Promise<UserMetrics> {
    return this.metricsCalculator.getUserMetrics(userId, timeRange);
  }

  async getSystemMetrics(timeRange?: TimeRange): Promise<SystemMetrics> {
    return this.metricsCalculator.getSystemMetrics(timeRange);
  }

  async getDashboardData(timeRange?: TimeRange): Promise<DashboardData> {
    return this.dataAggregator.getDashboardData(timeRange);
  }

  private generateEventId(): string {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

### Metrics Calculator
```typescript
// analytics/metrics-calculator.ts
import { DatabaseManager } from '../database/connection';

export interface ConversationMetrics {
  id: string;
  messageCount: number;
  totalTokens: number;
  inputTokens: number;
  outputTokens: number;
  averageResponseTime: number;
  createdAt: Date;
  lastActivity: Date;
  duration: number; // in seconds
  userEngagement: number; // engagement score
}

export interface UserMetrics {
  userId: string;
  conversationCount: number;
  totalMessages: number;
  totalTokensUsed: number;
  averageSessionDuration: number;
  mostActiveTimeOfDay: string;
  activityPattern: Record<string, number>;
  topConversationTopics: string[];
}

export interface SystemMetrics {
  totalConversations: number;
  totalMessages: number;
  totalTokensProcessed: number;
  averageConversationLength: number;
  activeUsers: number;
  systemUptime: number;
  errorRate: number;
  averageResponseTime: number;
  peakUsageHours: string[];
}

export class MetricsCalculator {
  constructor(private db: DatabaseManager) {}

  async processEvents(events: AnalyticsEvent[]): Promise<void> {
    for (const event of events) {
      switch (event.type) {
        case 'conversation_created':
          await this.updateConversationCreationMetrics(event);
          break;
        case 'message_sent':
          await this.updateMessageMetrics(event);
          break;
        case 'token_usage':
          await this.updateTokenMetrics(event);
          break;
        case 'user_activity':
          await this.updateUserActivityMetrics(event);
          break;
      }
    }
  }

  async getConversationMetrics(conversationId: string): Promise<ConversationMetrics> {
    const conversation = this.db.prepare(`
      SELECT * FROM conversations WHERE id = ?
    `).get(conversationId);

    if (!conversation) {
      throw new Error(`Conversation ${conversationId} not found`);
    }

    const messageStats = this.db.prepare(`
      SELECT 
        COUNT(*) as message_count,
        SUM(token_count) as total_tokens,
        AVG(token_count) as avg_tokens,
        MIN(timestamp) as first_message,
        MAX(timestamp) as last_message
      FROM messages 
      WHERE conversation_id = ?
    `).get(conversationId) as any;

    const tokenBreakdown = this.db.prepare(`
      SELECT 
        SUM(CASE WHEN role = 'user' THEN token_count ELSE 0 END) as input_tokens,
        SUM(CASE WHEN role = 'assistant' THEN token_count ELSE 0 END) as output_tokens
      FROM messages 
      WHERE conversation_id = ?
    `).get(conversationId) as any;

    const responseTimesQuery = this.db.prepare(`
      SELECT 
        m1.timestamp as user_message_time,
        m2.timestamp as assistant_response_time
      FROM messages m1
      JOIN messages m2 ON m2.conversation_id = m1.conversation_id
      WHERE m1.conversation_id = ? 
      AND m1.role = 'user' 
      AND m2.role = 'assistant'
      AND m2.timestamp > m1.timestamp
      ORDER BY m1.timestamp
    `).all(conversationId) as any[];

    const responseTimes = responseTimesQuery.map(row => {
      const userTime = new Date(row.user_message_time).getTime();
      const assistantTime = new Date(row.assistant_response_time).getTime();
      return assistantTime - userTime;
    });

    const averageResponseTime = responseTimes.length > 0 
      ? responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length 
      : 0;

    const createdAt = new Date(conversation.created_at);
    const lastActivity = new Date(messageStats.last_message || conversation.created_at);
    const duration = (lastActivity.getTime() - createdAt.getTime()) / 1000;

    return {
      id: conversationId,
      messageCount: messageStats.message_count || 0,
      totalTokens: messageStats.total_tokens || 0,
      inputTokens: tokenBreakdown.input_tokens || 0,
      outputTokens: tokenBreakdown.output_tokens || 0,
      averageResponseTime: averageResponseTime / 1000, // Convert to seconds
      createdAt,
      lastActivity,
      duration,
      userEngagement: this.calculateEngagementScore(messageStats, duration)
    };
  }

  async getUserMetrics(userId: string, timeRange?: TimeRange): Promise<UserMetrics> {
    const timeCondition = timeRange 
      ? `AND created_at BETWEEN '${timeRange.start.toISOString()}' AND '${timeRange.end.toISOString()}'`
      : '';

    const conversationStats = this.db.prepare(`
      SELECT COUNT(*) as conversation_count
      FROM conversations 
      WHERE user_id = ? ${timeCondition}
    `).get(userId) as any;

    const messageStats = this.db.prepare(`
      SELECT 
        COUNT(*) as total_messages,
        SUM(token_count) as total_tokens
      FROM messages m
      JOIN conversations c ON c.id = m.conversation_id
      WHERE c.user_id = ? ${timeCondition}
    `).get(userId) as any;

    const activityPattern = this.db.prepare(`
      SELECT 
        strftime('%H', timestamp) as hour,
        COUNT(*) as activity_count
      FROM messages m
      JOIN conversations c ON c.id = m.conversation_id
      WHERE c.user_id = ? ${timeCondition}
      GROUP BY hour
      ORDER BY hour
    `).all(userId) as any[];

    const mostActiveHour = activityPattern.reduce((max, current) => 
      current.activity_count > max.activity_count ? current : max
    , activityPattern[0] || { hour: '00' });

    return {
      userId,
      conversationCount: conversationStats.conversation_count || 0,
      totalMessages: messageStats.total_messages || 0,
      totalTokensUsed: messageStats.total_tokens || 0,
      averageSessionDuration: 0, // Calculate based on session data
      mostActiveTimeOfDay: `${mostActiveHour.hour}:00`,
      activityPattern: activityPattern.reduce((pattern, row) => {
        pattern[row.hour] = row.activity_count;
        return pattern;
      }, {}),
      topConversationTopics: [] // Implement topic analysis
    };
  }

  async getSystemMetrics(timeRange?: TimeRange): Promise<SystemMetrics> {
    const timeCondition = timeRange 
      ? `WHERE created_at BETWEEN '${timeRange.start.toISOString()}' AND '${timeRange.end.toISOString()}'`
      : '';

    const overallStats = this.db.prepare(`
      SELECT 
        (SELECT COUNT(*) FROM conversations ${timeCondition}) as total_conversations,
        (SELECT COUNT(*) FROM messages m JOIN conversations c ON c.id = m.conversation_id ${timeCondition}) as total_messages,
        (SELECT SUM(token_count) FROM messages m JOIN conversations c ON c.id = m.conversation_id ${timeCondition}) as total_tokens,
        (SELECT COUNT(DISTINCT user_id) FROM conversations ${timeCondition}) as active_users
    `).get() as any;

    const avgConversationLength = this.db.prepare(`
      SELECT AVG(message_count) as avg_length
      FROM (
        SELECT COUNT(*) as message_count
        FROM messages m
        JOIN conversations c ON c.id = m.conversation_id
        ${timeCondition}
        GROUP BY m.conversation_id
      )
    `).get() as any;

    const peakHours = this.db.prepare(`
      SELECT 
        strftime('%H', timestamp) as hour,
        COUNT(*) as activity_count
      FROM messages m
      JOIN conversations c ON c.id = m.conversation_id
      ${timeCondition}
      GROUP BY hour
      ORDER BY activity_count DESC
      LIMIT 3
    `).all() as any[];

    return {
      totalConversations: overallStats.total_conversations || 0,
      totalMessages: overallStats.total_messages || 0,
      totalTokensProcessed: overallStats.total_tokens || 0,
      averageConversationLength: avgConversationLength.avg_length || 0,
      activeUsers: overallStats.active_users || 0,
      systemUptime: this.calculateSystemUptime(),
      errorRate: 0, // Implement error tracking
      averageResponseTime: 0, // Implement response time tracking
      peakUsageHours: peakHours.map(row => `${row.hour}:00`)
    };
  }

  private calculateEngagementScore(messageStats: any, duration: number): number {
    // Simple engagement calculation based on messages per minute
    if (duration === 0) return 0;
    const messagesPerMinute = (messageStats.message_count || 0) / (duration / 60);
    return Math.min(messagesPerMinute * 10, 100); // Scale to 0-100
  }

  private calculateSystemUptime(): number {
    // Implement system uptime calculation
    return 99.9; // Placeholder
  }

  private async updateConversationCreationMetrics(event: AnalyticsEvent): Promise<void> {
    // Update conversation creation metrics
  }

  private async updateMessageMetrics(event: AnalyticsEvent): Promise<void> {
    // Update message-related metrics
  }

  private async updateTokenMetrics(event: AnalyticsEvent): Promise<void> {
    // Update token usage metrics
  }

  private async updateUserActivityMetrics(event: AnalyticsEvent): Promise<void> {
    // Update user activity metrics
  }
}
```

### Data Aggregation Service
```typescript
// analytics/data-aggregator.ts
import { DatabaseManager } from '../database/connection';

export interface DashboardData {
  overview: {
    totalConversations: number;
    totalMessages: number;
    totalTokens: number;
    activeUsers: number;
  };
  trends: {
    conversationsOverTime: TimeSeriesData[];
    messagesOverTime: TimeSeriesData[];
    tokensOverTime: TimeSeriesData[];
  };
  topMetrics: {
    mostActiveUsers: UserActivitySummary[];
    longestConversations: ConversationSummary[];
    peakUsageTimes: PeakUsageData[];
  };
  performance: {
    averageResponseTime: number;
    systemUptime: number;
    errorRate: number;
  };
}

export interface TimeSeriesData {
  timestamp: Date;
  value: number;
  label?: string;
}

export class DataAggregator {
  constructor(private db: DatabaseManager) {
    this.initializeAggregationTables();
  }

  private initializeAggregationTables(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS daily_aggregations (
        date TEXT PRIMARY KEY,
        total_conversations INTEGER DEFAULT 0,
        total_messages INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        unique_users INTEGER DEFAULT 0,
        avg_response_time REAL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS hourly_aggregations (
        datetime TEXT PRIMARY KEY,
        hour INTEGER,
        conversations INTEGER DEFAULT 0,
        messages INTEGER DEFAULT 0,
        tokens INTEGER DEFAULT 0,
        users INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS user_daily_stats (
        user_id TEXT,
        date TEXT,
        conversations INTEGER DEFAULT 0,
        messages INTEGER DEFAULT 0,
        tokens INTEGER DEFAULT 0,
        session_duration INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, date)
      );
    `);
  }

  async updateAggregations(events: AnalyticsEvent[]): Promise<void> {
    const groupedEvents = this.groupEventsByDate(events);
    
    for (const [date, dateEvents] of groupedEvents) {
      await this.updateDailyAggregation(date, dateEvents);
      await this.updateHourlyAggregations(date, dateEvents);
    }

    await this.updateUserDailyStats(events);
  }

  async getDashboardData(timeRange?: TimeRange): Promise<DashboardData> {
    const timeCondition = timeRange 
      ? `WHERE date BETWEEN '${timeRange.start.toISOString().split('T')[0]}' AND '${timeRange.end.toISOString().split('T')[0]}'`
      : 'WHERE date >= date("now", "-30 days")';

    // Overview data
    const overview = this.db.prepare(`
      SELECT 
        SUM(total_conversations) as totalConversations,
        SUM(total_messages) as totalMessages,
        SUM(total_tokens) as totalTokens,
        MAX(unique_users) as activeUsers
      FROM daily_aggregations
      ${timeCondition}
    `).get() as any;

    // Trends data
    const conversationTrends = this.db.prepare(`
      SELECT date, total_conversations as value
      FROM daily_aggregations
      ${timeCondition}
      ORDER BY date
    `).all() as any[];

    const messageTrends = this.db.prepare(`
      SELECT date, total_messages as value
      FROM daily_aggregations
      ${timeCondition}
      ORDER BY date
    `).all() as any[];

    const tokenTrends = this.db.prepare(`
      SELECT date, total_tokens as value
      FROM daily_aggregations
      ${timeCondition}
      ORDER BY date
    `).all() as any[];

    // Top metrics
    const mostActiveUsers = this.db.prepare(`
      SELECT 
        user_id,
        SUM(conversations) as totalConversations,
        SUM(messages) as totalMessages,
        SUM(tokens) as totalTokens
      FROM user_daily_stats
      WHERE date >= date("now", "-30 days")
      GROUP BY user_id
      ORDER BY totalMessages DESC
      LIMIT 10
    `).all() as any[];

    const longestConversations = this.db.prepare(`
      SELECT 
        id,
        title,
        message_count,
        created_at
      FROM (
        SELECT 
          c.id,
          c.title,
          COUNT(m.id) as message_count,
          c.created_at
        FROM conversations c
        LEFT JOIN messages m ON m.conversation_id = c.id
        WHERE c.created_at >= date("now", "-30 days")
        GROUP BY c.id
        ORDER BY message_count DESC
        LIMIT 10
      )
    `).all() as any[];

    const peakUsageTimes = this.db.prepare(`
      SELECT 
        hour,
        AVG(messages) as avgMessages,
        AVG(conversations) as avgConversations
      FROM hourly_aggregations
      WHERE datetime >= datetime("now", "-7 days")
      GROUP BY hour
      ORDER BY avgMessages DESC
    `).all() as any[];

    return {
      overview: {
        totalConversations: overview.totalConversations || 0,
        totalMessages: overview.totalMessages || 0,
        totalTokens: overview.totalTokens || 0,
        activeUsers: overview.activeUsers || 0
      },
      trends: {
        conversationsOverTime: conversationTrends.map(row => ({
          timestamp: new Date(row.date),
          value: row.value
        })),
        messagesOverTime: messageTrends.map(row => ({
          timestamp: new Date(row.date),
          value: row.value
        })),
        tokensOverTime: tokenTrends.map(row => ({
          timestamp: new Date(row.date),
          value: row.value
        }))
      },
      topMetrics: {
        mostActiveUsers: mostActiveUsers.map(row => ({
          userId: row.user_id,
          totalConversations: row.totalConversations,
          totalMessages: row.totalMessages,
          totalTokens: row.totalTokens
        })),
        longestConversations: longestConversations.map(row => ({
          id: row.id,
          title: row.title,
          messageCount: row.message_count,
          createdAt: new Date(row.created_at)
        })),
        peakUsageTimes: peakUsageTimes.map(row => ({
          hour: row.hour,
          avgMessages: row.avgMessages,
          avgConversations: row.avgConversations
        }))
      },
      performance: {
        averageResponseTime: 0, // Implement
        systemUptime: 99.9, // Implement
        errorRate: 0.1 // Implement
      }
    };
  }

  private groupEventsByDate(events: AnalyticsEvent[]): Map<string, AnalyticsEvent[]> {
    const grouped = new Map<string, AnalyticsEvent[]>();
    
    for (const event of events) {
      const date = event.timestamp.toISOString().split('T')[0];
      if (!grouped.has(date)) {
        grouped.set(date, []);
      }
      grouped.get(date)!.push(event);
    }
    
    return grouped;
  }

  private async updateDailyAggregation(date: string, events: AnalyticsEvent[]): Promise<void> {
    const conversationCreated = events.filter(e => e.type === 'conversation_created').length;
    const messagesCount = events.filter(e => e.type === 'message_sent').length;
    const tokensUsed = events
      .filter(e => e.type === 'token_usage')
      .reduce((sum, e) => sum + (e.data.tokens || 0), 0);
    
    const uniqueUsers = new Set(events.map(e => e.userId).filter(Boolean)).size;

    this.db.prepare(`
      INSERT OR REPLACE INTO daily_aggregations 
      (date, total_conversations, total_messages, total_tokens, unique_users)
      VALUES (?, 
        COALESCE((SELECT total_conversations FROM daily_aggregations WHERE date = ?), 0) + ?,
        COALESCE((SELECT total_messages FROM daily_aggregations WHERE date = ?), 0) + ?,
        COALESCE((SELECT total_tokens FROM daily_aggregations WHERE date = ?), 0) + ?,
        ?
      )
    `).run(date, date, conversationCreated, date, messagesCount, date, tokensUsed, uniqueUsers);
  }

  private async updateHourlyAggregations(date: string, events: AnalyticsEvent[]): Promise<void> {
    const hourlyGroups = new Map<number, AnalyticsEvent[]>();
    
    for (const event of events) {
      const hour = event.timestamp.getHours();
      if (!hourlyGroups.has(hour)) {
        hourlyGroups.set(hour, []);
      }
      hourlyGroups.get(hour)!.push(event);
    }

    for (const [hour, hourEvents] of hourlyGroups) {
      const datetime = `${date} ${hour.toString().padStart(2, '0')}:00:00`;
      const conversations = hourEvents.filter(e => e.type === 'conversation_created').length;
      const messages = hourEvents.filter(e => e.type === 'message_sent').length;
      const tokens = hourEvents
        .filter(e => e.type === 'token_usage')
        .reduce((sum, e) => sum + (e.data.tokens || 0), 0);
      const users = new Set(hourEvents.map(e => e.userId).filter(Boolean)).size;

      this.db.prepare(`
        INSERT OR REPLACE INTO hourly_aggregations 
        (datetime, hour, conversations, messages, tokens, users)
        VALUES (?, ?, ?, ?, ?, ?)
      `).run(datetime, hour, conversations, messages, tokens, users);
    }
  }

  private async updateUserDailyStats(events: AnalyticsEvent[]): Promise<void> {
    const userDayGroups = new Map<string, AnalyticsEvent[]>();
    
    for (const event of events) {
      if (!event.userId) continue;
      
      const key = `${event.userId}:${event.timestamp.toISOString().split('T')[0]}`;
      if (!userDayGroups.has(key)) {
        userDayGroups.set(key, []);
      }
      userDayGroups.get(key)!.push(event);
    }

    for (const [key, userEvents] of userDayGroups) {
      const [userId, date] = key.split(':');
      const conversations = userEvents.filter(e => e.type === 'conversation_created').length;
      const messages = userEvents.filter(e => e.type === 'message_sent').length;
      const tokens = userEvents
        .filter(e => e.type === 'token_usage')
        .reduce((sum, e) => sum + (e.data.tokens || 0), 0);

      this.db.prepare(`
        INSERT OR REPLACE INTO user_daily_stats 
        (user_id, date, conversations, messages, tokens)
        VALUES (?, ?, 
          COALESCE((SELECT conversations FROM user_daily_stats WHERE user_id = ? AND date = ?), 0) + ?,
          COALESCE((SELECT messages FROM user_daily_stats WHERE user_id = ? AND date = ?), 0) + ?,
          COALESCE((SELECT tokens FROM user_daily_stats WHERE user_id = ? AND date = ?), 0) + ?
        )
      `).run(userId, date, userId, date, conversations, userId, date, messages, userId, date, tokens);
    }
  }
}
```

### Analytics API Routes
```typescript
// routes/analytics.ts
import { AnalyticsEngine } from '../analytics/engine';
import { DatabaseManager } from '../database/connection';

const db = new DatabaseManager();
const analyticsEngine = new AnalyticsEngine(db);

export const analyticsRoutes = {
  async getDashboard(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const timeRange = this.parseTimeRange(url.searchParams);
    
    try {
      const dashboardData = await analyticsEngine.getDashboardData(timeRange);
      return new Response(JSON.stringify(dashboardData), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Failed to fetch dashboard data' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
  },

  async getConversationMetrics(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const conversationId = url.pathname.split('/').pop();
    
    if (!conversationId) {
      return new Response(
        JSON.stringify({ error: 'Conversation ID required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    try {
      const metrics = await analyticsEngine.getConversationMetrics(conversationId);
      return new Response(JSON.stringify(metrics), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Failed to fetch conversation metrics' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
  },

  async getUserMetrics(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const userId = url.pathname.split('/').pop();
    const timeRange = this.parseTimeRange(url.searchParams);
    
    if (!userId) {
      return new Response(
        JSON.stringify({ error: 'User ID required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    try {
      const metrics = await analyticsEngine.getUserMetrics(userId, timeRange);
      return new Response(JSON.stringify(metrics), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Failed to fetch user metrics' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
  },

  async getSystemMetrics(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const timeRange = this.parseTimeRange(url.searchParams);
    
    try {
      const metrics = await analyticsEngine.getSystemMetrics(timeRange);
      return new Response(JSON.stringify(metrics), {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Failed to fetch system metrics' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
  },

  private parseTimeRange(searchParams: URLSearchParams): TimeRange | undefined {
    const start = searchParams.get('start');
    const end = searchParams.get('end');
    
    if (start && end) {
      return {
        start: new Date(start),
        end: new Date(end)
      };
    }
    
    return undefined;
  }
};
```

## Performance Requirements
- **Data Processing**: Process 10,000+ analytics events per minute
- **Query Response**: Analytics queries respond within 500ms
- **Real-time Updates**: Analytics data updates within 30 seconds
- **Memory Usage**: Analytics engine memory under 256MB
- **Storage Efficiency**: Compressed time-series data storage

## Acceptance Criteria
- [ ] Analytics engine processing conversation data
- [ ] Real-time metrics calculation and aggregation
- [ ] Time-series data storage and retrieval
- [ ] Analytics API endpoints functional
- [ ] Dashboard data aggregation working
- [ ] User behavior analysis implemented
- [ ] Token usage tracking accurate
- [ ] Performance metrics within requirements
- [ ] Data export functionality operational
- [ ] Integration with WebSocket for real-time updates

## Testing Procedures
1. **Data Processing Testing**: Validate analytics event processing accuracy
2. **Performance Testing**: Test with large datasets and concurrent users
3. **API Testing**: Verify all analytics endpoints functionality
4. **Aggregation Testing**: Test data aggregation accuracy
5. **Real-time Testing**: Validate real-time data updates

## Integration Points
- **Week 5-6**: Backend API and WebSocket event integration
- **Week 8**: Frontend analytics components
- **Week 10**: Visualization dashboard implementation

## Data Privacy & Security
- User data anonymization for aggregated metrics
- Sensitive data filtering and protection
- Configurable data retention policies
- Secure analytics API endpoints
- Audit logging for analytics access

## Monitoring & Alerting
- Analytics pipeline health monitoring
- Data processing error alerting
- Performance metric thresholds
- Storage capacity monitoring
- Query performance tracking

## Advanced Analytics Patterns & Implementation Guide

### 1. Data Processing Pipeline Architecture

The analytics foundation follows a stream processing pattern with multiple stages:

#### Stream Processing Pipeline
```typescript
// analytics/stream-processor.ts
import { Transform, Writable } from 'stream';
import { EventEmitter } from 'events';

export interface StreamEvent {
  id: string;
  type: string;
  timestamp: Date;
  payload: any;
  metadata?: Record<string, any>;
}

export class AnalyticsStreamProcessor extends EventEmitter {
  private processors: Map<string, Transform> = new Map();
  private outputSinks: Map<string, Writable> = new Map();
  private metrics = {
    processed: 0,
    errors: 0,
    throughput: 0,
    latency: 0
  };

  constructor() {
    super();
    this.setupProcessingPipeline();
    this.startMetricsCollection();
  }

  private setupProcessingPipeline(): void {
    // Validation stage
    const validationProcessor = new Transform({
      objectMode: true,
      transform(chunk: StreamEvent, encoding, callback) {
        try {
          this.validateEvent(chunk);
          callback(null, chunk);
        } catch (error) {
          this.emit('validation_error', { event: chunk, error });
          callback(); // Skip invalid events
        }
      }
    });

    // Enrichment stage - add computed fields
    const enrichmentProcessor = new Transform({
      objectMode: true,
      transform(chunk: StreamEvent, encoding, callback) {
        const enriched = this.enrichEvent(chunk);
        callback(null, enriched);
      }
    });

    // Aggregation stage - real-time metrics
    const aggregationProcessor = new Transform({
      objectMode: true,
      transform(chunk: StreamEvent, encoding, callback) {
        this.updateRealTimeAggregates(chunk);
        callback(null, chunk);
      }
    });

    // Storage sink
    const storageSink = new Writable({
      objectMode: true,
      write(chunk: StreamEvent, encoding, callback) {
        this.persistEvent(chunk)
          .then(() => callback())
          .catch(error => callback(error));
      }
    });

    this.processors.set('validation', validationProcessor);
    this.processors.set('enrichment', enrichmentProcessor);
    this.processors.set('aggregation', aggregationProcessor);
    this.outputSinks.set('storage', storageSink);

    // Connect pipeline
    validationProcessor
      .pipe(enrichmentProcessor)
      .pipe(aggregationProcessor)
      .pipe(storageSink);
  }

  processEvent(event: StreamEvent): void {
    const startTime = Date.now();
    
    const validationProcessor = this.processors.get('validation');
    if (validationProcessor) {
      validationProcessor.write(event);
      
      // Track latency
      this.metrics.latency = Date.now() - startTime;
      this.metrics.processed++;
    }
  }

  private validateEvent(event: StreamEvent): void {
    if (!event.id || !event.type || !event.timestamp) {
      throw new Error('Invalid event: missing required fields');
    }
    
    if (event.timestamp > new Date()) {
      throw new Error('Invalid event: future timestamp');
    }
  }

  private enrichEvent(event: StreamEvent): StreamEvent {
    return {
      ...event,
      metadata: {
        ...event.metadata,
        processedAt: new Date(),
        enrichedFields: this.computeEnrichedFields(event)
      }
    };
  }

  private computeEnrichedFields(event: StreamEvent): Record<string, any> {
    const enriched: Record<string, any> = {};
    
    // Add time-based features
    const timestamp = new Date(event.timestamp);
    enriched.hourOfDay = timestamp.getHours();
    enriched.dayOfWeek = timestamp.getDay();
    enriched.isWeekend = timestamp.getDay() === 0 || timestamp.getDay() === 6;
    
    // Add event-specific enrichment
    switch (event.type) {
      case 'conversation_message':
        enriched.messageLength = event.payload.content?.length || 0;
        enriched.hasCodeBlocks = /```/.test(event.payload.content || '');
        enriched.estimatedReadTime = Math.ceil((event.payload.content?.length || 0) / 200);
        break;
        
      case 'token_usage':
        enriched.costEstimate = this.calculateTokenCost(event.payload.tokens, event.payload.model);
        enriched.efficiency = this.calculateTokenEfficiency(event.payload);
        break;
    }
    
    return enriched;
  }

  private updateRealTimeAggregates(event: StreamEvent): void {
    // Update in-memory aggregates for real-time dashboard
    const key = `${event.type}:${new Date().toISOString().split('T')[0]}`;
    // Implementation would update Redis or in-memory cache
  }

  private async persistEvent(event: StreamEvent): Promise<void> {
    // Implement batched writes to SQLite for performance
    // This would be handled by the DatabaseWriter class
  }

  private calculateTokenCost(tokens: number, model: string): number {
    const rates: Record<string, number> = {
      'claude-3-opus': 0.015,
      'claude-3-sonnet': 0.003,
      'claude-3-haiku': 0.00025
    };
    return (tokens / 1000) * (rates[model] || 0.001);
  }

  private calculateTokenEfficiency(payload: any): number {
    // Calculate tokens per meaningful output unit
    const outputTokens = payload.outputTokens || 0;
    const inputTokens = payload.inputTokens || 0;
    return outputTokens > 0 ? inputTokens / outputTokens : 0;
  }

  private startMetricsCollection(): void {
    setInterval(() => {
      this.emit('metrics', { ...this.metrics });
      this.metrics.throughput = this.metrics.processed; // Reset for next interval
      this.metrics.processed = 0;
    }, 60000); // Every minute
  }

  getMetrics() {
    return { ...this.metrics };
  }
}
```

### 2. Time-Series Data Management

#### Time-Series Storage with Compression
```typescript
// analytics/time-series-store.ts
export interface TimeSeriesPoint {
  timestamp: Date;
  value: number;
  tags?: Record<string, string>;
}

export interface TimeSeriesQuery {
  metric: string;
  start: Date;
  end: Date;
  interval?: string; // '1m', '5m', '1h', '1d'
  aggregation?: 'sum' | 'avg' | 'min' | 'max' | 'count';
  tags?: Record<string, string>;
}

export class TimeSeriesStore {
  constructor(private db: DatabaseManager) {
    this.initializeTimeSeriesTables();
  }

  private initializeTimeSeriesTables(): void {
    this.db.exec(`
      -- Raw time series data with compression
      CREATE TABLE IF NOT EXISTS time_series_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT NOT NULL,
        timestamp INTEGER NOT NULL, -- Unix timestamp for efficiency
        value REAL NOT NULL,
        tags TEXT, -- JSON string for tags
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      -- Pre-aggregated data for fast queries
      CREATE TABLE IF NOT EXISTS time_series_aggregated (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT NOT NULL,
        interval_type TEXT NOT NULL, -- '1m', '5m', '1h', '1d'
        timestamp INTEGER NOT NULL,
        value_sum REAL DEFAULT 0,
        value_avg REAL DEFAULT 0,
        value_min REAL DEFAULT NULL,
        value_max REAL DEFAULT NULL,
        value_count INTEGER DEFAULT 0,
        tags TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      -- Indexes for performance
      CREATE INDEX IF NOT EXISTS idx_ts_raw_metric_time ON time_series_raw(metric, timestamp);
      CREATE INDEX IF NOT EXISTS idx_ts_raw_timestamp ON time_series_raw(timestamp);
      CREATE INDEX IF NOT EXISTS idx_ts_agg_metric_interval_time ON time_series_aggregated(metric, interval_type, timestamp);
      
      -- Partitioning by day for large datasets
      CREATE TABLE IF NOT EXISTS time_series_partitions (
        partition_date TEXT PRIMARY KEY,
        table_name TEXT NOT NULL,
        row_count INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
  }

  async writePoints(metric: string, points: TimeSeriesPoint[]): Promise<void> {
    const stmt = this.db.prepare(`
      INSERT INTO time_series_raw (metric, timestamp, value, tags)
      VALUES (?, ?, ?, ?)
    `);

    const transaction = this.db.transaction((points: TimeSeriesPoint[]) => {
      for (const point of points) {
        stmt.run(
          metric,
          Math.floor(point.timestamp.getTime() / 1000),
          point.value,
          point.tags ? JSON.stringify(point.tags) : null
        );
      }
    });

    transaction(points);

    // Trigger aggregation for real-time data
    await this.updateAggregations(metric, points);
  }

  async query(query: TimeSeriesQuery): Promise<TimeSeriesPoint[]> {
    const startTimestamp = Math.floor(query.start.getTime() / 1000);
    const endTimestamp = Math.floor(query.end.getTime() / 1000);
    
    // Determine if we can use pre-aggregated data
    if (query.interval && this.shouldUseAggregatedData(query)) {
      return this.queryAggregated(query, startTimestamp, endTimestamp);
    }
    
    return this.queryRaw(query, startTimestamp, endTimestamp);
  }

  private async queryRaw(query: TimeSeriesQuery, start: number, end: number): Promise<TimeSeriesPoint[]> {
    let sql = `
      SELECT timestamp, value, tags
      FROM time_series_raw
      WHERE metric = ? AND timestamp BETWEEN ? AND ?
    `;
    
    const params = [query.metric, start, end];
    
    if (query.tags) {
      // Simple tag filtering - in production, consider using a JSON extension
      for (const [key, value] of Object.entries(query.tags)) {
        sql += ` AND json_extract(tags, '$.${key}') = ?`;
        params.push(value);
      }
    }
    
    sql += ` ORDER BY timestamp`;
    
    const rows = this.db.prepare(sql).all(...params) as any[];
    
    return rows.map(row => ({
      timestamp: new Date(row.timestamp * 1000),
      value: row.value,
      tags: row.tags ? JSON.parse(row.tags) : undefined
    }));
  }

  private async queryAggregated(query: TimeSeriesQuery, start: number, end: number): Promise<TimeSeriesPoint[]> {
    const valueColumn = query.aggregation ? `value_${query.aggregation}` : 'value_avg';
    
    const sql = `
      SELECT timestamp, ${valueColumn} as value, tags
      FROM time_series_aggregated
      WHERE metric = ? AND interval_type = ? AND timestamp BETWEEN ? AND ?
      ORDER BY timestamp
    `;
    
    const rows = this.db.prepare(sql).all(query.metric, query.interval, start, end) as any[];
    
    return rows.map(row => ({
      timestamp: new Date(row.timestamp * 1000),
      value: row.value,
      tags: row.tags ? JSON.parse(row.tags) : undefined
    }));
  }

  private shouldUseAggregatedData(query: TimeSeriesQuery): boolean {
    const timeRange = query.end.getTime() - query.start.getTime();
    const oneDayMs = 24 * 60 * 60 * 1000;
    
    // Use aggregated data for longer time ranges
    return timeRange > oneDayMs;
  }

  private async updateAggregations(metric: string, points: TimeSeriesPoint[]): Promise<void> {
    // Group points by different time intervals
    const intervals = ['1m', '5m', '1h', '1d'];
    
    for (const interval of intervals) {
      await this.aggregateForInterval(metric, points, interval);
    }
  }

  private async aggregateForInterval(metric: string, points: TimeSeriesPoint[], interval: string): Promise<void> {
    const buckets = new Map<number, { sum: number; count: number; min: number; max: number }>();
    
    // Calculate bucket size in seconds
    const bucketSize = this.getIntervalSeconds(interval);
    
    for (const point of points) {
      const bucketTimestamp = Math.floor(point.timestamp.getTime() / 1000 / bucketSize) * bucketSize;
      
      if (!buckets.has(bucketTimestamp)) {
        buckets.set(bucketTimestamp, {
          sum: 0,
          count: 0,
          min: point.value,
          max: point.value
        });
      }
      
      const bucket = buckets.get(bucketTimestamp)!;
      bucket.sum += point.value;
      bucket.count++;
      bucket.min = Math.min(bucket.min, point.value);
      bucket.max = Math.max(bucket.max, point.value);
    }
    
    // Insert or update aggregated data
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO time_series_aggregated 
      (metric, interval_type, timestamp, value_sum, value_avg, value_min, value_max, value_count)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    for (const [timestamp, bucket] of buckets) {
      stmt.run(
        metric,
        interval,
        timestamp,
        bucket.sum,
        bucket.sum / bucket.count,
        bucket.min,
        bucket.max,
        bucket.count
      );
    }
  }

  private getIntervalSeconds(interval: string): number {
    const map: Record<string, number> = {
      '1m': 60,
      '5m': 300,
      '1h': 3600,
      '1d': 86400
    };
    return map[interval] || 60;
  }

  // Data retention and cleanup
  async cleanupOldData(retentionDays: number): Promise<void> {
    const cutoffTimestamp = Math.floor((Date.now() - (retentionDays * 24 * 60 * 60 * 1000)) / 1000);
    
    // Remove old raw data
    this.db.prepare('DELETE FROM time_series_raw WHERE timestamp < ?').run(cutoffTimestamp);
    
    // Keep aggregated data longer
    const aggregatedCutoff = Math.floor((Date.now() - (retentionDays * 7 * 24 * 60 * 60 * 1000)) / 1000);
    this.db.prepare('DELETE FROM time_series_aggregated WHERE timestamp < ?').run(aggregatedCutoff);
  }
}
```

### 3. Advanced Analytics Calculations

#### Statistical Analysis Engine
```typescript
// analytics/statistical-analyzer.ts
export interface StatisticalSummary {
  count: number;
  sum: number;
  mean: number;
  median: number;
  mode: number[];
  variance: number;
  standardDeviation: number;
  min: number;
  max: number;
  range: number;
  percentiles: Record<number, number>;
  outliers: number[];
}

export interface TrendAnalysis {
  direction: 'increasing' | 'decreasing' | 'stable';
  slope: number;
  confidence: number;
  seasonality: {
    detected: boolean;
    period?: number;
    strength?: number;
  };
  anomalies: Array<{
    timestamp: Date;
    value: number;
    severity: 'low' | 'medium' | 'high';
    reason: string;
  }>;
}

export class StatisticalAnalyzer {
  // Calculate comprehensive statistics for a dataset
  calculateSummary(values: number[]): StatisticalSummary {
    if (values.length === 0) {
      throw new Error('Cannot calculate statistics for empty dataset');
    }

    const sorted = [...values].sort((a, b) => a - b);
    const count = values.length;
    const sum = values.reduce((acc, val) => acc + val, 0);
    const mean = sum / count;

    // Median calculation
    const median = count % 2 === 0
      ? (sorted[count / 2 - 1] + sorted[count / 2]) / 2
      : sorted[Math.floor(count / 2)];

    // Mode calculation (most frequent values)
    const frequency = new Map<number, number>();
    values.forEach(val => frequency.set(val, (frequency.get(val) || 0) + 1));
    const maxFreq = Math.max(...frequency.values());
    const mode = Array.from(frequency.entries())
      .filter(([_, freq]) => freq === maxFreq)
      .map(([val, _]) => val);

    // Variance and standard deviation
    const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / count;
    const standardDeviation = Math.sqrt(variance);

    // Min, max, range
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    const range = max - min;

    // Percentiles
    const percentiles: Record<number, number> = {};
    [25, 50, 75, 90, 95, 99].forEach(p => {
      percentiles[p] = this.calculatePercentile(sorted, p);
    });

    // Outlier detection using IQR method
    const q1 = percentiles[25];
    const q3 = percentiles[75];
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;
    const outliers = values.filter(val => val < lowerBound || val > upperBound);

    return {
      count,
      sum,
      mean,
      median,
      mode,
      variance,
      standardDeviation,
      min,
      max,
      range,
      percentiles,
      outliers
    };
  }

  // Analyze trends in time series data
  analyzeTrend(timeSeriesData: TimeSeriesPoint[]): TrendAnalysis {
    if (timeSeriesData.length < 3) {
      throw new Error('Need at least 3 data points for trend analysis');
    }

    const values = timeSeriesData.map(point => point.value);
    const timestamps = timeSeriesData.map(point => point.timestamp.getTime());

    // Linear regression for trend direction
    const { slope, correlation } = this.linearRegression(timestamps, values);
    
    const direction = slope > 0.01 ? 'increasing' : 
                     slope < -0.01 ? 'decreasing' : 'stable';
    
    const confidence = Math.abs(correlation);

    // Seasonality detection using autocorrelation
    const seasonality = this.detectSeasonality(values);

    // Anomaly detection using statistical methods
    const anomalies = this.detectAnomalies(timeSeriesData);

    return {
      direction,
      slope,
      confidence,
      seasonality,
      anomalies
    };
  }

  private calculatePercentile(sortedValues: number[], percentile: number): number {
    const index = (percentile / 100) * (sortedValues.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    
    if (lower === upper) {
      return sortedValues[lower];
    }
    
    const weight = index - lower;
    return sortedValues[lower] * (1 - weight) + sortedValues[upper] * weight;
  }

  private linearRegression(x: number[], y: number[]): { slope: number; intercept: number; correlation: number } {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumXX = x.reduce((sum, xi) => sum + xi * xi, 0);
    const sumYY = y.reduce((sum, yi) => sum + yi * yi, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    const correlation = (n * sumXY - sumX * sumY) / 
      Math.sqrt((n * sumXX - sumX * sumX) * (n * sumYY - sumY * sumY));

    return { slope, intercept, correlation };
  }

  private detectSeasonality(values: number[]): TrendAnalysis['seasonality'] {
    // Simple autocorrelation-based seasonality detection
    const maxLag = Math.min(values.length / 4, 50);
    let bestLag = 0;
    let bestCorrelation = 0;

    for (let lag = 1; lag <= maxLag; lag++) {
      const correlation = this.autocorrelation(values, lag);
      if (correlation > bestCorrelation) {
        bestCorrelation = correlation;
        bestLag = lag;
      }
    }

    const detected = bestCorrelation > 0.5;
    return {
      detected,
      period: detected ? bestLag : undefined,
      strength: detected ? bestCorrelation : undefined
    };
  }

  private autocorrelation(values: number[], lag: number): number {
    const n = values.length - lag;
    const mean1 = values.slice(0, n).reduce((a, b) => a + b, 0) / n;
    const mean2 = values.slice(lag).reduce((a, b) => a + b, 0) / n;

    let numerator = 0;
    let denominator1 = 0;
    let denominator2 = 0;

    for (let i = 0; i < n; i++) {
      const diff1 = values[i] - mean1;
      const diff2 = values[i + lag] - mean2;
      numerator += diff1 * diff2;
      denominator1 += diff1 * diff1;
      denominator2 += diff2 * diff2;
    }

    return numerator / Math.sqrt(denominator1 * denominator2);
  }

  private detectAnomalies(timeSeriesData: TimeSeriesPoint[]): TrendAnalysis['anomalies'] {
    const values = timeSeriesData.map(point => point.value);
    const stats = this.calculateSummary(values);
    const anomalies: TrendAnalysis['anomalies'] = [];

    // Statistical outlier detection
    const threshold1 = stats.mean + 2 * stats.standardDeviation;
    const threshold2 = stats.mean + 3 * stats.standardDeviation;
    const threshold3 = stats.mean - 2 * stats.standardDeviation;
    const threshold4 = stats.mean - 3 * stats.standardDeviation;

    timeSeriesData.forEach(point => {
      if (point.value > threshold2 || point.value < threshold4) {
        anomalies.push({
          timestamp: point.timestamp,
          value: point.value,
          severity: 'high',
          reason: 'Statistical outlier (3σ)'
        });
      } else if (point.value > threshold1 || point.value < threshold3) {
        anomalies.push({
          timestamp: point.timestamp,
          value: point.value,
          severity: 'medium',
          reason: 'Statistical outlier (2σ)'
        });
      }
    });

    return anomalies;
  }

  // Calculate moving averages for trend smoothing
  calculateMovingAverage(values: number[], windowSize: number): number[] {
    const result: number[] = [];
    
    for (let i = windowSize - 1; i < values.length; i++) {
      const window = values.slice(i - windowSize + 1, i + 1);
      const average = window.reduce((sum, val) => sum + val, 0) / windowSize;
      result.push(average);
    }
    
    return result;
  }

  // Calculate exponential moving average
  calculateEMA(values: number[], alpha: number = 0.1): number[] {
    const result: number[] = [values[0]];
    
    for (let i = 1; i < values.length; i++) {
      const ema = alpha * values[i] + (1 - alpha) * result[i - 1];
      result.push(ema);
    }
    
    return result;
  }
}
```

### 4. Data Visualization Preparation

#### Chart Data Transformer
```typescript
// analytics/chart-data-transformer.ts
export interface ChartDataPoint {
  x: string | number | Date;
  y: number;
  label?: string;
  color?: string;
  metadata?: Record<string, any>;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
  type?: 'line' | 'bar' | 'area' | 'scatter';
}

export interface ChartConfiguration {
  title: string;
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'heatmap' | 'histogram';
  series: ChartSeries[];
  xAxis?: {
    label: string;
    type: 'category' | 'time' | 'numeric';
    format?: string;
  };
  yAxis?: {
    label: string;
    format?: string;
    min?: number;
    max?: number;
  };
  options?: Record<string, any>;
}

export class ChartDataTransformer {
  // Transform time series data for line charts
  transformTimeSeriesForChart(
    timeSeriesData: TimeSeriesPoint[],
    title: string,
    seriesName: string = 'Value'
  ): ChartConfiguration {
    const data: ChartDataPoint[] = timeSeriesData.map(point => ({
      x: point.timestamp,
      y: point.value,
      metadata: point.tags
    }));

    return {
      title,
      type: 'line',
      series: [{
        name: seriesName,
        data,
        type: 'line'
      }],
      xAxis: {
        label: 'Time',
        type: 'time',
        format: 'YYYY-MM-DD HH:mm'
      },
      yAxis: {
        label: 'Value'
      }
    };
  }

  // Transform conversation metrics for dashboard
  transformConversationMetrics(metrics: ConversationMetrics[]): ChartConfiguration[] {
    const charts: ChartConfiguration[] = [];

    // Token usage over time
    const tokenData: ChartDataPoint[] = metrics.map((metric, index) => ({
      x: metric.createdAt,
      y: metric.totalTokens,
      label: metric.id,
      metadata: { messageCount: metric.messageCount }
    }));

    charts.push({
      title: 'Token Usage Over Time',
      type: 'line',
      series: [{
        name: 'Total Tokens',
        data: tokenData,
        type: 'line',
        color: '#3B82F6'
      }],
      xAxis: {
        label: 'Time',
        type: 'time'
      },
      yAxis: {
        label: 'Tokens'
      }
    });

    // Message count distribution
    const messageCountData = this.createHistogramData(
      metrics.map(m => m.messageCount),
      'Message Count Distribution'
    );

    charts.push({
      title: 'Message Count Distribution',
      type: 'histogram',
      series: [{
        name: 'Frequency',
        data: messageCountData,
        type: 'bar',
        color: '#10B981'
      }],
      xAxis: {
        label: 'Message Count',
        type: 'numeric'
      },
      yAxis: {
        label: 'Frequency'
      }
    });

    // Engagement vs Duration scatter plot
    const engagementData: ChartDataPoint[] = metrics.map(metric => ({
      x: metric.duration / 3600, // Convert to hours
      y: metric.userEngagement,
      label: metric.id,
      metadata: {
        messageCount: metric.messageCount,
        totalTokens: metric.totalTokens
      }
    }));

    charts.push({
      title: 'Engagement vs Duration',
      type: 'scatter',
      series: [{
        name: 'Conversations',
        data: engagementData,
        type: 'scatter',
        color: '#8B5CF6'
      }],
      xAxis: {
        label: 'Duration (hours)',
        type: 'numeric'
      },
      yAxis: {
        label: 'Engagement Score',
        min: 0,
        max: 100
      }
    });

    return charts;
  }

  // Transform user activity patterns
  transformUserActivityPattern(activityData: Record<string, number>): ChartConfiguration {
    const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
    const data: ChartDataPoint[] = hours.map(hour => ({
      x: `${hour}:00`,
      y: activityData[hour] || 0
    }));

    return {
      title: 'User Activity by Hour',
      type: 'bar',
      series: [{
        name: 'Activity Count',
        data,
        type: 'bar',
        color: '#F59E0B'
      }],
      xAxis: {
        label: 'Hour of Day',
        type: 'category'
      },
      yAxis: {
        label: 'Activity Count'
      }
    };
  }

  // Create heatmap for correlation analysis
  transformCorrelationMatrix(correlations: Record<string, Record<string, number>>): ChartConfiguration {
    const variables = Object.keys(correlations);
    const data: ChartDataPoint[] = [];

    variables.forEach((var1, i) => {
      variables.forEach((var2, j) => {
        data.push({
          x: i,
          y: j,
          label: `${var1} vs ${var2}`,
          metadata: {
            variable1: var1,
            variable2: var2,
            correlation: correlations[var1][var2]
          }
        });
      });
    });

    return {
      title: 'Correlation Matrix',
      type: 'heatmap',
      series: [{
        name: 'Correlation',
        data
      }],
      options: {
        variables,
        colorScale: {
          min: -1,
          max: 1,
          colors: ['#EF4444', '#FFFFFF', '#10B981']
        }
      }
    };
  }

  // Create histogram data
  private createHistogramData(values: number[], title: string): ChartDataPoint[] {
    if (values.length === 0) return [];

    const min = Math.min(...values);
    const max = Math.max(...values);
    const binCount = Math.min(20, Math.ceil(Math.sqrt(values.length)));
    const binWidth = (max - min) / binCount;

    const bins: number[] = new Array(binCount).fill(0);
    
    values.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binWidth), binCount - 1);
      bins[binIndex]++;
    });

    return bins.map((count, index) => ({
      x: min + (index + 0.5) * binWidth,
      y: count,
      label: `${(min + index * binWidth).toFixed(1)} - ${(min + (index + 1) * binWidth).toFixed(1)}`
    }));
  }

  // Transform real-time metrics for dashboard widgets
  transformRealTimeMetrics(metrics: any): Array<{
    id: string;
    title: string;
    value: number | string;
    change?: number;
    format?: string;
    color?: string;
  }> {
    return [
      {
        id: 'total-conversations',
        title: 'Total Conversations',
        value: metrics.totalConversations || 0,
        change: metrics.conversationGrowth || 0,
        format: 'number',
        color: '#3B82F6'
      },
      {
        id: 'total-messages',
        title: 'Total Messages',
        value: metrics.totalMessages || 0,
        change: metrics.messageGrowth || 0,
        format: 'number',
        color: '#10B981'
      },
      {
        id: 'total-tokens',
        title: 'Total Tokens',
        value: metrics.totalTokensProcessed || 0,
        change: metrics.tokenGrowth || 0,
        format: 'number',
        color: '#8B5CF6'
      },
      {
        id: 'active-users',
        title: 'Active Users',
        value: metrics.activeUsers || 0,
        change: metrics.userGrowth || 0,
        format: 'number',
        color: '#F59E0B'
      },
      {
        id: 'avg-response-time',
        title: 'Avg Response Time',
        value: `${(metrics.averageResponseTime || 0).toFixed(2)}s`,
        change: metrics.responseTimeChange || 0,
        format: 'duration',
        color: '#EF4444'
      },
      {
        id: 'system-uptime',
        title: 'System Uptime',
        value: `${(metrics.systemUptime || 0).toFixed(1)}%`,
        format: 'percentage',
        color: '#10B981'
      }
    ];
  }
}
```

### 5. Performance Optimization Strategies

#### Database Query Optimization
```typescript
// analytics/query-optimizer.ts
export class QueryOptimizer {
  constructor(private db: DatabaseManager) {}

  // Optimize analytics queries with caching and indexing
  async optimizeQuery<T>(
    queryKey: string,
    queryFn: () => Promise<T>,
    cacheTimeout: number = 300000 // 5 minutes
  ): Promise<T> {
    const cached = this.getFromCache<T>(queryKey);
    if (cached) {
      return cached;
    }

    const result = await queryFn();
    this.setCache(queryKey, result, cacheTimeout);
    return result;
  }

  // Batch processing for efficient data aggregation
  async batchProcessAnalytics(events: AnalyticsEvent[], batchSize: number = 1000): Promise<void> {
    const batches = this.chunkArray(events, batchSize);
    
    for (const batch of batches) {
      await this.processBatch(batch);
    }
  }

  private async processBatch(events: AnalyticsEvent[]): Promise<void> {
    // Group events by type for efficient processing
    const eventGroups = this.groupEventsByType(events);
    
    // Process each group with optimized queries
    await Promise.all([
      this.processConversationEvents(eventGroups.conversation_created || []),
      this.processMessageEvents(eventGroups.message_sent || []),
      this.processTokenEvents(eventGroups.token_usage || []),
      this.processUserActivityEvents(eventGroups.user_activity || [])
    ]);
  }

  // Memory-efficient data streaming for large datasets
  async streamLargeDataset<T>(
    query: string,
    processor: (row: any) => T,
    batchSize: number = 1000
  ): Promise<T[]> {
    const results: T[] = [];
    let offset = 0;
    
    while (true) {
      const batch = this.db.prepare(`${query} LIMIT ? OFFSET ?`).all(batchSize, offset);
      
      if (batch.length === 0) break;
      
      const processed = batch.map(processor);
      results.push(...processed);
      
      offset += batchSize;
      
      // Allow event loop to process other tasks
      await new Promise(resolve => setImmediate(resolve));
    }
    
    return results;
  }

  // Connection pooling for concurrent analytics queries
  private connectionPool: DatabaseManager[] = [];
  private readonly maxConnections = 5;

  async executeWithPool<T>(operation: (db: DatabaseManager) => Promise<T>): Promise<T> {
    const connection = await this.getConnection();
    try {
      return await operation(connection);
    } finally {
      this.releaseConnection(connection);
    }
  }

  private async getConnection(): Promise<DatabaseManager> {
    if (this.connectionPool.length > 0) {
      return this.connectionPool.pop()!;
    }
    
    if (this.connectionPool.length < this.maxConnections) {
      return new DatabaseManager(); // Create new connection
    }
    
    // Wait for a connection to become available
    return new Promise(resolve => {
      const checkForConnection = () => {
        if (this.connectionPool.length > 0) {
          resolve(this.connectionPool.pop()!);
        } else {
          setTimeout(checkForConnection, 10);
        }
      };
      checkForConnection();
    });
  }

  private releaseConnection(connection: DatabaseManager): void {
    this.connectionPool.push(connection);
  }

  // Query result caching
  private cache = new Map<string, { value: any; expiry: number }>();

  private getFromCache<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && cached.expiry > Date.now()) {
      return cached.value;
    }
    this.cache.delete(key);
    return null;
  }

  private setCache<T>(key: string, value: T, timeout: number): void {
    this.cache.set(key, {
      value,
      expiry: Date.now() + timeout
    });
  }

  // Utility methods
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  private groupEventsByType(events: AnalyticsEvent[]): Record<string, AnalyticsEvent[]> {
    return events.reduce((groups, event) => {
      if (!groups[event.type]) {
        groups[event.type] = [];
      }
      groups[event.type].push(event);
      return groups;
    }, {} as Record<string, AnalyticsEvent[]>);
  }

  private async processConversationEvents(events: AnalyticsEvent[]): Promise<void> {
    if (events.length === 0) return;
    
    const stmt = this.db.prepare(`
      INSERT OR IGNORE INTO conversation_analytics 
      (conversation_id, user_id, created_at, metadata)
      VALUES (?, ?, ?, ?)
    `);
    
    const transaction = this.db.transaction((events: AnalyticsEvent[]) => {
      for (const event of events) {
        stmt.run(
          event.conversationId,
          event.userId,
          event.timestamp.toISOString(),
          JSON.stringify(event.data)
        );
      }
    });
    
    transaction(events);
  }

  private async processMessageEvents(events: AnalyticsEvent[]): Promise<void> {
    // Similar optimized processing for message events
  }

  private async processTokenEvents(events: AnalyticsEvent[]): Promise<void> {
    // Similar optimized processing for token events
  }

  private async processUserActivityEvents(events: AnalyticsEvent[]): Promise<void> {
    // Similar optimized processing for user activity events
  }
}
```

### 6. Real-Time Analytics Dashboard Integration

#### WebSocket Analytics Broadcaster
```typescript
// analytics/websocket-broadcaster.ts
import { WebSocketServer, WebSocket } from 'ws';
import { EventEmitter } from 'events';

export interface AnalyticsUpdate {
  type: 'metric_update' | 'new_conversation' | 'new_message' | 'system_alert';
  timestamp: Date;
  data: any;
}

export class AnalyticsBroadcaster extends EventEmitter {
  private wss: WebSocketServer;
  private clients = new Set<WebSocket>();
  private updateBuffer: AnalyticsUpdate[] = [];
  private bufferFlushInterval: NodeJS.Timeout;

  constructor(port: number = 8081) {
    super();
    this.wss = new WebSocketServer({ port });
    this.setupWebSocketServer();
    this.startUpdateBuffer();
  }

  private setupWebSocketServer(): void {
    this.wss.on('connection', (ws: WebSocket) => {
      this.clients.add(ws);
      
      // Send initial dashboard data
      this.sendInitialData(ws);
      
      ws.on('close', () => {
        this.clients.delete(ws);
      });
      
      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(ws);
      });
    });
  }

  // Broadcast real-time updates to all connected clients
  broadcastUpdate(update: AnalyticsUpdate): void {
    this.updateBuffer.push(update);
    
    // If buffer is getting large, flush immediately
    if (this.updateBuffer.length >= 50) {
      this.flushUpdates();
    }
  }

  // Broadcast system metrics updates
  broadcastMetricsUpdate(metrics: any): void {
    this.broadcastUpdate({
      type: 'metric_update',
      timestamp: new Date(),
      data: metrics
    });
  }

  // Broadcast new conversation notification
  broadcastNewConversation(conversation: any): void {
    this.broadcastUpdate({
      type: 'new_conversation',
      timestamp: new Date(),
      data: conversation
    });
  }

  // Broadcast system alerts
  broadcastAlert(alert: { severity: string; message: string; details?: any }): void {
    this.broadcastUpdate({
      type: 'system_alert',
      timestamp: new Date(),
      data: alert
    });
  }

  private startUpdateBuffer(): void {
    // Flush updates every 1 second
    this.bufferFlushInterval = setInterval(() => {
      this.flushUpdates();
    }, 1000);
  }

  private flushUpdates(): void {
    if (this.updateBuffer.length === 0) return;
    
    const updates = [...this.updateBuffer];
    this.updateBuffer = [];
    
    const message = JSON.stringify({
      type: 'batch_update',
      updates,
      timestamp: new Date()
    });
    
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  private async sendInitialData(ws: WebSocket): Promise<void> {
    try {
      // Send current dashboard state to new client
      const dashboardData = await this.getCurrentDashboardData();
      
      ws.send(JSON.stringify({
        type: 'initial_data',
        data: dashboardData,
        timestamp: new Date()
      }));
    } catch (error) {
      console.error('Failed to send initial data:', error);
    }
  }

  private async getCurrentDashboardData(): Promise<any> {
    // This would integrate with your analytics engine
    // to get current dashboard state
    return {
      overview: {
        totalConversations: 0,
        totalMessages: 0,
        totalTokens: 0,
        activeUsers: 0
      },
      recentActivity: [],
      systemStatus: 'healthy'
    };
  }

  close(): void {
    clearInterval(this.bufferFlushInterval);
    this.wss.close();
  }
}
```

## Implementation Guidelines

### Week 9 Development Priorities

1. **Day 1-2**: Implement core analytics engine and stream processing
2. **Day 3**: Set up time-series data storage and aggregation
3. **Day 4**: Develop statistical analysis and chart data transformation
4. **Day 5**: Optimize performance and implement caching strategies

### Performance Targets
- Process 10,000+ events per minute
- Analytics queries under 500ms response time
- Real-time updates within 30 seconds
- Memory usage under 256MB for analytics engine

### Best Practices
- Use prepared statements for all database operations
- Implement connection pooling for concurrent queries
- Cache frequently accessed data with appropriate TTL
- Use batch processing for large datasets
- Monitor query performance and optimize indexes
- Implement graceful error handling and recovery

This comprehensive analytics foundation provides the building blocks for a robust, scalable analytics system that can handle real-time data processing, statistical analysis, and efficient data visualization preparation.