
import requests


from exceptions import ParsingError


def get_currencies():
    """Сортировка по валютам"""
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')

    try:
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения валют")
        currencies = response.json()
        formatted_currencies = {}
        for key, data in currencies['Valute'].items():
            formatted_currencies[key] = data['Value']
        formatted_currencies["RUB"] = 1
        return formatted_currencies
    except ParsingError as error:
        print(error)
