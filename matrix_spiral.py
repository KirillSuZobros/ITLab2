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
