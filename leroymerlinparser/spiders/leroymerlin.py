import scrapy
from scrapy.http import HtmlResponse
from leroymerlinparser.items import LeroymerlinparserItem
from scrapy.loader import ItemLoader

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{kwargs.get("catalogue")}/']

    def parse(self, response: HtmlResponse):
        base_url = "https://leroymerlin.ru"
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(base_url + next_page, callback=self.parse)

        product_links = response.xpath('//a[@data-qa="product-name"]')
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath('_id', "//span[@slot='article']/@content")
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//img[@alt='product image']/@src")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('currency', "//span[@slot='currency']/text()")
        i = 0
        specifications = {}
        specification_keys = response.xpath("//dl[@class='def-list']//dt[@class='def-list__term']/text()").getall()
        specification_values = response.xpath("//dl[@class='def-list']//dd[@class='def-list__definition']/text()").getall()
        while i < len(response.xpath("//dl[@class='def-list']/div[@class='def-list__group']").getall()):
            specifications[specification_keys[i]] = specification_values[i].replace(' ', '').replace('\n', '')
            i += 1
        loader.add_value('specifications', specifications)
        loader.add_value('link', response.url)
        yield loader.load_item()
