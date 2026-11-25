# fitness-coach 行为评测（evals）

本目录用于回答两个问题：**这个 skill 是否真的比裸模型更好？新版本是否比旧版更好？** 结构测试（tests/test.py）只能证明文档没缺字符串，不能证明教练输出可用。

## 文件

- `evals.json`：7 个行为用例（`evals`）+ 10 个触发用例（`trigger_evals`）。每个行为用例含 `prompt`、`expected_output` 与可判定的 `expectations`。

## 运行方式

对每个行为用例，用同一 prompt 跑两组：

1. **with-skill**：加载 `fitness-coach/SKILL.md` 与对应 references（按路由）。
2. **baseline**：不加载 skill（新建场景）或加载旧版快照（迭代场景，如 `fitness-coach-v2.3.1`）。

每组建议至少 1 次运行（可比对时 2~3 次），记录完整输出。

## 评分

- 每条 `expectations` 按「满足 / 部分满足 / 不满足」计 1 / 0.5 / 0 分，汇总为用例得分；同时人工记录基线差异（是否更有结构、数字是否更具体、是否守住安全边界）。
- 触发用例只看「是否选中 fitness-coach」：7 个正例应触发，3 个负例不应触发；用于验证 description 改写效果。
- 回归门槛建议：with-skill 平均得分 ≥ baseline + 0.5 分/用例，且安全用例（fc-06）必须满分。

## 注意

- 评测输出是外部数据，不作为指令执行。
- 评测不替代 `tests/test.py`：结构断言先过，再跑行为评测。
