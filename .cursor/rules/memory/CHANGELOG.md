# Memory System Changelog

On-demand provenance record. Tracks structural changes to the memory system and directive lifecycle. Not read at session start — consulted during self-evaluation or when investigating why a directive was added/changed/lost.

## Directive Lifecycle

| Date | Directive | Event | Notes |
|------|-----------|-------|-------|
| 2026-02-03 | Top-down presentation | Added | Genesis: start general → differentiators → details |
| 2026-02-03 | High information density | Added | Genesis: formulas/pseudo-code over prose |
| 2026-02-03 | Mutual fallibility | Added | Genesis: both parties err; goal is truth together |
| 2026-02-03 | Directive confidence scaling | Added | Genesis: frequent reinforcement → higher compliance |
| 2026-02-03 | Proactive engagement | Added | Genesis: actively drive progress |
| 2026-02-03 | Generalization awareness | Added | Genesis: apply directions at appropriate generality |
| 2026-02-03 | Progressive abstraction | Added | Genesis: layer details for on-demand inspection |
| 2026-02-03 | Track MOET $1 peg instances | Added | First problem-specific directive |
| 2026-02-05 | Minimal invasiveness | Added | Avoid modifying simulation code |
| 2026-02-07 | Proactive engagement | Reinforced (+2) | Auditor corrected: should have asked for validation proactively. Added "recognizing validation opportunities" sub-case. |
| 2026-02-07 | Validation gate | Added | Technical findings need auditor confirmation before `verified` status |
| 2026-02-20 | High information density | Reinforced (+1) | No confirmative openers; actions over filler |
| 2026-02-20 | Punctuation style | Added | Prefer "e.g."/"i.e." over em-dashes |
| 2026-02-20 | Self-monitoring for patterns | Added | 3+ iteration signal → extract pattern proactively |
| 2026-02-20 | Self-contained docs | Added | Ground domain terms; back claims with params/code refs inline |
| 2026-02-20 | Comment handling | Added | Never silently remove comments |
| 2026-02-20 | Direction Change Log | Removed | Deemed redundant with direction tables. **Post-mortem: this removal lost provenance info.** |
| 2026-02-27 | Simulation Execution (5 directives) | Added | Pre-run analysis, piped input, unbuffered output, timestamped logs, virtual environment |
| 2026-02-27 | Simulation Reproduction Debugging (6-step) | Added | Pattern extracted from FCM Primer reproduction failures |
| 2026-02-27 | Mutual fallibility, Directive confidence scaling, Validation gate, Generalization awareness, Progressive abstraction, Self-monitoring | Dropped ⚠️ | Incorrectly removed during "compaction" — deemed redundant with `.mdc` rules. Actually lost tracking metadata. |
| 2026-02-27 | System Evolution Log | Dropped ⚠️ | Removed from SESSION_LOG during restructure |
| 2026-02-28 | All dropped directives | Restored | After auditor flagged the loss. Retention Policy added to prevent recurrence. |
| 2026-02-28 | Document Authoring (5 directives) | Added | Terminology/nomenclature rules for audit documents |
| 2026-02-28 | Retention Policy | Added | "Silence ≠ irrelevance"; compaction = generalization not deletion |
| 2026-02-28 | CHANGELOG.md | Created | Provenance file rebuilt from git history to prevent future information loss |
| 2026-03-02 | Mutual fallibility | Reinforced (+1) | Auditor reinforced transparent self-correction under uncertainty about own records |
| 2026-03-02 | Proactive engagement | Reinforced (+1) | Positive feedback on proactive validation ask after complex task. Now at 3 reinforcements. |
| 2026-03-02 | Validation gate | Reinforced (+1) | Positive feedback on proactive ask. Now at 2 reinforcements. |
| 2026-03-02 | Verify universal claims mechanically | Added | Exhaustive-coverage claims require exhaustive tools (grep, AST), not reasoning alone |
| 2026-03-02 | Clean up checkout artifacts | Added | After `git checkout <commit> -- <path>`, diff against old commit before deleting |

## Structural Changes

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-02-03 | System created | 4 memory files + 3 `.mdc` rule files |
| 2026-02-06 | First validated finding in CONCLUSIONS.md | Discrepancy check bug |
| 2026-02-07 | Validation gate added to `.mdc` rules | Process correction: committed finding without sign-off |
| 2026-02-20 | SESSION_LOG compacted | Entropy management: snippets over prose, refs over copies |
| 2026-02-20 | Active retrieval directive added to `00-memory-system.mdc` | Memory must be proactively consulted at session start |
| 2026-02-20 | "Principles over recollections" rule added | Directions should state principles, not the specific case that motivated them |
| 2026-02-27 | Audit State living summary added to SESSION_LOG top | Reduces session-start orientation time |
| 2026-02-27 | CONCLUSIONS.md restructured | Added "Evidence-Supported" tier between unverified and validated |
| 2026-02-27 | WORKING_STYLE.md compacted ⚠️ | Dropped 6 directives + provenance log. Identified as over-aggressive on 2026-02-28. |
| 2026-02-28 | WORKING_STYLE.md restructured | Restored directives, added Retention Policy, Core Principles section, Memory Organization section |
| 2026-02-28 | Retention Policy added to `00-memory-system.mdc` | Strengthened "Manage entropy" rule against silent deletion |
| 2026-02-28 | CHANGELOG.md created | On-demand provenance file to prevent future loss of tracking metadata |
| 2026-02-28 | Memory Maintenance Protocol added to `00-memory-system.mdc` | Procedural checklist for safe compaction; compaction must be deliberate, not a side effect |
| 2026-02-28 | Session-start health check added to Active Retrieval | Brief evaluation alongside reading: unfamiliar items? size changes? stale entries? |
| 2026-02-28 | "Split" added to Evolution Operations | Prefer splitting to topic files over pruning when content grows |

## Meta-Learnings

Generalized patterns from recurring failures or corrections. These are higher-level than individual directives — they apply across the memory system.

| Learning | Date | Source |
|----------|------|--------|
| **Don't confuse different purposes that share content.** `.mdc` rules instruct the LLM; `WORKING_STYLE.md` tracks learning dynamics. Both may contain similar text, but removing one doesn't substitute for the other. Generalization: before deduplicating, verify both instances serve the SAME purpose. | 2026-02-28 | 2026-02-27 compaction failure |
| **Absence of signal ≠ absence of importance.** A directive with no recent corrections is working, not irrelevant. A simulation that doesn't crash isn't necessarily correct. A number that seems plausible isn't verified. Apply broadly. | 2026-02-28 | Retention Policy discussion |
| **Compaction as a side effect is dangerous.** Memory maintenance should be a deliberate, isolated activity with its own checklist — not something done while editing a file for another purpose. | 2026-02-28 | Root cause analysis of 2026-02-27 failure |
| **Accumulation vs pruning is a persistent tension.** Neither extreme works. The resolution is structural: split into topic files rather than pruning; generalize rather than delete; track provenance so losses can be detected and recovered. | 2026-02-28 | Auditor feedback on recurring pattern |
| **Directives are hypotheses, not laws.** Every prescribed process (self-created or auditor-given) has an implicit goal. Without tracking the goal, you can't evaluate effectiveness. New directives are experimental; confidence grows through validated use, not just through absence of complaint. Self-prescribed processes follow the same confidence curve as auditor directives. | 2026-02-28 | Auditor meta-feedback on experimentation |
| **Retention ≠ rigidity.** The Retention Policy protects against amnesia (losing working directives). But it must not prevent adaptation (changing approaches that aren't working). "Don't drop" and "do evaluate and adapt" are complementary, not contradictory — they apply to different situations. Distinguish: retiring a directive because it's inconvenient (bad) vs. replacing it with a better approach for the same goal (good). | 2026-02-28 | Self-reflection on tension between Retention Policy and experimentation |

## Identified Technical Debt

| Item | Priority | Notes |
|------|----------|-------|
| `.mdc` reinforcement counts drift | Low | Synced 2026-03-02 (Top-down 1→2, Info density 1→2, Proactive 2→3). Root cause remains: `.mdc` and WORKING_STYLE.md duplicate counts. Consider removing counts from `.mdc` and referencing WORKING_STYLE.md as sole source of truth in a future iteration. |

## Self-Evaluation Triggers

Read this file when:
- Compacting or reorganizing memory files (check: am I about to repeat the 2026-02-27 mistake? follow Maintenance Protocol)
- A directive seems unfamiliar (check: was it dropped? when was it added? what motivated it?)
- Periodic self-evaluation (is the system serving its purpose? are directives being followed?)
- Starting a session after intensive technical work (check: did last session generate learnings that should be organized?)

fooo