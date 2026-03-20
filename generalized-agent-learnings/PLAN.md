# Plan: Generalizing Agent Learnings

## Goal

Extract everything learned during a 7-week human-AI collaboration (code audit domain) into domain-independent guidance for an AI agent. The output should enable a fresh agent to replicate the evolved working style without re-learning from scratch.

## Source Material

All learnings were developed through iterative feedback with a technical human collaborator ("the auditor"). Sources:
- `memory/WORKING_STYLE.md` — 40+ directives with reinforcement tracking
- `memory/SESSION_LOG.md` — 18 session entries documenting evolution
- `memory/CHANGELOG.md` — directive lifecycle and meta-learnings
- `.cursor/rules/*.mdc` — system-level rules (4 files)
- `AUDITOR_GUIDE.md` — human-facing description of the system

## Extraction Principles

1. **Generalize away from the domain.** No references to specific protocols, formulas, bugs, or codebases. Replace domain examples with abstract or generic ones.
2. **Preserve the _why_.** Every directive exists because of a concrete failure or correction. State the principle and the failure mode it prevents, not the specific incident.
3. **Keep the meta-cognitive layers.** The most valuable learnings are about _how to learn_ — self-monitoring, pattern extraction, memory maintenance, failure recovery. These must be front and center.
4. **Audience is an AI agent.** Write as instructions/patterns, not prose. Dense, actionable, machine-parseable.
5. **Include the unsolved problems.** Some challenges (e.g., memory update crowding) are partially addressed but not fully solved. Document the current state of each.

## File Structure

| File | Purpose |
|------|---------|
| `PLAN.md` | This file — rationale and structure |
| `00-OVERVIEW.md` | System architecture: how files relate, reading order, when to consult what |
| `01-MEMORY-SYSTEM.md` | Persistent memory: file types, update rules, maintenance protocol, scaling |
| `02-INTERACTION-STYLE.md` | Human collaboration: communication, feedback loops, calibration |
| `03-SELF-IMPROVEMENT.md` | Self-reflection, learning, generalization, experimentation |
| `04-EVIDENCE-AND-VALIDATION.md` | Evidence gathering, validation gates, proactive engagement |
| `05-CODE-AND-DOCUMENTS.md` | Code editing principles, document authoring rules |
| `06-FAILURE-MODES.md` | Catalog of observed failure patterns with prevention strategies |
| `07-META-LEARNINGS.md` | Higher-order lessons about learning itself |
| `08-BOOTSTRAPPING.md` | How to start from scratch; the trajectory of learning; first-session template; transferring to new domains |

## Generalization Strategy

For each directive/learning, I ask:
- At what level of generality does this still hold?
- What failure mode does it prevent?
- Is it specific to the human collaborator, the domain, or fundamental to AI-human collaboration?
- Does it have an implicit goal that should be stated explicitly?

Three generality tiers:
1. **Universal** — applies to any AI-human collaboration (e.g., "state uncertainty explicitly")
2. **Technical collaboration** — applies when the joint task involves code/analysis (e.g., "verify code references after edits")
3. **Long-running engagement** — applies when the collaboration spans multiple sessions with accumulated state (e.g., "memory maintenance protocol")

Each directive is tagged with its tier.
