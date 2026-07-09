"""공통 로거. logs/{YYYY-MM-DD}/{name}.log 로 기록하고, 민감정보를 마스킹한다.
(지침서 9장 보안 규칙 5: 로그에 API 키/토큰/계좌번호가 그대로 출력되지 않도록 마스킹)
"""
from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

_SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key\s*[:=]\s*)([^\s&]+)", re.IGNORECASE),
    re.compile(r"(app[_-]?secret\s*[:=]\s*)([^\s&]+)", re.IGNORECASE),
    re.compile(r"(access[_-]?token\s*[:=]\s*)([^\s&]+)", re.IGNORECASE),
    re.compile(r"(account[_-]?no\s*[:=]\s*)([^\s&]+)", re.IGNORECASE),
]


class SecretMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern in _SECRET_PATTERNS:
            msg = pattern.sub(r"\1***MASKED***", msg)
        record.msg = msg
        record.args = ()
        return True


def get_logger(name: str, log_root: str | Path = "logs") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    day_dir = Path(log_root) / date.today().isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(day_dir / f"{name}.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SecretMaskingFilter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SecretMaskingFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
