import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from task_generator import TaskGenerator
from progress_tracker import ProgressTracker
from recommendation_engine import RecommendationEngine
from report_generator import ReportGenerator
from data_analyzer import DataAnalyzer


class NaturalLanguageInterface:
    def __init__(self):
        self._init_services()
        self.current_project_id = None
        
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
        
        self.templates = self.template_manager.list_templates()
        self.template_names = {t['title']: t['id'] for t in self.templates}
        self.template_ids = {t['id']: t['title'] for t in self.templates}
    
    def run(self):
        print("=" * 60)
        print("  AI智能体私域流量运营工作流自动化系统 - 自然语言交互")
        print("=" * 60)
        print("\n你可以用自然语言告诉我你想做什么，例如：")
        print("  - 启动数据分析工作流")
        print("  - 创建一个用户增长项目")
        print("  - 查看项目进度")
        print("  - 获取第1步的推荐")
        print("  - 生成报告")
        print("  - 退出")
        print("\n" + "=" * 60)
        
        while True:
            user_input = input("\n请输入你的指令: ").strip()
            if not user_input:
                continue
            
            response = self.process_input(user_input)
            print("\n" + response)
            
            if user_input.lower() in ['退出', 'quit', 'exit', 'bye', '结束']:
                break
    
    def process_input(self, user_input: str) -> str:
        if self._is_exit_command(user_input):
            return "再见！感谢使用AI智能体私域流量运营工作流自动化系统。"
        
        if self._is_help_command(user_input):
            return self._get_help_message()
        
        if self._is_list_templates_command(user_input):
            return self._list_templates()
        
        if self._is_start_workflow_command(user_input):
            return self._start_workflow(user_input)
        
        if self._is_show_progress_command(user_input):
            return self._show_progress(user_input)
        
        if self._is_get_recommendation_command(user_input):
            return self._get_recommendation(user_input)
        
        if self._is_generate_report_command(user_input):
            return self._generate_report(user_input)
        
        if self._is_analyze_command(user_input):
            return self._analyze(user_input)
        
        if self._is_show_projects_command(user_input):
            return self._show_projects()
        
        if self._is_complete_task_command(user_input):
            return self._complete_task(user_input)
        
        if self._is_search_command(user_input):
            return self._search(user_input)
        
        return self._unknown_command(user_input)
    
    def _is_exit_command(self, input_str: str) -> bool:
        keywords = ['退出', 'quit', 'exit', 'bye', '结束', '离开', '拜拜']
        return any(keyword in input_str for keyword in keywords)
    
    def _is_help_command(self, input_str: str) -> bool:
        keywords = ['帮助', 'help', '指令', '命令', '用法']
        return any(keyword in input_str for keyword in keywords)
    
    def _is_list_templates_command(self, input_str: str) -> bool:
        keywords = ['查看', '列表', '模板', '工作流']
        return all(k in input_str for k in ['模板', '列表']) or '查看工作流' in input_str
    
    def _is_start_workflow_command(self, input_str: str) -> bool:
        keywords = ['启动', '创建', '开始', '新建', '开启']
        has_workflow = any(wf in input_str for wf in ['工作流', '项目'])
        return any(k in input_str for k in keywords) and has_workflow
    
    def _is_show_progress_command(self, input_str: str) -> bool:
        keywords = ['进度', '状态', '进展']
        return any(k in input_str for k in keywords)
    
    def _is_get_recommendation_command(self, input_str: str) -> bool:
        keywords = ['推荐', '建议', '工具', '指导', '步骤']
        return any(k in input_str for k in keywords)
    
    def _is_generate_report_command(self, input_str: str) -> bool:
        keywords = ['报告', '生成', '总结']
        return any(k in input_str for k in keywords) and '报告' in input_str
    
    def _is_analyze_command(self, input_str: str) -> bool:
        keywords = ['分析', '数据', '建议']
        return '分析' in input_str or ('数据' in input_str and '建议' in input_str)
    
    def _is_show_projects_command(self, input_str: str) -> bool:
        return '项目' in input_str and ('列表' in input_str or '查看' in input_str)
    
    def _is_complete_task_command(self, input_str: str) -> bool:
        keywords = ['完成', '标记', '更新']
        return any(k in input_str for k in keywords) and ('任务' in input_str or '步骤' in input_str)
    
    def _is_search_command(self, input_str: str) -> bool:
        return '搜索' in input_str or '查找' in input_str
    
    def _get_help_message(self) -> str:
        help_text = "可用的自然语言指令:\n\n"
        help_text += "📋 模板管理:\n"
        help_text += "  - 查看工作流模板列表\n"
        help_text += "  - 列出所有模板\n\n"
        help_text += "🚀 项目创建:\n"
        help_text += "  - 启动数据分析工作流\n"
        help_text += "  - 创建用户增长项目\n"
        help_text += "  - 新建营销推广项目\n\n"
        help_text += "📊 进度管理:\n"
        help_text += "  - 查看项目进度\n"
        help_text += "  - 查看当前进度\n\n"
        help_text += "💡 智能推荐:\n"
        help_text += "  - 获取步骤1的推荐\n"
        help_text += "  - 推荐工具\n"
        help_text += "  - 搜索数据分析相关内容\n\n"
        help_text += "📝 报告生成:\n"
        help_text += "  - 生成项目报告\n"
        help_text += "  - 生成汇总报告\n\n"
        help_text += "🔍 数据分析:\n"
        help_text += "  - 数据分析报告\n"
        help_text += "  - 获取优化建议\n\n"
        help_text += "✅ 任务管理:\n"
        help_text += "  - 完成第一个任务\n"
        help_text += "  - 标记任务为完成\n\n"
        help_text += "📋 项目列表:\n"
        help_text += "  - 查看项目列表\n\n"
        help_text += "❌ 退出:\n"
        help_text += "  - 退出\n"
        help_text += "  - 结束\n"
        return help_text
    
    def _list_templates(self) -> str:
        result = f"可用的工作流模板 ({len(self.templates)} 个):\n\n"
        for i, template in enumerate(self.templates, 1):
            title = template['title'] or '未命名工作流'
            scope = template.get('scope', '未指定')
            steps = len(template['steps'])
            result += f"  {i}. {title}\n"
            result += f"     - 适用范围: {scope}\n"
            result += f"     - 步骤数: {steps}\n\n"
        return result
    
    def _start_workflow(self, input_str: str) -> str:
        template_id = None
        project_name = "新项目"
        
        for title, tid in self.template_names.items():
            if title in input_str or tid in input_str:
                template_id = tid
                break
        
        if not template_id:
            for tid, title in self.template_ids.items():
                if tid in input_str or title in input_str:
                    template_id = tid
                    break
        
        if not template_id:
            return "未找到匹配的工作流模板，请说清楚模板名称，例如：'启动数据分析工作流'"
        
        project_name_match = re.search(r'(项目|工作流)\s*(名称|叫|为)\s*(.+)', input_str)
        if project_name_match:
            project_name = project_name_match.group(3).strip()
        else:
            project_name = f"{self.template_ids.get(template_id, '工作流')}项目"
        
        template = self.template_manager.get_template(template_id)
        if not template:
            return f"模板 {template_id} 不存在"
        
        project_info = {'project_name': project_name}
        project_id = self.task_generator.generate_tasks(template, project_info)
        self.current_project_id = project_id
        
        project = self.task_generator.get_project_tasks(project_id)
        
        result = f"🎉 项目创建成功！\n\n"
        result += f"项目名称: {project_name}\n"
        result += f"项目ID: {project_id}\n"
        result += f"工作流模板: {template['title']}\n"
        result += f"生成任务数: {len(project['tasks'])}\n\n"
        result += f"📋 工作流步骤概览:\n"
        for step in template['steps']:
            result += f"  步骤{step['step_number']}: {step['title']}\n"
        
        return result
    
    def _show_progress(self, input_str: str) -> str:
        project_id = self._extract_project_id(input_str)
        
        if not project_id:
            projects = self.task_generator.list_projects()
            if not projects:
                return "暂无项目，请先创建项目"
            
            result = "项目列表:\n\n"
            for project in projects:
                progress = self.progress_tracker.get_project_progress(project['project_id'])
                result += f"📊 {project['project_name']} ({project['project_id']})\n"
                result += f"   进度: {progress['progress_percent']}%\n"
                result += f"   任务: {progress['completed_tasks']}/{progress['total_tasks']}\n\n"
            return result
        
        progress = self.progress_tracker.get_project_progress(project_id)
        if not progress:
            return f"项目 {project_id} 不存在"
        
        self.current_project_id = project_id
        
        result = f"📊 项目进度: {progress['project_name']}\n\n"
        result += f"整体进度: {progress['progress_percent']}%\n"
        result += f"总任务数: {progress['total_tasks']}\n"
        result += f"  ├─ 已完成: {progress['completed_tasks']}\n"
        result += f"  ├─ 进行中: {progress['in_progress_tasks']}\n"
        result += f"  ├─ 待办: {progress['pending_tasks']}\n"
        result += f"  └─ 逾期: {progress['overdue_tasks']}\n\n"
        
        result += f"各步骤进度:\n"
        for step_num, step_info in progress['step_progress'].items():
            bar = self._generate_progress_bar(step_info['percent'])
            result += f"  步骤{step_num}: {bar} {step_info['percent']}% ({step_info['completed']}/{step_info['total']})\n"
        
        return result
    
    def _get_recommendation(self, input_str: str) -> str:
        template_id = self.current_project_id
        
        project = None
        if self.current_project_id:
            project = self.task_generator.get_project_tasks(self.current_project_id)
        
        if not project:
            projects = self.task_generator.list_projects()
            if projects:
                self.current_project_id = projects[0]['project_id']
                project = projects[0]
        
        if project:
            template_id = project['template_id']
        else:
            for tid in self.template_ids:
                if tid in input_str or self.template_ids[tid] in input_str:
                    template_id = tid
                    break
        
        if not template_id:
            return "请先创建项目或指定模板名称"
        
        step_match = re.search(r'(步骤|第)\s*(\d+)', input_str)
        step_number = int(step_match.group(2)) if step_match else 1
        
        recs = self.recommendation_engine.get_step_recommendations(template_id, step_number)
        if 'error' in recs:
            return recs['error']
        
        result = f"💡 步骤推荐: {recs['step_title']}\n\n"
        
        if recs['notes']:
            result += "⚠️ 注意事项:\n"
            for note in recs['notes']:
                result += f"  - {note}\n"
        
        if recs['related_tools']:
            result += "\n🛠️ 推荐工具:\n"
            for tool in recs['related_tools']:
                result += f"  - {tool}\n"
        
        if recs['deliverables']:
            result += "\n📦 产出物:\n"
            for deliverable in recs['deliverables']:
                result += f"  - {deliverable}\n"
        
        return result
    
    def _generate_report(self, input_str: str) -> str:
        project_id = self.current_project_id
        
        if not project_id:
            projects = self.task_generator.list_projects()
            if projects:
                self.current_project_id = projects[0]['project_id']
                project_id = projects[0]['project_id']
        
        if not project_id:
            return "请先创建项目"
        
        if '汇总' in input_str:
            report = self.report_generator.generate_summary_report()
        else:
            report = self.report_generator.generate_project_report(project_id, 'full')
            output_path = self.report_generator.export_report(project_id)
        
        return report[:1000] + ("..." if len(report) > 1000 else "")
    
    def _analyze(self, input_str: str) -> str:
        if '建议' in input_str:
            suggestions = self.data_analyzer.generate_optimization_suggestions()
            result = f"🔍 优化建议 ({len(suggestions)} 条):\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                result += f"  {i}. {suggestion}\n"
            return result
        
        report = self.data_analyzer.generate_analysis_report()
        return report[:800] + ("..." if len(report) > 800 else "")
    
    def _show_projects(self) -> str:
        projects = self.task_generator.list_projects()
        if not projects:
            return "暂无项目，请先创建项目"
        
        result = f"📋 项目列表 ({len(projects)} 个):\n\n"
        for i, project in enumerate(projects, 1):
            progress = self.progress_tracker.get_project_progress(project['project_id'])
            result += f"  {i}. {project['project_name']}\n"
            result += f"     ID: {project['project_id']}\n"
            result += f"     模板: {project['template_title']}\n"
            result += f"     进度: {progress['progress_percent']}%\n"
            result += f"     任务: {progress['completed_tasks']}/{progress['total_tasks']}\n\n"
        return result
    
    def _complete_task(self, input_str: str) -> str:
        if not self.current_project_id:
            projects = self.task_generator.list_projects()
            if projects:
                self.current_project_id = projects[0]['project_id']
        
        if not self.current_project_id:
            return "请先创建项目"
        
        project = self.task_generator.get_project_tasks(self.current_project_id)
        if not project:
            return "项目不存在"
        
        task_match = re.search(r'(第|任务)\s*(\d+)', input_str)
        task_index = int(task_match.group(2)) - 1 if task_match else 0
        
        if task_index < 0 or task_index >= len(project['tasks']):
            return f"任务索引超出范围，该项目共有 {len(project['tasks'])} 个任务"
        
        task = project['tasks'][task_index]
        result = self.progress_tracker.update_task_status(self.current_project_id, task['task_id'], 'completed')
        
        if result:
            return f"✅ 任务 '{task['task_name']}' 已标记为完成！"
        else:
            return "任务更新失败"
    
    def _search(self, input_str: str) -> str:
        keyword_match = re.search(r'(搜索|查找)\s*(.+)$', input_str)
        if not keyword_match:
            return "请输入搜索关键词，例如：'搜索数据分析'"
        
        keyword = keyword_match.group(2).strip()
        results = self.recommendation_engine.search_recommendations(keyword)
        
        if not results:
            return f"未找到与 '{keyword}' 相关的内容"
        
        result = f"🔍 搜索结果: '{keyword}' ({len(results)} 条)\n\n"
        for i, res in enumerate(results[:5], 1):
            result += f"  {i}. {res['template_title']} - 步骤{res['step_number']}: {res['step_title']}\n"
            if res['notes']:
                result += f"     注意事项: {res['notes'][0][:30]}...\n"
        
        return result
    
    def _extract_project_id(self, input_str: str) -> str:
        projects = self.task_generator.list_projects()
        for project in projects:
            if project['project_id'] in input_str or project['project_name'] in input_str:
                return project['project_id']
        return None
    
    def _unknown_command(self, input_str: str) -> str:
        return f"抱歉，我不太理解 '{input_str}'。你可以说：\n\n" \
               "  - 启动数据分析工作流\n" \
               "  - 创建用户增长项目\n" \
               "  - 查看项目进度\n" \
               "  - 获取步骤推荐\n" \
               "  - 生成报告\n" \
               "  - 帮助"
    
    def _generate_progress_bar(self, percent: float) -> str:
        bar_length = 15
        filled = int(bar_length * (percent / 100))
        return f"[{'█'*filled}{'░'*(bar_length-filled)}]"


def main():
    nli = NaturalLanguageInterface()
    nli.run()


if __name__ == '__main__':
    main()