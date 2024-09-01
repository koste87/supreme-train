import datetime as dt
import json
import logging
import datetime
from pathlib import Path
import pandas as pd
from src.config import file_path
import os
import requests
from dotenv import load_dotenv


load_dotenv("..\\.env")

ROOT_PATH = Path(__file__).resolve().parent.parent

logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("..\\logs\\utils.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_data(data: str) -> datetime.datetime:
    """Функция преобразования даты"""
    logger.info(f"Получена строка даты: {data}")
    try:
        data_obj = datetime.datetime.strptime(data, "%d.%m.%Y %H:%M:%S")
        logger.info(f"Преобразована в объект datetime: {data_obj}")
        return data_obj
    except ValueError as e:
        logger.error(f"Ошибка преобразования даты: {e}")
        raise e


def reader_transaction_excel(file_path) -> pd.DataFrame:
    """Функция принимает на вход путь до файла и возвращает датафрейм"""
    logger.info(f"Вызвана функция получения транзакций из файла {file_path}")
    try:
        df_transactions = pd.read_excel(file_path)
        logger.info(f"Файл {file_path} найден, данные о транзакциях получены")

        return df_transactions
    except FileNotFoundError:
        logger.info(f"Файл {file_path} не найден")
        raise FileNotFoundError(f"Файл {file_path} не найден")


def get_dict_transaction(file_path) -> list[dict]:
    """Функция преобразовывающая датафрейм в словарь pyhton"""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Файл {file_path}  прочитан")
        dict_transaction = df.to_dict(orient="records")
        logger.info("Датафрейм  преобразован в список словарей")
        return dict_transaction
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден")
        raise
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        raise


if __name__ == "__main__":
    dict_transaction = get_dict_transaction(str(ROOT_PATH) + file_path)
    print(dict_transaction)


def get_user_setting(path):
    """Функция перевода настроек пользователя(курс и акции) из json объекта"""
    logger.info(f"Вызвана функция с файлом {path}")
    with open(path, "r", encoding="utf-8") as f:
        user_setting = json.load(f)
        logger.info("Получены настройки пользователя")
    return user_setting["user_currencies"], user_setting["user_stocks"]


def get_currency_rates(currencies):
    """функция, возвращает курсы"""
    logger.info("Вызвана функция для получения курсов")
    API_KEY = os.environ.get("API_KEY")
    symbols = ",".join(currencies)
    url = f"https://api.apilayer.com/currency_data/live?symbols={symbols}"

    headers = {"apikey": API_KEY}
    response = requests.get(url, headers=headers)
    status_code = response.status_code
    if status_code != 200:
        print(f"Запрос не был успешным. Возможная причина: {response.reason}")

    else:
        data = response.json()
        quotes = data.get("quotes", {})
        usd = quotes.get("USDRUB")
        eur_usd = quotes.get("USDEUR")
        eur = usd / eur_usd
        logger.info("Функция завершила свою работу")

        return [
            {"currency": "USD", "rate": round(usd, 2)},
            {"currency": "EUR", "rate": round(eur, 2)},
        ]


def get_stock_price(stocks):
    """Функция, возвращающая курсы акций"""
    logger.info("Вызвана функция возвращающая курсы акций")
    API_KEY_STOCK = os.environ.get("API_KEY_STOCK")
    stock_price = []
    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_STOCK}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Запрос не был успешным. Возможная причина: {response.reason}")
        else:
            data_ = response.json()
            stock_price.append({"stock": stock, "price": round(float(data_["Global Quote"]["05. price"]), 2)})
    logger.info("Функция завершила свою работу")
    return stock_price


if __name__ == "__main__":
    print(get_currency_rates(["USD", "EUR"]))

    stock = "AAPL"
    stock_price = get_stock_price(["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
    API_KEY_STOCK = '1LEAU1JX6KFZ65TN'


def top_transaction(df_transactions):
    """Функция вывода топ 5 транзакций по сумме платежа"""
    logger.info("Начало работы функции top_transaction")
    top_transaction = df_transactions.sort_values(by="Сумма платежа", ascending=True).iloc[:5]
    logger.info("Получен топ 5 транзакций по сумме платежа")
    result_top_transaction = top_transaction.to_dict(orient="records")
    top_transaction_list = []
    for transaction in result_top_transaction:
        top_transaction_list.append(
            {
                "date": str(
                    (datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S"))
                    .date()
                    .strftime("%d.%m.%Y")
                ).replace("-", "."),
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    logger.info("Сформирован список топ 5 транзакций")
    return top_transaction_list


if __name__ == "__main__":
    top_transaction_list = top_transaction(reader_transaction_excel(str(ROOT_PATH) + file_path))
    print(top_transaction_list)


def get_expenses_cards(df_transactions) -> list[dict]:
    """Функция, возвращающая расходы по каждой карте"""
    logger.info("Начало выполнения функции get_expenses_cards")

    cards_dict = (
        df_transactions.loc[df_transactions["Сумма платежа"] < 0]
        .groupby(by="Номер карты")
        .agg("Сумма платежа")
        .sum()
        .to_dict()
    )
    logger.debug(f"Получен словарь расходов по картам: {cards_dict}")

    expenses_cards = []
    for card, expenses in cards_dict.items():
        expenses_cards.append(
            {"last_digits": card, "total spent": abs(expenses), "cashback": abs(round(expenses / 100, 2))}
        )
        logger.info(f"Добавлен расход по карте {card}: {abs(expenses)}")

    logger.info("Завершение выполнения функции get_expenses_cards")
    return expenses_cards


if __name__ == "__main__":
    result_expenses_cards = get_expenses_cards(reader_transaction_excel(str(ROOT_PATH) + file_path))
    print(result_expenses_cards)


def transaction_currency(df_transactions: pd.DataFrame, data: str) -> pd.DataFrame:
    """Функция, формирующая расходы в заданном интервале"""
    logger.info(f"Вызвана функция transaction_currency с аргументами: df_transactions={df_transactions}, data={data}")
    fin_data = get_data(data)
    logger.debug(f"Получена конечная дата: {fin_data}")
    start_data = fin_data.replace(day=1)
    logger.debug(f"Получена начальная дата: {start_data}")
    fin_data = fin_data.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=1)
    logger.debug(f"Обновлена конечная дата: {fin_data}")
    transaction_currency = df_transactions.loc[
        (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) <= fin_data)
        & (pd.to_datetime(df_transactions["Дата операции"], dayfirst=True) >= start_data)
    ]
    logger.info(f"Получен DataFrame transaction_currency: {transaction_currency}")

    return transaction_currency


if __name__ == "__main__":
    transaction_currency = transaction_currency(
        reader_transaction_excel((str(ROOT_PATH) + file_path)), "29.07.2019 22:06:27"
    )
    print(transaction_currency)


def get_greeting():
    """Функция - приветствие"""
    hour = dt.datetime.now().hour
    if 4 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
