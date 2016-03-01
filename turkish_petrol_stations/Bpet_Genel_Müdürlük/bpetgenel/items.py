# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class BpetgenelItem(scrapy.Item):
    name = scrapy.Field()
    phone = scrapy.Field()
    fax = scrapy.Field()
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    url = scrapy.Field()
    city = scrapy.Field()
