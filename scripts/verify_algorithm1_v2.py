"""
Algorithm 1 v2: TF-IDF weighted keyword extraction
Uses jieba's built-in IDF dictionary (trained on Wikipedia + news corpus)
S(vi) = Σ w(vi, k) * tfidf(k, R), select if S(vi) >= theta
"""
import re, sys, subprocess
from collections import Counter

# Ensure jieba is available
try:
    import jieba
    import jieba.analyse
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'jieba', '-q'])
    import jieba
    import jieba.analyse

req_path = r"E:\digital model\wisecity架构_v2.md"
with open(req_path, 'r', encoding='utf-8') as f:
    req_text = f.read()

# DoDAF viewpoint keyword mappings
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

# TF-IDF extraction using jieba
clean = re.sub(r'[#*`\[\]()|~>\n\r]', ' ', req_text)
# Extract Chinese words (2-4 chars) and compute TF
cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', clean)
counter = Counter(cn_words)

# Load jieba IDF dictionary
idf_dict = {}
try:
    with open(jieba.analyse.idf_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                idf_dict[parts[0]] = float(parts[1])
except:
    pass

# Compute TF-IDF: tfidf = tf * idf (or tf * log(N/df) if no idf dict)
total_words = sum(counter.values())
N = len(counter)  # vocab size as proxy for corpus size

# Additional stopwords for architecture docs
extra_stop = set('系统架构模型数据功能管理模块服务应用平台网络技术安全设备接口流程信息业务监控处理分析决策支持实现提供通过进行可以包括使用采用需要能够同时所有相关主要整体各个不同基于构建建立形成覆盖满足符合适配支撑协同联动集成整合统一标准规范')

tfidf_scores = {}
for word, tf in counter.most_common(500):
    if word in extra_stop:
        continue
    if len(word) < 2:
        continue
    # TF
    tf_norm = tf / total_words
    # IDF: use jieba idf if available, else compute from local stats
    if word in idf_dict:
        idf = idf_dict[word]
    else:
        # fallback: words appearing in many docs get lower IDF
        df = max(1, tf)  # rough proxy
        idf = max(1.0, __import__('math').log(N / (df + 1)))
    tfidf_scores[word] = tf_norm * idf

# Normalize
total_tfidf = sum(tfidf_scores.values())
keywords = [(w, s/total_tfidf) for w, s in sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:50]]

print('=== Top 20 Keywords (TF-IDF normalized) ===')
for kw, freq in keywords[:20]:
    print(f'  {kw}: {freq:.4f}')

def compute_w(vi, keyword):
    for m in VP_KW.get(vi, []):
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

ss = sorted(scores.items(), key=lambda x: x[1], reverse=True)
print('\n=== Viewpoint Scores S(vi) - TF-IDF ===')
for vi, score in ss[:20]:
    bar = '\u2588' * int(score * 100)
    print(f'  {vi:8s}: {score:.4f} {bar}')

print('\n=== \u03b8 Sensitivity Analysis ===')
for theta in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20]:
    sel = [vi for vi, s in scores.items() if s >= theta]
    print(f'  \u03b8={theta:.2f}: {len(sel)} VP \u2192 {sel[:10]}' + ('...' if len(sel)>10 else ''))

print('\n=== Comparison with Paper ===')
r1 = {'PV-1', 'OV-4', 'CV-2'}
r23 = {'AV-1', 'CV-1', 'CV-2', 'OV-2', 'OV-4', 'OV-5b', 'SV-1', 'SV-4', 'SV-7', 'DIV-1', 'DIV-2', 'StdV-1'}

best_theta = None
best_f1 = 0
for theta in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20]:
    sel = {vi for vi, s in scores.items() if s >= theta}
    if not sel:
        continue
    recall = len(sel & r23) / len(r23)
    precision = len(sel & r23) / len(sel)
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) > 0 else 0
    print(f'  \u03b8={theta:.2f}: recall={recall:.1%}, precision={precision:.1%}, F1={f1:.3f}')
    if f1 > best_f1:
        best_f1 = f1
        best_theta = theta

print(f'\n  Best \u03b8={best_theta:.2f} (F1={best_f1:.3f})')