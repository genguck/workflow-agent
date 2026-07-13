import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator
from progress_tracker import ProgressTracker


def test_progress_tracker():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    manager = TemplateManager()
    manager.import_from_workflows(workflows)
    
    template = manager.get_template('用户增长')
    assert template is not None, "无法获取用户增长模板"
    
    project_info = {
        'project_name': '进度追踪测试项目',
        'assignee': '李四',
        'start_date': '2024-01-01'
    }
    
    generator = TaskGenerator()
    project_id = generator.generate_tasks(template, project_info)
    
    tracker = ProgressTracker()
    
    progress = tracker.get_project_progress(project_id)
    assert progress is not None, "无法获取项目进度"
    assert progress['total_tasks'] == 358, f"任务数量不正确: {progress['total_tasks']}"
    assert progress['completed_tasks'] == 0, "初始完成任务数应为0"
    assert progress['progress_percent'] == 0.0, "初始进度应为0%"
    print(f"初始进度: {progress['progress_percent']}%")
    
    project = generator.get_project_tasks(project_id)
    first_task_id = project['tasks'][0]['task_id']
    
    update_result = tracker.update_task_status(project_id, first_task_id, 'completed')
    assert update_result is True, "更新任务状态失败"
    
    progress = tracker.get_project_progress(project_id)
    assert progress['completed_tasks'] == 1, "完成任务数应为1"
    print(f"更新后进度: {progress['progress_percent']}%")
    
    update_result = tracker.update_task_status(project_id, first_task_id, 'in_progress')
    assert update_result is True, "更新任务状态失败"
    
    progress = tracker.get_project_progress(project_id)
    assert progress['in_progress_tasks'] == 1, "进行中任务数应为1"
    assert progress['completed_tasks'] == 0, "完成任务数应为0"
    print(f"再次更新后进度: {progress['progress_percent']}%")
    
    overdue_tasks = tracker.get_overdue_tasks(project_id)
    assert len(overdue_tasks) > 0, "应有逾期任务"
    print(f"逾期任务数: {len(overdue_tasks)}")
    
    reminders = tracker.generate_overdue_reminders(project_id)
    assert len(reminders) == len(overdue_tasks), "提醒数量应等于逾期任务数"
    print(f"生成的提醒数: {len(reminders)}")
    
    pending_reminders = tracker.get_pending_reminders()
    assert len(pending_reminders) >= len(reminders), "应有待处理提醒"
    
    if pending_reminders:
        mark_result = tracker.mark_reminder_read(pending_reminders[0]['reminder_id'])
        assert mark_result is True, "标记提醒为已读失败"
    
    report = tracker.generate_progress_report(project_id)
    assert '项目进度报告' in report, "报告内容不正确"
    assert '进度追踪测试项目' in report, "报告中应包含项目名称"
    print(f"\n进度报告:\n{report[:500]}...")
    
    print("\n所有测试通过！")
    
    return True


if __name__ == '__main__':
    success = test_progress_tracker()
    sys.exit(0 if success else 1)