# 评测体系

## 数据集格式

JSONL，每一行一个问题及其期望结果：

```json
{"question": "报销流程是什么？", "expected_answer": "提交报销单后由直属上级审批", "expected_doc_ids": ["uuid-of-doc"]}
```

`expected_doc_ids` 用于计算检索召回，`expected_answer` 用于 LLM 裁判判断回答正确性。

## 指标

| 指标 | 说明 |
| --- | --- |
| Recall@K | 引用命中期望文档的比例 |
| Answer Hit | 期望文档是否出现在回答引用的前 K 条 |
| Correct | LLM 裁判判定回答与期望答案语义一致的比例 |
| Avg Latency | 平均端到端耗时 |

## 运行方式

先启动后端并上传评测文档，然后执行：

```bash
python backend/scripts/eval_cli.py backend/data/eval/sample.jsonl \
  --base-url http://localhost:8000 \
  --api-key 你的Key \
  --judge-model gpt-4o-mini
```

输出 JSON 报告与终端汇总。每次修改 Prompt、检索参数或模型后，都应跑一遍回归评测。

## 建议基线

- 初始评测集至少 50 条，覆盖各智能体触发场景。
- Recall@K 低于 0.8 时优先调切片大小、Top K 与重排策略。
- 每条失败样本保存 question、citations、answer，便于人工复核。
