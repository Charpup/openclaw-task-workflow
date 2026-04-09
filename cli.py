#!/usr/bin/env python3
"""
Task Workflow V3 - CLI Interface
命令行接口
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta

# 添加 scripts 目录到路径
scripts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, scripts_path)

from task_persistence import (
    TaskPersistenceManager, TaskRecord, TaskStatus,
    CronConfigManager, get_today_file_path, ensure_daily_file_exists
)
from task_scheduler import TaskScheduler, DynamicTaskManager, TaskNode, init_daily_workflow, setup_cron_jobs


def cmd_init_daily(args):
    """初始化每日任务文件"""
    filepath = init_daily_workflow()
    print(f"✅ Created: {filepath}")
    
    # 检查并显示迁移的任务
    manager = TaskPersistenceManager()
    tasks = manager.get_current_tasks()
    migrated = [t for t in tasks if "migrated" in t.notes.lower()]
    
    if migrated:
        print(f"\n📦 Migrated {len(migrated)} incomplete tasks from previous day:")
        for task in migrated:
            print(f"  - {task.name} ({task.id})")


def cmd_list_tasks(args):
    """列出当前任务"""
    manager = TaskPersistenceManager()
    manager.initialize_daily_file()
    tasks = manager.get_current_tasks()
    
    if not tasks:
        print("No tasks for today.")
        return
    
    print(f"\n📋 Tasks for {datetime.now().strftime('%Y-%m-%d')}:\n")
    print(f"{'ID':<15} {'Name':<25} {'Status':<12} {'Complexity':<10}")
    print("-" * 65)
    
    status_icons = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "migrated": "📦"
    }
    
    for task in tasks:
        icon = status_icons.get(task.status, "⏳")
        print(f"{task.id:<15} {task.name:<25} {icon} {task.status:<10} {task.complexity_score:.1f}")
    
    # 统计
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    print(f"\n📊 Progress: {completed}/{total} completed ({completed/total*100:.1f}%)")


def cmd_add_task(args):
    """添加新任务"""
    manager = TaskPersistenceManager()
    manager.initialize_daily_file()
    
    task = TaskRecord(
        id=args.id,
        name=args.name,
        description=args.description or "",
        depends_on=args.depends_on.split(",") if args.depends_on else [],
        estimated_time=args.time,
        tool_calls_estimate=args.tools,
        decision_points=args.decisions
    )
    
    manager.add_task(task)
    print(f"✅ Task added: {args.name} ({args.id})")


def cmd_update_status(args):
    """更新任务状态"""
    manager = TaskPersistenceManager()
    manager.initialize_daily_file()
    
    status_map = {
        "pending": TaskStatus.PENDING,
        "running": TaskStatus.RUNNING,
        "completed": TaskStatus.COMPLETED,
        "failed": TaskStatus.FAILED
    }
    
    status = status_map.get(args.status.lower())
    if not status:
        print(f"❌ Invalid status: {args.status}")
        print(f"Valid statuses: {', '.join(status_map.keys())}")
        return
    
    manager.update_task_status(args.id, status, args.notes)
    print(f"✅ Updated {args.id} to {args.status}")


def cmd_log_progress(args):
    """记录进度事件"""
    manager = TaskPersistenceManager()
    manager.initialize_daily_file()
    manager.log_progress(args.event, args.details)
    print(f"✅ Logged: {args.event}")


def cmd_setup_cron(args):
    """设置 cron 配置"""
    payload = setup_cron_jobs()
    
    # 输出 OpenClaw cron API 格式
    print("\n📝 OpenClaw Cron API Payload:")
    print(json.dumps(payload, indent=2))
    
    # 保存到文件供参考
    cron_config_path = os.path.expanduser("~/.openclaw/workspace/skills/task-workflow-v3/config/cron-api-payload.json")
    os.makedirs(os.path.dirname(cron_config_path), exist_ok=True)
    with open(cron_config_path, 'w') as f:
        json.dump(payload, f, indent=2)
    print(f"\n💾 Saved to: {cron_config_path}")


def cmd_cleanup(args):
    """清理旧文件"""
    from pathlib import Path
    
    backlog_dir = Path("/root/.openclaw/workspace/task_backlog")
    cutoff = datetime.now() - timedelta(days=args.days)
    
    deleted = 0
    for file in backlog_dir.glob("*.md"):
        # 从文件名提取日期
        try:
            date_str = file.stem.split("-")[-3:]
            file_date = datetime.strptime("-".join(date_str), "%Y-%m-%d")
            
            if file_date < cutoff:
                file.unlink()
                deleted += 1
                print(f"🗑️  Deleted: {file.name}")
        except (ValueError, IndexError):
            continue
    
    print(f"\n✅ Cleaned up {deleted} old files")


def cmd_schedule_demo(args):
    """调度演示"""
    print("🎯 Task Scheduler Demo\n")
    
    tasks = [
        TaskNode(
            id="research-a",
            name="Research Option A",
            estimated_time="medium",
            tool_calls_estimate=6
        ),
        TaskNode(
            id="research-b",
            name="Research Option B",
            estimated_time="short",
            tool_calls_estimate=4
        ),
        TaskNode(
            id="research-c",
            name="Research Option C",
            estimated_time="long",
            tool_calls_estimate=10
        ),
        TaskNode(
            id="summary",
            name="Summary Analysis",
            depends_on=["research-a", "research-b", "research-c"],
            estimated_time="medium",
            decision_points=2
        )
    ]
    
    scheduler = TaskScheduler(max_batch_size=10, enable_persistence=True)
    batches = scheduler.schedule_tasks(tasks)
    
    print(f"Scheduled {len(tasks)} tasks into {len(batches)} batches:\n")
    
    for i, batch in enumerate(batches, 1):
        print(f"Batch {i}:")
        for task in batch:
            deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else ""
            print(f"  • {task.name} [complexity: {task.complexity_score:.1f}]{deps}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Task Workflow V3 - Persistent Task Management",
        prog="task-workflow-v3"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init-daily
    init_parser = subparsers.add_parser("init-daily", help="Initialize daily workflow file")
    init_parser.set_defaults(func=cmd_init_daily)
    
    # list
    list_parser = subparsers.add_parser("list", help="List today's tasks")
    list_parser.set_defaults(func=cmd_list_tasks)
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("id", help="Task ID")
    add_parser.add_argument("name", help="Task name")
    add_parser.add_argument("-d", "--description", help="Task description")
    add_parser.add_argument("--depends-on", help="Comma-separated dependency IDs")
    add_parser.add_argument("--time", choices=["short", "medium", "long"], 
                           default="medium", help="Estimated time")
    add_parser.add_argument("--tools", type=int, default=5, 
                           help="Estimated tool calls")
    add_parser.add_argument("--decisions", type=int, default=0,
                           help="Number of decision points")
    add_parser.set_defaults(func=cmd_add_task)
    
    # update
    update_parser = subparsers.add_parser("update", help="Update task status")
    update_parser.add_argument("id", help="Task ID")
    update_parser.add_argument("status", 
                              choices=["pending", "running", "completed", "failed"],
                              help="New status")
    update_parser.add_argument("--notes", default="", help="Additional notes")
    update_parser.set_defaults(func=cmd_update_status)
    
    # log
    log_parser = subparsers.add_parser("log", help="Log progress event")
    log_parser.add_argument("event", help="Event name")
    log_parser.add_argument("--details", default="", help="Event details")
    log_parser.set_defaults(func=cmd_log_progress)
    
    # setup-cron
    cron_parser = subparsers.add_parser("setup-cron", help="Setup cron jobs")
    cron_parser.set_defaults(func=cmd_setup_cron)
    
    # cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup old files")
    cleanup_parser.add_argument("--days", type=int, default=30,
                               help="Delete files older than N days")
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    # demo
    demo_parser = subparsers.add_parser("demo", help="Run scheduling demo")
    demo_parser.set_defaults(func=cmd_schedule_demo)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
