import asyncio

import httpx
import pytest

import matrix_spiral
from matrix_spiral import MatrixError, get_matrix, parse_matrix, spiral_order

SOURCE_URL = (
    "https://raw.githubusercontent.com/avito-tech/"
    "python-trainee-assignment/main/matrix.txt"
)
TRAVERSAL = [
    10, 50, 90, 130,
    140, 150, 160, 120,
    80, 40, 30, 20,
    60, 100, 110, 70,
]
SAMPLE_TEXT = """\
+-----+-----+-----+-----+
|  10 |  20 |  30 |  40 |
+-----+-----+-----+-----+
|  50 |  60 |  70 |  80 |
+-----+-----+-----+-----+
|  90 | 100 | 110 | 120 |
+-----+-----+-----+-----+
| 130 | 140 | 150 | 160 |
+-----+-----+-----+-----+
"""


# Пример-тест из задания: есть выход в сеть, поэтому помечен как network и по умолчанию пропускается (pytest.ini).
@pytest.mark.network
def test_get_matrix():
    assert asyncio.run(get_matrix(SOURCE_URL)) == TRAVERSAL


def test_parses_sample_matrix():
    assert parse_matrix(SAMPLE_TEXT) == [
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
        [130, 140, 150, 160],
    ]


def test_parses_1x1():
    assert parse_matrix("+---+\n| 7 |\n+---+") == [[7]]


def test_raises_on_empty_body():
    with pytest.raises(MatrixError, match="пустой"):
        parse_matrix("")


def test_raises_on_non_square():
    text = (
        "+---+---+\n| 1 | 2 |\n+---+---+\n"
        "| 3 | 4 |\n+---+---+\n| 5 | 6 |\n+---+---+"
    )
    with pytest.raises(MatrixError, match="не квадратная"):
        parse_matrix(text)


def test_raises_on_bad_cell():
    text = "+---+---+\n| 1 | x |\n+---+---+\n| 3 | 4 |\n+---+---+"
    with pytest.raises(MatrixError, match="не число"):
        parse_matrix(text)


def test_spiral_1x1():
    assert spiral_order([[42]]) == [42]


def test_spiral_2x2():
    assert spiral_order([[1, 2], [3, 4]]) == [1, 3, 4, 2]


def test_spiral_3x3():
    assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [
        1, 4, 7, 8, 9, 6, 3, 2, 5,
    ]


# Подменяет транспорт httpx на мок, чтобы тесты ошибок не выходили в сеть.
def _patch_client(handler):
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient

    def patched(*args, **kwargs):
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    return patched


@pytest.mark.asyncio
async def test_get_matrix_5xx(monkeypatch):
    monkeypatch.setattr(
        matrix_spiral.httpx, "AsyncClient",
        _patch_client(lambda req: httpx.Response(503)),
    )
    with pytest.raises(MatrixError, match="ошибка сервера 503"):
        await get_matrix("http://example.test/matrix.txt")


@pytest.mark.asyncio
async def test_get_matrix_empty_body(monkeypatch):
    monkeypatch.setattr(
        matrix_spiral.httpx, "AsyncClient",
        _patch_client(lambda req: httpx.Response(200, text="")),
    )
    with pytest.raises(MatrixError, match="пустой"):
        await get_matrix("http://example.test/matrix.txt")


@pytest.mark.asyncio
async def test_get_matrix_timeout(monkeypatch):
    def handler(req):
        raise httpx.ReadTimeout("boom", request=req)

    monkeypatch.setattr(
        matrix_spiral.httpx, "AsyncClient", _patch_client(handler)
    )
    with pytest.raises(MatrixError, match="таймаут"):
        await get_matrix("http://example.test/matrix.txt")
