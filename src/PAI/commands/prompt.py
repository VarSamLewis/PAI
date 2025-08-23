from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import typer

# Core chat session (owns send(), optional saving)
# Absolute import is the least brittle once the package is installed.
from PAI.core.session import ChatSession  # adjust if your package name differs

# Optional defaults resolver. If absent, we fall back to env vars and hard defaults.
try:
    from PAI.core.config import get_defaults  # should expose .provider and .model attrs
except Exception:
    get_defaults = None  # type: ignore

prompt_app = typer.Typer(help="One-shot prompts (ephemeral by default).")

# Default provider/model (overridable by env)
DEFAULT_PROVIDER = os.environ.get("PAI_DEFAULT_PROVIDER", "openai")
DEFAULT_MODEL = os.environ.get("PAI_DEFAULT_MODEL", "gpt-4o-mini")


def _resolve_provider_model(
    provider_flag: Optional[str],
    model_flag: Optional[str],
) -> tuple[str, str]:
    # Provider precedence: CLI > ENV > defaults file > hard default
    if provider_flag:
        provider = provider_flag
    elif os.environ.get("PAI_PROVIDER"):
        provider = os.environ["PAI_PROVIDER"]
    elif get_defaults:
        try:
            d = get_defaults()
            provider = getattr(d, "provider", None) or DEFAULT_PROVIDER
        except Exception:
            provider = DEFAULT_PROVIDER
    else:
        provider = DEFAULT_PROVIDER

    # Model precedence: CLI > ENV > defaults file > hard default
    if model_flag:
        model = model_flag
    elif os.environ.get("PAI_MODEL"):
        model = os.environ["PAI_MODEL"]
    elif get_defaults:
        try:
            d = get_defaults()
            model = getattr(d, "model", None) or DEFAULT_MODEL
        except Exception:
            model = DEFAULT_MODEL
    else:
        model = DEFAULT_MODEL

    return provider, model


def _read_text_arg_or_stdin(text_arg: Optional[str], file_path: Optional[Path]) -> str:
    # 1) explicit file wins
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")

    # 2) positional argument
    if text_arg is not None:
        return text_arg

    # 3) piped stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()

    raise typer.BadParameter("No input provided. Pass TEXT, --file, or pipe stdin.")


@prompt_app.callback(invoke_without_command=True)
def default(
    ctx: typer.Context,
    text: Optional[str] = typer.Argument(
        None,
        show_default=False,
        help="The prompt text (or use --file / stdin).",
    ),
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Read prompt text from a file."
    ),
    save: bool = typer.Option(
        False, "--save", help="Persist this interaction to a saved session file."
    ),
    session: Optional[str] = typer.Option(
        None, "--session", "-s", help="Session name when saving (auto if omitted)."
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Provider to use (overrides defaults)."
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Model to use (overrides defaults)."
    ),
    json_out: bool = typer.Option(
        False, "--json", help="Print machine-readable JSON instead of plain text."
    ),
):
    """
    Send a single prompt and print the reply.

    Examples:
      pai prompt "Translate this to Welsh"
      pai prompt --file notes.txt
      echo "Summarise this" | pai prompt
      pai prompt "Hello" --save --session quick-notes
      pai prompt "Try this" --provider openai --model gpt-4o-mini
    """
    # If user invoked a subcommand, don't run the default handler.
    if ctx.invoked_subcommand is not None:
        return

    prov, mdl = _resolve_provider_model(provider, model)
    prompt_text = _read_text_arg_or_stdin(text, file)

    # Name saved sessions "prompt-YYYYmmdd-HHMMSS" if not provided
    name = session or (time.strftime("prompt-%Y%m%d-%H%M%S") if save else None)

    sess = ChatSession(provider=prov, model=mdl, save=save, name=name)
    reply = sess.send(prompt_text)

    if json_out:
        payload = {
            "reply": reply,
            "provider": prov,
            "model": mdl,
            "saved": save,
            "session": sess.name if save else None,
        }
        typer.echo(json.dumps(payload, ensure_ascii=False))
    else:
        typer.echo(reply)
        if save:
            typer.echo(f"\nSaved under: {sess.name}")
