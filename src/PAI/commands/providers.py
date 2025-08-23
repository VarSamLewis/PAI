import json
import typer
from PAI.models.model_registry import ProviderRegistry as PR

providers_app = typer.Typer(help="Manage available providers")

@providers_app.command("list")
def list_providers(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full provider metadata"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON (implies verbose)"),
):
    """
    List providers known to PAI. By default shows a compact view.
    Use --verbose for all fields, or --json for machine-readable output.
    """
    info = PR.info()

    if json_out:
        typer.echo(json.dumps(info, indent=2))
        return

    if not verbose:
        # Compact view
        if not info:
            typer.echo("No providers found.")
            return
        for name, meta in info.items():
            aliases = f" (aliases: {', '.join(meta['aliases'])})" if meta["aliases"] else ""
            default = " [default]" if meta["default"] else ""
            status = "enabled" if meta["enabled"] else "disabled"
            typer.echo(f"{name}{default} — {status}{aliases}")
        return

    # Verbose view: print all metadata fields
    if not info:
        typer.echo("No providers found.")
        return
    for name, meta in info.items():
        typer.echo(f"name:       {name}")
        typer.echo(f"  default:   {meta['default']}")
        typer.echo(f"  enabled:   {meta['enabled']}")
        typer.echo(f"  registered:{meta['registered']}")
        typer.echo(f"  class_path:{meta.get('class_path') or '(built-in or unknown)'}")
        if meta["aliases"]:
            typer.echo(f"  aliases:   {', '.join(meta['aliases'])}")
        else:
            typer.echo(f"  aliases:   (none)")
        typer.echo("")  # blank line between entries

@providers_app.command("add")
def add(name: str, class_path: str, aliases: str = typer.Option("", "--aliases"), enable: bool = True):
    alias_list = [a.strip() for a in aliases.split(",") if a.strip()]
    PR.add_provider(name, class_path, aliases=alias_list, enabled=enable)
    typer.echo(f"Added {name} -> {class_path}")

@providers_app.command("enable")
def enable(name: str):
    PR.enable(name); typer.echo(f"Enabled {name}")

@providers_app.command("disable")
def disable(name: str):
    PR.disable(name); typer.echo(f"Disabled {name}")

@providers_app.command("remove")
def remove(name: str):
    PR.remove_provider(name); typer.echo(f"Removed {name}")

@providers_app.command("default")
def set_default(name: str):
    PR.set_default(name); typer.echo(f"Default set to {name}")

@providers_app.command("add-alias")
def add_alias(provider: str, alias: str):
    """Add a new alias for a provider, with safety checks."""
    alias_l = alias.lower()
    info = PR.info()

    # Resolve provider name (accept canonical or an existing alias)
    def _resolve_provider(name: str) -> str | None:
        n = name.lower()
        if n in info:
            return n
        for pname, meta in info.items():
            if n in [a.lower() for a in meta.get("aliases", [])]:
                return pname
        return None

    canon = _resolve_provider(provider)
    if not canon:
        typer.echo(
            f"Unknown provider '{provider}'. Use 'pai providers list' to see available providers.",
            err=True,
        )
        raise typer.Exit(1)

    # Check if alias already exists anywhere
    current_owner = None
    for pname, meta in info.items():
        if alias_l in [a.lower() for a in meta.get("aliases", [])]:
            current_owner = pname
            break

    if current_owner:
        if current_owner == canon:
            typer.echo(f"Alias '{alias}' already exists for provider '{canon}'. Nothing to do.")
            return
        typer.echo(
            f"Alias '{alias}' is already used by provider '{current_owner}'. Choose a different alias.",
            err=True,
        )
        raise typer.Exit(1)

    try:
        PR.add_alias(canon, alias)
        typer.echo(f"Alias '{alias}' added for provider '{canon}'.")
    except Exception as e:
        typer.echo(f"Failed to add alias: {e}", err=True)
        raise typer.Exit(1)


@providers_app.command("remove-alias")
def remove_alias(alias: str):
    """Remove an alias if it exists; otherwise, do nothing."""
    alias_l = alias.lower()
    info = PR.info()

    owner = None
    for pname, meta in info.items():
        if alias_l in [a.lower() for a in meta.get("aliases", [])]:
            owner = pname
            break

    if not owner:
        typer.echo(f"Alias '{alias}' not found; nothing to remove.")
        return

    try:
        PR.remove_alias(alias)
        typer.echo(f"Alias '{alias}' removed (was pointing to '{owner}').")
    except Exception as e:
        typer.echo(f"Failed to remove alias: {e}", err=True)
        raise typer.Exit(1)
