# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OhranagovbyItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    mobile = scrapy.Field()
    url = scrapy.Field()
    phone_code = scrapy.Field()
