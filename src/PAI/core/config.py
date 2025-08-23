from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional, Tuple

import tomllib

# Hard defaults (overridable by env)
DEFAULT_PROVIDER = os.environ.get("PAI_DEFAULT_PROVIDER", "openai")
DEFAULT_MODEL    = os.environ.get("PAI_DEFAULT_MODEL", "gpt-4o-mini")

@dataclass
class Settings:
    provider: Optional[str] = None
    model: Optional[str] = None
    # key resolution policy: 'auto' (keyring then env) | 'keyring' | 'env'
    auth_source: str = "auto"

# ---------------- paths ----------------

def _user_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else (Path.home() / ".pai")
    base.mkdir(parents=True, exist_ok=True)
    return base / "config.toml"

def _project_config_path(start: Path | None = None) -> Optional[Path]:
    # Search upwards for .pai.toml
    cur = start or Path.cwd()
    for p in (cur, *cur.parents):
        f = p / ".pai.toml"
        if f.exists():
            return f
    return None

# ---------------- io ----------------

def _read_toml(path: Path) -> dict:
    if not path or not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # As a very small fallback, allow JSON content in dev
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

def _dump_toml_table(name: str, kv: dict) -> str:
    # Minimal TOML writer for flat keys (string values).
    # Escapes double-quotes to avoid malformed TOML.
    lines = [f"[{name}]"]
    for k, v in kv.items():
        if v is None:
            continue
        s = str(v).replace('"', '\\"')
        lines.append(f'{k} = "{s}"')
    return "\n".join(lines) + "\n"

# ---------------- settings ----------------

@lru_cache(maxsize=1)
def read_settings() -> Settings:
    """
    Merge project and user settings.
    Precedence inside files: project (.pai.toml) overrides user (~/.pai/config.toml).
    PAI_AUTH_SOURCE env can override auth_source.
    """
    user_cfg = _read_toml(_user_config_path())
    proj_cfg = _read_toml(_project_config_path() or Path(""))

    merged: dict = {}
    merged.update(user_cfg)
    merged.update(proj_cfg)

    # Accept keys at top-level or under [pai]
    root = merged.get("pai", merged)

    s = Settings(
        provider=root.get("provider"),
        model=root.get("model"),
        auth_source=root.get("auth_source", "auto"),
    )

    env_src = os.environ.get("PAI_AUTH_SOURCE")
    if env_src in {"auto", "keyring", "env"}:
        s.auth_source = env_src

    return s

def write_user_settings(
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    auth_source: Optional[str] = None,
) -> None:
    """
    Persist user-level, non-secret preferences in ~/.pai/config.toml.
    Never writes secrets.
    """
    path = _user_config_path()
    cur = _read_toml(path).get("pai", {})
    if provider is not None:
        cur["provider"] = provider
    if model is not None:
        cur["model"] = model
    if auth_source is not None:
        if auth_source not in {"auto", "keyring", "env"}:
            raise ValueError("auth_source must be 'auto', 'keyring', or 'env'")
        cur["auth_source"] = auth_source

    text = _dump_toml_table("pai", cur)
    path.write_text(text, encoding="utf-8")

# ---------------- provider/model resolver ----------------

def resolve_provider_model(
    provider_flag: Optional[str],
    model_flag: Optional[str],
) -> Tuple[str, str]:
    """
    Resolve provider and model with consistent precedence:
        CLI flags > ENV (PAI_PROVIDER/PAI_MODEL) > config (project then user) > hard defaults
    """
    s = read_settings()
    provider = (
        provider_flag
        or os.environ.get("PAI_PROVIDER")
        or s.provider
        or DEFAULT_PROVIDER
    )
    model = (
        model_flag
        or os.environ.get("PAI_MODEL")
        or s.model
        or DEFAULT_MODEL
    )
    return provider, model

# ---------------- API key resolution ----------------

_ENV_NAMES = {
    "openai":    ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "google":    ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "mistral":   ["MISTRAL_API_KEY"],
    "groq":      ["GROQ_API_KEY"],
    "cohere":    ["COHERE_API_KEY"],
}

def _get_env_key(provider: str) -> Optional[str]:
    for name in _ENV_NAMES.get(provider.lower(), []):
        val = os.environ.get(name)
        if val:
            return val
    return None

def _get_keyring_key(provider: str) -> Optional[str]:
    try:
        import keyring  # optional
    except Exception:
        return None
    try:
        return keyring.get_password("pai", f"{provider.lower()}_api_key")
    except Exception:
        return None

def get_api_key(provider: str) -> Optional[str]:
    """
    Get an API key per configured policy:
      - 'keyring' : keyring only
      - 'env'     : env vars only
      - 'auto'    : try keyring, then env
    Never reads from any config file.
    """
    src = read_settings().auth_source
    prov = provider.lower()

    if src == "keyring":
        return _get_keyring_key(prov)
    if src == "env":
        return _get_env_key(prov)

    # auto
    return _get_keyring_key(prov) or _get_env_key(prov)
