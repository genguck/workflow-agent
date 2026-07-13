import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_parser import WorkflowParser
from template_manager import TemplateManager
from recommendation_engine import RecommendationEngine


def test_recommendation_engine():
    parser = WorkflowParser()
    workflows = parser.parse_folder(r'C:\Users\Administrator\AI\djhgzl')
    
    manager = TemplateManager()
    manager.import_from_workflows(workflows)
    
    engine = RecommendationEngine(manager)
    
    recs = engine.get_step_recommendations('用户增长', 1)
    assert 'error' not in recs, f"获取推荐失败: {recs.get('error')}"
    assert recs['step_number'] == 1, "步骤号不匹配"
    assert recs['step_title'] == '增长目标与北极星指标设定', "步骤名称不匹配"
    print(f"步骤推荐: {recs['step_title']}")
    print(f"  注意事项数: {len(recs['notes'])}")
    print(f"  相关工具: {recs['related_tools']}")
    print(f"  最佳实践: {recs['best_practices']}")
    
    overview = engine.get_template_overview('用户增长')
    assert 'error' not in overview, f"获取模板概览失败: {overview.get('error')}"
    assert overview['total_steps'] == 7, f"步骤数不正确: {overview['total_steps']}"
    assert 'estimated_total_time' in overview, "缺少预估时间"
    print(f"\n模板概览: {overview['title']}")
    print(f"  总步骤: {overview['total_steps']}")
    print(f"  预估总时间: {overview['estimated_total_time']}")
    
    search_results = engine.search_recommendations('数据分析')
    assert len(search_results) > 0, "搜索结果应为正数"
    print(f"\n搜索'数据分析'结果 ({len(search_results)} 条):")
    for result in search_results[:3]:
        print(f"  - {result['template_title']} 步骤{result['step_number']}: {result['step_title']} (相关度: {result['relevance']})")
    
    search_results = engine.search_recommendations('营销')
    assert len(search_results) > 0, "搜索结果应为正数"
    print(f"\n搜索'营销'结果 ({len(search_results)} 条):")
    for result in search_results[:3]:
        print(f"  - {result['template_title']} 步骤{result['step_number']}: {result['step_title']} (相关度: {result['relevance']})")
    
    print("\n所有测试通过！")
    
    return True


if __name__ == '__main__':
    success = test_recommendation_engine()
    sys.exit(0 if success else 1)