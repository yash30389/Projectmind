# ProjectMind

<p align="center">
  <img src="./projectmind-logo.png" alt="ProjectMind Logo" width="200"/>
</p>

**Local, project-aware AI engineering system with intelligent code analysis and business logic suggestions.**

ProjectMind is built differently from typical AI tools:

- ✅ **Understands Your Business Logic** - Context-aware analysis of your codebase
- ✅ **Intelligent Suggestions** - AI-powered recommendations based on code patterns
- ✅ **Multiple Perspectives** - 5 agent personas analyze from different angles
- ✅ **Not autonomous** - AI can only suggest, never edit silently
- ✅ **Not hallucinating** - Deterministic repo scanning before any AI
- ✅ **Not proprietary** - Built on open standards, runs locally
- ✅ **Explainable** - Every recommendation includes reasoning
- ✅ **Governed** - Project constraints are hard enforced

---

## 🏗 Architecture: Four Layers

```md
┌──────────────────────────────────┐
│ Layer C: CLI Interface            │
│ (Explicit, Auditable Commands)   │
└───────────────┬──────────────────┘
                ↓
┌──────────────────────────────────┐
│ Layer B: Context & Memory         │
│ (Vision, Goals, Constraints)     │
└───────────────┬──────────────────┘
                ↓
┌──────────────────────────────────┐
│ Layer A: Repository Intelligence │
│ (Deterministic Scanning)         │
└──────────────────────────────────┘
        +
┌──────────────────────────────────┐
│ Layer D: Architecture Discipline  │
│ (Docs, Decision Logs, Governance)│
└──────────────────────────────────┘
```

### Layer A: Repository Intelligence ✅ READY

- **RepoScanner**: Walks entire directory, detects languages
- **PythonParser**: Extracts functions, classes, imports (no execution)
- **FileMetadata**: Deterministic file-level data
- **Status**: Complete, tested

### Layer B: Context & Memory ✅ READY

- **ProjectContext**: Vision, goals, team info
- **ProjectConstraints**: Rules AI must follow
- **ContextLoader**: Load/save from YAML
- **Status**: Complete, tested

### Layer C: CLI Interface ✅ READY

**Phase 1 Commands**:

- `pmind scan` - Full repository scan
- `pmind analyze <file.py>` - Detailed Python file analysis
- `pmind context` - Manage project alignment
- `pmind init` - Initialize ProjectMind

**Phase 2 Commands** (NEW):

- `pmind summarize <file.py>` - Analyze and summarize Python file
- `pmind generate-docs` - Generate API documentation

**Phase 3 Commands** (NEW):

- `pmind search <query>` - Search code using semantic similarity
- `pmind index-files` - Index Python files for semantic search
- `pmind search-stats` - Display search index statistics

**Phase 5 Commands** (NEW):

- `pmind validate <action>` - Check policy compliance
- `pmind scan-threats <file>` - Detect security threats
- `pmind audit-log-action` - Log actions for compliance
- `pmind compliance-report` - Generate compliance evidence

**Status**: Complete, tested (86 tests passing)

### Layer D: Architecture Discipline & Advanced Features ✅ READY

- **Knowledge System** (Phase A): 11 comprehensive documentation files (4,100+ lines)
- **Context-Aware Agents** (Phase B): 4 intelligent agents with business context
- **Agent Personas** (Phase D): 5 personality models (Architect, Guardian, Craftsman, Mentor, Generalist)
- **Suggestion Engine** (Phase D): Context-aware code suggestions with 3 analysis types
- **Workflow Orchestration** (Phase D): Context-aware multi-step workflow execution
- **Status**: Complete, tested (158 tests passing)

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download ProjectMind
cd projectmind

# Install in development mode
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Initialize

```bash
# Create project context
pmind init

# This creates:
# - project_context.yaml (your project's vision & constraints)
# - .pmind/decisions/ (for decision logs)
```

### Scan Your Repo

```bash
# Quick scan
pmind scan

# JSON output
pmind scan --output json

# Verbose
pmind scan --verbose
```

### Analyze Python Files

```bash
# Analyze single file
pmind analyze src/core.py

# JSON output
pmind analyze src/core.py --output json
```

### Review Project Context

```bash
# View current context
pmind context

# Initialize from scratch
pmind context --init
```

---

## 📋 Feature Set

### ✅ Complete (Phases A, B, C, D)

| Feature | Status | Details |
| --- | --- | --- |
| Full repo scan | ✅ | Language detection, file metadata |
| Python parsing | ✅ | Functions, classes, imports (no execution) |
| Project context | ✅ | Vision, goals, constraints management |
| CLI interface | ✅ | 14+ commands for full capability |
| Knowledge system | ✅ | 11 docs, 4,100+ lines of business context |
| Context-aware agents | ✅ | 4 agents with topic-based context loading |
| Code analysis | ✅ | Complexity, functions, patterns, issues |
| Code summarization | ✅ | Document existing code automatically |
| Documentation generation | ✅ | Generate API docs from code |
| Embeddings & search | ✅ | Semantic code search with vectors |
| Policy engine | ✅ | Policy-based code validation |
| Security analysis | ✅ | Threat detection & compliance checks |
| Audit logging | ✅ | Action tracking for compliance |
| **Agent Personas** | ✅ | 5 perspectives: Architect, Guardian, Craftsman, Mentor, Generalist |
| **Suggestion Engine** | ✅ | 3 analysis types (general, security, performance) |
| **Workflow Context** | ✅ | Context-aware multi-step workflows |
| **Business Logic Analysis** | ✅ | Understand and improve business logic |
| Unit tests | ✅ | 158 tests, 100% pass rate |

### Test Coverage

```md
Phase A-B Integration Tests:      56 tests
Phase C Validation Tests:          25 tests
Phase D Enhancement Tests:         27 tests
Core System Tests:                 71 tests
────────────────────────────────── ───────
TOTAL:                           158 tests ✅
```

---

## 🧠 Business Logic Analysis

ProjectMind understands your code's **business logic** and provides **intelligent suggestions** for improvement.

### What It Can Do

✅ **Analyze existing code** - Understand complexity, structure, and patterns
✅ **Detect security issues** - Find vulnerabilities specific to your domain
✅ **Suggest improvements** - Context-aware recommendations for business logic
✅ **Multi-perspective analysis** - View code from 5 different expert angles:

**5 Agent Personas:**

1. **Architect** 🏗️ - Focuses on design and structure
2. **Guardian** 👮 - Prioritizes security and compliance
3. **Craftsman** 🔨 - Emphasizes code quality and patterns
4. **Mentor** 🎓 - Provides educational best practices
5. **Generalist** 🔄 - Balanced view across all concerns

### Example

```python
from projectmind.agents import ContextAwareSuggestionEngine, CodeAnalyzerAgent

analyzer = CodeAnalyzerAgent()
engine = ContextAwareSuggestionEngine(analyzer)

# Analyze your business logic
code = """
def calculate_order_total(items, user_tier, coupon_code=None):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    if user_tier == 'gold':
        total *= 0.9
    if coupon_code == 'SAVE10':
        total *= 0.9
    return total
"""

# Get context-aware suggestions
suggestions = engine.generate_suggestions(
    code=code,
    analysis_type="general",
    context_topics=["checkout", "pricing", "customer-retention"]
)

# Results include:
# - Long function detection
# - Duplicate discount logic
# - Missing tax/shipping calculation
# - Suggestion to extract discount logic
# - Recommendation to centralize pricing rules
```

---

## 🔧 Use Cases

### 1. **Code Improvement Suggestions**

- Understand legacy code in your project
- Get improvement suggestions based on business needs
- Refactor with confidence using AI insights

### 2. **Security & Compliance**

- Detect security vulnerabilities in your code
- Validate against compliance policies (GDPR, SOC2, etc.)
- Generate audit logs automatically

### 3. **Code Review Automation**

- Get pre-review analysis before human review
- Multi-perspective feedback (Architect, Guardian, Craftsman)
- Suggest best practices tailored to your codebase

### 4. **Business Logic Optimization**

- Improve checkout, payment, authorization logic
- Detect business logic vulnerabilities
- Optimize performance-critical code paths

### 5. **Documentation from Code**

- Auto-generate API documentation
- Create docstrings from code analysis
- Build knowledge base from codebase

### 6. **Developer Training**

- Mentor perspective provides learning-focused suggestions
- Understand why code patterns matter
- Learn best practices in context

---

## 🔐 Compliance & Security

### Core Principles

1. **Least Authority** - Each component does ONE thing
2. **No Autonomous Harm** - AI never edits without approval
3. **Explainability** - All reasoning is shown to user
4. **Context Integrity** - Only reason about known data

### Constraints (Hard-Enforced)

Your project context includes:

```yaml
constraints:
  no_autonomous_changes: true
  must_explain_reasoning: true
  respect_architecture: true
  custom_constraints:
    - AI cannot edit files directly
    - All suggestions must include reasoning
```

These are **NOT negotiable** by the AI.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=projectmind

# Verbose
pytest -v
```

---

## 📚 Documentation

### Phase Completion Reports

- [PHASE_D_COMPLETION_REPORT.md](PHASE_D_COMPLETION_REPORT.md) - Phase D: Agent Personas, Suggestion Engine, Workflow Context
- [PHASE_3_COMPLETION_REPORT.md](PHASE_3_COMPLETION_REPORT.md) - Phase C: Testing & Validation
- [PHASE_C_COMPLETION_REPORT.md](PHASE_C_COMPLETION_REPORT.md) - Earlier phase documentation

### Technical Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and architecture
- [docs/ARCHITECTURE_AND_DECISIONS.md](docs/ARCHITECTURE_AND_DECISIONS.md) - Design decisions
- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) - Setup and quick start guide
- [KNOWLEDGE_SYSTEM_COMPLETE.md](KNOWLEDGE_SYSTEM_COMPLETE.md) - Complete knowledge system reference
- [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) - Full project status and features

---

## 💡 How This Differs From Other AI Tools

| Feature | ProjectMind | ChatGPT-like | Copilot |
| --- | --- | --- | --- |
| Understands full codebase | ✅ | ❌ | ❌ |
| Can edit files silently | ❌ | ❌ | ✅ (risky) |
| Deterministic first | ✅ | ❌ | ❌ |
| Respects constraints | ✅ | ❌ | ❌ |
| Explainable by design | ✅ | ⚠️ | ⚠️ |
| Runs locally | ✅ | ❌ | ❌ |
| Open source | ✅ | ❌ | ❌ |

---

## 🤝 Contributing

ProjectMind is designed for:

- Solo developers & small teams
- Enterprises building AI governance
- Researchers in explainable AI
- Anyone who wants AI without the risk

---

## 📄 License

MIT License - See LICENSE file

---

## 🎯 Next Steps

1. **Review** [project_context.yaml](project_context.yaml)
2. **Run** `pmind scan` on your codebase
3. **Analyze** `pmind analyze <file.py>`
4. **Plan** Phase 2 features

---

**ProjectMind: Mature AI for serious teams.**
