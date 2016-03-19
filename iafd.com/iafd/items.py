# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IafdActorsItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    performer = scrapy.Field()
    social_site = scrapy.Field()
    init_place = scrapy.Field()
    init_date = scrapy.Field()
    end_date = scrapy.Field()
    gender = scrapy.Field()
    hair_colors = scrapy.Field()
    weight = scrapy.Field()
    height = scrapy.Field()
    isa = scrapy.Field()
    projects = scrapy.Field()


class IafdStudioItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    related = scrapy.Field()

class IafdDistributorItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class IafdTitleItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    participants = scrapy.Field()
    release_date = scrapy.Field()
    duration = scrapy.Field()
    actors = scrapy.Field()
    director = scrapy.Field()
    distributor = scrapy.Field()
    studio = scrapy.Field()
