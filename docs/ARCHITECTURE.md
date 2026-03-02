# ProjectMind: Project Architecture

## 🧠 System Design

ProjectMind is built as four independent, replaceable layers:

```
┌─────────────────────────────────────────┐
│ CLI Interface (Layer C)                 │
│ - Explicit, scriptable commands          │
│ - Auditable, reproducible                │
│ └→ pmind scan, pmind analyze, pmind init │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Context & Memory (Layer B)              │
│ - Project vision, goals, constraints    │
│ - Long-term alignment mechanism          │
│ └→ project_context.yaml, decision logs  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Repository Intelligence (Layer A)       │
│ - Deterministic code scanning            │
│ - Language-aware parsing                 │
│ - No guessing, no AI                    │
│ └→ RepoScanner, PythonParser            │
└─────────────────────────────────────────┘
```

## 📦 Modules

### `core/scanner.py`
- **RepoScanner**: Walks directory tree, ignores junk, detects languages
- **FileMetadata**: File-level metadata (size, lines, hash)
- Returns: Complete file inventory with hashes

### `core/python_parser.py`
- **PythonParser**: Extracts functions, classes, imports without execution
- **PythonFileAnalysis**: Structured data about Python files
- Returns: Deterministic code structure

### `core/context.py`
- **ProjectContext**: Vision, constraints, team info
- **ContextLoader**: Load/save context from YAML
- Returns: Project alignment for AI agents

### `cli/main.py`
- **pmind scan**: Full repository scan with language detection
- **pmind analyze**: Detailed Python file analysis
- **pmind context**: Manage project context
- **pmind init**: Initialize ProjectMind

## 🔄 Data Flow

```
User Command
    ↓
CLI Router (main.py)
    ↓
Scanner/Parser/ContextLoader
    ↓
Structured Output (JSON or text)
    ↓
User Reviews & Decides
```

## 🚀 Phase 2 Features (Not Yet Implemented)

- [ ] AI summarization layer
- [ ] Vector embeddings & retrieval
- [ ] Multi-agent orchestration
- [ ] Security & policy enforcement
- [ ] Test generation
- [ ] Architecture suggestions

## 🔐 Governance Rules (Hard Constraints)

1. **No autonomous file edits** - AI can only suggest
2. **Explainability required** - All AI must explain reasoning
3. **Respect architecture** - Cannot violate design decisions
4. **Deterministic first** - Non-AI layers must be bulletproof
