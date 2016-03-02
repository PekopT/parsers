# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BelorusneftItem(scrapy.Item):
    # define the fields for your item here like:
    address = scrapy.Field()
    phone = scrapy.Field()
    fuels = scrapy.Field()
