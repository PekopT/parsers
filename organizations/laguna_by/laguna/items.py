# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LagunaItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    working_time = scrapy.Field()
    city = scrapy.Field()
    url = scrapy.Field()
    country = scrapy.Field()
    oblast = scrapy.Field()
    type = scrapy.Field()

