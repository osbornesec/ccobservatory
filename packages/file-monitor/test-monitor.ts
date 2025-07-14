#!/usr/bin/env bun

/**
 * Test script for the file monitoring system
 * This script demonstrates how to use the FileMonitor to watch Claude Code files
 */

import { FileMonitor } from './src/index.ts';

async function testFileMonitor() {
  console.log('🚀 Starting Claude Code Observatory File Monitor Test');

  const monitor = new FileMonitor({
    enableDiscovery: true,
    performInitialScan: true,
    collectMetrics: true
  });

  // Set up event listeners
  monitor.on('ready', () => {
    console.log('✅ File monitor is ready');
    const status = monitor.getStatus();
    console.log('📊 Status:', status);
  });

  monitor.on('discoveryComplete', (result) => {
    console.log('🔍 Discovery completed:');
    console.log(`   Projects: ${result.projects.length}`);
    console.log(`   Conversations: ${result.conversations.length}`);
    console.log(`   Total messages: ${result.totalMessages}`);
    console.log(`   Total tokens: ${result.totalTokens}`);
    console.log(`   Processing errors: ${result.processingErrors.length}`);
    console.log(`   Scan duration: ${result.scanDuration}ms`);
  });

  monitor.on('fileAdded', (event) => {
    console.log(`📁 File added: ${event.filePath}`);
    if (event.messages) {
      console.log(`   Messages: ${event.messages.length}`);
    }
  });

  monitor.on('fileChanged', (event) => {
    console.log(`📝 File changed: ${event.filePath}`);
    if (event.newLines) {
      console.log(`   New messages: ${event.newLines.length}`);
    }
  });

  monitor.on('fileRemoved', (event) => {
    console.log(`🗑️ File removed: ${event.filePath}`);
  });

  monitor.on('projectDiscovered', (projectPath) => {
    console.log(`📂 Project discovered: ${projectPath}`);
  });

  monitor.on('error', (error) => {
    console.error('❌ Error:', error.message);
  });

  monitor.on('metricsUpdate', (metrics) => {
    console.log('📈 Metrics update:');
    console.log(`   Memory: ${(metrics.memoryUsage / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   Files watched: ${metrics.filesWatched}`);
  });

  try {
    // Start monitoring
    await monitor.start();
    
    console.log('🎯 File monitor started successfully');
    console.log('👀 Watching for Claude Code conversation changes...');
    console.log('Press Ctrl+C to stop');

    // Keep the process running
    process.on('SIGINT', async () => {
      console.log('\n🛑 Stopping file monitor...');
      await monitor.stop();
      console.log('✅ File monitor stopped');
      process.exit(0);
    });

    // Prevent the process from exiting
    setInterval(() => {}, 1000);

  } catch (error) {
    console.error('💥 Failed to start file monitor:', error);
    process.exit(1);
  }
}

// Run the test if this script is executed directly
if (import.meta.main) {
  testFileMonitor().catch(console.error);
}