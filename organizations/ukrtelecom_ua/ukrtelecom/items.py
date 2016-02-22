# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UkrtelecomItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    phone = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    working_time = scrapy.Field()
