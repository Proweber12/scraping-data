from lxml import html
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

base_url = 'https://news.mail.ru/'
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"}
response = requests.get(base_url, headers=headers)
root = html.fromstring(response.text)

# Сonnection MongoDB ------------>

client = MongoClient('127.0.0.1', 27017)

db = client['mailru_news']
news = db.news

# <------------ Сonnection MongoDB

news_pages_link = root.xpath("//a[contains(@class, 'js-topnews__item')]/@href")
additional_news = root.xpath("//li[@class='list__item']/a[@class='list__text']/@href")
news_pages_link += additional_news
print(news_pages_link)

for page_link in news_pages_link:
    response_page = requests.get(page_link, headers=headers)
    root_page = html.fromstring(response_page.text)
    id = page_link.split('/')[-2]
    news_name = root_page.xpath("//h1[@class='hdr__inner']")[0]
    source = root_page.xpath("//a[contains(@class, 'breadcrumbs__link')]/span[@class='link__text']")[0]
    date_publication = root_page.xpath("//span[contains(@class, 'js-ago')]")[0]
    print(page_link)
    print(source.text)
    print(news_name.text)
    print(date_publication.text)
    try:
        news.insert_one({
            "_id": id,
            "news_name": news_name.text,
            "source": source.text,
            "date_publication": date_publication.text,
            "page_link": page_link
        })
    except DuplicateKeyError:
        print("Duplicate key error collection")