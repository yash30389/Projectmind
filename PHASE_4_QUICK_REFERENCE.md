# Phase 4: Quick Reference Guide

## What is Phase 4?

Phase 4 adds **Multi-Agent Orchestration** to ProjectMind - a system for coordinating specialized AI agents to analyze code, detect security threats, and generate documentation.

## Quick Start

### 1. Analyze Code Complexity

```bash
cat mycode.py | pmind agent-analyze
```

### 2. Check Security

```bash
cat mycode.py | pmind agent-security
```

### 3. Generate Docs

```bash
cat mycode.py | pmind agent-docs
```

### 4. List Workflows

```bash
pmind workflow-list
```

## Architecture Overview

```md
┌─────────────────────────────────────┐
│   WorkflowOrchestrator               │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │  CodeAnalyzerAgent (Phase 4) │  │
│  │  - Complexity analysis       │  │
│  │  - Function extraction       │  │
│  │  - Issue detection           │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  SecurityAgent (Phase 4)     │  │
│  │  - Threat detection          │  │
│  │  - Compliance checking       │  │
│  │  - Security reports          │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  DocumentationAgent (Phase 4)│  │
│  │  - Doc generation            │  │
│  │  - API reference             │  │
│  │  - Summaries                 │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
         ↓         ↓         ↓
   Uses Phase 1,2,3,5 components
```

## Core Components

### 1. Agent Framework

- Base class for all agents
- State management (IDLE, RUNNING, COMPLETED, FAILED)
- Memory tracking
- Tool registration

### 2. Tool Registry

- Register tools dynamically
- Execution statistics
- Tool discovery

### 3. Specialized Agents

- **CodeAnalyzerAgent**: Code metrics and issues
- **SecurityAgent**: Threats and compliance
- **DocumentationAgent**: API docs and summaries

### 4. Workflow Orchestrator

- Run multi-step workflows
- Handle dependencies
- Track execution history

## Python API Examples

### Single Agent Usage

```python
from projectmind.agents import CodeAnalyzerAgent

agent = CodeAnalyzerAgent()
result = agent.execute("analyze_complexity", {"code": "x = 1"})
print(result.output)
# {'lines': 1, 'functions': 0, 'classes': 0, ...}
```

### Workflow Usage

```python
from projectmind.agents import (
    WorkflowOrchestrator, WorkflowDefinition, WorkflowStep,
    CodeAnalyzerAgent, SecurityAgent
)

orchestrator = WorkflowOrchestrator()
orchestrator.register_agent(CodeAnalyzerAgent())
orchestrator.register_agent(SecurityAgent())

workflow = WorkflowDefinition(
    name="analyze_and_secure",
    description="Run analysis and security checks",
    steps=[
        WorkflowStep(
            id="analyze",
            agent_name="code_analyzer",
            task="analyze_complexity",
            params={"code": "x = 1"}
        ),
        WorkflowStep(
            id="security",
            agent_name="security",
            task="scan_threats",
            params={"code": "x = 1"},
            depends_on=["analyze"]
        )
    ]
)

orchestrator.register_workflow(workflow)
result = orchestrator.execute_workflow("analyze_and_secure", verbose=True)
```

## CLI Commands

### agent-analyze

Analyze code for complexity and issues

```bash
pmind agent-analyze < code.py
pmind agent-analyze --verbose < code.py
```

### agent-security

Scan code for security threats

```bash
pmind agent-security < code.py
pmind agent-security --verbose < code.py
```

### agent-docs

Generate documentation

```bash
pmind agent-docs < code.py
pmind agent-docs --verbose < code.py
```

### workflow-list

List available workflows

```bash
pmind workflow-list
pmind workflow-list --verbose
```

## Test Results

✅ All 20 Phase 4 tests passing
✅ All 106 total tests passing (all 5 phases)

Run tests:

```bash
pytest tests/test_phase4_simple.py -v
```

## File Structure

```md
projectmind/agents/
├── __init__.py                    # Module exports
├── base_agent.py                  # Agent framework (350 lines)
├── tool_registry.py               # Tool system (300 lines)
├── code_analyzer_agent.py         # Code analysis (250 lines)
├── security_agent.py              # Security (200 lines)
├── documentation_agent.py         # Documentation (300 lines)
└── workflow_orchestrator.py       # Orchestration (400 lines)

projectmind/cli/main.py           # CLI integration (150 lines)

tests/
└── test_phase4_simple.py          # 20 tests
```

## Key Features

✅ Multi-agent coordination
✅ Workflow management with dependencies
✅ State machine for agent lifecycle
✅ Tool registry and discovery
✅ Memory tracking per agent
✅ CLI integration
✅ Verbose execution logging
✅ Execution history tracking

## Next Steps

1. Try the CLI commands:

   ```bash
   pmind agent-analyze < mycode.py
   pmind agent-security < mycode.py
   pmind agent-docs < mycode.py
   ```

2. Use the Python API for workflows:

   ```python
   from projectmind.agents import WorkflowOrchestrator
   # ... (see examples above)
   ```

3. Integrate with your workflow:
   - Call agents programmatically
   - Chain multiple analysis steps
   - Collect comprehensive reports

## Documentation

- See [PHASE_4_COMPLETE.md](docs/PHASE_4_COMPLETE.md) for detailed docs
- See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for architecture
- See [GETTING_STARTED.md](docs/GETTING_STARTED.md) for setup

## Project Status

✅ Phase 1: Repository Intelligence (23 tests)
✅ Phase 2: Code Analysis (22 tests)
✅ Phase 3: Embeddings & Search (20 tests)
✅ Phase 4: Multi-Agent Orchestration (20 tests)
✅ Phase 5: Security & Compliance (21 tests)

### **Total: 106/106 tests passing ✅**

### **System Status: PRODUCTION READY**
