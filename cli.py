import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator
from progress_tracker import ProgressTracker
from recommendation_engine import RecommendationEngine
from report_generator import ReportGenerator
from data_analyzer import DataAnalyzer


class WorkflowCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='AI智能体私域流量运营工作流自动化系统',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  workflow-cli templates list          # 列出所有工作流模板
  workflow-cli project create --template 用户增长 --name "Q4增长项目" --assignee 张三
  workflow-cli progress show <project_id>
  workflow-cli report generate <project_id>
  workflow-cli recommend --template 用户增长 --step 1
            """
        )
        
        self.subparsers = self.parser.add_subparsers(dest='command', help='可用命令')
        
        self._setup_templates_parser()
        self._setup_project_parser()
        self._setup_progress_parser()
        self._setup_recommend_parser()
        self._setup_report_parser()
        self._setup_analyze_parser()
        
        self._init_services()
    
    def _init_services(self):
        workflow_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parser = WorkflowParser()
        workflows = parser.parse_folder(workflow_dir)
        
        self.template_manager = TemplateManager()
        self.template_manager.import_from_workflows(workflows)
        
        self.task_generator = TaskGenerator()
        self.progress_tracker = ProgressTracker()
        self.recommendation_engine = RecommendationEngine(self.template_manager)
        self.report_generator = ReportGenerator(self.template_manager, self.task_generator, self.progress_tracker)
        self.data_analyzer = DataAnalyzer(self.template_manager, self.task_generator, self.progress_tracker)
    
    def _setup_templates_parser(self):
        templates_parser = self.subparsers.add_parser('templates', help='工作流模板管理')
        templates_subparsers = templates_parser.add_subparsers(dest='action')
        
        list_parser = templates_subparsers.add_parser('list', help='列出所有模板')
        
        show_parser = templates_subparsers.add_parser('show', help='查看模板详情')
        show_parser.add_argument('template_id', help='模板ID')
        
        stats_parser = templates_subparsers.add_parser('stats', help='模板统计信息')
    
    def _setup_project_parser(self):
        project_parser = self.subparsers.add_parser('project', help='项目管理')
        project_subparsers = project_parser.add_subparsers(dest='action')
        
        create_parser = project_subparsers.add_parser('create', help='创建新项目')
        create_parser.add_argument('--template', required=True, help='模板ID')
        create_parser.add_argument('--name', required=True, help='项目名称')
        create_parser.add_argument('--assignee', help='负责人')
        create_parser.add_argument('--start-date', dest='start_date', help='开始日期 (YYYY-MM-DD)')
        
        list_parser = project_subparsers.add_parser('list', help='列出所有项目')
        
        show_parser = project_subparsers.add_parser('show', help='查看项目详情')
        show_parser.add_argument('project_id', help='项目ID')
    
    def _setup_progress_parser(self):
        progress_parser = self.subparsers.add_parser('progress', help='进度管理')
        progress_subparsers = progress_parser.add_subparsers(dest='action')
        
        show_parser = progress_subparsers.add_parser('show', help='查看项目进度')
        show_parser.add_argument('project_id', help='项目ID')
        
        update_parser = progress_subparsers.add_parser('update', help='更新任务状态')
        update_parser.add_argument('project_id', help='项目ID')
        update_parser.add_argument('task_id', help='任务ID')
        update_parser.add_argument('status', choices=['pending', 'in_progress', 'completed'], help='任务状态')
        
        reminders_parser = progress_subparsers.add_parser('reminders', help='查看逾期提醒')
    
    def _setup_recommend_parser(self):
        recommend_parser = self.subparsers.add_parser('recommend', help='智能推荐')
        recommend_parser.add_argument('--template', required=True, help='模板ID')
        recommend_parser.add_argument('--step', type=int, help='步骤号')
        recommend_parser.add_argument('--search', help='关键词搜索')
    
    def _setup_report_parser(self):
        report_parser = self.subparsers.add_parser('report', help='报告管理')
        report_subparsers = report_parser.add_subparsers(dest='action')
        
        generate_parser = report_subparsers.add_parser('generate', help='生成项目报告')
        generate_parser.add_argument('project_id', help='项目ID')
        generate_parser.add_argument('--type', choices=['full', 'progress', 'tasks', 'deliverables', 'issues'], default='full', help='报告类型')
        
        summary_parser = report_subparsers.add_parser('summary', help='生成汇总报告')
    
    def _setup_analyze_parser(self):
        analyze_parser = self.subparsers.add_parser('analyze', help='数据分析')
        analyze_subparsers = analyze_parser.add_subparsers(dest='action')
        
        report_parser = analyze_subparsers.add_parser('report', help='生成数据分析报告')
        
        suggestions_parser = analyze_subparsers.add_parser('suggestions', help='获取优化建议')
    
    def run(self):
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        command_map = {
            'templates': self._handle_templates,
            'project': self._handle_project,
            'progress': self._handle_progress,
            'recommend': self._handle_recommend,
            'report': self._handle_report,
            'analyze': self._handle_analyze
        }
        
        handler = command_map.get(args.command)
        if handler:
            handler(args)
        else:
            print(f"未知命令: {args.command}")
            self.parser.print_help()
    
    def _handle_templates(self, args):
        if args.action == 'list':
            templates = self.template_manager.list_templates()
            print(f"{'='*60}")
            print(f"工作流模板列表 ({len(templates)} 个)")
            print(f"{'='*60}")
            for template in templates:
                print(f"\nID: {template['id']}")
                print(f"标题: {template['title']}")
                print(f"版本: {template['version']}")
                print(f"适用范围: {template.get('scope', '未指定')}")
                print(f"步骤数: {len(template['steps'])}")
        
        elif args.action == 'show':
            template = self.template_manager.get_template(args.template_id)
            if not template:
                print(f"模板 {args.template_id} 不存在")
                return
            
            overview = self.recommendation_engine.get_template_overview(args.template_id)
            if 'error' in overview:
                print(overview['error'])
                return
            
            print(f"{'='*60}")
            print(f"模板详情: {overview['title']}")
            print(f"{'='*60}")
            print(f"版本: {overview['version']}")
            print(f"适用范围: {overview['scope']}")
            print(f"文档目的: {overview.get('purpose', '未指定')}")
            print(f"总步骤: {overview['total_steps']}")
            print(f"预估时间: {overview['estimated_total_time']}")
            print(f"\n步骤概览:")
            for step in overview['steps_summary']:
                print(f"  步骤{step['step_number']}: {step['title']}")
                print(f"    - 目标: {step['objectives_count']} 个")
                print(f"    - 操作: {step['operations_count']} 个")
                print(f"    - 产出物: {step['deliverables_count']} 个")
        
        elif args.action == 'stats':
            stats = self.template_manager.get_stats()
            print(f"{'='*60}")
            print(f"模板统计")
            print(f"{'='*60}")
            print(f"总模板数: {stats['total_templates']}")
            print(f"总步骤数: {stats['total_steps']}")
            print(f"总工具数: {stats['total_tools']}")
            print(f"总子模板数: {stats['total_sub_templates']}")
    
    def _handle_project(self, args):
        if args.action == 'create':
            template = self.template_manager.get_template(args.template)
            if not template:
                print(f"模板 {args.template} 不存在")
                return
            
            project_info = {
                'project_name': args.name,
                'assignee': args.assignee or '',
                'start_date': args.start_date or ''
            }
            
            project_id = self.task_generator.generate_tasks(template, project_info)
            print(f"项目创建成功！")
            print(f"项目ID: {project_id}")
            print(f"项目名称: {args.name}")
            print(f"工作流模板: {template['title']}")
            print(f"负责人: {args.assignee or '未指定'}")
            
            project = self.task_generator.get_project_tasks(project_id)
            print(f"生成任务数: {len(project['tasks'])}")
        
        elif args.action == 'list':
            projects = self.task_generator.list_projects()
            if not projects:
                print("暂无项目")
                return
            
            print(f"{'='*60}")
            print(f"项目列表 ({len(projects)} 个)")
            print(f"{'='*60}")
            for project in projects:
                progress = self.progress_tracker.get_project_progress(project['project_id'])
                print(f"\n项目名称: {project['project_name']}")
                print(f"项目ID: {project['project_id']}")
                print(f"模板: {project['template_title']}")
                print(f"负责人: {project.get('assignee', '未指定')}")
                print(f"进度: {progress['progress_percent']}%")
                print(f"任务: {progress['completed_tasks']}/{progress['total_tasks']}")
        
        elif args.action == 'show':
            project = self.task_generator.get_project_tasks(args.project_id)
            if not project:
                print(f"项目 {args.project_id} 不存在")
                return
            
            progress = self.progress_tracker.get_project_progress(args.project_id)
            
            print(f"{'='*60}")
            print(f"项目详情: {project['project_name']}")
            print(f"{'='*60}")
            print(f"项目ID: {project['project_id']}")
            print(f"工作流模板: {project['template_title']}")
            print(f"负责人: {project.get('assignee', '未指定')}")
            print(f"开始日期: {project['start_date']}")
            print(f"创建时间: {project['created_at']}")
            print(f"\n进度概览:")
            print(f"  整体进度: {progress['progress_percent']}%")
            print(f"  总任务: {progress['total_tasks']}")
            print(f"  已完成: {progress['completed_tasks']}")
            print(f"  进行中: {progress['in_progress_tasks']}")
            print(f"  待办: {progress['pending_tasks']}")
            print(f"  逾期: {progress['overdue_tasks']}")
    
    def _handle_progress(self, args):
        if args.action == 'show':
            progress = self.progress_tracker.get_project_progress(args.project_id)
            if not progress:
                print(f"项目 {args.project_id} 不存在")
                return
            
            print(f"{'='*60}")
            print(f"项目进度: {progress['project_name']}")
            print(f"{'='*60}")
            print(f"整体进度: {progress['progress_percent']}%")
            print(f"总任务数: {progress['total_tasks']}")
            print(f"  ├─ 已完成: {progress['completed_tasks']}")
            print(f"  ├─ 进行中: {progress['in_progress_tasks']}")
            print(f"  ├─ 待办: {progress['pending_tasks']}")
            print(f"  └─ 逾期: {progress['overdue_tasks']}")
            print(f"\n各步骤进度:")
            for step_num, step_info in progress['step_progress'].items():
                bar = self._generate_progress_bar(step_info['percent'])
                print(f"  步骤{step_num}: {bar} {step_info['percent']}% ({step_info['completed']}/{step_info['total']})")
        
        elif args.action == 'update':
            result = self.progress_tracker.update_task_status(args.project_id, args.task_id, args.status)
            if result:
                print(f"任务 {args.task_id} 状态更新为 {args.status}")
            else:
                print(f"更新失败，项目或任务不存在")
        
        elif args.action == 'reminders':
            reminders = self.progress_tracker.get_pending_reminders()
            if not reminders:
                print("暂无待处理提醒")
                return
            
            print(f"{'='*60}")
            print(f"待处理提醒 ({len(reminders)} 条)")
            print(f"{'='*60}")
            for reminder in reminders:
                print(f"\n提醒ID: {reminder['reminder_id']}")
                print(f"项目: {reminder['project_id']}")
                print(f"任务: {reminder['task_name']}")
                print(f"截止日期: {reminder['due_date']}")
                print(f"消息: {reminder['message']}")
    
    def _handle_recommend(self, args):
        if args.step:
            recs = self.recommendation_engine.get_step_recommendations(args.template, args.step)
            if 'error' in recs:
                print(recs['error'])
                return
            
            print(f"{'='*60}")
            print(f"步骤推荐: {recs['step_title']}")
            print(f"{'='*60}")
            
            if recs['notes']:
                print(f"\n注意事项:")
                for note in recs['notes']:
                    print(f"  - {note}")
            
            if recs['related_tools']:
                print(f"\n推荐工具:")
                for tool in recs['related_tools']:
                    print(f"  - {tool}")
            
            if recs['best_practices']:
                print(f"\n最佳实践:")
                for practice in recs['best_practices']:
                    print(f"  - {practice}")
            
            if recs['deliverables']:
                print(f"\n产出物:")
                for deliverable in recs['deliverables']:
                    print(f"  - {deliverable}")
        
        elif args.search:
            results = self.recommendation_engine.search_recommendations(args.search)
            if not results:
                print(f"未找到与 '{args.search}' 相关的内容")
                return
            
            print(f"{'='*60}")
            print(f"搜索结果: '{args.search}' ({len(results)} 条)")
            print(f"{'='*60}")
            for result in results:
                print(f"\n模板: {result['template_title']}")
                print(f"步骤{result['step_number']}: {result['step_title']}")
                print(f"相关度: {result['relevance']}")
                if result['notes']:
                    print(f"注意事项: {result['notes'][:2]}")
    
    def _handle_report(self, args):
        if args.action == 'generate':
            report = self.report_generator.generate_project_report(args.project_id, args.type)
            if '不存在' in report:
                print(report)
                return
            
            print(report)
            
            output_path = self.report_generator.export_report(args.project_id, report_type=args.type)
            print(f"\n报告已导出: {output_path}")
        
        elif args.action == 'summary':
            report = self.report_generator.generate_summary_report()
            print(report)
    
    def _handle_analyze(self, args):
        if args.action == 'report':
            report = self.data_analyzer.generate_analysis_report()
            print(report)
        
        elif args.action == 'suggestions':
            suggestions = self.data_analyzer.generate_optimization_suggestions()
            print(f"{'='*60}")
            print(f"优化建议 ({len(suggestions)} 条)")
            print(f"{'='*60}")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. {suggestion}")
    
    def _generate_progress_bar(self, percent: float) -> str:
        bar_length = 20
        filled = int(bar_length * (percent / 100))
        return f"[{'█'*filled}{'░'*(bar_length-filled)}]"


def main():
    cli = WorkflowCLI()
    cli.run()


if __name__ == '__main__':
    main()