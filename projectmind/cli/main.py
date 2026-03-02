"""
Main CLI entrypoint.
"""

import click
import json
from pathlib import Path
from projectmind.core.scanner import RepoScanner
from projectmind.core.context import ContextLoader, ProjectContext
from projectmind.core.python_parser import PythonParser
from projectmind.compliance import PolicyEngine, ActionRequest, ComplianceReporter, ComplianceFramework
from projectmind.audit import AuditLog
from projectmind.security import ThreatDetector
from projectmind.summarization import CodeSummarizer, SummaryType, DocumentationGenerator
from projectmind.embeddings import SemanticSearch, EmbeddingGenerator, VectorStore


@click.group()
@click.version_option("0.1.0", prog_name="projectmind")
def cli():
    """ProjectMind: Local, project-aware AI engineering system."""
    pass


@cli.command()
@click.option(
    "--path",
    default=".",
    help="Path to repository to scan",
)
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Verbose output",
)
def scan(path: str, output: str, verbose: bool):
    """Scan repository and extract metadata."""
    try:
        scanner = RepoScanner(path)
        scanner.scan(verbose=verbose)

        if output == "json":
            click.echo(scanner.to_json())
        else:
            summary = scanner.get_summary()
            click.echo("\n📊 Repository Scan Summary")
            click.echo("=" * 50)
            click.echo(f"Root:           {summary['root']}")
            click.echo(f"Total Files:    {summary['total_files']}")
            click.echo(f"Total Lines:    {summary['total_lines']}")
            click.echo(f"Total Size:     {summary['total_size_mb']} MB")
            click.echo(f"\nLanguages:")
            for lang, count in summary["languages"].items():
                click.echo(f"  {lang}: {count}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--init",
    is_flag=True,
    help="Initialize default project context",
)
@click.option(
    "--path",
    default="project_context.yaml",
    help="Path to context file",
)
def context(init: bool, path: str):
    """Manage project context."""
    try:
        if init:
            default_context = ContextLoader.create_default()
            ContextLoader.save_to_file(default_context, path)
            click.echo(f"✅ Created default context at {path}")
        else:
            loaded_context = ContextLoader.load_from_file(path)
            click.echo("\n🧠 Project Context")
            click.echo("=" * 50)
            click.echo(f"Project: {loaded_context.vision.name}")
            click.echo(f"Description: {loaded_context.vision.description}")
            click.echo(f"\nPrinciples:")
            for principle in loaded_context.vision.key_principles:
                click.echo(f"  • {principle}")
            click.echo(f"\nConstraints:")
            click.echo(f"  • No autonomous changes: {loaded_context.constraints.no_autonomous_changes}")
            click.echo(
                f"  • Must explain reasoning: {loaded_context.constraints.must_explain_reasoning}"
            )
            click.echo(f"  • Respect architecture: {loaded_context.constraints.respect_architecture}")
            if loaded_context.constraints.custom_constraints:
                click.echo(f"\nCustom Constraints:")
                for constraint in loaded_context.constraints.custom_constraints:
                    click.echo(f"  • {constraint}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def analyze(file_path: str, output: str):
    """Analyze a Python file."""
    try:
        analysis = PythonParser.analyze_file(file_path)

        if analysis.has_syntax_error:
            click.echo(f"❌ Syntax Error: {analysis.error_message}", err=True)
            return

        if output == "json":
            result = {
                "file": analysis.file_path,
                "module_docstring": analysis.module_docstring,
                "imports": [
                    {
                        "module": imp.module,
                        "alias": imp.alias,
                        "is_from": imp.is_from,
                        "line": imp.line_number,
                    }
                    for imp in analysis.imports
                ],
                "functions": [
                    {
                        "name": func.name,
                        "line": func.line_number,
                        "parameters": func.parameters,
                        "decorators": func.decorators,
                        "is_async": func.is_async,
                    }
                    for func in analysis.functions
                ],
                "classes": [
                    {
                        "name": cls.name,
                        "line": cls.line_number,
                        "base_classes": cls.base_classes,
                        "methods": [m.name for m in cls.methods],
                    }
                    for cls in analysis.classes
                ],
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"\n📄 Analysis: {file_path}")
            click.echo("=" * 50)
            if analysis.module_docstring:
                click.echo(f"Module: {analysis.module_docstring[:80]}")

            if analysis.imports:
                click.echo(f"\nImports ({len(analysis.imports)}):")
                for imp in analysis.imports[:5]:
                    click.echo(f"  • {imp.module}")
                if len(analysis.imports) > 5:
                    click.echo(f"  ... and {len(analysis.imports) - 5} more")

            if analysis.functions:
                click.echo(f"\nFunctions ({len(analysis.functions)}):")
                for func in analysis.functions:
                    click.echo(f"  • {func.name}({', '.join(func.parameters)})")

            if analysis.classes:
                click.echo(f"\nClasses ({len(analysis.classes)}):")
                for cls in analysis.classes:
                    click.echo(f"  • {cls.name}")
                    for method in cls.methods[:3]:
                        click.echo(f"      - {method.name}()")
                    if len(cls.methods) > 3:
                        click.echo(f"      ... and {len(cls.methods) - 3} more")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def init():
    """Initialize ProjectMind in current directory."""
    try:
        # Create project context
        default_context = ContextLoader.create_default()
        ContextLoader.save_to_file(default_context, "project_context.yaml")

        # Create .pmind directory
        pmind_dir = Path(".pmind")
        pmind_dir.mkdir(exist_ok=True)

        # Create decision log directory
        (pmind_dir / "decisions").mkdir(exist_ok=True)

        click.echo("✅ ProjectMind initialized!")
        click.echo("  • Created project_context.yaml")
        click.echo("  • Created .pmind/decisions/ directory")
        click.echo("\nNext steps:")
        click.echo("  1. Review and edit project_context.yaml")
        click.echo("  2. Run: pmind scan")
        click.echo("  3. Run: pmind analyze <file.py>")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("action_type")
@click.option("--file", default=None, help="Target file")
@click.option("--summary", default=None, help="Change summary")
def validate(action_type: str, file: str, summary: str):
    """Validate an action against project policies."""
    try:
        context = ContextLoader.load_from_file("project_context.yaml")
        engine = PolicyEngine(context)

        request = ActionRequest(
            agent_name="user",
            action_type=action_type,
            target_file=file or "unknown",
            change_summary=summary,
        )

        if engine.validate_action(request):
            click.echo("✅ Action is allowed by policy")
        else:
            click.echo(engine.get_refusal_reason())

    except FileNotFoundError:
        click.echo("❌ project_context.yaml not found. Run 'pmind init' first.", err=True)


@cli.command()
@click.argument("file")
def scan_threats(file: str):
    """Scan a Python file for security threats."""
    try:
        detector = ThreatDetector()

        path = Path(file)
        if not path.exists():
            click.echo(f"❌ File not found: {file}", err=True)
            return

        with open(path) as f:
            code = f.read()

        threats = detector.scan_code(code, file)

        if not threats:
            click.echo(f"✅ No threats detected in {file}")
            return

        click.echo(f"⚠️  Found {len(threats)} threat(s):\n")

        for threat in threats:
            severity_icon = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🔵",
            }.get(str(threat.severity).split(".")[-1], "⚪")

            click.echo(f"{severity_icon} {threat.severity}")
            click.echo(f"   Location: {threat.location}")
            click.echo(f"   Issue: {threat.description}")
            click.echo(f"   Fix: {threat.recommendation}\n")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.argument("agent")
@click.argument("action")
@click.option("--target", default=None, help="Target file")
@click.option("--status", default="pending", help="Action status")
@click.option("--reason", default=None, help="Reason for action")
def audit_log_action(agent: str, action: str, target: str, status: str, reason: str):
    """Log an action in the audit trail."""
    try:
        pmind_dir = Path(".pmind")
        pmind_dir.mkdir(exist_ok=True)

        audit = AuditLog(str(pmind_dir / "audit"))

        entry = audit.log_action(
            agent=agent,
            action=action,
            target=target or "unknown",
            status=status,
            reason=reason,
        )

        click.echo(f"✅ Logged: {entry.agent} {entry.action} {entry.target}")
        click.echo(f"   Status: {entry.status}")
        click.echo(f"   Time: {entry.timestamp}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.option("--format", type=click.Choice(["markdown", "json"]), default="markdown")
@click.option("--output", default=None, help="Output file")
@click.option(
    "--frameworks",
    multiple=True,
    type=click.Choice(["eu_ai_act", "soc2", "iso27001", "internal"]),
    default=["internal"],
    help="Compliance frameworks",
)
def compliance_report(format: str, output: str, frameworks: tuple):
    """Generate compliance report."""
    try:
        reporter = ComplianceReporter()

        # Convert framework names to enum
        framework_enums = [
            ComplianceFramework[f.upper().replace("-", "_")] for f in frameworks
        ]

        if not output:
            output = f"compliance_report.{format}"

        reporter.generate_report(framework_enums, output, format=format)

        click.echo(f"✅ Report generated: {output}")

        # Print summary
        summary = reporter.get_summary()
        click.echo("\nCompliance Summary:")
        for framework, score in summary.items():
            click.echo(f"  • {framework.upper()}: {score['score']}% ({score['status']})")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.argument("file")
@click.option("--output", default=None, help="Output documentation file")
def summarize(file: str, output: str):
    """Analyze and summarize a Python file."""
    try:
        path = Path(file)

        if not path.exists():
            click.echo(f"❌ File not found: {file}", err=True)
            return

        if not path.suffix == ".py":
            click.echo("❌ Only Python files supported", err=True)
            return

        summarizer = CodeSummarizer()
        summary = summarizer.summarize_file(file, SummaryType.DETAILED)

        # Display summary
        click.echo(f"File: {summary.file_path}")
        click.echo(f"\n{summary.brief}\n")

        if summary.metrics:
            click.echo("Metrics:")
            click.echo(f"  Lines of Code: {summary.metrics.code_lines}")
            click.echo(f"  Functions: {summary.metrics.functions}")
            click.echo(f"  Classes: {summary.metrics.classes}")
            click.echo(f"  Complexity: {summary.metrics.cyclomatic_complexity}")
            click.echo(f"  Maintainability: {summary.metrics.maintainability_index:.0f}/100\n")

        # Generate documentation if requested
        if output:
            DocumentationGenerator.save_documentation(summary, output)
            click.echo(f"✅ Documentation saved to {output}")

        # Show issues
        if summary.warnings:
            click.echo("\nIssues:")
            for issue in summary.warnings:
                click.echo(f"  ⚠️  {issue}")

        # Show recommendations
        if summary.recommendations:
            click.echo("\nRecommendations:")
            for rec in summary.recommendations:
                click.echo(f"  💡 {rec}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.option("--path", default=".", help="Directory to analyze")
@click.option("--output", default=None, help="Output documentation file")
def generate_docs(path: str, output: str):
    """Generate API documentation for all Python files in directory."""
    try:
        directory = Path(path)

        if not directory.exists():
            click.echo(f"❌ Directory not found: {path}", err=True)
            return

        summarizer = CodeSummarizer()
        summaries = []

        # Find all Python files
        py_files = sorted(directory.rglob("*.py"))

        if not py_files:
            click.echo(f"❌ No Python files found in {path}", err=True)
            return

        click.echo(f"Analyzing {len(py_files)} Python files...\n")

        for py_file in py_files:
            try:
                summary = summarizer.summarize_file(str(py_file), SummaryType.DETAILED)
                summaries.append(summary)
                click.echo(f"✅ {py_file.name}: {summary.metrics.functions} functions, {summary.metrics.classes} classes")
            except Exception as e:
                click.echo(f"⚠️  {py_file.name}: {e}")

        # Generate API reference
        if summaries:
            api_ref = DocumentationGenerator.generate_api_reference(summaries)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(api_ref)
                click.echo(f"\n✅ API Reference saved to {output}")
            else:
                click.echo(f"\n{api_ref}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.argument("query")
@click.option(
    "--top-k",
    type=int,
    default=5,
    help="Number of results to return",
)
@click.option(
    "--path",
    default=".",
    help="Path to repository to search in",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Verbose output",
)
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def search(query: str, top_k: int, path: str, verbose: bool, output: str):
    """Search for code using semantic similarity."""
    try:
        # Scan and index the repository
        scanner = RepoScanner(path)
        scanner.scan()
        
        # Create semantic search instance
        search_engine = SemanticSearch()
        
        # Index Python files
        indexed_count = 0
        for file_path in scanner.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Generate embeddings for the file
                embedding = search_engine.generator.generate_embedding(
                    content,
                    source_file=file_path,
                    element_type="file",
                    element_name=Path(file_path).stem,
                )
                search_engine.store.add_embedding(embedding)
                indexed_count += 1
            except Exception as e:
                if verbose:
                    click.echo(f"  ⚠️  Error indexing {file_path}: {e}", err=True)
        
        click.echo(f"✅ Indexed {indexed_count} Python files")
        
        # Perform search
        results = search_engine.search(query, top_k=top_k)
        
        if not results:
            click.echo(f"❌ No results found for: {query}")
            return
        
        click.echo(f"\n✅ Found {len(results)} results for: {query}\n")
        
        if output == "json":
            results_json = [
                {
                    "id": emb.id,
                    "name": emb.element_name,
                    "similarity": float(score),
                    "file": emb.source_file,
                    "type": emb.element_type,
                }
                for emb, score in results
            ]
            click.echo(json.dumps(results_json, indent=2))
        else:
            for i, (embedding, score) in enumerate(results, 1):
                click.echo(f"{i}. {embedding.element_name} (similarity: {score:.2%})")
                click.echo(f"   Type: {embedding.element_type or 'unknown'}")
                if embedding.source_file:
                    click.echo(f"   File: {embedding.source_file}")
                click.echo()
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.option(
    "--path",
    default=".",
    help="Path to repository to index",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Verbose output",
)
def index_files(path: str, verbose: bool):
    """Index code files for semantic search."""
    try:
        # Scan the repository
        scanner = RepoScanner(path)
        scanner.scan(verbose=False)
        
        # Create semantic search instance
        search_engine = SemanticSearch()
        
        # Index all Python files
        indexed_count = 0
        total_files = len(scanner.python_files)
        
        for file_path in scanner.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Generate embeddings for the file
                embedding = search_engine.generator.generate_embedding(
                    content,
                    source_file=file_path,
                    element_type="file",
                    element_name=Path(file_path).stem,
                )
                search_engine.store.add_embedding(embedding)
                indexed_count += 1
                
                if verbose:
                    click.echo(f"✅ Indexed: {file_path}")
            except Exception as e:
                if verbose:
                    click.echo(f"⚠️  Skipped {file_path}: {e}", err=True)
        
        click.echo(f"\n✅ Successfully indexed {indexed_count}/{total_files} Python files")
        
        # Save index to disk
        search_engine.store.save_to_disk()
        click.echo(f"✅ Index saved to .pmind/embeddings/")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
def search_stats():
    """Display semantic search index statistics."""
    try:
        search_engine = SemanticSearch()
        
        # Try to load from disk if it exists
        store_path = Path(".pmind/embeddings")
        if store_path.exists():
            search_engine.store._load_from_disk()
        
        stats = search_engine.get_statistics()
        
        click.echo("\n📊 Semantic Search Statistics:")
        click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo(f"Total embeddings: {stats['total_embeddings']}")
        click.echo(f"Embedding dimension: {stats['embedding_dimension']}")
        click.echo(f"Vocabulary size: {stats['vocab_size']}")
        click.echo(f"Storage path: .pmind/embeddings/")
        
        if stats['total_embeddings'] > 0:
            click.echo(f"\n✅ Index is ready for search!")
        else:
            click.echo(f"\n⚠️  Index is empty. Run 'pmind index-files' first.")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


# ============================================================================
# Phase 4: Multi-Agent Orchestration Commands
# ============================================================================

@cli.command()
@click.argument("code", type=click.File("r"), default="-")
@click.option("--verbose", is_flag=True, help="Verbose output")
def agent_analyze(code, verbose):
    """Run code analyzer agent."""
    try:
        from projectmind.agents import CodeAnalyzerAgent
        
        agent = CodeAnalyzerAgent()
        code_text = code.read()
        
        if verbose:
            click.echo("🔍 Running Code Analyzer Agent...")
        
        # Execute multiple analysis tasks
        tasks = {
            "complexity": ("analyze_complexity", {"code": code_text}),
            "functions": ("extract_functions", {"code": code_text}),
            "issues": ("detect_issues", {"code": code_text}),
        }
        
        results = {}
        for task_name, (task, params) in tasks.items():
            result = agent.execute(task, params)
            results[task_name] = result.output if result.success else result.error
        
        click.echo("\n📈 Code Analysis Results:")
        click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if "complexity" in results:
            click.echo(f"Complexity Metrics: {results['complexity']}")
        if "functions" in results:
            click.echo(f"Functions Found: {results['functions']}")
        if "issues" in results:
            click.echo(f"Issues Detected: {results['issues']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.argument("code", type=click.File("r"), default="-")
@click.option("--verbose", is_flag=True, help="Verbose output")
def agent_security(code, verbose):
    """Run security agent."""
    try:
        from projectmind.agents import SecurityAgent
        
        agent = SecurityAgent()
        code_text = code.read()
        
        if verbose:
            click.echo("🔐 Running Security Agent...")
        
        result = agent.execute("scan_threats", {"code": code_text})
        
        click.echo("\n🔐 Security Analysis Results:")
        click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if result.success:
            output = result.output
            if isinstance(output, dict):
                click.echo(f"Threats Found: {output.get('threats_found', 0)}")
                if output.get('threats'):
                    click.echo("\nThreats:")
                    for threat in output['threats'][:5]:  # Show first 5
                        click.echo(f"  • {threat.get('type')}: {threat.get('message')}")
            else:
                click.echo(output)
        else:
            click.echo(f"Error: {result.error}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.argument("code", type=click.File("r"), default="-")
@click.option("--verbose", is_flag=True, help="Verbose output")
def agent_docs(code, verbose):
    """Run documentation agent."""
    try:
        from projectmind.agents import DocumentationAgent
        
        agent = DocumentationAgent()
        code_text = code.read()
        
        if verbose:
            click.echo("📝 Running Documentation Agent...")
        
        result = agent.execute("generate_summary", {"code": code_text})
        
        click.echo("\n📝 Generated Documentation:")
        click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if result.success:
            click.echo(result.output)
        else:
            click.echo(f"Error: {result.error}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.option("--verbose", is_flag=True, help="Verbose output")
def workflow_list(verbose):
    """List available workflows."""
    try:
        from projectmind.agents import WorkflowOrchestrator
        from projectmind.agents import CodeAnalyzerAgent, SecurityAgent, DocumentationAgent
        
        orchestrator = WorkflowOrchestrator()
        orchestrator.register_agent(CodeAnalyzerAgent())
        orchestrator.register_agent(SecurityAgent())
        orchestrator.register_agent(DocumentationAgent())
        
        # Register sample workflows
        from projectmind.agents import WorkflowDefinition, WorkflowStep
        
        workflows = [
            WorkflowDefinition(
                name="analyze_and_secure",
                description="Analyze code and check for security issues",
                steps=[
                    WorkflowStep(
                        id="analyze",
                        agent_name="code_analyzer",
                        task="analyze_complexity",
                        params={"code": ""}
                    ),
                    WorkflowStep(
                        id="security",
                        agent_name="security",
                        task="scan_threats",
                        params={"code": ""},
                        depends_on=["analyze"]
                    )
                ]
            ),
            WorkflowDefinition(
                name="full_analysis",
                description="Complete code analysis and documentation",
                steps=[
                    WorkflowStep(
                        id="analyze",
                        agent_name="code_analyzer",
                        task="analyze_complexity",
                        params={"code": ""}
                    ),
                    WorkflowStep(
                        id="security",
                        agent_name="security",
                        task="scan_threats",
                        params={"code": ""},
                        depends_on=["analyze"]
                    ),
                    WorkflowStep(
                        id="docs",
                        agent_name="documentation",
                        task="generate_summary",
                        params={"code": ""},
                        depends_on=["analyze"]
                    )
                ]
            )
        ]
        
        for workflow in workflows:
            orchestrator.register_workflow(workflow)
        
        click.echo("\n📋 Available Workflows:")
        click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for workflow in orchestrator.list_workflows():
            info = orchestrator.get_workflow_info(workflow)
            click.echo(f"• {workflow}")
            click.echo(f"  {info['description']}")
            click.echo(f"  Steps: {info['steps']}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


if __name__ == "__main__":
    cli()
