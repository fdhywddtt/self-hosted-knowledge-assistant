"""对黄金问答集运行评测。

用法: python scripts/eval_cli.py data/eval/sample.jsonl
"""

import argparse
import asyncio
import json
from pathlib import Path

import httpx


def load_dataset(path: Path) -> list[dict]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


async def judge_answer(
    client: httpx.AsyncClient,
    question: str,
    answer: str,
    expected: str,
    base_url: str,
    api_key: str,
    model: str,
) -> bool:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是评测裁判。判断模型回答与标准答案是否语义一致，只返回 yes 或 no。",
            },
            {
                "role": "user",
                "content": f"问题：{question}\n标准答案：{expected}\n模型回答：{answer}\n是否一致？",
            },
        ],
        "temperature": 0,
    }
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    response = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip().lower()
    return content.startswith("yes")


async def run(args) -> None:
    dataset = load_dataset(Path(args.dataset))
    results: list[dict] = []
    async with httpx.AsyncClient(timeout=300) as client:
        for item in dataset:
            question = item["question"]
            started = asyncio.get_event_loop().time()
            headers = {"X-API-Key": args.api_key} if args.api_key else None
            response = await client.post(
                f"{args.base_url.rstrip('/')}/api/v1/chat",
                json={"question": question},
                headers=headers,
            )
            response.raise_for_status()
            latency = asyncio.get_event_loop().time() - started
            body = response.json()

            hit_docs = {citation["document_id"] for citation in body.get("citations", [])}
            expected_docs = set(item.get("expected_doc_ids", []))
            recall = len(hit_docs & expected_docs) / len(expected_docs) if expected_docs else 1.0

            correct = None
            if args.judge_model:
                correct = await judge_answer(
                    client,
                    question,
                    body.get("answer", ""),
                    item.get("expected_answer", ""),
                    args.judge_base_url,
                    args.judge_api_key,
                    args.judge_model,
                )

            results.append(
                {
                    "question": question,
                    "agent_name": body.get("agent_name", ""),
                    "answer": body.get("answer", ""),
                    "recall": recall,
                    "correct": correct,
                    "latency": round(latency, 2),
                    "citations": body.get("citations", []),
                }
            )

    avg_recall = sum(item["recall"] for item in results) / len(results)
    avg_latency = sum(item["latency"] for item in results) / len(results)
    judged = [item for item in results if item["correct"] is not None]
    correct_rate = sum(item["correct"] for item in judged) / len(judged) if judged else None

    summary = {
        "total": len(results),
        "avg_recall": round(avg_recall, 4),
        "avg_latency": avg_latency,
        "correct_rate": round(correct_rate, 4) if correct_rate is not None else None,
    }
    output = {"summary": summary, "results": results}
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.output:
        Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="知识库问答评测")
    parser.add_argument("dataset", help="JSONL 评测集路径")
    parser.add_argument("--base-url", default="http://localhost:8000", help="后端服务地址")
    parser.add_argument("--api-key", default="", help="开启鉴权后的 API Key")
    parser.add_argument("--output", default="", help="报告输出路径")
    parser.add_argument("--judge-model", default="", help="LLM 裁判模型，留空则跳过")
    parser.add_argument("--judge-base-url", default="https://api.openai.com/v1")
    parser.add_argument("--judge-api-key", default="")
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
