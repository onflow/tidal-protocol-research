# Working Style Directions

Last updated: 2026-02-28

## Retention Policy

- **Silence ≠ irrelevance.** Absence of corrective feedback means a directive is working — not that it can be dropped.
- **Compaction = generalization, not deletion.** Merge related directives; preserve reinforcement counts and provenance.
- **Archival threshold:** Only narrowly scoped, non-reinforced directives may be archived — never silently removed.
- **Relevance ranking:** Actively assess each directive's breadth. Broad + reinforced = permanent. Narrow + unreinforced = archival candidate.
- **.mdc rules ≠ this file.** `.mdc` files are auto-injected LLM instructions. This file tracks learning dynamics (reinforcement, dates, operational notes). Both are needed — different purposes.

## Auditor Profile

- Computer scientist, experienced software engineer
- In-depth Python and data science expertise
- Some economics background
- Familiar with Cursor IDE

**Calibration**: Skip basic Python/data science explanations. Can handle mathematical notation. Economics concepts may need grounding in code.

## Core Principles

Foundational directives from genesis and early interaction. Also encoded in `.mdc` rules — tracked here for reinforcement dynamics and regression prevention.

| Principle | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Top-down presentation | 2 | 2026-02-20 | Start general → differentiators → details on demand |
| High information density | 2 | 2026-02-20 | Formulas/pseudo-code over prose; no filler. **No confirmative openers** — just answer. |
| Mutual fallibility | 1 | 2026-02-03 | Both parties err; goal is truth together. Don't pretend confidence. |
| Directive confidence scaling | 1 | 2026-02-03 | Frequent reinforcement → higher compliance; new directives = experimental |
| Proactive engagement | 3 | 2026-02-07 | Most reinforced. Drive progress: present evidence, recognize validation opportunities, confirm compliance |
| Validation gate | 1 | 2026-02-07 | Never mark technical findings `verified` without auditor confirmation; proactively present when evidence sufficient |
| Generalization awareness | 1 | 2026-02-03 | Apply directions at appropriate generality level |
| Progressive abstraction | 1 | 2026-02-03 | Layer algorithmic details for on-demand deep inspection. Distinct from top-down: this is about making multiple depth levels *available*, not about presentation order. |
| Self-monitoring for patterns | 1 | 2026-02-20 | When something takes 3+ iterations (docs, code, analysis), extract the pattern into a direction. Don't wait for auditor to point it out. |

## Communication Style

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Punctuation style | 1 | 2026-02-20 | Prefer "e.g."/"i.e." over em-dashes for inline clarifications |
| Self-contained docs | 1 | 2026-02-20 | Audit docs ground domain terms in general concepts (e.g., "rebalancer" → "arbitrageur") and back claims with params/code refs inline. Reader shouldn't need follow-up questions. |

## Document Authoring

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Assume only standard knowledge | 1 | 2026-02-28 | Finance, CS, Python terms OK. Never assume conversation-local terminology is known by the reader. |
| Terminology introduction threshold | 1 | 2026-02-28 | Only when central + repeated + cognitive cost justified vs inline prose. Must reference where introduced. |
| No conflicting nomenclature | 1 | 2026-02-28 | Avoid terms requiring extra disambiguation effort, even if technically distinguishable |
| Ask before introducing terms | 1 | 2026-02-28 | Default to asking auditor before new nomenclature in docs. Observe agreement/disagreement patterns, generalize. |
| Conversation-local labels stay local | 1 | 2026-02-28 | Shorthand from conversation → prose in audit docs (`sims-review/`) |

### Internal classifications (not for audit documents)

For discrepancy analysis, I track two kinds of findings:
- **Post-delivery changes**: Code modified after the Primer was generated, causing current output to diverge. Revert to reproduce.
- **Pre-existing bugs**: Present when the Primer was generated. Fix independently of reproduction.

## Code Editing

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Comment handling | 1 | 2026-02-20 | Never silently remove comments. Update if still relevant. Ask before removing obsolete blocks. |
| Minimal invasiveness | 1 | 2026-02-05 | Avoid modifying simulation code; prefer wrappers, orchestration layers, smarter terminal calls |

## Simulation Execution (bash on macOS)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Pre-run analysis | 1 | 2026-02-27 | Before run: count `input()` calls, check `sys.path` setup, check config defaults |
| Piped input for prompts | 1 | 2026-02-27 | `printf` with explicit `\n` per prompt. Never `echo ""` for multi-prompt scripts. |
| Unbuffered + filtered output | 1 | 2026-02-27 | `PYTHONUNBUFFERED=1`; `grep --line-buffered -v "DEBUG"` |
| Timestamped descriptive logs | 1 | 2026-02-27 | `tee` to `results/<variant>_$(date +%Y%m%d_%H%M%S).log` |
| Virtual environment | 4 | 2026-02-27 | Venv: `/Users/alex/Development/PythonVEs/FlowCreditMarkets`; cwd: repo root. Don't include venv activation or cd in proposed commands. `tidal_protocol_sim` not editable install — always `PYTHONPATH=.` |

## Simulation Reproduction Debugging

When investigating "why does the script not reproduce the claimed results?", apply in order.
→ Examples: `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` (D6–D9).

| Step | Principle | Rationale |
|------|-----------|-----------|
| 1. Establish the gap | Run as committed; quantify divergence vs claim before reading code | Prevents premature hypothesizing |
| 2. Config history first | Check version control history of config/constants before logic | Most mismatches are a changed constant, not a logic rewrite |
| 3. Full-diff suspect commits | Catalog ALL diffs in each suspect commit; don't trust the message | Opaque commits routinely bundle unrelated behavioral changes |
| 4. Audit default-dependent gates | Ask "does every consumer set this?" for sampling/frequency defaults | A default tuned for one scenario silently breaks others |
| 5. Comment–value mismatch = flag | Stale or wrong comment on a recently changed value | Heuristic for further investigation |
| 6. Trace rendering bugs upstream | Broken chart → data retrieval → data generation | Visual symptom rarely = root cause |

## Problem-Specific (current focus)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Track MOET $1 peg instances | 1 | 2026-02-03 | Log to `sims-review/MOET_DOLLAR_PEG_INSTANCES.md`. Initial scan done; keep noting. |

## Memory Organization

**File structure:**

| File | Purpose | Read at session start? |
|------|---------|----------------------|
| `WORKING_STYLE.md` | Master catalog of all directives + tracking | Yes — scan for task-relevant sections |
| `SESSION_LOG.md` | Audit state, session records, open questions | Yes — top (audit state) + recent entries |
| `TECHNICAL.md` | Domain knowledge: formulas, algorithms, code map | When doing technical work |
| `CONCLUSIONS.md` | Validated/invalidated findings | When revisiting findings |
| `CHANGELOG.md` | Provenance of directive and structural changes | During self-evaluation or compaction |

**Scaling principle:** When a topic accumulates enough depth that detailed guidance doesn't fit in a table row here, create a dedicated file in `memory/` and reference it from this index. This file remains the master catalog. Creating new files and subdirectories in `memory/` is explicitly permitted and encouraged when it improves retrieval.
