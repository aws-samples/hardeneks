from pathlib import Path
from unittest.mock import patch, MagicMock

from click import exceptions
import pytest
from typer.testing import CliRunner


from hardeneks import app, _config_callback

runner = CliRunner()


def test_config_callback_path_non_existent():
    path = Path("foo")
    with pytest.raises(exceptions.BadParameter):
        _config_callback(path)


def test_config_callback_path_directory(tmp_path):
    path = Path(tmp_path)
    with pytest.raises(exceptions.BadParameter):
        _config_callback(path)


def test_config_callback_file(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("hello")
    path = _config_callback(config)
    assert config == path


def test_config_callback_bad_yaml(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("'foo")
    with pytest.raises(exceptions.BadParameter):
        _config_callback(config)


def test_app_no_input():
    result = runner.invoke(app, [])
    assert result.exit_code == 2


@patch("kubernetes.config", load_kube_config=MagicMock())
def test_app_with_required_options(config):
    result = runner.invoke(
        app, ["--region", "us-east-1", "--context", "some-context"]
    )
    assert result.exit_code == 0
