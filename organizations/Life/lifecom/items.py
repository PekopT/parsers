# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LifecomItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()
    phone = scrapy.Field()
    city = scrapy.Field()
    time = scrapy.Field()
