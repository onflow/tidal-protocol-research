# Review: PLAN.md

## File Summary

PLAN.md is the meta-document describing the rationale, extraction principles, output file structure, and generalization strategy for converting domain-specific learnings from a 7-week code audit collaboration into domain-independent AI agent guidance.

## Source Coverage

**Most relevant source files**: All source files are relevant to PLAN.md, since it describes the extraction process across the whole system. However, the files most directly informing PLAN.md's content are:
- `00-memory-system.mdc` — the generalization guidelines, evolution operations, and content hierarchy concepts that PLAN.md's extraction principles parallel
- `memory/CHANGELOG.md` — the meta-learnings section and directive lifecycle that inform the "preserve the why" principle
- `memory/WORKING_STYLE.md` — the retention policy and directive-as-hypothesis framing that PLAN.md generalizes into extraction principles
- `AUDITOR_GUIDE.md` — the human-facing perspective that PLAN.md cites as source material

### Source Material Listing Gap

PLAN.md lists five source categories (lines 10–14):
```
- memory/WORKING_STYLE.md
- memory/SESSION_LOG.md
- memory/CHANGELOG.md
- .cursor/rules/*.mdc (4 files)
- AUDITOR_GUIDE.md
```

**Missing from the list**: `memory/TECHNICAL.md` and `memory/CONCLUSIONS.md`. Both are substantive source files that directly informed the generalized output:
- TECHNICAL.md informed `01-MEMORY-SYSTEM.md` (the TECHNICAL file architecture section), `04-EVIDENCE-AND-VALIDATION.md` (status tiers), and `05-CODE-AND-DOCUMENTS.md` (abstraction guidelines with status marking)
- CONCLUSIONS.md informed `04-EVIDENCE-AND-VALIDATION.md` (status transitions, validation gate) and `01-MEMORY-SYSTEM.md` (CONCLUSIONS file architecture)

These two files are discussed extensively in the output files but aren't acknowledged as source material in the plan.

### "40+ directives" Claim (line 10)

WORKING_STYLE.md contains approximately 35–38 directive rows across all tables (Core Principles: 10, Communication: 2, Document Authoring: 8, Code Editing: 3, Git Hygiene: 1, Simulation Execution: 5, Exhaustive Claims: 1, Sim Reproduction Debugging: 6 steps, Problem-Specific: 2). "40+" is a slight overcount. Suggest: "~35 directives" or "approximately 40 directives" for accuracy.

## Internal Consistency

### Cross-references TO PLAN.md from other files

No other file in `generalized-agent-learnings/` references PLAN.md. This is appropriate — PLAN.md is a process document about the extraction, not a content document referenced by the output.

### Cross-references FROM PLAN.md to other files

PLAN.md's file structure table (lines 26–37) serves as the master index. All nine output files are listed with accurate one-line descriptions. Verified:

| File in table | Exists? | Description accurate? |
|---------------|---------|----------------------|
| `00-OVERVIEW.md` | ✓ | ✓ |
| `01-MEMORY-SYSTEM.md` | ✓ | ✓ |
| `02-INTERACTION-STYLE.md` | ✓ | ✓ |
| `03-SELF-IMPROVEMENT.md` | ✓ | ✓ |
| `04-EVIDENCE-AND-VALIDATION.md` | ✓ | ✓ |
| `05-CODE-AND-DOCUMENTS.md` | ✓ | ✓ |
| `06-FAILURE-MODES.md` | ✓ | ✓ |
| `07-META-LEARNINGS.md` | ✓ | ✓ |
| `08-BOOTSTRAPPING.md` | ✓ | ✓ |

### Overlap with 00-OVERVIEW.md

Both PLAN.md and 00-OVERVIEW.md define the three generality tiers (`[universal]`, `[technical]`, `[long-running]`). PLAN.md lines 47–51 and 00-OVERVIEW.md lines 73–79 contain near-identical tier definitions with the same examples. This is a mild duplication — the canonical home should be 00-OVERVIEW.md (since it's the system overview read by adopters), with PLAN.md referencing it rather than redefining it.

Both files also list the output file structure (PLAN.md lines 26–37, 00-OVERVIEW.md lines 11–24). The purposes differ (PLAN.md explains extraction intent; 00-OVERVIEW.md explains system architecture), but the duplication adds maintenance burden. This is acceptable if PLAN.md is understood as a one-time process document not maintained after extraction.

## Findings

### Refinements

**R1: Source material list should include TECHNICAL.md and CONCLUSIONS.md.**

Current (line 9–14):
```markdown
## Source Material

All learnings were developed through iterative feedback with a technical human collaborator ("the auditor"). Sources:
- `memory/WORKING_STYLE.md` — 40+ directives with reinforcement tracking
- `memory/SESSION_LOG.md` — 18 session entries documenting evolution
- `memory/CHANGELOG.md` — directive lifecycle and meta-learnings
- `.cursor/rules/*.mdc` — system-level rules (4 files)
- `AUDITOR_GUIDE.md` — human-facing description of the system
```

Suggested:
```markdown
## Source Material

All learnings were developed through iterative feedback with a technical human collaborator ("the auditor"). Sources:
- `memory/WORKING_STYLE.md` — ~35 directives with reinforcement tracking
- `memory/SESSION_LOG.md` — 18 session entries documenting evolution
- `memory/CHANGELOG.md` — directive lifecycle and meta-learnings
- `memory/TECHNICAL.md` — domain knowledge structure, status conventions, verification queue
- `memory/CONCLUSIONS.md` — validated/invalidated findings, status tiers, change log
- `.cursor/rules/*.mdc` — system-level rules (4 files)
- `AUDITOR_GUIDE.md` — human-facing description of the system
```

**R2: Extraction principles could note which principles come from the source material vs. are new design decisions.**

Principles 1–3 and 5 are generalizations of existing source material patterns:
- Principle 1 (generalize away from domain) ← `00-memory-system.mdc` "Generalize appropriately"
- Principle 2 (preserve the why) ← `CHANGELOG.md` provenance tracking, `WORKING_STYLE.md` Notes column
- Principle 3 (keep meta-cognitive layers) ← `00-memory-system.mdc` § Recursive Self-Evolution
- Principle 5 (include unsolved problems) ← `WORKING_STYLE.md` § Memory Update Crowding, `SESSION_LOG.md` § Open Questions

Principle 4 (audience is an AI agent) is a new design decision specific to this extraction effort. Noting this distinction would make the plan more transparent.

**R3: The "7-week" and "code audit domain" references are domain-specific.**

Lines 5 and 9 reference the specific engagement ("7-week human-AI collaboration (code audit domain)", "the auditor"). The extraction principles say to "generalize away from the domain" (Principle 1), but the PLAN itself contains domain-specific references. This is acceptable for a process document, but if the PLAN is meant to serve as a template for future extraction efforts, these could be parameterized:

```
Extract everything learned during a [duration] human-AI collaboration ([domain] domain) into domain-independent guidance...
```

This is low-priority — the PLAN is primarily a historical document for this specific extraction.

### Extensions

**E1: Source-to-output mapping table.**

The PLAN describes what sources exist and what output files will be produced, but doesn't document which sources primarily inform which output files. A mapping table would make the extraction traceable and help a reviewer (or future extractor) verify completeness:

```markdown
## Source-to-Output Mapping

| Output File | Primary Sources |
|-------------|----------------|
| `00-OVERVIEW.md` | `00-memory-system.mdc`, `AUDITOR_GUIDE.md` |
| `01-MEMORY-SYSTEM.md` | `00-memory-system.mdc`, `WORKING_STYLE.md`, `TECHNICAL.md`, `CONCLUSIONS.md`, `CHANGELOG.md` |
| `02-INTERACTION-STYLE.md` | `01-audit-interaction.mdc`, `WORKING_STYLE.md`, `AUDITOR_GUIDE.md` |
| `03-SELF-IMPROVEMENT.md` | `00-memory-system.mdc`, `WORKING_STYLE.md`, `CHANGELOG.md` |
| `04-EVIDENCE-AND-VALIDATION.md` | `01-audit-interaction.mdc`, `CONCLUSIONS.md`, `WORKING_STYLE.md` |
| `05-CODE-AND-DOCUMENTS.md` | `02-technical-domain.mdc`, `WORKING_STYLE.md`, `TECHNICAL.md` |
| `06-FAILURE-MODES.md` | `CHANGELOG.md`, `SESSION_LOG.md`, `WORKING_STYLE.md` |
| `07-META-LEARNINGS.md` | `CHANGELOG.md`, `00-memory-system.mdc`, `SESSION_LOG.md` |
| `08-BOOTSTRAPPING.md` | `SESSION_LOG.md`, `00-memory-system.mdc`, `AUDITOR_GUIDE.md` |
```

**E2: No mention of a review/validation step.**

The PLAN describes the extraction process but not how to verify the quality of the extraction. Given that this review process is now being conducted, the PLAN could have anticipated it:

```markdown
## Validation

After extraction, each output file should be reviewed against:
1. Source material coverage — is everything generalizable captured?
2. Internal consistency — are cross-references between output files accurate and bidirectional?
3. Generalization quality — is domain-specific content appropriately abstracted?
4. Faithfulness — do generalizations preserve the original intent and failure-mode context?
```

This is retrospective — the PLAN was written before the review was planned — but including it would make the PLAN a more complete template for future extractions.

**E3: Tier usage is uneven across output files.**

PLAN.md defines three generality tiers and states "Each directive is tagged with its tier" (line 52). In practice, tier tags are used in 5 of 9 output files (01-MEMORY-SYSTEM, 02-INTERACTION-STYLE, 04-EVIDENCE-AND-VALIDATION, 05-CODE-AND-DOCUMENTS, 06-FAILURE-MODES). Files 03-SELF-IMPROVEMENT, 07-META-LEARNINGS, and 08-BOOTSTRAPPING do not use tier tags. The PLAN could note that tier tags apply to directive-level content, not to meta-observations or process descriptions, to set expectations correctly.

### Corrections

**C1: "40+ directives" count is inaccurate.**

As detailed above, WORKING_STYLE.md contains approximately 35–38 directive rows. "40+" overstates this. Suggest "~35 directives" or simply "directives" without a count.

### Abstractions/Generalizations

**A1: "the auditor" terminology.**

Line 9 uses "the auditor" to describe the human collaborator. This is domain-specific to the code audit context. In the generalized system, the equivalent role is simply "the human collaborator" or "the human." The PLAN's extraction principles correctly identify this need (Principle 1), but the PLAN itself hasn't been fully generalized. Since the PLAN is a historical/process document rather than part of the generalized output, this is acceptable — but if the PLAN were to serve as a template, "auditor" should become "human collaborator."

**A2: The generalization strategy's diagnostic questions are excellent and fully general.**

Lines 42–46:
```
- At what level of generality does this still hold?
- What failure mode does it prevent?
- Is it specific to the human collaborator, the domain, or fundamental to AI-human collaboration?
- Does it have an implicit goal that should be stated explicitly?
```

These are already maximally general and directly usable by any agent performing a similar extraction. No changes needed.

### Other

**O1: PLAN.md serves dual purposes — archival record AND reusable template.**

The file works as both: (a) a historical record documenting how and why this extraction was done, and (b) a template for future extraction efforts in new domains. Both uses are valuable. A brief note acknowledging this dual purpose would help future readers understand they can use it either way.

Suggested addition at the end:
```markdown
## Status

This document serves two purposes:
1. **Archival**: Records the rationale and plan for this specific extraction. Does not need to be maintained as the output files evolve.
2. **Template**: For future extraction efforts in new domains, use this as a starting point — replace domain-specific references with the new context.
```

*(Auditor feedback: both uses are intentional and valuable — don't force a choice between them.)*

**O2: Relationship to 00-OVERVIEW.md could be clearer.**

There's a natural question for readers: "What's the difference between PLAN.md and 00-OVERVIEW.md?" PLAN.md describes *how and why the extraction was done*. 00-OVERVIEW.md describes *the resulting system for adopters*. The PLAN could note this distinction explicitly, either in the file structure table or in a brief note:

```markdown
Note: `PLAN.md` documents the extraction process and is not part of the system an adopting agent would use. The entry point for adopters is `00-OVERVIEW.md`.
```

## Verdict

Changes are warranted. **Priority: medium.**

The file is well-structured and its extraction principles are sound. The main issues are:
1. Incomplete source material listing (missing TECHNICAL.md and CONCLUSIONS.md) — easy fix, high value for traceability
2. Missing source-to-output mapping — moderate effort, high value for verification
3. Slight inaccuracy in directive count — trivial fix
4. Missing status/role clarification (archival vs. living) — trivial but prevents confusion
5. Tier tag coverage note — minor but sets correct expectations

None of these are structural problems. The file fulfills its purpose as a plan document; the suggested changes improve completeness and traceability.
