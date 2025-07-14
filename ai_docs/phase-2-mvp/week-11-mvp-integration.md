# Week 11: MVP Integration & End-to-End Testing

## Overview
Integrate all Phase 2 components into a cohesive MVP system, conducting comprehensive end-to-end testing, performance optimization, and user acceptance validation. This week ensures all systems work together seamlessly to deliver a functional Claude Code Observatory MVP.

## Team Assignments
- **Full-Stack Lead**: End-to-end integration, system orchestration, deployment preparation
- **Backend Developer**: API integration testing, performance optimization, data flow validation
- **Frontend Developer**: UI/UX integration, user flow testing, responsive design validation
- **QA Engineer**: Comprehensive testing, bug tracking, acceptance criteria validation

## Daily Schedule

### Monday: System Integration & API Orchestration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Backend service integration and health monitoring
- **10:30-12:00**: Frontend-backend API integration validation

#### Afternoon (4 hours)
- **13:00-15:00**: WebSocket real-time feature integration testing
- **15:00-17:00**: Analytics pipeline end-to-end integration

### Tuesday: User Flow & Experience Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Complete user journey testing (onboarding to insights)
- **10:30-12:00**: Conversation management workflow validation

#### Afternoon (4 hours)
- **13:00-15:00**: Real-time collaboration features testing
- **15:00-17:00**: Dashboard and analytics user experience validation

### Wednesday: Performance Optimization & Load Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Database query optimization and indexing
- **10:30-12:00**: Frontend performance optimization and code splitting

#### Afternoon (4 hours)
- **13:00-15:00**: Load testing with simulated user scenarios
- **15:00-17:00**: Memory usage optimization and leak detection

### Thursday: Cross-Platform & Browser Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Cross-browser compatibility testing (Chrome, Firefox, Safari, Edge)
- **10:30-12:00**: Mobile and tablet responsive design validation

#### Afternoon (4 hours)
- **13:00-15:00**: Operating system compatibility testing
- **15:00-17:00**: Accessibility compliance validation (WCAG 2.1 AA)

### Friday: MVP Validation & Deployment Preparation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Final acceptance criteria validation
- **10:30-12:00**: Security audit and vulnerability assessment

#### Afternoon (4 hours)
- **13:00-15:00**: Production deployment preparation and configuration
- **15:00-17:00**: Documentation finalization and handoff preparation

## Technical Implementation Details

### Integration Test Suite
```typescript
// tests/integration/mvp-integration.test.ts
import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import { TestApplication } from './helpers/test-application';
import { TestDataGenerator } from './helpers/test-data-generator';
import { WebSocketClient } from '@/services/websocket';
import { ApiClient } from '@/services/api';

describe('MVP Integration Tests', () => {
  let app: TestApplication;
  let apiClient: ApiClient;
  let wsClient: WebSocketClient;
  let testData: TestDataGenerator;

  beforeAll(async () => {
    app = new TestApplication();
    await app.start();
    
    apiClient = new ApiClient(app.getApiUrl());
    wsClient = new WebSocketClient(app.getWsUrl());
    testData = new TestDataGenerator();
  });

  afterAll(async () => {
    await wsClient.disconnect();
    await app.stop();
  });

  describe('Complete User Journey', () => {
    test('should handle full conversation lifecycle', async () => {
      // 1. User authentication
      const user = await testData.createTestUser();
      const authToken = await apiClient.authenticate(user.credentials);
      expect(authToken).toBeDefined();

      // 2. Create conversation
      const conversationData = testData.generateConversationData();
      const conversation = await apiClient.createConversation(conversationData);
      expect(conversation.id).toBeDefined();

      // 3. Establish WebSocket connection
      await wsClient.connect(authToken);
      const connectionEstablished = await wsClient.waitForConnection();
      expect(connectionEstablished).toBe(true);

      // 4. Subscribe to conversation updates
      await wsClient.subscribe(`conversation:${conversation.id}`);

      // 5. Send messages and verify real-time updates
      const messages = testData.generateMessages(10);
      const receivedUpdates: any[] = [];

      wsClient.on('new_message', (data) => {
        receivedUpdates.push(data);
      });

      for (const messageData of messages) {
        const message = await apiClient.sendMessage(conversation.id, messageData);
        expect(message.id).toBeDefined();
      }

      // Wait for real-time updates
      await new Promise(resolve => setTimeout(resolve, 2000));
      expect(receivedUpdates).toHaveLength(messages.length);

      // 6. Verify analytics data
      const analytics = await apiClient.getConversationAnalytics(conversation.id);
      expect(analytics.messageCount).toBe(messages.length);
      expect(analytics.totalTokens).toBeGreaterThan(0);

      // 7. Test dashboard data
      const dashboardData = await apiClient.getDashboardData();
      expect(dashboardData.overview.totalConversations).toBeGreaterThan(0);
      expect(dashboardData.overview.totalMessages).toBeGreaterThan(0);
    });

    test('should handle concurrent users and conversations', async () => {
      const userCount = 5;
      const conversationsPerUser = 3;
      const messagesPerConversation = 10;

      const users = await Promise.all(
        Array.from({ length: userCount }, () => testData.createTestUser())
      );

      const authTokens = await Promise.all(
        users.map(user => apiClient.authenticate(user.credentials))
      );

      // Create conversations concurrently
      const conversationPromises = authTokens.flatMap((token, userIndex) =>
        Array.from({ length: conversationsPerUser }, async () => {
          const conversationData = testData.generateConversationData();
          return await apiClient.createConversation(conversationData, token);
        })
      );

      const conversations = await Promise.all(conversationPromises);
      expect(conversations).toHaveLength(userCount * conversationsPerUser);

      // Send messages concurrently
      const messagePromises = conversations.flatMap(conversation =>
        Array.from({ length: messagesPerConversation }, async () => {
          const messageData = testData.generateMessageData();
          return await apiClient.sendMessage(conversation.id, messageData);
        })
      );

      const messages = await Promise.all(messagePromises);
      expect(messages).toHaveLength(userCount * conversationsPerUser * messagesPerConversation);

      // Verify system metrics
      const systemMetrics = await apiClient.getSystemMetrics();
      expect(systemMetrics.totalConversations).toBeGreaterThanOrEqual(userCount * conversationsPerUser);
      expect(systemMetrics.totalMessages).toBeGreaterThanOrEqual(messages.length);
      expect(systemMetrics.activeUsers).toBeGreaterThanOrEqual(userCount);
    });
  });

  describe('Real-Time Features', () => {
    test('should handle typing indicators', async () => {
      const user1 = await testData.createTestUser();
      const user2 = await testData.createTestUser();
      
      const token1 = await apiClient.authenticate(user1.credentials);
      const token2 = await apiClient.authenticate(user2.credentials);

      const conversation = await apiClient.createConversation(
        testData.generateConversationData(),
        token1
      );

      // Connect both users
      const ws1 = new WebSocketClient(app.getWsUrl());
      const ws2 = new WebSocketClient(app.getWsUrl());

      await ws1.connect(token1);
      await ws2.connect(token2);

      await ws1.subscribe(`conversation:${conversation.id}`);
      await ws2.subscribe(`conversation:${conversation.id}`);

      // Test typing indicator
      const typingEvents: any[] = [];
      ws2.on('typing_indicator', (data) => {
        typingEvents.push(data);
      });

      // User 1 starts typing
      await ws1.send('typing_start', { conversationId: conversation.id });
      
      // Wait for event propagation
      await new Promise(resolve => setTimeout(resolve, 500));
      
      expect(typingEvents).toHaveLength(1);
      expect(typingEvents[0].userId).toBe(user1.id);
      expect(typingEvents[0].isTyping).toBe(true);

      // User 1 stops typing
      await ws1.send('typing_stop', { conversationId: conversation.id });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      expect(typingEvents).toHaveLength(2);
      expect(typingEvents[1].isTyping).toBe(false);

      await ws1.disconnect();
      await ws2.disconnect();
    });

    test('should handle presence updates', async () => {
      const users = await Promise.all([
        testData.createTestUser(),
        testData.createTestUser(),
        testData.createTestUser()
      ]);

      const tokens = await Promise.all(
        users.map(user => apiClient.authenticate(user.credentials))
      );

      const wsClients = tokens.map(() => new WebSocketClient(app.getWsUrl()));
      
      // Connect users sequentially
      const presenceEvents: any[] = [];
      wsClients[0].on('user_presence', (data) => {
        presenceEvents.push(data);
      });

      await wsClients[0].connect(tokens[0]);

      for (let i = 1; i < wsClients.length; i++) {
        await wsClients[i].connect(tokens[i]);
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // Verify presence events were received
      expect(presenceEvents.length).toBeGreaterThan(0);
      
      // Disconnect users and verify offline events
      for (const client of wsClients) {
        await client.disconnect();
      }
    });
  });

  describe('Analytics Integration', () => {
    test('should accurately track and aggregate metrics', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      // Create multiple conversations with varying message counts
      const conversationConfigs = [
        { messageCount: 5, tokenCount: 1000 },
        { messageCount: 10, tokenCount: 2500 },
        { messageCount: 3, tokenCount: 500 }
      ];

      const conversations = [];
      for (const config of conversationConfigs) {
        const conversation = await apiClient.createConversation(
          testData.generateConversationData(),
          token
        );

        const messages = testData.generateMessages(config.messageCount);
        for (const messageData of messages) {
          messageData.tokenCount = Math.floor(config.tokenCount / config.messageCount);
          await apiClient.sendMessage(conversation.id, messageData, token);
        }

        conversations.push({ ...conversation, ...config });
      }

      // Wait for analytics processing
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Verify conversation-level metrics
      for (const conv of conversations) {
        const metrics = await apiClient.getConversationAnalytics(conv.id);
        expect(metrics.messageCount).toBe(conv.messageCount);
        expect(metrics.totalTokens).toBeCloseTo(conv.tokenCount, -2); // Within 100 tokens
      }

      // Verify user-level metrics
      const userMetrics = await apiClient.getUserMetrics(user.id);
      expect(userMetrics.conversationCount).toBe(conversationConfigs.length);
      expect(userMetrics.totalMessages).toBe(
        conversationConfigs.reduce((sum, config) => sum + config.messageCount, 0)
      );

      // Verify system-level metrics
      const systemMetrics = await apiClient.getSystemMetrics();
      expect(systemMetrics.totalConversations).toBeGreaterThanOrEqual(conversationConfigs.length);
      expect(systemMetrics.averageConversationLength).toBeGreaterThan(0);
    });

    test('should provide real-time analytics updates', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      const wsClient = new WebSocketClient(app.getWsUrl());
      await wsClient.connect(token);

      const analyticsUpdates: any[] = [];
      wsClient.on('analytics_conversations', (data) => {
        analyticsUpdates.push(data);
      });

      // Subscribe to analytics updates
      await wsClient.subscribe('analytics:conversations');

      // Create conversation to trigger analytics update
      const conversation = await apiClient.createConversation(
        testData.generateConversationData(),
        token
      );

      // Wait for analytics update
      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(analyticsUpdates.length).toBeGreaterThan(0);
      
      await wsClient.disconnect();
    });
  });

  describe('Error Handling & Recovery', () => {
    test('should handle API errors gracefully', async () => {
      // Test with invalid authentication
      const invalidClient = new ApiClient(app.getApiUrl());
      
      await expect(
        invalidClient.createConversation(testData.generateConversationData(), 'invalid-token')
      ).rejects.toThrow();

      // Test with non-existent resources
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      await expect(
        apiClient.getConversation('non-existent-id', token)
      ).rejects.toThrow();

      await expect(
        apiClient.sendMessage('non-existent-id', testData.generateMessageData(), token)
      ).rejects.toThrow();
    });

    test('should handle WebSocket connection failures', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      const wsClient = new WebSocketClient('ws://invalid-url:9999');
      
      let connectionError = false;
      wsClient.on('error', () => {
        connectionError = true;
      });

      try {
        await wsClient.connect(token);
      } catch (error) {
        connectionError = true;
      }

      expect(connectionError).toBe(true);
    });

    test('should recover from temporary service interruptions', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      const conversation = await apiClient.createConversation(
        testData.generateConversationData(),
        token
      );

      // Simulate service interruption by creating messages rapidly
      const rapidMessages = Array.from({ length: 50 }, () => 
        testData.generateMessageData()
      );

      const results = await Promise.allSettled(
        rapidMessages.map(messageData =>
          apiClient.sendMessage(conversation.id, messageData, token)
        )
      );

      const successful = results.filter(result => result.status === 'fulfilled');
      const failed = results.filter(result => result.status === 'rejected');

      // Most messages should succeed, some may fail due to rate limiting
      expect(successful.length).toBeGreaterThan(rapidMessages.length * 0.8);
      
      // System should remain stable
      const finalMetrics = await apiClient.getConversationAnalytics(conversation.id);
      expect(finalMetrics.messageCount).toBe(successful.length);
    });
  });
});
```

### Performance Test Suite
```typescript
// tests/performance/mvp-performance.test.ts
import { describe, test, expect } from 'vitest';
import { PerformanceTestRunner } from './helpers/performance-runner';
import { LoadTestScenario } from './helpers/load-test-scenario';

describe('MVP Performance Tests', () => {
  const perfRunner = new PerformanceTestRunner();

  test('should handle 100 concurrent users', async () => {
    const scenario = new LoadTestScenario({
      userCount: 100,
      rampUpTime: 60000, // 1 minute
      testDuration: 300000, // 5 minutes
      actions: [
        { type: 'login', weight: 1 },
        { type: 'createConversation', weight: 0.3 },
        { type: 'sendMessage', weight: 2 },
        { type: 'viewDashboard', weight: 0.5 },
        { type: 'exportData', weight: 0.1 }
      ]
    });

    const results = await perfRunner.runScenario(scenario);

    // Performance requirements
    expect(results.averageResponseTime).toBeLessThan(500); // 500ms average
    expect(results.p95ResponseTime).toBeLessThan(2000); // 2s 95th percentile
    expect(results.errorRate).toBeLessThan(0.01); // <1% error rate
    expect(results.throughput).toBeGreaterThan(10); // >10 requests/second
    
    // Resource usage
    expect(results.maxMemoryUsage).toBeLessThan(1024 * 1024 * 1024); // <1GB
    expect(results.maxCpuUsage).toBeLessThan(80); // <80% CPU

    // Database performance
    expect(results.averageDbQueryTime).toBeLessThan(100); // 100ms average
    expect(results.connectionPoolUtilization).toBeLessThan(0.8); // <80% pool usage
  });

  test('should handle large conversation processing', async () => {
    const largeConversationTest = async () => {
      const startTime = performance.now();
      
      // Create conversation with 1000 messages
      const conversation = await perfRunner.createLargeConversation({
        messageCount: 1000,
        averageMessageLength: 500,
        includeCodeBlocks: true
      });

      const processingTime = performance.now() - startTime;
      
      // Verify analytics calculation performance
      const analyticsStartTime = performance.now();
      const analytics = await perfRunner.getConversationAnalytics(conversation.id);
      const analyticsTime = performance.now() - analyticsStartTime;

      return {
        processingTime,
        analyticsTime,
        analytics
      };
    };

    const result = await largeConversationTest();

    // Processing should complete within reasonable time
    expect(result.processingTime).toBeLessThan(30000); // 30 seconds
    expect(result.analyticsTime).toBeLessThan(5000); // 5 seconds

    // Analytics should be accurate
    expect(result.analytics.messageCount).toBe(1000);
    expect(result.analytics.totalTokens).toBeGreaterThan(0);
  });

  test('should handle real-time updates under load', async () => {
    const realtimeLoadTest = async () => {
      const connectionCount = 50;
      const messageRate = 10; // messages per second per connection
      const testDuration = 60000; // 1 minute

      const connections = await perfRunner.createWebSocketConnections(connectionCount);
      
      const startTime = performance.now();
      const messagesSent: number[] = [];
      const messagesReceived: number[] = [];
      const latencies: number[] = [];

      // Start sending messages from all connections
      const sendingPromises = connections.map(async (conn, index) => {
        const conversation = await perfRunner.createConversation();
        await conn.subscribe(`conversation:${conversation.id}`);

        let sentCount = 0;
        let receivedCount = 0;

        conn.on('new_message', (data) => {
          const latency = Date.now() - data.timestamp;
          latencies.push(latency);
          receivedCount++;
        });

        const interval = setInterval(async () => {
          if (performance.now() - startTime > testDuration) {
            clearInterval(interval);
            messagesSent[index] = sentCount;
            messagesReceived[index] = receivedCount;
            return;
          }

          await conn.sendMessage(conversation.id, {
            content: `Test message ${sentCount}`,
            timestamp: Date.now()
          });
          sentCount++;
        }, 1000 / messageRate);
      });

      await Promise.all(sendingPromises);
      await perfRunner.disconnectWebSocketConnections(connections);

      return {
        totalSent: messagesSent.reduce((sum, count) => sum + count, 0),
        totalReceived: messagesReceived.reduce((sum, count) => sum + count, 0),
        averageLatency: latencies.reduce((sum, lat) => sum + lat, 0) / latencies.length,
        p95Latency: latencies.sort()[Math.floor(latencies.length * 0.95)]
      };
    };

    const result = await realtimeLoadTest();

    // Message delivery should be reliable
    expect(result.totalReceived / result.totalSent).toBeGreaterThan(0.95); // >95% delivery rate

    // Latency should be acceptable
    expect(result.averageLatency).toBeLessThan(100); // <100ms average
    expect(result.p95Latency).toBeLessThan(500); // <500ms 95th percentile
  });

  test('should handle dashboard queries under load', async () => {
    const dashboardLoadTest = async () => {
      // Pre-populate with test data
      await perfRunner.populateTestData({
        conversationCount: 1000,
        averageMessagesPerConversation: 50,
        userCount: 100,
        timeSpan: 90 // days
      });

      const concurrentQueries = 20;
      const queryTypes = [
        'getDashboardData',
        'getConversationMetrics',
        'getUserMetrics',
        'getSystemMetrics'
      ];

      const startTime = performance.now();
      const results = await Promise.all(
        Array.from({ length: concurrentQueries }, async () => {
          const queryType = queryTypes[Math.floor(Math.random() * queryTypes.length)];
          const queryStart = performance.now();
          
          try {
            await perfRunner.executeQuery(queryType);
            return performance.now() - queryStart;
          } catch (error) {
            throw new Error(`Query ${queryType} failed: ${error.message}`);
          }
        })
      );

      return {
        totalTime: performance.now() - startTime,
        averageQueryTime: results.reduce((sum, time) => sum + time, 0) / results.length,
        maxQueryTime: Math.max(...results),
        minQueryTime: Math.min(...results)
      };
    };

    const result = await dashboardLoadTest();

    // Query performance requirements
    expect(result.averageQueryTime).toBeLessThan(500); // 500ms average
    expect(result.maxQueryTime).toBeLessThan(2000); // 2s maximum
    expect(result.totalTime).toBeLessThan(10000); // 10s total for all concurrent queries
  });
});
```

### End-to-End User Flow Test
```typescript
// tests/e2e/user-flow.test.ts
import { test, expect } from '@playwright/test';

test.describe('Complete User Flow', () => {
  test('should complete full MVP user journey', async ({ page, browser }) => {
    // 1. Navigate to application
    await page.goto('/');
    await expect(page).toHaveTitle(/Claude Code Observatory/);

    // 2. User registration/login
    await page.click('[data-testid="login-button"]');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'testpassword');
    await page.click('[data-testid="submit-login"]');

    // Wait for navigation to dashboard
    await expect(page).toHaveURL(/\/dashboard/);

    // 3. Create new conversation
    await page.click('[data-testid="new-conversation-button"]');
    await page.fill('[data-testid="conversation-title"]', 'Test Conversation');
    await page.click('[data-testid="create-conversation-submit"]');

    // Verify conversation created
    await expect(page.locator('[data-testid="conversation-title"]')).toContainText('Test Conversation');

    // 4. Send messages
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-message"]');

    await messageInput.fill('Hello, this is a test message');
    await sendButton.click();

    // Verify message appears
    await expect(page.locator('[data-testid="message-list"]')).toContainText('Hello, this is a test message');

    // Send another message with code
    await messageInput.fill('Here is some code:\n\n```javascript\nconsole.log("Hello World");\n```');
    await sendButton.click();

    // Verify code block rendering
    await expect(page.locator('[data-testid="code-block"]')).toBeVisible();

    // 5. Test real-time features
    const secondBrowser = await browser.newContext();
    const secondPage = await secondBrowser.newPage();
    
    // Login with second user (simulate in real test)
    await secondPage.goto('/conversations/[conversation-id]');
    // ... authentication steps for second user
    
    // Test typing indicators
    await messageInput.click();
    await messageInput.type('Typing a message...');
    
    // Verify typing indicator appears for other user
    await expect(secondPage.locator('[data-testid="typing-indicator"]')).toBeVisible();
    
    await messageInput.press('Enter');
    
    // Verify typing indicator disappears
    await expect(secondPage.locator('[data-testid="typing-indicator"]')).not.toBeVisible();

    // 6. Navigate to analytics dashboard
    await page.click('[data-testid="analytics-nav"]');
    await expect(page).toHaveURL(/\/analytics/);

    // Verify analytics components load
    await expect(page.locator('[data-testid="metrics-cards"]')).toBeVisible();
    await expect(page.locator('[data-testid="conversation-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-chart"]')).toBeVisible();

    // Test chart interactions
    await page.hover('[data-testid="conversation-chart"]');
    await expect(page.locator('[data-testid="chart-tooltip"]')).toBeVisible();

    // 7. Test data export
    await page.click('[data-testid="export-button"]');
    await page.click('[data-testid="export-csv"]');

    // Verify download initiated (check for download event)
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="confirm-export"]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.csv');

    // 8. Test responsive design
    await page.setViewportSize({ width: 768, height: 1024 }); // Tablet
    await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();

    await page.setViewportSize({ width: 375, height: 667 }); // Mobile
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();

    // 9. Test accessibility
    const accessibilityResults = await page.evaluate(() => {
      // Run basic accessibility checks
      const focusableElements = document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      const elementsWithAriaLabels = document.querySelectorAll('[aria-label], [aria-labelledby]');
      
      return {
        focusableElementsCount: focusableElements.length,
        elementsWithAriaLabelsCount: elementsWithAriaLabels.length,
        hasSkipLink: !!document.querySelector('[data-testid="skip-link"]')
      };
    });

    expect(accessibilityResults.focusableElementsCount).toBeGreaterThan(0);
    expect(accessibilityResults.elementsWithAriaLabelsCount).toBeGreaterThan(0);
    expect(accessibilityResults.hasSkipLink).toBe(true);

    // 10. Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    await expect(page).toHaveURL(/\/login/);

    await secondBrowser.close();
  });

  test('should handle error scenarios gracefully', async ({ page }) => {
    await page.goto('/');

    // Test network error handling
    await page.route('**/api/**', route => route.abort());
    
    await page.click('[data-testid="login-button"]');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'testpassword');
    await page.click('[data-testid="submit-login"]');

    // Verify error message displayed
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Connection error');

    // Test retry functionality
    await page.unroute('**/api/**');
    await page.click('[data-testid="retry-button"]');

    // Should succeed after retry
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
```

## Performance Requirements
- **Page Load Time**: Initial page load within 3 seconds
- **API Response Time**: All API calls respond within 500ms
- **Real-time Latency**: WebSocket messages delivered within 100ms
- **Concurrent Users**: Support 100+ concurrent users
- **Memory Usage**: Client-side memory under 150MB, server under 1GB

## Acceptance Criteria
- [ ] Complete end-to-end user journey functional
- [ ] All Phase 2 components integrated and working
- [ ] Real-time features working across multiple users
- [ ] Analytics dashboard displaying accurate data
- [ ] Performance requirements met under load
- [ ] Cross-browser compatibility verified
- [ ] Mobile and tablet responsiveness validated
- [ ] Accessibility compliance (WCAG 2.1 AA) achieved
- [ ] Security audit completed with no critical issues
- [ ] MVP ready for production deployment

## Testing Procedures
1. **Integration Testing**: Complete system integration validation
2. **User Acceptance Testing**: End-to-end user flow validation
3. **Performance Testing**: Load and stress testing under realistic conditions
4. **Cross-Platform Testing**: Browser and device compatibility validation
5. **Security Testing**: Vulnerability assessment and penetration testing
6. **Accessibility Testing**: WCAG compliance and assistive technology testing

## Integration Points
- **All Phase 2 Weeks**: Complete system integration
- **Phase 1 Components**: File monitoring and data ingestion integration
- **External Services**: Authentication, monitoring, and logging integration

## Deployment Preparation
- Production environment configuration
- Database migration scripts
- Environment variable documentation
- Monitoring and alerting setup
- Backup and recovery procedures
- SSL certificate configuration
- CDN setup for static assets
- Load balancer configuration

## Risk Mitigation
- **Performance Bottlenecks**: Comprehensive load testing and optimization
- **Integration Issues**: Thorough cross-component testing
- **Security Vulnerabilities**: Multiple security audits and penetration testing
- **Browser Compatibility**: Extensive cross-browser testing
- **Data Integrity**: Database transaction testing and backup validation

## Success Metrics
- **Functionality**: 100% of acceptance criteria met
- **Performance**: All performance benchmarks achieved
- **Quality**: Zero critical bugs, <5 minor bugs
- **User Experience**: Smooth user flows with <2% error rate
- **Compatibility**: Works across 95% of target browsers/devices

## Post-Integration Tasks
- Performance monitoring setup
- User feedback collection system
- Error tracking and logging
- Documentation finalization
- Team handoff and knowledge transfer
- Production deployment checklist
- Rollback procedures documentation