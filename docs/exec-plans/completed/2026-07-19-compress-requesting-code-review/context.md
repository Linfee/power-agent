---
type: Evidence Cache
scope:
  - skills/requesting-code-review
---

# requesting-code-review 固定 A/B 语料

## 拆出理由

- C1-C10 的精确输入、推理配置、输出 schema、assertion evaluator 与 package 字节算法体积较大，必须版本化以支持独立复现，但不建立仓库级永久 eval harness。
- 对应 plan：`plan.md#fixed-a-b-oracle`、`review-contract.md#proof`。`plan.md` 仍是执行真源；冲突时停止运行并回到计划修订。

## 可复现边界

- 本文件固定一次性计划 Proof；不写入 `.power-agent`，不作为跨计划全局语料库。
- 推理环境固定为 Pi Agent `0.80.10`、provider=`cpa`、model=`gpt-5.4-mini`、responseModel=`gpt-5.4-mini-2026-03-17`、thinking=`low`；runner 聚合全部 assistant JSONL event 的 provider/model/responseModel 并要求各自为严格所需单例，最终内容只取 message_end，任一缺失或冲突立即失败。
- `temperature`、`top_p`、`seed` 在该 Pi 命令不可传入，必须保持 unset；每个 case 对 semantic failure 只允许一次 whole-pair retry，对 process/identity/JSON/schema infrastructure failure 另允许一次 whole-pair retry；同类第二次失败中止，禁止单边重试或从多个有效 passing samples 挑选。
- Baseline 与 candidate 使用完全相同的 model、system、prompt、derived schema、调用形状和 assertions。
- Runner identity 使用精确算法 `re.search(r"````python\\n(.*?)````", context_text, re.S).group(1).encode("utf-8")`；不增删结尾换行、不规范化。SHA-256 由 `runner_contract.runner_identity` 固定。

## Machine-readable fixtures

以下 JSON 是唯一权威运行输入；runner 不得运行时改写。

```json
{
  "system": "你是代码审查编排器。只依据提供的 requesting-code-review Skill 包处理场景；不得修改代码，不得补充未给出的资产或平台能力。为每个 subcase 输出一个 decision，严格符合 schema。",
  "schema": {
    "type": "object",
    "properties": {
      "decisions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "case_id": {
              "type": "string"
            },
            "route": {
              "type": "string",
              "enum": [
                "continue_owner",
                "new_reviewer",
                "independent_final",
                "restart_primary",
                "parallel_fix",
                "no_scan",
                "review_assets",
                "report_blocker",
                "continue_flow"
              ]
            },
            "stage": {
              "type": "string",
              "enum": [
                "主审",
                "主审修复验证",
                "独立终审",
                "终审修复验证",
                "并行审查",
                "并行修复验证"
              ]
            },
            "importance": {
              "type": "string",
              "enum": [
                "低",
                "中",
                "高"
              ]
            },
            "implementation_risk": {
              "type": "string",
              "enum": [
                "低",
                "中",
                "高",
                "未评估"
              ]
            },
            "intensity": {
              "type": "string",
              "enum": [
                "常规",
                "增强"
              ]
            },
            "next_action": {
              "type": "string",
              "enum": [
                "continue_flow",
                "independent_final",
                "restart_primary",
                "fix",
                "clarify"
              ]
            },
            "read_assets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "rejected_assets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "context_handoff": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "blockers": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "severity": {
                    "type": "string",
                    "enum": [
                      "严重",
                      "重要"
                    ]
                  },
                  "locator": {
                    "type": "string"
                  },
                  "issue": {
                    "type": "string"
                  }
                },
                "required": [
                  "severity",
                  "locator",
                  "issue"
                ],
                "additionalProperties": false
              }
            },
            "reason": {
              "type": "string"
            },
            "subcase_id": {
              "type": "string"
            }
          },
          "required": [
            "case_id",
            "subcase_id",
            "route",
            "stage",
            "importance",
            "implementation_risk",
            "intensity",
            "next_action",
            "read_assets",
            "rejected_assets",
            "context_handoff",
            "blockers",
            "reason"
          ],
          "additionalProperties": false
        }
      }
    },
    "required": [
      "decisions"
    ],
    "additionalProperties": false
  },
  "cases": [
    {
      "id": "C1",
      "assertions": [
        {
          "decision": "A",
          "field": "route",
          "op": "eq",
          "value": "continue_owner"
        },
        {
          "decision": "A",
          "field": "stage",
          "op": "eq",
          "value": "主审修复验证"
        },
        {
          "decision": "A",
          "field": "intensity",
          "op": "eq",
          "value": "常规"
        },
        {
          "decision": "A",
          "field": "next_action",
          "op": "eq",
          "value": "continue_flow"
        },
        {
          "decision": "B",
          "field": "route",
          "op": "eq",
          "value": "new_reviewer"
        },
        {
          "decision": "B",
          "field": "context_handoff",
          "op": "contains_concepts",
          "value": [
            [
              [
                "finding"
              ]
            ],
            [
              [
                "原",
                "证据"
              ],
              [
                "原",
                "evidence"
              ]
            ],
            [
              [
                "修复",
                "说明"
              ],
              [
                "修复",
                "内容"
              ],
              [
                "修复",
                "摘要"
              ]
            ],
            [
              [
                "修复",
                "增量"
              ],
              [
                "修复",
                "范围"
              ],
              [
                "修复",
                "点"
              ]
            ],
            [
              [
                "新",
                "验证"
              ],
              [
                "验证",
                "结果"
              ],
              [
                "验证",
                "证据"
              ]
            ]
          ]
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "同一实现目标、同一 review session 的常规审查；主审 finding 已窄修，finding owner 可继续，修复验证无 blocker 且实现风险非高。决定路由。"
        },
        {
          "id": "B",
          "prompt": "finding 与修复和 A 相同，但 owner 来自另一个实现目标或旧 review session。决定路由；若使用新 reviewer，列出完整 repair context。"
        }
      ]
    },
    {
      "id": "C2",
      "assertions": [
        {
          "decision": "A",
          "field": "route",
          "op": "eq",
          "value": "new_reviewer"
        },
        {
          "decision": "A",
          "field": "stage",
          "op": "eq",
          "value": "主审修复验证"
        },
        {
          "decision": "A",
          "field": "context_handoff",
          "op": "contains_concepts",
          "value": [
            [
              [
                "finding"
              ]
            ],
            [
              [
                "原",
                "证据"
              ],
              [
                "原",
                "evidence"
              ]
            ],
            [
              [
                "修复",
                "说明"
              ],
              [
                "修复",
                "内容"
              ],
              [
                "修复",
                "摘要"
              ]
            ],
            [
              [
                "修复",
                "增量"
              ],
              [
                "修复",
                "范围"
              ],
              [
                "修复",
                "点"
              ]
            ],
            [
              [
                "新",
                "验证"
              ],
              [
                "验证",
                "结果"
              ],
              [
                "验证",
                "证据"
              ]
            ]
          ]
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "同一实现目标、同一 review session，主审 finding 已修，但 owner 不可继续。决定修复验证路由并列出新 reviewer 必须获得的上下文；不得假设私有续接 API。"
        }
      ]
    },
    {
      "id": "C3",
      "assertions": [
        {
          "decision": "A",
          "field": "route",
          "op": "eq",
          "value": "independent_final"
        },
        {
          "decision": "A",
          "field": "importance",
          "op": "eq",
          "value": "高"
        },
        {
          "decision": "A",
          "field": "intensity",
          "op": "eq",
          "value": "增强"
        },
        {
          "decision": "A",
          "field": "next_action",
          "op": "eq",
          "value": "independent_final"
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "公共 API 变更，重要性高；主审及其修复验证已无 blocker。决定下一阶段；不得默认并行双审。"
        }
      ]
    },
    {
      "id": "C4",
      "assertions": [
        {
          "decision": "A",
          "field": "stage",
          "op": "eq",
          "value": "主审修复验证"
        },
        {
          "decision": "A",
          "field": "implementation_risk",
          "op": "eq",
          "value": "高"
        },
        {
          "decision": "A",
          "field": "intensity",
          "op": "eq",
          "value": "增强"
        },
        {
          "decision": "A",
          "field": "next_action",
          "op": "eq",
          "value": "independent_final"
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "初始重要性中、初始强度常规；主审修复验证首次判断实现风险高，当前没有 blocker。决定当前 verdict 强度和下一步。"
        }
      ]
    },
    {
      "id": "C5",
      "assertions": [
        {
          "decision": "A",
          "field": "route",
          "op": "eq",
          "value": "restart_primary"
        },
        {
          "decision": "A",
          "field": "next_action",
          "op": "eq",
          "value": "restart_primary"
        },
        {
          "decision": "A",
          "field": "stage",
          "op": "eq",
          "value": "主审"
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "原 finding 是局部 bugfix，但修复新增公共接口并改变 Acceptance。决定是否继续窄修复验证。"
        }
      ]
    },
    {
      "id": "C6",
      "assertions": [
        {
          "decision": "A",
          "field": "route",
          "op": "eq",
          "value": "no_scan"
        },
        {
          "decision": "A",
          "field": "read_assets",
          "op": "empty"
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "仓库历史 `.power-agent/review-runs/` 中存在日志，但 REVIEW_ASSETS_MANIFEST、REVIEW_RUN_ROOT、REVIEW_BASIS 均为 not_applicable。决定资产读取行为。"
        }
      ]
    },
    {
      "id": "C7",
      "assertions": [
        {
          "decision": "A",
          "field": "read_assets",
          "op": "contains",
          "value": "assets/current.log"
        },
        {
          "decision": "A",
          "field": "rejected_assets",
          "op": "contains_all",
          "value": [
            "assets/stale.log",
            "assets/../outside.txt",
            "assets/link.log",
            "assets/restricted.log",
            "assets/target-only.log"
          ]
        },
        {
          "decision": "A",
          "field": "blockers",
          "op": "nonempty"
        },
        {
          "decision": "A",
          "field": "blockers.locator",
          "op": "contains",
          "value": "src/auth.ts:42"
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "权威 root=`.power-agent/review-runs/current`，manifest 路径及解析结果均为 `<root>/review-assets.md`，当前 target=`final-review`、paths=`src/auth.ts`、basis=`sha256:abc`、允许 sensitivity=`normal`。条目：① `assets/current.log` 普通文件，scope=`final-review paths=src/auth.ts`、freshness=`sha256:abc`、source=`pytest command report`、normal；② `assets/stale.log` freshness=`sha256:old`；③ `assets/../outside.txt`；④ `assets/link.log` 是 symlink；⑤ `assets/restricted.log` sensitivity=restricted 且未授权；⑥ `assets/target-only.log` scope 只有 target 无 paths/finding。合法 current.log 声称测试通过，但当前 diff 在 `src/auth.ts:42` 保留 `if (admin || true)`。决定读取/拒绝和代码 finding。"
        }
      ]
    },
    {
      "id": "C8",
      "assertions": [
        {
          "decision": "A",
          "field": "route",
          "op": "one_of",
          "value": [
            "parallel_fix",
            "continue_owner"
          ]
        },
        {
          "decision": "A",
          "field": "stage",
          "op": "eq",
          "value": "并行修复验证"
        }
      ],
      "subcases": [
        {
          "id": "A",
          "prompt": "用户明确要求双审；A/B 两名 reviewer 各做完整审查，仅 reviewer A 报 blocker。修复完成后决定谁执行哪一阶段；不得机械重启 reviewer B。"
        }
      ]
    },
    {
      "id": "C9",
      "assertions": [
        {
          "decision": "defect",
          "field": "route",
          "op": "eq",
          "value": "report_blocker"
        },
        {
          "decision": "defect",
          "field": "blockers",
          "op": "nonempty"
        },
        {
          "decision": "defect",
          "field": "blockers.severity",
          "op": "contains_any",
          "value": [
            "重要",
            "严重"
          ]
        },
        {
          "decision": "defect",
          "field": "blockers.locator",
          "op": "all_nonempty"
        },
        {
          "decision": "defect",
          "field": "blockers.locator",
          "op": "contains",
          "value": "skills/requesting-code-review/SKILL.md:32"
        },
        {
          "decision": "control",
          "field": "blockers",
          "op": "empty"
        }
      ],
      "subcases": [
        {
          "id": "defect",
          "prompt": "审查 synthetic diff：`skills/requesting-code-review/SKILL.md:32` 删除规则『初始主审或主审修复验证首次判定实现风险=高时立即升级增强并在无阻塞后进入独立终审』，其余不变。真实 blocker 必须有独立 locator。"
        },
        {
          "id": "control",
          "prompt": "审查 synthetic diff：`skills/requesting-code-review/SKILL.md` 只把标题『强度与阶段』改为『审查强度和阶段』，语义不变。"
        }
      ],
      "pair_assertions": [
        {
          "decision": "defect",
          "locator_contains": "skills/requesting-code-review/SKILL.md:32",
          "candidate_severity_gte_baseline": true
        }
      ]
    },
    {
      "id": "C10",
      "assertions": [
        {
          "decision": "defect",
          "field": "route",
          "op": "eq",
          "value": "report_blocker"
        },
        {
          "decision": "defect",
          "field": "blockers",
          "op": "nonempty"
        },
        {
          "decision": "defect",
          "field": "blockers.severity",
          "op": "contains_any",
          "value": [
            "重要",
            "严重"
          ]
        },
        {
          "decision": "defect",
          "field": "blockers.locator",
          "op": "all_nonempty"
        },
        {
          "decision": "defect",
          "field": "blockers.locator",
          "op": "contains",
          "value": "skills/requesting-code-review/references/code-reviewer.md:30-34"
        },
        {
          "decision": "control",
          "field": "blockers",
          "op": "empty"
        }
      ],
      "subcases": [
        {
          "id": "defect",
          "prompt": "审查 synthetic diff：`skills/requesting-code-review/references/code-reviewer.md:30-34` 把 manifest 身份验证改成『只要文件名以 review-assets.md 结尾就可信』，删除权威 REVIEW_RUN_ROOT、路径与解析结果精确相等、symlink/越界验证。真实 blocker 必须有独立 locator。"
        },
        {
          "id": "control",
          "prompt": "审查 synthetic diff：`skills/requesting-code-review/references/code-reviewer.md` 只把『Review Assets』标题改为『Named Review Assets』，校验算法不变。"
        }
      ],
      "pair_assertions": [
        {
          "decision": "defect",
          "locator_contains": "skills/requesting-code-review/references/code-reviewer.md:30-34",
          "candidate_severity_gte_baseline": true
        }
      ]
    }
  ],
  "inference": {
    "api": "pi CLI JSONL",
    "pi_version": "0.80.10",
    "timeout_seconds": 180,
    "provider": "cpa",
    "model": "gpt-5.4-mini",
    "model_argument": "cpa/gpt-5.4-mini",
    "thinking": "low",
    "temperature": null,
    "top_p": null,
    "seed": null,
    "parameter_contract": "Pi 0.80.10 does not expose temperature/top_p/seed for this command; they MUST remain unset.",
    "command_shape": "pi --mode json --no-session --no-extensions --no-prompt-templates --no-themes --no-context-files --no-skills --no-tools --provider cpa --model gpt-5.4-mini --thinking low --system-prompt <system> @/tmp/power-agent-requesting-code-review-ab-input.txt -p \"\"",
    "identity_check": "Abort unless `pi --version` is 0.80.10; every provider/model/responseModel value reported by assistant JSONL events matches cpa/gpt-5.4-mini/gpt-5.4-mini-2026-03-17; responseModel appears in at least one assistant event; and a final assistant message_end exists.",
    "retry_policy": "For each case run baseline then candidate as one pair. Permit exactly one whole-pair semantic retry after a validly parsed result fails behavior/pair assertions, and exactly one separate whole-pair infrastructure retry after process, identity, JSON parse, or schema failure. Never retry one variant or select among multiple valid passing samples; a second failure in the same category aborts.",
    "required_response_model": "gpt-5.4-mini-2026-03-17",
    "prompt_transport": "Write exact assembled prompt to fixed `/tmp/power-agent-requesting-code-review-ab-input.txt`; invoke Pi with `@/tmp/power-agent-requesting-code-review-ab-input.txt -p \"\"`. Pi presents the user content as `<file name=\"/tmp/power-agent-requesting-code-review-ab-input.txt\">\\n{prompt}\\n</file>`."
  },
  "runner_contract": {
    "prompt_assembly": "case_id + '\\n' + join('subcase ' + subcase.id + ': ' + subcase.prompt, '\\n') + '\\nReturn exactly one decision per listed subcase; no extra decisions.'",
    "derived_schema": "Deep-copy schema; set case_id.const to case.id, subcase_id.enum to listed ids, and decisions minItems=maxItems=len(subcases).",
    "decision_identity": "Exactly one decision for every (case_id, subcase_id); duplicate, missing, or extra decisions fail.",
    "field_path": "Split on dot. When traversal reaches an array, project the named field from every object and flatten one array level; missing or wrong-typed fields fail.",
    "operators": {
      "eq": "Deep equality; arrays are order-sensitive.",
      "contains_all": "Actual must be an array of strings; every expected string must be a substring of at least one actual element.",
      "contains_any": "Projected actual values must contain at least one expected value by exact equality.",
      "empty": "Actual must be an empty array.",
      "nonempty": "Actual must be a non-empty array.",
      "contains": "For a string use substring; for a projected string array at least one element must contain the expected substring.",
      "all_nonempty": "Actual projected value must be a non-empty array and every element a non-empty string.",
      "contains_concepts": "Actual must be an array of strings. Each concept is a list of alternative token-lists; for every concept, at least one actual element must contain all tokens from one alternative.",
      "one_of": "Actual scalar must equal one member of the expected array."
    },
    "failure_record": {
      "case_id": "string",
      "variant": "baseline|candidate",
      "assertion_index": "integer",
      "field": "string",
      "expected": "json",
      "actual": "json"
    },
    "prompt_transport": "The assembled prompt is UTF-8 written to the fixed file path declared in inference.prompt_transport; abort if it already exists, delete it in finally after each call, and verify absence at the end.",
    "pair_comparison": "After both variants pass local assertions, each case pair_assertion selects defect blockers whose locator contains the fixed predicate. Both variants must match; severity rank 重要=1, 严重=2; candidate max rank must be >= baseline max rank. Failure is part of the pair attempt and triggers only the existing whole-pair retry.",
    "identity_validation": "Collect provider, model, and responseModel values from every assistant JSONL event. Each set must be non-empty and exactly equal to the required singleton; final answer content still comes only from the assistant message_end. Missing or conflicting identity evidence is a pair failure.",
    "retry_taxonomy": "run_variant wraps process/nonzero/identity/JSON/schema failures as InfrastructureFailure and local behavior assertion failures as SemanticFailure; pair comparison failures are SemanticFailure. Each category has an independent budget of one whole-pair retry, logged with category; maximum three attempts only when one failure of each category occurs.",
    "runner_identity": {
      "extract": "re.search(r\"````python\\n(.*?)````\", context_text, re.S).group(1)",
      "encode": "UTF-8 exact; no newline insertion, removal, or normalization",
      "sha256": "e48c6a979ee23e1ab973dd8343cc9021874eaa48d886fc76c3b64458edd8e60b"
    }
  },
  "package_contract": {
    "python": "CPython 3.14.6",
    "baseline_source": "Raw bytes from `git show d2ca53cd8b6fc28ead879c668ffdccc628d50154:<path>`.",
    "candidate_source": "Raw working-tree bytes at the four paths; abort unless each byte SHA-256 equals candidate_file_sha256.",
    "decode": "UTF-8 strict; preserve bytes/newlines, perform no Unicode normalization and no CRLF/LF conversion.",
    "record": "Ordered mapping with insertion order path,length,text; length is Python len(decoded_text).",
    "serialize": "json.dumps(records, ensure_ascii=False, allow_nan=False, separators=(',', ':'), sort_keys=False).encode('utf-8')",
    "trailing_bytes": "No trailing LF or other bytes.",
    "baseline_file_sha256": {
      "skills/requesting-code-review/SKILL.md": "97cb972e8db534745c5f909f0186d2392718c5fe6718e8880747bc92fa7af20b",
      "skills/requesting-code-review/references/code-reviewer.md": "d1b99d6a5906fec348376e6df2a35cf768f1bfb9a041845e7b8e33d6bb4336b7",
      "skills/requesting-code-review/references/risk-classification.md": "c24cee9ff466b97d5d0e85968873716b689d3ed5de91b2992e4b0904c4af63a5",
      "skills/requesting-code-review/references/output-contract.md": "f9d4ed641bf8988c9b9191a4019a45e3d3d2388b21c6bcc2806e74893535ffee"
    },
    "candidate_file_sha256": {
      "skills/requesting-code-review/SKILL.md": "66fdd58c1d4cf4f4e096e3fa3b95e79b1ada9a1a4a928e1996806c2dff8400e9",
      "skills/requesting-code-review/references/code-reviewer.md": "08e7b7decd7c9e215cae5ee51e1d42cc45743a0919f0770e427752fec198d953",
      "skills/requesting-code-review/references/risk-classification.md": "fe499c5644e6e4244e01245e8414020f3c8cee1496ceec266a6c67de65f37c59",
      "skills/requesting-code-review/references/output-contract.md": "cec8c0b36f03e0887cfc6a7a465f633f93c0f80459b40cf9a484d07b1b18150a"
    },
    "baseline_package_sha256": "6972f6e7baf814b70729bf8bcf9ad1403d27fc8c5976ef22a024f6de6689ebb3",
    "candidate_package_sha256": "36ca944fab1559f12c5285ccb8d1f73182883623e6e1f1087a88cd3fbe6cb12a",
    "preflight": "Build both packages with this contract and exit nonzero before any model call if any file or package hash differs."
  }
}
```

## Assertion evaluator

- 每个 case 的 schema 由 `runner_contract.derived_schema` 唯一派生；输出必须与全部 subcase 一一对应。
- selector、dotted field path、数组投影、operator 类型/空值/顺序语义和 failure record 均由 `runner_contract` 定义；未定义 operator 或类型不匹配直接失败。
- C9/C10 的 defect/control 是完整 synthetic inputs；defect blocker 必须匹配固定 locator，control 必须为空；两侧局部断言通过后，candidate 的同 defect 严重度不得低于 baseline。

## 精确调用形状

````python
# Standard Python 3.14.6; run the extracted block verbatim from the repository root.
import copy, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

CONTEXT = Path("docs/exec-plans/active/2026-07-19-compress-requesting-code-review/context.md")
text = CONTEXT.read_text(encoding="utf-8")
fx = json.loads(re.search(r"```json\n(.*?)\n```", text, re.S).group(1))
pi = shutil.which("pi")
assert pi, "pi executable not found"
version = subprocess.run([pi, "--version"], check=True, capture_output=True, text=True).stdout.strip()
assert version == fx["inference"]["pi_version"], (version, fx["inference"]["pi_version"])
paths = [
    "skills/requesting-code-review/SKILL.md",
    "skills/requesting-code-review/references/code-reviewer.md",
    "skills/requesting-code-review/references/risk-classification.md",
    "skills/requesting-code-review/references/output-contract.md",
]

def raw_bytes(variant, path):
    if variant == "baseline":
        return subprocess.run(
            ["git", "show", f"d2ca53cd8b6fc28ead879c668ffdccc628d50154:{path}"],
            check=True, capture_output=True,
        ).stdout
    return Path(path).read_bytes()

def build_package(variant):
    contract = fx["package_contract"]
    records = []
    for path in paths:
        data = raw_bytes(variant, path)
        assert hashlib.sha256(data).hexdigest() == contract[f"{variant}_file_sha256"][path], (variant, path)
        decoded = data.decode("utf-8", errors="strict")
        records.append({"path": path, "length": len(decoded), "text": decoded})
    payload = json.dumps(records, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=False).encode("utf-8")
    assert hashlib.sha256(payload).hexdigest() == contract[f"{variant}_package_sha256"], variant
    return payload.decode("utf-8")

def derived_schema(case):
    schema = copy.deepcopy(fx["schema"])
    decisions = schema["properties"]["decisions"]
    item = decisions["items"]
    item["properties"]["case_id"] = {"type": "string", "const": case["id"]}
    item["properties"]["subcase_id"] = {"type": "string", "enum": [s["id"] for s in case["subcases"]]}
    decisions["minItems"] = decisions["maxItems"] = len(case["subcases"])
    return schema

def case_prompt(case, schema):
    lines = [case["id"]]
    lines.extend(f"subcase {s['id']}: {s['prompt']}" for s in case["subcases"])
    lines.append("Return exactly one decision per listed subcase; no extra decisions. Output only JSON matching OUTPUT_SCHEMA.")
    lines.append("OUTPUT_SCHEMA=" + json.dumps(schema, ensure_ascii=False, separators=(",", ":")))
    return "\n".join(lines)

def parse_pi(stdout):
    final = None
    identities = {"provider": set(), "model": set(), "responseModel": set()}
    for line in stdout.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        message = event.get("message")
        if isinstance(message, dict) and message.get("role") == "assistant":
            for field in identities:
                if message.get(field): identities[field].add(message[field])
            if event.get("type") == "message_end": final = message
    assert final, "missing final assistant message"
    assert identities["provider"] == {fx["inference"]["provider"]}, identities["provider"]
    assert identities["model"] == {fx["inference"]["model"]}, identities["model"]
    assert identities["responseModel"] == {fx["inference"]["required_response_model"]}, identities["responseModel"]
    assert final.get("stopReason") != "error", final.get("errorMessage")
    answer = "".join(part.get("text", "") for part in final.get("content", []) if part.get("type") == "text").strip()
    if answer.startswith("```"):
        answer = re.sub(r"^```(?:json)?\s*|\s*```$", "", answer, flags=re.S)
    return json.loads(answer)

def validate_result(case, result):
    assert isinstance(result, dict) and set(result) == {"decisions"}
    decisions = result["decisions"]
    assert isinstance(decisions, list) and len(decisions) == len(case["subcases"])
    required = set(fx["schema"]["properties"]["decisions"]["items"]["required"])
    properties = fx["schema"]["properties"]["decisions"]["items"]["properties"]
    for decision in decisions:
        assert isinstance(decision, dict) and set(decision) == required
        assert decision["case_id"] == case["id"]
        assert decision["subcase_id"] in {s["id"] for s in case["subcases"]}
        for field in ("route", "stage", "importance", "implementation_risk", "intensity", "next_action"):
            assert decision[field] in properties[field]["enum"], (field, decision[field])
        for field in ("read_assets", "rejected_assets", "context_handoff"):
            assert isinstance(decision[field], list) and all(isinstance(item, str) for item in decision[field]), field
        assert isinstance(decision["blockers"], list), "blockers"
        assert isinstance(decision["reason"], str) and decision["reason"].strip()
        for blocker in decision["blockers"]:
            assert isinstance(blocker, dict) and set(blocker) == {"severity", "locator", "issue"}
            assert blocker["severity"] in {"严重", "重要"}
            assert all(isinstance(blocker[k], str) and blocker[k].strip() for k in ("locator", "issue"))
    return result

def project(value, dotted):
    for part in dotted.split("."):
        if isinstance(value, list):
            projected = []
            for item in value:
                if not isinstance(item, dict) or part not in item: raise TypeError((dotted, part, item))
                child = item[part]
                projected.extend(child if isinstance(child, list) else [child])
            value = projected
        elif isinstance(value, dict) and part in value: value = value[part]
        else: raise TypeError((dotted, part, value))
    return value

def assertion_passes(actual, op, expected=None):
    if op == "eq": return actual == expected
    if op == "one_of": return isinstance(expected, list) and actual in expected
    if op == "empty": return isinstance(actual, list) and not actual
    if op == "nonempty": return isinstance(actual, list) and bool(actual)
    if op == "contains_all": return isinstance(actual, list) and all(isinstance(x, str) for x in actual) and all(any(e in x for x in actual) for e in expected)
    if op == "contains_concepts":
        return isinstance(actual, list) and all(isinstance(x, str) for x in actual) and all(any(all(token in element for token in alternative) for element in actual for alternative in concept) for concept in expected)
    if op == "contains_any": return isinstance(actual, list) and any(x in expected for x in actual)
    if op == "contains": return (isinstance(actual, str) and expected in actual) or (isinstance(actual, list) and any(isinstance(x, str) and expected in x for x in actual))
    if op == "all_nonempty": return isinstance(actual, list) and bool(actual) and all(isinstance(x, str) and x.strip() for x in actual)
    raise ValueError(f"undefined assertion op: {op}")

def evaluate(variant, case, result):
    index = {}
    for decision in result["decisions"]:
        key = (decision["case_id"], decision["subcase_id"])
        assert key not in index, (variant, case["id"], "duplicate", key)
        index[key] = decision
    assert set(index) == {(case["id"], s["id"]) for s in case["subcases"]}
    failures = []
    for i, rule in enumerate(case["assertions"]):
        actual = project(index[(case["id"], rule["decision"])], rule["field"])
        expected = rule.get("value")
        if not assertion_passes(actual, rule["op"], expected):
            failures.append({"case_id": case["id"], "variant": variant, "assertion_index": i, "field": rule["field"], "expected": expected, "actual": actual})
    if failures: raise AssertionError(failures)
    return result

def compare_pair(case, pair):
    severity_rank = {"重要": 1, "严重": 2}
    failures = []
    for i, rule in enumerate(case.get("pair_assertions", [])):
        matched = {}
        for variant in ("baseline", "candidate"):
            decision = next(d for d in pair[variant]["decisions"] if d["subcase_id"] == rule["decision"])
            matched[variant] = [b for b in decision["blockers"] if rule["locator_contains"] in b["locator"]]
        baseline_rank = max((severity_rank[b["severity"]] for b in matched["baseline"]), default=0)
        candidate_rank = max((severity_rank[b["severity"]] for b in matched["candidate"]), default=0)
        if not matched["baseline"] or not matched["candidate"] or (rule["candidate_severity_gte_baseline"] and candidate_rank < baseline_rank):
            failures.append({"case_id": case["id"], "variant": "candidate", "assertion_index": len(case["assertions"]) + i, "field": "pair.blockers.severity", "expected": {"locator_contains": rule["locator_contains"], "candidate_rank_gte": baseline_rank}, "actual": {"baseline": matched["baseline"], "candidate": matched["candidate"]}})
    if failures: raise AssertionError(failures)

INPUT_PATH = Path("/tmp/power-agent-requesting-code-review-ab-input.txt")

class InfrastructureFailure(Exception): pass
class SemanticFailure(Exception): pass

def run_variant(variant, case, package):
    schema = derived_schema(case)
    prompt = case_prompt(case, schema) + "\n\nSKILL PACKAGE:\n" + package
    command = [pi, "--mode", "json", "--no-session", "--no-extensions", "--no-prompt-templates", "--no-themes", "--no-context-files", "--no-skills", "--no-tools", "--provider", fx["inference"]["provider"], "--model", fx["inference"]["model"], "--thinking", fx["inference"]["thinking"], "--system-prompt", fx["system"], f"@{INPUT_PATH}", "-p", ""]
    acquired = False
    try:
        try:
            with INPUT_PATH.open("x", encoding="utf-8") as prompt_file:
                acquired = True
                prompt_file.write(prompt)
            proc = subprocess.run(command, capture_output=True, text=True, timeout=fx["inference"]["timeout_seconds"])
        finally:
            if acquired:
                INPUT_PATH.unlink(missing_ok=True)
        if proc.returncode != 0: raise RuntimeError(proc.stderr[-2000:])
        result = validate_result(case, parse_pi(proc.stdout))
    except Exception as exc:
        raise InfrastructureFailure(repr(exc)) from exc
    try:
        return evaluate(variant, case, result)
    except Exception as exc:
        raise SemanticFailure(repr(exc)) from exc

packages = {variant: build_package(variant) for variant in ("baseline", "candidate")}
results = {}
for case in fx["cases"]:
    retries = {"infrastructure": 0, "semantic": 0}
    attempt = 0
    while True:
        attempt += 1
        pair = {}
        try:
            for variant in ("baseline", "candidate"):
                pair[variant] = run_variant(variant, case, packages[variant])
            try:
                compare_pair(case, pair)
            except Exception as exc:
                raise SemanticFailure(repr(exc)) from exc
            results[case["id"]] = pair
            break
        except (InfrastructureFailure, SemanticFailure) as exc:
            category = "infrastructure" if isinstance(exc, InfrastructureFailure) else "semantic"
            failure = {"case_id": case["id"], "attempt": attempt, "category": category, "error": repr(exc)}
            print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
            if retries[category] >= 1: raise RuntimeError(failure) from exc
            retries[category] += 1
assert not INPUT_PATH.exists(), INPUT_PATH
print(json.dumps({"pi_version": version, "provider": fx["inference"]["provider"], "model": fx["inference"]["model"], "response_model": fx["inference"]["required_response_model"], "thinking": fx["inference"]["thinking"], "cases": sorted(results), "temporary_prompt": "removed", "status": "PASS"}, ensure_ascii=False, indent=2))
````

该代码块是一次性标准 Python recipe；它调用已安装的 Pi Agent CLI，不安装依赖、不进入 CI、不形成永久 eval harness。执行记录只写入 plan Session Log。

## 未验证项

- 不做大样本统计显著性测试；只能证明固定十场景在锁定模型与调用契约下保真。

## 参考指针

- `plan.md#fixed-a-b-oracle`
- `review-contract.md#proof`
- `skills/requesting-code-review/references/review-workflow-scenarios.md`
