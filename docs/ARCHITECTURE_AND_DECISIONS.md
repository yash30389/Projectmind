# ProjectMind - Architecture & Design Decisions

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│              (projectmind/cli/main.py)                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Multi-Agent Orchestrator                   │
│          (projectmind/agents/workflow_orchestrator.py) │
└─────────────────────────────────────────────────────────┘
          ↙            ↓            ↘
    ┌─────────┐  ┌─────────┐  ┌──────────────┐
    │CodeAnalyzer│SecurityAgent│DocumentationAgent
    │  Agent   │  Agent    │  Agent       │
    └─────────┘  └─────────┘  └──────────────┘
         ↓            ↓             ↓
    ┌─────────────────────────────────────────┐
    │   Phase 1-5 Specialized Modules         │
    │  (scanners, parsers, detectors, etc.)   │
    └─────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Multi-Agent Architecture (Phase 4)
**Decision**: Use specialized agents (CodeAnalyzer, Security, Documentation) rather than monolithic analyzer.

**Why:**
- Each agent focuses on one concern (code quality, security, docs)
- Agents can run in parallel or sequence via WorkflowOrchestrator
- Easy to add new agents without modifying existing code
- Each agent maintains its own memory and context

**Trade-offs:**
- Slight overhead from agent instantiation
- More complex than single analyzer
- Better for scaling to 10+ specialized analyzers

---

### 2. Local-Only Architecture (Entire System)
**Decision**: All processing happens on user's machine; no cloud calls.

**Why:**
- Privacy – no code leaves the computer
- Works offline
- No API costs
- GDPR/compliance-friendly

**Trade-offs:**
- Requires more local compute
- Can't use cutting-edge cloud models
- User responsible for updates

---

### 3. Plugin-Based Tool Registry (Phase 4)
**Decision**: ToolRegistry allows dynamic tool registration instead of hard-coded methods.

**Why:**
- New tools can be added without modifying Agent classes
- Tools can be enabled/disabled at runtime
- Each tool maintains its own execution stats
- Extensible for user-defined tools

**Example:**
```python
agent.register_tool("custom_check", my_function)
```

---

### 4. Vector Embeddings for Semantic Search (Phase 3)
**Decision**: Use embeddings instead of regex/keyword matching for code search.

**Why:**
- Can find code by meaning, not just exact keywords
- "Add numbers" finds `def sum(a, b)` 
- More intuitive for developers
- Handles synonyms automatically

**Trade-offs:**
- Slower than regex (milliseconds vs microseconds)
- Requires vector storage
- Embedding quality depends on training

---

### 5. Workflow-Based Execution (Phase 4)
**Decision**: Workflows support multi-step analysis with dependencies.

**Why:**
- Code analysis → Security check → Documentation generation
- Steps can depend on previous results
- Conditional execution based on findings
- Reusable workflow templates

**Example:**
```
Step 1: Analyze complexity
  ↓ (if complexity > threshold)
Step 2: Run security scan
  ↓ (regardless)
Step 3: Generate documentation
```

---

### 6. Separation of Concerns (All Phases)
**Decision**: Each phase handles one domain:

| Phase | Domain | Responsibility |
|-------|--------|-----------------|
| 1 | Discovery | Map project structure |
| 2 | Analysis | Understand code semantics |
| 3 | Search | Find code by meaning |
| 4 | Orchestration | Coordinate agents |
| 5 | Security | Threat detection & compliance |

**Why:**
- Each phase can be understood independently
- No circular dependencies
- Easy to test and maintain
- Clear upgrade path

---

## Component Relationships

### Phase 1: Repository Intelligence
```
Scanner → Analyzer → Context Generator
  ↓         ↓             ↓
[Finds files] [Extracts structure] [Builds project model]
```

### Phase 2: Code Analysis
```
PythonParser → CodeSummarizer → DocumentationGenerator
  ↓             ↓                ↓
[Parse AST] [Extract semantics] [Generate docs]
```

### Phase 3: Embeddings & Search
```
EmbeddingGenerator → VectorStore → SemanticSearch
  ↓                   ↓             ↓
[Convert code] [Index vectors] [Find similar code]
```

### Phase 4: Multi-Agent Orchestration
```
WorkflowOrchestrator → [Agent1, Agent2, Agent3] → Results
  ↓
[Coordinates execution with dependency resolution]
```

### Phase 5: Security & Compliance
```
ThreatDetector → PolicyEngine → ComplianceReporter
  ↓              ↓               ↓
[Find issues] [Check rules] [Generate report]
```

---

## Data Flow

### Typical Workflow
```
1. User runs: pmind scan
   ↓
2. Phase 1 scans directory → finds all Python files
   ↓
3. Phase 2 parses files → extracts code structure
   ↓
4. Phase 4 orchestrates agents:
   - CodeAnalyzerAgent analyzes complexity
   - SecurityAgent scans for threats
   - DocumentationAgent generates docs
   ↓
5. Results aggregated and displayed
```

### Semantic Search Flow
```
1. User indexes files: pmind index-files
   ↓
2. Phase 3 generates embeddings for each code snippet
   ↓
3. VectorStore saves embeddings locally
   ↓
4. User searches: pmind search "find functions that validate input"
   ↓
5. Query converted to embedding
   ↓
6. Semantic search finds most similar functions
```

---

## Error Handling Strategy

### Principle: Graceful Degradation
- Individual agent failure doesn't stop workflow
- Missing files are reported, not fatal
- Parse errors don't halt processing
- Each function has try/except with logging

### Example:
```python
try:
    result = agent.execute(task, params)
except Exception as e:
    # Log error
    # Return failure with details
    # Continue to next task
    return AgentResult(success=False, error=str(e))
```

---

## Performance Considerations

### Trade-offs Made

| Component | Choice | Why |
|-----------|--------|-----|
| Storage | File-based | Simple, no DB dependency |
| Parsing | Full AST | Accurate, not just regex |
| Search | Embeddings | Slow but accurate |
| Agents | Sequential | Simple, can parallelize later |
| Caching | In-memory | Fast access, reset on restart |

### Optimization Points for Future
- Parallel agent execution
- Incremental analysis (only changed files)
- Caching of embeddings
- Lazy loading of large projects

---

## Testing Strategy

### Unit Tests (Per Phase)
- Test individual components in isolation
- Mock external dependencies
- Target: 90%+ code coverage

### Integration Tests
- Test component interactions
- Example: SecurityAgent uses ThreatDetector correctly
- Verify workflows execute as expected

### End-to-End Tests
- Test entire CLI commands
- Verify output format and accuracy
- Test error conditions

---

## Extensibility Points

### Adding a New Agent
```python
from projectmind.agents import Agent

class CustomAgent(Agent):
    def __init__(self):
        config = AgentConfig(
            name="custom",
            description="Does custom analysis"
        )
        super().__init__(config)
        self.register_tool("analyze", self._analyze)
    
    def _execute_task(self, task, params):
        if task == "analyze":
            return self._analyze(params.get("code"))
```

### Adding a New Tool
```python
registry = ToolRegistry()
registry.register_tool(
    "my_check",
    "Does something specific",
    my_function,
    required_params=["code"]
)
```

### Adding a New Workflow
```python
workflow = WorkflowDefinition(
    name="my_workflow",
    steps=[
        WorkflowStep(...),
        WorkflowStep(...),
    ]
)
orchestrator.register_workflow(workflow)
```

---

## Security & Privacy Considerations

### What ProjectMind Does NOT Do
- Store code anywhere except user's machine
- Send data to external services
- Log sensitive information
- Cache credentials or secrets

### What ProjectMind Does
- Analyzes code for security issues
- Reports threats with line numbers
- Validates against policies
- Maintains execution audit trail

---

## Future Architecture Improvements

1. **Parallel Agent Execution** – Run agents concurrently
2. **Distributed Analysis** – Split large projects across cores
3. **Incremental Updates** – Only re-analyze changed files
4. **Plugin System** – Load custom agents at runtime
5. **Knowledge Graph** – Store code relationships for better analysis
