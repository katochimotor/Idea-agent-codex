from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class ProviderSetting(SQLModel, table=True):
    __tablename__ = "provider_settings"
    __table_args__ = (
        CheckConstraint("provider IN ('codex_cli', 'openai', 'anthropic')", name="ck_provider_settings_provider"),
        UniqueConstraint("provider", name="uq_provider_settings_provider"),
        Index("idx_provider_settings_active", "is_active", "updated_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    provider: str
    model_name: str
    api_key_encrypted: str | None = None
    is_active: bool = Field(default=False)
    last_tested_at: str | None = None
    created_at: str
    updated_at: str
