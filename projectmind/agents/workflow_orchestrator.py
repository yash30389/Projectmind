"""
Workflow Orchestrator.

Orchestrates multi-agent workflows for complex tasks.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime
import uuid

from .base_agent import Agent, AgentState, AgentResult


class WorkflowState(str, Enum):
    """Workflow execution states."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """Definition of a workflow step."""
    id: str
    agent_name: str
    task: str
    params: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[Callable] = None
    context_aware: bool = False
    context_topics: List[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""
    name: str
    description: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result from workflow execution."""
    workflow_id: str
    workflow_name: str
    state: WorkflowState
    steps_completed: int
    total_steps: int
    results: Dict[str, AgentResult]
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows."""

    def __init__(self):
        """Initialize workflow orchestrator."""
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.execution_history: List[WorkflowResult] = []

    def register_agent(self, agent: Agent) -> None:
        """Register an agent.

        Args:
            agent: Agent to register
        """
        self.agents[agent.config.name] = agent

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow definition.

        Args:
            workflow: Workflow definition
        """
        self.workflows[workflow.name] = workflow

    def execute_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any] = None,
        verbose: bool = False
    ) -> WorkflowResult:
        """Execute a workflow.

        Args:
            workflow_name: Name of workflow to execute
            context: Execution context
            verbose: Print verbose output

        Returns:
            Workflow result
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        workflow = self.workflows[workflow_name]
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()

        if verbose:
            print(f"[Orchestrator] Starting workflow: {workflow_name} (id={workflow_id[:8]})")

        # Initialize execution state
        execution_context = context or {}
        step_results: Dict[str, AgentResult] = {}
        completed_steps = 0

        try:
            # Execute steps in order
            for step in workflow.steps:
                if verbose:
                    print(f"  → Step: {step.task} (agent={step.agent_name})")

                # Check dependencies
                if not self._check_dependencies(step, step_results):
                    if verbose:
                        print(f"    ⚠ Skipped (dependency not met)")
                    continue

                # Check condition
                if step.condition and not step.condition(execution_context):
                    if verbose:
                        print(f"    ⚠ Skipped (condition false)")
                    continue

                # Get agent
                if step.agent_name not in self.agents:
                    raise ValueError(f"Unknown agent: {step.agent_name}")

                agent = self.agents[step.agent_name]

                # Prepare parameters
                params = self._resolve_params(step.params, step_results)

                # Add context snippets if context_aware
                if step.context_aware:
                    context_snippets = {}
                    for topic in step.context_topics:
                        snippet = agent.get_context_snippet(topic)
                        if snippet:
                            context_snippets[topic] = snippet
                    if context_snippets:
                        params["_context_snippets"] = context_snippets

                # Set context on agent
                agent.set_context(execution_context)

                # Execute task
                result = agent.execute(step.task, params)
                step_results[step.id] = result

                if result.success:
                    completed_steps += 1
                    if verbose:
                        print(f"    ✓ Success ({result.execution_time:.2f}s)")
                    
                    # Update execution context
                    execution_context[step.id] = result.output
                else:
                    if verbose:
                        print(f"    ✗ Failed: {result.error}")
                    raise Exception(f"Step {step.id} failed: {result.error}")

            # Workflow completed successfully
            execution_time = (datetime.now() - start_time).total_seconds()

            if verbose:
                print(f"✓ Workflow completed in {execution_time:.2f}s")

            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                state=WorkflowState.COMPLETED,
                steps_completed=completed_steps,
                total_steps=len(workflow.steps),
                results=step_results,
                execution_time=execution_time,
                metadata={"context": execution_context}
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            if verbose:
                print(f"✗ Workflow failed: {str(e)}")

            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                state=WorkflowState.FAILED,
                steps_completed=completed_steps,
                total_steps=len(workflow.steps),
                results=step_results,
                execution_time=execution_time,
                error=str(e)
            )

    def _check_dependencies(
        self,
        step: WorkflowStep,
        results: Dict[str, AgentResult]
    ) -> bool:
        """Check if step dependencies are met.

        Args:
            step: Workflow step
            results: Results from previous steps

        Returns:
            True if dependencies met
        """
        for dep_id in step.depends_on:
            if dep_id not in results:
                return False
            if not results[dep_id].success:
                return False
        return True

    def _resolve_params(
        self,
        params: Dict[str, Any],
        results: Dict[str, AgentResult]
    ) -> Dict[str, Any]:
        """Resolve parameter references to previous step results.

        Args:
            params: Parameters with possible references
            results: Results from previous steps

        Returns:
            Resolved parameters
        """
        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Reference to previous step result
                ref = value[1:]  # Remove $
                if ref in results:
                    resolved[key] = results[ref].output
                else:
                    resolved[key] = value
            else:
                resolved[key] = value

        return resolved

    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """Get information about a workflow.

        Args:
            workflow_name: Name of workflow

        Returns:
            Workflow information
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        workflow = self.workflows[workflow_name]

        return {
            "name": workflow.name,
            "description": workflow.description,
            "steps": len(workflow.steps),
            "agents_required": list(set(step.agent_name for step in workflow.steps)),
            "steps": [
                {
                    "id": step.id,
                    "task": step.task,
                    "agent": step.agent_name,
                    "depends_on": step.depends_on
                }
                for step in workflow.steps
            ]
        }

    def list_workflows(self) -> List[str]:
        """List all registered workflows.

        Returns:
            List of workflow names
        """
        return list(self.workflows.keys())

    def list_agents(self) -> List[str]:
        """List all registered agents.

        Returns:
            List of agent names
        """
        return list(self.agents.keys())

    def get_execution_history(self) -> List[WorkflowResult]:
        """Get execution history.

        Returns:
            List of workflow results
        """
        return self.execution_history

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics.

        Returns:
            Statistics
        """
        total_executions = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.state == WorkflowState.COMPLETED)
        failed = sum(1 for r in self.execution_history if r.state == WorkflowState.FAILED)
        total_time = sum(r.execution_time for r in self.execution_history)

        return {
            "workflows_registered": len(self.workflows),
            "agents_registered": len(self.agents),
            "executions": total_executions,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_executions * 100) if total_executions > 0 else 0,
            "total_execution_time": total_time,
            "average_execution_time": total_time / total_executions if total_executions > 0 else 0
        }
