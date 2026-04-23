from typing import Any
import action


def assert_valid_manifest(manifest: dict[str, Any]):
    """
    Validate some basics of the generated manifest
    See https://docs.github.com/en/rest/dependency-graph/dependency-submission?apiVersion=2022-11-28
    """
    assert isinstance(manifest["name"], str)
    assert isinstance(manifest["file"], dict)
    assert isinstance(manifest["resolved"], dict)


def test_airflow():
    """
    Test that we can parse a large lock file from airflow
    """
    manifest = action.uvlock_to_manifest("test/airflow/uv.lock")
    assert_valid_manifest(manifest)
    assert manifest["name"] == "test/airflow/uv.lock"
    assert manifest["file"] == {"source_location": "test/airflow/uv.lock"}
    assert len(manifest["resolved"].keys()) == 113
