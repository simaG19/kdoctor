from typer.testing import CliRunner
from kdoctor.cli import app

runner = CliRunner()
def test_help_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output