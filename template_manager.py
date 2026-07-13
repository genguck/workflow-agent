import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class TemplateManager:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.data_dir = data_dir
        self.templates_file = os.path.join(data_dir, 'templates.json')
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_templates(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)

    def import_from_workflows(self, workflows: List[Dict[str, Any]]):
        for workflow in workflows:
            template_id = self._generate_template_id(workflow['title'])
            template = {
                'id': template_id,
                'title': workflow['title'],
                'version': workflow.get('version', 'V1.0'),
                'scope': workflow.get('scope', ''),
                'purpose': workflow.get('purpose', ''),
                'update_date': workflow.get('update_date', datetime.now().strftime('%Y-%m-%d')),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'steps': workflow.get('steps', []),
                'templates': workflow.get('templates', []),
                'tools': workflow.get('tools', []),
                'notes': workflow.get('notes', []),
                'deliverables': workflow.get('deliverables', []),
                'config': {
                    'default_assignee': '',
                    'default_timezone': 'Asia/Shanghai',
                    'notification_enabled': True
                }
            }
            self.templates[template_id] = template
        self._save_templates()

    def _generate_template_id(self, title: str) -> str:
        normalized = title.replace('工作流', '').replace('流程', '').strip()
        if not normalized:
            normalized = 'workflow'
        return normalized.lower().replace(' ', '-').replace('_', '-')

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        return self.templates.get(template_id)

    def list_templates(self) -> List[Dict[str, Any]]:
        return list(self.templates.values())

    def create_template(self, template_data: Dict[str, Any]) -> str:
        template_id = template_data.get('id') or self._generate_template_id(template_data['title'])
        template_data['id'] = template_id
        template_data['created_at'] = datetime.now().isoformat()
        template_data['updated_at'] = datetime.now().isoformat()
        template_data['config'] = template_data.get('config', {
            'default_assignee': '',
            'default_timezone': 'Asia/Shanghai',
            'notification_enabled': True
        })
        self.templates[template_id] = template_data
        self._save_templates()
        return template_id

    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        if template_id not in self.templates:
            return False
        template = self.templates[template_id]
        template.update(updates)
        template['updated_at'] = datetime.now().isoformat()
        self._save_templates()
        return True

    def delete_template(self, template_id: str) -> bool:
        if template_id not in self.templates:
            return False
        del self.templates[template_id]
        self._save_templates()
        return True

    def update_config(self, template_id: str, config_key: str, config_value: Any) -> bool:
        if template_id not in self.templates:
            return False
        self.templates[template_id]['config'][config_key] = config_value
        self.templates[template_id]['updated_at'] = datetime.now().isoformat()
        self._save_templates()
        return True

    def get_stats(self) -> Dict[str, int]:
        total = len(self.templates)
        total_steps = sum(len(t['steps']) for t in self.templates.values())
        total_tools = sum(len(t['tools']) for t in self.templates.values())
        total_templates = sum(len(t['templates']) for t in self.templates.values())
        return {
            'total_templates': total,
            'total_steps': total_steps,
            'total_tools': total_tools,
            'total_sub_templates': total_templates
        }