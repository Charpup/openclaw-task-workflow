# Humanizer Skill 统一构建 — Task Plan

## Batch 1 — 项目初始化
- [x] T1: Fork blader/humanizer → Charpup/humanizer
- [x] T2: 创建项目目录

## Batch 2 — 素材提取
- [x] T3: Clone fork 到本地
- [x] T4: 提取 EN SKILL.md 到工作笔记（559行）
- [x] T5: 提取 ZH SKILL.md 到工作笔记（484行）
- [x] T6: 整理 Wikipedia 模式研究

## Batch 3 — 核心合并
- [x] T7: 构建 32 模式合并分类体系（含置信度分层 + 组合检测原则）

## Batch 4 — 参考文件编写
- [x] T8: patterns-full.md（235行，32模式完整定义）
- [x] T9: ai-vocab-en.md（49行）
- [x] T10: ai-vocab-zh.md（51行）
- [x] T11: scoring-rubric.md（62行，5维度×10分）
- [x] T12: voice-calibration.md（62行）

## Batch 5 — 主文件起草
- [x] T13: SKILL.md 主体（158行，远低于400行预算）

## Batch 6 — 示例与测试
- [x] T14: before-after 示例（EN + ZH）
- [x] T15: evals.json（4个测试用例）

## Batch 7 — skill-creator 迭代
- [x] T16: 跳过（skill 已被 Claude Code 识别，直接进冒烟测试）

## Batch 8 — 部署与 PR
- [x] T17: 结构验证通过 + 冒烟测试输入已准备
- [x] T18: 安装 skill（写入 ~/.claude/skills/humanizer/ 时自动完成）
- [x] T19: PR 分支推送到 Charpup/humanizer feat/quality-scoring-and-wiki-patterns

## Batch 9 — 提交与归档
- [x] T20: PR 提交 → blader/humanizer#94
- [ ] T21: /summarize 归档
