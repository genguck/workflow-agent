import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class ProgressTracker:
    def __init__(self):
        self.tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'tasks.json')
        self.reminders_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'reminders.json')
        self.tasks = self._load_tasks()
        self.reminders = self._load_reminders()

    def _load_tasks(self) -> Dict[str, Any]:
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_reminders(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.reminders_file):
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        data_dir = os.path.dirname(self.tasks_file)
        os.makedirs(data_dir, exist_ok=True)
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def _save_reminders(self):
        data_dir = os.path.dirname(self.reminders_file)
        os.makedirs(data_dir, exist_ok=True)
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, ensure_ascii=False, indent=2)

    def update_task_status(self, project_id: str, task_id: str, status: str) -> bool:
        if project_id not in self.tasks:
            return False
        
        project = self.tasks[project_id]
        for task in project['tasks']:
            if task['task_id'] == task_id:
                task['status'] = status
                task['updated_at'] = datetime.now().isoformat()
                if status == 'completed':
                    task['completed_at'] = datetime.now().isoformat()
                self._save_tasks()
                return True
        return False

    def get_project_progress(self, project_id: str) -> Optional[Dict[str, Any]]:
        if project_id not in self.tasks:
            return None
        
        project = self.tasks[project_id]
        total_tasks = len(project['tasks'])
        completed_tasks = sum(1 for t in project['tasks'] if t['status'] == 'completed')
        in_progress_tasks = sum(1 for t in project['tasks'] if t['status'] == 'in_progress')
        pending_tasks = sum(1 for t in project['tasks'] if t['status'] == 'pending')
        overdue_tasks = self.get_overdue_tasks(project_id)
        
        progress_percent = 0
        if total_tasks > 0:
            progress_percent = round((completed_tasks / total_tasks) * 100, 1)
        
        step_progress = {}
        for step_num in sorted(set(t['step_number'] for t in project['tasks'])):
            step_tasks = [t for t in project['tasks'] if t['step_number'] == step_num]
            step_completed = sum(1 for t in step_tasks if t['status'] == 'completed')
            step_progress[step_num] = {
                'total': len(step_tasks),
                'completed': step_completed,
                'percent': round((step_completed / len(step_tasks)) * 100, 1) if step_tasks else 0
            }
        
        return {
            'project_id': project_id,
            'project_name': project['project_name'],
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': len(overdue_tasks),
            'progress_percent': progress_percent,
            'step_progress': step_progress
        }

    def get_overdue_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        if project_id not in self.tasks:
            return []
        
        today = datetime.now().strftime('%Y-%m-%d')
        overdue = []
        
        for task in self.tasks[project_id]['tasks']:
            if task['status'] != 'completed' and task['due_date'] < today:
                overdue.append(task)
        
        return overdue

    def generate_overdue_reminders(self, project_id: str) -> List[Dict[str, Any]]:
        overdue_tasks = self.get_overdue_tasks(project_id)
        reminders = []
        
        for task in overdue_tasks:
            reminder = {
                'reminder_id': f"reminder-{datetime.now().strftime('%Y%m%d%H%M%S')}-{task['task_id']}",
                'project_id': project_id,
                'task_id': task['task_id'],
                'task_name': task['task_name'],
                'step_number': task['step_number'],
                'step_title': task['step_title'],
                'due_date': task['due_date'],
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'message': f"【逾期提醒】任务 '{task['task_name']}' 已逾期，截止日期: {task['due_date']}"
            }
            reminders.append(reminder)
        
        self.reminders.extend(reminders)
        self._save_reminders()
        
        return reminders

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        return [r for r in self.reminders if r['status'] == 'pending']

    def mark_reminder_read(self, reminder_id: str) -> bool:
        for reminder in self.reminders:
            if reminder['reminder_id'] == reminder_id:
                reminder['status'] = 'read'
                reminder['read_at'] = datetime.now().isoformat()
                self._save_reminders()
                return True
        return False

    def generate_progress_report(self, project_id: str) -> str:
        progress = self.get_project_progress(project_id)
        if not progress:
            return f"项目 {project_id} 不存在"
        
        report = f"{'='*60}\n"
        report += f"项目进度报告\n"
        report += f"{'='*60}\n"
        report += f"项目名称: {progress['project_name']}\n"
        report += f"项目ID: {project_id}\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*60}\n\n"
        report += f"整体进度: {progress['progress_percent']}%\n"
        report += f"总任务数: {progress['total_tasks']}\n"
        report += f"已完成: {progress['completed_tasks']}\n"
        report += f"进行中: {progress['in_progress_tasks']}\n"
        report += f"待办: {progress['pending_tasks']}\n"
        report += f"逾期: {progress['overdue_tasks']}\n\n"
        report += f"各步骤进度:\n"
        
        for step_num, step_info in progress['step_progress'].items():
            report += f"  步骤{step_num}: {step_info['completed']}/{step_info['total']} ({step_info['percent']}%)\n"
        
        overdue_tasks = self.get_overdue_tasks(project_id)
        if overdue_tasks:
            report += f"\n逾期任务列表:\n"
            for task in overdue_tasks:
                report += f"  - {task['task_name']} (步骤{task['step_number']}, 截止: {task['due_date']})\n"
        
        return report