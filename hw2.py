from pymongo import MongoClient

# Сonnection MongoDB ------------>

client = MongoClient('127.0.0.1', 27017)

db = client['hh_ru']
vacancies = db.vacancies

# <------------ Сonnection MongoDB

def get_vacancies(desired_salary, currency):
    for doc in vacancies.find({"$or": [{"min_salary": {"$gt": desired_salary}}, {"max_salary": {"$gt": desired_salary}}], "currency": currency}):
        return doc

print(get_vacancies(100000, "руб."))