import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator
from progress_tracker import ProgressTracker
from report_generator import ReportGenerator


def test_report_generator():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    manager = TemplateManager()
    manager.import_from_workflows(workflows)
    
    template = manager.get_template('用户增长')
    assert template is not None, "无法获取用户增长模板"
    
    project_info = {
        'project_name': '报告测试项目',
        'assignee': '王五',
        'start_date': '2024-01-01'
    }
    
    generator = TaskGenerator()
    project_id = generator.generate_tasks(template, project_info)
    
    tracker = ProgressTracker()
    
    report_generator = ReportGenerator(manager, generator, tracker)
    
    report = report_generator.generate_project_report(project_id, 'full')
    assert '工作流执行报告' in report, "报告标题不正确"
    assert '报告测试项目' in report, "报告中应包含项目名称"
    assert '项目进度' in report, "报告中应包含进度部分"
    assert '任务明细' in report, "报告中应包含任务部分"
    assert '产出物清单' in report, "报告中应包含产出物部分"
    assert '问题与风险' in report, "报告中应包含问题部分"
    assert '总结与建议' in report, "报告中应包含总结部分"
    print(f"完整报告生成成功，长度: {len(report)} 字符")
    print(f"报告前500字符:\n{report[:500]}...")
    
    progress_report = report_generator.generate_project_report(project_id, 'progress')
    assert '项目进度' in progress_report, "进度报告应包含进度部分"
    print(f"\n进度报告生成成功")
    
    deliverables_report = report_generator.generate_project_report(project_id, 'deliverables')
    assert '产出物清单' in deliverables_report, "产出物报告应包含产出物部分"
    print(f"产出物报告生成成功")
    
    report_path = report_generator.export_report(project_id, report_type='full')
    assert os.path.exists(report_path), f"报告文件未生成: {report_path}"
    print(f"\n报告导出成功: {report_path}")
    
    summary_report = report_generator.generate_summary_report()
    assert '项目汇总报告' in summary_report, "汇总报告标题不正确"
    print(f"汇总报告生成成功")
    
    print("\n所有测试通过！")
    
    return True


if __name__ == '__main__':
    success = test_report_generator()
    sys.exit(0 if success else 1)