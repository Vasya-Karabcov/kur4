from ast import parse

import requests


def get_currencies():
    response = requests.get("http://www.cbr.ru/scripts/xml_daily.asp")

    currencies = parse(response.content)
    formatted_currencies = {}
    for currency in currencies["ValCurs"]["Valute"]:
        value = float(currency["Value"].replace(",", "."))
        nominal = float(currency["Nominal"])
        formatted_currencies[currency["CharCode"]] = value / nominal
    formatted_currencies["RUB"] = 1
    return formatted_currencies
