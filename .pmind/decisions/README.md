# Decisions

This directory contains architectural and strategic decisions for ProjectMind.

## Format

Each decision is recorded as: `YYYYMMDD-slug.md`

Example: `20260301-four-layer-architecture.md`

## How to Add a Decision

1. Create new file with date and slug
2. Use the template below
3. Commit to git
4. Reference in relevant code comments

## Template

```markdown
# Decision: [Title]
**Date**: YYYY-MM-DD
**Status**: Proposed | Approved | Implemented | Rejected

## Problem
What issue led to this decision?

## Solution
What was decided?

## Reasoning
Why this solution?

## Constraints Checked
- Architecture: ✅/❌
- Security: ✅/❌
- Compliance: ✅/❌

## Alternatives Considered
1. ...
2. ...

## Risk Assessment
- Upside: ...
- Downside: ...
- Mitigation: ...
```

---

## Current Decisions

### 20260301-four-layer-architecture.md
**Status**: Implemented

The system is split into four independent layers:
1. Repository Intelligence (deterministic)
2. Context & Memory (governance)
3. CLI Interface (explicit)
4. Architecture Discipline (long-term)

This allows each layer to be replaced independently.
