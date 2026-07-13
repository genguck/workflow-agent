import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator
from progress_tracker import ProgressTracker
from recommendation_engine import RecommendationEngine
from report_generator import ReportGenerator
from data_analyzer import DataAnalyzer


def export_all():
    # 初始化服务
    workflow_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = WorkflowParser()
    workflows = parser.parse_folder(workflow_dir)

    template_manager = TemplateManager()
    template_manager.import_from_workflows(workflows)

    task_generator = TaskGenerator()
    progress_tracker = ProgressTracker()
    recommendation_engine = RecommendationEngine(template_manager)
    report_generator = ReportGenerator(template_manager, task_generator, progress_tracker)
    data_analyzer = DataAnalyzer(template_manager, task_generator, progress_tracker)

    # 创建导出目录
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exports')
    os.makedirs(export_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = []

    # 1. 导出模板列表
    templates = template_manager.list_templates()
    templates_path = os.path.join(export_dir, f'模板列表_{timestamp}.txt')
    with open(templates_path, 'w', encoding='utf-8') as f:
        f.write('=' * 60 + '\n')
        f.write('  工作流模板列表\n')
        f.write('=' * 60 + '\n\n')
        for i, t in enumerate(templates, 1):
            f.write(f'{i}. 模板ID: {t["id"]}\n')
            f.write(f'   标题: {t.get("title", "未命名")}\n')
            f.write(f'   版本: {t.get("version", "V1.0")}\n')
            f.write(f'   适用范围: {t.get("scope", "未指定")}\n')
            f.write(f'   步骤数: {len(t.get("steps", []))}\n\n')
    results.append(f'模板列表 -> {templates_path}')

    # 2. 导出每个模板的详情
    for template in templates:
        tid = template['id']
        title = template.get('title', '未命名')
        detail = template_manager.get_template(tid)
        if not detail:
            continue

        safe_name = tid.replace('/', '_').replace('\\', '_')
        detail_path = os.path.join(export_dir, f'模板详情_{safe_name}_{timestamp}.txt')
        with open(detail_path, 'w', encoding='utf-8') as f:
            f.write('=' * 60 + '\n')
            f.write(f'  {title}\n')
            f.write('=' * 60 + '\n\n')
            f.write(f'模板ID: {tid}\n')
            f.write(f'版本: {detail.get("version", "V1.0")}\n')
            f.write(f'适用范围: {detail.get("scope", "未指定")}\n')
            f.write(f'文档目的: {detail.get("purpose", "未指定")}\n')
            f.write(f'总步骤: {len(detail.get("steps", []))}\n\n')

            for step in detail.get('steps', []):
                f.write('-' * 50 + '\n')
                f.write(f'步骤{step.get("step_number", "?")}: {step.get("title", "")}\n')
                f.write('-' * 50 + '\n\n')

                if step.get('goals'):
                    f.write('【目标】\n')
                    for g in step['goals']:
                        f.write(f'  - {g}\n')
                    f.write('\n')

                if step.get('actions'):
                    f.write('【具体操作】\n')
                    for a in step['actions']:
                        f.write(f'  - {a}\n')
                    f.write('\n')

                if step.get('tools'):
                    f.write('【工具推荐】\n')
                    for t in step['tools']:
                        f.write(f'  - {t}\n')
                    f.write('\n')

                if step.get('notes'):
                    f.write('【注意事项】\n')
                    for n in step['notes']:
                        f.write(f'  - {n}\n')
                    f.write('\n')

                if step.get('deliverables'):
                    f.write('【产出物】\n')
                    for d in step['deliverables']:
                        f.write(f'  - {d}\n')
                    f.write('\n')

                if step.get('estimated_hours'):
                    f.write(f'【预估耗时】{step["estimated_hours"]}小时\n\n')
        results.append(f'模板详情[{title}] -> {detail_path}')

    # 3. 导出项目列表
    projects = task_generator.list_projects()
    projects_path = os.path.join(export_dir, f'项目列表_{timestamp}.txt')
    with open(projects_path, 'w', encoding='utf-8') as f:
        f.write('=' * 60 + '\n')
        f.write('  项目列表\n')
        f.write('=' * 60 + '\n\n')
        if not projects:
            f.write('暂无项目\n')
        else:
            for i, p in enumerate(projects, 1):
                progress = progress_tracker.get_project_progress(p['project_id'])
                f.write(f'{i}. 项目名称: {p["project_name"]}\n')
                f.write(f'   项目ID: {p["project_id"]}\n')
                f.write(f'   模板: {p.get("template_title", "未指定")}\n')
                f.write(f'   负责人: {p.get("assignee", "未指定")}\n')
                f.write(f'   创建时间: {p.get("created_at", "未知")}\n')
                f.write(f'   任务数: {len(p.get("tasks", []))}\n')
                if progress:
                    f.write(f'   进度: {progress["progress_percent"]}%\n')
                    f.write(f'   已完成: {progress["completed_tasks"]}/{progress["total_tasks"]}\n')
                f.write('\n')
    results.append(f'项目列表 -> {projects_path}')

    # 4. 导出每个项目的进度报告
    for project in projects:
        pid = project['project_id']
        progress = progress_tracker.get_project_progress(pid)
        if not progress:
            continue

        progress_path = os.path.join(export_dir, f'进度报告_{pid}_{timestamp}.txt')
        with open(progress_path, 'w', encoding='utf-8') as f:
            f.write('=' * 60 + '\n')
            f.write(f'  项目进度报告: {progress["project_name"]}\n')
            f.write('=' * 60 + '\n\n')
            f.write(f'项目ID: {pid}\n\n')
            f.write(f'整体进度: {progress["progress_percent"]}%\n')
            f.write(f'总任务数: {progress["total_tasks"]}\n')
            f.write(f'  已完成: {progress["completed_tasks"]}\n')
            f.write(f'  进行中: {progress["in_progress_tasks"]}\n')
            f.write(f'  待办: {progress["pending_tasks"]}\n')
            f.write(f'  逾期: {progress["overdue_tasks"]}\n\n')
            f.write('各步骤进度:\n')
            for step_num, step_info in sorted(progress.get('step_progress', {}).items()):
                bar = '█' * int(step_info['percent'] / 10) + '░' * (10 - int(step_info['percent'] / 10))
                f.write(f'  步骤{step_num}: [{bar}] {step_info["percent"]}% ({step_info["completed"]}/{step_info["total"]})\n')
        results.append(f'进度报告[{progress["project_name"]}] -> {progress_path}')

    # 5. 导出每个项目的完整报告
    for project in projects:
        pid = project['project_id']
        report = report_generator.generate_project_report(pid, 'full')
        report_path = os.path.join(export_dir, f'项目报告_{pid}_{timestamp}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        results.append(f'项目报告[{project["project_name"]}] -> {report_path}')

    # 6. 导出汇总报告
    summary_report = report_generator.generate_summary_report()
    summary_path = os.path.join(export_dir, f'汇总报告_{timestamp}.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_report)
    results.append(f'汇总报告 -> {summary_path}')

    # 7. 导出数据分析报告
    analysis_report = data_analyzer.generate_analysis_report()
    analysis_path = os.path.join(export_dir, f'数据分析报告_{timestamp}.txt')
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(analysis_report)
    results.append(f'数据分析报告 -> {analysis_path}')

    # 8. 导出优化建议
    suggestions = data_analyzer.generate_optimization_suggestions()
    suggestions_path = os.path.join(export_dir, f'优化建议_{timestamp}.txt')
    with open(suggestions_path, 'w', encoding='utf-8') as f:
        f.write('=' * 60 + '\n')
        f.write('  优化建议\n')
        f.write('=' * 60 + '\n\n')
        if suggestions:
            for i, s in enumerate(suggestions, 1):
                f.write(f'{i}. {s}\n')
        else:
            f.write('暂无优化建议\n')
    results.append(f'优化建议 -> {suggestions_path}')

    # 9. 导出全部数据为JSON
    all_data = {
        'export_time': datetime.now().isoformat(),
        'templates': templates,
        'projects': projects,
        'suggestions': suggestions
    }
    json_path = os.path.join(export_dir, f'全部数据_{timestamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    results.append(f'全部数据(JSON) -> {json_path}')

    # 输出导出结果
    print('=' * 60)
    print('  文档导出完成')
    print('=' * 60)
    print(f'\n导出目录: {export_dir}\n')
    print(f'共导出 {len(results)} 个文件:\n')
    for i, r in enumerate(results, 1):
        print(f'  {i}. {r}')
    print(f'\n导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')


if __name__ == '__main__':
    export_all()