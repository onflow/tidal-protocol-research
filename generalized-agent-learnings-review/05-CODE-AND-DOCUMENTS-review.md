# Review: 05-CODE-AND-DOCUMENTS.md

## File Summary

Covers practical craft skills for code editing (minimal invasiveness, comment handling, consistency scope), document authoring (self-contained docs, terminology discipline, scoped references, cross-references, results over process, code references, abstraction guidelines, tooling rendering), script execution (pre-run analysis, output management), and git hygiene. The highest-reinforcement directive in the collection (Minimal Invasiveness, 4 reinforcements) lives here.

## Source Coverage

### Primary Sources

| Source File | Relevance | Coverage |
|------------|-----------|----------|
| `memory/WORKING_STYLE.md` §Code Editing | Primary | **Complete.** All 3 directives (minimal invasiveness, comment handling, consistency scope) captured with full detail, including reinforcement counts, corollaries, and pre-flight checks. |
| `memory/WORKING_STYLE.md` §Document Authoring | Primary | **Nearly complete.** 7 of 8 entries captured. "GitHub-linked code refs" partially captured — the principle of citing the version-controlled URL is present, but the guidance on *which version to cite* (reader's working version vs. historical) is missing. See Extensions §2. |
| `memory/WORKING_STYLE.md` §Simulation Execution | Primary | **Mostly complete.** 4 of 5 entries captured. "Piped input for prompts" (`printf` with explicit `\n` per prompt) omitted. See Extensions §1. Virtual environment path (domain-specific) correctly omitted. |
| `memory/WORKING_STYLE.md` §Git Hygiene | Primary | **Complete.** "Clean up checkout artifacts" fully captured. |
| `.cursor/rules/02-technical-domain.mdc` §Abstraction Guidelines | Moderate | **Complete.** The 5-point guideline is captured and expanded with a useful paragraph explaining when it applies and what the abstraction is (lossy compression). |
| `.cursor/rules/00-memory-system.mdc` §How to Update | Low | "References over copies", "snippets over sentences" — these are memory-update rules, not document authoring rules. Correctly NOT duplicated in 05; they live in `01-MEMORY-SYSTEM.md`. |
| `.cursor/rules/01-audit-interaction.mdc` | Low | "When Presenting Technical Content" pattern overlaps with document structure guidance. Correctly placed in `02-INTERACTION-STYLE.md`, not duplicated here. |
| `AUDITOR_GUIDE.md` | None | Human-facing; no content relevant to 05. |

### Content NOT Captured (correctly excluded)

- `memory/WORKING_STYLE.md` §Exhaustive Claims — lives in `04-EVIDENCE-AND-VALIDATION.md` (correct placement)
- `memory/WORKING_STYLE.md` §Simulation Reproduction Debugging — lives in `04-EVIDENCE-AND-VALIDATION.md` §Tracing Root Causes (correct placement)
- `memory/WORKING_STYLE.md` §Internal Classifications (Post-delivery vs Pre-existing) — lives in `04-EVIDENCE-AND-VALIDATION.md` §Methodology Separation (correct placement)
- `memory/WORKING_STYLE.md` §Virtual Environment — domain-specific, correctly omitted per PLAN.md extraction principle 1

## Internal Consistency

### Cross-references TO this file from other files

| Source | Reference | Accurate? |
|--------|-----------|-----------|
| `00-OVERVIEW.md` reading order | Position 7: "domain-specific craft (technical collaboration)" | **Accurate.** Correctly characterizes the file's content and tier. |
| `04-EVIDENCE-AND-VALIDATION.md` cross-refs | "Root cause tracing methodology → `05-CODE-AND-DOCUMENTS.md` (code references in documents)" | **Slightly misleading.** 05 covers *maintaining* code references in documents, not root cause tracing methodology. The tracing methodology is entirely within 04 itself. The connection is that code reference maintenance is a downstream task after applying the root cause tracing method, but the cross-reference implies 05 contains tracing guidance. Suggest rewording to: "Code reference maintenance after changes → `05-CODE-AND-DOCUMENTS.md` (Code References in Documents)". |
| `03-SELF-IMPROVEMENT.md` §Examples of Extracted Patterns | Lists "Comments deleted during code rewrites, 3×" and "Line references going stale after edits, 2×" | **Accurate.** These patterns feed into 05's Comment Handling and Code References in Documents directives. No explicit back-reference needed — the connection is implicit and clear. |
| `06-FAILURE-MODES.md` | F2 (clean-slate rewriting), F5 (stale cross-references), F9 (scoped IDs out of context) | **Accurate.** All three failure modes have corresponding prevention mechanisms in 05. However, 05 does not reference 06 in return. |

### Cross-references FROM this file to other files

**None exist.** This is the only file in the collection without a `## Cross-References` section. Every other file (`01` through `04`, `06`, `07`, `08`) has one. This is a structural gap — see Findings §Refinements §1.

### Overlap with 02-INTERACTION-STYLE.md

`02-INTERACTION-STYLE.md` §Communication Micro-Rules contains one-line summaries of four topics that have full sections in 05:

| 02 Micro-Rule | 05 Section | Overlap Type |
|---------------|------------|--------------|
| "Self-contained documents" | §Self-Contained Documents | Summary ↔ Detail |
| "Cross-references" | §Cross-References | Summary ↔ Detail |
| "Scoped IDs need source context" | §Scoped References | Summary ↔ Detail |
| "Results over process" | §Results Over Process | Summary ↔ Detail |

This is a reasonable split (02 gives the quick-reference table, 05 gives the full guidance), but **neither file cross-references the other for these items**. A reader of 02 doesn't know 05 has the detail; a reader of 05 doesn't know 02 has the summary context.

## Findings

### Refinements

#### 1. Add a Cross-References section

Every other file in the collection has one. Suggested content:

```markdown
---

## Cross-References

- Minimal invasiveness, comment handling, consistency scope as failure modes → `06-FAILURE-MODES.md` (F2: clean-slate rewriting)
- Stale cross-references as a failure mode → `06-FAILURE-MODES.md` (F5)
- Scoped IDs as a failure mode → `06-FAILURE-MODES.md` (F9)
- Document authoring micro-rules (summary versions) → `02-INTERACTION-STYLE.md` §Communication Micro-Rules
- Pattern extraction that produced these directives → `03-SELF-IMPROVEMENT.md` §Examples of Extracted Patterns
- Abstraction guidelines and the domain knowledge structure → `01-MEMORY-SYSTEM.md` §TECHNICAL
- Evidence standards for claims in documents → `04-EVIDENCE-AND-VALIDATION.md` §Evidence Standards
```

#### 2. Generality tier tags are inconsistent

Per PLAN.md, each directive should be tagged with `[universal]`, `[technical]`, or `[long-running]`. The file has `[technical]` on most top-level sections and sub-sections, but some subsections under Document Authoring are untagged while being grouped under a tagged parent. This works but is inconsistent with how 02-INTERACTION-STYLE.md individually tags each item.

Specifically, the Script Execution section has `[technical]` at the section level but its three subsections (Pre-Run Analysis, Output Management, Git Hygiene) are untagged. Git Hygiene could arguably be `[long-running]` (it matters most when working across versions/branches over time), though `[technical]` is defensible.

**Recommendation**: Add tier tags to subsections that could plausibly be a different tier than their parent. For the current file, `[technical]` is appropriate for everything, so the current approach is acceptable — just note the convention differs from 02.

#### 3. Sharpen the design-intent vs implementation comment distinction

The current text in "Consistency Scope" says:

> When an edit works around a bug without changing the design: preserve the design-intent comment, add a NOTE explaining the current deviation.

The source material (WORKING_STYLE.md) has a crisper formulation that better explains *why*:

> "Design-intent comments describe what the code is *supposed* to do and help future developers understand the scope of safe changes."

The "scope of safe changes" framing is the key insight — it tells you why design-intent comments matter even when the code has been changed. Suggest adding this to the "Distinguish two types of comments" bullet:

```markdown
- **Design-intent comments**: Describe what the code is _supposed_ to do, architectural decisions, rationale. These help future developers understand the scope of safe changes. Preserve these even when working around a bug — they document the intended design vs. the current deviation.
```

#### 4. Script Execution section title vs. file title mismatch

The file is titled "Code Editing and Document Authoring" but contains a third major section, "Script Execution Principles," plus "Git Hygiene" nested under it. The PLAN.md description says "Code editing principles, document authoring rules" — it doesn't mention script execution.

Options:
- **a)** Rename the file title to "Code, Documents, and Execution" (broader, accurate)
- **b)** Keep the title and note that script execution/git hygiene are included as closely related craft skills
- **c)** Move Script Execution to another file (04-EVIDENCE-AND-VALIDATION is the closest fit, since running scripts is usually about gathering evidence)

**Recommendation**: Option (a) or (b). The content fits together as "practical craft skills for technical work." Moving it would fragment a natural grouping. But the PLAN.md description should be updated if the title changes.

### Extensions

#### 1. Missing: technique for supplying interactive inputs non-interactively

WORKING_STYLE.md §Simulation Execution has "Piped input for prompts":

> `printf` with explicit `\n` per prompt. Never `echo ""` for multi-prompt scripts.

The current 05 §Pre-Run Analysis says "Count interactive prompts (`input()` calls or equivalent) — you need to supply these" but doesn't give the technique for actually supplying them in an automated/non-interactive context. For an AI agent running scripts, this is directly actionable.

Suggested addition to Pre-Run Analysis:

```markdown
1. Count interactive prompts (`input()` calls or equivalent) — you need to supply these
   - When piping input: use `printf` with explicit `\n` per prompt (not `echo ""` for multi-prompt scripts)
   - For complex input sequences: consider a heredoc or input file
```

This should be generalized beyond Python's `input()` to mention other patterns (stdin reads, CLI prompts).

#### 2. Missing: guidance on which version to cite in version-controlled code references

WORKING_STYLE.md §GitHub-linked code refs contains a generalizable principle:

> **Reference HEAD commit** on the working branch so readers with the latest code can navigate directly — citing the audited commit forces them to translate shifted line numbers. Use case-by-case judgment: if a reference specifically concerns code *before* changes, cite the original commit and note this.

The current 05 §Code References in Documents mentions "version-controlled URLs (e.g., GitHub permalinks at the relevant commit)" but doesn't specify which commit to prefer. This is a non-obvious decision with real impact on document usability.

Suggested addition:

```markdown
- For living documents: consider linking to version-controlled URLs (e.g., GitHub permalinks)
  - **Default**: cite the version the reader is most likely working with (typically HEAD or the latest branch commit)
  - **Exception**: when a reference specifically concerns a historical state (pre-fix, pre-change), cite that version and note it explicitly
  - Rationale: citing a stale version forces readers to translate shifted line numbers
```

#### 3. Missing: the abstraction guidelines' connection to domain knowledge structure

The Abstraction Guidelines section explains *how* to abstract code, but doesn't connect to *where* abstractions are stored. In the memory system, `TECHNICAL.md` is structured precisely around these abstractions (terminology, core formulas, algorithmic abstractions, assumptions, code map). This connection appears in `01-MEMORY-SYSTEM.md` §TECHNICAL but 05 doesn't link back.

A one-line note would suffice:

```markdown
These guidelines define the quality standards for abstractions stored in the domain knowledge file (→ `01-MEMORY-SYSTEM.md` §TECHNICAL).
```

### Corrections

#### 1. No factual errors found

All reinforcement counts match the source (WORKING_STYLE.md). All principles are faithfully represented. The generalization from domain-specific to general is accurate throughout.

#### 2. Minor: "Tooling Rendering Awareness" example specificity

The discovered example mentions "backtick spans inside link text" with a workaround specific to VS Code/Cursor. Per PLAN.md principle 1 ("No references to specific protocols, formulas, bugs, or codebases"), tool-specific mentions should be minimized. However, PLAN.md targets domain content (protocols, codebases), not tooling examples — and the section already frames this as a "Discovered example" illustrating a general principle. **No change needed**, but worth noting that the example is narrowly useful only to agents working in VS Code/Cursor-type environments.

### Abstractions/Generalizations

#### 1. Script Execution: Python-specific language

Several items use Python-specific terminology that could be generalized without losing the practical detail:

| Current (Python-specific) | Suggested (general + example) |
|--------------------------|-------------------------------|
| "`input()` calls" | "interactive prompts (e.g., `input()` in Python, `readline` in Node)" |
| "`sys.path`, imports" | "module/import resolution paths (e.g., `sys.path` in Python, `NODE_PATH` in Node)" |
| "`PYTHONUNBUFFERED=1`" | "unbuffered output (e.g., `PYTHONUNBUFFERED=1` for Python)" |

The current text is already parenthetical ("or equivalent") for `input()` and uses "or equivalent" for `PYTHONUNBUFFERED=1`. This is a minor improvement — the current level of generalization is adequate for most use cases.

#### 2. Output Management: principle vs. tool separation

The Output Management section mixes principles and Unix tool names. Consider restructuring to lead with the principle:

```markdown
### Output Management

Principles:
- **Unbuffered output** — prevents lost output on crash
- **Filtered output** — keeps signal-to-noise ratio high (e.g., suppress DEBUG lines)
- **Dual logging** — both terminal and file, for real-time monitoring and post-hoc analysis
- **Timestamped, descriptive log files** — reproducibility and provenance

Tool examples (Unix):
- Unbuffered: `PYTHONUNBUFFERED=1` or language equivalent
- Filtered: `grep --line-buffered -v "DEBUG"` or similar
- Dual logging: `tee` to both terminal and file
```

This separates the transferable principle from the implementation detail, making it easier for agents working in non-Unix environments.

### Other

#### 1. Overlap management with 02-INTERACTION-STYLE.md

As noted in Internal Consistency, four document-authoring topics exist as both one-line micro-rules in 02 and full sections in 05. This is the right division of labor, but both files should acknowledge it:

- In 02 §Communication Micro-Rules, add a note: "Full guidance for document authoring rules → `05-CODE-AND-DOCUMENTS.md`"
- In 05, the suggested cross-references section (Refinements §1) covers the return link.

#### 2. The file naturally groups into two tiers of universality

The Code Editing and Document Authoring sections are broadly applicable to any agent that edits code or writes documents. The Script Execution and Git Hygiene sections are more specialized (agents that run scripts in shell environments). If the file were to grow, splitting along this line would be natural. No action needed now, but worth noting for future maintainers.

#### 3. Section ordering

The current order (Code Editing → Document Authoring → Script Execution) makes sense as a progression from most to least universally applicable. This is good.

## Verdict

**Changes warranted: medium priority.**

The content quality is high — faithful to sources, well-generalized, and actionable. The main gaps are:

1. **Missing cross-references section** (structural consistency issue — every other file has one) — **high priority within this file**
2. **Two missing extensions** (piped input technique, version-to-cite guidance) — **medium priority**, both are directly actionable for agents
3. **Overlap with 02 not cross-referenced** — **medium priority**, affects navigability
4. **Minor generalization opportunities** in Script Execution — **low priority**, current text is adequate

No corrections needed. The file is one of the most faithful generalizations in the collection — reinforcement counts, corollaries, pre-flight checks, and nuanced distinctions (design-intent vs implementation comments) all survive the extraction intact.
