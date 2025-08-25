import subprocess
import sys
import os


def run_cli_command(args, input_text=None):
    """
    Run a CLI command and return its output, error, and exit code.
    """
    result = subprocess.run(
        ["poetry", "run", "pai"] + args,
        input=input_text,
        capture_output=True,
        text=True,
        env=os.environ,
    )
    return result.stdout, result.stderr, result.returncode


def test_cli_init():
    """
    E2E test for 'pai init test openai --model gpt-4o-mini'
    """
    stdout, stderr, code = run_cli_command(
        ["init", "test", "openai", "--model", "gpt-4o-mini"]
    )
    assert code == 0, f"Non-zero exit code: {code}, stderr: {stderr}"
    assert (
        "openai" in stdout.lower() or "initialized" in stdout.lower()
    ), f"Unexpected output: {stdout}"


def test_cli_prompt():
    """
    E2E test for 'pai prompt test "Hello, world!"'
    """
    stdout, stderr, code = run_cli_command(["prompt", "test", "Hello, world!"])
    assert code == 0, f"Non-zero exit code: {code}, stderr: {stderr}"
    assert (
        "can't find the answer" in stdout.lower()
        or "session file saved" in stdout.lower()
        or "hello" in stdout.lower()
        or "response" in stdout.lower()
    ), f"Unexpected output: {stdout}"
