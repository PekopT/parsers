# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BiletixItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class EventItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    init_date = scrapy.Field()
    images = scrapy.Field()
    participants = scrapy.Field()
    genres = scrapy.Field()
    time = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    id = scrapy.Field()



class EventGroupItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    init_date = scrapy.Field()
    end_date = scrapy.Field()
    description = scrapy.Field()
    place = scrapy.Field()
    images = scrapy.Field()
    participants = scrapy.Field()
    category = scrapy.Field()
    id = scrapy.Field()

class MekanItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    place = scrapy.Field()
    images = scrapy.Field()
    countries = scrapy.Field()
    projects = scrapy.Field()
    url = scrapy.Field()

class PersonaItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    social = scrapy.Field()
    id = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
