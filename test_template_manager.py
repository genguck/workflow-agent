import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager


def test_template_manager():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    manager = TemplateManager()
    manager.import_from_workflows(workflows)
    
    stats = manager.get_stats()
    print(f"模板统计: {stats}")
    
    templates = manager.list_templates()
    print(f"\n导入的模板列表 ({len(templates)} 个):")
    for template in templates:
        print(f"  - ID: {template['id']}")
        print(f"    标题: {template['title']}")
        print(f"    版本: {template['version']}")
        print(f"    步骤数: {len(template['steps'])}")
        print(f"    配置: {template.get('config', {})}")
    
    test_id = templates[0]['id']
    test_template = manager.get_template(test_id)
    assert test_template is not None, f"无法获取模板 {test_id}"
    assert test_template['id'] == test_id, "模板ID不匹配"
    print(f"\n测试获取模板: 成功获取模板 {test_id}")
    
    update_result = manager.update_config(test_id, 'default_assignee', '张三')
    assert update_result is True, "更新配置失败"
    updated_template = manager.get_template(test_id)
    assert updated_template['config']['default_assignee'] == '张三', "配置更新未生效"
    print(f"测试更新配置: 成功更新 default_assignee 为 '张三'")
    
    new_template = {
        'title': '测试工作流',
        'version': 'V1.0',
        'scope': '测试团队',
        'steps': []
    }
    new_id = manager.create_template(new_template)
    assert new_id == '测试', f"模板ID生成不正确: {new_id}"
    assert manager.get_template(new_id) is not None, "新模板未保存"
    print(f"测试创建模板: 成功创建模板 {new_id}")
    
    delete_result = manager.delete_template(new_id)
    assert delete_result is True, "删除模板失败"
    assert manager.get_template(new_id) is None, "模板删除未生效"
    print(f"测试删除模板: 成功删除模板 {new_id}")
    
    assert stats['total_templates'] == 7, f"模板数量不正确: {stats['total_templates']}"
    print(f"\n所有测试通过！")
    
    return True


if __name__ == '__main__':
    success = test_template_manager()
    sys.exit(0 if success else 1)