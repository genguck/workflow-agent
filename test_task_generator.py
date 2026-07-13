import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator


def test_task_generator():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    manager = TemplateManager()
    manager.import_from_workflows(workflows)
    
    template = manager.get_template('用户增长')
    assert template is not None, "无法获取用户增长模板"
    
    project_info = {
        'project_name': '2024年Q4用户增长项目',
        'assignee': '张三',
        'start_date': '2024-10-01'
    }
    
    generator = TaskGenerator()
    project_id = generator.generate_tasks(template, project_info)
    
    print(f"项目ID: {project_id}")
    
    project_tasks = generator.get_project_tasks(project_id)
    assert project_tasks is not None, "无法获取项目任务"
    assert project_tasks['project_name'] == '2024年Q4用户增长项目', "项目名称不匹配"
    assert project_tasks['assignee'] == '张三', "负责人不匹配"
    assert project_tasks['template_id'] == '用户增长', "模板ID不匹配"
    
    total_tasks = len(project_tasks['tasks'])
    print(f"生成的任务总数: {total_tasks}")
    
    step_task_counts = {}
    for task in project_tasks['tasks']:
        step_num = task['step_number']
        if step_num not in step_task_counts:
            step_task_counts[step_num] = {'objective': 0, 'operation': 0, 'deliverable': 0}
        step_task_counts[step_num][task['task_type']] += 1
    
    print("\n各步骤任务分布:")
    for step_num in sorted(step_task_counts.keys()):
        counts = step_task_counts[step_num]
        print(f"  步骤{step_num}: 目标({counts['objective']}) + 操作({counts['operation']}) + 产出物({counts['deliverable']})")
    
    assert total_tasks > 0, "任务数量应为正数"
    
    csv_path = generator.export_to_csv(project_id)
    assert os.path.exists(csv_path), f"CSV文件未生成: {csv_path}"
    print(f"\nCSV导出成功: {csv_path}")
    
    print("\n所有测试通过！")
    
    return True


if __name__ == '__main__':
    success = test_task_generator()
    sys.exit(0 if success else 1)