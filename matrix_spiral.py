"""Скачивает квадратную матрицу и возвращает обход по спирали"""

from __future__ import annotations

import re
from typing import Final

CELL_RE = re.compile(r"-?\d+")


class MatrixError(Exception):
    """Любая ошибка: сеть, статус ответа или формат матрицы"""


def parse_matrix(text: str) -> list[list[int]]:
    """Превращает текст '+---+ / | 1 |' в список строк"""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise MatrixError("пустой ответ")

    rows: list[list[int]] = []
    for lineno, line in enumerate(lines, start=1):
        s = line.strip()
        if s.startswith("+"):
            continue
        cells = [c.strip() for c in s.split("|")[1:-1]]
        if not cells:
            raise MatrixError(f"строка {lineno}: нет ячеек")
        row: list[int] = []
        for c in cells:
            if not CELL_RE.fullmatch(c):
                raise MatrixError(f"строка {lineno}: не число {c!r}")
            row.append(int(c))
        rows.append(row)

    if not rows:
        raise MatrixError("нет строк матрицы")
    return rows
