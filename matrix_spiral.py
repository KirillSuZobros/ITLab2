"""Скачивает квадратную матрицу и возвращает обход по спирали"""

from __future__ import annotations

import asyncio
import re
from typing import Final

import httpx

DEFAULT_TIMEOUT: Final[float] = 30.0
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
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise MatrixError("строки разной длины")
    if len(rows) != width:
        raise MatrixError(f"матрица не квадратная: {len(rows)}x{width}")
    return rows
    
def spiral_order(matrix: list[list[int]]) -> list[int]:
    """Обход против часовой стрелки с левого верхнего угла"""
    result: list[int] = []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix) - 1
    while top <= bottom and left <= right:
        for row in range(top, bottom + 1):
            result.append(matrix[row][left])
        left += 1
        for col in range(left, right + 1):
            result.append(matrix[bottom][col])
        bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][right])
            right -= 1
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[top][col])
            top += 1
    return result
async def get_matrix(url: str, timeout: float = DEFAULT_TIMEOUT) -> list[int]:
    """Скачивает квадратную матрицу и возвращает обход по спирали"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
    except httpx.TimeoutException as exc:
        raise MatrixError(f"таймаут: {exc!r}") from exc
    except httpx.HTTPError as exc:
        raise MatrixError(f"сетевая ошибка: {exc!r}") from exc

    if resp.status_code >= 500:
        raise MatrixError(f"ошибка сервера {resp.status_code}")
    if resp.status_code >= 400:
        raise MatrixError(f"ошибка клиента {resp.status_code}")

    return spiral_order(parse_matrix(resp.text))
