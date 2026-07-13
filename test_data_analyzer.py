import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator
from progress_tracker import ProgressTracker
from data_analyzer import DataAnalyzer


def test_data_analyzer():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    manager = TemplateManager()
    manager.import_from_workflows(workflows)
    
    template = manager.get_template('用户增长')
    assert template is not None, "无法获取用户增长模板"
    
    project_info = {
        'project_name': '数据分析测试项目',
        'assignee': '赵六',
        'start_date': '2024-01-01'
    }
    
    generator = TaskGenerator()
    project_id = generator.generate_tasks(template, project_info)
    
    tracker = ProgressTracker()
    
    analyzer = DataAnalyzer(manager, generator, tracker)
    
    usage = analyzer.analyze_workflow_usage()
    assert 'total_templates' in usage, "缺少总模板数"
    assert 'total_projects' in usage, "缺少总项目数"
    assert 'template_usage' in usage, "缺少模板使用统计"
    print(f"工作流使用分析: {usage['total_templates']} 个模板, {usage['total_projects']} 个项目")
    
    completion = analyzer.analyze_task_completion()
    assert 'total_tasks' in completion, "缺少总任务数"
    assert 'completed_tasks' in completion, "缺少已完成任务数"
    assert 'overdue_tasks' in completion, "缺少逾期任务数"
    assert 'overall_completion_rate' in completion, "缺少完成率"
    print(f"任务完成分析: {completion['total_tasks']} 总任务, {completion['completed_tasks']} 已完成, {completion['overdue_rate']}% 逾期")
    
    step_effectiveness = analyzer.analyze_step_effectiveness()
    assert 'total_steps' in step_effectiveness, "缺少总步骤数"
    assert 'avg_objectives_per_step' in step_effectiveness, "缺少平均目标数"
    assert 'avg_operations_per_step' in step_effectiveness, "缺少平均操作数"
    assert 'avg_deliverables_per_step' in step_effectiveness, "缺少平均产出物数"
    print(f"步骤有效性分析: {step_effectiveness['total_steps']} 总步骤, 平均 {step_effectiveness['avg_operations_per_step']} 操作/步骤")
    
    suggestions = analyzer.generate_optimization_suggestions()
    assert isinstance(suggestions, list), "建议应为列表"
    assert len(suggestions) > 0, "应有优化建议"
    print(f"\n优化建议 ({len(suggestions)} 条):")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    report = analyzer.generate_analysis_report()
    assert '工作流数据分析报告' in report, "报告标题不正确"
    assert '工作流使用情况' in report, "报告中应包含使用情况"
    assert '任务完成情况' in report, "报告中应包含完成情况"
    assert '步骤有效性分析' in report, "报告中应包含步骤分析"
    assert '优化建议' in report, "报告中应包含优化建议"
    print(f"\n分析报告生成成功，长度: {len(report)} 字符")
    
    print("\n所有测试通过！")
    
    return True


if __name__ == '__main__':
    success = test_data_analyzer()
    sys.exit(0 if success else 1)