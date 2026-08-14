# DeepSeek V4 Compatibility Lab

[English](README.md) | 中文

这是一个给 DeepSeek V4 客户端集成用的小型兼容实验仓库。它刻意把三件事分开：

| 问题 | 用什么检查 |
| --- | --- |
| 请求和流有没有拼对？ | 本仓库的离线 fixtures |
| 模型选工具、填参数、串联工具的能力怎样？ | 固定版本的 `tool-eval-bench` |
| 推理服务有多快？ | `tool-eval-bench bench --perf` |

没有调用模型，就不会发布模型分数；离线 fixtures 也不会冒充 benchmark。

## 跑离线套件

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync --locked --all-groups
uv run dsv4-compat-lab run --check
```

[当前矩阵](MATRIX.md)有 9 个小案例：thinking / non-thinking 工具循环、漏传 `reasoning_content`、孤立和未完成的工具结果、strict schema、交错的流式 tool call、被截断的参数，以及损坏的 SSE。

每个 fixture 的 SHA-256 都写在[机器结果](results/offline.json)里，底层检查器固定到 [DeepSeek Protocol Doctor](https://github.com/Whning0513/deepseek-protocol-doctor) 的具体 commit。

## 可选的真实工具能力测试

下面只打印固定版本命令，不会发请求：

```bash
uv run python scripts/live_tool_eval.py
```

只有显式加 `--execute` 且设置 `DEEPSEEK_API_KEY` 才会产生真实、可能计费的 API 调用。比较结果前先看[运行说明](docs/tool-eval-bench.md)。当前 recipe 明确关闭 thinking，因为固定版本的上游 benchmark 还没有把 `reasoning_content` 写回多轮工具历史。

## 当前采用的官方信息

`lab.lock.json` 记录了 2026-08-14 核对的官方文档：

- API base URL 仍是 `https://api.deepseek.com`；
- 当前模型名是 `deepseek-v4-pro` 和 `deepseek-v4-flash`；
- 旧的 `deepseek-chat`、`deepseek-reasoner` 已在 2026-07-24 退役；
- thinking 默认开启，thinking 工具调用轮次必须原样回传 `reasoning_content`。

来源：[V4 发布说明](https://api-docs.deepseek.com/news/news260424)、[Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode)、[Tool Calls](https://api-docs.deepseek.com/guides/tool_calls)。

## 加一条客户端案例

先脱敏，再把案例缩到最小。新增 fixture 后，在 `cases/manifest.json` 写出预期的稳定 finding code，然后运行：

```bash
uv run dsv4-compat-lab run --write
uv run pytest
```

不要提交真实 prompt、客户数据、密钥，也不要为了通过检查去改写 `reasoning_content`。真实分数要附原始 benchmark 报告和完整配置，不能只摘一个总分。

MIT License。第三方社区项目，不是 DeepSeek 官方组件。
