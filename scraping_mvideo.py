from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import hashlib

from time import sleep

# Сonnection MongoDB ------------>

client = MongoClient('127.0.0.1', 27017)

db = client['mvideo_trends']
trends = db.trends

# <------------ Сonnection MongoDB

s = Service('./geckodriver')
driver = webdriver.Firefox(service=s)
driver.get('https://www.mvideo.ru')

driver.execute_script('window.scrollBy(0, 1500)')

# Пришлось добавить так как мой медленный интернет(1Мб/с) не успевает прогрузить страницу, не знаю как у других :)
sleep(10)

trend_button = driver.find_element(By.XPATH, "//span[contains(text(), 'В тренде')]/../..")
trend_button.click()

product_names = driver.find_elements(By.XPATH, "//mvid-product-cards-group[@_ngcontent-serverapp-c248='']/div[contains(@class, 'product-mini-card__name')]")
product_prices = driver.find_elements(By.XPATH, "//mvid-product-cards-group[@_ngcontent-serverapp-c248='']/div[contains(@class, 'product-mini-card__price')]//span[@class='price__main-value']")
product_links = driver.find_elements(By.XPATH, "//mvid-product-cards-group[@_ngcontent-serverapp-c248='']/div[contains(@class, 'product-mini-card__name')]//a")
product_ratings = driver.find_elements(By.XPATH, "//mvid-product-cards-group[@_ngcontent-serverapp-c248='']/div[contains(@class, 'product-mini-card__rating')]//span[contains(@class, 'product-rating__feedback')]")


count = 0

while count < len(product_names):
    print(product_names[count].text)
    print(int(product_prices[count].text.replace(" ", "")))
    print(product_links[count].get_attribute('href'))
    print(product_ratings[count].text)
    print()
    try:
        trends.insert_one({
            "_id": (hashlib.sha256(product_links[count].get_attribute('href').encode())).hexdigest(),
            "product_name": product_names[count].text,
            "product_price": int(product_prices[count].text.replace(" ", "")),
            "product_link": product_links[count].get_attribute('href'),
            "product_rating": product_ratings[count].text
        })
    except DuplicateKeyError:
        print("Dublicate key error")
    count += 1

driver.close()
