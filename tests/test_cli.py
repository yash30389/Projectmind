"""ProjectMind CLI tests"""

import pytest
from click.testing import CliRunner
from projectmind.cli.main import cli


@pytest.fixture
def runner():
    """Provide click test runner."""
    return CliRunner()


def test_cli_help(runner):
    """Test CLI help."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ProjectMind" in result.output


def test_cli_version(runner):
    """Test CLI version."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_init_command(runner):
    """Test init command."""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "ProjectMind initialized" in result.output


def test_scan_command(runner):
    """Test scan command."""
    with runner.isolated_filesystem():
        # Create test files
        with open("test.py", "w") as f:
            f.write("print('hello')")

        result = runner.invoke(cli, ["scan"])
        assert result.exit_code == 0
        assert "Repository Scan Summary" in result.output
