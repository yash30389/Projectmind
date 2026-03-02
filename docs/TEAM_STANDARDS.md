# ProjectMind - Team Standards & Code Organization

## Code Style & Conventions

### Naming Conventions

#### Classes
- PascalCase: `CodeAnalyzerAgent`, `WorkflowOrchestrator`
- Descriptive: Use full words, not abbreviations
- Suffix patterns:
  - Agents: `*Agent` (e.g., `SecurityAgent`)
  - Handlers: `*Handler` (e.g., `ErrorHandler`)
  - Utilities: `*Util` (e.g., `FileUtil`)
  - Enums: `*State`, `*Status` (e.g., `AgentState`)

#### Functions & Methods
- snake_case: `execute_workflow()`, `analyze_file()`
- Start with verb: `analyze`, `check`, `generate`, `validate`
- Private methods: `_internal_method()`
- Properties: Use @property decorator for expensive computations

#### Variables
- snake_case: `workflow_result`, `project_path`
- Be descriptive: `agent_results` not `ar`
- Constants: UPPER_SNAKE_CASE: `MAX_FILE_SIZE = 1000`

#### Module Organization
```
projectmind/
├── agents/           # Multi-agent framework
│   ├── base_agent.py       # Base Agent class
│   ├── tool_registry.py    # Tool management
│   ├── [agent_name]_agent.py
│   └── workflow_orchestrator.py
├── core/            # Fundamental analysis
├── embeddings/      # Vector search
├── security/        # Threat detection
├── compliance/      # Policy engine
├── audit/          # Logging & audit trail
├── summarization/  # Text generation
└── cli/            # Command interface
```

---

## Type Hints & Documentation

### Type Hints Requirements
- **Required for**: Public functions, class methods, agent tools
- **Optional for**: Internal helpers, simple loops
- Use modern syntax (Python 3.9+):
  ```python
  # ✓ Good
  def analyze(code: str) -> dict[str, Any]:
      pass
  
  # ✗ Avoid (old style)
  def analyze(code: str) -> Dict[str, Any]:
      pass
  ```

### Docstring Format
- Use triple quotes: `"""`
- First line: One-sentence summary
- Parameters: List each with type and description
- Returns: Describe return value and type
- Raises: Document exceptions raised

#### Example:
```python
def register_tool(
    self,
    name: str,
    tool: Callable,
    description: str = None,
) -> bool:
    """
    Register a new tool with this agent.
    
    Parameters:
    -----------
    name : str
        Unique identifier for the tool
    tool : Callable
        Function to register as a tool
    description : str, optional
        Human-readable description
        
    Returns:
    --------
    bool
        True if registration succeeded, False otherwise
        
    Raises:
    -------
    ValueError
        If name is empty or tool is not callable
    """
```

---

## Error Handling Standards

### Philosophy: Explicit Errors, Graceful Degradation

### Try/Except Pattern
```python
# ✓ Good: Specific exception, informative error
try:
    result = analyze_file(path)
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    return AgentResult(
        success=False,
        error=f"Could not analyze: {str(e)}"
    )

# ✗ Bad: Generic exception, silent failure
try:
    result = analyze_file(path)
except:
    pass
```

### Error Propagation
```python
# ✓ Good: Propagate with context
try:
    execute_workflow(workflow)
except WorkflowError as e:
    raise WorkflowError(f"Workflow failed at step {step}: {e}")

# ✗ Bad: Re-raise without context
except Exception as e:
    raise e
```

### Return Error Pattern
Some functions return errors instead of raising:
```python
class AgentResult:
    success: bool
    result: Any = None
    error: str = None
    
    @property
    def failed(self) -> bool:
        return not self.success
```

---

## Testing Standards

### Test Organization
```
tests/
├── test_[phase_name]_[component].py
├── test_phase1_scanner.py
├── test_phase2_parser.py
├── test_phase4_agents.py
└── conftest.py (pytest fixtures)
```

### Test Naming
- File: `test_[feature].py`
- Function: `test_[feature]_[scenario]`
- Example: `test_code_analyzer_agent_complexity_detection`

### Test Structure (AAA Pattern)
```python
def test_agent_executes_task():
    # Arrange
    agent = CodeAnalyzerAgent()
    code = "def foo(): pass"
    
    # Act
    result = agent.execute("analyze", {"code": code})
    
    # Assert
    assert result.success
    assert "def foo" in result.result
```

### Coverage Requirements
- Target: 85%+ coverage for critical paths
- Run: `pytest --cov=projectmind tests/`
- Known exceptions: Plot generation, external API calls

---

## Logging Standards

### Logging Levels
| Level | When to Use | Example |
|-------|------------|---------|
| DEBUG | Detailed flow information | Function entry/exit, variable values |
| INFO | Important events | File processed, workflow started |
| WARNING | Potentially harmful situations | Missing optional file, slow execution |
| ERROR | Error conditions | File not found, parse error |
| CRITICAL | Very serious errors | Complete failure, corrupted data |

### Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

def analyze_file(path: str) -> dict:
    logger.info(f"Analyzing {path}")
    
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(path)
    
    logger.debug(f"File size: {os.path.getsize(path)} bytes")
    # ... analysis ...
```

### What NOT to Log
- Passwords, API keys, tokens
- Sensitive user data
- Entire file contents (log line numbers instead)
- Stack traces unless ERROR/CRITICAL level

---

## Import Organization

### Import Order
```python
# 1. Standard library
import os
import sys
from pathlib import Path
from typing import Optional

# 2. Third-party libraries
import yaml

# 3. Local imports
from projectmind.agents import Agent
from projectmind.core import Context

# 4. Type checking only
if TYPE_CHECKING:
    from projectmind.types import WorkflowResult
```

### Rules
- Group by category (stdlib, third-party, local)
- Alphabetical within group
- Use absolute imports, not relative
- Don't do `from x import *`

---

## Class Design Patterns

### Agent Pattern
All agents inherit from `Agent` base class:

```python
from projectmind.agents import Agent, AgentConfig

class MyAgent(Agent):
    def __init__(self):
        config = AgentConfig(
            name="my_agent",
            description="Does something specific",
            version="1.0"
        )
        super().__init__(config)
        self.register_tool("my_tool", self._my_tool)
    
    def _execute_task(self, task: str, params: dict) -> Any:
        """Execute a specific task."""
        if task == "my_tool":
            return self._my_tool(params)
        
        raise ValueError(f"Unknown task: {task}")
    
    def _my_tool(self, params: dict) -> dict:
        """Implement the actual tool logic."""
        pass
```

### Result Pattern
All operations return Result objects:

```python
@dataclass
class AgentResult:
    success: bool
    result: Any = None
    error: str = None
    metadata: dict = None
    
    @property
    def failed(self) -> bool:
        return not self.success
```

### Registry Pattern
Dynamic registration of tools/components:

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register_tool(self, name: str, tool: Tool) -> None:
        """Register a new tool."""
        if name in self._tools:
            raise ValueError(f"Tool {name} already registered")
        self._tools[name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieve a registered tool."""
        return self._tools.get(name)
```

---

## Performance Guidelines

### When to Optimize
1. Processing takes >5 seconds for typical input
2. Memory usage scales poorly with project size
3. Same computation done multiple times

### How to Optimize
1. **Profile first**: Use `cProfile` to find bottlenecks
2. **Cache smartly**: Store computed results, invalidate on change
3. **Parallelize**: Use multiprocessing for independent tasks
4. **Lazy load**: Load data only when needed

### Example:
```python
class FileAnalyzer:
    def __init__(self):
        self._cache: dict[str, AnalysisResult] = {}
    
    def analyze(self, file_path: str) -> AnalysisResult:
        # Check cache first
        if file_path in self._cache:
            return self._cache[file_path]
        
        # Compute if not cached
        result = self._do_analysis(file_path)
        
        # Store and return
        self._cache[file_path] = result
        return result
```

---

## Configuration Management

### Configuration Hierarchy
1. **Defaults**: Hard-coded in code
2. **config.yaml**: Project-level overrides
3. **Environment variables**: Runtime overrides
4. **CLI arguments**: One-off changes

### Example:
```python
# Default
MAX_FILE_SIZE = 10_000_000

# Can be overridden in config.yaml:
# analysis:
#   max_file_size: 5000000

# Can be overridden by env var:
# export PROJECTMIND_MAX_FILE_SIZE=1000000

# Can be overridden by CLI:
# pmind analyze --max-file-size 500000
```

---

## Backwards Compatibility

### Rules for Version Updates
- **Patch version** (1.0.1): Bug fixes only, no API changes
- **Minor version** (1.1.0): New features, backwards compatible
- **Major version** (2.0.0): Breaking changes allowed

### When Adding Features
- Add new optional parameters before removing old ones
- Deprecate before removing (warn for 2 versions)
- Update CHANGELOG.md

### Example:
```python
def analyze(
    self,
    code: str,
    include_metrics: bool = True,  # New parameter, default True
    verbose: bool = False,  # Keep old parameter
) -> dict:
    # Check for deprecated usage
    if not include_metrics:
        warnings.warn(
            "include_metrics=False is deprecated",
            DeprecationWarning
        )
```

---

## Code Review Checklist

Before submitting code:

- [ ] Code follows naming conventions
- [ ] Type hints on public functions
- [ ] Docstrings on classes and public methods
- [ ] Tests written for new functionality
- [ ] All tests pass: `pytest tests/`
- [ ] No hardcoded paths or secrets
- [ ] Error handling with try/except
- [ ] Logging at appropriate levels
- [ ] No circular imports
- [ ] No dead code or commented-out lines
- [ ] Docstring examples work: `pytest --doctest-modules`

