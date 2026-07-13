import os
import re
import json
from typing import Dict, List, Any

class WorkflowParser:
    def __init__(self):
        self.chinese_numerals = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
        self.workflow_patterns = {
            'title': re.compile(r'^(.*工作流|内容创作全流程)\s*$'),
            'version': re.compile(r'文档版本：(.*)$'),
            'scope': re.compile(r'适用范围：(.*)$'),
            'purpose': re.compile(r'文档目的：(.*)$'),
            'update_date': re.compile(r'最后更新：(.*)$'),
            'section': re.compile(r'^([一二三四五六七八九十]+)、(.*)$'),
            'subsection': re.compile(r'^(\d+\.\d+)\s+(.*)$'),
            'step_title': re.compile(r'^[一二三四五六七八九十]+、步骤([一二三四五六七八九十]+)：(.*)$'),
            'step_title_alt': re.compile(r'^步骤([一二三四五六七八九十]+)：(.*)$'),
            'target': re.compile(r'(\d+\.\d+\.\d+)\s+(.*)$'),
            'list_item': re.compile(r'^[-●•*]\s+(.*)$'),
            'table_row': re.compile(r'\|.*\|'),
            'header': re.compile(r'^(#{1,6})\s+(.*)$'),
            'numbered_item': re.compile(r'^(\d+)\.\s+(.*)$'),
            'task_item': re.compile(r'^\[\s*[x ]\s*\]\s+(.*)$'),
            'objectives_section': re.compile(r'^\d+\.\d+\s+目标\s*$'),
            'operations_section': re.compile(r'^\d+\.\d+\s+具体操作\s*$'),
            'tools_section': re.compile(r'^\d+\.\d+\s+工具推荐\s*$'),
            'notes_section': re.compile(r'^\d+\.\d+\s+注意事项\s*$'),
            'deliverables_section': re.compile(r'^\d+\.\d+\s+产出物\s*$'),
            'time_section': re.compile(r'^\d+\.\d+\s+时间预估\s*$'),
            'templates_section': re.compile(r'^\d+\.\d+\s+模板'),
        }
    
    def _chinese_to_number(self, chinese: str) -> int:
        if chinese in self.chinese_numerals:
            return self.chinese_numerals[chinese]
        return 0

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        workflow = {
            'title': '',
            'version': '',
            'scope': '',
            'purpose': '',
            'update_date': '',
            'steps': [],
            'templates': [],
            'tools': [],
            'notes': [],
            'deliverables': [],
            'raw_content': []
        }

        current_step = None
        current_section = None
        current_subsection = None
        current_template = None
        in_template = False
        template_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            workflow['raw_content'].append(line)

            if not workflow['title']:
                match = self.workflow_patterns['title'].match(line)
                if match:
                    workflow['title'] = match.group(1)
                    continue

            match = self.workflow_patterns['version'].match(line)
            if match:
                workflow['version'] = match.group(1)
                continue

            match = self.workflow_patterns['scope'].match(line)
            if match:
                workflow['scope'] = match.group(1)
                continue

            match = self.workflow_patterns['purpose'].match(line)
            if match:
                workflow['purpose'] = match.group(1)
                continue

            match = self.workflow_patterns['update_date'].match(line)
            if match:
                workflow['update_date'] = match.group(1)
                continue

            match = self.workflow_patterns['step_title'].match(line)
            if match:
                step_num = self._chinese_to_number(match.group(1))
                current_step = {
                    'step_number': step_num,
                    'title': match.group(2),
                    'objectives': [],
                    'operations': [],
                    'templates': [],
                    'tools': [],
                    'notes': [],
                    'deliverables': [],
                    'time_estimate': ''
                }
                workflow['steps'].append(current_step)
                continue
            
            match = self.workflow_patterns['step_title_alt'].match(line)
            if match:
                step_num = self._chinese_to_number(match.group(1))
                current_step = {
                    'step_number': step_num,
                    'title': match.group(2),
                    'objectives': [],
                    'operations': [],
                    'templates': [],
                    'tools': [],
                    'notes': [],
                    'deliverables': [],
                    'time_estimate': ''
                }
                workflow['steps'].append(current_step)
                continue

            if current_step:
                match = self.workflow_patterns['subsection'].match(line)
                if match:
                    subsection_num = match.group(1)
                    subsection_title = match.group(2)
                    
                    if '目标' in subsection_title:
                        current_section = 'objectives'
                        continue
                    elif '具体操作' in subsection_title:
                        current_section = 'operations'
                        continue
                    elif '工具推荐' in subsection_title:
                        current_section = 'tools'
                        continue
                    elif '注意事项' in subsection_title:
                        current_section = 'notes'
                        continue
                    elif '产出物' in subsection_title:
                        current_section = 'deliverables'
                        continue
                    elif '时间预估' in subsection_title:
                        current_section = 'time_estimate'
                        continue
                    elif '模板' in subsection_title or '表' in subsection_title:
                        in_template = True
                        template_content = [line]
                        current_template = {'name': subsection_title, 'content': []}
                        continue

                if '模板' in line and ('模板' in line or '表' in line):
                    in_template = True
                    template_content = [line]
                    current_template = {'name': line, 'content': []}
                    continue

                if in_template:
                    if self.workflow_patterns['table_row'].match(line):
                        template_content.append(line)
                        current_template['content'].append(line)
                        continue
                    elif line.startswith('##') or line.startswith('#'):
                        in_template = False
                        if current_template and current_template['content']:
                            current_step['templates'].append(current_template)
                            workflow['templates'].append(current_template)
                        current_template = None
                        template_content = []
                        continue
                    else:
                        template_content.append(line)
                        current_template['content'].append(line)
                        continue

                if line.startswith('-') or line.startswith('●') or line.startswith('•'):
                    item = line[1:].strip()
                    if current_section == 'objectives':
                        current_step['objectives'].append(item)
                    elif current_section == 'operations':
                        current_step['operations'].append(item)
                    elif current_section == 'tools':
                        current_step['tools'].append(item)
                    elif current_section == 'notes':
                        current_step['notes'].append(item)
                    elif current_section == 'deliverables':
                        current_step['deliverables'].append(item)
                    continue

                if line.startswith('[') and ']' in line:
                    item = line[line.index(']')+1:].strip()
                    if item:
                        current_step['deliverables'].append(item)
                    continue

                if current_section == 'time_estimate' and line.strip():
                    current_step['time_estimate'] = line
                    continue

                if current_section == 'objectives' and line.strip():
                    match_num = self.workflow_patterns['numbered_item'].match(line)
                    if match_num:
                        current_step['objectives'].append(match_num.group(2))
                    else:
                        current_step['objectives'].append(line)
                    continue

                if current_section == 'notes' and line.strip():
                    current_step['notes'].append(line)
                    continue

                if current_section == 'operations' and line.strip():
                    match_num = self.workflow_patterns['numbered_item'].match(line)
                    if match_num:
                        current_step['operations'].append(match_num.group(2))
                    else:
                        match_sub = self.workflow_patterns['target'].match(line)
                        if match_sub:
                            current_step['operations'].append(match_sub.group(2))
                        else:
                            current_step['operations'].append(line)
                    continue

        if current_template and current_template['content']:
            if current_step:
                current_step['templates'].append(current_template)
            workflow['templates'].append(current_template)

        workflow['tools'] = list(set([tool for step in workflow['steps'] for tool in step['tools']]))
        workflow['notes'] = list(set([note for step in workflow['steps'] for note in step['notes']]))
        workflow['deliverables'] = list(set([item for step in workflow['steps'] for item in step['deliverables']]))

        return workflow

    def parse_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        workflows = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.txt') and 'workflow' in filename.lower():
                file_path = os.path.join(folder_path, filename)
                workflow = self.parse_file(file_path)
                workflow['filename'] = filename
                workflows.append(workflow)
        return workflows

    def save_workflows(self, workflows: List[Dict[str, Any]], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(workflows, f, ensure_ascii=False, indent=2)

    def load_workflows(self, input_path: str) -> List[Dict[str, Any]]:
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)