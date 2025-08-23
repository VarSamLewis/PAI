from __future__ import annotations

import json
import re
from typing import Optional

import typer

from PAI.core.config import resolve_provider_model, get_api_key
from PAI.models.model_registry import ProviderRegistry

models_app = typer.Typer(help="List available models for a provider (no chat session).")

@models_app.callback(invoke_without_command=True)
def list_models(
    ctx: typer.Context,
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider to query"),
    grep: Optional[str] = typer.Option(None, "--grep", "-g", help="Filter by substring or regex"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON array"),
):
    if ctx.invoked_subcommand is not None:
        return

    prov, _ = resolve_provider_model(provider, model_flag=None)
    try:
        client = ProviderRegistry.get_provider(prov, api_key=get_api_key(prov))
        if not hasattr(client, "models"):
            raise typer.BadParameter(f"Provider '{prov}' does not support listing models.")
        all_models: list[str] = client.models()  # type: ignore[attr-defined]
    except Exception as e:
        typer.echo(f"Failed to list models for {prov}: {e}", err=True)
        raise typer.Exit(1)

    # Optional filter
    items = all_models
    if grep:
        try:
            pat = re.compile(grep)
            items = [m for m in all_models if pat.search(m)]
        except re.error:
            items = [m for m in all_models if grep.lower() in m.lower()]

    if json_out:
        typer.echo(json.dumps(items, indent=2))
    else:
        if not items:
            typer.echo("No models found.")
        else:
            typer.echo(f"Provider: {prov}")
            for m in items:
                typer.echo(f"  - {m}")
