from bs4 import BeautifulSoup
import requests
import json

input_job = input("Введите профессию: ")
input_page_count = int(input("Введите число страниц: "))

base_url = "https://hh.ru"

headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"}
params = {"text": input_job, "page": [i for i in range(input_page_count)]}
hh_list = []

for j in params["page"]:
    response = requests.get(base_url + "/search/vacancy", headers=headers, params={"text": params["text"], "page": str(j)})

    dom = BeautifulSoup(response.text, "html.parser")
    div_contain = dom.find_all("div", {"class": "vacancy-serp-item"})

    for job in div_contain:
        name_vacancy = job.find("a", {"class": "bloko-link"}).getText()
        salary = job.find("span", {"data-qa": "vacancy-serp__vacancy-compensation"})
        if salary != None:
            salary = salary.getText()
        else:
            salary = "Нет определённой цены"
        link_vacancy = job.find("a", {"class": "bloko-link"})["href"]
        workaday = job.find("a", {"class": "bloko-link_kind-secondary"})
        if workaday != None:
            workaday = workaday.getText()
        else:
            workaday = "Компания работадателя не указана"
        location = job.find("div", {"data-qa": "vacancy-serp__vacancy-address"})
        if location != None:
            location = location.getText()
        else:
            location = "Адрес не указан"
        hh_list.append({"Название вакансии": name_vacancy, "Заработная плата": salary, "Ссылка на вакансию": link_vacancy, "Ссылка на сайт поиска работы": base_url, "Компания работадатель": workaday, "Расположение": location})

with open('hh_jobs.json', 'w', encoding="utf-8") as f:
    json.dump(hh_list, f, indent=3, ensure_ascii=False)