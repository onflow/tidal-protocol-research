# Auditor Guide: Tidal Protocol Audit with Adaptive Memory

## What This Is

A Cursor IDE setup where the AI assistant maintains persistent memory across sessions. The AI:
- Abstracts algorithmic details into formulas and pseudo-code
- Learns from your corrections and preferences
- Adapts its explanations to your needs
- Tracks conclusions, assumptions, and open questions

## Quick Start

1. **Open the workspace** in Cursor: `/Users/alex/Git/tidal-protocol-research/`
2. **Start a conversation** asking about any aspect of the codebase
3. **Correct and guide** — the AI learns from your feedback

That's it. The memory system operates automatically.

## How the Learning Loop Works

```
You ask/direct → AI responds → You correct/confirm → AI updates memory → Better responses
```

The AI tracks:
- **Technical knowledge**: Terminology, formulas, algorithms (in `memory/TECHNICAL.md`)
- **Working style**: How you prefer to receive information (in `memory/WORKING_STYLE.md`)
- **Conclusions**: What's been validated or invalidated (in `memory/CONCLUSIONS.md`)

### Giving Directions

Be explicit about preferences. Examples:

- "Always show me the code reference when presenting a formula"
- "I prefer to see the mathematical invariant before the implementation"
- "Don't explain basic Python — I know it"
- "When discussing health factors, always relate back to liquidation risk"

The more consistently you give a direction, the more reliably the AI follows it.

### Correcting Mistakes

When the AI gets something wrong:
1. State the correction directly
2. The AI will acknowledge, update memory, and restate understanding
3. Confirm or refine further

Example:
> **AI**: The liquidation threshold is 80%
> **You**: No, it's configurable per asset. Check `protocol.py` line 142.
> **AI**: Corrected — liquidation threshold is per-asset, not global. [Updates memory]

### Validating Conclusions

The AI will actively seek validation when it finds conclusive evidence:

> **AI**: I found the yield token formula in `yield_tokens.py:47`. It matches V(t) = V₀(1+APR)^(t/525600). The code is:
> ```python
> value = initial_price * (1 + apr) ** (minutes / 525600)
> ```
> Can I mark this as validated?

You confirm, refine, or challenge. The AI won't passively wait — it will flag when evidence looks conclusive.

You can also point out validated information directly:
> "Confirmed: liquidation penalty is 5%, see `liquidator.py:89`"

## Suggested Starting Points for Phase 2

### Option A: Top-Down System Overview
Ask: *"Give me a one-paragraph summary of what this simulation does, then list the 5 most important algorithmic components."*

### Option B: Specific Domain Deep-Dive
Pick a domain and go deep:
- *"Explain the health factor system — formula first, then how agents use it"*
- *"How does MOET maintain its peg? Start with the mechanism, then the math"*
- *"Walk me through a liquidation cascade scenario"*

### Option C: Code-First Exploration
Point at specific code:
- *"Abstract `tidal_protocol_sim/core/uniswap_v3_math.py` — what are the core mathematical operations?"*
- *"What does `high_tide_agent.py` decide, and based on what inputs?"*

### Option D: Assumption Verification
Challenge stated assumptions:
- *"The memory says liquidation penalty is 5%. Verify this in the code."*
- *"Is the 10% reserve ratio target hardcoded or configurable?"*

## What to Expect

**Early sessions**: The AI will ask clarifying questions and make mistakes. This is normal — it's calibrating to your expertise level and preferences.

**After a few interactions**: Responses become more aligned with your style. Technical depth matches your needs.

**Over time**: The memory accumulates verified formulas, validated conclusions, and refined working patterns. New sessions start from this foundation.

## Checking Memory State

You can inspect what the AI has learned:

| File | Contents |
|------|----------|
| `memory/TECHNICAL.md` | Terminology, formulas, algorithms, code map |
| `memory/WORKING_STYLE.md` | Your preferences and directions |
| `memory/CONCLUSIONS.md` | Validated/invalidated findings |
| `memory/SESSION_LOG.md` | History of significant interactions |

You can also ask the AI directly:
- *"What do you currently understand about the health factor system?"*
- *"What assumptions have we validated so far?"*
- *"What working style directions are you following?"*

## Editing Memory Directly

You can edit the memory files directly if needed. The AI reads them at the start of relevant conversations.

Common edits:
- Correct a wrong formula
- Add terminology you want consistently used
- Remove outdated conclusions
- Adjust working style preferences

## Tips for Effective Collaboration

1. **Be direct** — The AI responds well to clear, explicit feedback
2. **Challenge claims** — Ask for code references; verify formulas
3. **State scope** — "This direction applies generally" vs "Just for this problem"
4. **Summarize periodically** — "Let's capture what we've established about X"
5. **Ask for abstraction levels** — "Give me the one-liner, then the full derivation"

## The Goal

By the end of the audit, you should have:
- Verified mathematical models of core protocol mechanics
- Validated (or invalidated) key assumptions
- A compact knowledge base that accurately represents the simulation
- Confidence in the correctness of the implementation

The AI is your research assistant, not the authority. You verify. You conclude. The AI helps you get there efficiently.
