# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, Compose


def fix_price_type(price):
    try:
        return int(price[0].replace(' ', ''))
    except TypeError:
        return price


class LeroymerlinparserItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field(input_processor=Compose(fix_price_type))
    currency = scrapy.Field(output_processor=TakeFirst())
    specifications = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())

