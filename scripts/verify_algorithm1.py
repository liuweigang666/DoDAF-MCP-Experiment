"""
Algorithm 1: DoDAF Viewpoint Selection via Keyword-Weight Mapping
S(vi) = Σ w(vi, k) * f(k, R), select if S(vi) >= theta
"""
import re
from collections import Counter

req_path = r"E:\digital model\wisecity架构_v2.md"
with open(req_path, 'r', encoding='utf-8') as f:
    req_text = f.read()

VP_KW = {
    'AV-1': ['概述','总体','目标','背景','范围'],
    'CV-1': ['能力','构想','愿景','战略'],
    'CV-2': ['能力','分类','层次','概念'],
    'OV-1': ['场景','概念图','高层'],
    'OV-2': ['资源流','接口','数据流','信息流','交换'],
    'OV-4': ['组织','机构','部门','角色','单位'],
    'OV-5b': ['活动','流程','过程','业务','处置'],
    'SV-1': ['系统','组件','接口','连接','模块','交互'],
    'SV-4': ['功能','分解','子系统'],
    'SV-7': ['度量','性能','指标','参数'],
    'SV-9': ['技术','预测','趋势','演进'],
    'DIV-1': ['概念数据','实体','数据模型'],
    'DIV-2': ['逻辑数据','属性','数据结构','数据库'],
    'StdV-1': ['规范','标准','协议','合规'],
    'PV-1': ['项目','组合','规划'],
}

# Keyword extraction
clean = re.sub(r'[#*`\[\]()|~>\n\r]', ' ', req_text)
cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', clean)
counter = Counter(cn_words)
common = set('系统架构模型数据功能管理模块服务应用平台网络技术安全设备接口流程信息业务监控处理分析决策支持实现提供通过进行可以包括使用采用需要能够同时所有相关主要整体各个不同基于构建建立形成覆盖满足符合适配支撑协同联动集成整合统一标准规范')
filtered = [(w, c) for w, c in counter.most_common(200) if w not in common]
total = sum(c for _, c in filtered[:50])
keywords = [(w, c/total) for w, c in filtered[:50]]

print('=== Top 20 Keywords (normalized frequency) ===')
for kw, freq in keywords[:20]:
    print(f'  {kw}: {freq:.4f}')

def compute_w(vi, keyword):
    mappings = VP_KW.get(vi, [])
    for m in mappings:
        if m in keyword or keyword in m:
            return 1.0
    return 0.0

ALL_VP = ['AV-1','AV-2','CV-1','CV-2','CV-3','CV-4','CV-5','CV-6',
    'OV-1','OV-2','OV-3','OV-4','OV-5a','OV-5b','OV-6a','OV-6b','OV-6c',
    'SV-1','SV-2','SV-3','SV-4','SV-5a','SV-5b','SV-6','SV-7','SV-8','SV-9','SV-10a','SV-10b','SV-10c',
    'DIV-1','DIV-2','DIV-3','StdV-1','StdV-2','PV-1','PV-2','PV-3']

scores = {}
for vi in ALL_VP:
    S = sum(compute_w(vi, kw) * freq for kw, freq in keywords)
    scores[vi] = S

sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
print('\n=== Viewpoint Scores S(vi) ===')
for vi, score in sorted_scores[:20]:
    bar = '█' * int(score * 100)
    print(f'  {vi:8s}: {score:.4f} {bar}')

print('\n=== θ Sensitivity Analysis ===')
for theta in [0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25]:
    sel = [vi for vi, s in scores.items() if s >= theta]
    print(f'  θ={theta:.2f}: {len(sel)} VP → {sel[:8]}' + ('...' if len(sel)>8 else ''))

print('\n=== Comparison with Actual Paper Selections ===')
r1 = {'PV-1', 'OV-4', 'CV-2'}
r23 = {'AV-1', 'CV-1', 'CV-2', 'OV-2', 'OV-4', 'OV-5b', 'SV-1', 'SV-4', 'SV-7', 'DIV-1', 'DIV-2', 'StdV-1'}
sel = {vi for vi, s in scores.items() if s >= 0.15}
print(f'  θ=0.15 selected: {sel}')
print(f'  Round 1 actual: {r1}')
print(f'  Rounds 2&3 actual: {r23}')
print(f'  R1 recall: {len(sel & r1)/len(r1):.1%}')
print(f'  R2&3 recall: {len(sel & r23)/len(r23):.1%}')
if sel:
    print(f'  R2&3 precision: {len(sel & r23)/len(sel):.1%}')