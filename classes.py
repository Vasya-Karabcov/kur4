import json
from abc import ABC, abstractmethod

import requests

from exceptions import ParsingError
from utils import get_currencies


class Engine(ABC):
    """абстрактный класс для классов HH, SJ"""
    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunter(Engine):
    """Класс для работы с HH"""
    url = "https://api.hh.ru/vacancies"

    def __init__(self, keyword):
        self.params = {
            "per_page": 100,
            "page": 1,
            "text": keyword,
            'only_with_salary': True,
        }
        self.vacancies = []

    def get_request(self):
        """Получаем json файл"""
        response = requests.get(self.url, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f" Ошибка получения вакансий")
        else:
            return response.json()["items"]

    def get_vacancies(self, pages_count=2):
        """Получаем вакансии с сайта"""
        self.vacancies = []
        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f"({self.__class__.__name__}) Парсинг страницы {page} -", end=" ")
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}")
            if len(page_vacancies) == 0:
                break

    def get_formatted_vacancies(self):
        """Форматирует вакансии"""
        formatted_vacancies = []
        currencies = get_currencies()

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["employer"]["name"],
                "title": vacancy["name"],
                "url": vacancy["url"],
                "api": "HeadHunter",
                "salary_from": vacancy["salary"]["from"] if vacancy["salary"] else None,
                "salary_to": vacancy["salary"]["to"] if vacancy["salary"] else None,
            }

            if vacancy["salary"]["currency"] == "RUR":
                vacancy["salary"]["currency"] = 'RUB'
            if vacancy["salary"]["currency"] == "BYR":
                vacancy["salary"]["currency"] = 'BYN'

            formatted_vacancy["currency"] = vacancy["salary"]["currency"]
            formatted_vacancy["currency_value"] = currencies[vacancy["salary"]["currency"]]


            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies


class SuperJob(Engine):
    """Класс для работы с SJ"""
    url = "https://api.superjob.ru/2.0/vacancies/"

    def __init__(self, keyword):
        self.params = {
            "count": 100,
            "page": None,
            "keyword": keyword,
        }
        self.headers = {
            "X-Api-App-Id": "v3.r.137790492.b6016538bc67c4f0697976608cb85704725377de.4af9a707f83a655b95cf6d7cb67d5b58c18ddfc8"
        }
        self.vacancies = []

    def get_request(self):
        """Получаем json файл"""
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f" Ошибка получения вакансий")
        return response.json()["objects"]

    def get_formatted_vacancies(self):
        """Форматирует вакансии"""
        formatted_vacancies = []
        currencies = get_currencies()
        sj_currencies = {
            "rub": "RUB",
            "uah": "UAH",
            "uzs": "UZS",
        }

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["firm_name"],
                "title": vacancy["profession"],
                "url": vacancy["link"],
                "api": "SuperJob",
                "salary_from": vacancy["payment_from"] if vacancy["payment_from"] and vacancy[
                    "payment_from"] != 0 else None,
                "salary_to": vacancy["payment_to"] if vacancy["payment_to"] and vacancy["payment_to"] != 0 else None,
            }

            if vacancy["currency"] in sj_currencies:
                formatted_vacancy["currency"] = sj_currencies[vacancy["currency"]]
                formatted_vacancy["currency_value"] = currencies[sj_currencies[vacancy["currency"]]] if sj_currencies[
                                                                                                            vacancy[
                                                                                                                "currency"]] in currencies else 1
            elif vacancy["currency"]:
                formatted_vacancy["currency"] = "RUB"
                formatted_vacancy["currency_value"] = 1
            else:
                formatted_vacancy["currency"] = None
                formatted_vacancy["currency_value"] = None

            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        """Получаем вакансии с сайта"""
        self.vacancies = []
        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f"({self.__class__.__name__}) Парсинг страницы {page} -", end=" ")
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}")
            if len(page_vacancies) == 0:
                break


class Vacancy:
    """Класс для вакансий"""
    def __init__(self, vacancy):
        self.employer = vacancy["employer"]
        self.title = vacancy["title"]
        self.url = vacancy["url"]
        self.api = vacancy["api"]
        self.salary_from = vacancy["salary_from"]
        self.salary_to = vacancy["salary_to"]
        self.currency = vacancy["currency"]
        self.currency_value = vacancy["currency_value"]

    def __str__(self):
        return f"""
Работодатель: \"{self.employer}\"
Вакансия: \"{self.title}\"
Зарплата: {self.salary_from}
Ссылка: {self.url}
        """

    def __lt__(self, other):
        if other.salary_from is None: # Чтобы NONE > 0
            return True
        if self.salary_from is None:
            return False
        return self.salary_from < other.salary_from


class Connector:
    """Класс для работы с json"""
    def __init__(self, keyword, vacancies_json):
        self.filename = f"{keyword.title()}.json"
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(vacancies_json, file, indent=4, ensure_ascii=False)

    def select(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            vacancies = json.load(file)

        return [Vacancy(x) for x in vacancies]

