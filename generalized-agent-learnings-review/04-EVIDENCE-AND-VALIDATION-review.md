# Review: 04-EVIDENCE-AND-VALIDATION.md

## File Summary

This file covers the epistemology of AI-human technical collaboration: how the agent should gather evidence, when to present findings, how to handle truth claims at different confidence levels, and how to manage context transitions that might invalidate prior conclusions. It bridges interaction style (02) and failure modes (06) by prescribing the positive practices that prevent premature validation, unverified claims, and stale assumptions.

## Source Coverage

### Primary Sources

| Source | Relevance | Coverage |
|--------|-----------|----------|
| `01-audit-interaction.mdc` §When Finding Evidence, §Recognizing Validation Opportunities | High | Well captured. Status transitions, proactive presentation, indicators for sufficient evidence. |
| `00-memory-system.mdc` §Validation Gate | High | Well captured. Two-category split (technical vs operational) generalized cleanly. |
| `WORKING_STYLE.md` §Exhaustive Claims | High | Well captured and correctly tagged `[technical]`. |
| `WORKING_STYLE.md` §Simulation Reproduction Debugging | High | Good generalization: "Simulation Reproduction Debugging" → "Tracing Root Causes", sim-specific language replaced with generic terms. |
| `WORKING_STYLE.md` §Verify code refs after edits | Medium | Captured as "Cross-Referencing After Changes". Overlaps with `05-CODE-AND-DOCUMENTS.md` §Code References in Documents. |
| `WORKING_STYLE.md` §Internal classifications | Medium | Captured as "Methodology Separation". Domain context (post-delivery vs pre-existing bugs) generalized to (external changes vs pre-existing issues). |
| `SESSION_LOG.md` §2026-03-03 (Commit Transition) | Medium | The zero-hypothesis carry-forward model and transition protocol are well generalized from the specific da4cbf9→ba544b1 transition. |
| `SESSION_LOG.md` §2026-03-10d (Remediation Cross-Check) | Medium | Captured as "Remediation Verification". Brief but covers the essentials. |
| `CONCLUSIONS.md` (structure + change log) | Low | The Conclusion Change Log format is not captured (see Extensions below). |
| `AUDITOR_GUIDE.md` §Validating Conclusions | Low | The human's ability to proactively validate ("Confirmed: X, see file:line") is not captured (see Extensions). |
| `01-audit-interaction.mdc` §When Uncertain | Low | Uncertainty behaviors are related to but distinct from "Cost of False Confidence" — not fully captured. |

### Content Missing from Sources

1. **Status definition precision.** The source (`00-memory-system.mdc` line 55–56) explicitly defines:
   - `evidence-supported`: "sufficient code evidence found, awaiting or not yet presented for auditor confirmation"
   - `verified`: "auditor has confirmed the finding"
   
   The generalized file has the status ladder diagram and the transitions but never explicitly defines what each status *means*. A reader encountering `evidence-supported` for the first time doesn't know how it differs from `unverified`. See Refinements §1.

2. **Verification Queue concept.** `TECHNICAL.md` (lines 154–162) maintains a "Verification Queue" — a list of items needing code verification, with items crossed off as they're verified. This is a practical organizational tool for tracking pending validation work. Not captured anywhere in the generalized files.

3. **Human-initiated validation.** `AUDITOR_GUIDE.md` (line 66–67) shows a pattern where the human proactively confirms: "Confirmed: liquidation penalty is 5%, see `liquidator.py:89`". The current file only describes the agent-initiated flow (agent presents → asks "Can I mark validated?" → human confirms). The reverse direction (human volunteers confirmation) is missing.

4. **Conclusion Change Log format.** `CONCLUSIONS.md` (lines 103–127) maintains a dated change log tracking every status transition with evidence. This audit trail for validation decisions is a valuable pattern not captured in 04 or elsewhere in the generalized files.

5. **Explicit uncertainty behaviors.** `01-audit-interaction.mdc` §When Uncertain (lines 70–74) prescribes specific behaviors: "State uncertainty explicitly / Offer best hypothesis with caveats / Ask targeted clarifying questions / Do not pretend confidence." The "Cost of False Confidence" section (04 lines 103–109) explains *why* over-claiming is bad but doesn't prescribe the *alternative behaviors* as concretely. These are partially covered in `02-INTERACTION-STYLE.md` §3 (Mutual Fallibility) but the evidence-specific uncertainty behaviors deserve mention in 04.

## Internal Consistency

### Cross-References from 04

| Target | Claimed Reference | Accuracy |
|--------|-------------------|----------|
| `02-INTERACTION-STYLE.md` §4 | "Proactive engagement" | **Correct.** §4 is indeed Proactive Engagement. |
| `06-FAILURE-MODES.md` F3, F6 | "Exhaustive claims, premature validation" | **Correct.** F3 = exhaustive claims without verification; F6 = premature validation. |
| `08-BOOTSTRAPPING.md` | "Phase transitions, transferring to new domains" | **Partially accurate.** 08 covers collaboration phases and domain transfer, but the "phase transitions" reference is ambiguous — 04's "Context Transitions" section is about *scope/version transitions* (new codebase version, new analysis area), not collaboration phases. The cross-reference should be more specific: "→ `08-BOOTSTRAPPING.md` (transferring to new domains; Content Hierarchy for change caution)". |
| `05-CODE-AND-DOCUMENTS.md` | "Code references in documents" | **Correct.** The section exists and covers the same topic. |

### Cross-References TO 04 from Other Files

| Source File | References 04? | Notes |
|-------------|---------------|-------|
| `00-OVERVIEW.md` | Yes (reading order, line 31) | Described as "how to handle findings and truth claims" |
| `01-MEMORY-SYSTEM.md` | No | Should reference 04 for the validation gate (currently describes it inline at §Update Rules and §CONCLUSIONS) |
| `02-INTERACTION-STYLE.md` | No | No cross-reference section. §4 (Proactive Engagement) is closely related but doesn't point to 04. |
| `03-SELF-IMPROVEMENT.md` | No | The Cross-References section (lines 204–209) doesn't mention 04 despite significant topic overlap: proactive engagement, self-reflection → validation readiness, pattern extraction → finding consolidation. |
| `05-CODE-AND-DOCUMENTS.md` | No | No cross-reference section. "Code References in Documents" overlaps with 04 §Cross-Referencing After Changes. |
| `06-FAILURE-MODES.md` | No | F3 and F6 directly correspond to 04 content but have no forward reference. Only a summary table + cross-cutting pattern analysis. |
| `07-META-LEARNINGS.md` | No | §8 (Proactivity) and §13 (Trust Through Self-Correction) are deeply related to evidence/validation but the Cross-References section doesn't mention 04. |
| `08-BOOTSTRAPPING.md` | No | No reference back despite 04 cross-referencing 08. |

**Verdict**: Cross-references are unidirectional. 04 points to four other files; none of those four point back. This is part of a broader pattern across the series (only 03, 04, and 07 have dedicated cross-reference sections), but it's a gap worth flagging for the series-wide review.

### Content Overlap

| 04 Section | Overlapping File | Overlap Severity | Resolution |
|------------|-----------------|------------------|------------|
| Cross-Referencing After Changes (lines 78–83) | `05-CODE-AND-DOCUMENTS.md` §Code References in Documents (lines 89–95) | **Moderate** — both prescribe: cross-check ALL refs after edits, trace root cause of shifts, do as background task | 04 should reference 05 for the detailed prescription and focus only on the *evidence integrity* angle (stale references corrupt the evidence chain). Currently, both files contain nearly identical operational instructions. |
| Presenting Findings §Structure (lines 88–93) | `02-INTERACTION-STYLE.md` §Top-Down Presentation (lines 12–15) | **Low** — 02 is about general presentation structure; 04 is specifically about presenting *evidence-backed findings*. Different enough to coexist. | No change needed. |
| Status Transitions (lines 96–101) | `01-MEMORY-SYSTEM.md` §CONCLUSIONS (lines 79–96) | **Low** — 01 describes the data structure; 04 describes the workflow. Complementary. | No change needed. |

## Findings

### Refinements

**R1: Explicit status definitions.** The status ladder (lines 18–22) shows transitions but doesn't define the statuses. Add a brief definition table:

```markdown
| Status | Meaning |
|--------|---------|
| `unverified` | Stated or extracted, not yet investigated |
| `evidence-supported` | Agent has gathered sufficient evidence; not yet human-confirmed |
| `verified` | Human has explicitly confirmed the finding |
| `disputed` | Conflicting evidence exists |
| `invalidated` | Previously believed, now disproven |
```

This is especially important because `evidence-supported` is a non-obvious status (it's a gate *between* unverified and verified, not just "has some evidence"). Source: `00-memory-system.mdc` lines 55–56.

**R2: Tighten "Cross-Referencing After Changes" to avoid duplication with 05.** Currently lines 78–83 repeat operational instructions that appear nearly verbatim in `05-CODE-AND-DOCUMENTS.md`. Suggested rewrite:

```markdown
### Cross-Referencing After Changes

`[technical]`

After making changes (code fixes, document edits), all references in affected documents become suspect.
The evidence chain depends on accurate references — a stale line number sends the reader to wrong code,
undermining the finding it supports.

→ `05-CODE-AND-DOCUMENTS.md` §Code References in Documents for the full operational protocol
(cross-check ALL references, trace root cause of shifts, do as background task during edits).
```

**R3: Cross-reference to 08 should be more specific.** Line 168 says "Context transitions and the bootstrapping trajectory → `08-BOOTSTRAPPING.md` (phase transitions, transferring to new domains)". The "phase transitions" in 08 refer to the *collaboration* phases (genesis → calibration → productive → meta-refinement), not *context* transitions (new codebase version, new scope). Suggested: "→ `08-BOOTSTRAPPING.md` (transferring to new domains; Content Hierarchy for deciding re-verification priority)".

**R4: "Methodology Separation" framing is slightly narrow.** Lines 115–124 frame the separation as "external changes vs pre-existing issues" tied to reproducibility investigation. The underlying principle is more general: *when multiple potential causes are entangled, separate them by timeline/origin and investigate independently*. A one-line reframe at the top would help:

```markdown
## Methodology Separation

`[technical]`

When investigating a system with multiple overlapping anomalies, separate the investigation by cause origin
and timeline. This prevents conflating different explanations for the same observed symptom.
```

The current text after line 116 already serves as a good concrete example; adding this preamble makes the general principle explicit before the specific case.

### Extensions

**E1: Verification Queue as a practical tool.** Add a brief section or note about maintaining a running list of items pending verification. From `TECHNICAL.md` lines 154–162:

```markdown
### Verification Queue

`[technical]`

Maintain a running list of claims awaiting verification. As items are verified, mark them (strikethrough
or move to the appropriate verified section). This prevents claims from silently persisting at `unverified`
indefinitely — the queue creates visibility and accountability for pending verification work.
```

**E2: Bidirectional validation flow.** The file describes only agent-initiated validation (agent presents → asks to validate → human confirms). Add:

```markdown
The human may also proactively validate: "Confirmed: X, see evidence Y." This is equally valid and should
be recorded immediately — update the finding's status and note the human's evidence reference.
```

This comes from `AUDITOR_GUIDE.md` line 66–67.

**E3: Uncertainty behaviors as the alternative to false confidence.** After the "Cost of False Confidence" section (line 109), add a brief prescriptive counterpoint:

```markdown
**The alternative**: When evidence is incomplete, state what you know and what you don't. Offer your best
hypothesis with explicit caveats. Ask targeted questions that would resolve the remaining uncertainty.
"I think this is X but haven't verified Y aspect" is always preferable to presenting X as established fact.
```

This draws from `01-audit-interaction.mdc` §When Uncertain (lines 70–74) and complements the existing "Cost of False Confidence" by prescribing what to do instead.

**E4: Conclusion Change Log as audit trail.** Mention the value of maintaining a dated log of every status transition:

```markdown
### Maintaining a Validation Audit Trail

`[long-running]`

Track every status change for findings in a dated change log:

| Date | Finding | Status Change | Evidence |
|------|---------|--------------|----------|

This creates accountability and enables post-hoc review of the validation process itself — useful
during context transitions (which findings were validated when? with what evidence?).
```

From `CONCLUSIONS.md` lines 103–127.

### Corrections

**C1: No factual errors found.** All claims are accurately traced from source material. Status transitions, validation gate semantics, evidence standards, and methodology separation are all faithful to the originals.

**C2: Minor structural note.** The "Remediation Verification" subsection (lines 153–160) is nested under "Context Transitions and Zero-Hypothesis Carry-Forward" but is conceptually independent — it applies whenever a set of fixes is applied, not only during context transitions. Consider making it a peer section or explicitly noting that it applies broadly: "This applies after any batch of changes, not only during context transitions."

### Abstractions/Generalizations

**A1: Root cause tracing steps are well-generalized but unevenly abstract.** The six steps (lines 68–75) range from highly general (step 1: "Establish the gap first") to code-investigation-specific (step 5: "Comment–value mismatch = flag"). The `[technical]` tag is appropriate, but steps 1 and 6 could be tagged as applying more broadly:

- Step 1 ("Establish the gap first — quantify divergence before reading code") → universally applicable to any gap analysis: quantify the divergence before hypothesizing about cause.
- Step 6 ("Trace symptoms upstream") → universal debugging principle: the visible symptom is rarely the root cause.

Steps 2–5 are appropriately technical. No change strictly needed, but a note like "Steps 1 and 6 apply to any investigation; steps 2–5 are specific to code/config debugging" would help readers generalize correctly.

**A2: "Context Transitions" could note the general principle more explicitly.** The section title and opening (lines 127–131) jump straight into the mechanics. A one-sentence framing would help: "Prior findings are hypotheses about a specific context. When the context changes, each finding becomes a zero-hypothesis: assumed to hold until re-verified." This principle applies beyond codebases — it applies whenever the environment under study changes (new data, new version, new scope).

### Other

**O1: Bidirectional cross-references across the series.** As noted in Internal Consistency, 04 references four other files but none reference it back. Files that should reference 04:
- `03-SELF-IMPROVEMENT.md` Cross-References section should add: "Validation gate and evidence standards → `04-EVIDENCE-AND-VALIDATION.md`"
- `06-FAILURE-MODES.md` should either add a cross-reference section or note "→ `04-EVIDENCE-AND-VALIDATION.md` for the prescriptive counterpart to F3, F6"
- `07-META-LEARNINGS.md` Cross-References section should add: "Evidence handling and validation → `04-EVIDENCE-AND-VALIDATION.md`"

This is a series-wide issue, not specific to 04, but 04 is particularly under-referenced given its centrality to the collaboration model.

**O2: The file is well-structured and appropriately scoped.** At 170 lines, it's concise without being skeletal. The progression from validation gate → evidence standards → presenting findings → methodology → context transitions follows a logical arc from "what counts as evidence" through "how to present it" to "how to handle it when context changes."

**O3: Tier tagging is consistent.** `[universal]` for the validation gate and opportunity recognition, `[technical]` for evidence standards and methodology, `[long-running]` for context transitions. All appropriate.

## Verdict

**Changes warranted: medium priority.**

The file is solid — well-structured, accurately generalized, and appropriately tagged. No factual errors. The main opportunities are:

1. **Add status definitions** (R1) — high value, low effort. The status ladder without definitions is a usability gap.
2. **Deduplicate with 05** (R2) — medium value, prevents reader confusion about which file is authoritative on code reference verification.
3. **Extend with verification queue, bidirectional validation, uncertainty behaviors, and audit trail** (E1–E4) — medium value each, adds practical tools from source material.
4. **Fix cross-reference specificity** (R3) and **broaden "Remediation Verification" scope** (C2) — low effort, improves accuracy.
5. **Bidirectional cross-references** (O1) — requires changes in OTHER files (03, 06, 07), not in 04 itself.

None of these are structural problems. The file works well as-is; the changes would sharpen it from "good generalization" to "comprehensive reference."
