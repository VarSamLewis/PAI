import typer
import json
import os
from typing import Optional, List
from pathlib import Path
from .PAI import PAI

app = typer.Typer(help="Personal AI Interface - Initialize once, prompt many times")

# Session file to persist configuration
SESSION_FILE = Path.home() / ".PAI_session.json"


def save_session_config(provider: str, model: str, api_key: Optional[str] = None):
    """Save session configuration to file"""
    config = {"provider": provider, "model": model, "api_key": api_key}
    with open(SESSION_FILE, "w") as f:
        json.dump(config, f)
    typer.echo(f"Session saved: {provider} ({model})")


def load_session_config() -> dict:
    """Load session configuration from file"""
    if not SESSION_FILE.exists():
        typer.echo("No active session. Run 'PAI init <provider>' first.", err=True)
        raise typer.Exit(1)

    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def create_ai_from_config() -> PAI:
    """Create PAI instance from saved configuration"""
    config = load_session_config()
    ai = PAI()

    provider = config["provider"]
    model = config["model"]
    api_key = config.get("api_key")

    kwargs = {"model": model}
    if api_key:
        kwargs["api_key"] = api_key

    try:
        ai.use_provider(provider, **kwargs)
    except ValueError:
        typer.echo(f"Unsupported provider: {provider}", err=True)
        raise typer.Exit(1)

    return ai


@app.command()
def init(
    provider: str = typer.Argument(..., help="AI provider (openai, anthropic, etc.)"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="Model to use"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="API key (overrides environment variable)"
    ),
):
    """Initialize a persistent AI session"""

    try:
        # Test the configuration by creating a session
        ai = PAI()
        available_providers = PAI.available_providers()

        if provider not in available_providers:
            typer.echo(
                f"Provider '{provider}' not supported. Available providers: {', '.join(available_providers)}",
                err=True,
            )
            raise typer.Exit(1)

        kwargs = {"model": model}
        if api_key:
            kwargs["api_key"] = api_key

        ai.use_provider(provider, **kwargs)

        save_session_config(provider, model, api_key)
        typer.echo(f"Session initialized successfully!")
        typer.echo(f"\nNow you can use: PAI prompt 'Your question here'")

    except Exception as e:
        typer.echo(f"Failed to initialize session: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def prompt(
    text: str = typer.Argument(..., help="The prompt to send to the AI"),
    show_config: bool = typer.Option(
        False, "--show-config", help="Show session config before response"
    ),
    params: List[str] = typer.Option(
        [],
        "--param",
        "-p",
        help="Parameters in format name=value (can be used multiple times)",
    ),
):
    """Send a prompt to the initialized AI session"""

    try:
        ai = create_ai_from_config()

        if show_config:
            config = load_session_config()
            typer.echo(f"Using: {config['provider']} ({config['model']})")

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

        response = ai.generate(text, **kwargs)

        final_response = ai.evaluate_response(text, response, **kwargs)
        typer.echo(f"{final_response}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def chat():
    """Start an interactive chat with the initialized session"""

    try:
        ai = create_ai_from_config()
        config = load_session_config()

        typer.echo(f"Interactive chat with {config['provider']} ({config['model']})")
        typer.echo("Type 'exit', 'quit', or press Ctrl+C to end\n")

        while True:
            try:
                user_input = typer.prompt("You", prompt_suffix=": ")

                if user_input.lower() in ["exit", "quit", "q"]:
                    typer.echo("Chat ended")
                    break

                response = ai.generate(user_input)
                typer.echo(f"AI: {response}\n")

            except (KeyboardInterrupt, EOFError):
                typer.echo("\nChat ended")
                break

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def status():
    """Show current session status"""

    try:
        config = load_session_config()
        typer.echo("Current Session:")
        typer.echo(f"   Provider: {config['provider']}")
        typer.echo(f"   Model: {config['model']}")
        typer.echo(
            f"   API Key: {'Set' if config.get('api_key') else 'From environment'}"
        )
        typer.echo(f"   Config file: {SESSION_FILE}")

    except:
        typer.echo("No active session")
        typer.echo("Run 'PAI init <provider>' to create a session")


@app.command()
def reset():
    """Clear the current session"""

    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
        typer.echo("Session cleared")
    else:
        typer.echo("No active session to clear")


@app.command()
def test():
    """Test the current session with a simple prompt"""

    try:
        ai = create_ai_from_config()
        config = load_session_config()

        typer.echo(f"Testing {config['provider']} ({config['model']})...")
        response = ai.generate("Write a haiku about coding")

        typer.echo(f"Session working!")
        typer.echo(f"Response: {response}")

    except Exception as e:
        typer.echo(f"Test failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def providers():
    """List available providers and their default models"""
    providers = PAI.available_providers()

    typer.echo("Available Providers:")
    for provider in providers:
        typer.echo(f"   - {provider}")

    typer.echo("\nUse 'PAI init <provider> --model <model>' to initialize a session")


if __name__ == "__main__":
    app()
