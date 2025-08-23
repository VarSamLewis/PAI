from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Type, Any

import tomllib

@dataclass
class _ProviderMeta:
    name: str
    class_path: Optional[str] = None
    enabled: bool = True
    aliases: List[str] = field(default_factory=list)


class ProviderRegistry:
    """
    Single source of truth for providers:
      - In-memory registry of provider classes (populated by @register or dynamic add)
      - Persistent config of enabled/disabled providers, aliases, default
    """
    _registry: Dict[str, Type[Any]] = {}      # name -> provider class
    _aliases: Dict[str, str] = {}             # alias -> canonical name
    _meta: Dict[str, _ProviderMeta] = {}      # name -> metadata (enabled, class_path, aliases)
    _default: Optional[str] = None            # canonical name of default provider
    _config_loaded: bool = False

    # ----------------- public decorator API -----------------

    @classmethod
    def register(cls, name: str, *aliases: str):
        """Decorator to register a provider class by name (and optional aliases)."""
        def inner(wrapped_class: Type[Any]):
            canon = name.lower()
            cls._registry[canon] = wrapped_class
            # ensure config is loaded so we can merge aliases/enabled
            cls._ensure_config()
            meta = cls._meta.get(canon) or _ProviderMeta(name=canon)
            # keep existing class_path if provided via config, else mark as built-in
            meta.class_path = meta.class_path or f"{wrapped_class.__module__}:{wrapped_class.__name__}"
            meta.enabled = meta.enabled if canon in cls._meta else True
            # merge aliases
            existing = set(meta.aliases)
            for a in aliases:
                al = a.lower()
                if al not in cls._aliases:
                    cls._aliases[al] = canon
                existing.add(al)
            meta.aliases = sorted(existing)
            cls._meta[canon] = meta
            # if no default yet, the first registered becomes default
            if not cls._default:
                cls._default = canon
            return wrapped_class
        return inner

    # ----------------- runtime use -----------------

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> Any:
        """Instantiate a provider by name or alias. Autoloads dynamic providers if needed."""
        cls._ensure_config()
        canon = cls._resolve_name(name)
        cls._ensure_loaded(canon)
        if canon not in cls._registry:
            available = ", ".join(sorted(cls.enabled_providers()))
            raise ValueError(f"Unknown provider: {name}. Enabled providers: {available or '(none)'}")
        return cls._registry[canon](**kwargs)

    @classmethod
    def providers(cls) -> List[str]:
        """All known provider names (registered in memory)."""
        cls._ensure_config()
        return sorted(cls._registry.keys())

    @classmethod
    def enabled_providers(cls) -> List[str]:
        """Providers marked enabled in config (and/or registered)."""
        cls._ensure_config()
        return sorted([n for n, m in cls._meta.items() if m.enabled])

    @classmethod
    def default_provider(cls) -> Optional[str]:
        cls._ensure_config()
        return cls._default

    @classmethod
    def list_models(cls, name: str, **kwargs) -> list[str]:
        prov = cls.get_provider(name, **kwargs)
        if hasattr(prov, "models"):
            return prov.models()  # type: ignore[attr-defined]
        raise NotImplementedError(f"Provider '{name}' does not support model listing.")

    # ----------------- management ops (called by CLI commands) -----------------

    @classmethod
    def add_provider(cls, name: str, class_path: str, *, aliases: Optional[List[str]] = None, enabled: bool = True) -> None:
        """
        Add or update a provider definition (persistent). Tries to import & register immediately.
        class_path: 'package.module:ClassName' or 'package.module.ClassName'
        """
        cls._ensure_config()
        canon = name.lower()
        meta = cls._meta.get(canon) or _ProviderMeta(name=canon)
        meta.class_path = class_path
        meta.enabled = enabled
        if aliases:
            for a in aliases:
                al = a.lower()
                cls._aliases[al] = canon
            meta.aliases = sorted(set(meta.aliases) | {a.lower() for a in aliases})
        cls._meta[canon] = meta
        # attempt to import and register now
        cls._import_and_register(canon, class_path)
        # set default if none
        if not cls._default:
            cls._default = canon
        cls._save_config()

    @classmethod
    def enable(cls, name: str) -> None:
        cls._ensure_config()
        canon = cls._resolve_name(name)
        meta = cls._meta.get(canon) or _ProviderMeta(name=canon)
        meta.enabled = True
        cls._meta[canon] = meta
        # try to autoload class if not loaded
        if canon not in cls._registry and meta.class_path:
            cls._import_and_register(canon, meta.class_path)
        cls._save_config()

    @classmethod
    def disable(cls, name: str) -> None:
        cls._ensure_config()
        canon = cls._resolve_name(name)
        meta = cls._meta.get(canon) or _ProviderMeta(name=canon)
        meta.enabled = False
        cls._meta[canon] = meta
        cls._save_config()

    @classmethod
    def remove_provider(cls, name: str) -> None:
        """
        Remove a provider from persistent config (and aliases). Does not delete code.
        If the provider was dynamically imported, it remains importable; we just stop listing/enabling it.
        """
        cls._ensure_config()
        canon = cls._resolve_name(name)
        # remove aliases pointing to it
        to_del = [a for a, tgt in cls._aliases.items() if tgt == canon]
        for a in to_del:
            del cls._aliases[a]
        # remove meta
        if canon in cls._meta:
            del cls._meta[canon]
        # do not forcibly remove from _registry; leave current process intact
        if cls._default == canon:
            cls._default = next(iter(sorted(cls.enabled_providers())), None)
        cls._save_config()

    @classmethod
    def set_default(cls, name: str) -> None:
        cls._ensure_config()
        canon = cls._resolve_name(name)
        if canon not in cls._meta or not cls._meta[canon].enabled:
            raise ValueError(f"Cannot set default to '{name}': provider not enabled.")
        cls._default = canon
        cls._save_config()

    @classmethod
    def add_alias(cls, provider_name: str, alias: str) -> None:
        cls._ensure_config()
        canon = cls._resolve_name(provider_name)
        al = alias.lower()
        cls._aliases[al] = canon
        meta = cls._meta.get(canon) or _ProviderMeta(name=canon)
        meta.aliases = sorted(set(meta.aliases) | {al})
        cls._meta[canon] = meta
        cls._save_config()

    @classmethod
    def remove_alias(cls, alias: str) -> None:
        cls._ensure_config()
        al = alias.lower()
        prov = cls._aliases.pop(al, None)
        if prov and prov in cls._meta:
            m = cls._meta[prov]
            m.aliases = [a for a in m.aliases if a != al]
            cls._meta[prov] = m
        cls._save_config()

    @classmethod
    def info(cls) -> Dict[str, dict]:
        """
        Return a serialisable snapshot for CLI: {name: {enabled, aliases, class_path, registered}}
        """
        cls._ensure_config()
        out: Dict[str, dict] = {}
        for name, meta in cls._meta.items():
            out[name] = {
                "enabled": meta.enabled,
                "aliases": list(meta.aliases),
                "class_path": meta.class_path,
                "registered": name in cls._registry,
                "default": (name == cls._default),
            }
        # include any registered-but-not-in-config providers (fallback to enabled=True)
        for name in cls._registry.keys():
            if name not in out:
                out[name] = {
                    "enabled": True,
                    "aliases": [],
                    "class_path": f"{cls._registry[name].__module__}:{cls._registry[name].__name__}",
                    "registered": True,
                    "default": (name == cls._default),
                }
        return dict(sorted(out.items()))

    # ----------------- internal helpers -----------------

    @classmethod
    def _resolve_name(cls, name: str) -> str:
        n = name.lower()
        return cls._aliases.get(n, n)

    @classmethod
    def _ensure_loaded(cls, canon: str) -> None:
        """If provider class isn't loaded but exists in config with a class_path, import and register it."""
        if canon in cls._registry:
            return
        meta = cls._meta.get(canon)
        if meta and meta.class_path:
            cls._import_and_register(canon, meta.class_path)

    @classmethod
    def _import_and_register(cls, canon: str, class_path: str) -> None:
        """Import a provider class from a string path and register it."""
        module_name, class_name = cls._split_class_path(class_path)
        mod = importlib.import_module(module_name)
        klass = getattr(mod, class_name)
        # do not call @register again if this provider is already registered by decorator
        if canon not in cls._registry:
            cls._registry[canon] = klass
        # ensure meta exists
        meta = cls._meta.get(canon) or _ProviderMeta(name=canon)
        meta.class_path = class_path
        cls._meta[canon] = meta

    @staticmethod
    def _split_class_path(class_path: str) -> tuple[str, str]:
        if ":" in class_path:
            module_name, class_name = class_path.split(":", 1)
        else:
            # fallback 'pkg.module.ClassName'
            parts = class_path.split(".")
            module_name, class_name = ".".join(parts[:-1]), parts[-1]
        if not module_name or not class_name:
            raise ValueError(f"Invalid class_path: {class_path!r}")
        return module_name, class_name

    # ----------------- persistence -----------------

    @classmethod
    def _config_path(cls) -> Path:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg) if xdg else (Path.home() / ".pai")
        base.mkdir(parents=True, exist_ok=True)
        return base / "providers.toml"

    @classmethod
    def _ensure_config(cls) -> None:
        if cls._config_loaded:
            return
        cls._load_config()
        cls._config_loaded = True

    @classmethod
    def _load_config(cls) -> None:
        path = cls._config_path()
        if not path.exists() or tomllib is None:
            return
        data = {}
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        # default
        cls._default = (data.get("default") or "").lower() or cls._default
        # providers table
        provs = data.get("providers", {})
        for name, entry in provs.items():
            canon = name.lower()
            meta = _ProviderMeta(
                name=canon,
                class_path=entry.get("class"),
                enabled=bool(entry.get("enabled", True)),
                aliases=[a.lower() for a in entry.get("aliases", [])],
            )
            cls._meta[canon] = meta
            for al in meta.aliases:
                cls._aliases[al] = canon

    @classmethod
    def _save_config(cls) -> None:
        path = cls._config_path()
        lines: List[str] = []
        if cls._default:
            lines.append(f'default = "{cls._default}"\n')
        if cls._meta:
            lines.append("\n[providers]\n")
            for name in sorted(cls._meta.keys()):
                m = cls._meta[name]
                lines.append(f'  [providers."{name}"]\n')
                lines.append(f"  enabled = {str(bool(m.enabled)).lower()}\n")
                if m.class_path:
                    lines.append(f'  class = "{m.class_path}"\n')
                if m.aliases:
                    alias_str = ", ".join(f'"{a}"' for a in m.aliases)
                    lines.append(f"  aliases = [{alias_str}]\n")
        tmp = path.with_suffix(".tmp")
        tmp.write_text("".join(lines), encoding="utf-8")
        tmp.replace(path)
