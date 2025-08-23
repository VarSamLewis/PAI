from __future__ import annotations

from typing import Optional

import typer

from PAI.core.config import resolve_provider_model, get_api_key
from PAI.models.model_registry import ProviderRegistry

test_app = typer.Typer(help="Send a simple test prompt to the configured provider/model (no chat session).")


@test_app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Override provider for this test"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model for this test"),
    prompt: str = typer.Option("Write a haiku about coding", "--prompt", "-q", help="Test prompt to send"),
):
    """
    Sends a predefined string to whatever provider/model is currently resolved.
    No ChatSession is created; this is a pure one-shot request.
    """
    # If subcommands are ever added later, don't run the default handler.
    if ctx.invoked_subcommand is not None:
        return

    try:
        prov, mdl = resolve_provider_model(provider, model)
        typer.echo(f"Testing {prov} ({mdl})...")

        client = ProviderRegistry.get_provider(
            prov,
            model=mdl,
            api_key=get_api_key(prov),
        )

        if hasattr(client, "models") and mdl not in client.models():
            typer.echo(f"Unknown model: {mdl!r}. Try --model gpt-4o-mini.", err=True)
            raise typer.Exit(2)

        response = client.generate(prompt)
        typer.echo("OK — provider responded.")
        typer.echo(f"Response: {response}")

    except Exception as e:
        typer.echo(f"Test failed: {e}", err=True)
        raise typer.Exit(1)
