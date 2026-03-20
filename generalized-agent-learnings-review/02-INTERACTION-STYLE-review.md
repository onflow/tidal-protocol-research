# Review: 02-INTERACTION-STYLE.md

## File Summary

Covers human collaboration patterns: seven core principles for interaction style (top-down presentation, information density, mutual fallibility, proactive engagement, progressive abstraction, directive confidence scaling, generalization awareness), calibration to the human's expertise, the feedback loop, scope definitions for directives, and communication micro-rules.

## Source Coverage

**Primary source**: `.cursor/rules/01-audit-interaction.mdc` — the most directly mapped source. All seven core principles from this file are captured and generalized. The scope definitions table is carried over. The four interaction patterns (When Presenting Technical Content, When Receiving Corrections, When Uncertain, When Finding Evidence) are partially absorbed into the core principles rather than preserved as separate protocols (see Refinements below).

**Secondary sources**:
- `memory/WORKING_STYLE.md` — The Auditor Profile is generalized into "Expertise Profile" (§Calibrating to the Human). Communication Style directions are captured in "Communication Micro-Rules." The "Retention and Evaluation" section's insight that "silence ≠ irrelevance" is captured in the Feedback Loop's treatment of implicit feedback. The detailed document authoring and code editing sections are appropriately deferred to `05-CODE-AND-DOCUMENTS.md`.
- `memory/CHANGELOG.md` — The reinforcement history and provenance data informed the confidence levels stated in the file (e.g., proactive engagement being "the single most reinforced directive"). Not directly quoted, which is correct for a generalized document.
- `AUDITOR_GUIDE.md` — The learning loop diagram (`Human directs → Agent complies → Human gives feedback → Agent updates memory → Better compliance`) is faithfully reproduced in §Feedback Loop. The human-facing tips ("Challenge claims", "State scope", "Summarize periodically") have agent-side implications that aren't explicitly captured (see Extensions).
- `00-memory-system.mdc` — The Validation Gate and Directive Confidence sections are covered, with the validation gate appropriately deferred to `04-EVIDENCE-AND-VALIDATION.md`.

**Content captured well**:
- All seven core principles with rationale and behavioral specifics
- The Expertise Profile concept (generalized from "Auditor Profile")
- Feedback loop with three feedback types (explicit positive, explicit negative, implicit)
- The critical insight that "absence of correction means working, NOT irrelevant"
- Scope definitions with promotion/demotion

**Content missing or thin** (detailed in Extensions below):
- The "When Finding Evidence" structured protocol from `01-audit-interaction.mdc` (lines 76–92) is not present even as a summary — it's fully deferred to `04-EVIDENCE-AND-VALIDATION.md` without a cross-reference
- The "Recognizing Validation Opportunities" subsection from `01-audit-interaction.mdc` (lines 85–92) with its four indicators — same issue
- Agent-side implications of the human's collaboration tips from `AUDITOR_GUIDE.md`

## Internal Consistency

### References TO this file (from other files)

| Source File | Reference | Accurate? |
|---|---|---|
| `00-OVERVIEW.md` reading order item 2 | `02-INTERACTION-STYLE.md` — how to work with the human | ✓ |
| `03-SELF-IMPROVEMENT.md` line 83 | `→ 02-INTERACTION-STYLE.md §7: Generalization Awareness` | ✓ — §7 is indeed Generalization Awareness |
| `03-SELF-IMPROVEMENT.md` line 209 | `Generalization awareness (directive application) → 02-INTERACTION-STYLE.md §7` | ✓ |
| `04-EVIDENCE-AND-VALIDATION.md` line 166 | `Validation gate and proactive engagement → 02-INTERACTION-STYLE.md §4 (proactive engagement)` | ✓ — §4 is Proactive Engagement |
| `08-BOOTSTRAPPING.md` line 175 | `→ 02-INTERACTION-STYLE.md for content guidance` | ✓ |

All inbound references are accurate.

### References FROM this file (to other files)

**None.** This is the most significant structural gap. Every other substantive file in the collection (`01-MEMORY-SYSTEM.md`, `03-SELF-IMPROVEMENT.md`, `04-EVIDENCE-AND-VALIDATION.md`, `05-CODE-AND-DOCUMENTS.md`, `06-FAILURE-MODES.md`, `07-META-LEARNINGS.md`, `08-BOOTSTRAPPING.md`) has a `## Cross-References` section at the end. `02-INTERACTION-STYLE.md` does not.

Cross-references that should exist (based on content overlap and the referencing pattern in other files):
- **To `04-EVIDENCE-AND-VALIDATION.md`**: The validation gate, the "When Finding Evidence" protocol, and evidence presentation are mentioned or implied in §4 but the full treatment lives in 04
- **To `03-SELF-IMPROVEMENT.md`**: "Learning from corrections" (§3 behaviors) is expanded into a 6-step protocol there; generalization protocol (§7) has a detailed treatment there; the three priorities problem underlies proactive engagement
- **To `06-FAILURE-MODES.md`**: F4 (over-generalization) is the concrete failure behind §7; F6 (premature validation) relates to §4; F7 (memory update omission) relates to the feedback loop
- **To `01-MEMORY-SYSTEM.md`**: Memory update crowding relates to the feedback loop's operational challenge
- **To `07-META-LEARNINGS.md`**: §8 (proactivity as differentiator) expands on §4; §7 (human teaches through corrections) expands on the feedback loop; §11 (expertise shapes collaboration geometry) expands on the expertise profile

### Bidirectionality Check

| Other File | References 02? | 02 References It? | Bidirectional? |
|---|---|---|---|
| `03-SELF-IMPROVEMENT.md` | ✓ (2 refs) | ✗ | **No** — needs outbound ref |
| `04-EVIDENCE-AND-VALIDATION.md` | ✓ (1 ref) | ✗ | **No** — needs outbound ref |
| `08-BOOTSTRAPPING.md` | ✓ (1 ref) | ✗ | **No** — needs outbound ref |
| `06-FAILURE-MODES.md` | ✗ | ✗ | OK (no strong coupling) |
| `07-META-LEARNINGS.md` | ✗ | ✗ | OK (could add, not critical) |

## Findings

### Refinements

**R1: "Single most reinforced directive (3 reinforcements)" provenance statement**

```
This is the single most reinforced directive (3 reinforcements).
```
This is domain-specific provenance from the Tidal audit, not a generalizable instruction. The *concept* that proactive engagement was the most reinforced and therefore highest-priority directive is valuable, but the specific count is anchored in one engagement. Suggested replacement:

> **In practice, this tends to be one of the most important directives.** It governs the overall posture of the collaboration: the agent as an active contributor, not a passive tool.

**R2: §1 Pattern step 2 is slightly technical**

```
2. Core mechanism or formula (abstracted)
```

For a `[universal]` directive, "mechanism or formula" is narrow. Suggested:

> 2. Core concept, mechanism, or model (abstracted)

**R3: §3 "When wrong" protocol could reference the fuller version in 03**

The behaviors listed under "When wrong" (acknowledge, update memory, restate, ask for confirmation) are a subset of the 6-step correction protocol in `03-SELF-IMPROVEMENT.md` (which adds "trace root cause" and "check cascade effects"). Either expand here or add an explicit forward-reference:

> For the full correction-handling protocol, see `03-SELF-IMPROVEMENT.md` §Learning From Corrections.

**R4: §5 Progressive Abstraction depth levels are code-centric**

The four levels reference code-specific concepts:
```
- Level 2: Full implementation with edge cases
- Level 3: Code walkthrough with line references
```

The tag is `[technical]`, which is appropriate, but a small addition could broaden it:

> Adapt the specific levels to your domain. For code-centric work: Level 0 = purpose, Level 1 = algorithm, Level 2 = implementation, Level 3 = code walkthrough. For non-code work: Level 0 = purpose, Level 1 = model/framework, Level 2 = full detail with evidence, Level 3 = raw data/sources.

**R5: Minor redundancy — "No confirmative openers"**

Mentioned both in §2 (High Information Density, "Concrete rules" list) and in the Communication Micro-Rules table at the end. The table entry is sufficient; the §2 mention could be trimmed to avoid duplication, or §2 could reference the table. Not a high-priority issue.

### Extensions

**E1: Missing `## Cross-References` section** (high priority)

Every other file in the collection has one. This file needs:

```markdown
## Cross-References

- Validation gate and evidence presentation → `04-EVIDENCE-AND-VALIDATION.md`
- Full correction-handling protocol → `03-SELF-IMPROVEMENT.md` §Learning From Corrections
- Generalization protocol (pattern extraction side) → `03-SELF-IMPROVEMENT.md` §Two Kinds of Generalization
- Failure modes: over-generalization (F4), premature validation (F6), memory update omission (F7) → `06-FAILURE-MODES.md`
- Proactivity as the collaboration differentiator → `07-META-LEARNINGS.md` §8
- Memory update crowding (interaction-related challenge) → `01-MEMORY-SYSTEM.md` §Memory Update Crowding Problem
- How the human's role evolves over the collaboration → `07-META-LEARNINGS.md` §12
```

**E2: "When Finding Evidence" interaction protocol missing**

The source (`01-audit-interaction.mdc` lines 76–92) has a structured 5-step protocol:
1. Present evidence concisely
2. State confidence level and reasoning
3. If evidence sufficient, memorize as `evidence-supported`
4. Present to human, ask to elevate to `verified`
5. Offer to go deeper

This protocol sits at the intersection of interaction style (how to present) and evidence handling (what the steps are). `04-EVIDENCE-AND-VALIDATION.md` covers it fully in "Presenting Findings" and "Status Transitions." The interaction-style file should at minimum have a brief forward-reference under §4 (Proactive Engagement):

> **When presenting findings**: See `04-EVIDENCE-AND-VALIDATION.md` §Presenting Findings for the structured protocol. Key interaction-style point: always ask explicitly for validation — don't present and assume the human will respond.

**E3: "Recognizing Validation Opportunities" indicators**

The source lists four specific indicators (multiple concordant references, mechanism fully traced, formula cross-checked, insight built over multiple exchanges). These are mentioned in the concrete examples of §4 but not as a structured list of triggers. The full list lives in `04-EVIDENCE-AND-VALIDATION.md`. A brief mention or cross-reference in §4 would improve navigability.

**E4: Agent-side implications of human collaboration tips**

From `AUDITOR_GUIDE.md` lines 125–129, the human is advised to:
- "Challenge claims — Ask for code references; verify formulas"
- "State scope — 'This direction applies generally' vs 'Just for this problem'"
- "Summarize periodically — 'Let's capture what we've established about X'"

These have agent-side counterparts that could be added to the interaction patterns:
- **Expect challenges**: Welcome them as validation opportunities. Have evidence ready.
- **Ask for scope when not provided**: "Should this apply generally, or just for this task?"
- **Offer periodic summaries proactively**: "We've now established X, Y, Z — want me to consolidate?"

These would fit naturally under §4 (Proactive Engagement) or as additions to the Communication Micro-Rules.

**E5: The human's evolving role**

`07-META-LEARNINGS.md` §12 describes how the human's role evolves (teacher → reviewer → collaborator) and how the agent should match each role. This insight has direct interaction-style implications: how you communicate with a human who's still in the "teaching" phase vs. one who's in the "collaborating" phase. Currently this insight lives only in `07-META-LEARNINGS.md`. A brief mention or forward-reference in the Calibrating section would connect these concerns:

> The human's role evolves over the collaboration. Early: they teach (expect frequent corrections). Later: they review and collaborate (expect more initiative from you). Calibrate your posture to match. → `07-META-LEARNINGS.md` §12

### Corrections

No factual errors found. All section numbering matches the cross-references from other files. The generalization from domain-specific source material is accurate and faithful.

One near-correction: §4 states proactive engagement had "3 reinforcements" — this is accurate per the source material (`WORKING_STYLE.md`, `CHANGELOG.md`) but is provenance from a specific engagement, not a generalizable fact. See R1 above.

### Abstractions/Generalizations

**A1: §4 Concrete examples are somewhat domain-specific**

The four examples under Proactive Engagement:
```
- After tracing a mechanism through code: proactively summarize and ask to mark as validated
- After receiving a correction: proactively check whether the correction applies to other places
- After finding conflicting evidence: proactively flag it...
- After completing a multi-step task: proactively ask whether the approach worked...
```

The first is code-audit-specific. The others are generic. Suggested revision for the first:
> - After completing an investigation that produces a finding: proactively summarize and ask to mark as validated

**A2: Communication Micro-Rules "Self-contained documents" tagged `[technical]`**

The principle "formal documents should be readable without follow-up questions: ground domain terms, back claims with references" applies to any formal deliverable (reports, proposals, analyses), not just technical documents. The tag is defensible (the concrete implementation details are technical), but the principle generalizes. Consider adding a note:

> The principle generalizes to any formal deliverable. The specific practices (code references, parameter values) are technical.

**A3: "Scoped IDs need source context" tagged `[technical]`**

This principle — that identifiers meaningful in one document need descriptive context when cited elsewhere — applies to any multi-document system, not just technical ones. However, the practical impact is mainly felt in technical documentation with cross-references. The tag is reasonable as-is.

### Other

**O1: Structural comparison with the source's interaction patterns**

The source (`01-audit-interaction.mdc`) has a clean "Interaction Patterns" section with four sub-patterns:
1. When Presenting Technical Content
2. When Receiving Corrections
3. When Uncertain
4. When Finding Evidence

The generalized file dissolves these into the Core Principles sections (1 → §1, 2 → §3, 3 → §3, 4 → partially §4 / partially deferred to 04). This is a reasonable design choice that reduces redundancy, but it means the file doesn't serve as a quick-reference for "what do I do when X happens?" A brief "Interaction Patterns Quick Reference" subsection (even just a table pointing to where each pattern is covered) would improve navigability:

```markdown
## Interaction Pattern Quick Reference

| Situation | Where Covered |
|---|---|
| Presenting information | §1 Top-Down Presentation (pattern) |
| Receiving a correction | §3 Mutual Fallibility + `03-SELF-IMPROVEMENT.md` §Learning From Corrections |
| Uncertain about something | §3 Mutual Fallibility (behaviors, first bullet) |
| Evidence ready for validation | `04-EVIDENCE-AND-VALIDATION.md` §Presenting Findings |
```

**O2: File is well-scoped**

The file maintains a clear boundary: it covers *how to interact*, not *what to remember* (01), *how to improve* (03), or *how to handle evidence* (04). The decisions about what to defer to other files are sound. The main structural issue is the missing cross-references section that would make those deferral decisions explicit to the reader.

## Verdict

Changes are warranted. Priority: **medium**.

The content quality is high — the seven core principles are well-generalized, the expertise profile and feedback loop sections add genuine value beyond the source material, and the scope/tagging system is applied consistently.

The primary gaps are structural (missing cross-references section) and connective (a few places where content deferred to other files needs explicit forward-references). The refinements are mostly sharpening existing content rather than correcting errors.

**Priority ordering of changes**:
1. **High**: Add `## Cross-References` section (E1) — structural gap that breaks the collection's consistency
2. **Medium**: Add forward-reference to `04-EVIDENCE-AND-VALIDATION.md` for evidence presentation protocol (E2)
3. **Medium**: Revise provenance-specific language in §4 (R1)
4. **Low**: Add interaction pattern quick-reference (O1)
5. **Low**: Minor generalizations in §1 pattern, §4 examples, §5 levels (R2, A1, R4)
6. **Low**: Trim "no confirmative openers" redundancy (R5)
7. **Low**: Add human role evolution note (E5) and collaboration tips counterparts (E4)
