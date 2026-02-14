#!/usr/bin/env node
/**
 * Task New - Create a new task with proper naming
 * Usage: node bin/task-new.js "Task Name" [options]
 */

const TaskIndexManager = require('../lib/task-index-manager');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log('Task New - Create a new task\n');
    console.log('Usage: node task-new.js "Task Name" [options]\n');
    console.log('Options:');
    console.log('  --priority, -p    Task priority (low|medium|high) [default: medium]');
    console.log('  --description, -d Task description');
    console.log('  --objectives, -o  Comma-separated objectives');
    console.log('\nExample:');
    console.log('  node task-new.js "Fix Bug" --priority high --description "Critical fix"');
    process.exit(0);
  }

  const taskName = args[0];
  
  // Parse options
  const options = {
    priority: 'medium',
    description: '',
    objectives: []
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    const nextArg = args[i + 1];

    if ((arg === '--priority' || arg === '-p') && nextArg) {
      options.priority = nextArg;
      i++;
    } else if ((arg === '--description' || arg === '-d') && nextArg) {
      options.description = nextArg;
      i++;
    } else if ((arg === '--objectives' || arg === '-o') && nextArg) {
      options.objectives = nextArg.split(',').map(o => o.trim());
      i++;
    }
  }

  const manager = new TaskIndexManager();
  
  try {
    await manager.init();
    
    const task = await manager.createTask({
      name: taskName,
      ...options
    });

    console.log('✅ Task created successfully!\n');
    console.log(`Task ID:    ${task.number}`);
    console.log(`Name:       ${task.name}`);
    console.log(`File:       ${task.filename}`);
    console.log(`Path:       ${task.filepath}`);
    console.log(`Priority:   ${task.priority}`);
    console.log(`Status:     ${task.status}`);
    
  } catch (error) {
    console.error('❌ Failed to create task:', error.message);
    process.exit(1);
  }
}

main();
