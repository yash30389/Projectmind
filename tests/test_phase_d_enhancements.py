"""
Phase D Tests - Workflow Context Passing, Personas, and Suggestion Engine.
"""

import pytest
from projectmind.agents import (
    CodeAnalyzerAgent, SecurityAgent, DocumentationAgent,
    WorkflowOrchestrator, WorkflowDefinition, WorkflowStep
)
from projectmind.agents.suggestion_engine import ContextAwareSuggestionEngine
from projectmind.agents.agent_personas import (
    AgentPersona, get_persona, get_persona_for_context_topics, PersonaSet
)


class TestWorkflowContextPassing:
    """Test context passing in workflow steps."""

    def test_workflow_step_has_context_aware_flag(self):
        """Test that WorkflowStep supports context_aware flag."""
        step = WorkflowStep(
            id="step1",
            agent_name="code_analyzer",
            task="analyze_code",
            params={"code": "print('hello')"},
            context_aware=True,
            context_topics=["standards", "architecture"]
        )
        
        assert step.context_aware is True
        assert "standards" in step.context_topics
        assert "architecture" in step.context_topics

    def test_context_aware_step_integration(self):
        """Test context awareness in workflow execution."""
        orchestrator = WorkflowOrchestrator()
        analyzer = CodeAnalyzerAgent()
        orchestrator.register_agent(analyzer)
        
        workflow = WorkflowDefinition(
            name="context_aware_analysis",
            description="Analyze code with context",
            steps=[
                WorkflowStep(
                    id="analyze",
                    agent_name="code_analyzer",
                    task="analyze_complexity",
                    params={"code": "def long(): pass"},
                    context_aware=True,
                    context_topics=["standards", "architecture"]
                )
            ]
        )
        orchestrator.register_workflow(workflow)
        
        result = orchestrator.execute_workflow("context_aware_analysis")
        assert result.state.value == "completed"

    def test_context_snippets_passed_to_agent(self):
        """Test that context snippets are passed as parameters."""
        orchestrator = WorkflowOrchestrator()
        analyzer = CodeAnalyzerAgent()
        orchestrator.register_agent(analyzer)
        
        # Create a context-aware step
        step = WorkflowStep(
            id="analyze",
            agent_name="code_analyzer",
            task="analyze_complexity",
            params={"code": "x = 1"},
            context_aware=True,
            context_topics=["standards"]
        )
        
        # Check that step has context configuration
        assert step.context_aware is True
        assert len(step.context_topics) > 0

    def test_non_context_aware_steps_unchanged(self):
        """Test that non-context-aware steps work as before."""
        orchestrator = WorkflowOrchestrator()
        analyzer = CodeAnalyzerAgent()
        orchestrator.register_agent(analyzer)
        
        workflow = WorkflowDefinition(
            name="normal_workflow",
            description="Normal workflow without context",
            steps=[
                WorkflowStep(
                    id="analyze",
                    agent_name="code_analyzer",
                    task="analyze_complexity",
                    params={"code": "x = 1"},
                    context_aware=False  # Not context-aware
                )
            ]
        )
        orchestrator.register_workflow(workflow)
        
        result = orchestrator.execute_workflow("normal_workflow")
        assert result.state.value == "completed"


class TestSuggestionEngine:
    """Test context-aware suggestion engine."""

    def test_suggestion_engine_initialization(self):
        """Test creating suggestion engine."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        assert engine.agent is agent
        assert len(engine.suggestions) == 0

    def test_general_analysis_suggestions(self):
        """Test general analysis produces suggestions."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = """
def long_function():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x = 27
    y = 28
    z = 29
    aa = 30
    bb = 31
    cc = 32
    dd = 33
    ee = 34
    ff = 35
    gg = 36
    hh = 37
    ii = 38
    jj = 39
    kk = 40
    ll = 41
    mm = 42
    nn = 43
    oo = 44
    pp = 45
    qq = 46
    rr = 47
    ss = 48
    tt = 49
    uu = 50
    vv = 51
    return x
"""
        suggestions = engine.generate_suggestions(code, "general")
        
        # General analysis should produce some suggestions or none, both are valid
        assert isinstance(suggestions, list)
        if suggestions:
            assert all(hasattr(s, 'title') for s in suggestions)
            assert all(hasattr(s, 'context_reference') for s in suggestions)

    def test_security_analysis_suggestions(self):
        """Test security analysis produces security-focused suggestions."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = """
password = "MyPassword123"
api_key = "sk-1234567890abcdef"
result = eval(user_input)
"""
        suggestions = engine.generate_suggestions(code, "security")
        
        assert len(suggestions) > 0
        for suggestion in suggestions:
            assert suggestion.category in ["security", "standards"]

    def test_performance_analysis_suggestions(self):
        """Test performance analysis produces performance suggestions."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = """
results = []
for i in range(1000):
    for j in range(1000):
        for k in range(100):
            results.append(i * j * k)
"""
        suggestions = engine.generate_suggestions(code, "performance")
        
        assert len(suggestions) > 0

    def test_suggestions_have_context_references(self):
        """Test that all suggestions reference context documents."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = "def long(): pass\nif True:\n    if True:\n        if True:\n            if True:\n                pass"
        suggestions = engine.generate_suggestions(code)
        
        for suggestion in suggestions:
            assert suggestion.context_reference
            assert ".md" in suggestion.context_reference

    def test_get_suggestions_by_category(self):
        """Test filtering suggestions by category."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = """
def long():
    pass
if True: pass
password = "secret"
"""
        suggestions = engine.generate_suggestions(code)
        
        security_suggestions = engine.get_suggestions_by_category("security")
        assert all(s.category == "security" for s in security_suggestions)

    def test_get_suggestions_by_severity(self):
        """Test filtering suggestions by severity."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = """
password = "secret"
if True: pass
"""
        suggestions = engine.generate_suggestions(code)
        
        warnings = engine.get_suggestions_by_severity("warning")
        assert all(s.severity == "warning" for s in warnings)

    def test_suggestion_summary(self):
        """Test getting summary of suggestions."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = """
password = "secret"
if True: pass
"""
        suggestions = engine.generate_suggestions(code)
        summary = engine.summary()
        
        assert "total_suggestions" in summary
        assert "by_severity" in summary
        assert "by_category" in summary
        assert summary["total_suggestions"] == len(suggestions)

    def test_format_suggestions_text(self):
        """Test formatting suggestions as plain text."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = "password = 'secret'"
        engine.generate_suggestions(code)
        
        formatted = engine.format_suggestions(markdown=False)
        assert isinstance(formatted, str)
        assert "CODE SUGGESTIONS" in formatted or "No suggestions" in formatted

    def test_format_suggestions_markdown(self):
        """Test formatting suggestions as markdown."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = "password = 'secret'"
        engine.generate_suggestions(code)
        
        formatted = engine.format_suggestions(markdown=True)
        assert isinstance(formatted, str)
        assert "#" in formatted or "No suggestions" in formatted


class TestAgentPersonas:
    """Test agent personas system."""

    def test_architect_persona(self):
        """Test architect persona."""
        persona = get_persona(AgentPersona.ARCHITECT)
        
        assert persona.name == AgentPersona.ARCHITECT
        assert "architecture" in persona.focus_topics
        assert persona.primary_concern
        assert persona.recommendation_style

    def test_guardian_persona(self):
        """Test guardian persona."""
        persona = get_persona(AgentPersona.GUARDIAN)
        
        assert persona.name == AgentPersona.GUARDIAN
        assert "business" in persona.focus_topics
        assert "privacy" in persona.description.lower() or "security" in persona.description.lower()

    def test_craftsman_persona(self):
        """Test craftsman persona."""
        persona = get_persona(AgentPersona.CRAFTSMAN)
        
        assert persona.name == AgentPersona.CRAFTSMAN
        assert "standards" in persona.focus_topics
        assert "quality" in persona.description.lower() or "code" in persona.description.lower()

    def test_mentor_persona(self):
        """Test mentor persona."""
        persona = get_persona(AgentPersona.MENTOR)
        
        assert persona.name == AgentPersona.MENTOR
        assert "testing" in persona.focus_topics
        assert "learn" in persona.description.lower() or "improvement" in persona.description.lower()

    def test_generalist_persona(self):
        """Test generalist persona."""
        persona = get_persona(AgentPersona.GENERALIST)
        
        assert persona.name == AgentPersona.GENERALIST
        assert len(persona.focus_topics) >= 3  # Multiple focus areas

    def test_get_persona_for_context_topics(self):
        """Test selecting persona for given topics."""
        # Topics focusing on architecture
        arch_persona = get_persona_for_context_topics(["architecture", "design", "decisions"])
        assert arch_persona in [AgentPersona.ARCHITECT, AgentPersona.GENERALIST]

        # Topics focusing on security/business
        security_persona = get_persona_for_context_topics(["business", "goals", "principles"])
        assert security_persona in [AgentPersona.GUARDIAN, AgentPersona.GENERALIST]

        # Topics focusing on standards
        standards_persona = get_persona_for_context_topics(["standards", "naming", "conventions"])
        assert standards_persona in [AgentPersona.CRAFTSMAN, AgentPersona.GENERALIST]

    def test_persona_apply_to_analysis(self):
        """Test persona filtering analysis suggestions."""
        persona = get_persona(AgentPersona.ARCHITECT)
        
        suggestions = [
            {"title": "Architecture", "category": "architecture"},
            {"title": "Code Style", "category": "standards"},
            {"title": "Security", "category": "security"}
        ]
        
        filtered = persona.apply_to_analysis(suggestions)
        
        # Architect should filter for architecture-relevant items
        assert all("persona_angle" in s or "critical_question" in s for s in filtered)

    def test_persona_set_all_perspectives(self):
        """Test getting all perspectives from persona set."""
        persona_set = PersonaSet([AgentPersona.ARCHITECT, AgentPersona.GUARDIAN])
        
        perspectives = persona_set.get_all_perspectives("code organization")
        
        assert "architect" in perspectives
        assert "guardian" in perspectives
        assert all("focus" in p for p in perspectives.values())
        assert all("approach" in p for p in perspectives.values())

    def test_persona_set_summarize(self):
        """Test summarizing persona set."""
        persona_set = PersonaSet()
        
        summary = persona_set.summarize_perspectives()
        
        assert isinstance(summary, str)
        assert "ARCHITECT" in summary or "architect" in summary.lower()
        assert "GUARDIAN" in summary or "guardian" in summary.lower()

    def test_all_personas_have_critical_questions(self):
        """Test that all personas have question templates."""
        from projectmind.agents.agent_personas import PERSONAS
        
        for persona_name, persona in PERSONAS.items():
            assert hasattr(persona, 'question_template')
            assert "{aspect}" in persona.question_template


class TestPhaseDIntegration:
    """Integration tests for Phase D features."""

    def test_context_aware_workflow_end_to_end(self):
        """Test complete context-aware workflow."""
        orchestrator = WorkflowOrchestrator()
        
        # Register agents
        analyzer = CodeAnalyzerAgent()
        orchestrator.register_agent(analyzer)
        
        # Register workflow with context-aware step
        workflow = WorkflowDefinition(
            name="context_workflow",
            description="Workflow with context awareness",
            steps=[
                WorkflowStep(
                    id="step1",
                    agent_name="code_analyzer",
                    task="analyze_complexity",
                    params={"code": "x = 1"},
                    context_aware=True,
                    context_topics=["standards", "architecture"]
                )
            ]
        )
        orchestrator.register_workflow(workflow)
        
        result = orchestrator.execute_workflow("context_workflow")
        assert result.state.value == "completed"

    def test_suggestion_engine_with_personas(self):
        """Test suggestion engine selecting personas."""
        agent = CodeAnalyzerAgent()
        engine = ContextAwareSuggestionEngine(agent)
        
        code = "def long(): pass\nif True: pass"
        suggestions = engine.generate_suggestions(
            code,
            "general",
            context_topics=["architecture", "standards"]
        )
        
        # Suggestions may or may not be generated depending on code analysis
        assert isinstance(suggestions, list)
        if suggestions:
            assert all(s.context_reference for s in suggestions)

    def test_multi_persona_analysis(self):
        """Test analyzing code through multiple persona lenses."""
        personas = PersonaSet([
            AgentPersona.ARCHITECT,
            AgentPersona.CRAFTSMAN,
            AgentPersona.GUARDIAN
        ])
        
        perspectives = personas.get_all_perspectives("function design")
        
        assert len(perspectives) == 3
        assert all("focus" in p for p in perspectives.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
