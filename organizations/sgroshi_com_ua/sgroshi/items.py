# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SgroshiItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    address_ua = scrapy.Field()
    url = scrapy.Field()
    city = scrapy.Field()
    phone = scrapy.Field()
    city_ua = scrapy.Field()
    working_time = scrapy.Field()
    working_time_ua = scrapy.Field()