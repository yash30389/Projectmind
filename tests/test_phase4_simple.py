"""
Simplified Phase 4 Tests: Multi-Agent Orchestration System.

Focus on core functionality and workflow orchestration.
"""

import unittest
from pathlib import Path
import sys

# Add projectmind to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from projectmind.agents import (
    Agent, AgentState, AgentResult, AgentConfig,
    CodeAnalyzerAgent, SecurityAgent, DocumentationAgent,
    WorkflowOrchestrator, WorkflowDefinition, WorkflowStep,
    WorkflowState
)


class TestAgentFramework(unittest.TestCase):
    """Test base Agent framework."""

    def test_agent_creation(self):
        """Test agent creation."""
        config = AgentConfig(name="test_agent", description="Test agent")
        agent = Agent(config=config)
        
        self.assertEqual(agent.config.name, "test_agent")
        self.assertEqual(agent.state, AgentState.IDLE)

    def test_agent_status(self):
        """Test agent status reporting."""
        config = AgentConfig(name="test_agent", description="Test agent")
        agent = Agent(config=config)
        
        status = agent.get_status()
        self.assertEqual(status["name"], "test_agent")
        self.assertEqual(status["state"], AgentState.IDLE)


class TestCodeAnalyzerAgent(unittest.TestCase):
    """Test CodeAnalyzerAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = CodeAnalyzerAgent()

    def test_code_analyzer_creation(self):
        """Test CodeAnalyzerAgent creation."""
        self.assertEqual(self.agent.config.name, "code_analyzer")
        self.assertIsNotNone(self.agent)

    def test_analyze_complexity(self):
        """Test complexity analysis."""
        code = """
def hello():
    print("Hello")
    for i in range(10):
        print(i)
"""
        
        result = self.agent.execute("analyze_complexity", {"code": code})
        self.assertTrue(result.success)

    def test_extract_functions(self):
        """Test function extraction."""
        code = """
def func1():
    pass

def func2():
    pass
"""
        
        result = self.agent.execute("extract_functions", {"code": code})
        self.assertTrue(result.success)

    def test_detect_issues(self):
        """Test issue detection."""
        code = """
def very_long_function_with_too_many_lines():
    x = 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    x = x + 1
    return x
"""
        
        result = self.agent.execute("detect_issues", {"code": code})
        self.assertTrue(result.success)


class TestSecurityAgent(unittest.TestCase):
    """Test SecurityAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = SecurityAgent()

    def test_security_agent_creation(self):
        """Test SecurityAgent creation."""
        self.assertEqual(self.agent.config.name, "security")
        self.assertIsNotNone(self.agent)

    def test_scan_threats(self):
        """Test threat scanning."""
        code = "import os; os.system('ls')"
        
        result = self.agent.execute("scan_threats", {"code": code})
        self.assertTrue(result.success)


class TestDocumentationAgent(unittest.TestCase):
    """Test DocumentationAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = DocumentationAgent()

    def test_documentation_agent_creation(self):
        """Test DocumentationAgent creation."""
        self.assertEqual(self.agent.config.name, "documentation")
        self.assertIsNotNone(self.agent)

    def test_generate_summary(self):
        """Test summary generation."""
        code = """
def hello():
    '''Say hello'''
    print("Hello")
"""
        
        result = self.agent.execute("generate_summary", {"code": code})
        self.assertTrue(result.success)

    def test_generate_docstrings(self):
        """Test docstring generation."""
        code = """
def add(a, b):
    return a + b
"""
        
        result = self.agent.execute("generate_docstrings", {"code": code})
        self.assertTrue(result.success)


class TestWorkflowOrchestrator(unittest.TestCase):
    """Test WorkflowOrchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = WorkflowOrchestrator()
        
        # Register agents
        self.analyzer = CodeAnalyzerAgent()
        self.security = SecurityAgent()
        self.docs = DocumentationAgent()
        
        self.orchestrator.register_agent(self.analyzer)
        self.orchestrator.register_agent(self.security)
        self.orchestrator.register_agent(self.docs)

    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(len(self.orchestrator.list_agents()), 3)

    def test_execute_simple_workflow(self):
        """Test executing a simple workflow."""
        steps = [
            WorkflowStep(
                id="analyze",
                agent_name="code_analyzer",
                task="analyze_complexity",
                params={"code": "x = 1"}
            )
        ]
        
        workflow = WorkflowDefinition(
            name="simple_workflow",
            description="Simple test workflow",
            steps=steps
        )
        
        self.orchestrator.register_workflow(workflow)
        result = self.orchestrator.execute_workflow("simple_workflow")
        
        self.assertEqual(result.state, WorkflowState.COMPLETED)
        self.assertEqual(result.steps_completed, 1)

    def test_execute_multi_step_workflow(self):
        """Test executing a multi-step workflow."""
        steps = [
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
        
        workflow = WorkflowDefinition(
            name="multi_workflow",
            description="Multi-step workflow",
            steps=steps
        )
        
        self.orchestrator.register_workflow(workflow)
        result = self.orchestrator.execute_workflow("multi_workflow")
        
        self.assertEqual(result.state, WorkflowState.COMPLETED)
        self.assertEqual(result.steps_completed, 2)

    def test_workflow_with_dependencies(self):
        """Test workflow with step dependencies."""
        steps = [
            WorkflowStep(
                id="step1",
                agent_name="code_analyzer",
                task="analyze_complexity",
                params={"code": "def f(): pass"}
            ),
            WorkflowStep(
                id="step2",
                agent_name="documentation",
                task="generate_summary",
                params={"code": "def f(): pass"},
                depends_on=["step1"]
            )
        ]
        
        workflow = WorkflowDefinition(
            name="dep_workflow",
            description="Workflow with dependencies",
            steps=steps
        )
        
        self.orchestrator.register_workflow(workflow)
        result = self.orchestrator.execute_workflow("dep_workflow")
        
        self.assertEqual(result.state, WorkflowState.COMPLETED)

    def test_get_workflow_info(self):
        """Test getting workflow information."""
        steps = [
            WorkflowStep(
                id="step1",
                agent_name="code_analyzer",
                task="analyze_complexity",
                params={"code": "x = 1"}
            )
        ]
        
        workflow = WorkflowDefinition(
            name="info_workflow",
            description="Info workflow",
            steps=steps
        )
        
        self.orchestrator.register_workflow(workflow)
        info = self.orchestrator.get_workflow_info("info_workflow")
        
        self.assertEqual(info["name"], "info_workflow")
        self.assertEqual(len(info["steps"]), 1)

    def test_orchestrator_statistics(self):
        """Test orchestrator statistics."""
        stats = self.orchestrator.get_statistics()
        
        self.assertIn("workflows_registered", stats)
        self.assertIn("agents_registered", stats)
        self.assertIn("executions", stats)

    def test_list_workflows(self):
        """Test listing workflows."""
        steps = [
            WorkflowStep(
                id="step1",
                agent_name="code_analyzer",
                task="analyze_complexity",
                params={"code": "x = 1"}
            )
        ]
        
        workflow = WorkflowDefinition(
            name="list_workflow",
            description="List workflow",
            steps=steps
        )
        
        self.orchestrator.register_workflow(workflow)
        workflows = self.orchestrator.list_workflows()
        
        self.assertIn("list_workflow", workflows)

    def test_list_agents(self):
        """Test listing agents."""
        agents = self.orchestrator.list_agents()
        
        self.assertIn("code_analyzer", agents)
        self.assertIn("security", agents)
        self.assertIn("documentation", agents)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agents and orchestrator."""

    def test_full_workflow_integration(self):
        """Test full workflow with multiple agents."""
        # Create orchestrator
        orchestrator = WorkflowOrchestrator()
        
        # Register agents
        orchestrator.register_agent(CodeAnalyzerAgent())
        orchestrator.register_agent(SecurityAgent())
        orchestrator.register_agent(DocumentationAgent())
        
        # Create workflow
        steps = [
            WorkflowStep(
                id="analyze",
                agent_name="code_analyzer",
                task="analyze_complexity",
                params={"code": "x = 1\ny = 2"}
            ),
            WorkflowStep(
                id="security",
                agent_name="security",
                task="scan_threats",
                params={"code": "x = 1\ny = 2"},
                depends_on=["analyze"]
            ),
            WorkflowStep(
                id="docs",
                agent_name="documentation",
                task="generate_summary",
                params={"code": "x = 1\ny = 2"},
                depends_on=["analyze"]
            )
        ]
        
        workflow = WorkflowDefinition(
            name="full_workflow",
            description="Full integration workflow",
            steps=steps
        )
        
        orchestrator.register_workflow(workflow)
        result = orchestrator.execute_workflow("full_workflow", verbose=False)
        
        self.assertEqual(result.state, WorkflowState.COMPLETED)
        self.assertEqual(result.steps_completed, 3)


if __name__ == "__main__":
    unittest.main()
