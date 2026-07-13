import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class TaskGenerator:
    def __init__(self):
        self.tasks_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'tasks.json')
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_tasks(self):
        data_dir = os.path.dirname(self.tasks_file)
        os.makedirs(data_dir, exist_ok=True)
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def generate_tasks(self, template: Dict[str, Any], project_info: Dict[str, Any]) -> str:
        project_id = project_info.get('project_id') or self._generate_project_id(project_info['project_name'])
        
        start_date_str = project_info.get('start_date') or datetime.now().strftime('%Y-%m-%d')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        
        tasks = []
        task_id_counter = 1
        
        for step in template['steps']:
            step_tasks = self._generate_step_tasks(step, project_id, start_date, task_id_counter)
            tasks.extend(step_tasks)
            task_id_counter += len(step_tasks)
            
            estimated_days = self._parse_time_estimate(step.get('time_estimate', ''))
            start_date += timedelta(days=estimated_days)

        project_tasks = {
            'project_id': project_id,
            'project_name': project_info['project_name'],
            'template_id': template['id'],
            'template_title': template['title'],
            'assignee': project_info.get('assignee', ''),
            'created_at': datetime.now().isoformat(),
            'start_date': project_info.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            'tasks': tasks
        }

        self.tasks[project_id] = project_tasks
        self._save_tasks()
        
        return project_id

    def _generate_step_tasks(self, step: Dict[str, Any], project_id: str, start_date: datetime, base_id: int) -> List[Dict[str, Any]]:
        tasks = []
        
        for i, objective in enumerate(step.get('objectives', []), 1):
            task = {
                'task_id': f"{project_id}-{base_id + i - 1}",
                'step_number': step['step_number'],
                'step_title': step['title'],
                'task_type': 'objective',
                'task_name': objective,
                'description': f"步骤{step['step_number']}目标: {objective}",
                'status': 'pending',
                'priority': 'high',
                'due_date': (start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                'assignee': '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tasks.append(task)
        
        for i, operation in enumerate(step.get('operations', []), 1):
            task = {
                'task_id': f"{project_id}-{base_id + len(step.get('objectives', [])) + i - 1}",
                'step_number': step['step_number'],
                'step_title': step['title'],
                'task_type': 'operation',
                'task_name': operation,
                'description': f"步骤{step['step_number']}操作: {operation}",
                'status': 'pending',
                'priority': 'medium',
                'due_date': (start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'assignee': '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tasks.append(task)
        
        for i, deliverable in enumerate(step.get('deliverables', []), 1):
            task = {
                'task_id': f"{project_id}-{base_id + len(step.get('objectives', [])) + len(step.get('operations', [])) + i - 1}",
                'step_number': step['step_number'],
                'step_title': step['title'],
                'task_type': 'deliverable',
                'task_name': deliverable,
                'description': f"步骤{step['step_number']}产出物: {deliverable}",
                'status': 'pending',
                'priority': 'high',
                'due_date': (start_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                'assignee': '',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            tasks.append(task)
        
        return tasks

    def _generate_project_id(self, project_name: str) -> str:
        normalized = project_name.strip().replace(' ', '-').replace('_', '-')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{normalized}-{timestamp}"

    def _parse_time_estimate(self, time_estimate: str) -> int:
        import re
        match = re.search(r'(\d+)', time_estimate)
        if match:
            return int(match.group(1))
        return 3

    def get_project_tasks(self, project_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(project_id)

    def list_projects(self) -> List[Dict[str, Any]]:
        return list(self.tasks.values())

    def export_to_excel(self, project_id: str, output_path: str = None) -> str:
        project = self.tasks.get(project_id)
        if not project:
            raise ValueError(f"项目 {project_id} 不存在")
        
        if output_path is None:
            output_path = os.path.join(os.path.dirname(self.tasks_file), f"{project_id}.xlsx")
        
        try:
            import pandas as pd
            rows = []
            for task in project['tasks']:
                rows.append({
                    '任务ID': task['task_id'],
                    '步骤': task['step_number'],
                    '步骤名称': task['step_title'],
                    '任务类型': task['task_type'],
                    '任务名称': task['task_name'],
                    '描述': task['description'],
                    '状态': task['status'],
                    '优先级': task['priority'],
                    '截止日期': task['due_date'],
                    '负责人': task['assignee']
                })
            
            df = pd.DataFrame(rows)
            df.to_excel(output_path, index=False, encoding='utf-8')
            return output_path
        except ImportError:
            return self.export_to_csv(project_id, output_path.replace('.xlsx', '.csv'))

    def export_to_csv(self, project_id: str, output_path: str = None) -> str:
        project = self.tasks.get(project_id)
        if not project:
            raise ValueError(f"项目 {project_id} 不存在")
        
        if output_path is None:
            output_path = os.path.join(os.path.dirname(self.tasks_file), f"{project_id}.csv")
        
        import csv
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['任务ID', '步骤', '步骤名称', '任务类型', '任务名称', '描述', '状态', '优先级', '截止日期', '负责人'])
            for task in project['tasks']:
                writer.writerow([
                    task['task_id'],
                    task['step_number'],
                    task['step_title'],
                    task['task_type'],
                    task['task_name'],
                    task['description'],
                    task['status'],
                    task['priority'],
                    task['due_date'],
                    task['assignee']
                ])
        return output_path