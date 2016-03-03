# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OrganizationItem(scrapy.Item):
    name = scrapy.Field()
    phone = scrapy.Field()
    url = scrapy.Field()

class TehnoskarbItem(OrganizationItem):
    address_rus = scrapy.Field()
    address_ua = scrapy.Field()
    working_time_ru = scrapy.Field()
    working_time_ua = scrapy.Field()
    add_url_ru = scrapy.Field()
    add_url_ua = scrapy.Field()

