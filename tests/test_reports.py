import pytest
import pandas as pd
from src.reports import spending_by_category


@pytest.fixture
def sample_data():
    # Пример тестовых данных
    data = {
        "Дата операции": [
            "01.12.2021 12:00:00",
            "15.12.2021 10:30:00",
            "25.12.2021 18:45:00",
            "05.01.2022 08:00:00",
            "20.02.2022 16:20:00",
        ],
        "Категория": ["Продукты", "Продукты", "Транспорт", "Продукты", "Транспорт"],
        "Сумма": [100, 200, 50, 150, 80],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category_with_date(sample_data):
    # Тестирование функции с указанной датой и категорией "Продукты"
    result = spending_by_category(sample_data, "Продукты", "30.12.2021 17:50:30")
    assert (
        len(result) == 2
    )  # Ожидается 2 строки, так как только две операции с категорией
    # "Продукты" за последние три месяца от указанной даты


def test_spending_by_category_no_date(sample_data):
    result = spending_by_category(sample_data, "Продукты")
    assert len(result) == 0  # Ожидаем три строки, соответствующие категории "Продукты"


def test_spending_by_category_future_date(sample_data):
    # Тестирование функции с будущей датой
    result = spending_by_category(sample_data, "Продукты", "01.01.2023 00:00:00")
    assert (
        len(result) == 0
    )  # Ожидается 0 строк, так как нет операций с категорией "Продукты" за последние три месяца от будущей даты


def test_spending_by_category_no_transactions(sample_data):
    # Тестирование функции с категорией, для которой нет транзакций
    result = spending_by_category(sample_data, "Здоровье", "30.12.2021 17:50:30")
    assert len(result) == 0  # Ожидается 0 строк, так как нет транзакций с категорией "Здоровье"


if __name__ == "__main__":
    pytest.main()
