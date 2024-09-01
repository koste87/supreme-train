from pathlib import Path
from src.config import file_path
from src.utils import reader_transaction_excel
from src.services import get_transactions_fizlicam


ROOT_PATH = Path(__file__).resolve().parent.parent


def maine_transactions():
    """Функция упраления проектом"""
    print(
        """Добро пожаловать в раздел 'Сервис'
    Предлагаем ознакомиться с возможностями Инвест-копилки.
    Хотите знать, сколько денег Вы могли бы отложить в Инвест-копилку за месяц?
    """
    )
    while True:
        es_no = input("Введите 'да' или 'нет': ").lower()
        if es_no == "да":
            # Читаем данные из excel-файла
            transactions = reader_transaction_excel(file_path)
            # Запрашиваем лимит округления
            while True:
                limit = int(
                    input(
                        "Выберите комфортную Вам сумму округления остатка для инвесткопилки."
                        "Введите число 10, 50 или 100: "
                    ))
                if limit == 10 or limit == 50 or limit == 100:
                    print(f"Выбрано округление до {limit} рублей")
                    break
                else:
                    print("Ошибка ввода")
                    continue
                    # Запрашиваем месяц
                while True:
                    month_choice = int(
                        input(f'Для расчета возьмём 2021 год. Введите порядковый номер месяца {range(1, 13)}: ')
                    )
                    if 0 < month_choice < 10:
                        month = "2021-0" + str(month_choice)
                        break
                    elif 9 < month_choice < 13:
                        month = "2021-" + str(month_choice)
                        break
                    else:
                        print("Ошибка. Введите число в диапазоне от 1 до 12.")
                        continue
                        get_transactions_fizlicam(transactions, month, limit)
                        logger.info(f"Производим расчет сумм для инвесткопилки на {month}")
                        # создаем json-строку
