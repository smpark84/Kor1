"""설정 로더. config/*.yaml을 읽고 ${ENV_VAR} 참조를 .env/환경변수로 치환한다.
(지침서 9장 보안 규칙: API 키는 코드/설정 파일에 직접 쓰지 않고 환경변수만 참조)
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_env_vars(value: Any) -> Any:
    if isinstance(value, str):
        def _replace(match: re.Match) -> str:
            env_key = match.group(1)
            return os.environ.get(env_key, "")

        return _ENV_VAR_PATTERN.sub(_replace, value)
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(v) for v in value]
    return value


def load_config(filename: str = "settings.yaml", config_dir: str | Path | None = None) -> dict:
    """config/{filename}을 로드하고 ${ENV_VAR} 참조를 실제 값으로 치환해 반환한다."""
    load_dotenv(_PROJECT_ROOT / ".env")

    base_dir = Path(config_dir) if config_dir else _PROJECT_ROOT / "config"
    config_path = base_dir / filename

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return _resolve_env_vars(raw)


def load_indicators_config() -> dict:
    return load_config("indicators_config.yaml")
