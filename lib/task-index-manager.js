/**
 * Task Index Manager - Manages active task list and ID assignment
 * Part of task-workflow archive system
 */

const fs = require('fs').promises;
const path = require('path');

class TaskIndexManager {
  constructor(options = {}) {
    this.config = {
      activeDir: options.activeDir || './01_active/tasks',
      archiveDir: options.archiveDir || './02_archive',
      indexFile: options.indexFile || './01_active/tasks/index.json',
      ...options
    };
    this.index = null;
  }

  /**
   * Initialize the index manager
   */
  async init() {
    await this.ensureDirectories();
    await this.loadIndex();
  }

  /**
   * Ensure directory structure exists
   */
  async ensureDirectories() {
    const dirs = [
      this.config.activeDir,
      path.dirname(this.config.indexFile)
    ];

    for (const dir of dirs) {
      await fs.mkdir(dir, { recursive: true });
    }
  }

  /**
   * Load or create index
   */
  async loadIndex() {
    try {
      const content = await fs.readFile(this.config.indexFile, 'utf-8');
      this.index = JSON.parse(content);
    } catch {
      // Create new index
      this.index = {
        version: '1.0.0',
        lastTaskId: 0,
        activeTasks: [],
        archivedTasks: [],
        updatedAt: new Date().toISOString()
      };
      await this.saveIndex();
    }
  }

  /**
   * Save index to file
   */
  async saveIndex() {
    this.index.updatedAt = new Date().toISOString();
    await fs.writeFile(
      this.config.indexFile,
      JSON.stringify(this.index, null, 2)
    );
  }

  /**
   * Create a new task
   */
  async createTask(taskData) {
    const taskId = this.index.lastTaskId + 1;
    this.index.lastTaskId = taskId;

    const taskNumber = String(taskId).padStart(3, '0');
    const taskName = taskData.name.toLowerCase().replace(/\s+/g, '_');
    const filename = `task_${taskNumber}_${taskName}.md`;

    const task = {
      id: taskId,
      number: taskNumber,
      name: taskData.name,
      filename,
      description: taskData.description || '',
      status: 'pending',
      priority: taskData.priority || 'medium',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      filepath: path.join(this.config.activeDir, filename)
    };

    // Add to active tasks
    this.index.activeTasks.push(task);
    await this.saveIndex();

    // Create task file from template
    await this.createTaskFile(task, taskData);

    return task;
  }

  /**
   * Create task file from template
   */
  async createTaskFile(task, taskData) {
    const template = `# Task ${task.number}: ${task.name}

**Created:** ${new Date().toISOString().split('T')[0]}  
**Status:** ${task.status}  
**Priority:** ${task.priority}  
**Task ID:** ${task.number}

---

## Description

${taskData.description || 'No description provided.'}

## Objectives

${taskData.objectives ? taskData.objectives.map(o => `- [ ] ${o}`).join('\n') : '- [ ] Define objectives'}

## Progress

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| 1 - Planning | ⏳ | - | - |
| 2 - Execution | ⏳ | - | - |
| 3 - Validation | ⏳ | - | - |

## Notes

${taskData.notes || ''}

---

*Created by task-workflow 🜁*
`;

    await fs.writeFile(task.filepath, template);
  }

  /**
   * Get all active tasks
   */
  getActiveTasks() {
    return this.index.activeTasks.filter(t => t.status !== 'completed');
  }

  /**
   * Get a specific task by ID
   */
  getTask(taskId) {
    return this.index.activeTasks.find(t => t.id === taskId);
  }

  /**
   * Update task status
   */
  async updateTaskStatus(taskId, status) {
    const task = this.getTask(taskId);
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    task.status = status;
    task.updatedAt = new Date().toISOString();

    await this.saveIndex();
    return task;
  }

  /**
   * Archive a completed task
   */
  async archiveTask(taskId) {
    const taskIndex = this.index.activeTasks.findIndex(t => t.id === taskId);
    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`);
    }

    const task = this.index.activeTasks[taskIndex];

    if (task.status !== 'completed') {
      throw new Error(`Task ${taskId} is not completed (status: ${task.status})`);
    }

    // Determine archive location
    const archiveDate = new Date();
    const yearMonth = `${archiveDate.getFullYear()}-${String(archiveDate.getMonth() + 1).padStart(2, '0')}`;
    const archiveDir = path.join(this.config.archiveDir, yearMonth, 'tasks');
    await fs.mkdir(archiveDir, { recursive: true });

    // Update filename for archive
    const archivedFilename = task.filename.replace('.md', '_completed.md');
    const archivePath = path.join(archiveDir, archivedFilename);

    // Move file
    await fs.rename(task.filepath, archivePath);

    // Update task record
    task.archivedAt = new Date().toISOString();
    task.originalPath = task.filepath;
    task.archivePath = archivePath;

    // Move from active to archived
    this.index.activeTasks.splice(taskIndex, 1);
    this.index.archivedTasks.push(task);

    await this.saveIndex();

    return {
      ...task,
      archiveLocation: archivePath
    };
  }

  /**
   * Generate task status report
   */
  async generateReport() {
    const active = this.getActiveTasks();
    const pending = active.filter(t => t.status === 'pending');
    const inProgress = active.filter(t => t.status === 'in_progress');

    return {
      summary: {
        totalActive: active.length,
        pending: pending.length,
        inProgress: inProgress.length,
        completed: this.index.archivedTasks.length
      },
      pendingTasks: pending,
      inProgressTasks: inProgress,
      recentArchived: this.index.archivedTasks.slice(-5)
    };
  }
}

module.exports = TaskIndexManager;
