# Compliance & Security Framework

## 🔐 AI Safety Principles

ProjectMind enforces five core AI safety principles:

### 1. Least Authority
Each AI agent has **limited scope**:
- Coding agent: Can only suggest code, never write to disk
- Security agent: Can only flag issues, never disable checks
- Test agent: Can only generate tests, never modify source

### 2. No Autonomous Harm
AI is **never autonomous**:
- Every action requires human approval
- No silent file edits
- No automatic deployments
- No credential exposure

### 3. Explainability by Default
**All AI outputs must explain**:
- The reasoning
- The assumptions
- The limitations
- Alternative approaches

### 4. Context Integrity
AI can only reason about:
- Files that physically exist
- Parsed code structures
- Explicitly loaded constraints
- Previous approved decisions

### 5. Auditability
All actions are **logged and reviewable**:
- Decision logs in `.pmind/decisions/`
- Command history in terminal
- Context versions in git
- No hidden operations

---

## 📋 Compliance Checklist

### For High-Security Environments

- [ ] All LLM prompts logged to `.pmind/prompts/`
- [ ] All AI suggestions require approval before implementation
- [ ] Modify `project_context.yaml` to add organization policies
- [ ] Set up git hooks to prevent constraint violations
- [ ] Regular audits of decision logs

### For Small Teams

- [ ] Use default `project_context.yaml`
- [ ] Keep `.pmind/decisions/` in git history
- [ ] Review AI suggestions before accepting
- [ ] Document architectural decisions

### For Enterprises

- [ ] Custom constraint rules (see examples)
- [ ] AI policy enforcement layer (Phase 5)
- [ ] Security scanning integration
- [ ] Compliance reporting

---

## 🚫 AI Boundaries (HARD REFUSAL)

Your AI will refuse requests to:

❌ **Generate malware or exploit code**
❌ **Bypass security controls**
❌ **Violate licenses or terms of service**
❌ **Scrape private or personal data**
❌ **Break laws or regulations**
❌ **Edit files outside constraints**
❌ **Run arbitrary commands**
❌ **Access external systems without approval**

---

## 📊 Compliance Mapping

### EU AI Act (Levels of Compliance)

| Principle | ProjectMind | Status |
| --- | --- | --- |
| Transparency | Full audit trail | ✅ |
| Human oversight | Required for all actions | ✅ |
| Technical robustness | Deterministic core | ✅ |
| Data governance | Local-only processing | ✅ |
| Accountability | Decision logs | ✅ |

### SOC 2 Alignment

| Control | ProjectMind | Status |
| --- | --- | --- |
| Access control | Context-based | ✅ |
| Change management | Git + decision logs | ✅ |
| Monitoring | Audit trail | ✅ |
| Security policies | project_context.yaml | ✅ |

---

## 🔒 Project Constraints in YAML

Example custom constraints:

```yaml
constraints:
  no_autonomous_changes: true
  must_explain_reasoning: true
  respect_architecture: true
  
  # Add organization policies:
  custom_constraints:
    - "Never suggest removing security checks"
    - "Always respect PII and data privacy"
    - "Architectural decisions are immutable"
    - "All refactors require team approval"
    - "No external API calls without SecOps review"
```

---

## 📝 Decision Log Template

Create `.pmind/decisions/YYYYMMDD-title.md`:

```markdown
# Decision: [Title]
**Date**: 2026-03-01
**Status**: Proposed / Approved / Implemented / Rejected

## Problem
What issue led to this decision?

## Solution
What was decided?

## Reasoning
Why this solution?

## Constraints Checked
- Architecture: ✅
- Security: ✅
- Compliance: ✅

## Alternatives Considered
1. ...
2. ...

## Risk Assessment
- Upside: ...
- Downside: ...
- Mitigation: ...
```

---

## 🛡️ Security Best Practices

1. **Keep `project_context.yaml` in git** - Version your constraints
2. **Review `.pmind/decisions/` regularly** - Catch drift
3. **Use deterministic layers first** - AI is last resort
4. **Log all LLM interactions** - For compliance audits
5. **Update constraints quarterly** - Keep policies fresh

---

## 🚀 Phase 5: AI Policy Engine

Future versions will include:

- Automated constraint validation
- Policy enforcement middleware
- Compliance scoring dashboard
- Integration with security tools
- Automated refusal logic

For now: **Manual review required** ✅

---

## 📞 Questions?

Compliance questions → Check `project_context.yaml`
Security concerns → Create decision log
Feature limitations → See ARCHITECTURE.md
