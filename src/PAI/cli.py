import typer
from typing import Optional, List
from .PAI import PAI
import logging

from PAI.utils.logger import logger


def _access_console_hadler(verbose):
    logger.console_handler.setLevel(logging.DEBUG if verbose else logging.WARNING)
    # print(f"Logging level set to {'DEBUG' if verbose else 'WARNING'}")


app = typer.Typer(help="Personal AI Interface - Initialize once, prompt many times")


@app.command()
def init(
    session_name: str = typer.Argument("default", help="Session name"),
    provider: str = typer.Argument(..., help="AI provider (openai, anthropic, etc.)"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    _access_console_hadler(verbose)

    try:
        ai = PAI(session_name)
        available_providers = PAI.available_providers()
        if provider not in available_providers:
            typer.echo(
                f"Provider '{provider}' not supported. Available providers: {', '.join(available_providers)}",
                err=True,
            )
            raise typer.Exit(1)
        ai.init_session(session_name, provider, model, api_key)
        typer.echo("Session initialized successfully!")
        typer.echo("\nNow you can use: PAI prompt 'Your question here'")
    except Exception as e:
        typer.echo(f"Failed to initialize session: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def load(session_name: str = typer.Argument("default", help="Session name"),
    provider: str = typer.Argument(..., help="AI provider (openai, anthropic, etc.)"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    _access_console_hadler(verbose)

    try:
        ai = PAI(session_name)
        available_providers = PAI.available_providers()
        if provider not in available_providers:
            typer.echo(
                f"Provider '{provider}' not supported. Available providers: {', '.join(available_providers)}",
                err=True,
            )
            raise typer.Exit(1)
        ai.load_session(session_name, provider, model, api_key)
        typer.echo("Session loaded successfully!")
        typer.echo("\nNow you can use: PAI prompt 'Your question here'")
    except Exception as e:
        typer.echo(f"Failed to load session: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def prompt(
    session_name: str = typer.Argument("default", help="Session name"),
    text: str = typer.Argument(..., help="The prompt to send to the AI"),
    iterations: int = typer.Option(2, "--iterations", "-n", help="Number of iterations for the prompt"),
        params: List[str] = typer.Option(
        [],
        "--param",
        "-p",
        help="Parameters in format name=value (can be used multiple times)",
    ),
    show_session_log: bool = typer.Option(
        False, "--show-session_log", help="Show session log before response"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    _access_console_hadler(verbose)

    try:
        ai = PAI(session_name)
        ai.get_session_log()
        ai.recreate_session()
        if show_session_log:
            typer.echo(f"Using: {ai.current_provider} ({ai.current_model})")
        kwargs = {}
        for param in params:
            try:
                name, value = param.split("=", 1)
                if value.lower() == "true":
                    kwargs[name] = True
                elif value.lower() == "false":
                    kwargs[name] = False
                else:
                    if value.isdigit():
                        kwargs[name] = int(value)
                    elif (
                        all(c.isdigit() or c == "." for c in value)
                        and value.count(".") <= 1
                    ):
                        kwargs[name] = float(value)
                    else:
                        kwargs[name] = value
            except ValueError:
                typer.echo(
                    f"Invalid parameter format: {param}. Use name=value format.",
                    err=True,
                )

        final_response, tool_use, resource_use = ai.generate_loop(
            text, iterations=iterations, **kwargs
            )

        typer.echo(f"{final_response}")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def status(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """Show current session status"""

    _access_console_hadler(verbose)

    try:
        ai = PAI()
        ai.get_session_log()
        ai.recreate_session()
        session_status = ai.status()
        typer.echo("Current Session:")
        typer.echo(f"   Provider: {session_status['provider']}")
        typer.echo(f"   Model: {session_status['model']}")
        typer.echo(
            f"   API Key: {'Set' if ai.session_log.get('api_key') else 'From environment'}"
        )
        typer.echo(f"   Config file: {ai.session_file}")
    except Exception:
        typer.echo("No active session")
        typer.echo("Run 'PAI init <provider>' to create a session")


@app.command()
def test(
    session_name: str = typer.Argument("default", help="Session name"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """Test the current session with a simple prompt"""

    _access_console_hadler(verbose)

    try:
        ai = PAI(session_name)
        ai.get_session_log()
        ai.recreate_session()
        typer.echo(f"Testing {ai.current_provider} ({ai.current_model})...")
        response = ai.generate("Say Hi")
        typer.echo(f"Session working!")
        typer.echo(f"Response: {response}")
    except Exception as e:
        typer.echo(f"Test failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def providers(
    session_name: str = typer.Argument("default", help="Session name"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """List available providers and their default models"""

    _access_console_hadler(verbose)

    providers = PAI.available_providers()
    typer.echo("Available Providers:")
    for provider in providers:
        typer.echo(f"   - {provider}")
    typer.echo("\nUse 'PAI init <provider> --model <model>' to initialize a session")


if __name__ == "__main__":
    app()
