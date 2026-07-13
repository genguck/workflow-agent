import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class ReportGenerator:
    def __init__(self, template_manager, task_generator, progress_tracker):
        self.template_manager = template_manager
        self.task_generator = task_generator
        self.progress_tracker = progress_tracker
        self.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_project_report(self, project_id: str, report_type: str = 'full') -> str:
        project = self.task_generator.get_project_tasks(project_id)
        if not project:
            return f"项目 {project_id} 不存在"
        
        progress = self.progress_tracker.get_project_progress(project_id)
        template = self.template_manager.get_template(project['template_id'])
        
        report = self._generate_report_header(project, progress)
        
        if report_type == 'full' or report_type == 'progress':
            report += self._generate_progress_section(progress)
        
        if report_type == 'full' or report_type == 'tasks':
            report += self._generate_tasks_section(project)
        
        if report_type == 'full' or report_type == 'deliverables':
            report += self._generate_deliverables_section(project)
        
        if report_type == 'full' or report_type == 'issues':
            report += self._generate_issues_section(project, progress)
        
        if report_type == 'full':
            report += self._generate_summary_section(project, progress, template)
        
        return report

    def _generate_report_header(self, project: Dict[str, Any], progress: Dict[str, Any]) -> str:
        header = f"{'='*70}\n"
        header += f"工作流执行报告\n"
        header += f"{'='*70}\n"
        header += f"项目名称: {project['project_name']}\n"
        header += f"项目ID: {project['project_id']}\n"
        header += f"工作流模板: {project['template_title']}\n"
        header += f"负责人: {project.get('assignee', '未指定')}\n"
        header += f"开始日期: {project['start_date']}\n"
        header += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"{'='*70}\n\n"
        return header

    def _generate_progress_section(self, progress: Dict[str, Any]) -> str:
        section = f"【项目进度】\n"
        section += f"{'─'*50}\n"
        section += f"整体进度: {progress['progress_percent']}%\n"
        section += f"总任务数: {progress['total_tasks']}\n"
        section += f"  ├─ 已完成: {progress['completed_tasks']}\n"
        section += f"  ├─ 进行中: {progress['in_progress_tasks']}\n"
        section += f"  ├─ 待办: {progress['pending_tasks']}\n"
        section += f"  └─ 逾期: {progress['overdue_tasks']}\n\n"
        
        section += f"各步骤进度:\n"
        for step_num, step_info in progress['step_progress'].items():
            bar = self._generate_progress_bar(step_info['percent'])
            section += f"  步骤{step_num}: {bar} {step_info['percent']}% ({step_info['completed']}/{step_info['total']})\n"
        section += "\n"
        
        return section

    def _generate_progress_bar(self, percent: float) -> str:
        bar_length = 20
        filled = int(bar_length * (percent / 100))
        return f"[{'█'*filled}{'░'*(bar_length-filled)}]"

    def _generate_tasks_section(self, project: Dict[str, Any]) -> str:
        section = f"【任务明细】\n"
        section += f"{'─'*50}\n"
        
        status_counts = {'pending': 0, 'in_progress': 0, 'completed': 0}
        for task in project['tasks']:
            status_counts[task['status']] += 1
        
        section += f"任务状态分布:\n"
        section += f"  ├─ 待办: {status_counts['pending']}\n"
        section += f"  ├─ 进行中: {status_counts['in_progress']}\n"
        section += f"  └─ 已完成: {status_counts['completed']}\n\n"
        
        section += f"按步骤分组:\n"
        step_tasks = {}
        for task in project['tasks']:
            step_num = task['step_number']
            if step_num not in step_tasks:
                step_tasks[step_num] = []
            step_tasks[step_num].append(task)
        
        for step_num in sorted(step_tasks.keys()):
            tasks = step_tasks[step_num]
            step_title = tasks[0]['step_title'] if tasks else ''
            section += f"\n  步骤{step_num}: {step_title}\n"
            for task in tasks[:5]:
                status_icon = '✓' if task['status'] == 'completed' else '○' if task['status'] == 'in_progress' else '□'
                section += f"    {status_icon} {task['task_name']} ({task['task_type']})\n"
            if len(tasks) > 5:
                section += f"    ... 还有 {len(tasks) - 5} 个任务\n"
        
        section += "\n"
        return section

    def _generate_deliverables_section(self, project: Dict[str, Any]) -> str:
        deliverables = [t for t in project['tasks'] if t['task_type'] == 'deliverable']
        
        section = f"【产出物清单】\n"
        section += f"{'─'*50}\n"
        section += f"产出物总数: {len(deliverables)}\n\n"
        
        completed = [d for d in deliverables if d['status'] == 'completed']
        pending = [d for d in deliverables if d['status'] != 'completed']
        
        if completed:
            section += f"已完成:\n"
            for d in completed[:10]:
                section += f"  ✓ {d['task_name']}\n"
            if len(completed) > 10:
                section += f"  ... 还有 {len(completed) - 10} 个\n"
        
        if pending:
            section += f"\n待交付:\n"
            for d in pending[:10]:
                overdue_mark = ' ⚠️逾期' if d['due_date'] < datetime.now().strftime('%Y-%m-%d') else ''
                section += f"  □ {d['task_name']} (截止: {d['due_date']}){overdue_mark}\n"
            if len(pending) > 10:
                section += f"  ... 还有 {len(pending) - 10} 个\n"
        
        section += "\n"
        return section

    def _generate_issues_section(self, project: Dict[str, Any], progress: Dict[str, Any]) -> str:
        overdue_tasks = self.progress_tracker.get_overdue_tasks(project['project_id'])
        
        section = f"【问题与风险】\n"
        section += f"{'─'*50}\n"
        
        if progress['overdue_tasks'] > 0:
            section += f"⚠️ 逾期任务: {progress['overdue_tasks']} 个\n"
            section += f"\n逾期任务列表:\n"
            for task in overdue_tasks[:10]:
                section += f"  - {task['task_name']}\n"
                section += f"    步骤: {task['step_number']} - {task['step_title']}\n"
                section += f"    截止日期: {task['due_date']}\n"
            if len(overdue_tasks) > 10:
                section += f"  ... 还有 {len(overdue_tasks) - 10} 个逾期任务\n"
        else:
            section += f"✓ 暂无逾期任务\n"
        
        completion_rate = progress['progress_percent']
        if completion_rate < 30:
            section += f"\n⚠️ 风险提示: 项目进度落后，建议加快推进\n"
        elif completion_rate < 60:
            section += f"\n提示: 项目进度正常，请继续保持\n"
        else:
            section += f"\n✓ 项目进度良好\n"
        
        section += "\n"
        return section

    def _generate_summary_section(self, project: Dict[str, Any], progress: Dict[str, Any], template: Optional[Dict[str, Any]]) -> str:
        section = f"【总结与建议】\n"
        section += f"{'─'*50}\n"
        
        section += f"项目状态评估:\n"
        if progress['progress_percent'] >= 80:
            section += f"  ✓ 项目接近完成\n"
        elif progress['progress_percent'] >= 50:
            section += f"  ○ 项目进行中\n"
        else:
            section += f"  □ 项目启动阶段\n"
        
        if progress['overdue_tasks'] > 0:
            section += f"\n建议:\n"
            section += f"  1. 优先处理逾期任务\n"
            section += f"  2. 评估资源分配是否合理\n"
            section += f"  3. 考虑调整后续任务时间计划\n"
        
        if template:
            section += f"\n工作流模板信息:\n"
            section += f"  模板名称: {template['title']}\n"
            section += f"  版本: {template['version']}\n"
            section += f"  适用范围: {template.get('scope', '未指定')}\n"
        
        section += f"\n{'='*70}\n"
        section += f"报告结束\n"
        section += f"{'='*70}\n"
        
        return section

    def export_report(self, project_id: str, output_path: str = None, report_type: str = 'full') -> str:
        report = self.generate_project_report(project_id, report_type)
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.reports_dir, f"{project_id}_{report_type}_{timestamp}.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path

    def generate_summary_report(self, project_ids: List[str] = None) -> str:
        if project_ids is None:
            projects = self.task_generator.list_projects()
            project_ids = [p['project_id'] for p in projects]
        
        report = f"{'='*70}\n"
        report += f"项目汇总报告\n"
        report += f"{'='*70}\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*70}\n\n"
        report += f"总项目数: {len(project_ids)}\n\n"
        
        for project_id in project_ids:
            project = self.task_generator.get_project_tasks(project_id)
            if project:
                progress = self.progress_tracker.get_project_progress(project_id)
                report += f"【{project['project_name']}】\n"
                report += f"  项目ID: {project_id}\n"
                report += f"  模板: {project['template_title']}\n"
                report += f"  负责人: {project.get('assignee', '未指定')}\n"
                report += f"  进度: {progress['progress_percent']}%\n"
                report += f"  任务: {progress['completed_tasks']}/{progress['total_tasks']} 完成\n"
                report += f"  逾期: {progress['overdue_tasks']} 个\n"
                report += f"\n"
        
        report += f"{'='*70}\n"
        return report