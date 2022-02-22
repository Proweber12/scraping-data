from bs4 import BeautifulSoup
import requests
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

input_job = input("Введите профессию: ")
input_page_count = int(input("Введите число страниц: "))

max_quantity_paged = 100

if input_page_count > max_quantity_paged:
    input_page_count = max_quantity_paged

base_url = "https://hh.ru"

headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"}
params = {"text": input_job, "items_on_page": 20, "page": [i for i in range(input_page_count)]}
hh_list = []

# Сonnection MongoDB ------------>

client = MongoClient('127.0.0.1', 27017)

db = client['hh_ru']
vacancies = db.vacancies

# <------------ Сonnection MongoDB

for j in params["page"]:
    response = requests.get(base_url + "/search/vacancy", headers=headers, params={"text": params["text"], "items_on_page": params["items_on_page"], "page": str(j)})

    dom = BeautifulSoup(response.text, "html.parser")
    div_contain = dom.find_all("div", {"class": "vacancy-serp-item"})

    for job in div_contain:
        name_vacancy = job.find("a", {"class": "bloko-link"}).getText()
        salary = job.find("span", {"data-qa": "vacancy-serp__vacancy-compensation"})
        salary_sum = None
        salary_min = None
        salary_max = None
        currency = None
        if salary != None:
            if "бел." in salary.getText().split():
                salary_sum = salary.getText().split()
                currency = "".join(salary_sum[-2:])
                del salary_sum[-2:]
            else:
                salary_sum = salary.getText().split()
                currency = salary.getText().split().pop()
                del salary_sum[-1]

            # Format salary 100 000 - 150 000
            if "–" in salary_sum:
                salary_sum_index = salary_sum.index("–")
                salary_min = int("".join(salary_sum[:salary_sum_index]))
                salary_max = int("".join(salary_sum[salary_sum_index+1:]))

            # Format salary "от 100 000" or "до 150 000"
            if salary_sum[0] == "от":
                del salary_sum[0]
                salary_min = int("".join(salary_sum))
            elif salary_sum[0] == "до":
                del salary_sum[0]
                salary_max = int("".join(salary_sum))
        else:
            salary = None
        link_vacancy = job.find("a", {"class": "bloko-link"})["href"]
        workaday = job.find("a", {"class": "bloko-link_kind-secondary"})
        if workaday != None:
            workaday = workaday.getText()
        else:
            workaday = None
        location = job.find("div", {"data-qa": "vacancy-serp__vacancy-address"})
        if location != None:
            location = location.getText()
        else:
            location = None
        hh_list.append({"Название вакансии": name_vacancy, "Минимальная заработная плата": salary_min, "Максимальная заработная плата": salary_max, "Валюта": currency, "Ссылка на вакансию": link_vacancy, "Ссылка на сайт поиска работы": base_url, "Компания работадатель": workaday, "Расположение": location})
        id_vacancy = link_vacancy.split("/")[-1].split("?")[0]

        try:
            vacancies.insert_one({
                                  "_id": id_vacancy,
                                  "name": name_vacancy,
                                  "min_salary": salary_min,
                                  "max_salary": salary_max,
                                  "currency": currency,
                                  "link_vacancy": link_vacancy,
                                  "base_url": base_url,
                                  "workaday": workaday,
                                  "location": location
                                  })
        except DuplicateKeyError:
            print("Duplicate key error collection")

with open('hh_jobs.json', 'w', encoding="utf-8") as f:
    json.dump(hh_list, f, indent=3, ensure_ascii=False)
