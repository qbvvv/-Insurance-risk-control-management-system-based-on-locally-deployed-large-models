## 自然语言风控规则的智能化实现（毕业设计工程）

本工程对应论文题目“自然语言风控规则的智能化实现研究”，主要目标：

- 将业务人员用自然语言描述的风控需求（如“同一用户3个月内理赔超过3次则标记为高风险”）自动转换为结构化、可执行的风控规则；
- 利用国内大模型 Qwen-1.8B-Chat（transformers 加载）进行语义理解和逻辑解析；
- 评估生成规则的准确性、可解释性与业务适应性。

### 工程结构

project_root/
- data/                     # 样本数据 & 标注好的自然语言规则→结构化规则
- rules_engine/
  - __init__.py
  - schema.py               # 定义规则中间表示的数据结构（知识表示）
  - rule_executor.py        # 规则执行引擎
- nlp_parser/
  - __init__.py
  - prompt_templates.py     # 大模型提示词模板
  - parser_llm.py           # 调用大模型解析自然语言规则 → 结构化 JSON
  - postprocess.py          # 对 LLM 返回的 JSON 结果校验&修正
- evaluation/
  - __init__.py
  - metrics.py              # 字段级准确率、整体匹配率等指标
  - experiments.py          # 不同配置、不同提示词的实验脚本
- api/
  - __init__.py
  - server.py               # FastAPI 提供 HTTP 接口
- notebooks/
  - exploration.ipynb       # 探索性实验、画图、可视化
- config.py
- requirements.txt
- README.md

### 环境准备

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 下载 Qwen-1.8B-Chat 模型到本地（推荐 ModelScope）：

```powershell
pip install modelscope
modelscope download --model Qwen/Qwen-1_8B-Chat --local_dir ./qwen1.8
```

3. 设置环境变量（示例 PowerShell），指向模型所在目录：

```powershell
$env:QWEN_MODEL_PATH="F:\桌面\保险项目\毕业设计\qwen1.8"
```

也可使用模型 ID 从 ModelScope/HuggingFace 在线加载（需联网）：

```powershell
$env:QWEN_MODEL_PATH="Qwen/Qwen-1_8B-Chat"
```

### 快速使用

- 调用大模型解析规则（Python）：

```python
from nlp_parser.parser_llm import QwenRuleLLMParser

parser = QwenRuleLLMParser(prompt_variant="json_only")
rule_text = "同一用户3个月内理赔超过3次则标记为高风险"
parsed = parser.parse_single_rule_to_dict(rule_text)
print(parsed)
```

- 启动 HTTP 接口（FastAPI）：

```bash
uvicorn api.server:app --reload
```

然后访问 `POST /parse_rule`，输入：

```json
{"rule_text": "同一用户3个月内理赔超过3次则标记为高风险"}
```

即可获得结构化规则 JSON。

