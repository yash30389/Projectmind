# ProjectMind - Knowledge System Quick Reference

## The Three-Tier Knowledge System (At a Glance)

### What Problem Are We Solving?
ProjectMind can analyze code, but it doesn't understand **WHY** code exists or **WHAT** the project is trying to achieve. We're building a multi-tier knowledge system to fix this.

---

## Quick Navigation

### Tier 1: Business & Product Context
**File**: BUSINESS_CONTEXT.md
**Size**: ~115 lines
**Purpose**: "What does this project do and why?"

**Key Sections:**
- Product Vision
- Target Users
- Value Propositions
- Core Principles (especially: local-only, privacy-first)
- Success Metrics

**Agent Usage:**
```python
agent.business_context  # Access business context
agent.get_context_snippet("business")  # Get specific section
```

---

### Tier 2: Architecture & Design
**File**: ARCHITECTURE_AND_DECISIONS.md
**Size**: ~300 lines
**Purpose**: "How is the system built and WHY?"

**Key Sections:**
- System Architecture (diagram)
- 6 Key Design Decisions (multi-agent, local-only, plugin registry, embeddings, workflows, separation of concerns)
- Component Relationships
- Data Flow
- Error Handling Strategy
- Performance Trade-offs
- Extensibility Points

**Agent Usage:**
```python
agent.architecture  # Access architecture context
agent.get_context_snippet("architecture")  # Get diagram
agent.get_context_snippet("decisions")  # Get decision rationale
```

---

### Tier 3: Codebase Intelligence
**Files**: All Phase 1-5 implementation
**Size**: ~5,000 lines
**Purpose**: "What is the actual code doing?"

**Coverage:**
- Phase 1: Repository scanning and structure discovery
- Phase 2: Code analysis and summarization
- Phase 3: Semantic search with embeddings
- Phase 4: Multi-agent orchestration
- Phase 5: Security and compliance

**Agent Usage:**
```python
# Automatically available in all agents
result = agent.execute("analyze", {"code": "..."})
```

---

## Why Each Tier Matters

| Tier | What It Answers | When Used |
|------|-----------------|-----------|
| **Tier 1** | "Should we do this?" | Evaluating new requirements |
| **Tier 2** | "How should we do this?" | Designing solutions |
| **Tier 3** | "Can we do this?" | Implementing and validating |

---

## Implementation Roadmap

### Phase A: Knowledge System Foundation ✅ COMPLETE
- [x] Create BUSINESS_CONTEXT.md (Tier 1)
- [x] Create ARCHITECTURE_AND_DECISIONS.md (Tier 2)
- [x] Create TEAM_STANDARDS.md (Tier 2)
- [x] Create KNOWLEDGE_SYSTEM_IMPLEMENTATION.md (guide)

### Phase B: Agent Integration (NEXT)
- [ ] Update Agent base class to load all contexts
- [ ] Add `get_context_snippet()` method
- [ ] Update 3 agents to use context in tools
- [ ] Update workflows to be context-aware

### Phase C: Testing & Validation
- [ ] Write tests for context loading
- [ ] Write tests for context-aware tools
- [ ] Update integration tests
- [ ] Validate all 106 tests still pass

### Phase D: Enhanced Capabilities
- [ ] Context-aware code recommendations
- [ ] Architectural alignment checking
- [ ] Standards compliance validation
- [ ] Reasoning explanations in output

---

## Example: How Knowledge System Works

### Before (Current)
```
User: "Analyze this code"
↓
Agent: "Complexity: high, 500+ lines"
(No context about project goals or constraints)
```

### After (With Knowledge System)
```
User: "Analyze this code"
↓
Agent loads BUSINESS_CONTEXT.md
Agent loads ARCHITECTURE_AND_DECISIONS.md
Agent loads TEAM_STANDARDS.md
↓
Agent: "Complexity: high, 500+ lines
         → Consider refactoring per separation of concerns (ARCHITECTURE)
         → Follow naming conventions in TEAM_STANDARDS
         → Aligns with privacy-first principle (BUSINESS_CONTEXT)"
(Recommendations now grounded in project context)
```

---

## File Organization

```
docs/
├── BUSINESS_CONTEXT.md              [Tier 1] What/Why
├── ARCHITECTURE_AND_DECISIONS.md    [Tier 2] How/Why
├── TEAM_STANDARDS.md                [Tier 2] Standards
└── KNOWLEDGE_SYSTEM_IMPLEMENTATION.md [Guide]

projectmind/
└── agents/
    └── base_agent.py  [Will load all context files]
```

---

## Key Concepts to Understand

### "Separation of Concerns" (Core Design Decision)
- Each component has one job
- Each phase handles one domain
- Agents specialize in different analysis areas
- **Impact on code**: Functions should be focused, classes should have single purpose

### "Local-Only Architecture" (Core Business Value)
- All processing on user's machine
- No cloud dependencies
- No data leaves the computer
- **Impact on code**: No API calls to external services, no cloud uploads

### "Multi-Agent Pattern" (Architectural Choice)
- Multiple specialized agents (Code, Security, Documentation)
- Each agent maintains its own memory
- Agents coordinate through WorkflowOrchestrator
- **Impact on code**: Agent classes inherit from base Agent, register tools with registry

---

## Common Questions Answered by Knowledge System

### "Should I add this feature?"
→ Check BUSINESS_CONTEXT for alignment with vision

### "How should I structure this code?"
→ Check ARCHITECTURE_AND_DECISIONS for pattern examples

### "What naming conventions should I use?"
→ Check TEAM_STANDARDS for naming rules

### "Does this violate our architecture?"
→ Check ARCHITECTURE_AND_DECISIONS for design decisions

### "Why was code written this way?"
→ Check ARCHITECTURE_AND_DECISIONS for decision rationale

### "What's the correct error handling approach?"
→ Check TEAM_STANDARDS for error handling standards

---

## Integration Checklist

After each document is created and before agents are updated:

- [ ] Document is in `docs/` folder
- [ ] Document is mentioned in this quick reference
- [ ] Document is referenced in KNOWLEDGE_SYSTEM_IMPLEMENTATION.md
- [ ] Content is clear and well-organized
- [ ] No typos or formatting issues
- [ ] Cross-references are accurate
- [ ] Examples are code-valid

---

## Success Criteria

The knowledge system is working when:

✅ Agents can access all context documents
✅ Agents reference context in tool outputs
✅ Recommendations align with project values
✅ System explanations cite which document they come from
✅ New developers can understand project by reading Tiers 1-2
✅ Automated tools can validate code against known standards

---

## Performance Impact

**Context Loading**: ~10-50ms per agent initialization (cached in memory)
**Context Retrieval**: ~1-5ms per query (in-memory string search)
**Agent Overhead**: Minimal (~5% increase in execution time)

---

## Future Extensions

### Tier 2.5: Patterns & Recipes
- "How to add a new agent?"
- "How to add a new phase?"
- "How to implement feature type X?"

### Tier 2.6: Failure Modes
- "Known bugs and workarounds"
- "Performance bottlenecks"
- "How to debug common issues"

### Tier 4: Runtime Learning
- Track which recommendations are accepted
- Learn project-specific patterns
- Adapt future recommendations

---

## References

- **Implementing**: See KNOWLEDGE_SYSTEM_IMPLEMENTATION.md
- **Decisions**: See ARCHITECTURE_AND_DECISIONS.md
- **Standards**: See TEAM_STANDARDS.md
- **Product**: See BUSINESS_CONTEXT.md

---

## Need Help?

1. **"What should the agent do?"** → Check BUSINESS_CONTEXT
2. **"How should the agent do it?"** → Check ARCHITECTURE_AND_DECISIONS
3. **"What rules apply?"** → Check TEAM_STANDARDS
4. **"How to implement context loading?"** → Check KNOWLEDGE_SYSTEM_IMPLEMENTATION

