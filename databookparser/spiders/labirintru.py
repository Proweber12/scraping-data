import scrapy
from scrapy.http import HtmlResponse

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Сonnection MongoDB ------------>

client = MongoClient('127.0.0.1', 27017)

db = client['data_book']
data_book = db.data_book

# <------------ Сonnection MongoDB

class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/Программирование']

    def parse(self, response: HtmlResponse):
        base_url = "https://www.labirint.ru"

        next_page = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(base_url + "/search/Программирование" + next_page, callback=self.parse)
        links = response.xpath("//a[@class='product-title-link']/@href").getall()
        for link in links:
            yield response.follow(base_url + link, callback=self.databook_parse)

    def databook_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath("//h1/text()").get()
        authors = response.xpath("//div[@class='authors']/a/text()").getall()
        basic_price = int(response.xpath("//span[@class='buying-priceold-val-number']/text()").get())
        discounted_price = int(response.xpath("//span[@class='buying-pricenew-val-number']/text()").get())
        rate = float(response.xpath("//div[@id='rate']/text()").get())
        try:
            data_book.insert_one({
                "_id": link.split("/")[-2],
                "link": link,
                "name": name,
                "authors": ", ".join(authors),
                "basic_price": basic_price,
                "product_rating": discounted_price,
                "rate": rate,
            })
        except DuplicateKeyError:
            print("Dublicate key error")
        print(link, name, *authors, basic_price, discounted_price, rate)
