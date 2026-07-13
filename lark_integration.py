import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator


class LarkIntegration:
    def __init__(self, report_generator: ReportGenerator = None):
        self.report_generator = report_generator
    
    def generate_lark_document(self, project_id: str, report_type: str = 'full') -> str:
        if not self.report_generator:
            return "报告生成器未初始化"
        
        report = self.report_generator.generate_project_report(project_id, report_type)
        
        doc_content = f"""# 工作流执行报告

## 项目ID
{project_id}

## 报告类型
{report_type}

---

{report}

---

*报告由AI智能体工作流自动化系统自动生成*
"""
        
        return doc_content
    
    def generate_summary_lark_document(self) -> str:
        if not self.report_generator:
            return "报告生成器未初始化"
        
        report = self.report_generator.generate_summary_report()
        
        doc_content = f"""# 工作流汇总报告

---

{report}

---

*报告由AI智能体工作流自动化系统自动生成*
"""
        
        return doc_content
    
    def generate_task_list_document(self, project_id: str) -> str:
        if not self.report_generator:
            return "报告生成器未初始化"
        
        project = self.report_generator.task_generator.get_project_tasks(project_id)
        if not project:
            return f"项目 {project_id} 不存在"
        
        doc_content = f"""# 项目任务清单

## 项目信息
- 项目名称: {project['project_name']}
- 项目ID: {project_id}
- 工作流模板: {project['template_title']}
- 负责人: {project.get('assignee', '未指定')}
- 创建时间: {project.get('created_at', '未知')}

## 任务列表

"""
        
        step_tasks = {}
        for task in project['tasks']:
            step_num = task.get('step_number', 0)
            if step_num not in step_tasks:
                step_tasks[step_num] = []
            step_tasks[step_num].append(task)
        
        for step_num in sorted(step_tasks.keys()):
            doc_content += f"### 步骤{step_num}\n\n"
            for task in step_tasks[step_num]:
                status_icon = "✅" if task['status'] == 'completed' else "🔄" if task['status'] == 'in_progress' else "⏳"
                doc_content += f"- {status_icon} {task['task_name']}\n"
                if task.get('estimated_hours'):
                    doc_content += f"  - 预估耗时: {task['estimated_hours']}小时\n"
                if task.get('dependencies'):
                    doc_content += f"  - 依赖任务: {', '.join(task['dependencies'])}\n"
                doc_content += "\n"
        
        doc_content += """---

*任务清单由AI智能体工作流自动化系统自动生成*
"""
        
        return doc_content
    
    def generate_progress_document(self, project_id: str) -> str:
        if not self.report_generator:
            return "报告生成器未初始化"
        
        progress = self.report_generator.progress_tracker.get_project_progress(project_id)
        if not progress:
            return f"项目 {project_id} 不存在"
        
        doc_content = f"""# 项目进度报告

## 项目信息
- 项目名称: {progress['project_name']}
- 项目ID: {project_id}

## 整体进度
- **完成率**: {progress['progress_percent']}%
- **总任务数**: {progress['total_tasks']}
- **已完成**: {progress['completed_tasks']}
- **进行中**: {progress['in_progress_tasks']}
- **待办**: {progress['pending_tasks']}
- **逾期**: {progress['overdue_tasks']}

## 各步骤进度

"""
        
        for step_num, step_info in sorted(progress['step_progress'].items()):
            bar = "█" * int(step_info['percent'] / 10) + "░" * (10 - int(step_info['percent'] / 10))
            doc_content += f"### 步骤{step_num}\n"
            doc_content += f"- 进度: {step_info['percent']}% [{bar}]\n"
            doc_content += f"- 任务完成: {step_info['completed']}/{step_info['total']}\n\n"
        
        if progress['overdue_tasks'] > 0:
            doc_content += f"""## ⚠️ 逾期提醒
共有 {progress['overdue_tasks']} 个任务逾期，请及时处理！
"""
        
        doc_content += """---

*进度报告由AI智能体工作流自动化系统自动生成*
"""
        
        return doc_content