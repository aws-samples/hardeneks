from unittest.mock import patch
from pathlib import Path

from click import exceptions
import pytest


from hardeneks import (
    _config_callback,
    _get_cluster_name,
    _get_current_context,
)


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


@patch("kubernetes.config.list_kube_config_contexts")
def test_get_current_context_None(config):
    config.return_value = ({}, {"name": "some-context"})
    context = _get_current_context("")
    assert context == "some-context"


def test_get_current_context():
    context = "some-context"
    assert _get_current_context(context) == context


@patch("boto3.client")
def test_get_cluster_name(client):
    client.return_value.list_clusters.return_value = {
        "clusters": ["gpu-cluster-test", "foo-cluster", "bad-cluster"]
    }
    context = "someperson@gpu-cluster-test.us-west-2.eksctl.io"
    region = "us-west-2"
    cluster_name = "gpu-cluster-test"

    assert _get_cluster_name(context, region) == cluster_name
