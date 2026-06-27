# DoDAF-MCP-Experiment

Experimental data and reproduction scripts for the paper:

**"An LLM-Driven MCP Framework for Automated DoDAF-Compliant Architecture Model Generation: A Case Study on Smart City Emergency Systems"**

> Submitted to IEEE Access

## Repository Contents

```
├── README.md
├── requirements/
│   └── smart_city_emergency_requirements.md    # Natural language requirement document
├── scripts/
│   ├── verify_algorithm1.py                    # Algorithm 1: TF-based keyword-weight mapping
│   └── verify_algorithm1_v2.py                 # Algorithm 1 v2: TF-IDF weighted keyword extraction
├── data/
│   ├── baseline_comparison.md                  # P2 Baseline: MCP vs CSV import comparison
│   ├── model_stats.csv                         # Element statistics by DoDAF viewpoint
│   └── ea_model_export.xml                     # EA model export (XMI 1.1 format)
```

## Experiment Overview

Three rounds of experiments were conducted using DeepSeek-V4 as the LLM backend. The Smart City Emergency Command System served as the case study, with the following key metrics:

| Metric | Value |
|--------|-------|
| LLM Backend | DeepSeek-V4 |
| Temperature (generation) | 0.3 |
| Temperature (weight matrix) | 0.0 (deterministic) |
| Avg. pipeline time | 4 min 50 s |
| MCP tool calls | 61.3 per round |
| Tool-call reliability | 100% (184 invocations, 0 failures) |
| Avg. SysML diagrams | 9.0 per session |
| Expert-assessed correctness | 92.3% (post-verification) |

## Reproduction

### Prerequisites
- Python 3.10+
- jieba (for Algorithm 1 v2)
- The EAMCP (Enterprise Architect MCP Server) source code is not publicly released due to institutional restrictions.

### Running Algorithm 1

```bash
# TF-based version
python scripts/verify_algorithm1.py

# TF-IDF version
python scripts/verify_algorithm1_v2.py
```

### Baseline Comparison

See `data/baseline_comparison.md` for the detailed comparison between MCP-based generation and the CSV/PlantUML text-based baseline approach.

## Data Availability Statement

The natural language requirement document, complete experimental data (tool call traces, Verifier reports, and ablation study results), and analyzed metrics are provided in this repository.

## Citation

If you use this data in your research, please cite:

```
Liu, W., Peng, B., Wen, B., Yan, Z., Gao, X., Pei, Y., Tian, J., & Zhang, R.
"An LLM-Driven MCP Framework for Automated DoDAF-Compliant Architecture Model Generation."
IEEE Access, 2026.
```

## License

This experimental data is provided for research reproducibility purposes. The EAMCP source code is not publicly released.