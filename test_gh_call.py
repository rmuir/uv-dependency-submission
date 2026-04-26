import subprocess
import sys
from unittest.mock import patch, MagicMock

import pytest

from action import retrying_check_output


@pytest.fixture
def mock_sleep():
    with patch("action.sleep") as mock:
        yield mock


def test_retrying_check_output_happy_path():
    cmd = ["gh", "api", "some/endpoint"]
    input_data = '{"key": "value"}'
    expected_output = "Dependency submission successful!\n"

    with patch("subprocess.check_output", return_value=expected_output) as mock_check_output:
        result = retrying_check_output(cmd, input=input_data)

    assert result == expected_output
    mock_check_output.assert_called_once_with(
        cmd,
        input=input_data,
        stderr=sys.stderr,
        universal_newlines=True,
    )


def test_retrying_check_output_retries_on_500(mock_sleep: MagicMock):
    cmd = ["gh", "api", "some/endpoint"]
    input_data = '{"key": "value"}'
    expected_output = "Dependency submission successful!\n"

    retryable_error = subprocess.CalledProcessError(1, cmd)
    retryable_error.output = '{"status": "500"}'

    with patch("subprocess.check_output", side_effect=[retryable_error, expected_output]) as mock_check_output:
        result = retrying_check_output(cmd, input=input_data)

    assert result == expected_output
    assert mock_check_output.call_count == 2
    mock_check_output.assert_called_with(
        cmd,
        input=input_data,
        stderr=sys.stderr,
        universal_newlines=True,
    )
    mock_sleep.assert_called_once_with(1)


def test_retrying_check_output_no_retry_on_empty_output(mock_sleep: MagicMock):
    cmd = ["gh", "api", "some/endpoint"]
    input_data = '{"key": "value"}'

    empty_output_error = subprocess.CalledProcessError(1, cmd)
    empty_output_error.output = ""

    with patch("subprocess.check_output", side_effect=empty_output_error) as mock_check_output:
        with pytest.raises(subprocess.CalledProcessError):
            retrying_check_output(cmd, input=input_data)

    mock_check_output.assert_called_once()
    mock_sleep.assert_not_called()


def test_retrying_check_output_retries_on_server_error(mock_sleep: MagicMock):
    cmd = ["gh", "api", "some/endpoint"]
    input_data = '{"key": "value"}'
    expected_output = "Dependency submission successful!\n"

    retryable_error = subprocess.CalledProcessError(1, cmd)
    retryable_error.output = '{"message": "Server Error"}'

    with patch("subprocess.check_output", side_effect=[retryable_error, expected_output]) as mock_check_output:
        result = retrying_check_output(cmd, input=input_data)

    assert result == expected_output
    assert mock_check_output.call_count == 2
    mock_check_output.assert_called_with(
        cmd,
        input=input_data,
        stderr=sys.stderr,
        universal_newlines=True,
    )
    mock_sleep.assert_called_once_with(1)


def test_retrying_check_output_exhausts_retries(mock_sleep: MagicMock):
    cmd = ["gh", "api", "some/endpoint"]
    input_data = '{"key": "value"}'

    retryable_error = subprocess.CalledProcessError(1, cmd)
    retryable_error.output = '{"status": "500"}'

    with patch("subprocess.check_output", side_effect=[retryable_error] * 5) as mock_check_output:
        with pytest.raises(subprocess.CalledProcessError):
            retrying_check_output(cmd, input=input_data)

    assert mock_check_output.call_count == 5
    assert mock_sleep.call_count == 4
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)
    mock_sleep.assert_any_call(4)
    mock_sleep.assert_any_call(8)
