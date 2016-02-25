# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PharmacykievItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    indication = scrapy.Field()





