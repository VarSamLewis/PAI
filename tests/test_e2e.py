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
           env=os.environ
       )
    return result.stdout, result.stderr, result.returncode

def test_cli_init():
    """
    E2E test for 'pai init openai --model gpt-4o-mini'
    """
    stdout, stderr, code = run_cli_command(["init", "openai", "--model", "gpt-4o-mini"])
    assert code == 0, f"Non-zero exit code: {code}, stderr: {stderr}"
    assert "openai" in stdout.lower() or "initialized" in stdout.lower(), f"Unexpected output: {stdout}"

def test_cli_prompt():
    """
    E2E test for 'pai prompt "Hello, world!"'
    """
    stdout, stderr, code = run_cli_command(["prompt", "Hello, world!"])
    assert code == 0, f"Non-zero exit code: {code}, stderr: {stderr}"
    assert "hello" in stdout.lower() or "response" in stdout.lower(), f"Unexpected output: {stdout}"


def test_cli_chat():
    """
    E2E test for 'pai chat' with interactive input
    """
    input_text = "Hello World\nexit\n"

    stdout, stderr, code = run_cli_command(["chat"], input_text=input_text)
    assert code == 0, f"Non-zero exit code: {code}, stderr: {stderr}"
    assert "Interactive chat" in stdout, f"Unexpected output: {stdout}"
    assert "AI:" in stdout, f"Unexpected output: {stdout}"
    assert "hello" in stdout.lower(), f"Unexpected output: {stdout}"
    