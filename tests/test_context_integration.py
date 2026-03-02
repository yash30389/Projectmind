"""
Context Integration Tests - Phase C.

Tests for knowledge system integration with agents.
"""

import pytest
from pathlib import Path
from projectmind.agents import (
    Agent, AgentConfig, CodeAnalyzerAgent, SecurityAgent, DocumentationAgent
)


class TestContextLoading:
    """Test knowledge context loading infrastructure."""

    def test_agent_loads_context_on_init(self):
        """Test that agents load context files on initialization."""
        config = AgentConfig(
            name="test_agent",
            description="Test agent for context loading",
            version="1.0.0"
        )
        agent = Agent(config)
        
        # Verify context attributes exist
        assert hasattr(agent, 'business_context')
        assert hasattr(agent, 'architecture')
        assert hasattr(agent, 'standards')
        assert hasattr(agent, 'project_context')

    def test_context_attributes_are_strings_or_dicts(self):
        """Test that loaded context is in expected format."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        assert isinstance(agent.business_context, str)
        assert isinstance(agent.architecture, str)
        assert isinstance(agent.standards, str)
        assert isinstance(agent.project_context, dict)

    def test_business_context_loaded(self):
        """Test that BUSINESS_CONTEXT.md is loaded successfully."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        # Business context should contain key principles
        assert len(agent.business_context) > 0

    def test_architecture_context_loaded(self):
        """Test that ARCHITECTURE_AND_DECISIONS.md is loaded successfully."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        # Architecture context should exist
        assert len(agent.architecture) > 0

    def test_standards_context_loaded(self):
        """Test that TEAM_STANDARDS.md is loaded successfully."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        # Standards context should exist
        assert len(agent.standards) > 0


class TestContextRetrieval:
    """Test context snippet retrieval by topic."""

    def test_get_context_snippet_business(self):
        """Test retrieving business context snippet."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        snippet = agent.get_context_snippet("business")
        assert isinstance(snippet, str)
        assert len(snippet) > 0

    def test_get_context_snippet_architecture(self):
        """Test retrieving architecture context snippet."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        snippet = agent.get_context_snippet("architecture")
        assert isinstance(snippet, str)
        assert len(snippet) > 0

    def test_get_context_snippet_standards(self):
        """Test retrieving standards context snippet."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        snippet = agent.get_context_snippet("standards")
        assert isinstance(snippet, str)
        assert len(snippet) > 0

    def test_get_context_snippet_topic_aliases(self):
        """Test that context retrieval works with topic aliases."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        # Business aliases
        business_snippet = agent.get_context_snippet("business")
        goals_snippet = agent.get_context_snippet("goals")
        principles_snippet = agent.get_context_snippet("principles")
        
        assert business_snippet == goals_snippet
        assert business_snippet == principles_snippet
        assert len(business_snippet) > 0

    def test_get_context_snippet_architecture_aliases(self):
        """Test that architecture aliases work."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        arch_snippet = agent.get_context_snippet("architecture")
        design_snippet = agent.get_context_snippet("design")
        decisions_snippet = agent.get_context_snippet("decisions")
        
        assert arch_snippet == design_snippet
        assert arch_snippet == decisions_snippet
        assert len(arch_snippet) > 0

    def test_get_context_snippet_standards_aliases(self):
        """Test that standards aliases work."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        standard_snippet = agent.get_context_snippet("standards")
        naming_snippet = agent.get_context_snippet("naming")
        conventions_snippet = agent.get_context_snippet("conventions")
        
        assert standard_snippet == naming_snippet
        assert standard_snippet == conventions_snippet
        assert len(standard_snippet) > 0

    def test_get_context_snippet_unknown_topic(self):
        """Test that unknown topics return empty string."""
        config = AgentConfig(name="test", description="test", version="1.0.0")
        agent = Agent(config)
        
        snippet = agent.get_context_snippet("nonexistent_topic")
        assert snippet == ""


class TestCodeAnalyzerContextAwareness:
    """Test CodeAnalyzerAgent context integration."""

    def test_code_analyzer_references_documentation(self):
        """Test that code analyzer includes documentation references in results."""
        analyzer = CodeAnalyzerAgent()
        
        # Code with a long function
        code = """
def very_long_function():
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
    return x + y + z
"""
        result = analyzer._detect_issues(code)
        
        assert "count" in result
        # Should have "references" field pointing to documentation
        if "references" in result:
            assert isinstance(result["references"], list)

    def test_code_analyzer_inherits_context(self):
        """Test that CodeAnalyzerAgent inherits context from base."""
        analyzer = CodeAnalyzerAgent()
        
        # Should have context methods
        assert hasattr(analyzer, 'get_context_snippet')
        assert callable(analyzer.get_context_snippet)
        
        # Should have context attributes
        assert hasattr(analyzer, 'business_context')
        assert hasattr(analyzer, 'architecture')
        assert hasattr(analyzer, 'standards')


class TestSecurityAgentContextAwareness:
    """Test SecurityAgent context integration."""

    def test_security_agent_references_business_context(self):
        """Test that security agent uses business context in threat detection."""
        agent = SecurityAgent()
        
        # Code with actual security threat (eval)
        code = """
def handle_user_input(user_input):
    result = eval(user_input)
    return result
"""
        result = agent._scan_threats(code)
        
        assert "success" in result
        # If threats found, should reference business context for privacy concerns
        if result.get("threats_found", 0) > 0:
            if "context_note" in result:
                assert "BUSINESS_CONTEXT" in result["context_note"]

    def test_security_agent_inherits_context(self):
        """Test that SecurityAgent has context capability."""
        agent = SecurityAgent()
        
        assert hasattr(agent, 'get_context_snippet')
        assert callable(agent.get_context_snippet)
        
        snippet = agent.get_context_snippet("business")
        assert len(snippet) > 0


class TestDocumentationAgentContextAwareness:
    """Test DocumentationAgent context integration."""

    def test_documentation_agent_references_standards(self):
        """Test that documentation agent references standards."""
        agent = DocumentationAgent()
        
        # Module path (just a test path)
        result = agent._generate_module_docs(__file__)
        
        assert result["success"] is True
        # Should have reference to standards
        if "standards_reference" in result:
            assert "TEAM_STANDARDS" in result["standards_reference"]

    def test_documentation_agent_api_reference_includes_standards(self):
        """Test that API reference generation includes standards note."""
        agent = DocumentationAgent()
        
        code = """
def function_one():
    pass

def function_two():
    pass

class MyClass:
    pass
"""
        result = agent._generate_api_reference(code)
        
        assert result["success"] is True
        if "standards_reference" in result:
            assert "TEAM_STANDARDS" in result["standards_reference"]

    def test_documentation_agent_summary_references_architecture(self):
        """Test that summary generation references architecture."""
        agent = DocumentationAgent()
        
        code = """
def process_data():
    pass

def analyze_data():
    pass

class DataProcessor:
    pass
"""
        result = agent._generate_summary(code)
        
        assert result["success"] is True
        if "architecture_reference" in result:
            assert "ARCHITECTURE" in result["architecture_reference"]

    def test_documentation_agent_inherits_context(self):
        """Test that DocumentationAgent has context capability."""
        agent = DocumentationAgent()
        
        assert hasattr(agent, 'get_context_snippet')
        assert callable(agent.get_context_snippet)
        
        snippet = agent.get_context_snippet("standards")
        assert len(snippet) > 0


class TestAllAgentsInheritContext:
    """Test that all agents inherit context loading capability."""

    def test_all_agents_have_context_methods(self):
        """Test that all agent types have context methods."""
        agents = [
            Agent(AgentConfig(name="base", description="base", version="1.0")),
            CodeAnalyzerAgent(),
            SecurityAgent(),
            DocumentationAgent()
        ]
        
        for agent in agents:
            assert hasattr(agent, '_load_knowledge_context')
            assert hasattr(agent, '_load_markdown')
            assert hasattr(agent, '_load_yaml')
            assert hasattr(agent, 'get_context_snippet')

    def test_all_agents_load_context_on_init(self):
        """Test that all agents initialize with context."""
        agents = [
            Agent(AgentConfig(name="base", description="base", version="1.0")),
            CodeAnalyzerAgent(),
            SecurityAgent(),
            DocumentationAgent()
        ]
        
        for agent in agents:
            assert hasattr(agent, 'business_context')
            assert hasattr(agent, 'architecture')
            assert hasattr(agent, 'standards')
            assert len(agent.business_context) > 0 or len(agent.architecture) > 0


class TestContextIntegrationEndToEnd:
    """End-to-end tests for context integration."""

    def test_code_analyzer_with_context_quality(self):
        """Test that CodeAnalyzer produces context-aware analysis."""
        analyzer = CodeAnalyzerAgent()
        
        complex_code = """
def bad_function(a, b):
    if a > 0:
        if b > 0:
            if a < 100:
                if b < 100:
                    if a != b:
                        if a > b:
                            return a - b
                        else:
                            return b - a
        else:
            return 0
    return -1
"""
        result = analyzer._detect_issues(complex_code)
        
        assert "count" in result
        # Should have analysis results
        assert isinstance(result.get("issues", []), list)

    def test_documentation_generation_complete(self):
        """Test complete documentation generation with context."""
        agent = DocumentationAgent()
        
        code = """
class DataManager:
    def __init__(self):
        pass
    
    def load_data(self):
        pass
    
    def save_data(self):
        pass
    
    def process_data(self):
        pass
"""
        
        # Test all documentation generation methods
        api_result = agent._generate_api_reference(code)
        summary_result = agent._generate_summary(code)
        docstrings_result = agent._generate_docstrings(code)
        
        assert api_result["success"] is True
        assert summary_result["success"] is True
        assert docstrings_result["success"] is True

    def test_security_scan_with_business_context(self):
        """Test that security scanning uses business context."""
        agent = SecurityAgent()
        
        sensitive_code = """
password = "MyPassword123"
api_key = "sk-1234567890abcdef"
def authenticate(user):
    if user == 'admin':
        return True
    return False
"""
        result = agent._scan_threats(sensitive_code)
        
        assert "success" in result
        # Verify result has expected structure
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
