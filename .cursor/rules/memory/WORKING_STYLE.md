# Working Style Directions

Last updated: 2026-02-27

## Auditor Profile

- Computer scientist, experienced software engineer
- In-depth Python and data science expertise
- Some economics background
- Familiar with Cursor IDE

**Calibration**: Skip basic Python/data science explanations. Can handle mathematical notation. Economics concepts may need grounding in code.

## Communication

Directions that emerged from interaction. Baseline principles (mutual fallibility, proactive engagement, validation gate, generalization awareness, directive confidence scaling) live in `01-audit-interaction.mdc` and `00-memory-system.mdc` — not duplicated here.

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Top-down, high density | 2 | 2026-02-20 | Formulas/pseudo-code over prose; no filler. **No confirmative openers** — just answer. Start general → differentiators → details on demand. |
| Proactive engagement | 3 | 2026-02-07 | Most reinforced direction. Actively drive progress: present evidence, recognize validation opportunities, confirm direction compliance on important applications. |
| Punctuation style | 1 | 2026-02-20 | Prefer "e.g." / "i.e." over em-dashes for inline clarifications. |
| Self-contained docs | 1 | 2026-02-20 | Audit docs should ground domain terms in general concepts (e.g., "rebalancer" → "arbitrageur") and back claims with parameters/code refs inline. Reader shouldn't need follow-up questions. |

## Code Editing

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Comment handling | 1 | 2026-02-20 | Never silently remove comments. Update if still relevant. If a comment block seems entirely obsolete, ask before removing (can reference specific line ranges). |
| Minimal invasiveness | 1 | 2026-02-05 | Avoid modifying simulation code; prefer wrappers, orchestration layers, smarter terminal calls |

## Simulation Execution (bash on macOS)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Pre-run analysis | 1 | 2026-02-27 | Before suggesting a run command: (1) count `input()` calls and what each expects, (2) check `sys.path` setup vs venv availability, (3) check config defaults that may contradict prompt behavior |
| Piped input for prompts | 1 | 2026-02-27 | Use `printf` with explicit `\n` per prompt answer (e.g., `printf "\nN\n"` for two prompts). Never `echo ""` for multi-prompt scripts — it only provides one newline |
| Unbuffered + filtered output | 1 | 2026-02-27 | `PYTHONUNBUFFERED=1` for real-time output; `grep --line-buffered -v "DEBUG"` to suppress debug noise while preserving streaming |
| Timestamped descriptive logs | 1 | 2026-02-27 | Always `tee` to `tidal_protocol_sim/results/<descriptive_variant>_$(date +%Y%m%d_%H%M%S).log`. Include scenario variant in filename |
| Virtual environment | 4 | 2026-02-27 | Venv: `/Users/alex/Development/PythonVEs/FlowCreditMarkets`; cwd: `/Users/alex/Git/tidal-protocol-research`. Use internally for verification. **Do NOT include venv activation or cd in proposed commands** — auditor handles standard setup. Only include deviations (e.g., `PYTHONPATH=.`) if required. **`tidal_protocol_sim` is NOT an editable install** — always set `PYTHONPATH=.` |

## Simulation Reproduction Debugging

When investigating "why does the script not reproduce the claimed results?", apply in order.
Concrete examples of each step: → `sims-review/FCM_PRIMER_FIGURE_MAPPING.md` (D6–D8).

| Step | Principle | Rationale |
|------|-----------|-----------|
| 1. Establish the gap | Run as committed; quantify divergence vs claim before reading code | Prevents premature hypothesizing |
| 2. Config history first | Check version control history of config/constants before investigating logic | Most mismatches are a changed constant, not a logic rewrite |
| 3. Full-diff suspect commits | Catalog ALL diffs in each suspect commit; don't trust the message | Opaque commits routinely bundle unrelated behavioral changes |
| 4. Audit default-dependent gates | Sampling/frequency gates work for their original use case; ask "does every consumer set this?" | A default tuned for one scenario silently breaks others frequently |
| 5. Comment–value mismatch = flag | Stale or wrong comment on a recently changed value signals haste or intent | Heuristic for what aspects to investigate further |
| 6. Trace rendering bugs upstream | Broken chart → data retrieval → data generation; the visual symptom is rarely the root cause | Heuristic for what aspects to investigate further |

## Problem-Specific (current focus)

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Track MOET $1 peg instances | 1 | 2026-02-03 | Log to `sims-review/MOET_DOLLAR_PEG_INSTANCES.md` when encountered. Initial scan done; keep noting new occurrences. |
