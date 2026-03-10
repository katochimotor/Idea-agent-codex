from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime

import httpx
from sqlmodel import Session, select

from backend.ai.secret_cipher import SecretCipher
from backend.models.provider_setting_model import ProviderSetting


PROVIDER_DEFAULTS = {
    "codex_cli": {
        "label": "Codex CLI",
        "model_name": "codex",
    },
    "openai": {
        "label": "OpenAI API",
        "model_name": "gpt-4.1-mini",
    },
    "anthropic": {
        "label": "Anthropic",
        "model_name": "claude-3-5-haiku-latest",
    },
}


@dataclass
class ActiveProviderConfig:
    provider: str
    model_name: str
    api_key: str | None = None


class ProviderSettingsService:
    def __init__(self) -> None:
        self.cipher = SecretCipher()

    def _now(self) -> str:
        return datetime.utcnow().isoformat()

    def _validate_provider(self, provider: str) -> str:
        if provider not in PROVIDER_DEFAULTS:
            raise ValueError(f"Unsupported provider: {provider}")
        return provider

    def _mask_api_key(self, api_key: str) -> str:
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}...{api_key[-4:]}"

    def _get_setting(self, session: Session, provider: str) -> ProviderSetting | None:
        return session.exec(select(ProviderSetting).where(ProviderSetting.provider == provider)).first()

    def _get_env_api_key(self, provider: str) -> str | None:
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        if provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return None

    def list_settings(self, session: Session) -> dict:
        rows = session.exec(select(ProviderSetting).order_by(ProviderSetting.provider.asc())).all()
        providers = []
        active_provider = "codex_cli"

        for provider_key, defaults in PROVIDER_DEFAULTS.items():
            row = next((item for item in rows if item.provider == provider_key), None)
            masked_key = None
            if row and row.api_key_encrypted:
                masked_key = self._mask_api_key(self.cipher.decrypt(row.api_key_encrypted))
            if row and row.is_active:
                active_provider = provider_key

            providers.append(
                {
                    "provider": provider_key,
                    "label": defaults["label"],
                    "model_name": row.model_name if row else defaults["model_name"],
                    "is_active": bool(row.is_active) if row else provider_key == active_provider,
                    "has_api_key": bool(row.api_key_encrypted or self._get_env_api_key(provider_key)) if row else bool(self._get_env_api_key(provider_key)),
                    "api_key_hint": masked_key,
                    "last_tested_at": row.last_tested_at if row else None,
                }
            )

        return {
            "providers": providers,
            "active_provider": active_provider,
        }

    def get_active_provider_config(self, session: Session) -> ActiveProviderConfig | None:
        row = session.exec(
            select(ProviderSetting)
            .where(ProviderSetting.is_active == True)  # noqa: E712
            .order_by(ProviderSetting.updated_at.desc())
        ).first()
        if not row:
            return ActiveProviderConfig(provider="codex_cli", model_name=PROVIDER_DEFAULTS["codex_cli"]["model_name"])

        return ActiveProviderConfig(
            provider=row.provider,
            model_name=row.model_name,
            api_key=self.cipher.decrypt(row.api_key_encrypted) if row.api_key_encrypted else self._get_env_api_key(row.provider),
        )

    def _resolve_api_key(self, session: Session, provider: str, api_key: str | None, *, required: bool) -> str | None:
        if provider == "codex_cli":
            return None
        if api_key:
            return api_key.strip()

        existing = self._get_setting(session, provider)
        if existing and existing.api_key_encrypted:
            return self.cipher.decrypt(existing.api_key_encrypted)

        env_key = self._get_env_api_key(provider)
        if env_key:
            return env_key

        if required:
            raise ValueError("API key is required for this provider.")
        return None

    def _test_codex_cli(self) -> dict:
        codex_cmd = shutil.which("codex.cmd")
        codex_ps1 = shutil.which("codex.ps1")
        codex_bin = shutil.which("codex")

        if not any((codex_cmd, codex_ps1, codex_bin)):
            raise ValueError("Codex CLI is not installed or not available in PATH.")

        if codex_cmd:
            command = [codex_cmd, "--version"]
        elif codex_ps1:
            command = ["powershell", "-ExecutionPolicy", "Bypass", "-File", codex_ps1, "--version"]
        else:
            command = ["cmd", "/c", codex_bin, "--version"]

        try:
            response = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15,
                check=True,
            )
        except (subprocess.CalledProcessError, OSError) as exc:
            detail = getattr(exc, "stderr", None) or getattr(exc, "stdout", None) or str(exc)
            raise ValueError(f"Codex CLI check failed: {detail}") from exc

        return {
            "ok": True,
            "provider": "codex_cli",
            "model_name": PROVIDER_DEFAULTS["codex_cli"]["model_name"],
            "message": response.stdout.strip() or response.stderr.strip() or "Codex CLI is available.",
        }

    def _test_openai(self, api_key: str, model_name: str) -> dict:
        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "input": "Reply with OK",
                "max_output_tokens": 16,
            },
            timeout=20.0,
        )
        response.raise_for_status()
        return {"ok": True, "provider": "openai", "model_name": model_name, "message": "OpenAI connection succeeded."}

    def _test_anthropic(self, api_key: str, model_name: str) -> dict:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model_name,
                "max_tokens": 16,
                "messages": [{"role": "user", "content": "Reply with OK"}],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        return {
            "ok": True,
            "provider": "anthropic",
            "model_name": model_name,
            "message": "Anthropic connection succeeded.",
        }

    def test_connection(self, session: Session, provider: str, api_key: str | None = None) -> dict:
        provider = self._validate_provider(provider)
        model_name = PROVIDER_DEFAULTS[provider]["model_name"]
        if provider == "codex_cli":
            return self._test_codex_cli()

        resolved_key = self._resolve_api_key(session, provider, api_key, required=True)

        try:
            if provider == "openai":
                return self._test_openai(resolved_key, model_name)
            return self._test_anthropic(resolved_key, model_name)
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:400] if exc.response is not None else str(exc)
            raise ValueError(f"{provider} test failed: {detail}") from exc
        except httpx.HTTPError as exc:
            raise ValueError(f"{provider} connection failed: {exc}") from exc

    def save_provider(self, session: Session, provider: str, api_key: str | None = None) -> dict:
        provider = self._validate_provider(provider)
        now = self._now()
        resolved_key = self._resolve_api_key(session, provider, api_key, required=False)
        encrypted_key = self.cipher.encrypt(resolved_key) if resolved_key else None
        row = self._get_setting(session, provider)

        if not row:
            row = ProviderSetting(
                provider=provider,
                model_name=PROVIDER_DEFAULTS[provider]["model_name"],
                api_key_encrypted=encrypted_key,
                is_active=True,
                last_tested_at=None,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
        else:
            row.model_name = PROVIDER_DEFAULTS[provider]["model_name"]
            row.api_key_encrypted = encrypted_key or row.api_key_encrypted
            row.is_active = True
            row.updated_at = now

        active_rows = session.exec(
            select(ProviderSetting)
            .where(ProviderSetting.provider != provider)
            .where(ProviderSetting.is_active == True)  # noqa: E712
        ).all()
        for active_row in active_rows:
            active_row.is_active = False
            active_row.updated_at = now

        session.commit()
        session.refresh(row)

        return {
            "provider": row.provider,
            "label": PROVIDER_DEFAULTS[row.provider]["label"],
            "model_name": row.model_name,
            "is_active": row.is_active,
            "has_api_key": bool(row.api_key_encrypted or self._get_env_api_key(row.provider)),
            "api_key_hint": self._mask_api_key(resolved_key) if resolved_key else None,
            "last_tested_at": row.last_tested_at,
        }

    def mark_tested(self, session: Session, provider: str) -> None:
        row = self._get_setting(session, provider)
        if not row:
            return
        row.last_tested_at = self._now()
        row.updated_at = row.last_tested_at
        session.commit()
