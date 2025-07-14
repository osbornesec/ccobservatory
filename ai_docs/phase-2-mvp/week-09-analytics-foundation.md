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