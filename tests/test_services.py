import pytest
import json
from src.services import get_transactions_fizlicam


@pytest.fixture
def sample_dict_transaction():
    return [
        {"Описание": "Константин Л."},
        {"Описание": "Оплата услуг"},
    ]


def test_get_transactions_fizlicam_success(sample_dict_transaction):
    pattern = r"Константин Л."
    result = get_transactions_fizlicam(sample_dict_transaction, pattern)
    expected = json.dumps(
        [
            {"Описание": "Константин Л."},
        ],
        ensure_ascii=False,
    )
    assert result == expected


def test_get_transactions_fizlicam_no_match(sample_dict_transaction):
    """Проверка если в списке нет данных соответствующих паттерну, выводим пустой список"""
    pattern = r"Аптеки"
    result = get_transactions_fizlicam(sample_dict_transaction, pattern)
    expected = json.dumps([])
    assert result == expected


def test_get_transactions_fizlicam_empty_input():
    """Проверка, паттерн корректный но нет данных"""
    pattern = r"Константин Л."
    expected_result = "[]"

    result = get_transactions_fizlicam([], pattern)
    assert result == expected_result


@pytest.mark.parametrize(
    "dict_transaction, pattern, expected_output",
    [
        (
            [
                {"Описание": "Перевод физлицу"},
                {"Описание": "Оплата услуги"},
                {"Описание": "Перевод физлицу на сумму 1000"},
            ],
            r"Перевод физлицу",
            json.dumps(
                [
                    {"Описание": "Перевод физлицу"},
                    {"Описание": "Перевод физлицу на сумму 1000"},
                ],
                ensure_ascii=False,
            ),
        ),
        (
            [
                {"Описание": "Оплата кредита"},
                {"Описание": "Оплата услуги"},
            ],
            r"Перевод физлицу",
            "[]",
        ),
        (
            [
                {"Описание": "Перевод физлицу"},
                {"Описание": "Перевод физлицу"},
            ],
            r"Перевод физлицу",
            json.dumps(
                [
                    {"Описание": "Перевод физлицу"},
                    {"Описание": "Перевод физлицу"},
                ],
                ensure_ascii=False,
            ),
        ),
    ],
)
def test_get_transactions_fizlicam(dict_transaction, pattern, expected_output):

    result = get_transactions_fizlicam(dict_transaction, pattern)

    assert result == expected_output
