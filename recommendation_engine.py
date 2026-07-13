import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class RecommendationEngine:
    def __init__(self, template_manager):
        self.template_manager = template_manager
        self.recommendation_logs = []

    def get_step_recommendations(self, template_id: str, step_number: int) -> Dict[str, Any]:
        template = self.template_manager.get_template(template_id)
        if not template:
            return {'error': f"模板 {template_id} 不存在"}
        
        step = None
        for s in template['steps']:
            if s['step_number'] == step_number:
                step = s
                break
        
        if not step:
            return {'error': f"步骤 {step_number} 不存在"}
        
        recommendations = {
            'template_id': template_id,
            'template_title': template['title'],
            'step_number': step_number,
            'step_title': step['title'],
            'tools': step.get('tools', []),
            'notes': step.get('notes', []),
            'templates': step.get('templates', []),
            'objectives': step.get('objectives', []),
            'deliverables': step.get('deliverables', []),
            'time_estimate': step.get('time_estimate', ''),
            'related_tools': self._get_related_tools(step),
            'best_practices': self._extract_best_practices(step)
        }
        
        self._log_recommendation(template_id, step_number, 'step')
        
        return recommendations

    def _get_related_tools(self, step: Dict[str, Any]) -> List[str]:
        common_tools = {
            '调研': ['问卷星', '问卷网', '麦客表单', '金数据'],
            '分析': ['Excel', 'Python', 'SQL', 'Tableau', 'Power BI'],
            '设计': ['Figma', 'Sketch', 'Adobe Photoshop', 'Canva'],
            '写作': ['Notion', '飞书文档', 'Google Docs', 'Markdown'],
            '沟通': ['飞书', '钉钉', '企业微信', 'Zoom'],
            '项目管理': ['Jira', 'Trello', '飞书项目', 'PingCode'],
            '数据分析': ['百度统计', 'Google Analytics', 'GrowingIO', '神策数据'],
            '营销': ['巨量引擎', '微信广告', '百度推广', '腾讯广告'],
            '用户增长': ['Mixpanel', 'Amplitude', 'Heap', 'Leanplum']
        }
        
        tools = []
        step_text = f"{step['title']} {' '.join(step.get('objectives', []))} {' '.join(step.get('operations', []))}"
        
        for keyword, keyword_tools in common_tools.items():
            if keyword in step_text:
                tools.extend(keyword_tools)
        
        return list(set(tools))

    def _extract_best_practices(self, step: Dict[str, Any]) -> List[str]:
        practices = []
        
        if step.get('notes'):
            for note in step['notes']:
                if len(note) > 10:
                    practices.append(note)
        
        objectives = step.get('objectives', [])
        if objectives:
            practices.append(f"核心目标: {objectives[0]}")
        
        if step.get('time_estimate'):
            practices.append(f"建议用时: {step['time_estimate']}")
        
        return practices

    def search_recommendations(self, keyword: str) -> List[Dict[str, Any]]:
        results = []
        templates = self.template_manager.list_templates()
        
        for template in templates:
            for step in template['steps']:
                step_text = f"{step['title']} {' '.join(step.get('objectives', []))} {' '.join(step.get('operations', []))} {' '.join(step.get('notes', []))}"
                
                if keyword.lower() in step_text.lower():
                    results.append({
                        'template_id': template['id'],
                        'template_title': template['title'],
                        'step_number': step['step_number'],
                        'step_title': step['title'],
                        'relevance': self._calculate_relevance(keyword, step_text),
                        'notes': step.get('notes', []),
                        'tools': step.get('tools', []),
                        'objectives': step.get('objectives', [])[:3]
                    })
        
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        self._log_recommendation('search', keyword, 'keyword')
        
        return results[:10]

    def _calculate_relevance(self, keyword: str, text: str) -> float:
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        
        exact_matches = text_lower.count(keyword_lower)
        partial_matches = sum(1 for word in text_lower.split() if keyword_lower in word)
        
        return exact_matches * 2 + partial_matches

    def get_template_overview(self, template_id: str) -> Dict[str, Any]:
        template = self.template_manager.get_template(template_id)
        if not template:
            return {'error': f"模板 {template_id} 不存在"}
        
        overview = {
            'id': template['id'],
            'title': template['title'],
            'version': template['version'],
            'scope': template['scope'],
            'purpose': template['purpose'],
            'total_steps': len(template['steps']),
            'total_tools': len(template.get('tools', [])),
            'total_notes': len(template.get('notes', [])),
            'steps_summary': [],
            'estimated_total_time': self._estimate_total_time(template)
        }
        
        for step in template['steps']:
            overview['steps_summary'].append({
                'step_number': step['step_number'],
                'title': step['title'],
                'objectives_count': len(step.get('objectives', [])),
                'operations_count': len(step.get('operations', [])),
                'deliverables_count': len(step.get('deliverables', [])),
                'time_estimate': step.get('time_estimate', '')
            })
        
        return overview

    def _estimate_total_time(self, template: Dict[str, Any]) -> str:
        total_days = 0
        for step in template['steps']:
            import re
            match = re.search(r'(\d+)', step.get('time_estimate', ''))
            if match:
                total_days += int(match.group(1))
            else:
                total_days += 3
        
        if total_days < 7:
            return f"{total_days}天"
        elif total_days < 30:
            weeks = total_days // 7
            days = total_days % 7
            return f"{weeks}周{days}天"
        else:
            months = total_days // 30
            days = total_days % 30
            return f"{months}个月{days}天"

    def _log_recommendation(self, template_id: str, step_number: int, type: str):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': type,
            'template_id': template_id,
            'step_number': step_number
        }
        self.recommendation_logs.append(log_entry)
        
        if len(self.recommendation_logs) > 100:
            self.recommendation_logs = self.recommendation_logs[-100:]