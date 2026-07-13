import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataAnalyzer:
    def __init__(self, template_manager, task_generator, progress_tracker):
        self.template_manager = template_manager
        self.task_generator = task_generator
        self.progress_tracker = progress_tracker
        self.analysis_results = {}

    def analyze_workflow_usage(self) -> Dict[str, Any]:
        templates = self.template_manager.list_templates()
        projects = self.task_generator.list_projects()
        
        template_usage = {}
        for template in templates:
            template_usage[template['id']] = {
                'title': template['title'],
                'version': template['version'],
                'project_count': 0,
                'total_tasks': len(template['steps']),
                'avg_completion_time': 0,
                'usage_count': 0
            }
        
        for project in projects:
            template_id = project['template_id']
            if template_id in template_usage:
                template_usage[template_id]['project_count'] += 1
        
        results = {
            'total_templates': len(templates),
            'total_projects': len(projects),
            'total_workflows': len(templates),
            'template_usage': template_usage,
            'most_used_template': self._find_most_used_template(template_usage),
            'least_used_template': self._find_least_used_template(template_usage)
        }
        
        self.analysis_results['workflow_usage'] = results
        
        return results

    def _find_most_used_template(self, template_usage: Dict[str, Any]) -> Optional[str]:
        max_count = 0
        most_used = None
        for template_id, usage in template_usage.items():
            if usage['project_count'] > max_count:
                max_count = usage['project_count']
                most_used = template_id
        return most_used

    def _find_least_used_template(self, template_usage: Dict[str, Any]) -> Optional[str]:
        min_count = float('inf')
        least_used = None
        for template_id, usage in template_usage.items():
            if usage['project_count'] < min_count:
                min_count = usage['project_count']
                least_used = template_id
        return least_used

    def analyze_task_completion(self) -> Dict[str, Any]:
        projects = self.task_generator.list_projects()
        
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        pending_tasks = 0
        overdue_tasks = 0
        
        completion_rates = []
        
        for project in projects:
            progress = self.progress_tracker.get_project_progress(project['project_id'])
            if progress:
                total_tasks += progress['total_tasks']
                completed_tasks += progress['completed_tasks']
                in_progress_tasks += progress['in_progress_tasks']
                pending_tasks += progress['pending_tasks']
                overdue_tasks += progress['overdue_tasks']
                
                if progress['total_tasks'] > 0:
                    completion_rates.append(progress['progress_percent'])
        
        avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
        median_completion_rate = self._calculate_median(completion_rates)
        
        results = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'overall_completion_rate': round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0,
            'avg_project_completion_rate': round(avg_completion_rate, 1),
            'median_project_completion_rate': round(median_completion_rate, 1),
            'completion_rate_distribution': self._get_completion_distribution(completion_rates),
            'overdue_rate': round((overdue_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
        }
        
        self.analysis_results['task_completion'] = results
        
        return results

    def _calculate_median(self, values: List[float]) -> float:
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]

    def _get_completion_distribution(self, completion_rates: List[float]) -> Dict[str, int]:
        distribution = {
            '0-25%': 0,
            '26-50%': 0,
            '51-75%': 0,
            '76-100%': 0
        }
        
        for rate in completion_rates:
            if rate <= 25:
                distribution['0-25%'] += 1
            elif rate <= 50:
                distribution['26-50%'] += 1
            elif rate <= 75:
                distribution['51-75%'] += 1
            else:
                distribution['76-100%'] += 1
        
        return distribution

    def analyze_step_effectiveness(self) -> Dict[str, Any]:
        templates = self.template_manager.list_templates()
        
        step_stats = {}
        
        for template in templates:
            for step in template['steps']:
                step_key = f"{template['id']}-{step['step_number']}"
                step_stats[step_key] = {
                    'template_id': template['id'],
                    'template_title': template['title'],
                    'step_number': step['step_number'],
                    'step_title': step['title'],
                    'objectives_count': len(step.get('objectives', [])),
                    'operations_count': len(step.get('operations', [])),
                    'deliverables_count': len(step.get('deliverables', [])),
                    'notes_count': len(step.get('notes', [])),
                    'tools_count': len(step.get('tools', []))
                }
        
        avg_objectives = sum(s['objectives_count'] for s in step_stats.values()) / len(step_stats) if step_stats else 0
        avg_operations = sum(s['operations_count'] for s in step_stats.values()) / len(step_stats) if step_stats else 0
        avg_deliverables = sum(s['deliverables_count'] for s in step_stats.values()) / len(step_stats) if step_stats else 0
        
        results = {
            'total_steps': len(step_stats),
            'avg_objectives_per_step': round(avg_objectives, 1),
            'avg_operations_per_step': round(avg_operations, 1),
            'avg_deliverables_per_step': round(avg_deliverables, 1),
            'step_stats': step_stats,
            'most_detailed_step': self._find_most_detailed_step(step_stats),
            'least_detailed_step': self._find_least_detailed_step(step_stats)
        }
        
        self.analysis_results['step_effectiveness'] = results
        
        return results

    def _find_most_detailed_step(self, step_stats: Dict[str, Any]) -> Optional[str]:
        max_details = 0
        most_detailed = None
        for step_key, stats in step_stats.items():
            details = stats['objectives_count'] + stats['operations_count'] + stats['deliverables_count']
            if details > max_details:
                max_details = details
                most_detailed = step_key
        return most_detailed

    def _find_least_detailed_step(self, step_stats: Dict[str, Any]) -> Optional[str]:
        min_details = float('inf')
        least_detailed = None
        for step_key, stats in step_stats.items():
            details = stats['objectives_count'] + stats['operations_count'] + stats['deliverables_count']
            if details < min_details:
                min_details = details
                least_detailed = step_key
        return least_detailed

    def generate_optimization_suggestions(self) -> List[str]:
        suggestions = []
        
        workflow_usage = self.analyze_workflow_usage()
        task_completion = self.analyze_task_completion()
        step_effectiveness = self.analyze_step_effectiveness()
        
        if workflow_usage['total_projects'] > 0:
            most_used = workflow_usage['most_used_template']
            if most_used:
                suggestions.append(f"模板 '{workflow_usage['template_usage'][most_used]['title']}' 使用最频繁，建议重点优化其流程")
        
        if task_completion['overdue_rate'] > 30:
            suggestions.append(f"逾期率较高 ({task_completion['overdue_rate']}%)，建议重新评估任务时间预估")
        
        if task_completion['overall_completion_rate'] < 50:
            suggestions.append(f"整体完成率较低 ({task_completion['overall_completion_rate']}%)，建议简化工作流步骤")
        
        avg_ops = step_effectiveness['avg_operations_per_step']
        if avg_ops > 30:
            suggestions.append(f"平均每步骤操作数较多 ({avg_ops}个)，建议拆分复杂步骤")
        elif avg_ops < 5:
            suggestions.append(f"平均每步骤操作数较少 ({avg_ops}个)，建议增加详细操作指导")
        
        most_detailed = step_effectiveness['most_detailed_step']
        if most_detailed:
            stats = step_effectiveness['step_stats'][most_detailed]
            suggestions.append(f"步骤 '{stats['step_title']}' 最详细，可作为其他步骤的参考模板")
        
        if not suggestions:
            suggestions.append("当前工作流运行良好，暂无明显优化建议")
        
        return suggestions

    def generate_analysis_report(self) -> str:
        workflow_usage = self.analyze_workflow_usage()
        task_completion = self.analyze_task_completion()
        step_effectiveness = self.analyze_step_effectiveness()
        suggestions = self.generate_optimization_suggestions()
        
        report = f"{'='*70}\n"
        report += f"工作流数据分析报告\n"
        report += f"{'='*70}\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*70}\n\n"
        
        report += f"【工作流使用情况】\n"
        report += f"{'─'*50}\n"
        report += f"总模板数: {workflow_usage['total_templates']}\n"
        report += f"总项目数: {workflow_usage['total_projects']}\n"
        report += f"\n模板使用统计:\n"
        for template_id, usage in workflow_usage['template_usage'].items():
            report += f"  - {usage['title']}: {usage['project_count']} 个项目\n"
        
        report += f"\n【任务完成情况】\n"
        report += f"{'─'*50}\n"
        report += f"总任务数: {task_completion['total_tasks']}\n"
        report += f"已完成: {task_completion['completed_tasks']} ({task_completion['overall_completion_rate']}%)\n"
        report += f"进行中: {task_completion['in_progress_tasks']}\n"
        report += f"待办: {task_completion['pending_tasks']}\n"
        report += f"逾期: {task_completion['overdue_tasks']} ({task_completion['overdue_rate']}%)\n"
        report += f"\n项目完成率分布:\n"
        for range_label, count in task_completion['completion_rate_distribution'].items():
            bar = self._generate_bar(count, 5)
            report += f"  {range_label}: {bar} {count} 个项目\n"
        
        report += f"\n【步骤有效性分析】\n"
        report += f"{'─'*50}\n"
        report += f"总步骤数: {step_effectiveness['total_steps']}\n"
        report += f"平均目标数/步骤: {step_effectiveness['avg_objectives_per_step']}\n"
        report += f"平均操作数/步骤: {step_effectiveness['avg_operations_per_step']}\n"
        report += f"平均产出物数/步骤: {step_effectiveness['avg_deliverables_per_step']}\n"
        
        report += f"\n【优化建议】\n"
        report += f"{'─'*50}\n"
        for i, suggestion in enumerate(suggestions, 1):
            report += f"  {i}. {suggestion}\n"
        
        report += f"\n{'='*70}\n"
        report += f"分析报告结束\n"
        report += f"{'='*70}\n"
        
        return report

    def _generate_bar(self, count: int, max_length: int) -> str:
        bar_length = min(count, max_length)
        return f"{'█'*bar_length}{'░'*(max_length-bar_length)}"