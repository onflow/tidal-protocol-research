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
| Self-monitoring for patterns | 1 | 2026-02-20 | When something takes 3+ iterations (docs, code, analysis), extract the pattern into a direction. Don't wait for auditor to point it out. |

## Code Editing

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Comment handling | 1 | 2026-02-20 | Never silently remove comments. Update if still relevant. If a comment block seems entirely obsolete, ask before removing it (can reference specific line ranges). |

## Documentation & Technical Writing

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Self-contained simulation docs | 1 | 2026-02-20 | Technical documentation for audit should ground domain-specific terms (e.g., "rebalancer") in general concepts (e.g., "arbitrageur"), and back mechanical claims with specific parameters or code refs inline. A reader shouldn't need follow-up questions to understand the core narrative. |

## Domain-Specific (this audit)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Progressive abstraction | 1 | 2026-02-03 | Layer details for on-demand deep inspection |
| Minimal invasiveness | 1 | 2026-02-05 | Avoid modifying simulation code; prefer wrappers, orchestration layers, smarter terminal calls |

## Simulation Execution (bash on macOS)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Pre-run analysis | 1 | 2026-02-27 | Before suggesting a run command: (1) count `input()` calls and what each expects, (2) check `sys.path` setup vs venv availability, (3) check config defaults that may contradict prompt behavior |
| Piped input for prompts | 1 | 2026-02-27 | Use `printf` with explicit `\n` per prompt answer (e.g., `printf "\nN\n"` for two prompts). Never `echo ""` for multi-prompt scripts — it only provides one newline |
| Unbuffered + filtered output | 1 | 2026-02-27 | `PYTHONUNBUFFERED=1` for real-time output; `grep --line-buffered -v "DEBUG"` to suppress debug noise while preserving streaming |
| Timestamped descriptive logs | 1 | 2026-02-27 | Always `tee` to `tidal_protocol_sim/results/<descriptive_variant>_$(date +%Y%m%d_%H%M%S).log`. Include scenario variant in filename (e.g., `no_arb_delay`, `moderate`) |
| Virtual environment | 1 | 2026-02-27 | Activate `source /Users/alex/Development/PythonVEs/FlowCreditMarkets/bin/activate` first; run from project root `/Users/alex/Git/tidal-protocol-research`. The venv has `tidal_protocol_sim` as editable install, so `PYTHONPATH=.` is not needed |

## Problem-Specific (current focus)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Track MOET $1 peg instances | 1 | 2026-02-03 | Log to `sims-review/MOET_DOLLAR_PEG_INSTANCES.md` when encountered |


<!-- Direction Change Log removed 2026-02-20: redundant with direction tables above. 
     Rationale/derivation context now lives in each direction's Notes column. -->
