from classes import HeadHunter, SuperJob, Connector


def main():
    vacancies_json = []
    keyword = input("Введите ключевое слово для поиска: ")

    hh = HeadHunter(keyword)
    sj = SuperJob(keyword)

    for api in (hh, sj):
        api.get_vacancies(pages_count=10)
        vacancies_json.extend(api.get_formatted_vacancies())

        connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

    while True:
        command = input("1 - Вывести список вакансий;\n"
                        "2 - Отсотировать по мин. зп\n"
                        ">>>")

        if command.lower() == "1":
            vacancies = connector.select()
        elif command.lower() == "2":
            vacancies = sorted(connector.select())

        for vacancy in vacancies:
            print(vacancy, end='\n')


if __name__ == "__main__":
    main()
