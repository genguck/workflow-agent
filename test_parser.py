import sys
import os

from workflow_parser import WorkflowParser

def test_parse():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    print(f"成功解析 {len(workflows)} 个工作流文档")
    
    for i, workflow in enumerate(workflows):
        print(f"\n{'='*60}")
        print(f"工作流 {i+1}: {workflow['title']}")
        print(f"版本: {workflow['version']}")
        print(f"适用范围: {workflow['scope']}")
        print(f"步骤数: {len(workflow['steps'])}")
        
        for step in workflow['steps']:
            print(f"  - 步骤{step['step_number']}: {step['title']}")
            print(f"    目标数: {len(step['objectives'])}")
            print(f"    操作数: {len(step['operations'])}")
            print(f"    工具数: {len(step['tools'])}")
            print(f"    注意事项数: {len(step['notes'])}")
            print(f"    产出物数: {len(step['deliverables'])}")
            print(f"    模板数: {len(step['templates'])}")
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'workflows.json')
    parser.save_workflows(workflows, output_path)
    print(f"\n工作流数据已保存到: {output_path}")
    
    return len(workflows) == 7

if __name__ == '__main__':
    success = test_parse()
    sys.exit(0 if success else 1)