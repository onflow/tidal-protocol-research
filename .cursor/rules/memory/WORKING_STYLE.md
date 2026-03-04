# Working Style Directions

Last updated: 2026-03-02

## Retention and Evaluation

- **Silence ≠ irrelevance.** Absence of corrective feedback means a directive is working — not that it can be dropped.
- **Compaction = generalization, not deletion.** Merge related directives; preserve reinforcement counts and provenance.
- **Archival threshold:** Only narrowly scoped, non-reinforced directives may be archived — never silently removed.
- **Relevance ranking:** Actively assess each directive's breadth. Broad + reinforced = permanent. Narrow + unreinforced = archival candidate.
- **.mdc rules ≠ this file.** `.mdc` files are auto-injected LLM instructions. This file tracks learning dynamics (reinforcement, dates, operational notes). Both are needed — different purposes.
- **Directives are hypotheses.** Every directive (including self-prescribed ones) has an implicit goal. Evaluate whether it's achieving that goal. Self-prescribed processes follow the same confidence scaling as auditor directives: new = experimental, frequently validated = stable. If a directive isn't helping, adapt or replace it — that's not "forgetting," it's learning.
- **Explore in high-impact areas.** Regularly try adapted approaches for tasks that are frequent, time-consuming, or have received corrective feedback. Track what you tried and whether it improved outcomes. Occasional poor performance from a new strategy is acceptable; never exploring is not.

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
| Top-down presentation | 1 | 2026-02-03 | Start general → differentiators → details on demand |
| High information density | 2 | 2026-02-20 | Formulas/pseudo-code over prose; no filler. **No confirmative openers** — just answer. |
| Mutual fallibility | 2 | 2026-03-02 | Both parties err; goal is truth together. Don't pretend confidence. Softened conclusions validated as good practice (2026-03-02). |
| Directive confidence scaling | 1 | 2026-02-03 | Frequent reinforcement → higher compliance; new directives = experimental |
| Proactive engagement | 3 | 2026-03-02 | Most reinforced. Drive progress: present evidence, recognize validation opportunities, confirm compliance |
| Validation gate | 2 | 2026-03-02 | Never mark technical findings `verified` without auditor confirmation; proactively present when evidence sufficient. Positive feedback on proactive ask after complex task (2026-03-02). |
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
| Comment handling | 2 | 2026-03-03 | Never silently remove comments. When rewriting a function body, preserve all existing comments that document intent, assumptions, or non-obvious logic. Update wording only where the old comment contradicts the new code. Stripping comments during a rewrite is the same failure mode as stripping comments during a refactor. |
| Minimal invasiveness | 3 | 2026-03-03 | Modify only the broken part. When fixing a bug in a function, keep the function skeleton (guards, comments, variable names, structure) and replace only the lines that implement the broken behavior. A full rewrite triggers clean-slate thinking that treats existing comments and structure as expendable. **Corollary**: When a fix bypasses code (e.g., removing a swap call), don't also modify the bypassed code — changes to shared infrastructure affect all callers, not just the one you're fixing. Extraordinary changes (removing fail-fast guards, changing error handling strategy) require extraordinary evidence: enumerate all callers, verify impact on each. |

## Git Hygiene

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Clean up checkout artifacts | 1 | 2026-03-02 | After `git checkout <commit> -- <path>` and restoring HEAD, verify no leftover files. `git status --short` immediately after restore. For each suspect file: (1) confirm absent at HEAD, (2) confirm present at old commit, (3) **diff on-disk content against old commit version** — only delete if identical. If the file has local modifications not in any commit, do NOT delete. |

## Simulation Execution (bash on macOS)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Pre-run analysis | 1 | 2026-02-27 | Before run: count `input()` calls, check `sys.path` setup, check config defaults |
| Piped input for prompts | 1 | 2026-02-27 | `printf` with explicit `\n` per prompt. Never `echo ""` for multi-prompt scripts. |
| Unbuffered + filtered output | 1 | 2026-02-27 | `PYTHONUNBUFFERED=1`; `grep --line-buffered -v "DEBUG"` |
| Timestamped descriptive logs | 1 | 2026-02-27 | `tee` to `results/<variant>_$(date +%Y%m%d_%H%M%S).log` |
| Virtual environment | 4 | 2026-02-27 | Venv: `/Users/alex/Development/PythonVEs/FlowCreditMarkets`; cwd: repo root. Don't include venv activation or cd in proposed commands. `tidal_protocol_sim` not editable install — always `PYTHONPATH=.` |

## Exhaustive Claims Require Exhaustive Verification

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Verify universal claims mechanically | 1 | 2026-03-02 | Claims like "X never happens," "zero random draws," or "always the case that..." are exhaustive-coverage claims. Verify them with exhaustive tools (grep, AST search) before presenting. Reasoning alone is insufficient — it's the wrong tool for the job. The auditor cannot tractably verify these; they rely on me to have actually done the exhaustive search. |

**Failure pattern to avoid:** Arriving at an exhaustive claim via high-level reasoning ("the simulation is deterministic, so probably no random draws") without actually verifying exhaustively. This is backwards — use the mechanical tool first, then state the fact.

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
