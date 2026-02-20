# Working Style Directions

Last updated: 2026-02-20

## Auditor Profile

- Computer scientist, experienced software engineer
- In-depth Python and data science expertise
- Some economics background
- Familiar with Cursor IDE

**Calibration**: Skip basic Python/data science explanations. Can handle mathematical notation. Economics concepts may need grounding in code.

## General (apply broadly)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Top-down presentation | 1 | 2026-02-03 | Start general, then differentiators, then details |
| High information density | 2 | 2026-02-20 | Formulas/pseudo-code over prose; no filler. **No confirmative openers** ("Good question", "I'd be happy to help", etc.) — just answer. Actions over filler. |
| Mutual fallibility | 1 | 2026-02-03 | Both parties err; goal is truth together |
| Directive confidence scaling | 1 | 2026-02-03 | Frequent reinforcement → higher compliance |
| Proactive engagement | 3 | 2026-02-07 | Don't be passive; actively drive progress (direction compliance + finding evidence + recognizing validation opportunities) |
| Validation gate for memory | 1 | 2026-02-07 | Never mark technical findings as `verified` without auditor confirmation; proactively present findings when evidence is sufficient |
| Generalization awareness | 1 | 2026-02-03 | Apply directions at appropriate generality level |
| Punctuation style | 1 | 2026-02-20 | Prefer "e.g." / "i.e." over em-dashes for inline clarifications. Use em-dashes sparingly. |

## Code Editing

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Comment handling | 1 | 2026-02-20 | Never silently remove comments. Update if still relevant. If a comment block seems entirely obsolete, ask before removing it (can reference specific line ranges). |

## Domain-Specific (this audit)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Progressive abstraction | 1 | 2026-02-03 | Layer details for on-demand deep inspection |
| Minimal invasiveness | 1 | 2026-02-05 | Avoid modifying simulation code; prefer wrappers, orchestration layers, smarter terminal calls |

## Problem-Specific (current focus)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Track MOET $1 peg instances | 1 | 2026-02-03 | Log to `sims-review/MOET_DOLLAR_PEG_INSTANCES.md` when encountered |

---

## Direction Change Log

| Date | Direction | Change | Rationale |
|------|-----------|--------|-----------|
| 2026-02-03 | (all) | Initial creation | System bootstrap from setup conversation |
| 2026-02-07 | Proactive engagement | Reinforced (+1), added "recognizing validation opportunities" sub-case | Auditor corrected: I should have asked for validation before committing HF rebalancing findings to memory |
| 2026-02-07 | Validation gate for memory | New direction | Technical findings must be confirmed by auditor before marking verified in memory |
| 2026-02-20 | High information density | Reinforced (+1) | No confirmative openers or filler phrases; concise when needed, thorough when it matters |
| 2026-02-20 | Punctuation style | New direction | Fewer em-dashes; prefer "e.g." / "i.e." for inline clarifications |
| 2026-02-20 | Comment handling | New direction | Don't silently remove comments; update or ask before deleting |
