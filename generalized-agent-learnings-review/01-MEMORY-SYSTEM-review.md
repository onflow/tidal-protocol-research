# Review: 01-MEMORY-SYSTEM.md

## File Summary

Describes the persistent memory system: five files with distinct purposes, update rules (when and how), the memory update crowding problem and its partial solution (always-injected checklists), the maintenance protocol, evolution operations, scaling strategy, health checks, and the content hierarchy that governs change caution.

## Source Coverage

### Primary Sources

| Source File | Relevance | Coverage |
|---|---|---|
| `00-memory-system.mdc` | **Primary** — main source for almost all content | High but with notable gaps (see Extensions) |
| `03-memory-update-triggers.mdc` | The trigger checklist | Well captured in §Memory Update Crowding and §Always-Injected Checklists |
| `memory/WORKING_STYLE.md` | Memory Update Crowding section, Retention Policy, Memory Organization | Crowding section well covered; Retention Policy partially absorbed |
| `memory/CHANGELOG.md` | Meta-Learnings, Structural Changes, Directive Lifecycle | Absorbed at a general level; specific meta-learnings generalized appropriately |
| `memory/SESSION_LOG.md` | Sessions 2026-02-27 and 2026-02-28 (memory system iterations) | Design decisions and failure-driven evolution captured without domain specifics |
| `AUDITOR_GUIDE.md` | Human-facing description of the system | Not directly relevant to agent-facing content; properly excluded |

### Well-Captured Content

- File architecture (5 files, purposes, tags) — faithful to source, well generalized
- Update rules (6 trigger conditions) — accurate transcription from `00-memory-system.mdc` lines 24-31
- How to update (snippets over sentences, references over copies, etc.) — all 6 rules from source present
- Maintenance protocol (5 rules) — maps to source lines 100-109
- Evolution operations vocabulary — complete set from source lines 113-119
- Memory Update Crowding problem — excellent treatment; adds the "Implementation Pattern: Always-Injected Checklists" generalization which goes *beyond* the source material (good)
- Content Hierarchy — accurate, matches source and cross-referenced files

### Missing Content (see Extensions below for details)

1. **Active Retrieval protocol** — the session-start reading protocol is absent
2. **Validation Gate as it applies to memory updates** — the two-category distinction (technical conclusions vs. operational content) is not mentioned
3. **Self-evaluation questions for the memory system** — 7 questions from source omitted
4. **Directive Confidence model** — not mentioned in this file
5. **Pattern extraction trigger** — the "3+ iterations → extract pattern" rule from `00-memory-system.mdc` line 32 is absent from the update rules
6. **Retention Policy** — no explicit section on when to retain vs. archive directives
7. **Autonomy Principle** and **Stability Gradient** — from source's Recursive Self-Evolution section

## Internal Consistency

### Cross-References FROM This File

Line 210:
> → `07-META-LEARNINGS.md` §10b for the error-recovery perspective; `08-BOOTSTRAPPING.md` § Content Hierarchy for the change-frequency perspective.

- `07-META-LEARNINGS.md` §10b (lines 142-156): **Valid.** Discusses Content Hierarchy from error-recovery perspective.
- `08-BOOTSTRAPPING.md` § Content Hierarchy (lines 192-205): **Valid.** Discusses Content Hierarchy from change-frequency perspective.

### Cross-References TO This File (from other files)

| File | Reference | Valid? |
|---|---|---|
| `03-SELF-IMPROVEMENT.md` line 205 | "Three Priorities Problem → also discussed in `01-MEMORY-SYSTEM.md` (Memory Update Crowding)" | ✓ Section exists at line 131 |
| `07-META-LEARNINGS.md` line 237 | "The persistence infrastructure → `01-MEMORY-SYSTEM.md`" | ✓ |
| `08-BOOTSTRAPPING.md` line 173 | "→ `01-MEMORY-SYSTEM.md` for content guidance" | ✓ |
| `08-BOOTSTRAPPING.md` line 177 | "→ `01-MEMORY-SYSTEM.md` TECHNICAL section for format guidance" | ✓ Section exists at line 62 |
| `08-BOOTSTRAPPING.md` line 179 | "→ `01-MEMORY-SYSTEM.md` Memory Update Crowding for rationale" | ✓ Section exists at line 131 |
| `08-BOOTSTRAPPING.md` line 205 | "`01-MEMORY-SYSTEM.md` § Content Hierarchy for its role in maintenance decisions" | ✓ Section exists at line 197 |

### Missing Cross-References

This file lacks a dedicated **Cross-References** section at the bottom, unlike `03-SELF-IMPROVEMENT.md`, `04-EVIDENCE-AND-VALIDATION.md`, `06-FAILURE-MODES.md`, and `07-META-LEARNINGS.md`, which all have one. Several natural cross-references are absent:

1. **Memory Update Crowding → `03-SELF-IMPROVEMENT.md`** (Three Priorities Problem): The back-reference exists in `03-SELF-IMPROVEMENT.md` line 205, but `01-MEMORY-SYSTEM.md` doesn't reciprocate.
2. **Maintenance Protocol → `06-FAILURE-MODES.md`** (F1: Compaction Catastrophe): The maintenance protocol was directly motivated by F1, but no cross-reference exists.
3. **Update Rules → `04-EVIDENCE-AND-VALIDATION.md`** (Validation Gate): Different memory categories have different update rules, relevant here.
4. **Content Hierarchy → `03-SELF-IMPROVEMENT.md`** (Experimentation caution by level): The content hierarchy governs how cautiously to experiment, covered in `03-SELF-IMPROVEMENT.md`.
5. **WORKING_STYLE description → `02-INTERACTION-STYLE.md`** (Directive Confidence Scaling §6): The WORKING_STYLE file's reinforcement tracking is the mechanism for directive confidence.

### Bidirectionality Check

The `03-SELF-IMPROVEMENT.md` → `01-MEMORY-SYSTEM.md` reference is **unidirectional**. `01-MEMORY-SYSTEM.md` should reference back. Same for `08-BOOTSTRAPPING.md`'s three references. The cross-references are **accurate but not bidirectional**.

## Findings

### Refinements

**R1: WORKING_STYLE description could mention the retention policy.**
Lines 11-36 describe the WORKING_STYLE file. The description covers structure and fields well but omits that the file should contain a retention policy governing when directives may be archived. The source `WORKING_STYLE.md` has a prominent "Retention and Evaluation" section (lines 6-13) with 7 rules. The generalized file's Maintenance Protocol (line 157) partially covers this, but the WORKING_STYLE description itself should note that this file includes retention rules.

Suggested addition after line 36:
```
**Retention policy** (include in the file):
- Silence ≠ irrelevance: absence of corrective feedback means a directive is working, not expendable
- Compaction = generalization, not deletion: merge related directives; preserve reinforcement counts
- Archival threshold: only narrowly scoped, non-reinforced directives may be archived — never silently removed
```

**R2: SESSION_LOG living summary could be more specific.**
Line 44 says "Living summary at top: current state of the engagement (active focus, phase per workstream, key references)." The source `SESSION_LOG.md` shows a richer living summary with: active commit/version, per-workstream status table, policy notes, timeline, and prior analysis references. A generalized version:

Suggested replacement for line 44:
```
- **Living summary** at top: what the engagement is working on, status per workstream (table format), key policies/constraints, references to prior analysis rounds
```

**R3: The "Implementation Pattern: Always-Injected Checklists" section (lines 146-155) is excellent** but could note one additional property: **actionability** — each check should map to a specific memory file/action, not just a yes/no question. The source checklist (`03-memory-update-triggers.mdc`) demonstrates this: each trigger maps to a specific file update (feedback → WORKING_STYLE, artifact → SESSION_LOG, etc.).

**R4: Health Checks section (lines 189-195) could mention checking for duplicated data drift.** `07-META-LEARNINGS.md` §10c describes how duplicated data between system rules and memory files drifts. The health check is the natural place to catch this.

### Extensions

**E1: Active Retrieval Protocol (significant gap).**
The source `00-memory-system.mdc` lines 61-75 describes a session-start active retrieval protocol:

> Memory files are not auto-injected — they live on a reference shelf. At session start, **proactively read and evaluate**:
> 1. `SESSION_LOG.md` — Audit State summary (top) + last 1–2 session entries + Open Questions table
> 2. `WORKING_STYLE.md` — scan for directions relevant to the task at hand
> 3. `CONCLUSIONS.md` — only if the session involves validating or revisiting findings

The `00-OVERVIEW.md` mentions "Why Active Retrieval, Not Auto-Injection" as a key design decision. But `01-MEMORY-SYSTEM.md` — the file that should operationalize this — has no Active Retrieval section. The Health Checks section (line 189) implies reading memory at session start but doesn't describe *what* to read, *in what order*, or *how deeply*.

Suggested new section after "Update Rules" and before "Maintenance Protocol":

```markdown
## Active Retrieval

Memory files are not auto-injected into every prompt. They sit on a reference shelf. The agent must proactively read them.

### At Session Start

Read selectively, in this order:

1. **SESSION_LOG** — Living summary (top) + last 1-2 session entries + Open Questions table. Goal: orient to current state.
2. **WORKING_STYLE** — Scan for directives relevant to the current task. Goal: prime behavioral calibration.
3. **CONCLUSIONS** — Only if the session involves validating or revisiting findings. Goal: avoid re-deriving known results.
4. **TECHNICAL** — Only if doing technical work in the domain. Goal: access verified formulas, algorithms, code map.
5. **CHANGELOG** — Only during self-evaluation or compaction. Goal: recall past failures and structural changes.

### During Work

Connect current work to prior findings, open questions, and established patterns. Don't wait to be reminded.

### Why Active, Not Automatic

Auto-injecting all memory files into every prompt would pollute context with irrelevant content. Active retrieval forces the agent to decide what's relevant — itself a form of learning. It also prevents the memory system from degrading performance by consuming context budget on every turn.
```

**E2: Validation Gate mention in Update Rules.**
The source `00-memory-system.mdc` lines 34-47 describes the validation gate directly in the memory system file, because it governs *how memory is updated*. The generalized file's Update Rules (lines 109-130) describe when and how to update, but omit the critical distinction: technical conclusions require human validation for `verified` status, while operational content is freely updated.

Suggested addition after line 120 (after the "How to Update" bullets):

```markdown
### Validation Gate for Memory Updates

Not all memory content follows the same update rules:

- **Technical conclusions** (findings about the system being analyzed): The agent independently records at `unverified` or `evidence-supported`. Only the human can elevate to `verified`. Proactively present when evidence is sufficient.
- **Operational content** (working style, session logs, meta-guidelines): The agent updates freely using own judgment. No human gate required.

→ `04-EVIDENCE-AND-VALIDATION.md` for full treatment.
```

**E3: Self-evaluation questions for the memory system.**
The source `00-memory-system.mdc` lines 91-98 has 7 specific questions for periodic evaluation of the memory system:

> - Is the current structure serving its purpose?
> - Are there unused categories or overflowing ones?
> - Do update patterns suggest a better organization?
> - Is the system too complex? Too shallow?
> - Do new directions conflict with current system rules?
> - Did I fail to follow a guideline? If so, is the guideline unclear, or did I miss it?
> - Did the human correct my process? If so, which rule should have caught this?

These are memory-system-specific and belong here (in addition to the broader self-reflection protocol in `03-SELF-IMPROVEMENT.md`). Suggested addition in the Maintenance Protocol or as a new subsection "Periodic Self-Evaluation."

**E4: Pattern extraction trigger in Update Rules.**
The source `00-memory-system.mdc` line 32 states a memory update trigger:

> **Pattern extraction trigger**: When something takes 3+ iterations to get right (documentation, code, analysis), extract the pattern into `WORKING_STYLE.md` as a direction. Don't wait for the auditor to point it out.

This is absent from the generalized file's "When to Update" section (lines 113-121). It's well covered in `03-SELF-IMPROVEMENT.md`, but the source places it in the memory update context for a reason — it's a trigger condition for a specific type of memory write. A brief mention with cross-reference would be appropriate:

Suggested addition to the "When to Update" list (after item 6):
```
7. **Pattern emerging from repeated friction?** (3+ iterations on similar task) → Extract into WORKING_STYLE as a new directive (→ `03-SELF-IMPROVEMENT.md` §Pattern Extraction for protocol)
```

**E5: Directive Confidence — brief mention.**
The source `00-memory-system.mdc` lines 77-85 describes how directive confidence varies based on reinforcement. This directly relates to how WORKING_STYLE should be interpreted and is absent from the WORKING_STYLE description in this file. While fully covered in `02-INTERACTION-STYLE.md` §6, a brief note in the WORKING_STYLE description would help:

Suggested addition in the WORKING_STYLE section (after "Design principle" at line 26):
```
**Confidence interpretation**: Reinforcement count determines compliance level — frequently reinforced = stable/high compliance; recently added = experimental/open to modification; contradicted = invalidated. → `02-INTERACTION-STYLE.md` §6 for the full confidence ladder.
```

**E6: Retention Policy as a distinct concept.**
The Maintenance Protocol (lines 162-168) covers compaction safety rules. But the *retention policy* — when to keep vs. archive directives — is a related but distinct concept. The source `WORKING_STYLE.md` lines 6-13 has "Retention and Evaluation" with rules like "Silence ≠ irrelevance," "Relevance ranking: broad + reinforced = permanent; narrow + unreinforced = archival candidate." This is partially in the Maintenance Protocol but not explicitly called out as a retention policy. This could be a subsection within Maintenance Protocol or merged into R1 above.

### Corrections

No factual or structural errors found. The content that is present accurately represents the source material. The Content Hierarchy table matches both the source (`00-memory-system.mdc`) and cross-referenced discussions in `07-META-LEARNINGS.md` and `08-BOOTSTRAPPING.md`.

One minor observation: The file tags (e.g., `[long-running]`, `[technical]`) from the PLAN.md tier system are used on section headings (lines 12, 39, 80, 99, 132, 158) but inconsistently — some sections have them, some don't. The Health Checks, Scaling, and Content Hierarchy sections lack tier tags. Either all sections should have them or the tags should be applied more selectively with a rationale.

### Abstractions/Generalizations

The file is well-generalized. No domain-specific content (protocol names, specific formulas, audit terminology) remains. All references to the Tidal Protocol audit have been appropriately stripped.

One mild domain-specificity:
- Line 77: "Scope tag: When referencing specific code versions (commits, line numbers), tag the scope at the top. Protocol-level knowledge carries forward; line numbers need re-verification." — This is phrased for a code audit context but generalizes to any work with versioned references. Could be slightly broadened: "When referencing versioned artifacts (code at specific commits, documents at specific revisions), tag the version scope. Domain-level knowledge carries forward; artifact-specific references need re-verification when the version changes."

### Other

**O1: Missing Cross-References section.**
Files `03-SELF-IMPROVEMENT.md`, `04-EVIDENCE-AND-VALIDATION.md`, `06-FAILURE-MODES.md`, and `07-META-LEARNINGS.md` all end with a dedicated `## Cross-References` section listing related content in other files. `01-MEMORY-SYSTEM.md` does not, despite having multiple natural cross-reference points. Adding one would improve consistency and navigability.

Suggested section at the end of the file:
```markdown
## Cross-References

- Memory Update Crowding / Three Priorities Problem → `03-SELF-IMPROVEMENT.md` (The Three Priorities Problem)
- Maintenance Protocol / Compaction Catastrophe → `06-FAILURE-MODES.md` (F1)
- Validation gate for memory updates → `04-EVIDENCE-AND-VALIDATION.md` (The Validation Gate)
- Directive confidence and reinforcement tracking → `02-INTERACTION-STYLE.md` §6 (Directive Confidence Scaling)
- Content Hierarchy / error-recovery → `07-META-LEARNINGS.md` §10b
- Content Hierarchy / change-frequency → `08-BOOTSTRAPPING.md` § Content Hierarchy
- Self-evaluation questions → `03-SELF-IMPROVEMENT.md` (Self-Reflection Protocol, Periodic)
- Bootstrapping the memory system from scratch → `08-BOOTSTRAPPING.md` (First-Session Template)
```

**O2: The "Implementation Pattern: Always-Injected Checklists" (lines 146-155) is one of the strongest sections in the file.** It successfully generalizes a specific solution into a reusable pattern with clear properties (position, specificity, brevity). This is the kind of generalization the whole document set should aspire to.

**O3: Structural suggestion.** The file flows: Architecture → Update Rules → Maintenance → other. The missing Active Retrieval section (E1) would fit naturally between Update Rules and Maintenance, creating a complete lifecycle: what the files are (Architecture) → how to read them (Active Retrieval) → when/how to write them (Update Rules) → how to maintain them (Maintenance). Alternatively, Active Retrieval could precede Update Rules since reading precedes writing in the session lifecycle.

## Verdict

**Changes warranted: yes. Priority: high.**

The file's existing content is accurate and well-generalized, but the **absence of the Active Retrieval protocol (E1) is a significant gap** — an agent reading this file would know what memory files to create and how to update them, but not how to *use* them at session start. This is one of the most important operational details in the source material. The missing Validation Gate mention (E2) and Cross-References section (O1) are medium-priority. The remaining extensions (E3-E6) and refinements (R1-R4) are low-priority polish.

| Priority | Items |
|---|---|
| **High** | E1 (Active Retrieval), O1 (Cross-References section) |
| **Medium** | E2 (Validation Gate in update rules), E4 (Pattern extraction trigger), R1 (Retention policy in WORKING_STYLE description) |
| **Low** | E3 (Self-evaluation questions), E5 (Directive confidence mention), E6 (Retention policy section), R2-R4 (refinements), O3 (structural reordering) |
