# ProjectMind - Knowledge System Implementation Guide

## Objective: Make ProjectMind Understand Like an Experienced Developer

### Current State
✅ **Code Intelligence**: ProjectMind can analyze code quality, complexity, security
❌ **Business Logic Understanding**: ProjectMind cannot explain WHY code exists
❌ **Context Awareness**: ProjectMind doesn't know project goals or constraints

### Desired State
✅ **Code Intelligence**: Maintain existing capabilities
✅ **Business Logic Understanding**: Explain intent and design decisions
✅ **Context Awareness**: Consider project goals when making recommendations

---

## Three-Tier Knowledge System

### Tier 1: Business & Product Context ✅ COMPLETE
**File**: BUSINESS_CONTEXT.md

**What it covers:**
- Product vision and goals
- Target users and use cases
- Key value propositions
- Core principles and constraints
- Success metrics

**Used by agents to:**
- Understand why the project exists
- Make recommendations aligned with values
- Understand user context

**Example connection:**
```
User: "Why did you reject this code?"
Agent: "This creates a cloud dependency, but your 
        BUSINESS_CONTEXT says you're 'local-only architecture' 
        to ensure privacy"
```

---

### Tier 2: Architecture & Design Decisions ✅ COMPLETE
**File**: ARCHITECTURE_AND_DECISIONS.md

**What it covers:**
- System architecture and component relationships
- Design decisions and their rationale
- Trade-offs made in each decision
- Data flow through the system
- Why patterns were chosen
- Performance considerations
- Future improvement points

**Used by agents to:**
- Understand how components fit together
- Explain architectural choices
- Identify when patterns are violated
- Suggest improvements aligned with design

**Example connection:**
```
User: "Should we add this feature?"
Agent: "Looking at ARCHITECTURE_AND_DECISIONS.md, 
        separation of concerns is a core principle. 
        This feature violates that principle, so we 
        should refactor first"
```

---

### Tier 3: Codebase Intelligence ✅ COMPLETE
**Files**: Phase 1-5 implementation

**What it covers:**
- Actual code structure and organization
- Function relationships and dependencies
- Code quality metrics
- Security issues and vulnerabilities
- Documentation status
- Performance bottlenecks

**Used by agents to:**
- Analyze actual code
- Propose changes
- Validate against standards
- Generate documentation

**Example connection:**
```
User: "How do we implement this requirement?"
Agent: "Phase 2 DocumentationGenerator can extract 
        docstrings, Phase 3 can find similar patterns, 
        Phase 4 can orchestrate the implementation"
```

---

## Implementing Tier 2 Knowledge Access

### Step 1: Add Context Loading to Agent Base Class

```python
# In projectmind/agents/base_agent.py

from pathlib import Path
import yaml

class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self._load_knowledge_context()
    
    def _load_knowledge_context(self) -> None:
        """Load business context, architecture, and standards."""
        self.business_context = self._load_markdown("docs/BUSINESS_CONTEXT.md")
        self.architecture = self._load_markdown("docs/ARCHITECTURE_AND_DECISIONS.md")
        self.standards = self._load_markdown("docs/TEAM_STANDARDS.md")
        self.project_context = self._load_yaml("project_context.yaml")
    
    def _load_markdown(self, path: str) -> str:
        """Load markdown file contents."""
        try:
            doc_path = Path(__file__).parent.parent.parent / path
            if doc_path.exists():
                return doc_path.read_text()
        except Exception as e:
            logger.warning(f"Could not load {path}: {e}")
        return ""
    
    def _load_yaml(self, path: str) -> dict:
        """Load YAML configuration."""
        try:
            config_path = Path(__file__).parent.parent.parent / path
            if config_path.exists():
                with open(config_path) as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load {path}: {e}")
        return {}
    
    def get_context_snippet(self, topic: str) -> str:
        """
        Retrieve relevant context by topic.
        
        Examples:
        - "architecture" -> Returns architecture overview
        - "decisions" -> Returns design decisions
        - "naming" -> Returns naming conventions
        """
        context_sources = {
            "architecture": self.architecture,
            "decisions": self.architecture,
            "design": self.architecture,
            "business": self.business_context,
            "goals": self.business_context,
            "naming": self.standards,
            "testing": self.standards,
            "error_handling": self.standards,
            "logging": self.standards,
        }
        return context_sources.get(topic, "")
```

### Step 2: Add Context-Aware Tool Methods

```python
# Example in projectmind/agents/code_analyzer_agent.py

def _get_style_recommendations(self, code: str) -> list[str]:
    """
    Get style recommendations based on team standards.
    Uses loaded context to identify violations.
    """
    context = self.get_context_snippet("naming")
    
    recommendations = []
    
    # Check naming conventions
    if "PascalCase" in context:
        # Look for camelCase classes
        if re.search(r'class [a-z][a-zA-Z]*:', code):
            recommendations.append(
                "Class names should use PascalCase "
                "(see TEAM_STANDARDS.md)"
            )
    
    return recommendations

def _explain_decision(self, code_pattern: str) -> str:
    """
    Explain WHY code is written a certain way.
    References architectural decisions.
    """
    architecture = self.get_context_snippet("architecture")
    
    if "agent" in code_pattern.lower():
        if "multi-agent" in architecture:
            return (
                "This pattern aligns with our multi-agent architecture "
                "decision (see ARCHITECTURE_AND_DECISIONS.md)"
            )
    
    return "Pattern matches project architecture"
```

### Step 3: Update Workflow to Include Context

```python
# In projectmind/agents/workflow_orchestrator.py

class WorkflowStep:
    def __init__(self, ...):
        ...
        self.context_aware = True  # Use knowledge system
        self.explain_reasoning = True  # Explain WHY

class WorkflowOrchestrator:
    def _execute_step(self, step: WorkflowStep, ...):
        """Execute step with context awareness."""
        
        # Get agent
        agent = self._get_agent(step.agent_type)
        
        # Add context to parameters if needed
        if step.context_aware:
            params["business_context"] = agent.business_context
            params["architecture"] = agent.architecture
            params["standards"] = agent.standards
        
        # Execute
        result = agent.execute(step.task, params)
        
        # Enhance with reasoning if requested
        if step.explain_reasoning:
            result.reasoning = agent.get_context_snippet("decisions")
        
        return result
```

---

## Immediate Integration Points

### 1. Enhanced Code Analysis
```
User asks: "Analyze this code"
↓
Agent loads standards and architecture
↓
Agent checks against team standards
↓
Agent explains recommendations in context
↓
Output includes:
  - Code quality metrics
  - Alignment with architecture
  - Compliance with standards
  - Why each recommendation matters
```

### 2. Smart Refactoring Suggestions
```
User asks: "How should I refactor this?"
↓
Agent checks against architecture decisions
↓
Agent verifies alignment with separation of concerns
↓
Agent suggests refactoring that maintains design
↓
Output includes rationale from ARCHITECTURE_AND_DECISIONS.md
```

### 3. Requirement Understanding
```
User states: "Add feature X"
↓
Agent checks business context for constraints
↓
Agent checks architecture for integration points
↓
Agent checks standards for implementation pattern
↓
Output provides:
  - Whether feature aligns with values
  - How to integrate with existing system
  - What standards to follow
```

---

## Extending the Knowledge System

### Adding Tier 2.5: Common Patterns
**File**: docs/PATTERNS_AND_RECIPES.md (Future)

**Content:**
- How to add a new agent
- How to add a new phase
- Common refactoring patterns
- Integration patterns

### Adding Tier 2.6: Failure Analysis
**File**: docs/FAILURE_MODES.md (Future)

**Content:**
- Known failure modes
- How to debug common issues
- Performance bottlenecks
- Recovery strategies

---

## Testing the Knowledge System

### Unit Test
```python
def test_agent_loads_business_context():
    agent = CodeAnalyzerAgent()
    assert agent.business_context
    assert "privacy" in agent.business_context.lower()

def test_agent_provides_context_snippet():
    agent = SecurityAgent()
    snippet = agent.get_context_snippet("decisions")
    assert "local-only" in snippet.lower()
```

### Integration Test
```python
def test_agent_explains_recommendations_with_context():
    agent = CodeAnalyzerAgent()
    code = "class myClass: pass"  # Wrong case
    
    # Get style recommendations
    recommendations = agent._get_style_recommendations(code)
    
    # Should reference team standards
    assert any("PascalCase" in rec for rec in recommendations)
    assert any("TEAM_STANDARDS" in rec for rec in recommendations)
```

---

## Validation Checklist

Before deploying knowledge system:

- [ ] All Tier 1 context documents exist and are accurate
- [ ] All Tier 2 context documents exist and are complete
- [ ] Agent base class loads all context files
- [ ] Context loading handles missing files gracefully
- [ ] Agents use context in tool implementations
- [ ] Workflows can access context through agents
- [ ] Test suite validates context-aware behavior
- [ ] Documentation updated with new capabilities
- [ ] CLI outputs can explain reasoning from context
- [ ] No hardcoded assumptions in agent logic

---

## Measuring Success

### Quantitative Metrics
- Code recommendations include context references: >80%
- Refactoring suggestions mention architectural alignment: >70%
- User-facing output includes reasoning: 100%

### Qualitative Feedback
- Users report system "understands the project"
- New developers can learn from system's explanations
- Recommendations feel personalized, not generic
- System catches violations of team standards

---

## Example: Full Workflow with Knowledge System

```
User: "Should we extract this function into a module?"

Agent execution (with knowledge system):
├─ Load BUSINESS_CONTEXT
│  └─ Check if change aligns with "code clarity" principle
├─ Load ARCHITECTURE_AND_DECISIONS
│  └─ Check if change respects "separation of concerns"
├─ Load TEAM_STANDARDS
│  └─ Check naming and organization conventions
├─ Analyze code structure
├─ Simulate extraction
├─ Validate against all contexts
└─ Return result:
   {
     "recommendation": "YES, extract recommended",
     "reasoning": [
       "Aligns with 'separation of concerns' principle",
       "Improves code clarity per BUSINESS_CONTEXT",
       "Module name should follow Team Standards",
       "See ARCHITECTURE_AND_DECISIONS for similar patterns"
     ],
     "implementation": "..."
   }
```

---

## Next Steps

1. **Implement Step 1**: Add context loading to Agent base class
2. **Implement Step 2**: Update 3 agents to use context
3. **Implement Step 3**: Update workflows to be context-aware
4. **Test**: Run test_phase4_integration with context
5. **Validate**: Verify recommendations now include reasoning
6. **Document**: Update README with new capabilities
7. **Expand**: Add Tier 2.5 and 2.6 documents as needed

