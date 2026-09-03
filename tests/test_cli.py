from typer.testing import CliRunner
from xavierlabs.cli import app

runner = CliRunner()


def test_cli_banner_no_args():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "terminal-native" in result.stdout.lower() or "xavierlabs" in result.stdout.lower()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Terminal-Native Computational Scientific Research Swarm" in result.stdout
    assert "research" in result.stdout
    assert "run" in result.stdout
    assert "history" in result.stdout
    assert "config" in result.stdout


def test_cli_config():
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Execution Sandbox" in result.stdout
    assert "Ideator Model" in result.stdout


def test_cli_paper_missing():
    result = runner.invoke(app, ["paper", "non_existent_folder"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()
