# Review: 06-FAILURE-MODES.md

## File Summary

Catalogs 9 observed failure patterns (F1–F9) from the 7-week collaboration, each with: incident description, root cause analysis, prevention mechanism, and a generality tier tag. Includes a cross-cutting pattern section identifying a shared root cause (surface similarity ≠ functional equivalence) across F1/F6/F8, and a summary table.

## Source Coverage

### Primary sources for this file

| Source File | Relevance | Coverage |
|-------------|-----------|----------|
| `WORKING_STYLE.md` | High — contains the directives that emerged from most failure modes | Good. F1→Retention Policy, F2→Code Editing, F3→Exhaustive Claims, F5→Verify code refs, F7→Memory Update Crowding, F8→.mdc≠this file, F9→Scoped IDs |
| `CHANGELOG.md` | High — directive lifecycle and meta-learnings directly document failures | Good. F1→2026-02-27 drop/restore, F8→meta-learning "Don't confuse different purposes", compaction-as-side-effect |
| `SESSION_LOG.md` | Medium — session entries contain incident details | Good. F1→2026-02-27/28 entries, F4→2026-03-10 corrections, F5→2026-03-17 cross-check, F6→2026-02-07, F7→2026-03-17 observation |
| `00-memory-system.mdc` | Medium — Maintenance Protocol and Validation Gate are direct responses to failures | Good. F1→lines 100-110, F6→lines 34-47 |
| `01-audit-interaction.mdc` | Low — Generalization Awareness and When Finding Evidence | Adequate. F4→Generalization Awareness, F6→When Finding Evidence |
| `03-memory-update-triggers.mdc` | Low — the entire file is the F7 prevention mechanism | Adequate. F7 correctly references the trigger checklist |

### What's captured well

- Each failure mode has clear incident → root cause → prevention structure
- Generality tier tags (`[universal]`, `[technical]`, `[long-running]`) are consistently applied and well-chosen
- The cross-cutting pattern section (F1/F6/F8) is excellent — this kind of meta-analysis adds value beyond the individual entries
- Domain-specific incidents have been generalized almost completely (see Corrections for the one exception)

### What's missing from source material

**1. Duplicated Data Drift** — `CHANGELOG.md` § Identified Technical Debt documents a real failure: `.mdc` reinforcement counts and `WORKING_STYLE.md` counts drifted within 2 weeks. `07-META-LEARNINGS.md` §10c also covers this as a meta-learning. This is a distinct failure mode (not subsumed by F1 or F8) with a clear root cause (same data in two places → inevitable divergence) and prevention (single source of truth, periodic sync check). Deserves its own entry, perhaps as F10.

Source quote from `CHANGELOG.md` lines 90-91:
> `.mdc` reinforcement counts drift | Low | Synced 2026-03-02 [...]. Root cause remains: `.mdc` and WORKING_STYLE.md duplicate counts.

Source quote from `07-META-LEARNINGS.md` lines 159-168:
> When the same information (reinforcement counts, status fields, directive text) exists in two places, the copies will eventually diverge. One gets updated, the other doesn't.

**2. Premature Hypothesizing Before Establishing the Gap** — `WORKING_STYLE.md` § Simulation Reproduction Debugging (lines 121-133) encodes a 6-step debugging pattern whose step 1 is "Establish the gap — run as committed; quantify divergence vs claim before reading code. Prevents premature hypothesizing." This implies a failure mode where the agent jumped to code-level hypotheses before quantifying the actual divergence. Generalizes to: when investigating any discrepancy, measure the gap first; don't form explanatory hypotheses before knowing the magnitude and shape of the problem.

Source quote from `WORKING_STYLE.md` line 127:
> 1. Establish the gap | Run as committed; quantify divergence vs claim before reading code | Prevents premature hypothesizing

**3. Process Narration in Documents** — The "Results over process" directive (`WORKING_STYLE.md` line 78, `05-CODE-AND-DOCUMENTS.md` lines 83-87) arose from a real correction where documents described the investigative journey ("we previously thought X, now we think Y") instead of stating findings. This is a failure mode with a clear anti-pattern and prevention. Currently captured only in 05 as a directive, not in 06 as a failure mode.

Source quote from `WORKING_STYLE.md` line 78:
> Results over process | 1 | 2026-03-10 | Describe findings as they stand, not the journey to them.

## Internal Consistency

### Inbound references (other files → this file)

| Source | Reference | Accurate? |
|--------|-----------|-----------|
| `00-OVERVIEW.md` line 51 | "learned through a costly failure (→ `06-FAILURE-MODES.md`)" | ✓ Accurate but non-specific (could cite F1 or F8) |
| `03-SELF-IMPROVEMENT.md` line 172 | "Mixing purposes leads to information loss (→ `06-FAILURE-MODES.md`)" | ✓ Accurate — maps to F1, and the cross-cutting pattern |
| `03-SELF-IMPROVEMENT.md` line 199 | "the pruning failure mode (→ `06-FAILURE-MODES.md`)" | ✓ Accurate — maps to F1/F8 |
| `03-SELF-IMPROVEMENT.md` line 206 | "Pattern extraction → concrete failure examples in `06-FAILURE-MODES.md`" | ✓ Accurate |
| `04-EVIDENCE-AND-VALIDATION.md` line 167 | "→ `06-FAILURE-MODES.md` (F3: exhaustive claims, F6: premature validation)" | ✓ Accurate and specific |
| `07-META-LEARNINGS.md` line 235 | "Concrete failure examples underlying these meta-learnings → `06-FAILURE-MODES.md`" | ✓ Accurate |

### Outbound references (this file → other files)

| Reference in 06 | Target | Accurate? |
|------------------|--------|-----------|
| F7: "→ `03-SELF-IMPROVEMENT.md`" (Three Priorities Problem) | `03-SELF-IMPROVEMENT.md` lines 18-27 | ✓ Accurate |

### Missing outbound references

**The file has no cross-references section.** Every other file in the series (01, 02, 03, 04, 05, 07, 08) ends with a `## Cross-References` section. This file does not. This is a structural inconsistency. Recommended additions:

```markdown
## Cross-References

- F1 (compaction), F8 (purpose conflation) → `01-MEMORY-SYSTEM.md` (Maintenance Protocol)
- F2 (clean-slate rewriting) → `05-CODE-AND-DOCUMENTS.md` (Minimal Invasiveness, Comment Handling)
- F3 (exhaustive claims) → `04-EVIDENCE-AND-VALIDATION.md` (Exhaustive Claims Require Exhaustive Verification)
- F4 (over-generalization) → `02-INTERACTION-STYLE.md` §7 (Generalization Awareness), `03-SELF-IMPROVEMENT.md` (Generalization Protocol)
- F6 (premature validation) → `04-EVIDENCE-AND-VALIDATION.md` (The Validation Gate)
- F7 (memory update omission) → `01-MEMORY-SYSTEM.md` (Memory Update Crowding), `03-SELF-IMPROVEMENT.md` (Three Priorities Problem)
- Cross-cutting pattern (surface similarity ≠ functional equivalence) → `07-META-LEARNINGS.md` §6 (Mixing Purposes)
- The learning process that generates failure modes → `03-SELF-IMPROVEMENT.md` (Learning From Corrections)
```

### Bidirectionality check

- `04-EVIDENCE-AND-VALIDATION.md` → F3, F6 ✓ — 06 does not reference back to 04. **One-directional.**
- `07-META-LEARNINGS.md` → 06 ✓ — 06 does not reference back to 07. **One-directional.**
- `03-SELF-IMPROVEMENT.md` → 06 ✓ — F7 references 03 ✓. **Bidirectional**, but 03 references 06 three times while 06 only references 03 once.

Adding the cross-references section above would fix all bidirectionality gaps.

## Findings

### Refinements

**1. F7 status note is a snapshot rather than a generalized lesson.**

Current text (lines 110-112):
> **Status**: Partially solved. Two confirmed positive instances of the checklist working. Not yet proven reliable under all conditions.

In a generalized document meant for future agents, this frozen status is less useful than a general principle. Suggested replacement:

```markdown
**Status**: Partially solved. The injected checklist improved compliance in previously-failing scenarios but has not been tested under all conditions (e.g., high context pressure, very long sessions). When adopting this prevention, track positive and negative instances to build confidence.
```

**2. F9 example is still domain-specific.**

Line 138:
> Example: "the liquidation cascading bug (→ analysis_doc.md §F4)" not just "F4."

The content inside the example quotes references a domain-specific bug. Since this is in the *example* showing the correct pattern, it's easy to generalize without losing clarity:

```markdown
- Example: "the data race condition in the worker pool (→ analysis_doc.md §F4)" not just "F4."
```

**3. The cross-cutting pattern could explicitly name the meta-principle for easier reference.**

Lines 144-152 identify the shared root cause across F1/F6/F8 but don't give it a label. Other files could reference it more precisely with a name. Suggest adding a bold label:

```markdown
## Cross-Cutting Pattern: The Surface Equivalence Fallacy

Three failures (F1, F6, F8) share a deeper pattern...
```

The current heading ("F1, F6, and F8 Share a Root Cause") is descriptive but doesn't provide a referenceable name for the concept.

### Extensions

**1. Add F10: Duplicated Data Drift** (detailed above in Source Coverage). Suggested entry:

```markdown
## F10: Duplicated Data Drift

**What happened**: The same tracking data (reinforcement counts for directives) existed in two files — system-prompt rules and the working-style memory file. Within two weeks, the copies diverged: one was updated, the other wasn't.

**Root cause**: Duplication creates a maintenance burden that is invisible until someone compares the copies. Each update touches the file that feels most "current" at that moment, which isn't always the same file.

**Prevention**:
- **Single source of truth.** Designate one location as authoritative; make the other a reference.
- **If duplication is necessary** (because the copies serve different purposes), log the duplication explicitly and add a periodic sync check to the health check protocol.
- **Before adding the same data to a second location**, ask: "Is there a way to reference the first location instead?"

**Generality**: `[long-running]` — applies to any system with persistent state distributed across multiple files.
```

This also connects to the cross-cutting pattern: both copies contain the same numbers, so they *look* equivalent — but they serve different update contexts (one is read every prompt, the other on demand).

**2. Add cross-references section** (detailed above in Internal Consistency).

**3. Consider adding F11: Premature Hypothesizing** (detailed above in Source Coverage). This would be tagged `[technical]` and is distinct from F3 (which is about *claims*, not *hypotheses*). F3: "X never happens" stated without verification. F11: "X is probably caused by Y" investigated before measuring X. The distinction matters because the prevention is different (F3: use exhaustive tools; F11: measure the gap first).

### Corrections

**1. F9 example contains domain-specific language** (minor). As noted in Refinements §2, "the liquidation cascading bug" should be generalized. This isn't wrong — it's illustrative — but it's inconsistent with the document's stated goal of being domain-independent.

No other factual or structural errors found. The failure mode descriptions, root causes, and prevention mechanisms all accurately reflect the source material.

### Abstractions/Generalizations

**1. F2 could be broadened slightly.** The current framing is specific to code ("function body", "comments", "design intent"). The deeper pattern — that *rewriting* triggers a different cognitive mode than *editing*, causing embedded metadata to be treated as expendable — applies to any structured artifact (documents, configuration files, data schemas). Consider adding a one-sentence generalization:

```markdown
**Broader pattern**: Rewriting any structured artifact (code, document, configuration) triggers "generation mode" where existing content is treated as raw material. Editing triggers "modification mode" where existing content is treated as an artifact with embedded decisions. The failure occurs when generation mode is applied where modification mode is appropriate.
```

**2. F5 is well-generalized** but the current tier (`[technical]`) could arguably be `[long-running]` as well, since it applies to any system where analysis documents reference mutable artifacts. The technical tag is appropriate, but a note could mention it compounds in long-running engagements where many documents accumulate references.

### Other

**1. Summary table tier inconsistency.** The summary table (lines 158-168) wraps tier tags in backticks (`` `[long-running]` ``), while the body text of each entry uses `[long-running]` without backticks. This is a cosmetic inconsistency — minor, but worth standardizing in either direction.

**2. The file is well-structured and among the strongest in the series.** The incident → root cause → prevention pattern is consistent and actionable. The cross-cutting pattern section demonstrates the kind of meta-analysis that makes this document more than a list. The generality tier tags are well-chosen and consistently applied.

**3. Potential structural addition: failure mode severity or frequency.** The summary table has ID, failure mode, root cause, and tier, but no indication of severity or recurrence frequency. Some failures occurred once (F9); others recurred across multiple sessions before being addressed (F7, F2). A "recurrence" column (once / recurring / persistent) would help readers prioritize which preventions to implement first. This is optional — the current structure is clean and the document is already information-dense.

## Verdict

Changes warranted: **medium priority**.

The document is strong — well-generalized, well-structured, accurate. The highest-value changes are:

1. **Add cross-references section** (structural inconsistency with all other files in the series) — quick fix, high value for navigability
2. **Add F10: Duplicated Data Drift** — real failure mode from source material, clearly generalizable, distinct from existing entries
3. **Generalize F9 example** — minor text change to remove the last domain-specific reference
4. **Refine F7 status note** — make it a general lesson rather than a frozen snapshot

Lower-priority:
5. Consider F11 (Premature Hypothesizing) — adds value but requires judgment about whether it's distinct enough from F3
6. Consider broadening F2 beyond code to structured artifacts generally
7. Name the cross-cutting pattern ("Surface Equivalence Fallacy") for easier cross-referencing
