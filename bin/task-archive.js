#!/usr/bin/env node
/**
 * Task Archive - Archive a completed task
 * Usage: node bin/task-archive.js <task-id>
 */

const TaskIndexManager = require('../lib/task-index-manager');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log('Task Archive - Archive a completed task\n');
    console.log('Usage: node task-archive.js <task-id>\n');
    console.log('Example:');
    console.log('  node task-archive.js 5');
    process.exit(0);
  }

  const taskId = parseInt(args[0], 10);
  
  if (isNaN(taskId)) {
    console.error('❌ Invalid task ID');
    process.exit(1);
  }

  const manager = new TaskIndexManager();
  
  try {
    await manager.init();
    
    // First check if task exists and is completed
    const task = manager.getTask(taskId);
    if (!task) {
      console.error(`❌ Task ${taskId} not found`);
      process.exit(1);
    }

    if (task.status !== 'completed') {
      console.error(`❌ Task ${taskId} is not completed (current status: ${task.status})`);
      console.log('   Use: node task-update.js ' + taskId + ' --status completed');
      process.exit(1);
    }
    
    const archived = await manager.archiveTask(taskId);

    console.log('✅ Task archived successfully!\n');
    console.log(`Task ID:        ${archived.number}`);
    console.log(`Name:           ${archived.name}`);
    console.log(`Archived at:    ${archived.archivedAt}`);
    console.log(`Archive path:   ${archived.archivePath}`);
    
  } catch (error) {
    console.error('❌ Failed to archive task:', error.message);
    process.exit(1);
  }
}

main();
