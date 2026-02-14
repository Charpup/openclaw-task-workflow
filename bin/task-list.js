#!/usr/bin/env node
/**
 * Task List - List active tasks
 * Usage: node bin/task-list.js [options]
 */

const TaskIndexManager = require('../lib/task-index-manager');

async function main() {
  const args = process.argv.slice(2);
  
  const showAll = args.includes('--all') || args.includes('-a');
  const showCompleted = args.includes('--completed') || args.includes('-c');

  const manager = new TaskIndexManager();
  
  try {
    await manager.init();
    
    const report = await manager.generateReport();

    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║              Task Workflow Dashboard                   ║');
    console.log('╚════════════════════════════════════════════════════════╝\n');

    console.log(`📊 Summary: ${report.summary.totalActive} active, ${report.summary.completed} completed\n`);

    if (report.inProgressTasks.length > 0) {
      console.log('🔄 In Progress:');
      for (const task of report.inProgressTasks) {
        console.log(`   #${task.number} ${task.name} (${task.priority})`);
      }
      console.log('');
    }

    if (report.pendingTasks.length > 0) {
      console.log('⏳ Pending:');
      for (const task of report.pendingTasks) {
        console.log(`   #${task.number} ${task.name} (${task.priority})`);
      }
      console.log('');
    }

    if (showCompleted || showAll) {
      if (report.recentArchived.length > 0) {
        console.log('✅ Recently Completed:');
        for (const task of report.recentArchived) {
          console.log(`   #${task.number} ${task.name}`);
        }
        console.log('');
      }
    }

    if (report.summary.totalActive === 0) {
      console.log('🎉 All tasks completed! Use task-new.js to create new tasks.\n');
    }
    
  } catch (error) {
    console.error('❌ Failed to list tasks:', error.message);
    process.exit(1);
  }
}

main();
